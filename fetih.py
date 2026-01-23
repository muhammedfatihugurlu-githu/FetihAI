import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io
import urllib.parse

# --- 🔑 ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Abim Secrets kısmında OPENAI_API_KEY eksik!")
    st.stop()

# --- 🎨 SAYFA AYARLARI ---
st.set_page_config(page_title="FetihAI v4.1", page_icon="🇹🇷", layout="wide")

# --- 🧠 HAFIZA VE ARŞİV ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

MODEL_NAME = 'gemini-1.5-flash'

# --- 🛠️ YENİ NESİL ÇİZİM MOTORU (GÜÇLENDİRİLMİŞ) ---
def resim_ciz_hizli(prompt_tr):
    try:
        # 1. Adım: Gemini ile süslemeye çalış
        prompt_en = prompt_tr # Varsayılan olarak Türkçesini tut
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            cevap = model.generate_content(f"Translate to English for image generation (short, artistic): {prompt_tr}", request_options={"timeout": 10})
            if cevap.text:
                prompt_en = cevap.text
        except:
            pass # Gemini hata verirse Türkçe devam et (Pollinations anlıyor)

        # 2. Adım: Pollinations'a gönder
        encoded_prompt = urllib.parse.quote(prompt_en)
        # Seed ekleyerek her seferinde farklı resim gelmesini sağlıyoruz
        seed = int(time.time())
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
        
        response = requests.get(image_url, timeout=45)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        return None

# --- 📜 YAN MENÜ (ARŞİV) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            baslik = f"{tarih} | {st.session_state.messages[0]['content'][:15]}..."
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Kaydedildi!")

    st.divider()
    for k in list(st.session_state.arsiv.keys()):
        if st.button(k, use_container_width=True):
            st.session_state.messages = st.session_state.arsiv[k]
            st.rerun()

# --- 🖥️ ANA EKRAN ---
st.title("🇹🇷 FetihAI v4.1")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🖼️ Hızlı Resim Çizdir", expanded=False):
        hayal = st.text_input("Ne hayal ediyorsun?", key="draw_v41")
        if st.button("Hemen Oluştur", use_container_width=True):
            if hayal:
                with st.spinner("FetihAI fırçasını hazırladı..."):
                    img_bytes = resim_ciz_hizli(hayal)
                    if img_bytes:
                        st.image(Image.open(io.BytesIO(img_bytes)), caption="Buyur abim!")
                    else:
                        st.error("Sunucu hattında bir kopukluk oldu. Lütfen tekrar bas abim.")
            else:
                st.info("Bir şeyler yazman lazım abim.")

with c2:
    with st.expander("📸 Fotoğraf Analizi", expanded=False):
        yukle = st.file_uploader("Resim Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")

# --- 💬 SOHBET ---
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            if yukle:
                res = model.generate_content(["Abine samimi cevap ver:", Image.open(yukle), prompt])
            else:
                res = model.generate_content(f"Muhammed Fatih abine samimi ve zeki bir asistan gibi cevap ver: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except:
            st.error("Sohbet motorunda bir takılma oldu.")