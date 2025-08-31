"""
api_json_cleaner: APIレスポンス由来の"汚いJSON"をキレイに整えて安全にパース・保存するユーティリティ。

主な機能:
- 文字化け/誤エンコードの自動検出とデコード(日本語対応)
- よくあるAPIレスポンス特有のエスケープ/破損の修復
- JSONの整形・検証
- Pythonデータとして受け渡し、必要に応じて保存

公開API:
- clean_json_text
- parse
- save_json
- cleanse_and_parse
"""

from .cleaner import clean_json_text, cleanse_and_parse, parse, save_json

__all__ = [
    "clean_json_text",
    "parse",
    "save_json",
    "cleanse_and_parse",
]

__version__ = "0.1.0"
