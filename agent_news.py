import os
import requests
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

def fetch_live_threat_intel():
    if not NEWS_API_KEY:
        return {"error": "NEWS_API_KEY is missing in .env file."}
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "cybersecurity OR malware OR phishing OR ransomware OR zero-day",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 4, # 🚨 FIX 1: Reduced to 4 so AI doesn't get overwhelmed
        "apiKey": NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        news_data = response.json()
        
        if news_data.get("status") != "ok":
            return {"error": f"News API Error: {news_data.get('message', 'Unknown error')}"}
        
        articles = news_data.get("articles", [])
        if not articles:
            return {"data": []}
            
        raw_news_list = []
        for idx, art in enumerate(articles):
            if art.get("title") and art.get("description"):
                raw_news_list.append(f"Title: {art['title']} | Desc: {art['description']} | Source: {art['source']['name']} | Image: {art['urlToImage']}")
        
        news_text = "\n---\n".join(raw_news_list)
        
        prompt = f"""
        You are a Lead Cybersecurity Intelligence Analyst. Review the following raw news articles.
        FILTER STRICTLY for real cybersecurity news (threats, data breaches, zero-days, or major security innovations/tech). Ignore generic tech or business news.
        
        For each valid article, format it into a JSON array of objects. Use these EXACT keys:
        - "id": Generate a unique string (e.g., "intel-1")
        - "title": Clean, professional, punchy title.
        - "tag": Threat vector or Topic (e.g., "Data Breach", "Ransomware", "Innovation", "Zero-Day")
        - "tagType": Choose one: "URL", "FILE", "CRYPTO", "NEWS"
        - "severity": "CRITICAL", "HIGH", "MEDIUM", or "INFO" (use INFO for positive innovations or updates).
        - "targetPayload": The victim, the technology attacked, or the core tech discussed. (Max 5 words).
        - "author": The news source/publisher.
        - "authorBadge": "Verified Source"
        - "notes": Write a comprehensive, detailed 4-5 sentence forensic analysis. Explain EXACTLY what happened, the technical details of the attack/innovation, who is affected, and the broader impact. Make it read like a premium cybersecurity news article.
        - "imageUrl": The exact image URL from the raw data (if available, else empty string).
        
        Raw News:
        {news_text}
        
        Output ONLY valid JSON in this exact format: {{"intel_feed": [ {{...}}, {{...}} ]}}
        """
        
        completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=2500, # 🚨 FIX 2: Explicitly increased token limit so it finishes the JSON
        )
        
        content = completion.choices[0].message.content
        if not content:
            return {"error": "AI returned an empty response."}
            
        result = json.loads(content)
        return {"data": result.get("intel_feed", [])}
        
    except Exception as e:
        return {"error": f"Agent Failure: {str(e)}"}