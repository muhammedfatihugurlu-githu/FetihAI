import streamlit as st
import google.generativeai as genai
import time
from PIL import Image

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    # For testing UI
    genai.configure(api_key="dummy")
    # st.error("Abim Secrets kısmında anahtarı bulamadım!")
    # st.stop()

st.set_page_config(page_title="FetihAI v0.4", page_icon="🇹🇷⚔️", layout="wide")

# --- MODEL AYARI ---
MODEL_ISMI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])
if "yuklenen_dosya" not in st.session_state:
    st.session_state.yuklenen_dosya = None
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False

kisilik =  "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kat."


# --- YAN MENÜ (ARŞİV) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ISMI).start_chat(history=[])
        st.rerun()

    if st.button("💾 Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            ozet = st.session_state.messages[0]["content"][:15]
            st.session_state.arsiv[f"{tarih} | {ozet}"] = list(st.session_state.messages)
            st.success("Kaydedildi!")

    st.divider()
    for isim in list(st.session_state.arsiv.keys()):
        c1, c2 = st.columns([4,1])
        if c1.button(f"{isim}", key=f"l_{isim}"):
            st.session_state.messages = st.session_state.arsiv[isim]
            st.rerun()
        if c2.button("X", key=f"d_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun()

# --- ANA EKRAN ---
st.title("🇹🇷⚔️ FetihAI v0.4")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı") # Yan Başlık

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MESAJ ÇUBUĞU ---
st.markdown("<div style='height: 300px;'></div>")  # Spacer to push chat bar to bottom

st.markdown("""
<style>
[data-testid="stButton"] button {
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
}
</style>
""", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([0.08, 0.92])
    with col1:
        if st.button("📷", use_container_width=True):
            st.session_state.show_uploader = not st.session_state.show_uploader
    with col2:
        prompt = st.chat_input("İstediğini yaz abim...")

if st.session_state.show_uploader:
    with st.popover("Fotoğraf Seç"):
        st.info("Kamera veya Galeriden Seç Abim 👇")
        yuklenen_dosya = st.file_uploader(
            "Resim Yükle", 
            type=['png', 'jpg', 'jpeg'], 
            label_visibility="collapsed"
        )
        
        if yuklenen_dosya:
            st.session_state.yuklenen_dosya = yuklenen_dosya
            st.image(yuklenen_dosya, caption="Ne isteyecektin...", width=150)
            st.session_state.show_uploader = False

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if st.session_state.yuklenen_dosya:
                img = Image.open(st.session_state.yuklenen_dosya)
                model_multi = genai.GenerativeModel(MODEL_ISMI)
                response = model_multi.generate_content([f"{kisilik}\nSoru: {prompt}", img])
            else:
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")

            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata verdi abim: {e}")
