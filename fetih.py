import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io
from google.api_core import exceptions

# --- 🔑 GÜVENLİ ANAHTARLAR ---
if "OPENAI_API_KEY" in st.secrets and "HF_TOKEN" in st.secrets:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("Abim Secrets kısmında OPENAI_API_KEY veya HF_TOKEN eksik!")
    st.stop()

# --- 🎨 SAYFA AYARLARI VE TASARIM ---
st.set_page_config(page_title="FetihAI v2.5", page_icon="🇹🇷", layout="wide")

st.markdown("""
    <style>
    /* Dosya yükleme alanını küçültme */
    .stFileUploader {min-height: 0px !important; padding-top: 0px !important;}
    .stFileUploader section {padding: 5px !important; border-radius: 10px !important;}
    .stFileUploader label {display: none !important;}
    /* Arşiv butonu tasarımı */
    .stButton > button {border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 HAFIZA VE ARŞİV MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

MODEL_ISMI = 'gemini-2.5-flash'

# --- 🛠️ FONKSİYONLAR ---

def guvenli_cevir(metin):
    """Resim çizimi için Türkçeyi İngilizceye çevirir (Kota korumalı)"""
    try:
        model = genai.GenerativeModel(MODEL_ISMI)
        res = model.generate_content(f"Translate to English for an image prompt: {metin}")
        return res.text
    except exceptions.ResourceExhausted:
        st.error("Google kotası doldu, 30 saniye bekle abim.")
        return None
    except: return metin

def inatci_resim_ciz(prompt_en):
    """HuggingFace motorunu uyanana kadar 3 kere dener"""
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    for i in range(3):
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_en})
        if response.status_code == 200:
            return response.content
        elif response.status_code in [503, 429]:
            time.sleep(8) # Motorun uyanması için bekle
            continue
    return None

# --- 📜 YAN MENÜ (ARŞİV) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💾 Mevcut Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M:%S")
            baslik = f"{tarih} | {st.session_state.messages[0]['content'][:15]}..."
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Arşive eklendi!")
    
    st.divider()
    st.subheader("Eski Sohbetler")
    for key in list(st.session_state.arsiv.keys()):
        if st.button(key, use_container_width=True):
            st.session_state.messages = st.session_state.arsiv[key]
            st.rerun()

# --- 🖥️ ANA EKRAN ---
st.title("🇹🇷 FetihAI v2.5")

# Mesaj Geçmişini Yazdır
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 📸 ARAÇLAR PANELI ---
st.divider()
sol, sag = st.columns(2)

with sol:
    with st.expander("🖼️ Fotoğraf Oluştur", expanded=False):
        hayal = st.text_input("Ne hayal ediyorsun abim?", key="hayal_input")
        if st.button("Hayali Çiz", use_container_width=True):
            if hayal:
                with st.spinner("FetihAI fırçasını hazırlıyor..."):
                    en_prompt = guvenli_cevir(hayal)
                    if en_prompt:
                        img_data = inatci_resim_ciz(en_prompt)
                        if img_data:
                            st.image(Image.open(io.BytesIO(img_data)), caption="Buyur abim.")
                        else:
                            st.warning("Çizim motoru şu an uykuda, 10 saniye sonra tekrar bas uyanacaktır.")
            else:
                st.info("Önce bir şeyler yaz abim.")

with sag:
    with st.expander("📸 Fotoğraf Analiz Et", expanded=False):
        yuklenen = st.file_uploader("Dosya Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")
        if yuklenen:
            st.image(yuklenen, width=150)

# --- 💬 SOHBET GİRİŞİ ---
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(MODEL_ISMI)
            if yuklenen:
                img = Image.open(yuklenen)
                res = model.generate_content(["Sen samimi FetihAI'sın. Muhammed Fatih abine cevap ver.", img, prompt])
            else:
                res = model.generate_content(f"Kullanıcı: Muhammed Fatih. Samimi ol. Cevap ver: {prompt}")
            
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except exceptions.ResourceExhausted:
            st.error("Google çok yoğun, 30 saniye sonra tekrar dene abim.")