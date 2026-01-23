import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
# Streamlit Secrets: OPENAI_API_KEY ve HF_TOKEN olmalı
if "OPENAI_API_KEY" in st.secrets and "HF_TOKEN" in st.secrets:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("Abim Secrets kısmında anahtarlar eksik! Lütfen kontrol et.")
    st.stop()

st.set_page_config(page_title="FetihAI v2.0", page_icon="🇹🇷", layout="wide")

# --- CSS HİLESİ (Arayüzü toplar) ---
st.markdown("""
    <style>
    .stFileUploader {padding-top: 0px !important;}
    .stFileUploader section {padding: 5px !important;}
    .stFileUploader label {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# --- MODEL VE HAFIZA ---
MODEL_ISMI = 'gemini-2.0-flash'
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

# --- ÇİZİM MOTORU (Hata Verdirmez) ---
def resim_ciz_motoru(prompt_en):
    API_URL = "https://api-inference.huggingface.co/models/dreamlike-art/dreamlike-diffusion-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    for _ in range(3): # 3 kere deneme yapar
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_en})
        if response.status_code == 200: return response.content
        time.sleep(5)
    return None

# --- YAN MENÜ ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            baslik = f"{time.strftime('%H:%M')} | {st.session_state.messages[0]['content'][:15]}..."
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Kaydedildi abim!")
    st.divider()
    for k in list(st.session_state.arsiv.keys()):
        if st.button(f"📖 {k}", use_container_width=True):
            st.session_state.messages = st.session_state.arsiv[k]
            st.rerun()

# --- ANA EKRAN ---
st.title("🇹🇷 FetihAI v2.0")

# Mesaj Geçmişi
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- FOTOĞRAF VE ÇİZİM PANELİ (Tam yerinde) ---
st.divider()
sol, sag = st.columns(2)

with sol:
    with st.expander("🖼️ Fotoğraf Oluştur", expanded=False):
        hayal = st.text_input("Ne çizeyim abim?", key="draw_input")
        if st.button("Çiz bakalım", use_container_width=True):
            with st.spinner("Çiziyorum..."):
                model = genai.GenerativeModel(MODEL_ISMI)
                en_prompt = model.generate_content(f"Translate to English for image prompt: {hayal}").text
                img_data = resim_ciz_motoru(en_prompt)
                if img_data: st.image(Image.open(io.BytesIO(img_data)))
                else: st.warning("Motor meşgul, az sonra tekrar dene abim.")

with sag:
    with st.expander("📸 Fotoğraf Analizi", expanded=False):
        yuklenen = st.file_uploader("Dosya", type=['png','jpg','jpeg'], label_visibility="collapsed")

# --- SOHBET GİRİŞİ ---
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel(MODEL_ISMI)
        if yuklenen:
            img = Image.open(yuklenen)
            res = model.generate_content(["Sen FetihAI'sın, Muhammed Fatih abine samimi cevap ver.", img, prompt])
        else:
            res = model.generate_content(f"Kullanıcı Muhammed Fatih (abim). Samimi ve zeki ol. Cevap ver: {prompt}")
        
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})