from __future__ import annotations

import json
from api_json_cleaner import cleanse_and_parse
from api_json_cleaner.cleaner import CleanOptions


def test_jsonp_callback():
    txt = 'callbackName({"a":1, unq:2,})'
    obj = cleanse_and_parse(txt)
    assert obj == {"a": 1, "unq": 2}


def test_js_loop_prefix():
    txt = 'for(;;); { list: [1,2,3,] }'
    obj = cleanse_and_parse(txt)
    assert obj == {"list": [1, 2, 3]}


def test_length_prefix():
    payload = '{"x":1,}'
    txt = f"{len(payload)}\n" + payload
    obj = cleanse_and_parse(txt)
    assert obj == {"x": 1}


def test_ndjson_as_array():
    nd = '{"id":1}\n{"id":2}\n{"id":3}\n'
    obj = cleanse_and_parse(nd)
    assert isinstance(obj, list) and [o["id"] for o in obj] == [1, 2, 3]


def test_unwrap_container_and_prefer_primary():
    obj = cleanse_and_parse('{"count": 2, "results": [{"a":1},{"a":2}]}')
    assert obj == [{"a": 1}, {"a": 2}]
    obj2 = cleanse_and_parse('{"data": {"b": 1}}')
    assert obj2 == {"b": 1}


def test_parse_inner_json_strings():
    inner = '{"y": [1,2,3]}'
    txt = json.dumps({"x": inner})  # 値がJSON文字列
    obj = cleanse_and_parse(txt)
    assert obj == {"x": {"y": [1, 2, 3]}}
