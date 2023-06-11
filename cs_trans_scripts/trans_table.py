#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# 2つのJSONパッチファイルを走査して、翻訳テーブルを作成する

from __future__ import annotations

import argparse
import json
import sys

ENC = "utf-8"


def pargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="2つのJSONパッチファイルを走査して、翻訳テーブルを作成する")
    parser.add_argument(
        dest="file1",
        help="ファイル1",
    )
    parser.add_argument(
        dest="file2",
        help="ファイル2",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    args = parser.parse_args()
    return args


def main() -> None:
    args = pargs()
    dic1 = parse_json_patch(args.file1)
    dic2 = parse_json_patch(args.file2)
    trans_table = create_table(dic1, dic2)
    json.dump(trans_table, sys.stdout, ensure_ascii=False, indent=4)


def parse_json_patch(file: str) -> dict:
    with open(file, encoding=ENC) as fp:
        js = json.load(fp)
    result = {}
    for item in js:
        if item["op"] == "replace":
            path = item["path"]
            if path in result:
                print(f"\a\x1b[93mpath({path})の重複があります\x1b[0m", file=sys.stderr, flush=True)
            result[path] = item["value"]
    return result


def create_table(dic1: dict, dic2: dict) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for k, v1 in dic1.items():
        if k in dic2:
            v2 = dic2[k]
            if v1 != v2:
                if v1 not in result:
                    result[v1] = [v2]
                elif v2 not in result[v1]:
                    print(f"\a\x1b[93m異なる翻訳({v1})があります\x1b[0m", file=sys.stderr, flush=True)
                    result[v1].append(v2)
    return result


if __name__ == "__main__":
    main()
