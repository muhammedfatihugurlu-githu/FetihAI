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
    st.error("Abim Secrets kısmında OPENAI_API_KEY veya HF_TOKEN eksik!")
    st.stop()

# --- 🎨 SAYFA AYARLARI ---
st.set_page_config(page_title="FetihAI v2.6", page_icon="🇹🇷", layout="wide")

# CSS: Arayüzü toparlar
st.markdown("""
    <style>
    .stFileUploader {min-height: 0px !important;}
    .stFileUploader label {display: none !important;}
    .stChatFloatingInputContainer {padding-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 HAFIZA VE ARŞİV SİSTEMİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

MODEL_NAME = 'gemini-2.5-flash'

# --- 🛠️ FONKSİYONLAR ---

def guvenli_cevir(metin):
    """Kota hatasına karşı dirençli çeviri"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        res = model.generate_content(f"Translate this to English (only output translation): {metin}")
        return res.text
    except exceptions.ResourceExhausted:
        st.error("Google kotası doldu, 15-20 saniye bekle abim.")
        return None
    except: return metin

def resim_ciz_inatci(prompt_en):
    """Motor uyanana kadar 4 defa dener"""
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    deneme_sayisi = 4
    for i in range(deneme_sayisi):
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_en})
        if response.status_code == 200:
            return response.content
        elif response.status_code in [503, 429]:
            # Motor yükleniyor demektir, bekle ve mesaj ver
            if i < deneme_sayisi - 1:
                st.toast(f"Motor uyanıyor... Deneme {i+1}/{deneme_sayisi}", icon="💤")
                time.sleep(10) # 10 saniye bekle ve tekrar dene
            continue
    return None

# --- 📜 YAN MENÜ (ARŞİV) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih_saat = time.strftime("%H:%M:%S")
            baslik = f"{tarih_saat} | {st.session_state.messages[0]['content'][:15]}..."
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.sidebar.success("Kaydedildi!")

    st.divider()
    st.subheader("Eski Kayıtlar")
    for key in list(st.session_state.arsiv.keys()):
        if st.button(key, use_container_width=True):
            st.session_state.messages = st.session_state.arsiv[key]
            st.rerun()

# --- 🖥️ ANA EKRAN ---
st.title("🇹🇷 FetihAI v2.6")

# Sohbet geçmişini göster
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 🛠️ ARAÇ PANELI ---
st.divider()
col_ciz, col_analiz = st.columns(2)

with col_ciz:
    with st.expander("🖼️ Fotoğraf Oluştur", expanded=False):
        cizim_input = st.text_input("Ne hayal ediyorsun abim?", key="ciz_in")
        if st.button("Hayali Çiz", use_container_width=True):
            if cizim_input:
                with st.spinner("FetihAI hayal ediyor... (Motor uyanıyor olabilir)"):
                    ing_prompt = guvenli_cevir(cizim_input)
                    if ing_prompt:
                        img_bytes = resim_ciz_inatci(ing_prompt)
                        if img_bytes:
                            st.image(Image.open(io.BytesIO(img_bytes)), caption="Buyur abim, çizdim.")
                        else:
                            st.error("Motor şu an çok ağır uykuda, 30 saniye sonra tekrar dener misin?")
            else:
                st.info("Çizmem için bir şeyler yazmalısın abim.")

with col_analiz:
    with st.expander("📸 Fotoğraf Analizi", expanded=False):
        dosya = st.file_uploader("Resim Seç", type=['png','jpg','jpeg'], key="analiz_yukle")
        if dosya:
            st.image(dosya, width=150)

# --- 💬 SOHBET GİRİŞİ ---
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            if dosya:
                img_data = Image.open(dosya)
                response = model.generate_content(["Sen samimi FetihAI'sın, abine cevap ver.", img_data, prompt])
            else:
                response = model.generate_content(f"Muhammed Fatih abine samimi cevap ver: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except exceptions.ResourceExhausted:
            st.error("Google kotası doldu, biraz bekle abim.")
        except Exception as e:
            st.error(f"Hata oluştu abim: {e}")