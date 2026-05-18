# DNS resolution path

**Question:** Can I tie a DNS answer to the TCP connection that uses it?

Capture file: `../captures/02-dns-resolution.pcapng`

## How the capture was made

Target: `info.cern.ch`; local resolver: `192.168.2.1`; returned address:
`188.184.67.127`.

```zsh
dumpcap -i en0 -s 0 \
  -w captures/02-dns-resolution.pcapng \
  -a duration:8 \
  -f \
  "(udp port 53 or tcp port 53 or host 188.184.67.127)"

dig @192.168.2.1 info.cern.ch A

curl -4 --http1.1 --no-keepalive \
  --resolve info.cern.ch:80:188.184.67.127 \
  http://info.cern.ch/
```

`dig` forces the DNS query into the capture. The curl command pins the TCP
connection to the same address returned by the query.

## What to look at in Wireshark

DNS filter:

```text
dns && dns.qry.name == "info.cern.ch"
```

The workstation asks the local resolver for an A record:

```text
192.168.2.100 -> 192.168.2.1  A? info.cern.ch
192.168.2.1 -> 192.168.2.100  CNAME webafs902.cern.ch, A 188.184.67.127
```

TCP filter:

```text
ip.addr == 188.184.67.127 && tcp.port == 80
```

The next connection goes to the returned IP:

```text
192.168.2.100:58074 -> 188.184.67.127:80  SYN
188.184.67.127:80 -> 192.168.2.100:58074  SYN-ACK
192.168.2.100:58074 -> 188.184.67.127:80  ACK
192.168.2.100:58074 -> 188.184.67.127:80  HTTP GET /
```

The DNS response is transaction `0x0d14` at `17:17:00.555887-0400`. The SYN to
`188.184.67.127` follows about 16.6 ms later. The DNS answer does not move user
data by itself; it supplies the address used by the transport-layer connection.

One capture wrinkle is visible later in the stream: Wireshark marks frame 8 as
`TCP Previous segment not captured`, then sees the HTTP `200 OK` as a
retransmission in frame 10. That does not change the DNS-to-TCP relationship,
but it is a useful reminder that packet captures can have their own gaps.

## Wireshark screenshots

![DNS query and answer](../screenshots/02-dns-query-response.png)

![TCP connection to resolved address](../screenshots/02-dns-to-tcp.png)

![HTTP request after resolution](../screenshots/02-dns-http-request.png)
