from dataclasses import dataclass
from functools import partial
import typing
import enum
from pycares import ares_query_a_result, ares_query_aaaa_result
import ipaddress
from . import parser as spf_parser
from .parser import parse_record, Qualifier
from .expander import Expander
from emailsec import errors
from emailsec.dns_resolver import DNSResolver

IPVersion = typing.Literal[4, 6]


class SPFResult(enum.StrEnum):
    NONE = "none"
    NEUTRAL = "neutral"
    PASS = "pass"
    FAIL = "fail"
    SOFTFAIL = "softfail"
    TEMPERROR = "temperror"
    PERMERROR = "permerror"

    @classmethod
    def from_qualifier(cls, q: Qualifier) -> "SPFResult":
        match q:
            case Qualifier.PASS:
                return cls.PASS
            case Qualifier.FAIL:
                return cls.FAIL
            case Qualifier.SOFTFAIL:
                return cls.SOFTFAIL
            case Qualifier.NEUTRAL:
                return cls.NEUTRAL


@dataclass
class SPFCheck:
    result: SPFResult
    domain: str
    sender_ip: str
    exp: str

    # TODO: figure out how to include the mechanism


async def _ip_networks_from_a_records(
    dns_resolver: DNSResolver, name: str, ip_version: IPVersion, cidr: str | None = None
) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    ip_networks = []

    query_results: list[ares_query_a_result] | list[ares_query_aaaa_result] | None
    if ip_version == 4:
        query_results = await dns_resolver.a(name)
    elif ip_version == 6:
        query_results = await dns_resolver.aaaa(name)

    if not query_results:
        return []

    for qres in query_results:
        print(f"{qres.host}/{cidr=}")
        ip_networks.append(ipaddress.ip_network(qres.host + (cidr or ""), False))

    return ip_networks


async def check_spf(sender_ip: str, sender: str) -> SPFCheck:
    parsed_ip = ipaddress.ip_address(sender_ip)
    if "@" not in sender:
        sender = f"postmaster@{sender}"
    domain = sender.split("@", maxsplit=1)[-1]

    result_builder = partial(SPFCheck, domain=domain, sender_ip=sender_ip)

    dns_resolver = DNSResolver()

    try:
        res, explanation = await _rec_check_host(
            dns_resolver, parsed_ip, sender, domain
        )
    except errors.Permerror as error:
        return result_builder(result=SPFResult.PERMERROR, exp=error.args[0])
    except errors.Temperror as error:
        return result_builder(result=SPFResult.TEMPERROR, exp=error.args[0])
    else:
        return result_builder(result=res, exp=explanation)


async def _rec_check_host(
    dns_resolver: DNSResolver,
    parsed_ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
    sender: str,
    domain: str,
    recursion=0,
) -> tuple[SPFResult, str]:
    if recursion > 10:
        raise errors.Permerror("Too much recursion")

    end_result = None

    expander = Expander(str(parsed_ip), sender, domain=domain)

    spfs = []
    txt_records = await dns_resolver.txt(domain)
    if not txt_records:
        return SPFResult.NONE, ""
    for txt_record in txt_records:
        if txt_record.text.lower().startswith("v=spf1 "):
            spfs.append(txt_record.text)
    print(spfs)
    if len(spfs) > 1:
        raise errors.Permerror("Too many SPF records")

    try:
        parsed_spf = parse_record(spfs[0])
    except ValueError:
        raise errors.Permerror(f"Failed to parse SPF record {spfs[0]!r}")

    modifiers = {}
    for mechanism in parsed_spf:
        match mechanism:
            case spf_parser.Modifier(name=name, value=value):
                modifiers[name] = value

            case spf_parser.All(qualifier=qualifier):
                end_result = SPFResult.from_qualifier(qualifier)
                break

            case spf_parser.Include():
                target_name = expander.expand(mechanism.domain_spec)
                # Recursive evaluation
                # https://datatracker.ietf.org/doc/html/rfc7208#section-5.2
                rec_result, _ = await _rec_check_host(
                    dns_resolver=dns_resolver,
                    parsed_ip=parsed_ip,
                    sender=sender,
                    domain=target_name,
                    recursion=recursion + 1,
                )
                match rec_result:
                    case SPFResult.PASS:
                        end_result = rec_result
                        break
                    case SPFResult.FAIL | SPFResult.SOFTFAIL | SPFResult.NEUTRAL:
                        continue
                    case SPFResult.TEMPERROR | SPFResult.PERMERROR | SPFResult.NONE:
                        end_result = SPFResult.PERMERROR
                        break

            case spf_parser.Exists():
                target_name = expander.expand(mechanism.domain_spec)
                if await dns_resolver.a(target_name):
                    end_result = SPFResult.from_qualifier(mechanism.qualifier)
                    break

            case spf_parser.A():
                target_name = (
                    expander.expand(mechanism.domain_spec)
                    if mechanism.domain_spec
                    else domain
                )
                ip_networks = await _ip_networks_from_a_records(
                    dns_resolver, target_name, parsed_ip.version, cidr=mechanism.cidr
                )
                if any(parsed_ip in ip_network for ip_network in ip_networks):
                    end_result = SPFResult.from_qualifier(mechanism.qualifier)
                    break

            case spf_parser.IP4() | spf_parser.IP6():
                if parsed_ip in mechanism.ip_network:
                    end_result = SPFResult.from_qualifier(mechanism.qualifier)
                    break

            case spf_parser.MX():
                target_name = (
                    expander.expand(mechanism.domain_spec)
                    if mechanism.domain_spec
                    else domain
                )
                for mx_record in (await dns_resolver.mx(target_name)) or []:
                    ip_networks = await _ip_networks_from_a_records(
                        dns_resolver,
                        mx_record.host,
                        parsed_ip.version,
                        cidr=mechanism.cidr,
                    )
                    print(
                        f"MX {parsed_spf=} {mx_record=}/{target_name=}/{ip_networks=}/{parsed_ip=}"
                    )
                    if any(parsed_ip in ip_network for ip_network in ip_networks):
                        end_result = SPFResult.from_qualifier(mechanism.qualifier)
                        break

                if end_result:
                    break

            case spf_parser.PTR():
                target_name = (
                    expander.expand(mechanism.domain_spec)
                    if mechanism.domain_spec
                    else domain
                )
                ptr_record = await dns_resolver.ptr(parsed_ip.reverse_pointer)
                if not ptr_record:
                    continue
                validated_domains = []
                for alias in ptr_record.aliases[:10]:
                    ip_networks = await _ip_networks_from_a_records(
                        dns_resolver, alias, parsed_ip.version
                    )
                    if any(parsed_ip in ip_network for ip_network in ip_networks):
                        validated_domains.append(alias)

                if target_name in validated_domains or any(
                    target_name.endswith(validated_domain)
                    for validated_domain in validated_domains
                ):
                    end_result = SPFResult.from_qualifier(mechanism.qualifier)
                    break

    if end_result is None and "redirect" in modifiers:
        # At this point, there's no "all" mechanism or it would have returned
        # while processing it
        rec_result, _ = await _rec_check_host(
            dns_resolver=dns_resolver,
            parsed_ip=parsed_ip,
            sender=sender,
            domain=expander.expand(modifiers["redirect"]),
            recursion=recursion + 1,
        )

    explanation = ""
    if end_result is SPFResult.FAIL and "exp" in modifiers:
        target_name = expander.expand(modifiers["exp"])
        try:
            txt_records = await dns_resolver.txt(target_name)
        except Exception:
            pass
        else:
            if txt_records:
                explanation = "".join(txt_record.text for txt_record in txt_records)

    # TODO: if result is "fail" look for the exp modifier

    if end_result:
        return end_result, explanation
    else:
        return SPFResult.NEUTRAL, ""
