import struct

from dnslib import DNSRecord, DNSHeader, RR, QTYPE, A
from dnslib.server import DNSHandler

from send_packet import send_tcp, send_udp


class PassthroughDNSHandler(DNSHandler):
    def get_reply(self, data: bytes) -> bytes:
        """
        Method to send data directly to upstream DNS server and parse reply from it
            :param data: The DNS packet to send.
            :return: The response from the upstream DNS server.
        """
        host, port = self.server.resolver.address, self.server.resolver.port

        request = DNSRecord.parse(data)
        domain = str(request.q.qname)[:-1]
        black_list = self.server.resolver.black_list
        self.server.logger.log_request(self, request)

        if domain in black_list.keys():
            if black_list[domain] == "":
                print("Not resolved: " + domain)
                response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
                return response.pack()

            response = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
                                 q=request.q, a=RR(domain, QTYPE.A, rdata=A(black_list[domain])))

            self.server.logger.log_reply(self, response)
            return response.pack()

        if self.protocol == 'tcp':
            data = struct.pack("!H", len(data)) + data
            response = send_tcp(data, host, port)
            response = response[2:]
        else:
            response = send_udp(data, host, port)

        reply = DNSRecord.parse(response)
        self.server.logger.log_reply(self, reply)

        return response
