#!/usr/bin/env python3

import sys
import zlib
from argparse import ArgumentParser

import intelhex


def ti_cc23xx_offsets():
    # ccfg starts at:
    offset = 0x4E020000
    # data from https://www.ti.com/lit/ug/swcu193a/swcu193a.pdf table 9-2 CRC Locations
    sections = [
        (0x0, 0xC),
        (0x10, 0x74C),
        (0x750, 0x7CC),
        (0x7D0, 0x7FC),
    ]
    return [(offset + start, offset + end, offset + end) for start, end in sections]


def crc32_calculate_and_insert(handle, start: int, end: int, dest):
    CRC_LEN = 4
    maxend = handle.maxaddr() + 1 - CRC_LEN

    assert end > start, "end address must be after start address"
    assert start >= handle.minaddr(), f"start not inside file {start} < {handle.minaddr()}"
    assert end <= handle.maxaddr(), f"end not inside file {start} < {handle.maxaddr()}"
    assert dest <= maxend, f"destination not inside file {dest} > {maxend}"
    assert dest <= start - CRC_LEN or dest >= end, "crc would overwrite data"

    data = handle.gets(start, end - start)
    crc = (zlib.crc32(data) & 0xFFFFFFFF).to_bytes(CRC_LEN, "little")
    handle.puts(dest, crc)


def hex_crc_insert(filename: str, offsets: list):
    handle = intelhex.IntelHex()
    format = filename.split(".")[-1]
    handle.loadfile(filename, format=format)

    for start, end, dest in offsets:
        crc32_calculate_and_insert(handle, start, end, dest)

    handle.tofile(filename, format=format)


def parse_and_run(argv) -> int:
    crc32sums = []

    parser = ArgumentParser(prog=argv[0])
    parser.add_argument("filename", type=str, help="File to process")
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        default="none",
        choices=["none", "ti_cc23xx"],
        help="use predefined modifications for device",
    )
    parser.add_argument(
        "-c",
        "--crc32",
        action="append",
        type=str,
        help="start,end,dest: calculate crc32 from start till end and write it to dest. Can be given multple times.",
    )

    args = parser.parse_args(argv[1:])

    if args.device == "ti_cc23xx":
        crc32sums.extend(ti_cc23xx_offsets())

    if args.crc32:
        for offset in args.crc32:
            start, end, dest = offset.split(",")
            crc32sums.append((int(start, 0), int(end, 0), int(dest, 0)))

    if len(crc32sums) == 0:
        print("There are no crc32sums to be calculated. Aborting!")
        return -1

    hex_crc_insert(args.filename, crc32sums)
    return 0


def main():
    sys.exit(parse_and_run(sys.argv))


if __name__ == "__main__":
    main()
