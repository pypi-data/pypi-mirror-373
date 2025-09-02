"""Macros related helpers as defined in RFC7208:
https://datatracker.ietf.org/doc/html/rfc7208#section-7"""

import time
import ipaddress
import re

macro_string_regex = re.compile(
    (
        r"%{(?P<letter>[slodipvhcrt])"
        r"(?P<count>(\d+))?"
        r"(?P<reverse>(r))?"
        r"(?P<delimiter>([\.\-\+,\/_=]))?}"
    ),
    re.IGNORECASE,
)


class Expander:
    def __init__(
        self, ip: str, sender: str, domain: str | None = None, exp_mode: bool = False
    ) -> None:
        self.ip = ip
        self.parsed_ip = ipaddress.ip_address(ip)
        self.domain = domain if domain else sender.split("@", maxsplit=1)[-1]
        self.sender = sender
        self.exp_mode = exp_mode

    def expand(self, value: str) -> str:
        if "%" not in value:
            return value

        # Handle special cases first
        value = value.replace("%_", " ").replace("%-", "%20").replace("%%", "%")

        # Then look for regular macro strings
        for match in re.finditer(macro_string_regex, value):
            gd = match.groupdict()
            res = self.expand_letter(gd["letter"])
            if gd["reverse"] or gd["count"] or gd["delimiter"]:
                delimiter = gd["delimiter"] or "."
                parts = res.split(delimiter)

                if gd["reverse"]:
                    parts = parts[::-1]

                count = int(gd["count"]) if gd["count"] else len(parts)
                res = ".".join(parts[-count:])

            value = value.replace(match.group(), res, 1)

        return value

    def expand_letter(self, macro: str) -> str:
        match macro.lower():
            case "s":
                return self.sender
            case "l":
                return self.sender.split("@", maxsplit=1)[0]
            case "o":
                return self.sender.split("@", maxsplit=1)[1]
            case "d":
                return self.domain
            case "i":
                if self.parsed_ip.version == 4:
                    return self.ip
                else:
                    return self.parsed_ip.reverse_pointer.removesuffix(".ip6.arpa")[
                        ::-1
                    ]
            case "p":
                #  p = the validated domain name of <ip> (do not use)
                raise NotImplementedError()
            case "v":
                # v = the string "in-addr" if <ip> is ipv4, or "ip6" if <ip> is ipv6
                if self.parsed_ip.version == 4:
                    return "in-addr"
                else:
                    return "ip6"
            case "h":
                # h = HELO/EHLO domain
                # TODO: implement
                raise NotImplementedError()
            case "c":
                if not self.exp_mode:
                    raise ValueError("c only allowed in exp mode")
                return self.ip
            case "r":
                # The "r" macro expands to the name of the receiving MTA.
                # TODO: implement
                return "unknown"
            case "t":
                if not self.exp_mode:
                    raise ValueError("c only allowed in exp mode")
                # Timestamp
                return str(int(time.time()))

        raise RuntimeError()
