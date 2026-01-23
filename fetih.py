import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io
from google.api_core import exceptions

# --- ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets and "HF_TOKEN" in st.secrets:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("Secrets eksik abim!")
    st.stop()

st.set_page_config(page_title="FetihAI v2.2", page_icon="🇹🇷")

# --- KOTA DOSTU ÇEVİRİ FONKSİYONU ---
def guvenli_cevir(metin):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Kotayı yormamak için kısa ve net bir sistem mesajıyla çeviriyoruz
        response = model.generate_content(f"Translate this to English for an image prompt, only output the translation: {metin}")
        return response.text
    except exceptions.ResourceExhausted:
        st.error("Google kotası doldu abim, 1 dakika bekleyip tekrar dene.")
        return None
    except Exception as e:
        return metin # Hata olursa olduğu gibi gönder

# --- RESİM ÇİZME MOTORU ---
def resim_ciz(prompt_en):
    API_URL = "https://api-inference.huggingface.co/models/dreamlike-art/dreamlike-diffusion-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt_en})
    if response.status_code == 200: return response.content
    return None

# --- ARAYÜZ ---
st.title("🇹🇷 FetihAI v2.2")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Göster
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🖼️ Fotoğraf Oluştur", expanded=False):
        hayal = st.text_input("Ne çizeyim?", key="draw_input")
        if st.button("Çiz", use_container_width=True):
            if hayal:
                with st.spinner("İşleniyor..."):
                    en_prompt = guvenli_cevir(hayal)
                    if en_prompt:
                        img_data = resim_ciz(en_prompt)
                        if img_data: st.image(Image.open(io.BytesIO(img_data)))
                        else: st.warning("Çizim motoru meşgul, tekrar dene.")

with c2:
    with st.expander("📸 Analiz", expanded=False):
        yuklenen = st.file_uploader("Dosya", type=['png','jpg','jpeg'], label_visibility="collapsed")

# --- SOHBET ---
if prompt := st.chat_input("Yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            if yuklenen:
                res = model.generate_content(["Abine cevap ver.", Image.open(yuklenen), prompt])
            else:
                res = model.generate_content(f"Sen FetihAI'sın, abine cevap ver: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except exceptions.ResourceExhausted:
            st.error("Google çok yoğun abim, mesajını 30 saniye sonra tekrar gönder.")