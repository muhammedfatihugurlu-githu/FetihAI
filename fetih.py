import streamlit as st
import google.generativeai as genai
import time
from PIL import Image

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    st.error("Abim Secrets kısmında anahtarı bulamadım!")
    st.stop()

st.set_page_config(page_title="FetihAI v0.4", page_icon="🇹🇷⚔️", layout="wide")

# --- 🎨 ÖZEL TASARIM (CSS) ---
# Bu kısım o koca "Browse Files" kutusunu ve ikonları küçültür
st.markdown("""
    <style>
    /* Dosya yükleme alanını küçült */
    .stFileUploader {
        min-height: 0px !important;
        padding-top: 0px !important;
    }
    .stFileUploader section {
        padding: 5px !important;
        border-radius: 10px !important;
    }
    /* "Browse files" yazısını ve ikonu küçült */
    .stFileUploader label {
        display: none !important; /* Etiketi gizle */
    }
    .stFileUploader div div {
        font-size: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MODEL AYARI ---
MODEL_ISMI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kaynat"

# --- YAN MENÜ ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ISMI).start_chat(history=[])
        st.rerun()
    if st.button("💾 Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            st.session_state.arsiv[f"{tarih} | Sohbet"] = list(st.session_state.messages)
            st.success("Kaydedildi!")

# --- ANA EKRAN ---
st.title("🇹🇷⚔️ FetihAI v0.4")

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- KÜÇÜLTÜLMÜŞ FOTOĞRAF ALANI ---
st.divider()
with st.expander("📸 Fotoğraf Ekle", expanded=False):
    # 'label_visibility' gizlendi ve CSS ile kutu daraltıldı
    yuklenen_dosya = st.file_uploader(
        "Resim", 
        type=['png', 'jpg', 'jpeg'], 
        label_visibility="collapsed"
    )
    if yuklenen_dosya:
        st.image(yuklenen_dosya, width=150)

# --- MESAJ ÇUBUĞU ---
if prompt := st.chat_input("İstediğini yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if yuklenen_dosya:
                img = Image.open(yuklenen_dosya)
                model_multi = genai.GenerativeModel(MODEL_ISMI)
                response = model_multi.generate_content([f"{kisilik}\nSoru: {prompt}", img])
            else:
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata: {e}")