import streamlit as st
import google.generativeai as genai
import time

# --- GÜVENLİ ANAHTAR SİSTEMİ ---
if "AIzaSyCNlmOq4hp991IxUJU6ra_22_axM66M2As" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["AIzaSyCNlmOq4hp991IxUJU6ra_22_axM66M2As"]
else:
    st.error("Secrets kısmına anahtarı girmemişsin abim!")
    st.stop()

genai.configure(api_key=SİHİRLİ_ANAHTAR)

st.set_page_config(page_title="FetihAI v0.3", page_icon="🇹🇷⚔️", layout="wide")

# --- MODEL AYARI: SADECE 2.5 ---
MODEL_ADI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 
if "chat_session" not in st.session_state:
    # Direkt senin istediğin ismi deniyoruz
    model = genai.GenerativeModel(MODEL_ADI)
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et."
# --- YAN MENÜ ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    st.info(f"Aktif Motor: {MODEL_ADI}")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ADI).start_chat(history=[])
        st.rerun()

    if st.button("💾 Sohbeti Arşivle", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            baslik = f"{tarih} | {st.session_state.messages[0]['content'][:15]}..."
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.toast("Arşivlendi!")
    
    st.subheader("Eski Sohbetler")
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
            st.error(f"Hata: {e}")