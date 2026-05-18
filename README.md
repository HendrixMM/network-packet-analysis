# Network Packet Analysis with Wireshark

Packet-level walkthroughs of four common protocol interactions captured on
macOS. Each scenario starts with a narrow question and answers it from the
capture rather than from a protocol diagram.

## Scenarios

1. **TCP connection lifecycle**: a single HTTPS connection to GitHub, including
   SYN, SYN-ACK, ACK, encrypted TLS records, and connection teardown.
2. **DNS resolution path**: a DNS A-record query to the local resolver followed
   by the TCP connection to the returned address.
3. **ARP resolution**: link-layer address resolution before an ICMP exchange on
   the local network.
4. **HTTP vs HTTPS payload visibility**: the same host over ports 80 and 443,
   showing cleartext HTTP headers beside encrypted TLS application data.

## Repository layout

- `captures/`: packet captures in `.pcapng` format
- `writeups/`: short analysis notes tied to the captures
- `screenshots/`: Wireshark GUI screenshots referenced from the writeups
- `tools/`: small helper used to convert tcpdump `.pcap` files to `.pcapng`

## Reproducing

Open any file in `captures/` with Wireshark 4.x. The writeups include the
capture command, traffic trigger, and display filters used for each scenario.

These captures were taken on `en0` from macOS with `tcpdump`, then converted to
pcapng. No custom dissectors were used.

## Notes

Packet capture on macOS requires access to `/dev/bpf*`. If capture fails with a
permission error, run the following from Terminal:

```zsh
sudo chgrp admin /dev/bpf*
sudo chmod g+rw /dev/bpf*
```
