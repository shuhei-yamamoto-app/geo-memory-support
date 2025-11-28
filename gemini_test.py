# gemini_test.py

import os
import google.generativeai as genai

# 仮想環境の activate.ps1 で設定したキーをそのまま使う
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY が見つかりません。仮想環境が有効か確認してください。")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash-lite")

# とりあえず簡単なプロンプトでテスト
response = model.generate_content("こんにちは。1行で自己紹介してください。")

print("=== Gemini の返答 ===")
print(response.text)
