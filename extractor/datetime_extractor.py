# datetime_extractor.py
import re
from typing import List

def extract_date(text: str) -> List[str]:
    """日付（年/月/日）を抽出する"""
    patterns = [
        r"\d{4}年\d{1,2}月\d{1,2}日",     # 2025年11月14日
        r"\d{1,2}月\d{1,2}日",            # 11月14日
        r"\d{1,2}/\d{1,2}",               # 11/14
    ]

    return _find_unique(text, patterns)


def extract_time(text: str) -> List[str]:
    """時間（時刻）を抽出する"""
    patterns = [
        r"\d{1,2}時\d{1,2}分",            # 18時30分
        r"\d{1,2}時",                     # 18時
        r"\d{1,2}:\d{2}",                 # 18:30
        r"午前\d{1,2}時",                 # 午前9時
        r"午後\d{1,2}時",                 # 午後3時
    ]

    return _find_unique(text, patterns)


def extract_relative(text: str) -> List[str]:
    """相対的な時間表現を抽出する"""
    patterns = [
        r"今日|明日|明後日|昨日",
        r"来週|再来週|先週",
        r"今週の\d{1,2}日",              # 今週の15日
    ]

    return _find_unique(text, patterns)


def extract_datetime(text: str) -> dict:
    """日時の抽出結果をまとめて返す"""
    return {
        "date": extract_date(text),
        "time": extract_time(text),
        "relative": extract_relative(text),
    }


def _find_unique(text: str, patterns: List[str]) -> List[str]:
    """正規表現で抽出した結果から重複を除去して返す"""
    found = []

    for pat in patterns:
        for m in re.finditer(pat, text):
            found.append(m.group())

    # 重複を削除（出現順を保持）
    result = []
    seen = set()
    for x in found:
        if x not in seen:
            seen.add(x)
            result.append(x)

    return result
