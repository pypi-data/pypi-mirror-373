from dataclasses import dataclass
from pyparsing import (
    Word,
    alphas,
    alphanums,
    nums,
    Literal,
    Optional,
    Group,
    OneOrMore,
    QuotedString,
    ZeroOrMore,
    printables,
    Suppress,
    White,
    ParseException,
)

from emailsec.arc import ARCChainStatus

# RFC 8601 ABNF components following the specification
WSP = White(" \t", exact=1)
CRLF = White("\r", exact=1) + White("\n", exact=1)
FWS = Optional(ZeroOrMore(WSP) + CRLF) + OneOrMore(WSP)

authserv_id = Word(alphanums + ".-_")
method = Word(alphas, alphanums + "-")
result = Word(alphas)
ptype = Word(alphas)
dot_atom_text = Word(alphanums + ".-_")
# More flexible value that can handle email addresses and other real-world content
value = Word(printables, exclude_chars=";") | QuotedString('"', escChar="\\")

property = Group(
    Optional(FWS).suppress()
    + ptype
    + Literal(".").suppress()
    + dot_atom_text
    + Optional(FWS).suppress()
    + Literal("=").suppress()
    + Optional(FWS).suppress()
    + value
    + Optional(FWS).suppress()
)

resinfo = Group(
    Optional(FWS).suppress()
    + method
    + Optional(FWS).suppress()
    + Literal("=").suppress()
    + Optional(FWS).suppress()
    + result
    + Optional(FWS).suppress()
    + ZeroOrMore(property)
)

instance_tag = Suppress("i=") + Word(nums)

arc_auth_results = (
    Optional(instance_tag)
    + Suppress(Optional(";"))
    + Optional(FWS).suppress()
    + authserv_id
    + Optional(FWS).suppress()
    + Suppress(";")
    + Optional(FWS).suppress()
    + OneOrMore(resinfo + Suppress(Optional(";")))
)


@dataclass
class AuthResult:
    """Single authentication method result"""

    method: str  # spf, dkim, dmarc, arc
    result: str  # pass, fail, temperror, etc
    properties: dict[str, str]  # smtp.mailfrom, header.d, etc


@dataclass
class ARCAuthenticationResults:
    """Parsed ARC-Authentication-Results header (RFC 8617 Section 4.1.1)"""

    instance: int
    authserv_id: str
    results: list[AuthResult]


def normalize_header(header_value: str) -> str:
    """
    Pre-process header value to normalize multi-line properties and remove problematic whitespace.

    This handles real-world cases like:
    - Multi-line property values (e.g., smtp.mailfrom=value\ncontinued)
    - Comments in parentheses
    - Extra whitespace and newlines
    """
    if not header_value:
        return header_value

    # Split into lines and process each line
    lines = header_value.split("\n")
    normalized_parts: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # If this line starts with a property continuation (no method=result pattern)
        if not ("=" in line and not line.startswith(" ") and not line.startswith("\t")):
            # This might be a continuation of a previous property value
            if normalized_parts and "=" in normalized_parts[-1]:
                # Append to the last property value
                normalized_parts[-1] += " " + line
            else:
                normalized_parts.append(line)
        else:
            # This is a new method=result or property
            normalized_parts.append(line)

    # Join all parts and clean up extra whitespace
    normalized = " ".join(normalized_parts)

    # Remove comments in parentheses (RFC 8601 doesn't specify these)
    import re

    normalized = re.sub(r"\([^)]*\)", "", normalized)

    # Clean up extra whitespace around semicolons and equals
    normalized = re.sub(r"\s*;\s*", ";", normalized)
    normalized = re.sub(r"\s*=\s*", "=", normalized)

    # Clean up multiple spaces
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def parse_arc_authentication_results(header_value: str) -> ARCAuthenticationResults:
    """
    Parse ARC-Authentication-Results header per RFC 8617 Section 4.1.1.

    Format: i=1; authserv-id; method=result property=value
    Example: i=1; mx.example.com; spf=pass smtp.mailfrom=example.org;
             dkim=pass header.d=example.org
    """
    try:
        if not header_value or not header_value.strip():
            raise ValueError("Empty header value")

        # Pre-process the header to normalize multi-line properties
        normalized_header = normalize_header(header_value)

        parsed = arc_auth_results.parse_string(normalized_header)

        # Extract components
        instance = 1
        authserv_id = None
        results = []

        for item in parsed:
            if isinstance(item, str) and item.isdigit():
                instance = int(item)
            elif isinstance(item, str) and item.strip() and authserv_id is None:
                authserv_id = item.strip()
            elif hasattr(item, "as_list"):
                # This is a resinfo group
                resinfo_list = item.as_list()
                if len(resinfo_list) >= 2:
                    method = resinfo_list[0]
                    result = resinfo_list[1]

                    properties = {}
                    for i in range(2, len(resinfo_list)):
                        if (
                            isinstance(resinfo_list[i], list)
                            and len(resinfo_list[i]) >= 3
                        ):
                            # This is a property group: [ptype, dot_atom_text, value]
                            prop_list = resinfo_list[i]
                            prop_name = (
                                prop_list[0] + "." + prop_list[1]
                            )  # ptype.dot_atom_text
                            prop_value = prop_list[2]
                            properties[prop_name] = prop_value

                    results.append(
                        AuthResult(method=method, result=result, properties=properties)
                    )

        # Ensure authserv_id is always a string (default to empty string if None)
        if authserv_id is None:
            authserv_id = ""

        return ARCAuthenticationResults(
            instance=instance, authserv_id=authserv_id, results=results
        )
    except ParseException as e:
        raise ValueError(f"Invalid ARC-Authentication-Results: {e}")
    except Exception as e:
        raise ValueError(f"Invalid ARC-Authentication-Results: {e}")


def extract_original_auth_results(
    arc_chain_status: ARCChainStatus, aar_header: bytes
) -> dict[str, str] | None:
    """
    Extract trusted authentication results from ARC chain.

    Per RFC 8617 Section 7.2: "If the ARC chain validates, the Authentication-Results
    from the ARC-Authentication-Results header field SHOULD be considered equivalent
    to locally performed authentication checks."
    """
    if arc_chain_status != ARCChainStatus.PASS:
        return None

    try:
        parsed = parse_arc_authentication_results(aar_header.decode())

        # Extract key results for DMARC override consideration
        auth_results = {}
        for result in parsed.results:
            if result.method in ["spf", "dkim", "dmarc"]:
                auth_results[result.method] = result.result
                # Could also extract properties like smtp.mailfrom, header.d

        return auth_results
    except Exception:
        return None
