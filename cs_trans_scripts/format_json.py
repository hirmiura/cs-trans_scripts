#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# ルーズJSONをピュアJSONに変換する

from __future__ import annotations

import argparse
import json
import sys
import time

import dirtyjson

# 何故かcredits.jsonにBOMが付いている
ENC = "utf-8-sig"


def pargs():
    parser = argparse.ArgumentParser(description="ルーズJSONをピュアJSONに変換する")
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
        print(f"読み込み中: {f}", file=sys.stderr)
        t_sta = time.perf_counter()
        with open(f, encoding=ENC) as fp:
            js = dirtyjson.load(fp)
        t_dlt = time.perf_counter() - t_sta
        print(f"  {t_dlt}秒", file=sys.stderr)
        json.dump(js, sys.stdout, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
