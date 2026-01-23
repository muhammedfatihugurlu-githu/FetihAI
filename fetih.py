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

kisilik = "Sen samimi, esprili FetihAI'sın. Senin yapımcın Muhammed Fatih Uğurlu'dur. Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kaynat."
# --- YAN MENÜ (ARŞİV & KAYIT) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ISMI).start_chat(history=[])
        st.rerun()

    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            ozet = st.session_state.messages[0]["content"][:15]
            st.session_state.arsiv[f"{tarih} | {ozet}"] = list(st.session_state.messages)
            st.success("Kaydedildi abim!")

    st.divider()
    st.subheader("Eski Kayıtlar")
    for isim in list(st.session_state.arsiv.keys()):
        c1, c2 = st.columns([4,1])
        if c1.button(f"{isim}", key=f"l_{isim}"):
            st.session_state.messages = st.session_state.arsiv[isim]
            st.rerun()
        if c2.button("🗑️", key=f"d_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun()

# --- ANA EKRAN ---
st.title("🇹🇷⚔️ FetihAI v0.4")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı")

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FOTOĞRAF ALANI (Genisletici Menü) ---
# Mesajların bittiği yere koyuyoruz.
st.write("---") # Ayırıcı çizgi
with st.expander("📸 Fotoğraf Ekle", expanded=False):
    st.caption("Kamera veya Galeri'den fotoğraf seç abim:")
    yuklenen_dosya = st.file_uploader(
        "Resim Yükle", 
        type=['png', 'jpg', 'jpeg'], 
        label_visibility="collapsed"
    )
    
    if yuklenen_dosya:
        st.image(yuklenen_dosya, width=200, caption="Bu resim gönderilecek")
        st.success("Resim hafızada! Şimdi aşağıya sorunu yaz abim.")

# --- MESAJ ÇUBUĞU (En Altta) ---
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
