# extractor/combined.py
from .datetime_extractor import extract_datetime
from .place_extractor import extract_place
from .action_extractor import extract_action


def extract_all(text: str) -> dict:
    """日時 + 場所 + 行動の抽出をまとめて返す"""
    dt = extract_datetime(text)
    place = extract_place(text)
    action = extract_action(text)

    return {
        "date": dt["date"],
        "time": dt["time"],
        "relative": dt["relative"],
        "place": place,
        "action": action
    }
