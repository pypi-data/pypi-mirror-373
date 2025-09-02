import pyparsing
import hashlib
import base64
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.asymmetric import ed25519


import typing
import re
from pyparsing import (
    CaselessLiteral,
    Combine,
    Optional,
    Literal,
    Word,
    ZeroOrMore,
    Group,
    OneOrMore,
    alphanums,
    alphas,
    printables,
    White,
    StringEnd,
)
from emailsec.dns_resolver import DNSResolver
import emailsec.utils


WSP = White(" \t", exact=1)
CRLF = White("\r", exact=1) + White("\n", exact=1)  # | White("\n", exact=1)
LWSP = ZeroOrMore(WSP | (CRLF + WSP))
FWS = Optional(ZeroOrMore(WSP) + CRLF) + OneOrMore(WSP)

ALPHADIGITPS = Word(alphanums + "+/")
base64string = ALPHADIGITPS + ZeroOrMore(Optional(FWS) + ALPHADIGITPS)

version = CaselessLiteral("v=1")
tval = Word(printables + " \t\r\n", exclude_chars=";")

tag_name = Word(alphas, alphanums + "_")

tag_value = Optional(Combine(tval | FWS | WSP) | base64string)  #  | WSP | FWS) + tval)

tag_spec = Group(
    Optional(FWS).suppress()
    + tag_name
    + Optional(FWS).suppress()
    + Literal("=").suppress()
    + Optional(FWS).suppress()
    + tag_value
    + Optional(FWS).suppress()
)
tag_lists = (
    tag_spec
    + Optional(OneOrMore(Literal(";").suppress() + tag_spec))
    + Optional(Literal(";")).suppress()
)

dkim_header_field = tag_lists + StringEnd()

dkim_txt_record = tag_lists + StringEnd()


class DKIMSignature(typing.TypedDict):
    v: str
    a: str
    b: str
    bh: str
    c: typing.NotRequired[str]
    d: str
    h: str
    i: typing.NotRequired[str]
    l: typing.NotRequired[int]  # noqa: E741
    q: typing.NotRequired[str]
    s: str
    t: typing.NotRequired[int]
    x: typing.NotRequired[int]
    z: typing.NotRequired[str]


_SIG_REQUIRED_FIELDS = {"v", "a", "b", "bh", "d", "h", "s"}
_DKIMAlgorithm = typing.Literal["rsa-sha1", "rsa-sha256", "ed25519-sha256"]
_CanonicalizationAlg = typing.Literal["simple", "relaxed"]


def _algorithm(alg: str) -> _DKIMAlgorithm:
    match alg:
        case "rsa-sha1" | "rsa-sha256" | "ed25519-sha256":
            return alg
        case _:
            raise ValueError(f"Unsupported algorithm {alg}")


def parse_dkim_header_field(data: str) -> DKIMSignature:
    sig: DKIMSignature = {}  # type: ignore
    for result in dkim_header_field.parse_string(data, parse_all=True).as_list():
        field = result[0]
        match field:
            case "v" | "a" | "b" | "bh" | "c" | "d" | "h" | "i" | "q" | "s" | "z":
                sig[field] = "".join(re.split(r"\s+", result[1]))
            case "l" | "t" | "x":
                try:
                    sig[field] = int(result[1])
                except ValueError as ve:
                    raise ValueError(f"Invalid field value {result=}") from ve
            case _:
                continue

    if (
        missing_fields := set(sig.keys()) & _SIG_REQUIRED_FIELDS
    ) != _SIG_REQUIRED_FIELDS:
        raise ValueError(f"Missing required fields {missing_fields=}")

    if (v := sig["v"]) != "1":
        raise ValueError(f"Invalid version tag {v=}")

    return sig


def _validate_canonicalization_algorithm(alg: str) -> _CanonicalizationAlg:
    match alg:
        case "simple" | "relaxed":
            return alg
        case _:
            raise ValueError("Invalid canonicalization algorithm {alg=}")


def _hash_from_alg(dkim_alg: _DKIMAlgorithm, data: bytes) -> bytes:
    match dkim_alg:
        case "rsa-sha1":
            return hashlib.sha1(data).digest()
        case "rsa-sha256" | "ed25519-sha256":
            return hashlib.sha256(data).digest()


def body_hash(
    body: emailsec.utils.Body,
    l: int | None,  # noqa: E741
    dkim_alg: _DKIMAlgorithm,
    alg: _CanonicalizationAlg,
) -> bytes:
    match alg:
        case "simple":
            if body.endswith(b"\r\n"):
                # Reduce CRLFs to a single one at the end
                canonicalized_body = re.sub(rb"(\r\n)+$", b"\r\n", body)
            else:
                # Or add a CRLF is there is none
                canonicalized_body = body + b"\r\n"
        case "relaxed":
            # Ignore all whitespace at the end of line without removing the
            # final CRLF
            canonicalized_body = re.sub(rb"[\x09\x20]+\r\n", b"\r\n", body)
            # Reduce all WSP (tab or space) sequence to a single space
            canonicalized_body = re.sub(rb"[\x09\x20]+", b" ", canonicalized_body)

            # Same treatment as for simple, reduce ending CRLFs to single one
            if canonicalized_body.endswith(b"\r\n"):
                canonicalized_body = re.sub(rb"(\r\n)+$", b"\r\n", canonicalized_body)
            else:
                # Or add one if missing
                canonicalized_body += b"\r\n"

    if l is not None:
        canonicalized_body = canonicalized_body[:l]

    return base64.b64encode(_hash_from_alg(dkim_alg, canonicalized_body))


class KeyInfo(typing.TypedDict):
    """https://datatracker.ietf.org/doc/html/rfc6376#section-3.6.1"""

    v: typing.NotRequired[str]
    n: typing.NotRequired[str]
    p: str | None
    k: typing.NotRequired[str]
    h: typing.NotRequired[str]


async def public_key_info(q: str | None, d: str, s: str) -> KeyInfo:
    if q and q != "dns/txt":
        raise ValueError(f"Invalid {q=}")

    key_info: KeyInfo = {}  # type: ignore
    resolver = DNSResolver()
    txt_records = await resolver.txt(f"{s}._domainkey.{d}")
    if txt_records:
        try:
            parsed_record = dkim_txt_record.parse_string(
                txt_records[0].text, parse_all=True
            )
        except pyparsing.ParseException as parse_error:
            raise ValueError(f"Invalid record {txt_records[0].text}") from parse_error

        for result in parsed_record.as_list():
            key = result[0]
            match key:
                case "p":
                    key_info["p"] = None if len(result) == 1 else result[1]
                case "v" | "n" | "k" | "h":
                    key_info[key] = result[1]
                case _:
                    continue
    else:
        raise ValueError(f"No TXT record found for {s}._domainkey.{d}")

    if "v" in key_info:
        if (v := key_info["v"]) != "DKIM1":
            raise ValueError(f"Unexpected version {v}")

    if "p" not in key_info:
        raise ValueError("Missing p")

    return key_info


def public_key(key_info: KeyInfo):
    if not key_info["p"]:
        raise ValueError(f"No key {key_info=}")

    k = key_info.get("k", "rsa")
    if k == "ed25519":
        return ed25519.Ed25519PublicKey.from_public_bytes(
            base64.b64decode(key_info["p"])
        )
    else:
        return load_der_public_key(base64.b64decode(key_info["p"]))


def canonicalize_headers(
    headers: list[tuple[bytes, bytes]], alg: _CanonicalizationAlg
) -> list[tuple[bytes, bytes]]:
    match alg:
        case "simple":
            return headers
        case "relaxed":
            canonicalized_headers = []
            for h, value in headers:
                # Unfold value (CLRF separation)
                value = re.sub(rb"\r?\n", b"", value)
                # Convert one more WSP to a single SP
                value = re.sub(rb"[\x09\x20]+", b" ", value)
                canonicalized_headers.append((h.lower().strip(), value.strip()))

            return canonicalized_headers


def _select_headers(
    headers_idx: emailsec.utils.Headers, hs: str
) -> list[emailsec.utils.Header]:
    # headers can appear multiple times, and they should be selected from
    # bottom to top
    # https://datatracker.ietf.org/doc/html/rfc6376#section-5.4.2
    headers_to_sign: list[emailsec.utils.Header] = []
    for h in hs.split(":"):
        if headers_idx.get(h.lower()):
            headers_to_sign.append(headers_idx[h.lower()].pop())

    return headers_to_sign


def headers_hash(
    headers_to_sign: list[emailsec.utils.Header],
    alg: _CanonicalizationAlg,
    sig_header: emailsec.utils.Header,
) -> bytes:
    canonicalized_headers = b""

    for bh, value in canonicalize_headers(headers_to_sign, alg):
        canonicalized_headers += (
            bh + b":" + value + (b"\r\n" if alg == "relaxed" else b"")
        )

    dkim_header_name, dkim_header_value = sig_header
    if alg == "relaxed":
        dkim_header_value = dkim_header_value.strip()
        dkim_header_value = re.sub(rb"(\n|\r)", b"", dkim_header_value)
        dkim_header_value = re.sub(rb"\s+", b" ", dkim_header_value)
        dkim_header_name = dkim_header_name.lower()

    canonicalized_dkim = dkim_header_name + b":" + dkim_header_value
    canonicalized_dkim = re.sub(rb"b=[\w0-9\s/+=]+", b"b=", canonicalized_dkim)
    canonicalized_headers += canonicalized_dkim.rstrip()
    return canonicalized_headers


class _DKIMStyleSig(typing.TypedDict):
    c: typing.NotRequired[str]
    a: str
    l: typing.NotRequired[int]
    h: str
    bh: typing.NotRequired[str]  # ARC seals are missing bh
    q: typing.NotRequired[str]
    d: str
    s: str
    t: typing.NotRequired[int]
    b: str


class _SigVerifier(typing.TypedDict):
    q: typing.NotRequired[str]
    d: str
    s: str
    t: typing.NotRequired[int]
    b: str
