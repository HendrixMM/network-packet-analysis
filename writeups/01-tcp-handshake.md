# TCP connection lifecycle

**Question:** Can I identify a TCP session from setup through teardown and point
to where TLS begins?

Capture file: `../captures/01-tcp-handshake.pcapng`

## How the capture was made

Target: `github.com` resolved to `140.82.113.4`.

```zsh
dumpcap -i en0 -s 0 \
  -w captures/01-tcp-handshake.pcapng \
  -a duration:8 \
  -f \
  "host 140.82.113.4 and tcp port 443"

curl -4 --http1.1 --no-keepalive \
  --resolve github.com:443:140.82.113.4 \
  https://github.com/HendrixMM
```

`dumpcap` wrote the capture as native pcapng. `capinfos` reports one interface
block for `en0`, with the first packet at `2026-05-18T17:13:09.256337-0400`.

## What to look at in Wireshark

Display filter:

```text
ip.addr == 140.82.113.4 && tcp.port == 443
```

The first three packets are the TCP handshake:

```text
192.168.2.100:58048 -> 140.82.113.4:443  SYN, win 65535, seq 0
140.82.113.4:443 -> 192.168.2.100:58048  SYN-ACK, win 65535, ack 1
192.168.2.100:58048 -> 140.82.113.4:443  ACK, win 132480
```

After the ACK, frame 4 is a `PSH, ACK` carrying a 317-byte TLS Client Hello.
The PSH flag means the sender asked TCP to push the bytes up to the receiving
application promptly; it does not change the TLS interpretation. Frame 5 is the
server's `Server Hello, Change Cipher Spec, Application Data`, followed by more
TLSv1.3 Application Data records.

Teardown starts when the client sends FIN:

```text
192.168.2.100:58048 -> 140.82.113.4:443  FIN-ACK
140.82.113.4:443 -> 192.168.2.100:58048  FIN-ACK
192.168.2.100:58048 -> 140.82.113.4:443  RST
```

The reset is frame 190, `0.382824` seconds after the first SYN, after both
sides have already exchanged FINs. I would not treat that as a failed
connection; the HTTP request completed and curl closed the socket.

## Wireshark screenshots

![TCP handshake](../screenshots/01-tcp-handshake.png)

![TLS records after TCP setup](../screenshots/01-tls-records.png)

![TCP teardown](../screenshots/01-tcp-teardown.png)
