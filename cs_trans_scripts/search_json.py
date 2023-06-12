#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# JSONファイルを検索して、一致したJSON Pointerを返す

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from typing import TypeAlias

import jsonpointer
from jsonpointer import JsonPointer

ENC = "utf-8-sig"
Ptr: TypeAlias = list[str]


def search(doc, value, ptr_filter="") -> list[JsonPointer]:
    ptr: Ptr = [""]
    cmp_filter = re.compile(ptr_filter) if ptr_filter else None
    result = _search(doc, value, cmp_filter, ptr)
    return result


def _search(doc, value, cmp_ptr_filter, curPtr: Ptr) -> list[JsonPointer]:
    result = []
    doSearch = True
    strptr = ptr_to_str(curPtr)
    if cmp_ptr_filter:
        if not cmp_ptr_filter.search(strptr):
            doSearch = False
    if doSearch and doc == value:
        result.append(JsonPointer(strptr))

    match doc:
        case str():
            pass
        case Sequence():
            for num, subDoc in enumerate(doc):
                subResult = _search(subDoc, value, cmp_ptr_filter, curPtr + [str(num)])
                result.extend(subResult)
        case Mapping():
            for key, subDoc in doc.items():
                subResult = _search(subDoc, value, cmp_ptr_filter, curPtr + [str(key)])
                result.extend(subResult)

    return result


def ptr_to_str(ptr: Ptr) -> str:
    escaped = []
    for p in ptr:
        escaped.append(jsonpointer.escape(p))
    return "/".join(escaped)


def pargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JSONファイルを検索して、一致したJSON Pointerを返す")
    parser.add_argument(
        "-f",
        dest="filter",
        help="検索するJSONポインターに一致する正規表現",
    )
    parser.add_argument(
        dest="value",
        help="検索する文字列(完全一致)",
    )
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
        subRes = search(js, args.value, args.filter)
        for r in subRes:
            print(r.path)


if __name__ == "__main__":
    main()
