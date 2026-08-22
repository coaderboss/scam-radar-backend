import re
import difflib

# agent_brand.py mein list ko update kar:
TOP_BRANDS = ["google", "amazon", "paypal", "netflix", "hdfc", "sbi", "csjmu", "aktu", "iitk"]

# 🧠 THE HACKER DICTIONARY (Leet-Speak Translation Map)
# Converts '0' -> 'o', '1' -> 'i', '@' -> 'a', etc.
LEET_MAP = str.maketrans("0134578@+", "oieastbba")

def check_brand_impersonation(url: str | None):
    if not url: return "No URL provided."
    
    # 1. Extract raw domain (to check for weird capitalization)
    raw_domain = re.sub(r'^https?:\/\/(www\.)?', '', url).split('.')[0]
    has_weird_case = raw_domain != raw_domain.lower()
    
    # 2. Apply Hacker Dictionary (Clean the string)
    clean_domain = raw_domain.lower().translate(LEET_MAP)
    
    for brand in TOP_BRANDS:
        # 3. Calculate distance
        similarity = difflib.SequenceMatcher(None, clean_domain, brand).ratio()
        
        # If it's a 100% match after translation, but wasn't originally (e.g. g00gle.com)
        if similarity == 1.0 and clean_domain != raw_domain.lower():
            return f"🚨 CRITICAL RISK: Homograph attack detected. Mimicking '{brand}' using fake characters."
            
        # Lowered threshold to 70% to catch g0glle, arnazon, etc.
        elif 0.70 <= similarity < 1.0:
            return f"🚨 HIGH RISK: Typosquatting detected. Trying to mimic '{brand}'. (Match: {round(similarity*100)}%)"
            
        # Exactly 100% match (Safe, but check case)
        elif similarity == 1.0:
            if has_weird_case:
                return f"⚠️ WARNING: Official '{brand}' domain, but uses highly suspicious capitalization."
            return f"ℹ️ Official '{brand}' domain detected."
            
    return "No major brand impersonation detected."