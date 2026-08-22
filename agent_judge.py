import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Ab isko API key 100% milegi
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

def get_master_verdict(dl_report, brand_report):
    prompt = f"""
    You are the Senior Master Judge AI for a Cybersecurity Threat Radar.
    Review the independent agent reports below:
    
    1. Brand Detective: {brand_report}
    2. Deep Learning & DB Scanners: {dl_report}
    
    Rule: If the Brand Detective flags HIGH RISK typosquatting, output DANGER immediately regardless of the DL model's score.
    Rule 1: If Brand Detective says "HIGH RISK", "CRITICAL RISK", or "WARNING", you MUST output [DANGER].
    Rule 2: Never trust the Deep Learning score if the Brand Detective flags an issue.
    
    Provide a final, authoritative 2-sentence verdict advising the user. Start with [DANGER] or [SAFE].
    """
   # ...
    response = groq_client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="openai/gpt-oss-20b",
        temperature=0.1,
    )
    return response.choices[0].message.content