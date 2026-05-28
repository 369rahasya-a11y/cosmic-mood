import json
import os
import requests

from supabase import create_client

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# LOAD PROMPT
with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# OPENROUTER REQUEST
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
)

result = response.json()

text = result["choices"][0]["message"]["content"]

# CLEAN JSON
if text.startswith("```json"):
    text = text.replace("```json", "").replace("```", "")

parsed = json.loads(text)

# SUPABASE
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

print("Uploaded successfully")
