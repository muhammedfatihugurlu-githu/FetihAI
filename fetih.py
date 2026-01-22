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

# Session State Tanımları
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])

# Samimi Kişilik
kisilik =  "Sen samimi, esprili FetihAI'sın. Muhammed Fatih'e 'abim' diye hitap et. Çok zekisin. Kullanıcılara cana yakın cevaplar ver."

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    st.subheader("İşlemler")
    
    # 1. Yeni Sohbet Butonu
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = genai.GenerativeModel(MODEL_ISMI).start_chat(history=[])
        st.rerun()

    # 2. Sohbeti Kaydet Butonu (GERİ GELDİ!)
    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M:%S")
            # İlk mesajdan kısa bir özet alıp başlık yapıyoruz
            ozet = st.session_state.messages[0]["content"][:20] + "..." if len(st.session_state.messages) > 0 else "Sohbet"
            baslik = f"{tarih} | {ozet}"
            st.session_state.arsiv[baslik] = list(st.session_state.messages)
            st.success("Sohbet arşive eklendi abim!")
        else:
            st.warning("Kaydedecek bir şey yok abim.")

    st.divider()
    st.subheader("📁 Eski Kayıtlar")
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

# Mesajları Ekrana Dök
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FOTOĞRAF YÜKLEME ALANI (GİZLİ BÖLME) ---
# Mesaj çubuğunun hemen üzerinde küçük bir buton gibi durur
with st.popover("➕ Fotoğraf Ekle", help="Resim yüklemek için tıkla abim"):
    st.markdown("###### 📸 Fotoğraf Yükle")
    yuklenen_dosya = st.file_uploader("Resim seç", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if yuklenen_dosya:
        st.image(yuklenen_dosya, width=200, caption="Gönderilecek Resim")
        st.info("Resim seçildi, aşağıya sorunu yazabilirsin abim.")

# --- MESAJ GİRİŞ ÇUBUĞU ---
if prompt := st.chat_input("İstediğini yaz abim..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Cevap üretimi
    with st.chat_message("assistant"):
        try:
            if yuklenen_dosya:
                # Eğer kullanıcı gizli bölmeden resim seçtiyse
                img = Image.open(yuklenen_dosya)
                model_multi = genai.GenerativeModel(MODEL_ISMI)
                response = model_multi.generate_content([f"{kisilik}\nSoru: {prompt}", img])
            else:
                # Sadece metin varsa
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu abim: {e}")