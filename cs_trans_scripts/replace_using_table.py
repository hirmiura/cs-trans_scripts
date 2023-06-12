#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# JSONファイルを検索して、一致した値を置き換える

from __future__ import annotations

import argparse
import json
import sys
from typing import TypeAlias

from cs_trans_scripts import search_json

ENC = "utf-8-sig"

ReplaceTable: TypeAlias = dict[str, list[str]]


def replace(doc, table: ReplaceTable, ptr_filter="^(?!(.*/)?id$)") -> None:
    for k, v in table.items():
        ptrs = search_json.search(doc, k, ptr_filter)
        for p in ptrs:
            p.set(doc, v[0])


def pargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JSONファイルを検索して、一致した値を置き換える")
    parser.add_argument(
        "-f",
        dest="filter",
        help="検索するJSONポインターに一致する正規表現",
    )
    parser.add_argument(
        dest="table",
        help="置換テーブル",
    )
    parser.add_argument(
        dest="files",
        nargs="+",
        help="対象ファイル",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    args = parser.parse_args()
    return args


def main() -> None:
    args = pargs()
    with open(args.table, encoding=ENC) as fp:
        table = json.load(fp)
    for f in args.files:
        with open(f, encoding=ENC) as fp:
            js = json.load(fp)
        replace(js, table, args.filter or "^(?!(.*/)?id$)")
        json.dump(js, sys.stdout, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
