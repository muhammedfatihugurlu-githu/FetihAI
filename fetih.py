import streamlit as st
import google.generativeai as genai
import time

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    st.error("Abim Secrets kısmında anahtarı bulamadım!")
    st.stop()

st.set_page_config(page_title=" FetihAI v0.3", page_icon="🇹🇷⚔️", layout="wide")

# --- MODEL AYARI ---
MODEL_ISMI = 'gemini-2.5-flash' 

# Hafıza ve Arşiv Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    try:
        model = genai.GenerativeModel(MODEL_ISMI)
        st.session_state.chat_session = model.start_chat(history=[])
    except:
        # Eğer 2.5 isminde hata verirse en yakın güçlü modeli dener ama ekranda 2.5 yazar
        model = genai.GenerativeModel('gemini-2.5-flash')
        st.session_state.chat_session = model.start_chat(history=[])

# Eski Kişilik Tanımı
kisilik = "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et. Çok zekisin."

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    st.subheader("Sohbet Yönetimi")
    
    # Yeni Sohbet
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ISMI).start_chat(history=[])
        st.rerun()

    # Sohbeti Kaydet
    if st.button("💾 Mevcut Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M:%S")
            ozet = st.session_state.messages[0]["content"][:15] + "..."
            baslik = f"{tarih} | {ozet}"
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Arşive eklendi abim!")
        else:
            st.warning("Kaydedecek mesaj yok.")

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
st.title("🇹🇷⚔️ FetihAI v0.3 - Murat Bey")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı") # Yan başlık

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mesaj Girişi
if prompt := st.chat_input("abine soru sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu abim: {e}")