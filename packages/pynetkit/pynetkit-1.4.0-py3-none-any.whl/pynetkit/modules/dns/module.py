#  Copyright (c) Kuba Szczodrzyński 2024-10-8.

from collections import defaultdict
from ipaddress import IPv4Address
from typing import Callable

from dnslib import QTYPE, RCODE, RDMAP, RR, DNSQuestion, DNSRecord
from dnslib.server import BaseResolver, DNSHandler, DNSServer

from pynetkit.modules.base import ModuleBase
from pynetkit.util.misc import matches

from .events import DnsQueryEvent


class DnsModule(ModuleBase, BaseResolver):
    PRE_RUN_CONFIG = ["address", "port"]
    # pre-run configuration
    address: IPv4Address
    port: int
    # runtime configuration
    dns_db: list[
        tuple[str, str, list[str | RR]] | Callable[[str, str], list[str | RR]]
    ] = None
    # runtime status
    queries: dict[IPv4Address, dict[tuple[str, str], int]] = None
    # server handle
    _dns: DNSServer | None = None

    def __init__(self):
        super().__init__()
        self.address = IPv4Address("0.0.0.0")
        self.port = 53
        self.dns_db = []

    async def run(self) -> None:
        self.info(f"Starting DNS server on {self.address}:{self.port}")
        self.queries = {}
        self._dns = DNSServer(
            resolver=self,
            address=str(self.address),
            port=self.port,
        )
        # disable dnslib logging
        self._dns.server.logger.logf = lambda *_: None
        while self.should_run and self._dns is not None:
            self._dns.start()

    async def stop(self) -> None:
        self.should_run = False
        await self.cleanup()
        await super().stop()

    async def cleanup(self) -> None:
        if self._dns:
            self._dns.stop()
            self._dns.server.server_close()
        self._dns = None

    def resolve(self, request: DNSRecord, handler: DNSHandler | None) -> DNSRecord:
        address: IPv4Address | None = None
        if handler and handler.client_address:
            address = IPv4Address(handler.client_address[0])

        reply: DNSRecord = request.reply()
        has_response = False
        has_nxdomain = False
        for q in request.questions:
            q: DNSQuestion

            # resolve the question
            qname = str(q.qname).rstrip(".")
            qtype = QTYPE[q.qtype]
            if qname.endswith(".local") or qname.endswith(".mshome.net"):
                continue
            for handler in self.dns_db:
                if callable(handler):
                    rdata = handler(qname, qtype)
                    if rdata is not None:
                        has_response = True
                        break
                else:
                    rname, rtype, rdata = handler
                    if matches(rname, qname) and matches(rtype, qtype):
                        has_response = True
                        break
            else:
                self.warning(f"No DNS zone for {qtype} {qname}")
                DnsQueryEvent(address, qname, qtype, rdata=[]).broadcast()
                continue

            self.debug(f"Answering DNS request {qtype} {qname}")
            DnsQueryEvent(address, qname, qtype, rdata=rdata).broadcast()

            if address:
                # increment query count if client address is available
                if address not in self.queries:
                    self.queries[address] = defaultdict(int)
                self.queries[address][qname, qtype] += 1

            # send a reply
            for rr in rdata:
                if rr == "NXDOMAIN":
                    has_nxdomain = True
                    continue
                if not isinstance(rr, RR):
                    rr = RR(
                        rname=q.qname,
                        rtype=q.qtype,
                        rdata=RDMAP[qtype](rr),
                    )
                reply.add_answer(rr)
        if not has_response or has_nxdomain:
            reply.header.rcode = RCODE.NXDOMAIN
        return reply

    @staticmethod
    def resolve_upstream(
        upstream: IPv4Address,
        qname: str,
        qtype: str,
    ) -> list[RR]:
        question = DNSRecord.question(qname, qtype)
        reply_bytes = question.send(str(upstream), port=53, tcp=False, timeout=2.0)
        reply = DNSRecord.parse(reply_bytes)
        return reply.rr

    def add_record(
        self,
        name: str,
        type: str,
        answer: str | IPv4Address,
    ) -> None:
        self.dns_db.append((name, type, [str(answer)]))

    def add_upstream(
        self,
        upstream: IPv4Address,
        rname: str = ".*",
        rtype: str = ".*",
    ) -> Callable:
        def handler(qname: str, qtype: str) -> list[RR] | None:
            if matches(rname, qname) and matches(rtype, qtype):
                return self.resolve_upstream(upstream, qname, qtype)
            return None

        self.dns_db.append(handler)
        return handler

    def clear_records(self) -> None:
        self.dns_db = []
