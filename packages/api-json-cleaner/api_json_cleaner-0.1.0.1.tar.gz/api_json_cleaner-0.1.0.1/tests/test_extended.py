from __future__ import annotations

import json
import sys
import time
import subprocess
from pathlib import Path

import pytest

from api_json_cleaner import cleanse_and_parse, save_json
from api_json_cleaner.cleaner import CleanOptions


def test_vendor_prefix_anti_json_hijacking():
    txt = ")]}',\n{\n  unquoted: 1,\n}"
    obj = cleanse_and_parse(txt)
    assert obj == {"unquoted": 1}


def test_encoding_shift_jis_bytes():
    # Shift_JISの日本語をbytesで与えて自動判定されるか
    d = {"msg": "日本語テスト"}
    b = json.dumps(d, ensure_ascii=False).encode("cp932")
    obj = cleanse_and_parse(b)
    assert obj["msg"] == "日本語テスト"


def test_save_json_roundtrip(tmp_path: Path):
    data = {"text": "テスト", "arr": [1, 2, 3]}
    p = tmp_path / "out.json"
    save_json(data, str(p), ensure_ascii=False, indent=2)
    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded == data


def test_cli_strict_mode_disables_json5(tmp_path: Path):
    # JSON5な入力を厳密モードで失敗させる
    p = tmp_path / "in.json"
    p.write_text("{ 'a': 1 }", encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "api_json_cleaner.cli",
        str(p),
        "--no-json5",
    ]
    rc = subprocess.run(cmd, capture_output=True, text=True)
    assert rc.returncode != 0 or "'a'" in (rc.stdout + rc.stderr)


@pytest.mark.slow
def test_large_payload_performance():
    # 10万要素程度のリストを含むJSON（軽微な汚れ有り）
    N = 100_000
    dirty = '{ data: [' + ','.join('1' for _ in range(N)) + ',], note: "～" }'
    t0 = time.perf_counter()
    obj = cleanse_and_parse(dirty)
    dt = time.perf_counter() - t0
    assert len(obj["data"]) == N
    # 目安: 2秒以内（環境差あり、目安のみ）
    assert dt < 2.5
