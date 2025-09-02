from enum import StrEnum
import typing
from dataclasses import dataclass

import publicsuffixlist
from emailsec.dns_resolver import DNSResolver
from emailsec import errors

if typing.TYPE_CHECKING:
    from emailsec.spf.checker import SPFCheck
    from emailsec.dkim.checker import DKIMCheck
    from emailsec.arc import ARCCheck

AlignmentMode = typing.Literal["relaxed", "strict"]


class DMARCPolicy(StrEnum):
    NONE = "none"
    QUARANTINE = "quarantine"
    REJECT = "reject"


@dataclass
class DMARCRecord:
    policy: DMARCPolicy
    spf_mode: AlignmentMode
    dkim_mode: AlignmentMode
    # percentage: int


@dataclass
class DMARCResult:
    result: str  # pass, fail, none
    policy: DMARCPolicy
    spf_aligned: bool | None = None
    dkim_aligned: bool | None = None
    arc_override_applied: bool = False


async def get_dmarc_policy(domain: str) -> DMARCRecord | None:
    """Fetch DMARC policy according to RFC 7489 Section 6.1.

    Note that the spec does not include a temp error result, it will instead `errors.TempErrror`.
    """
    resolver = DNSResolver()
    try:
        txt_records = await resolver.txt(f"_dmarc.{domain}")
    except errors.Permerror:
        pass
    except errors.Temperror:
        raise
    else:
        if txt_records:
            try:
                return parse_dmarc_record(txt_records[0].text)
            except Exception:
                return None

    # RFC 7419 Section 6.6.3: "If the set is now empty, the Mail Receiver MUST query the DNS for
    # a DMARC TXT record at the DNS domain matching the Organizational
    # Domain in place of the RFC5322.From domain in the message (if
    # different).
    psl = publicsuffixlist.PublicSuffixList()
    organizational_domain = psl.privatesuffix(domain.lower()) or domain
    if organizational_domain != domain:
        try:
            txt_records = await resolver.txt(f"_dmarc.{organizational_domain}")
        except errors.Permerror:
            pass
        except errors.Temperror:
            raise
        else:
            if txt_records:
                try:
                    return parse_dmarc_record(txt_records[0].text)
                except Exception:
                    return None

    return None


def parse_dmarc_record(record: str) -> DMARCRecord:
    tags = {}
    for part in record.split(";"):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            tags[key.strip()] = value.strip()

    if "v" not in tags:
        raise ValueError("Missing mandatory v=DMARC1 tag")

    if tags["v"] != "DMARC1":
        raise ValueError(f"Invalid DMARC version: {tags['v']}, expected DMARC1")

    if "p" not in tags:
        raise ValueError("Missing mandatory p= tag")

    return DMARCRecord(
        policy=DMARCPolicy(tags.get("p", "none")),
        spf_mode="strict" if tags.get("aspf") == "s" else "relaxed",
        dkim_mode="strict" if tags.get("adkim") == "s" else "relaxed",
        # percentage=int(tags.get('pct', '100'))
    )


def is_spf_aligned(
    rfc5312_mail_from: str,
    rfc5322_from: str,
    mode: AlignmentMode = "relaxed",
) -> bool:
    match mode:
        case "strict":
            return rfc5312_mail_from.lower() == rfc5322_from.lower()
        case "relaxed":
            psl = publicsuffixlist.PublicSuffixList()
            return psl.privatesuffix(rfc5312_mail_from) == psl.privatesuffix(
                rfc5322_from
            )


def is_dkim_aligned(
    dkim_domain: str,
    rfc5322_from: str,
    mode: AlignmentMode = "relaxed",
) -> bool:
    match mode:
        case "strict":
            return dkim_domain.lower() == rfc5322_from.lower()
        case "relaxed":
            psl = publicsuffixlist.PublicSuffixList()
            return psl.privatesuffix(dkim_domain) == psl.privatesuffix(rfc5322_from)


async def check_dmarc(
    header_from: str,
    envelope_from: str,
    spf_check: "SPFCheck",
    dkim_check: "DKIMCheck",
    arc_check: "ARCCheck",
    configuration: typing.Any = None,
) -> DMARCResult:
    """
    DMARC evaluation per RFC 7489 Section 3 (Identifier Alignment).

    RFC 7489: "A message satisfies the DMARC checks if at least one of the supported
    authentication mechanisms: 1. produces a 'pass' result, and 2. produces that
    result based on an identifier that is in alignment"
    """
    # Import here to avoid circular imports
    from emailsec.spf.checker import SPFResult
    from emailsec.dkim.checker import DKIMResult
    from emailsec.arc import ARCChainStatus
    from emailsec.authentication_results import extract_original_auth_results

    # Get DMARC policy (RFC 7489 Section 6.1)
    dmarc_policy = await get_dmarc_policy(header_from)
    if not dmarc_policy:
        return DMARCResult(result="none", policy=DMARCPolicy.NONE)

    # Check identifier alignment (RFC 7489 Section 3.1)
    # SPF alignment: envelope sender domain vs header from domain
    spf_aligned = spf_check.result == SPFResult.PASS and is_spf_aligned(
        envelope_from, header_from, dmarc_policy.spf_mode
    )

    # DKIM alignment: signing domain (d=) vs header from domain
    dkim_aligned = bool(
        dkim_check.result == DKIMResult.SUCCESS
        and dkim_check.domain
        and is_dkim_aligned(dkim_check.domain, header_from, dmarc_policy.dkim_mode)
    )

    # RFC 7489: DMARC passes if either SPF or DKIM is aligned and passes
    dmarc_pass = spf_aligned or dkim_aligned

    # ARC override logic (RFC 8617 Section 7.2.1)
    # RFC 8617: "a DMARC processor MAY choose to accept the authentication
    # assessments provided by an Authenticated Received Chain"
    arc_override_applied = False
    if (
        not dmarc_pass
        and configuration
        and hasattr(configuration, "trusted_signers")
        and configuration.trusted_signers
        and arc_check.signer in configuration.trusted_signers
        and arc_check.result == ARCChainStatus.PASS
        and arc_check.aar_header
    ):
        parsed_aar = extract_original_auth_results(
            arc_check.result, arc_check.aar_header
        )
        if parsed_aar and "dmarc" in parsed_aar and parsed_aar["dmarc"] == "pass":
            dmarc_pass = True
            arc_override_applied = True

    return DMARCResult(
        result="pass" if dmarc_pass else "fail",
        policy=dmarc_policy.policy,
        spf_aligned=spf_aligned,
        dkim_aligned=dkim_aligned,
        arc_override_applied=arc_override_applied,
    )
