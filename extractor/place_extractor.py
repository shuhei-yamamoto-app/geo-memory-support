# extractor/place_extractor.py
import re
from typing import List


def extract_place(text: str) -> List[str]:
    """場所っぽい名詞を抽出する（簡易版）"""
    # 駅 / 学校 / 公園 / 市役所 / 区役所 / 大学 / 病院 / 会社 / 店 / ビル
    pattern = r"\S*(駅|大学|学校|公園|病院|会社|店|ビル|センター|ホール|会館|スタジアム)"

    found = []
    for m in re.finditer(pattern, text):
        place = m.group().strip("。、．.")
        if place not in found:
            found.append(place)

    return found
