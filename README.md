# <b>DNSProxy</b><br/><br/>

This is a DNS Proxy server that supports black list and written in Python using dnslib library.
This proxy server supports both TCP and UDP and can run them at both time. 
It supports all main package types such as:<br/>
<b>A</b> - IPv4 address<br/>
<b>AAAA</b> - IPv6 address<br/>
<b>NS</b> - Name server<br/>
<b>CNAME</b> - Canonical name<br/>
<b>SOA</b> - Start of authority<br/>
<b>MX</b> - Mail exchange<br/>
<b>SRV</b> - Service record<br/>

# <b>How does it work?</b><br/>
<br/>
User sends a DNS request to the proxy server.<br/><br/>
This request is handled by handler, where the request is checked against the black list.<br/>
If it is, the second check is made to see if we need to resolve the request to a different IP address.<br/><br/>
If the IP address where to resolve is in config file, we return the response packet with the new IP address.<br/>
If not, we return the response packet with no IP address.<br/>
If domain in not in black list, we send the request to the upstream DNS Server and return the response packet.<br/>
<br/>

The first thing to do is to specify upstream DNS server in config file(or you can pass it as a command line argument).<br/>
Then you can specify black list file in config file(if needed).<br/>
<br/>
Then the server can be started by running the following command: <b>sudo python3 main.py</b><br/>
In this particular case the server will run on its default port (53) and will listen on all addresses,
upstreaming the queries to configfile upstream server address. Only UDP datagrams will be accepted.<br/>

# <b>Flags:</b><br/>
<b>-p, --port</b>: Local proxy port (default: 53)<br/>
<b>-a, --address</b>: Local proxy address (default: all)<br/>
<b>-u, --upstream</b>: Upstream DNS server address ( IP:PORT format (default: None) )<br/>
<b>--tcp</b>: Enable TCP connections listening (default: False)<br/>
<b>--timeout</b>: Upstream server timeout (default: 5)<br/>
<b>--strip-aaaa</b>: Returns NXDOMAIN for AAAA queries(default: off) 
<br/>*this arg is used with resolver. 
Since we use PassThroughDNSHandler to send packets directly to upstream server, this flag makes no difference <br/>
<b>--log</b>: Log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)<br/>
<b>--log-prefix</b>: Log prefix (timestamp/handler/resolver) (default: False)<br/>
