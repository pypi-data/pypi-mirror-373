import asyncio
import typing

from emailsec import errors

import aiodns
import pycares

_MAX_LOOKUPS = 10


class DNSResolver:
    def __init__(self) -> None:
        self.__lookups_counter = 0
        self.__resolver = aiodns.DNSResolver(loop=asyncio.get_running_loop())

    async def _query(self, name: str, query_type: str) -> typing.Any:
        self.__lookups_counter += 1
        if self.__lookups_counter > _MAX_LOOKUPS:
            raise errors.Permerror("Max DNS lookups exceeded")

        try:
            return await self.__resolver.query(name, query_type)
        except aiodns.error.DNSError as dns_error:
            error_msg = dns_error.args[1]
            match dns_error.args[0]:
                case aiodns.error.ARES_ENOTFOUND | aiodns.error.ARES_ENODATA:  # type: ignore
                    return None
                case (
                    aiodns.error.ARES_EBADQUERY  # type: ignore
                    | aiodns.error.ARES_EFORMERR  # type: ignore
                    | aiodns.error.ARES_EBADNAME  # type: ignore
                    | aiodns.error.ARES_EBADRESP  # type: ignore
                ):
                    raise errors.Permerror(
                        f"DNS error (code {dns_error.args[0]}): {error_msg}"
                    )
                case _:
                    raise errors.Temperror(
                        f"DNS error (code {dns_error.args[0]}): {error_msg}"
                    )

    async def txt(self, name: str) -> list[pycares.ares_query_txt_result] | None:
        return await self._query(name, "TXT")

    async def mx(self, name: str) -> list[pycares.ares_query_mx_result] | None:
        return await self._query(name, "MX")

    async def a(self, name: str) -> list[pycares.ares_query_a_result] | None:
        return await self._query(name, "A")

    async def aaaa(self, name: str) -> list[pycares.ares_query_aaaa_result] | None:
        return await self._query(name, "AAAA")

    async def ptr(self, name: str) -> pycares.ares_query_ptr_result | None:
        return await self._query(name, "PTR")
