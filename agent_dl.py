import os
import pickle
import re
from dotenv import load_dotenv
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_SECRET_KEY", ""))

print("⏳ Loading DL Models & Vector Engine...")
with open("advanced_msg_tokenizer.pkl", "rb") as f:
    text_tokenizer = pickle.load(f)
text_model = load_model("advanced_msg_model.h5")

with open("char_tokenizer.pkl", "rb") as f:
    url_tokenizer = pickle.load(f)
url_model = load_model("url_cnn_model.h5")

embedder = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ DL Agents Ready!")

def clean_url(url_str):
    return re.sub(r'^www\.', '', re.sub(r'^https?:\/\/', '', str(url_str).lower()))

# Yahan apne clz, government, aur known normal domains daal de
EXACT_SAFE_DOMAINS = ["csjmu.ac.in", "google.com", "github.com", "linkedin.com", "sbi.co.in"]

def run_dl_scan(url: str | None, message: str | None):
    url_result, message_result, rag_context = None, None, []

    if url and url.strip():
        cleaned = clean_url(url)
        
        # 1. Exact Safelist Check (Bypass AI only for highly trusted known sites)
        if cleaned in EXACT_SAFE_DOMAINS:
            url_result = "SAFE (0.1%)"
        else:
            # 2. Universal Deep Learning Scan (For the rest of the internet)
            url_seq = url_tokenizer.texts_to_sequences([cleaned])
            url_pad = pad_sequences(url_seq, maxlen=80, padding='post', truncating='post')
            url_score = float(url_model.predict(url_pad, verbose=0)[0][0]) # type: ignore
            url_result = f"{'DANGER' if url_score > 0.5 else 'SAFE'} ({round(url_score*100, 1)}%)"
        
        # RAG Vector Search
        url_vector = embedder.encode(cleaned).tolist()
        db_match = supabase.rpc('match_threats', {'query_embedding': url_vector, 'match_threshold': 0.85, 'match_count': 1}).execute()
        if db_match.data: 
            rag_context.append(f"URL DB Info: {db_match.data[0]['description']}") # type: ignore

    if message and message.strip():
        msg_seq = text_tokenizer.texts_to_sequences([message])
        msg_pad = pad_sequences(msg_seq, maxlen=50, padding='post', truncating='post')
        msg_score = float(text_model.predict(msg_pad, verbose=0)[0][0]) # type: ignore
        message_result = f"{'DANGER' if msg_score > 0.5 else 'SAFE'} ({round(msg_score*100, 1)}%)"

    return {"url_dl": url_result, "msg_dl": message_result, "db_context": rag_context}