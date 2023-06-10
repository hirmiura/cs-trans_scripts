#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# JSON PointerのリストでフィルターしたJSON Patchを返す

from __future__ import annotations

import argparse
import io
import json
import sys
import typing

ENC = "utf-8-sig"


def pargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JSON PointerのリストでフィルターしたJSON Patchを返す")
    parser.add_argument(
        "-p",
        dest="pointer_file",
        help="JSONポインターのリストの書かれたファイル",
    )
    parser.add_argument(
        dest="files",
        nargs="+",
        help="フィルターをかけるJSONパッチファイル",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    args = parser.parse_args()
    return args


def main() -> None:
    args = pargs()
    pointers = parse_pointer_file(args.pointer_file)
    patches = parse_patches(pointers, args.files)
    json.dump(patches, sys.stdout, ensure_ascii=False, indent=4)


def parse_pointer_file(file: str) -> list:
    fp: io.TextIOWrapper | typing.TextIO
    if file:
        fp = open(file, encoding=ENC)
    else:
        fp = sys.stdin
    plist = [line.rstrip() for line in fp if line]
    fp.close()
    return plist


def parse_patches(pointers: list, files: list) -> list:
    result = []
    for f in files:
        with open(f, encoding=ENC) as fp:
            js = json.load(fp)
        for patchlist in js:
            for pt in pointers:
                if match_pointer_patch(pt, patchlist):
                    result.append(patchlist)
                    break
    return result


def match_pointer_patch(pointer: str, patch: dict) -> bool:
    if pointer == patch["path"]:
        return True
    return False


if __name__ == "__main__":
    main()
