import os
import time
import itertools
import google.generativeai as genai
from supabase import create_client, Client

# Initialize database clients
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
moods = ["Ambitious", "Adventurous", "Creative", "Rebellious", "Confident", "Anxious", "Sad", "Lonely", "Romantic", "Nostalgic", "Exhausted", "Lazy", "Peaceful", "Daydreamy", "Irritated"]

print("Clearing yesterday's forecast...")
try:
    supabase.table("daily_horoscopes").delete().neq("zodiac_sign", "").execute()
    print("Database cleared successfully!")
except Exception as e:
    print(f"Notice: Could not clear old entries: {e}")

print("Starting cosmic generations...")
for sign, mood in itertools.product(signs, moods):
    print(f"👉 Processing: {sign} + {mood}...")
    
    prompt = f"Generate a 3-sentence daily horoscope for a {sign} who is feeling {mood}."
    
    for attempt in range(3):
        try:
            print(f"   Calling Gemini API (Attempt {attempt + 1})...")
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            print("   Pushing text data to Supabase database...")
            supabase.table("daily_horoscopes").insert({
                "zodiac_sign": sign,
                "mood": mood,
                "horoscope_text": text
            }).execute()
            
            print(f"   ✅ Saved successfully: {sign} ({mood})")
            break
            
        except Exception as e:
            print(f"   ❌ CRITICAL SYSTEM ERROR for {sign}-{mood}: {e}")
            print("   Waiting 35 seconds to clear system block...")
            time.sleep(35)
            
    # Force a brief steady wait time
    time.sleep(10)

print("All done!")
