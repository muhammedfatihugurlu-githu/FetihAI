import streamlit as st
import google.generativeai as genai

# --- AYARLAR ---
SİHİRLİ_ANAHTAR = "AIzaSyB4unpScQ46PpwROLrOgCaZ9t0mbk_Zkpk"
genai.configure(api_key=SİHİRLİ_ANAHTAR)

# Web Sayfası Başlığı
st.set_page_config(page_title="FetihAI Web", page_icon="⚔️")

st.title("⚔️ FetihAI")

# Yapay Zeka Kurulumu
if "messages" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash')
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

kisilik = "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et."

# Eski Mesajları Ekranda Tut
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mesaj Gönderme Alanı
if prompt := st.chat_input("Mesajını yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # AI'ya kişiliği hatırlatarak sor
            response = st.session_state.chat.send_message(f"{kisilik}\nSoru: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata: {e}")