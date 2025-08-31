from __future__ import annotations

import json
import sys
import subprocess
from pathlib import Path

import pytest

from api_json_cleaner import clean_json_text, cleanse_and_parse, parse
from api_json_cleaner.cleaner import CleanOptions


def test_parse_basic_cleanup():
    # BOM + 未クォートキー + 末尾カンマ + 制御文字混入
    dirty = b"\xef\xbb\xbf\x01{\n  \"list\": [1,2,3,], unquoted_key: \"\xe5\x80\xa4\"\n}"
    obj = cleanse_and_parse(dirty)
    assert obj["list"] == [1, 2, 3]
    assert obj["unquoted_key"] == "値"


def test_html_entity_unescape_after_parse():
    s = '{"text": "A &quot;B&quot; &amp; C"}'
    obj = cleanse_and_parse(s)
    assert obj["text"] == 'A "B" & C'


def test_japanese_wave_tilde_normalization():
    # FULLWIDTH TILDE(FF5E), TILDE OPERATOR(223C) → WAVE DASH(301C)
    s = '{"s": "～∼"}'  # FF5E + 223C
    obj = cleanse_and_parse(s)
    assert obj["s"] == "〜〜"  # 301C x2


def test_prolonged_sound_mark_normalization():
    # カナ文脈のダッシュを長音符に
    s = '{"s": "コ-ヒ-"}'
    obj = cleanse_and_parse(s)
    assert obj["s"] == "コーヒー"


def test_json5_fallback_comment_single_quote_trailing_comma():
    # コメント/単一引用符/末尾カンマ
    txt = """
// comment
{
  'a': 1,
}
"""
    obj = cleanse_and_parse(txt)
    assert obj == {"a": 1}


def test_yen_backslash_conversion_backslash_to_yen():
    # 値中のバックスラッシュを円記号へ
    s = '{"p": "C:\\\\\\path"}'  # "C:\\path"
    opts = CleanOptions(yen_backslash="backslash-to-yen")
    obj = cleanse_and_parse(s, options=opts)
    assert obj["p"].count("\\") == 0
    assert "¥" in obj["p"]


def test_cli_raw_outputs_cleaned_json(tmp_path: Path):
    # CLIの --raw で未クォートキーや末尾カンマが修正されること
    dirty = '{ list: [1,2,3,], unq: 1 }'
    p_in = tmp_path / "in.json"
    p_in.write_text(dirty, encoding="utf-8")

    cmd = [
        sys.executable,
        "-m",
        "api_json_cleaner.cli",
        str(p_in),
        "--raw",
    ]
    out = subprocess.check_output(cmd, text=True, encoding="utf-8")
    # 生テキストとしてキーにクォートが付与され、末尾カンマが除去されていること
    assert '"list"' in out and '"unq"' in out
    assert ",[}" not in out
