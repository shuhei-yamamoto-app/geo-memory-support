# extractor/place_extractor_ginza.py
from typing import List, Dict
from .ginza_nlp import get_nlp

import re

PLACE_LABELS = ("City", "Park", "Location", "Facility")
TIME_LABELS = ("Time", "Date", "Duration")

PLACE_SUFFIXES = (
    "駅", "大学", "学校", "公園", "病院", "会社",
    "センター", "ホール", "会館", "スタジアム", "ビル", "店"
)

PLACE_CASE_PARTICLES = ("で", "に", "へ")

TIME_WORD_HINTS = (
    "今日", "明日", "明後日", "昨日",
    "来週", "再来週", "今週", "先週",
    "月曜日", "火曜日", "水曜日", "木曜日",
    "金曜日", "土曜日", "日曜日",
)

ACTION_TAIL_RE = re.compile(
    r"(で)?(集合|待ち合わせ)(で)?(する|しよう|しましょう|しませんか)?$"
)

def _normalize_place_phrase(phrase: str) -> str:
    # 前後の余計な記号を除去
    phrase = phrase.strip(" 　、。,.！？!?")

    # ★「〜で集合」「〜で待ち合わせ」パターンを削る
    #   例: 東京駅で集合で → 東京駅
    #       東京駅で待ち合わせしましょう → 東京駅
    phrase = ACTION_TAIL_RE.sub("", phrase)
    phrase = phrase.strip(" 　、。,.！？!?")  # もう一度トリム

    # 末尾の格助詞「で・に・へ」を落とす（従来の処理）
    for p in PLACE_CASE_PARTICLES:
        if phrase.endswith(p):
            phrase = phrase[: -len(p)]
            break

    return phrase



def _is_time_like(name: str) -> bool:
    """文字列ベースで『時間っぽい』ものを除外する"""
    if any(h in name for h in TIME_WORD_HINTS):
        return True
    if name.endswith("曜日"):
        return True
    return False


def _remove_sub_places(places: List[str]) -> List[str]:
    """長い場所名に含まれてしまっている短い場所名を除外"""
    result: List[str] = []
    for p in places:
        if any(p != q and p in q for q in places):
            continue
        result.append(p)
    return result


def extract_place(text: str) -> List[str]:
    nlp = get_nlp()
    doc = nlp(text)

    # name -> その場所候補がテキスト中に最初に現れたトークン位置
    candidates: Dict[str, int] = {}

    def add_candidate(name: str, index: int):
        """候補を登録（短いインデックスを優先）"""
        if not name:
            return
        if _is_time_like(name):
            return
        if name in candidates:
            candidates[name] = min(candidates[name], index)
        else:
            candidates[name] = index

    # ① 固有表現から
    for ent in doc.ents:
        if ent.label_ not in PLACE_LABELS:
            continue

        ent_tokens = list(ent)
        # 渋谷(のカフェ) の「渋谷」みたいな修飾エンティティはスキップ
        if all(t.dep_ == "nmod" and t.head.pos_ in ("NOUN", "PROPN") for t in ent_tokens):
            continue

        name = _normalize_place_phrase(ent.text)
        add_candidate(name, ent.start)

    # ② 語尾ルール（〜駅, 〜公園 など）
    for token in doc:
        surf = token.text
        if any(surf.endswith(suf) for suf in PLACE_SUFFIXES):
            name = _normalize_place_phrase(surf)
            add_candidate(name, token.i)

    # ③ 係り受け + 助詞で場所として使われている名詞句
    for token in doc:
        if token.pos_ not in ("NOUN", "PROPN"):
            continue

        # 「火曜日」など時間系の名詞は除外
        if token.ent_type_ in TIME_LABELS:
            continue

        # 渋谷の（カフェ）など修飾語側は除外
        if token.dep_ == "nmod":
            continue

        has_place_case = any(
            child.text in PLACE_CASE_PARTICLES and child.dep_ == "case"
            for child in token.children
        )
        if not has_place_case:
            continue

        subtree_tokens = list(token.subtree)

        # subtree 内に Time 系が混ざっていたら（来週の火曜日に〜）除外
        if any(t.ent_type_ in TIME_LABELS for t in subtree_tokens):
            continue

        subtree_tokens.sort(key=lambda t: t.i)
        phrase = "".join(t.text for t in subtree_tokens)
        name = _normalize_place_phrase(phrase)

        start_index = min(t.i for t in subtree_tokens)
        add_candidate(name, start_index)

    # ④ 出現位置でソートしてリスト化
    ordered = [name for name, _idx in sorted(candidates.items(), key=lambda x: x[1])]

    # ⑤ サブ文字列の場所名を除去（センタービル vs 新宿センタービル7階の会議室）
    ordered = _remove_sub_places(ordered)

    return ordered
