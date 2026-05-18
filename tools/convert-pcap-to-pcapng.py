#!/usr/bin/env python3
"""Convert a tcpdump pcap file to pcapng while preserving packet timestamps."""

from __future__ import annotations

import argparse

from scapy.utils import RawPcapReader, RawPcapNgWriter


def convert(source: str, destination: str, interface_name: bytes = b"en0") -> int:
    reader = RawPcapReader(source)
    writer = RawPcapNgWriter(destination)
    writer.linktype = reader.linktype
    writer._write_header(None)

    count = 0
    try:
        for packet, metadata in reader:
            timestamp = metadata.sec + metadata.usec / 1_000_000
            writer._write_packet(
                packet,
                reader.linktype,
                sec=timestamp,
                caplen=metadata.caplen,
                wirelen=metadata.wirelen,
                ifname=interface_name,
            )
            count += 1
    finally:
        writer.close()
        reader.close()

    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--interface", default="en0")
    args = parser.parse_args()

    count = convert(args.source, args.destination, args.interface.encode("utf-8"))
    print(f"Converted {count} packets.")


if __name__ == "__main__":
    main()
