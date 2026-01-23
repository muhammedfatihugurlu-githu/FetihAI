import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io

# --- GÜVENLİ ANAHTAR KONTROLLERİ ---
if "OPENAI_API_KEY" in st.secrets and "HF_TOKEN" in st.secrets:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("Secrets kısmında anahtarlar eksik abim!")
    st.stop()

st.set_page_config(page_title="FetihAI v2.1", page_icon="🇹🇷", layout="wide")

# --- ÇİZİM FONKSİYONU (HATA VERMEZ) ---
def resim_ciz_motoru(prompt_text):
    # Bu yöntem Google kütüphanesini KULLANMAZ, o yüzden hata vermez
    API_URL = "https://api-inference.huggingface.co/models/dreamlike-art/dreamlike-diffusion-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Sunucu uyanana kadar 3 deneme
    for i in range(3):
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text})
        if response.status_code == 200:
            return response.content
        time.sleep(5)
    return None

# --- ANA EKRAN ---
st.title("🇹🇷 FetihAI v2.1")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Göster
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- PANEL ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🖼️ Fotoğraf Oluştur", expanded=False):
        hayal = st.text_input("Ne çizeyim?", key="draw_input")
        if st.button("Çiz", use_container_width=True):
            if hayal:
                with st.spinner("Çiziliyor..."):
                    # Önce İngilizceye çevir (Huggingface için)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    en_prompt = model.generate_content(f"Translate to English: {hayal}").text
                    
                    # Çizdir
                    img_data = resim_ciz_motoru(en_prompt)
                    if img_data:
                        st.image(Image.open(io.BytesIO(img_data)))
                    else:
                        st.warning("Motor meşgul, birazdan tekrar dene abim.")

with c2:
    with st.expander("📸 Analiz", expanded=False):
        yuklenen = st.file_uploader("Dosya", type=['png','jpg','jpeg'], label_visibility="collapsed")

# --- SOHBET ---
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-2.0-flash')
        if yuklenen:
            img = Image.open(yuklenen)
            res = model.generate_content(["Sen FetihAI'sın, samimi ol.", img, prompt])
        else:
            res = model.start_chat().send_message(f"Samimi ol abime cevap ver: {prompt}")
        
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})