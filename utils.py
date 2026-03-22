import streamlit as st
from openai import OpenAI
import time
import re
import markdown
import html
import unicodedata

token = st.secrets.get("HF_TOKEN")
if not token:
    st.error("Missing HF_TOKEN in secrets")
    st.stop()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=token,
)

def generate_ai(prompt):
    last_error = ""
    for _ in range(3):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role":"system","content":"You are an elite branding strategist and python developer."},
                    {"role":"user","content":prompt}
                ],
                max_tokens=3000, 
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = str(e) # Save the error message
            time.sleep(2)
            
    # If it fails 3 times, show the error on the UI
    st.error(f"🚨 API Connection Failed: {last_error}")
    return None

def extract_json(text):
    if not text:
        return None
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        import json
        try:
            return json.loads(match.group())
        except:
            return None
    return None

def normalize_text(text):
    if not text:
        return ""
    html_text = markdown.markdown(text)
    clean = re.sub('<.*?>', '', html_text)
    clean = html.unescape(clean)
    clean = unicodedata.normalize("NFKD", clean).encode("ascii", "ignore").decode("ascii")
    return clean

def glass_card(text):
    st.markdown(f'<div class="glass">{text}</div>', unsafe_allow_html=True)

def font_card(font):
    font_url = font.replace(" ", "+")
    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family={font_url}&display=swap" rel="stylesheet">
    <div class="glass">
    <p style="font-family:'{font}', sans-serif; font-size:28px; margin-bottom:6px;">{font}</p>
    <p style="font-family:'{font}', sans-serif; opacity:0.7;">The quick brown fox jumps over the lazy dog.</p>
    </div>
    """, unsafe_allow_html=True)
