import json
import os
import requests
import time

from supabase import create_client

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# LOAD PROMPT
with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

MODELS = [
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "mistralai/mistral-7b-instruct:free",
]

result = None

for model_name in MODELS:

    print(f"Trying model: {model_name}")

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=120
        )

        print("STATUS:", response.status_code)

        result = response.json()

        # SUCCESS
        if "choices" in result:
            print(f"Success with {model_name}")
            break

        print("FAILED:")
        print(result)

    except Exception as e:
        print("ERROR:")
        print(e)

        continue

# FINAL CHECK
if not result or "choices" not in result:
    raise Exception("All models failed.")

# EXTRACT TEXT
text = result["choices"][0]["message"]["content"]

# CLEAN JSON
if text.startswith("```json"):
    text = text.replace("```json", "").replace("```", "")

# PARSE JSON
parsed = json.loads(text)

# CONNECT SUPABASE
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# INSERT
for item in parsed["horoscopes"]:
    supabase.table("horoscopes").upsert({
        "horoscope_date": parsed["date"],
        "sign": item["sign"],
        "mood": item["mood"],
        "content": item["content"]
    }).execute()

print("All horoscopes uploaded successfully.")

