#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2023 hirmiura (https://github.com/hirmiura)
#
# CS形式のJSONを読み込んでリストを辞書に変換する

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Mapping, Sequence
from typing import Any

import dirtyjson

ENC_F = "utf-8-sig"

KEY_ID = "id"
TARGET_KEYS = [
    "achievements",
    # "alt",
    "arriving",
    "betrayal",
    "consequences",
    "cultures",
    "decks",
    "dicta",
    "elements",
    "endings",
    "epiphany",
    "epiphany.colonel",
    "epiphany.lionsmith",
    "failure",
    "fatiguing",
    "induces",
    "inductions",
    "killmortal",
    "legacies",
    "legcies",
    "levers",
    # "linked",
    "mortal.introduce",
    "opx.progress0",
    "opx.progress1",
    "opx.progress2",
    "portals",
    "recipes",
    "rkx.promote",
    "settings",
    "slots",
    "striking.foe",
    "striking.foe.weapon",
    "striking.underling",
    "striking.underling.weapon",
    "success",
    "upgrade.exile.ally",
    "verbs",
]

CC_MATCH = "\033[32m"
CC_WARN = "\033[33m"
CC_RESET = "\033[0m"

args: argparse.Namespace | None = None


def pargs() -> argparse.Namespace:
    global args
    parser = argparse.ArgumentParser(description="CS形式のJSONを読み込んでリストを辞書に変換する")
    parser.add_argument(
        "-d",
        dest="denormalize",
        action="store_true",
        help="逆変換",
    )
    parser.add_argument(
        "-t",
        dest="time",
        action="store_true",
        help="時間表示",
    )
    parser.add_argument(
        "-p",
        dest="progress",
        action="store_true",
        help="進捗表示",
    )
    parser.add_argument(
        dest="file",
        help="ファイル",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    args = parser.parse_args()
    return args


def main() -> None:
    args = pargs()
    json_doc = read_json(args.file)
    if args and args.time:
        print("変換中: ", end="", file=sys.stderr)
        t_sta = time.perf_counter()
    if args.denormalize:
        result = denormalize(json_doc)
    else:
        result = normalize(json_doc)
    if args and args.time:
        t_dlt = time.perf_counter() - t_sta
        print(f"\n  {t_dlt}秒", file=sys.stderr)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=4)


def read_json(file) -> Any:
    """JSONファイルを読み込む

    Args:
        file (_type_): ファイル

    Returns:
        Any: JSONオブジェクト
    """
    global args
    if args and args.time:
        print(f"読込中: {file}", file=sys.stderr)
        t_sta = time.perf_counter()
    with open(file, encoding=ENC_F) as fp:
        json_doc = dirtyjson.load(fp)
    if args and args.time:
        t_dlt = time.perf_counter() - t_sta
        print(f"  {t_dlt}秒", file=sys.stderr)
    return json_doc


def normalize(jobj, _parent_key=None) -> Any:
    result: Any = None
    match jobj:
        case Mapping():
            result = {}
            for k, v in jobj.items():
                progress("+")
                result[k] = normalize(v, k)
        case Sequence() if not isinstance(jobj, str):
            if match_target_keys(_parent_key):
                if len(jobj) > 0 and isinstance(jobj[0], dict) and KEY_ID in jobj[0]:
                    result = {}
                    for v in jobj:
                        id = v[KEY_ID]
                        if id in result:
                            print(
                                f"\a{CC_WARN}id({id})の重複があります{CC_RESET}",
                                file=sys.stderr,
                                flush=True,
                            )
                        progress(f"{CC_MATCH}+{CC_RESET}")
                        result[id] = normalize(v)
                else:
                    result = []
                    print(
                        f"{CC_WARN}{_parent_key}/{KEY_ID}が見つかりません{CC_RESET}",
                        file=sys.stderr,
                        flush=True,
                    )
                    for v in jobj:
                        progress("-")
                        result.append(normalize(v))
            else:
                result = []
                for v in jobj:
                    progress("-")
                    result.append(normalize(v))
        case _:
            progress(".")
            result = jobj
    return result


def denormalize(jobj) -> Any:
    result: Any = None
    match jobj:
        case Mapping():
            result = {}
            for k, v in jobj.items():
                if match_target_keys(k) and isinstance(v, dict):
                    result[k] = []
                    for vv in v.values():
                        progress(f"{CC_MATCH}-{CC_RESET}")
                        result[k].append(denormalize(vv))
                else:
                    progress("+")
                    result[k] = denormalize(v)
        case Sequence() if not isinstance(jobj, str):
            result = []
            for v in jobj:
                progress("-")
                result.append(denormalize(v))
        case _:
            progress(".")
            result = jobj
    return result


def match_target_keys(key) -> bool:
    if key is None:
        return False
    if key in TARGET_KEYS:
        return True
    return False


def progress(bar="+", output=sys.stderr):
    global args
    if args and args.progress:
        print(bar, end="", file=output, flush=True)


if __name__ == "__main__":
    main()
