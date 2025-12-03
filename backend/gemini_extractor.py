import os
import json
import re
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY が設定されていません。")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash-lite"  # gemini_test.py と同じにする


def extract_with_gemini(text: str) -> dict:
    prompt = f"""
あなたは、日本語テキストから「場所」「時間」「行動」を抽出するアシスタントです。

次の文から、
- 「場所」（駅・ビル・施設・学校・公園・会社・オフィスなど）
- 「時間」（日付・時刻・曜日・「明日」「来週」などの時間表現）
- 「行動」（その文で人がしようとしている主な動作：集合する、移動する、打ち合わせをする、など）

を抽出し、必ず次の JSON 形式「だけ」を出力してください。

出力フォーマット:
{{
  "places": ["場所1", "場所2"],
  "times": ["時間1", "時間2"],
  "actions": ["行動1", "行動2"]
}}

制約:
- 解説や文章は書かず、JSON だけを返してください。
- 配列が空の場合は [] としてください。
- 同じ要素は重複させないでください。
- ``` などのコードブロックは使わないでください。

文:
{text}
"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # Gemini の生の返答を確認用に出す
        raw_text = (response.text or "").strip()
        print("=== Gemini raw response ===")
        print(raw_text)

        # 万が一、前後に余計な文字がついた場合に備えて、
        # 最初の { ... } の部分だけ抜き出す
        m = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if m:
            json_str = m.group(0)
        else:
            # まったく { } が無い場合はそのままパースを試す
            json_str = raw_text

        data = json.loads(json_str)

        places = [str(p) for p in data.get("places", [])]
        times = [str(t) for t in data.get("times", [])]
        actions = [str(a) for a in data.get("actions", [])]

        return {
            "places": places,
            "times": times,
            "actions": actions,
        }

    except Exception as e:
        print("Gemini extraction error:", repr(e))
        return {
            "places": [],
            "times": [],
            "actions": [],
        }
