from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cleaner import CleanOptions, cleanse_and_parse, clean_json_text


def _read_stdin_bytes() -> bytes:
    data = sys.stdin.buffer.read()
    return data


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="API由来の汚いJSONをクレンジング/パース/保存します")
    p.add_argument("input", nargs="?", help="入力ファイルパス。省略時はstdinから読み込み")
    p.add_argument("-o", "--output", help="出力ファイルパス(JSONとして保存)")
    p.add_argument("--raw", action="store_true", help="パースせずクレンジング済みJSON文字列を出力")
    p.add_argument("--indent", type=int, default=2, help="保存/表示時のインデント(デフォルト:2)")
    p.add_argument("--no-ascii", action="store_true", help="保存時にensure_ascii=Falseで日本語をそのまま保存")
    p.add_argument("--no-json5", action="store_true", help="JSON5互換のフォールバックを無効化（厳密モード）")

    args = p.parse_args(argv)

    if args.input:
        data: bytes = Path(args.input).read_bytes()
    else:
        data = _read_stdin_bytes()

    opts = CleanOptions(indent=args.indent, allow_json5=not args.no_json5)

    if args.raw:
        text = clean_json_text(data, options=opts)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0

    obj = cleanse_and_parse(data, options=opts)

    if args.output:
        from .cleaner import save_json

        save_json(obj, args.output, ensure_ascii=not args.no_ascii, indent=args.indent)
        return 0

    # 標準出力にきれいなJSONを表示
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
