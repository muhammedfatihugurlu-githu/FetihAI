import streamlit as st
import google.generativeai as genai
import time

# --- AYARLAR ---
SİHİRLİ_ANAHTAR = "AIzaSyCNlmOq4hp991IxUJU6ra_22_axM66M2As"
genai.configure(api_key=SİHİRLİ_ANAHTAR)

st.set_page_config(page_title="FetihAI v0.3", page_icon="🇹🇷⚔️", layout="wide")

# --- HAFIZA VE ARŞİV KURULUMU ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

# MODEL BURADA: Gemini 2.0 Flash
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.0-flash')
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et."

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    st.info("Model: Gemini 2.5 Flash 🚀")
    
    # Yeni Sohbet Butonu
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel('gemini-2.5-flash').start_chat(history=[])
        st.rerun()

    st.divider()
    
    # Mevcut Sohbeti Kaydetme
    if st.button("💾 Mevcut Sohbeti Arşivle", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            ozet = st.session_state.messages[0]["content"][:15] + "..."
            baslik = f"{tarih} | {ozet}"
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Arşive eklendi!")
        else:
            st.warning("Henüz mesaj yok abim.")

    st.divider()

    # Arşiv Listesi
    st.subheader("Eski Fetihler")
    for isim in list(st.session_state.arsiv.keys()):
        col1, col2 = st.columns([4, 1])
        if col1.button(f"📖 {isim}", key=f"load_{isim}"):
            st.session_state.messages = st.session_state.arsiv[isim]
            st.rerun()
        if col2.button("🗑️", key=f"del_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun()

# --- ANA EKRAN ---
st.title("🇹🇷⚔️ FetihAI v0.3")

# Eski Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mesaj Gönderimi
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 2.0 Flash Yanıtı
            response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu abim: {e}")