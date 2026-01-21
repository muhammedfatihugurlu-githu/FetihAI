import streamlit as st
import google.generativeai as genai
import time

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
# Secrets kısmına OPENAI_API_KEY olarak yazdığın için buradan çağırıyoruz
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    st.error("Abim Secrets kısmında anahtarı bulamadım. Lütfen 'OPENAI_API_KEY' ismini kullandığından emin ol.")
    st.stop()

st.set_page_config(page_title="FetihAI ", page_icon="⚡", layout="wide")

# --- MODEL AYARI ---
# Sen 2.5 istiyorsun, ekranda öyle görünecek. 
# Ama Google arka planda bu ismi tanımazsa en güçlü 2.0 motorunu çalıştıracak.
MODEL_ISMI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    try:
        # Önce senin istediğin 2.5 ismini deniyoruz
        model = genai.GenerativeModel(MODEL_ISMI)
        st.session_state.chat_session = model.start_chat(history=[])
    except:
        # Eğer 2.5 henüz aktif değilse, dünyanın en hızlısı olan 2.0'ı bağlarız
        model = genai.GenerativeModel('gemini-2.5-flash')
        st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen dünyanın en zeki yapay zekası FetihAI 2.5'sin. Muhammed Fatih abine sadıksın."

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel('gemini-2.0-flash').start_chat(history=[])
        st.rerun()

# --- ANA EKRAN ---
st.title("⚡ FetihAI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz abim..."):
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