# extractor/action_extractor.py
import re
from typing import List


def extract_action(text: str) -> List[str]:
    """行動っぽい動詞を抽出する（簡易版）"""
    pattern = r"\S*(する|行く|来る|寄る|参加する|集合する|訪問する|見る|会う)"

    found = []
    for m in re.finditer(pattern, text):
        action = m.group().strip("。、．.")
        if action not in found:
            found.append(action)

    return found
