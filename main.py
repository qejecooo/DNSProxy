from __future__ import print_function
import json

import handler as handler
from handler import PassthroughDNSHandler

from dnslib.server import DNSServer, DNSLogger
from resolver import ProxyResolver


if __name__ == '__main__':
    import argparse, time

    with open("config.json", "r") as read_file:
        config_file = json.load(read_file)
        black_list = config_file["black_list"]
        upstream_server = config_file["upstream_server"]

    handler.black_list = black_list

    p = argparse.ArgumentParser(description="DNS Proxy")
    p.add_argument("--port", "-p", type=int, default=53,
                   metavar="<port>",
                   help="Local proxy port (default:53)")
    p.add_argument("--address", "-a", default="",
                   metavar="<address>",
                   help="Local proxy listen address (default:all)")
    p.add_argument("--upstream", "-u",
                   metavar="<dns server:port>",
                   help="Upstream DNS server:port")
    p.add_argument("--tcp", action='store_true', default=False,
                   help="TCP proxy (default: UDP only)")
    p.add_argument("--timeout", "-o", type=float, default=5,
                   metavar="<timeout>",
                   help="Upstream timeout (default: 5s)")
    p.add_argument("--strip-aaaa", action='store_true', default=False,
                   help="Return NXDOMAIN for AAAA queries (default: off)")
    p.add_argument("--log", default="request,reply,truncated,error",
                   help="Log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)")
    p.add_argument("--log-prefix", action='store_true', default=False,
                   help="Log prefix (timestamp/handler/resolver) (default: False)")
    args = p.parse_args()

    try:
        args.dns, _, args.dns_port = args.upstream.partition(':')
    except AttributeError:
        args.dns = upstream_server
        args.dns_port = 53

    args.dns_port = int(args.dns_port)

    print("Starting Proxy Resolver (%s:%d -> %s:%d) [%s]" % (
        args.address or "*", args.port,
        args.dns, args.dns_port,
        "UDP/TCP" if args.tcp else "UDP"))

    resolver = ProxyResolver(args.dns, args.dns_port, args.timeout, args.strip_aaaa)
    handler = PassthroughDNSHandler
    logger = DNSLogger(args.log, prefix=args.log_prefix)

    udp_server = DNSServer(resolver,
                           port=args.port,
                           address=args.address,
                           logger=logger,
                           handler=handler
                           )
    udp_server.start_thread()

    if args.tcp:
        tcp_server = DNSServer(resolver,
                               port=args.port,
                               address=args.address,
                               tcp=True,
                               logger=logger,
                               handler=handler
                              )
        tcp_server.start_thread()

    while udp_server.isAlive():
        time.sleep(1)
