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
    st.error("Secrets eksik abim! Streamlit panelinden HF_TOKEN ve OPENAI_API_KEY'i kontrol et.")
    st.stop()

# --- 🎨 SAYFA AYARLARI ---
st.set_page_config(page_title="FetihAI v3.1", page_icon="🇹🇷", layout="wide")

# --- 🧠 HAFIZA VE ARŞİV ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

# KOTA DOSTU MODEL: Günde 1500 istek hakkı verir, hata almazsın.
MODEL_NAME = 'gemini-1.5-flash' 

# --- 🛠️ FONKSİYONLAR ---

def guvenli_cevir(metin):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        res = model.generate_content(f"Sadece İngilizceye çevir (image prompt): {metin}")
        return res.text
    except: return metin

def resim_ciz_motoru(prompt_en):
    # ŞU ANIN EN HIZLI VE EN İYİ MODELİ: FLUX.1-schnell
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # 5 kere inatla deniyoruz
    for i in range(5):
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt_en}, timeout=40)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                st.toast(f"Motor ısınıyor, saniye {i*10+10}/50...", icon="💤")
                time.sleep(10) 
            else:
                time.sleep(2)
        except: continue
    return None

# --- 📜 YAN MENÜ (ARŞİV) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            baslik = f"{time.strftime('%H:%M')} | {st.session_state.messages[0]['content'][:15]}"
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Arşive eklendi!")

    st.divider()
    st.subheader("Geçmiş Sohbetler")
    for k in list(st.session_state.arsiv.keys()):
        if st.button(k, use_container_width=True):
            st.session_state.messages = st.session_state.arsiv[k]
            st.rerun()

# --- 🖥️ ANA EKRAN ---
st.title("🇹🇷 FetihAI v3.1")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🖼️ Resim Çizdir (Hızlı Mod)", expanded=False):
        hayal = st.text_input("Ne hayal ediyorsun?", key="draw_v3")
        if st.button("Hemen Çiz", use_container_width=True):
            if hayal:
                with st.spinner("FetihAI fırçasını kaptı, geliyor..."):
                    en_p = guvenli_cevir(hayal)
                    img_data = resim_ciz_motoru(en_p)
                    if img_data:
                        st.image(Image.open(io.BytesIO(img_data)), caption="Buyur abim!")
                    else:
                        st.error("Abim bu sefer sunucu gerçekten ağır bakımda. 2-3 dakika sonra tekrar denersen düzelecektir.")

with c2:
    with st.expander("📸 Fotoğraf Analizi", expanded=False):
        yukle = st.file_uploader("Dosya Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")

# --- 💬 SOHBET ---
if prompt := st.chat_input("Yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            if yukle:
                res = model.generate_content(["Resmi yorumla ve abine cevap ver:", Image.open(yukle), prompt])
            else:
                res = model.generate_content(f"Kullanıcı Muhammed Fatih. Samimi bir asistan gibi cevap ver: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except exceptions.ResourceExhausted:
            st.error("Google kota doldu, az bekle abim.")