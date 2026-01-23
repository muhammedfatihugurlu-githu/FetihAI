import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io
from google.api_core import exceptions

# --- 🔑 ANAHTAR KONTROLLERİ ---
if "OPENAI_API_KEY" in st.secrets and "HF_TOKEN" in st.secrets:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("Secrets eksik abim!")
    st.stop()

# --- 🎨 SAYFA AYARLARI ---
st.set_page_config(page_title="FetihAI v3.0", page_icon="🇹🇷", layout="wide")

# --- 🧠 HAFIZA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

# KOTA DOSTU MODEL (Günde 1500 İstek)
MODEL_NAME = 'gemini-2.5-flash' 

# --- 🛠️ FONKSİYONLAR ---

def guvenli_cevir(metin):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        res = model.generate_content(f"Translate this to a detailed English image prompt: {metin}")
        return res.text
    except: return metin

def resim_ciz_motoru(prompt_en):
    # Daha yeni ve hızlı uyanan bir model: Stable Diffusion 2.1
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Sunucu uyanana kadar inatla 5 kere deniyoruz
    for i in range(5):
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt_en}, timeout=30)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                st.toast(f"Sunucu uyanıyor abim, bekle... (Deneme {i+1}/5)", icon="💤")
                time.sleep(12) # Bekleme süresini artırdık
            else:
                time.sleep(5)
        except:
            continue
    return None

# --- 📜 YAN MENÜ ---
with st.sidebar:
    st.title("📜 Arşiv")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("💾 Kaydet", use_container_width=True):
        if st.session_state.messages:
            st.session_state.arsiv[f"{time.strftime('%H:%M')} | Sohbet"] = list(st.session_state.messages)
            st.success("Kaydedildi!")
    st.divider()
    for k in list(st.session_state.arsiv.keys()):
        if st.button(k, use_container_width=True):
            st.session_state.messages = st.session_state.arsiv[k]
            st.rerun()

# --- 🖥️ ANA EKRAN ---
st.title("🇹🇷 FetihAI v3.0")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🖼️ Resim Çizdir", expanded=False):
        hayal = st.text_input("Ne çizelim?", key="draw")
        if st.button("Emret Çizeyim", use_container_width=True):
            if hayal:
                with st.spinner("Motoru ısıtıyorum, biraz sürebilir..."):
                    en_prompt = guvenli_cevir(hayal)
                    img = resim_ciz_motoru(en_prompt)
                    if img: st.image(Image.open(io.BytesIO(img)))
                    else: st.error("Sunucu şu an gerçekten kapalı abim, 1-2 dakika sonra tekrar dene.")

with c2:
    with st.expander("📸 Resim Analiz", expanded=False):
        yukle = st.file_uploader("Dosya", type=['png','jpg','jpeg'], label_visibility="collapsed")

# --- 💬 SOHBET ---
if prompt := st.chat_input("Yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            if yukle:
                res = model.generate_content(["Cevap ver:", Image.open(yukle), prompt])
            else:
                res = model.generate_content(f"Kullanıcı Muhammed Fatih. Samimi ol: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except exceptions.ResourceExhausted:
            st.error("Kota doldu abim.")