# extractor/ginza_nlp.py
import spacy

# 一度ロードして使い回す
_nlp = spacy.load("ja_ginza")

def get_nlp():
    return _nlp
