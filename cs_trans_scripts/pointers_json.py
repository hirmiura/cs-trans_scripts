#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# JSONファイルを走査して、全てのJSON Pointerを列挙する

from __future__ import annotations

import argparse
import json

ENC = "utf-8-sig"


def pargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JSONファイルからJSON Pointerのリストを作成する")
    parser.add_argument(
        dest="files",
        nargs="+",
        help="ファイル",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    args = parser.parse_args()
    return args


def main() -> None:
    args = pargs()
    for f in args.files:
        with open(f, encoding=ENC) as fp:
            js = json.load(fp)
        parse(js)


def parse(obj) -> None:
    pointer = [""]
    _parse(obj, pointer)


def _parse(obj, pointer: list) -> None:
    match obj:
        case list():
            parse_list(obj, pointer)
        case dict():
            parse_dict(obj, pointer)
        case _:
            print("/".join(pointer))


def parse_list(obj: list, pointer: list) -> None:
    for i, item in enumerate(obj):
        new_pointer = pointer + [str(i)]
        _parse(item, new_pointer)


def parse_dict(obj: dict, pointer: list) -> None:
    for k, v in obj.items():
        new_pointer = pointer + [str(k)]
        _parse(v, new_pointer)


if __name__ == "__main__":
    main()
