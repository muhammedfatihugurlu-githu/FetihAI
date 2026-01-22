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

# --- MODEL AYARI ---
MODEL_ISMI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et. Çok zekisin. Kullanıcılara cana yakın cevaplar ver."
# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ISMI).start_chat(history=[])
        st.rerun()

    st.divider()
    st.subheader("📁 Kaydedilen Sohbetler")
    for isim in list(st.session_state.arsiv.keys()):
        col1, col2 = st.columns([4, 1])
        if col1.button(f"📖 {isim}", key=f"load_{isim}"):
            st.session_state.messages = st.session_state.arsiv[isim]
            st.rerun()
        if col2.button("🗑️", key=f"del_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun()

# --- ANA EKRAN ---
st.title("🇹🇷⚔️ FetihAI v0.4")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı")

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GÖRSEL YÜKLEME (ARTI SEMBOLÜ) ---
# Mesaj çubuğunun hemen üzerinde duracak şekilde ayarladık
col1, col2 = st.columns([1, 10])
with col1:
    # label'ı boş bıraktık ki sadece buton gibi dursun
    yuklenen_dosya = st.file_uploader("➕", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

if yuklenen_dosya:
    st.info("Görsel hazır abim, şimdi mesajını yazıp sorabilirsin.")
    st.image(yuklenen_dosya, width=100)

# Mesaj Girişi
if prompt := st.chat_input("İstediğini yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if yuklenen_dosya:
                img = Image.open(yuklenen_dosya)
                model_multi = genai.GenerativeModel(MODEL_ISMI)
                # Görselle birlikte soruyu gönder
                response = model_multi.generate_content([f"{kisilik}\nSoru: {prompt}", img])
            else:
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu abim: {e}")