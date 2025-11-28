import spacy

nlp = spacy.load("ja_ginza")

text = "明日11時に新宿駅で友人と会ってから、代々木公園に行き、その後渋谷のカフェで勉強します。"
doc = nlp(text)

print("◆ 固有表現（ENTITIES）")
for ent in doc.ents:
    print(f"text={ent.text:10s} label={ent.label_:5s}")

print("\n◆ トークン（形態素 + 係り受け）")
for token in doc:
    print(
        f"text={token.text:6s} "
        f"lemma={token.lemma_:6s} "
        f"pos={token.pos_:4s} "
        f"dep={token.dep_:8s} "
        f"head={token.head.text}"
    )
