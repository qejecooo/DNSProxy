import socket

from dnslib import DNSRecord, RCODE, QTYPE
from dnslib.server import BaseResolver


class ProxyResolver(BaseResolver):
    def __init__(self, address, port, timeout=0, strip_aaaa=False):
        self.address = address
        self.port = port
        self.timeout = timeout
        self.strip_aaaa = strip_aaaa

    def resolve(self, request, handler):
        """
        Resolve request using upstream DNS server
        :param request: client`s DNS request
        :param handler: DNSHandler instance
        :return: reply from upstream DNS server
        """
        try:
            if self.strip_aaaa and request.q.qtype == QTYPE.AAAA:
                reply = request.reply()
                reply.header.rcode = RCODE.NXDOMAIN
            else:
                if handler.protocol == 'udp':
                    proxy_r = request.send(self.address, self.port,
                                           timeout=self.timeout)
                else:
                    proxy_r = request.send(self.address, self.port,
                                           tcp=True, timeout=self.timeout)
                reply = DNSRecord.parse(proxy_r)
        except socket.timeout:
            reply = request.reply()
            reply.header.rcode = getattr(RCODE, 'NXDOMAIN')
        return reply
