from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from charset_normalizer import from_bytes


_CTRL_CHARS = (
    list(range(0x00, 0x09))
    + list(range(0x0B, 0x20))
)


_CTRL_RE = re.compile(
    "[" + "".join(re.escape(chr(c)) for c in _CTRL_CHARS) + "]"
)


_UNQUOTED_KEY_RE = re.compile(r"(?P<pre>[{,]\s*)(?P<key>[A-Za-z_][A-Za-z0-9_\-]*)(?P<post>\s*:)" )
_TRAILING_COMMA_RE = re.compile(r",\s*(?P<closer>[}\]])")
_JSON_HIJACK_PREFIX_RE = re.compile(r"^\s*\)\]\}',?\s*\n?")
_JS_LOOP_PREFIX_RE = re.compile(r"^\s*(?:for\s*\(\s*;\s*;\s*\)\s*;|while\s*\(\s*1\s*\)\s*;)\s*")
_LENGTH_PREFIX_RE = re.compile(r"^\s*(?P<len>\d+)\s*(?:\r\n|\r|\n)")
_JSONP_RE = re.compile(r"^\s*[A-Za-z_$][\w$]*\s*\(\s*(?P<body>[\s\S]+?)\s*\)\s*;?\s*$")


@dataclass
class CleanOptions:
    strip_bom: bool = True
    remove_ctrl_chars: bool = True
    fix_unquoted_keys: bool = True
    fix_trailing_commas: bool = True
    unescape_common: bool = True
    html_entity_unescape: bool = True  # パース後に文字列へ適用
    ensure_ascii: bool = False  # 保存時のデフォルト
    indent: Optional[int] = 2
    # --- 日本語向け ---
    ja_mode: bool = True  # 日本語文字列の正規化を既定で有効化
    unicode_normalization: Optional[str] = "NFKC"  # NFC / NFKC / None
    normalize_newlines: bool = True  # \r\n/\r→\n
    unify_wave_tilde: bool = True  # U+FF5EなどをU+301Cに統一
    unify_prolonged_sound_mark: bool = True  # カナ文脈のダッシュ→長音符
    unify_hyphen: bool = False  # 非カナ文脈のダッシュ→"-"（控えめにoff）
    yen_backslash: str = "preserve"  # preserve|yen-to-backslash|backslash-to-yen
    fix_mojibake: bool = False  # 任意: ftfyを用いた修復
    # --- JSON5 互換 ---
    allow_json5: bool = True  # コメント/単一引用符/末尾カンマなどの緩い構文を許容
    # --- ベンダー固有フォーマット ---
    allow_jsonp: bool = True  # callbackName({...}); を許容
    allow_js_prefix: bool = True  # for(;;); / while(1); 等のプリフィックス
    allow_length_prefix: bool = True  # 長さ+改行の前置き "123\n{...}"
    allow_ndjson: bool = True  # NDJSONを配列として解釈（フォールバック）
    unwrap_singleton_container: bool = False  # {"data": {...}} → {...}
    prefer_primary_container: bool = False  # {count:.., results:[...]} → results
    parse_inner_json_strings: bool = False  # 値がJSON文字列なら再パース
    inner_json_max_size: int = 2_000_000  # 2MB上限


def _decode_best_effort(data: bytes) -> str:
    """バイト列から最も適切なエンコーディングでデコードし、文字化けを軽減。"""
    result = from_bytes(data).best()
    if result is None:
        # フォールバック
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return data.decode("cp932", errors="replace")
    return str(result)


def _strip_bom(text: str) -> str:
    if text.startswith("\ufeff"):
        return text.lstrip("\ufeff")
    return text


def _remove_control_chars(text: str) -> str:
    return _CTRL_RE.sub("", text)


def _unescape_common(text: str) -> str:
    """API特有の二重エスケープ・雑多なエスケープを正規化。

    例:
    - 文字列としてのJSONがさらにJSON内でエスケープされている
    - 改行が \n のまま埋め込まれ可読性が悪い
    """
    # 二重エスケープを可能な範囲で戻す
    # 例: "{\"a\":\"b\"}" -> {"a":"b"}
    try:
        if re.search(r"^\s*\".*\"\s*$", text, re.S):
            # 外側が完全にクォートされた巨大文字列なら一度JSONとして読み直す
            inner = json.loads(text)
            if isinstance(inner, str):
                text = inner
    except Exception:
        pass

    return text


def _fix_unquoted_keys(text: str) -> str:
    # JSONではキーはダブルクォート必須。一般的なケースのみ安全に修正。
    def repl(m: re.Match[str]) -> str:
        return f"{m.group('pre')}\"{m.group('key')}\"{m.group('post')}"

    return _UNQUOTED_KEY_RE.sub(repl, text)


def _fix_trailing_commas(text: str) -> str:
    return _TRAILING_COMMA_RE.sub(r"\g<closer>", text)


def clean_json_text(
    data: bytes | str,
    *,
    options: Optional[CleanOptions] = None,
) -> str:
    """JSONテキストをできるだけ破壊せずにクレンジングして返す。

    - bytes入力: 文字コード自動推定でデコード
    - 余分な制御文字の除去
    - 二重エスケープ等の正規化
    - 末尾カンマや未クォートキーの軽度修正
    - BOM除去
    """
    opts = options or CleanOptions()

    if isinstance(data, bytes):
        text = _decode_best_effort(data)
    else:
        text = data

    if opts.strip_bom:
        text = _strip_bom(text)

    if opts.remove_ctrl_chars:
        text = _remove_control_chars(text)

    # Google系/一部APIの anti-JSON-hijacking プレフィックス: ")]}',\n"
    text = _JSON_HIJACK_PREFIX_RE.sub("", text)
    # for(;;); / while(1);
    if (options or CleanOptions()).allow_js_prefix:
        text = _JS_LOOP_PREFIX_RE.sub("", text)
    # 長さプレフィックス 123\n{...}
    if (options or CleanOptions()).allow_length_prefix:
        text = _LENGTH_PREFIX_RE.sub("", text)
    # JSONP callbackName({...});
    if (options or CleanOptions()).allow_jsonp:
        m = _JSONP_RE.match(text)
        if m:
            text = m.group("body")

    if opts.unescape_common:
        text = _unescape_common(text)

    if opts.fix_unquoted_keys:
        text = _fix_unquoted_keys(text)

    if opts.fix_trailing_commas:
        text = _fix_trailing_commas(text)

    return text


def parse(data: bytes | str, *, options: Optional[CleanOptions] = None) -> Any:
    """クレンジング後にjson.loadsでパースしてPythonデータを返す。"""
    text = clean_json_text(data, options=options)

    # さらにJSON文字列が中に埋め込まれている場合、2段階で読むことを試す
    opts = options or CleanOptions()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # 再度アンエスケープを試みて読む（全体が二重エスケープの場合など）
        try:
            obj = json.loads(_unescape_common(text))
        except Exception:
            # JSON5として解釈（コメントや単一引用符、末尾カンマなど）
            if opts.allow_json5:
                try:
                    import json5  # type: ignore
                    obj = json5.loads(text)
                except Exception:
                    # NDJSONとしての解釈
                    if opts.allow_ndjson:
                        lines = [ln for ln in text.splitlines() if ln.strip()]
                        parsed: list[Any] = []
                        ok = True
                        for ln in lines:
                            try:
                                parsed.append(json.loads(ln))
                            except Exception:
                                ok = False
                                break
                        if ok:
                            obj = parsed
                        else:
                            raise
                    else:
                        raise
            else:
                # JSON5未許可でもNDJSONは試す
                if opts.allow_ndjson:
                    lines = [ln for ln in text.splitlines() if ln.strip()]
                    parsed: list[Any] = []
                    ok = True
                    for ln in lines:
                        try:
                            parsed.append(json.loads(ln))
                        except Exception:
                            ok = False
                            break
                    if ok:
                        obj = parsed
                    else:
                        raise
                else:
                    raise

    # 値の中に文字化け残骸がある場合の軽い修正（例: \uFFFDの連発など）
    def _html_unescape(s: str) -> str:
        # ごく限定的なHTMLエンティティをデコード
        return (
            s.replace("&quot;", '"')
            .replace("&#34;", '"')
            .replace("&#39;", "'")
            .replace("&amp;", "&")
        )

    def _is_kana_char(ch: str) -> bool:
        return ("\u3040" <= ch <= "\u309F") or ("\u30A0" <= ch <= "\u30FF")

    def _ja_normalize(s: str, opts: CleanOptions) -> str:
        t = s
        # 改行
        if opts.normalize_newlines:
            t = t.replace("\r\n", "\n").replace("\r", "\n")
        # まず波ダッシュ統一（正規化でFULLWIDTH TILDEが~になってしまう前に）
        if opts.unify_wave_tilde:
            # FF5E/223C を先に波ダッシュへ
            t = t.replace("\uFF5E", "\u301C").replace("\u223C", "\u301C")
            # ASCII ~ を日本語文脈でのみ 〜 に置換
            if "~" in t:
                chars = list(t)
                for i, ch in enumerate(chars):
                    if ch == "~":
                        prev = chars[i-1] if i-1 >= 0 else ""
                        nxt = chars[i+1] if i+1 < len(chars) else ""
                        if (
                            _is_kana_char(prev) or _is_kana_char(nxt)
                            or ("\u4E00" <= prev <= "\u9FFF")
                            or ("\u4E00" <= nxt <= "\u9FFF")
                            or ("\uFF01" <= prev <= "\uFF60")
                            or ("\uFF01" <= nxt <= "\uFF60")
                        ):
                            chars[i] = "\u301C"
                t = "".join(chars)
        # Unicode正規化
        if opts.unicode_normalization in {"NFC", "NFKC"}:
            t = unicodedata.normalize(opts.unicode_normalization, t)
        # カナ文脈のダッシュ類を長音符へ
        if opts.unify_prolonged_sound_mark:
            chars = list(t)
            for i, ch in enumerate(chars):
                if ch in "-−‐‑‒–—":  # U+2212, U+2010..U+2014など
                    prev = chars[i-1] if i-1 >= 0 else ""
                    nxt = chars[i+1] if i+1 < len(chars) else ""
                    if _is_kana_char(prev) or _is_kana_char(nxt):
                        chars[i] = "ー"
            t = "".join(chars)
        # 非カナ文脈のダッシュをASCIIへ
        if opts.unify_hyphen:
            t = re.sub(r"[\u2212\u2010\u2011\u2012\u2013\u2014]", "-", t)
        # Yen/Backslash変換
        if opts.yen_backslash == "yen-to-backslash":
            t = t.replace("¥", "\\")
        elif opts.yen_backslash == "backslash-to-yen":
            t = t.replace("\\", "¥")
        # 文字化けの修復（任意依存）
        if opts.fix_mojibake:
            try:
                from ftfy import fix_text
                t = fix_text(t)
            except Exception:
                pass
        return t

    def _maybe_unwrap(o: Any) -> Any:
        if isinstance(o, dict):
            keys = list(o.keys())
            primary = ["results", "items", "data", "payload", "d"]
            if opts.unwrap_singleton_container and len(keys) == 1 and keys[0] in primary:
                return o[keys[0]]
            if opts.prefer_primary_container:
                for k in ["results", "items", "data"]:
                    if k in o:
                        return o[k]
        return o

    def _post_fix(v: Any, *, _depth: int = 0) -> Any:
        if isinstance(v, str):
            # 置換は最小限
            s = v.replace("\uFFFD", "�")
            if opts.html_entity_unescape:
                s = _html_unescape(s)
            if opts.ja_mode:
                s = _ja_normalize(s, opts)
            # 値がJSONらしい文字列なら再パース（サイズ制限あり）
            st = s.lstrip()
            if (
                opts.parse_inner_json_strings
                and _depth < 5
                and len(s) <= opts.inner_json_max_size
                and (st.startswith("{") or st.startswith("["))
            ):
                try:
                    inner = parse(s, options=opts)
                    return inner
                except Exception:
                    pass
            return s
        if isinstance(v, list):
            return [_post_fix(x, _depth=_depth + 1) for x in v]
        if isinstance(v, dict):
            o = {k: _post_fix(val, _depth=_depth + 1) for k, val in v.items()}
            return _maybe_unwrap(o)
        return v

    return _post_fix(_maybe_unwrap(obj))


def save_json(
    obj: Any,
    path: str,
    *,
    ensure_ascii: Optional[bool] = None,
    indent: Optional[int] = None,
    newline: str = "\n",
) -> None:
    """PythonデータをキレイなJSONとして保存。日本語はデフォルトで非ASCIIエスケープ。"""
    ensure_ascii = True if ensure_ascii is None else ensure_ascii
    indent = 2 if indent is None else indent
    text = json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent)
    with open(path, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)


def cleanse_and_parse(
    data: bytes | str,
    *,
    save_to: Optional[str] = None,
    options: Optional[CleanOptions] = None,
) -> Any:
    """まとめてクレンジング→パース→（任意で保存）まで行う高級API。"""
    obj = parse(data, options=options)
    if save_to:
        save_json(obj, save_to)
    return obj
