import typing
from dataclasses import dataclass
import re
import pyparsing
import enum
from pyparsing import (
    CaselessLiteral,
    Combine,
    Optional,
    Literal,
    Regex,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
    nums,
    printables,
)
from pyparsing import pyparsing_common
import ipaddress


class Qualifier(enum.StrEnum):
    PASS = "+"
    FAIL = "-"
    SOFTFAIL = "~"
    NEUTRAL = "?"


@dataclass
class Modifier:
    name: str
    value: str

    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        data = parse_result.as_dict()
        return cls(
            name=data["name"],
            value=data["value"],
        )


@dataclass(kw_only=True)
class _BaseMechanism:
    qualifier: Qualifier = Qualifier.PASS


@dataclass
class All(_BaseMechanism):
    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        return cls()


@dataclass
class MX(_BaseMechanism):
    domain_spec: str | None
    cidr: str | None

    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        data = parse_result[0].as_dict()
        return cls(
            domain_spec=data.get("domain_spec"),
            cidr=data.get("cidr"),
        )


@dataclass
class A(_BaseMechanism):
    domain_spec: str | None
    cidr: str | None

    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        data = parse_result[0].as_dict()
        return cls(
            domain_spec=data.get("domain_spec"),
            cidr=data.get("cidr"),
        )


@dataclass
class _BaseIP(_BaseMechanism):
    ip_network: ipaddress.IPv4Network | ipaddress.IPv6Network

    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        data = parse_result.as_dict()
        try:
            return cls(
                ip_network=ipaddress.ip_network(
                    data["ip_address"] + data.get("cidr", "")
                )
            )
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            raise pyparsing.ParseException(f"Invalid IP network {data=}")


@dataclass
class IP4(_BaseIP):
    pass


@dataclass
class IP6(_BaseIP):
    pass


@dataclass
class _MechanismWithRequiredDomainSpec(_BaseMechanism):
    domain_spec: str

    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        data = parse_result.as_dict()
        return cls(
            domain_spec=data["domain_spec"],
        )


@dataclass
class Include(_MechanismWithRequiredDomainSpec):
    pass


@dataclass
class Exists(_MechanismWithRequiredDomainSpec):
    pass


@dataclass
class PTR(_BaseMechanism):
    domain_spec: str | None

    @classmethod
    def from_parse_results(cls, parse_result: pyparsing.ParseResults) -> typing.Self:
        data = parse_result.as_dict()
        return cls(
            domain_spec=data.get("domain_spec"),
        )


macro_string_regex = re.compile(
    (
        r"%{(?P<letter>[slodipvhcrt])"
        r"(?P<count>(\d+))?"
        r"(?P<reverse>(r))?"
        r"(?P<delimiter>([\.\-\+,\/_=]))?}"
    ),
    re.IGNORECASE,
)


version = CaselessLiteral("v=spf1")
qualifier = Word("+-?~", exact=1)
name = Word(alphas, alphanums + "-_.")

dual_cidr_length = Combine(Literal("/") + Word(nums))

macro_literal = Word(printables, exact=1, exclude_chars="%")
macro_expand = Regex(macro_string_regex) | Literal("%%") | Literal("%_") | Literal("%-")

domain_end = (
    Combine(Literal(".") + Word(alphanums + "-") + Optional(Literal(".")))
    | macro_expand
)

macro_string = Combine(
    ZeroOrMore(macro_expand | macro_literal, stop_on=dual_cidr_length)
)


def _check_domain_end(toks: pyparsing.ParseResults) -> None:
    domain_end = toks[0].removesuffix(".")
    if "." in domain_end:
        top_label = domain_end.split(".")[-1]
    else:
        top_label = domain_end

    if not top_label:
        raise pyparsing.ParseException("empty label")

    try:
        # Is the top label a macro expand
        macro_expand.parse_string(top_label, parse_all=True)
    except pyparsing.ParseException:
        # Or a valid RFC1035/1123 DNS label
        if not re.match(r"^(?!-)[a-zA-Z0-9-_]{1,63}(?<!-)$", top_label):
            raise pyparsing.ParseException("invalid top label")

    return None


domain_spec = macro_string.set_parse_action(_check_domain_end)


all_ = CaselessLiteral("all").set_parse_action(All.from_parse_results)

include = (
    CaselessLiteral("include:").suppress() + domain_spec.set_results_name("domain_spec")
).set_parse_action(Include.from_parse_results)

ip4_cidr_length = Combine(Literal("/") + Regex("3[0-2]|2[0-9]|1[0-9]|[1-9]"))
ip4 = (
    CaselessLiteral("ip4:").suppress()
    + pyparsing_common.ipv4_address.set_results_name("ip_address")
    + Optional(ip4_cidr_length).set_results_name("cidr")
).set_parse_action(IP4.from_parse_results)

ip6_cidr_length = Literal("/") + Word(nums)
ip6 = (
    CaselessLiteral("ip6:").suppress()
    + pyparsing_common.ipv6_address.set_results_name("ip_address")
    + Optional(ip6_cidr_length).set_results_name("cidr")
).set_parse_action(IP6.from_parse_results)

a = pyparsing.Group(
    CaselessLiteral("a").suppress()
    + Optional(
        pyparsing.ungroup(Literal(":").suppress() + domain_spec)
    ).set_results_name("domain_spec")
    + Optional(dual_cidr_length).set_results_name("cidr")
).set_parse_action(A.from_parse_results)


mx = pyparsing.Group(
    CaselessLiteral("mx").suppress()
    + Optional(
        pyparsing.ungroup(Literal(":").suppress() + domain_spec)
    ).set_results_name("domain_spec")
    + Optional(dual_cidr_length).set_results_name("cidr")
).set_parse_action(MX.from_parse_results)

ptr = (
    CaselessLiteral("ptr").suppress()
    + Optional(
        pyparsing.ungroup(Literal(":").suppress() + domain_spec)
    ).set_results_name("domain_spec")
).set_parse_action(PTR.from_parse_results)

exists = (
    CaselessLiteral("exists:").suppress() + domain_spec.set_results_name("domain_spec")
).set_parse_action(lambda toks: Exists(toks))

unknown_modifier = (
    name.set_results_name("name")
    + Literal("=").suppress()
    + name.set_results_name("value")
)
redirect = (
    CaselessLiteral("redirect").set_results_name("name")
    + Literal("=").suppress()
    + domain_spec.set_results_name("value")
)
exp = (
    CaselessLiteral("exp").set_results_name("name")
    + Literal("=").suppress()
    + domain_spec.set_results_name("value")
)
modifiers = (redirect | exp | unknown_modifier).set_parse_action(
    Modifier.from_parse_results
)


def _merge_qualifier(toks):
    group = toks[0]
    if len(group) == 2:
        group[1].qualifier = Qualifier(group[0])
        return group[1]
    return toks


mechanism = pyparsing.ungroup(
    pyparsing.Group(
        Optional(qualifier) + (all_ | include | ip4 | ip6 | a | mx | ptr | exists)
    ).set_parse_action(_merge_qualifier)
)
record = version.suppress() + ZeroOrMore(mechanism | modifiers)

Mechanism = typing.TypeVar("Mechanism", bound=_BaseMechanism)


def parse_record(rec: str) -> list[Mechanism | Modifier]:
    try:
        return record.parse_string(rec, parse_all=True).as_list()
    except pyparsing.ParseException as parse_error:
        raise ValueError(f"Invalid record {rec!r}") from parse_error
