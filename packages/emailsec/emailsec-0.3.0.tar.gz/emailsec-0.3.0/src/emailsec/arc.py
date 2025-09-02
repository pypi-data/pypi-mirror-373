from dataclasses import dataclass
import typing
import enum
import re

import emailsec.utils
from emailsec.dkim.checker import (
    _verify_sig,
    _verify_dkim_signature,
)
from emailsec.dkim.parser import (
    _algorithm,
    headers_hash,
    tag_lists,
    _DKIMStyleSig,
    _SigVerifier,
    _CanonicalizationAlg,
)
from emailsec.utils import body_and_headers_for_canonicalization

arc_message_signature = tag_lists
arc_seal = tag_lists


class ARCMessageSignature(typing.TypedDict):
    i: int
    a: str
    b: str
    bh: str
    c: typing.NotRequired[str]
    d: str
    h: str
    l: typing.NotRequired[int]  # noqa: E741
    q: typing.NotRequired[str]
    s: str
    t: typing.NotRequired[int]
    x: typing.NotRequired[int]
    z: typing.NotRequired[str]


class ARCSeal(typing.TypedDict):
    i: int
    a: str
    b: str
    d: str
    s: str
    cv: str
    t: typing.NotRequired[int]


_ARC_SEAL_REQUIRED_FIELDS = {"i", "a", "b", "d", "s", "cv"}
_ARC_MSG_SIG_REQUIRED_FIELDS = {"i", "a", "b", "bh", "d", "h", "s"}


class ARCChainStatus(enum.StrEnum):
    NONE = "none"
    FAIL = "fail"
    PASS = "pass"


@dataclass
class ARCCheck:
    result: ARCChainStatus
    exp: str
    signer: str | None = None
    aar_header: bytes | None = None


def parse_arc_seal(data: str) -> ARCSeal:
    sig: ARCSeal = {}  # type: ignore
    for result in arc_seal.parse_string(data, parse_all=True).as_list():
        field = result[0]
        match field:
            case "a" | "b" | "d" | "s" | "cv":
                sig[field] = "".join(re.split(r"\s+", result[1]))
            case "t" | "i":
                try:
                    sig[field] = int(result[1])
                except ValueError as ve:
                    raise ValueError(f"Invalid field value {result=}") from ve
            case "h":
                # https://datatracker.ietf.org/doc/html/rfc8617#section-4.1.3
                # must fail if h tag is found in seal
                raise ValueError("h tag not allowed")
            case _:
                continue
    if (
        missing_fields := set(sig.keys()) & _ARC_SEAL_REQUIRED_FIELDS
    ) != _ARC_SEAL_REQUIRED_FIELDS:
        raise ValueError(f"Missing required fields {missing_fields=}")

    return sig


def parse_arc_message_signature(data: str) -> ARCMessageSignature:
    sig: ARCMessageSignature = {}  # type: ignore
    for result in arc_message_signature.parse_string(data, parse_all=True).as_list():
        field = result[0]
        match field:
            case "a" | "b" | "bh" | "c" | "d" | "h" | "q" | "s" | "z":
                sig[field] = "".join(re.split(r"\s+", result[1]))
            case "l" | "t" | "x" | "i":
                try:
                    sig[field] = int(result[1])
                except ValueError as ve:
                    raise ValueError(f"Invalid field value {result=}") from ve
            case _:
                continue

    if missing_fields := _ARC_MSG_SIG_REQUIRED_FIELDS - set(sig.keys()):
        raise ValueError(f"Missing required fields {missing_fields=}")

    return sig


async def arc_seal_verify(
    arc_set_headers: tuple[
        emailsec.utils.Header, emailsec.utils.Header, emailsec.utils.Header
    ],
    sig: ARCSeal,
) -> bool:
    header_canonicalization: _CanonicalizationAlg = "relaxed"
    dkim_alg = _algorithm(sig["a"])

    # headers ordering: aar_header, ams_header, seal_header
    headers_to_sign = list(arc_set_headers[:2])
    # the ARC-Seal is treated differently as the body hash needs to be stripped
    sig_header = arc_set_headers[-1]
    canonicalized_message = headers_hash(
        headers_to_sign,
        header_canonicalization,
        sig_header,
    )
    return await _verify_sig(
        dkim_alg, typing.cast(_SigVerifier, sig), canonicalized_message
    )


_ARC_INSTANCE = re.compile(rb"\s?i\s*=\s*(\d+)", re.MULTILINE | re.IGNORECASE)


def _aar_instance(header_value: bytes) -> int:
    if (match := re.search(_ARC_INSTANCE, header_value)) is not None:
        return int(match.group(1))

    raise ValueError(f"Instance not found in {header_value=}")


async def check_arc(
    message: bytes, body_and_headers: emailsec.utils.BodyAndHeaders | None = None
) -> ARCCheck:
    if body_and_headers:
        body, headers = body_and_headers
    else:
        body, headers = body_and_headers_for_canonicalization(message)

    arc_message_signatures = headers.get("arc-message-signature")
    if not arc_message_signatures:
        return ARCCheck(ARCChainStatus.NONE, "No ARC Sets")
    arc_authentication_results = headers.get("arc-authentication-results", [])
    arc_seals = headers.get("arc-seal", [])

    if not (
        len(arc_message_signatures) == len(arc_authentication_results) == len(arc_seals)
    ):
        return ARCCheck(ARCChainStatus.FAIL, "Uneven ARC Sets")

    if len(arc_authentication_results) > 50:
        return ARCCheck(ARCChainStatus.FAIL, "Too many ARC Sets")

    parsed_ams = sorted(
        (
            (
                parse_arc_message_signature(value.decode()),
                (header_name, value),
            )
            for header_name, value in headers["arc-message-signature"]
        ),
        key=lambda x: x[0]["i"],
    )
    parsed_as = sorted(
        (
            (
                parse_arc_seal(value.decode()),
                (header_name, value),
            )
            for header_name, value in headers["arc-seal"]
        ),
        key=lambda x: x[0]["i"],
    )
    aars = sorted(
        (
            (
                _aar_instance(value),
                (header_name, value),
            )
            for header_name, value in headers["arc-authentication-results"]
        ),
        key=lambda x: x[0],
    )

    highest_validated_aar = None
    highest_validated_signer = None

    for instance in range(len(arc_message_signatures), 0, -1):
        ams, ams_header = parsed_ams.pop()
        if ams["i"] != instance:
            return ARCCheck(ARCChainStatus.FAIL, f"Cannot find AMS for {instance=}")

        seal, seal_header = parsed_as.pop()
        if seal["i"] != instance:
            return ARCCheck(ARCChainStatus.FAIL, f"Cannot find AS for {instance=}")

        aar_instance, aar_header = aars.pop()
        if aar_instance != instance:
            return ARCCheck(ARCChainStatus.FAIL, f"Cannot find AAR for {instance=}")

        if instance == 1 and seal["cv"] != "none":
            return ARCCheck(ARCChainStatus.FAIL, f"AMS cv must be none for {instance=}")
        elif instance > 1 and seal["cv"] != "pass":
            return ARCCheck(ARCChainStatus.FAIL, f"AMS cv fail for {instance=}")

        is_ams_valid = await _verify_dkim_signature(
            body, headers, ams_header, typing.cast(_DKIMStyleSig, ams)
        )
        if not is_ams_valid:
            return ARCCheck(ARCChainStatus.FAIL, f"Cannot verify AMS for {instance=}")

        arc_set_headers = (aar_header, ams_header, seal_header)

        is_seal_valid = await arc_seal_verify(arc_set_headers, seal)
        if not is_seal_valid:
            return ARCCheck(ARCChainStatus.FAIL, f"Cannot verify AS for {instance=}")

        if highest_validated_aar is None:
            highest_validated_aar = aar_header[1]
            highest_validated_signer = seal["d"]

    return ARCCheck(
        ARCChainStatus.PASS,
        "",
        signer=highest_validated_signer,
        aar_header=highest_validated_aar,
    )
