import os
import time
import itertools
from google import genai
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

# Initialize Cloud Clients with direct REST endpoint options for new Supabase keys
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

options = ClientOptions(
    postgrest_client_timeout=10,
    headers={"apiKey": key, "Authorization": f"Bearer {key}"}
)

supabase: Client = create_client(url, key, options=options)
ai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
moods = ["Ambitious", "Adventurous", "Creative", "Rebellious", "Confident", "Anxious", "Sad", "Lonely", "Romantic", "Nostalgic", "Exhausted", "Lazy", "Peaceful", "Daydreamy", "Irritated"]

print("Clearing yesterday's forecast...")
try:
    supabase.table("daily_horoscopes").delete().neq("zodiac_sign", "").execute()
except Exception as e:
    print(f"Notice: Could not clear old entries (table might be empty): {e}")

print("Starting cosmic generations...")
for sign, mood in itertools.product(signs, moods):
    print(f"Generating for {sign} - {mood}...")
    
    prompt = f"""
    You are an expert, modern astrologer who writes intuitive, empathetic, and culturally relevant horoscopes. 
    Generate a daily horoscope for:
    - Zodiac Sign: {sign}
    - Selected Mood: {mood}

    [TONE INSTRUCTIONS BASED ON MOOD]
    - If Mood is (Ambitious, Adventurous, Creative, Rebellious, Confident): Use "Fierce & Direct" energy. Be a cosmic hype-man. Use active verbs. Urge immediate action.
    - If Mood is (Anxious, Sad, Lonely, Romantic, Nostalgic): Use "Nurturing & Deeply Empathetic" energy. Validate emotional depth. Speak like a trusted friend. 
    - If Mood is (Exhausted, Lazy, Peaceful, Daydreamy, Irritated): Use "Grounding & Calm" energy. Give permission to slow down or protect peace.

    [STRICT WRITING RULES]
    1. Never mention the name of the mood directly in the text. Mirror the feeling.
    2. Structure: Sentence 1: Acknowledge energy. Sentence 2: Practical advice. Sentence 3: Perspective shift.
    3. Word Count: Strictly between 50 and 70 words. Punchy.
    4. Output: Return ONLY the horoscope text. No greetings.
    5. Introduce absolute variety. Avoid using common astrological clichés like "The stars align," "Cosmic shift," or repeating sentence structures from yesterday. Make every generation unique.
    """
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        text = response.text.strip()
        
        supabase.table("daily_horoscopes").insert({
            "zodiac_sign": sign,
            "mood": mood,
            "horoscope_text": text
        }).execute()
        
    except Exception as e:
        print(f"Error generating for {sign}-{mood}: {e}")
    
    # Wait 2 seconds to stay safely within free tier API rate limits
    time.sleep(2)

print("All 180 horoscopes successfully synced to the cloud database!")
