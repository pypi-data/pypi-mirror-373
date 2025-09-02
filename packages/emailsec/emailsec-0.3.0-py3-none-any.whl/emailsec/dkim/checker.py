from enum import StrEnum
from dataclasses import dataclass
import typing
import email.utils

import emailsec.utils
from emailsec import errors
from emailsec.utils import body_and_headers_for_canonicalization
from emailsec.dmarc import is_dkim_aligned
from emailsec.dkim.parser import (
    DKIMSignature,
    parse_dkim_header_field,
    public_key_info,
    public_key,
    body_hash,
    headers_hash,
    _select_headers,
    _validate_canonicalization_algorithm,
    _algorithm,
    _DKIMStyleSig,
    _SigVerifier,
)


class DKIMResult(StrEnum):
    SUCCESS = "SUCCESS"
    PERMFAIL = "PERMFAIL"
    TEMPFAIL = "TEMPFAIL"


@dataclass
class DKIMCheck:
    result: DKIMResult
    domain: str | None = None
    selector: str | None = None
    signature: DKIMSignature | None = None


async def check_dkim(
    message: bytes, body_and_headers: emailsec.utils.BodyAndHeaders | None = None
) -> DKIMCheck:
    if body_and_headers:
        body, headers = body_and_headers
    else:
        body, headers = body_and_headers_for_canonicalization(message)

    signatures = []
    for header_name, raw_signature in headers.get("dkim-signature", []):
        try:
            sig = parse_dkim_header_field(raw_signature.decode())
        except ValueError:
            continue

        signatures.append(((header_name, raw_signature), sig))

    if not signatures:
        return DKIMCheck(result=DKIMResult.PERMFAIL)

    # Try to pick an aligned signature if multiple signatures are present
    def _sort_sig(item: tuple[emailsec.utils.Header, DKIMSignature]) -> bool:
        _, s = item
        _, from_addr = email.utils.parseaddr(headers["from"][0][1].decode().strip())
        rfc5322_from = from_addr.partition("@")[-1]
        return is_dkim_aligned(s["d"], rfc5322_from)

    # Verify the top 5 signatures and stop once one verifies successfully
    for sig_header, parsed_sig in sorted(signatures, key=_sort_sig, reverse=True)[:5]:
        try:
            if await _verify_dkim_signature(
                body, headers, sig_header, typing.cast(_DKIMStyleSig, parsed_sig)
            ):
                return DKIMCheck(
                    result=DKIMResult.SUCCESS,
                    domain=parsed_sig["d"],
                    selector=parsed_sig["s"],
                    signature=parsed_sig,
                )
        except errors.Temperror:
            return DKIMCheck(
                result=DKIMResult.TEMPFAIL,
                domain=parsed_sig["d"],
                selector=parsed_sig["s"],
                signature=parsed_sig,
            )
        except errors.Permerror:
            continue

    return DKIMCheck(result=DKIMResult.PERMFAIL)


async def _verify_dkim_signature(
    body: emailsec.utils.Body,
    headers: emailsec.utils.Headers,
    sig_header: emailsec.utils.Header,
    sig: _DKIMStyleSig,
) -> bool:
    c = sig.get("c", "simple/simple")
    c_parts = c.split("/")
    if len(c_parts) < 2:
        c_parts.append("simple")
    header_canonicalization, body_canonicalization = map(
        _validate_canonicalization_algorithm, c_parts
    )

    dkim_alg = _algorithm(sig["a"])

    bh = body_hash(body, sig.get("l"), dkim_alg, body_canonicalization)
    if "bh" not in sig:
        raise ValueError("Sig missing bh")
    if bh.decode() != sig["bh"]:
        raise ValueError(f"Body hash does not match {bh.decode()}!={sig['bh']}")

    canonicalized_message = headers_hash(
        _select_headers(headers, sig["h"]), header_canonicalization, sig_header
    )
    return await _verify_sig(dkim_alg, sig, canonicalized_message)


async def _verify_sig(
    dkim_alg, sig: _SigVerifier, canonicalized_message: bytes
) -> bool:
    # TODO: check for expiration/timestamp

    key_info = await public_key_info(sig.get("q"), sig["d"], sig["s"])
    pk = public_key(key_info)

    try:
        match dkim_alg:
            case "rsa-sha1" | "rsa-sha256":
                _rsa_verify(dkim_alg, pk, sig, canonicalized_message)
            case "ed25519-sha256":
                _ed25519_verify(dkim_alg, pk, sig, canonicalized_message)
    except Exception:  # InvalidSignature and other crypto exceptions
        return False
    else:
        return True


def _ed25519_verify(
    dkim_alg,
    pk,
    sig: _SigVerifier,
    message: bytes,
) -> None:
    import base64
    import hashlib

    pk.verify(
        base64.b64decode(sig["b"]),
        hashlib.sha256(message).digest(),
    )


def _rsa_verify(
    dkim_alg,
    pk,
    sig: _SigVerifier,
    message: bytes,
) -> None:
    import base64
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    hasher: hashes.HashAlgorithm
    match dkim_alg:
        case "rsa-sha1":
            hasher = hashes.SHA1()
        case "rsa-sha256":
            hasher = hashes.SHA256()

    pk.verify(
        base64.b64decode(sig["b"]),
        message,
        padding.PKCS1v15(),
        hasher,
    )  # type: ignore
