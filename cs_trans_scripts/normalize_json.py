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

ENC = "utf-8"

ID = "id"
SLOTS = "slots"


def pargs():
    parser = argparse.ArgumentParser(description="IDでハッシュ化する")
    parser.add_argument(
        "-d",
        dest="denormalize",
        action="store_true",
        help="逆変換",
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
    if args.denormalize:
        denormalize(args.files)
    else:
        normalize(args.files)


def normalize(files: list) -> dict:
    result: dict = {}
    for f in files:
        print(f"読み込み中: {f}", file=sys.stderr)
        t_sta = time.perf_counter()
        with open(f, encoding=ENC) as fp:
            js = json.load(fp)
        for ty, li in js.items():
            print("|", end="", file=sys.stderr, flush=True)
            if ty not in result:
                result[ty] = {}
            for item in li:
                print(".", end="", file=sys.stderr, flush=True)
                id = item[ID]
                if id in result[ty]:
                    print(f"\n  \a\x1b[93mid({id})の重複があります\x1b[0m", file=sys.stderr, flush=True)
                result[ty][id] = item
                # slots
                if SLOTS in item and isinstance(item[SLOTS], list):
                    newslots = {}
                    for slotitem in item[SLOTS]:
                        print(",", end="", file=sys.stderr, flush=True)
                        slotid = slotitem[ID]
                        if slotid in newslots:
                            print(
                                f"\n  \a\x1b[93mid({slotid})の重複があります\x1b[0m",
                                file=sys.stderr,
                                flush=True,
                            )
                        newslots[slotid] = slotitem
                    result[ty][id][SLOTS] = newslots

        t_dlt = time.perf_counter() - t_sta
        print(f"\n  {t_dlt}秒", file=sys.stderr)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=4)
    return result


def denormalize(files: list) -> dict:
    result: dict = {}
    for f in files:
        print(f"読み込み中: {f}", file=sys.stderr)
        t_sta = time.perf_counter()
        with open(f, encoding=ENC) as fp:
            js = json.load(fp)
        for ty, dic in js.items():
            print("|", end="", file=sys.stderr, flush=True)
            if ty not in result:
                result[ty] = []
            for item in dic.values():
                print(".", end="", file=sys.stderr, flush=True)
                if SLOTS in item:
                    newslots = []
                    for slotitem in item[SLOTS].values():
                        print(",", end="", file=sys.stderr, flush=True)
                        newslots.append(slotitem)
                    item[SLOTS] = newslots
                result[ty].append(item)
        t_dlt = time.perf_counter() - t_sta
        print(f"\n  {t_dlt}秒", file=sys.stderr)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=4)
    return result


if __name__ == "__main__":
    main()
