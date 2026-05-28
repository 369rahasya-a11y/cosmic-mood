````python
import json
import os
import time
from datetime import datetime

from groq import Groq
from supabase import create_client

# =========================
# ENV VARIABLES
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# =========================
# VALIDATION
# =========================

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY missing")

if not SUPABASE_URL:
    raise Exception("SUPABASE_URL missing")

if not SUPABASE_KEY:
    raise Exception("SUPABASE_SERVICE_ROLE_KEY missing")

# =========================
# CLIENTS
# =========================

client = Groq(
    api_key=GROQ_API_KEY
)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("CONNECTED")

# =========================
# DATA
# =========================

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces"
]

MOODS = [
    "Ambitious",
    "Adventurous",
    "Creative",
    "Rebellious",
    "Confident",
    "Anxious",
    "Sad",
    "Lonely",
    "Romantic",
    "Nostalgic",
    "Exhausted",
    "Lazy",
    "Peaceful",
    "Daydreamy",
    "Irritated"
]

# =========================
# LOAD MASTER PROMPT
# =========================

with open("prompt.txt", "r", encoding="utf-8") as f:
    MASTER_PROMPT = f.read()

today = datetime.utcnow().date().isoformat()

# =========================
# GENERATE
# =========================

for sign in SIGNS:

    for mood in MOODS:

        print(f"\n========== {sign} → {mood} ==========\n")

        prompt = f"""
{MASTER_PROMPT}

IMPORTANT:

Generate ONLY ONE horoscope.

Zodiac Sign:
{sign}

Mood:
{mood}

Return ONLY ONE valid JSON object.

STRICT FORMAT:

{{
  "date": "{today}",
  "sign": "{sign}",
  "mood": "{mood}",
  "content": "horoscope text here"
}}

RULES:
- Output ONLY JSON
- Do NOT add explanations
- Do NOT add markdown
- Do NOT wrap JSON in triple backticks
- Do NOT generate multiple JSON objects
- Do NOT generate arrays
- Do NOT generate labels
- The response must start with {{
- The response must end with }}
"""

        try:

            print("Generating...")

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,
                max_tokens=400
            )

            text = completion.choices[0].message.content.strip()

            print("\nRAW RESPONSE:\n")
            print(text)

            # =========================
            # CLEAN RESPONSE
            # =========================

            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

            # FIND JSON START
            json_start = text.find("{")

            # FIND JSON END
            json_end = text.rfind("}")

            if json_start != -1 and json_end != -1:
                text = text[json_start:json_end + 1]

            print("\nCLEANED JSON:\n")
            print(text)

            print("Parsing JSON...")

            parsed = json.loads(text)

            print("Uploading...")

            supabase.table("horoscopes").upsert({
                "horoscope_date": parsed["date"],
                "sign": parsed["sign"],
                "mood": parsed["mood"],
                "content": parsed["content"]
            }).execute()

            print("SUCCESS")

        except Exception as e:

            print("FAILED:")
            print(str(e))

        time.sleep(2)

print("\nALL 180 HOROSCOPES GENERATED")
````
