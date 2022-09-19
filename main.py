import json
import argparse, time
import handler

from dnslib.server import DNSServer, DNSLogger
from resolver import ProxyResolver


def main():
    with open("config.json", "r") as read_file:
        config_file = json.load(read_file)

        black_list = config_file.get("black_list")
        local_dns_server = config_file.get("local_dns_server")
        upstream_server = config_file.get("upstream_server")

    parser = argparse.ArgumentParser(description="DNS Proxy")
    parser.add_argument("--port", "-p", type=int, default=53,
                        metavar="<port>",
                        help="Local proxy port (default:53)")
    parser.add_argument("--address", "-a", default="",
                        metavar="<address>",
                        help="Local proxy listen address (default:all)")
    parser.add_argument("--upstream", "-u",
                        metavar="<dns server:port>",
                        help="Upstream DNS server:port")
    parser.add_argument("--tcp", action='store_true', default=False,
                        help="TCP proxy (default: UDP only)")
    parser.add_argument("--timeout", "-o", type=float, default=5,
                        metavar="<timeout>",
                        help="Upstream timeout (default: 5s)")
    parser.add_argument("--strip-aaaa", action='store_true', default=False,
                        help="Return NXDOMAIN for AAAA queries (default: off)")
    parser.add_argument("--log", default="request,reply,truncated,error",
                        help="Log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)")
    parser.add_argument("--log-prefix", action='store_true', default=False,
                        help="Log prefix (timestamp/handler/resolver) (default: False)")
    args = parser.parse_args()

    if args.upstream and ":" in args.upstream:
        dns_addr = args.upstream.split(":")
        args.dns = dns_addr[0]
        args.dns_port = int(dns_addr[1])
    else:
        args.dns = upstream_server["ip"]
        args.dns_port = upstream_server["port"]

    if local_dns_server and args.address == "" and args.port == 53:
        args.address = local_dns_server["ip"]
        args.port = local_dns_server["port"]

    print("Starting Proxy Resolver (%s:%d -> %s:%d) [%s]" % (
        args.address or "*", args.port,
        args.dns, args.dns_port,
        "UDP/TCP" if args.tcp else "UDP"))

    resolver = ProxyResolver(args.dns, args.dns_port, args.timeout, args.strip_aaaa, black_list)
    logger = DNSLogger(args.log, prefix=args.log_prefix)

    udp_server = DNSServer(resolver,
                           port=args.port,
                           address=args.address,
                           logger=logger,
                           handler=handler.PassthroughDNSHandler
                           )
    udp_server.start_thread()

    if args.tcp:
        tcp_server = DNSServer(resolver,
                               port=args.port,
                               address=args.address,
                               tcp=True,
                               logger=logger,
                               handler=handler.PassthroughDNSHandler
                               )
        tcp_server.start_thread()

    while udp_server.isAlive():
        time.sleep(1)


if __name__ == '__main__':
    main()
