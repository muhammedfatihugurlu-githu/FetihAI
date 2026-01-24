import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io
import urllib.parse 
import random
from streamlit_mic_recorder import mic_recorder, speech_to_text

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    st.error("Abim Secrets kısmında anahtarı bulamadım!")
    st.stop()

st.set_page_config(page_title="FetihAI v0.6", page_icon="🇹🇷⚔️", layout="wide")

# --- MODEL AYARI ---
MODEL_ISMI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Senin yapımcın Muhammed Fatih Uğurlu'dur. Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy, birde tatlı bir sevgilisi var, ismi Zeynep Sude Oktay yani Zoktay, ikisi sevgililer, bak bunu kimse sormadıkça söyleme. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kaynat. Her cevap başında 'vay, hoşgeldin, ooo' kelimelerini kullanma."

# --- 🛠️ ÇİZİM MOTORU (EN SADE HALİ) ---
def resim_ciz_hizli(prompt_tr):
    try:
        # Karmaşık çeviri yerine basit bir yapı
        encoded_prompt = urllib.parse.quote(prompt_tr)
        # En stabil link yapısı
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except:
        return None
    return None

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
st.title("🇹🇷⚔️ FetihAI v0.6")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı")

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ARAÇLAR PANELİ ---
st.write("---")
col_cizim, col_foto = st.columns(2)

with col_cizim:
    with st.expander("🎨 Resim Çizdir", expanded=False):
        hayal = st.text_input("Ne çizeyim abim?", key="simple_draw")
        if st.button("Çiz Gelsin", use_container_width=True):
            if hayal:
                with st.spinner("Çiziyorum abim..."):
                    img_bytes = resim_ciz_hizli(hayal)
                    if img_bytes:
                        st.image(img_bytes, caption="Hakkını helal et, elimden bu geldi!")
                    else:
                        st.error("Bağlantı zayıf, tekrar bas abim.")

with col_foto:
    with st.expander("📸 Fotoğraf Gönder", expanded=False):
        yuklenen_dosya = st.file_uploader("Resim Yükle", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        if yuklenen_dosya:
            st.image(yuklenen_dosya, width=200)

# --- 🎤 SESLİ GİRİŞ (Yukarıda, Araçlar Panelinde Dursun) ---
with col_cizim: # Veya uygun gördüğün bir sütun
    st.write("🎙️ **Sesli Komut:**")
    ses_metni = speech_to_text(
        language='tr', 
        start_prompt="🎤 Konuş", 
        stop_prompt="🛑 Durdur", 
        just_once=True, # Konuşma bitince sussun
        key='sesli_fetih'
    )

# --- 🎤 SESLİ GİRİŞ (Yukarıda Araçlarda Tanımladıysan Burayı Atla) ---
# Not: Eğer yukarıda col_cizim içinde ses_metni'ni tanımladıysan, 
# buradaki if kontrolü onu otomatik yakalayacak.

# --- ⌨️ TEK VE YEGANE MESAJ ÇUBUĞU ---
yazi_metni = st.chat_input("İstediğini yaz abim...")

# --- 🧠 GİRİŞ KONTROLÜ (SES Mİ YAZI MI?) ---
final_prompt = None

# Önce ses gelmiş mi diye bakıyoruz (Yukarıdaki ses_metni değişkeni)
if 'ses_metni' in locals() and ses_metni:
    final_prompt = ses_metni
# Ses yoksa yazıya bakıyoruz
elif yazi_metni:
    final_prompt = yazi_metni

# --- 🚀 İŞLEME BAŞLAMA ---
if final_prompt:
    # 1. Kullanıcı mesajını ekrana bas ve hafızaya ekle
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # 2. Gemini'den cevap al
    with st.chat_message("assistant"):
        try:
            # Fotoğraf kontrolü (yuklenen_dosya değişkeni yukarıdaki expander'dan gelmeli)
            if 'yuklenen_dosya' in locals() and yuklenen_dosya:
                img = Image.open(yuklenen_dosya)
                model_multi = genai.GenerativeModel(MODEL_ISMI)
                response = model_multi.generate_content([f"{kisilik}\nSoru: {final_prompt}", img])
            else:
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {final_prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu abim: {e}")