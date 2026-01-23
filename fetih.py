import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests
import io
import urllib.parse
import random  # YENİ: Rastgelelik için gerekli kütüphane

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    st.error("Abim Secrets kısmında anahtarı bulamadım!")
    st.stop()

st.set_page_config(page_title="FetihAI v4.6", page_icon="🇹🇷⚔️", layout="wide")

# --- MODEL AYARI (Kota Dostu 1.5 Sürümü) ---
MODEL_ISMI = 'gemini-1.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Senin yapımcın Muhammed Fatih Uğurlu'dur. Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kaynat. Her cevap başında 'vay, hoşgeldin, ooo' kelimelerini kullanma."

# --- 🛠️ HIZLI ÇİZİM FONKSİYONU (DÜZELTİLDİ) ---
def resim_ciz_hizli(prompt_tr):
    try:
        # Gemini ile promptu zenginleştir
        model_cevir = genai.GenerativeModel(MODEL_ISMI)
        try:
            cevap = model_cevir.generate_content(f"Sadece İngilizceye çevir ve detaylandır (cool image prompt): {prompt_tr}")
            prompt_en = cevap.text if cevap.text else prompt_tr
        except:
            prompt_en = prompt_tr

        encoded_prompt = urllib.parse.quote(prompt_en)
        
        # --- DÜZELTME BURADA ---
        # Sadece zamanı değil, büyük rastgele bir sayı kullanıyoruz ki
        # sistem asla aynı resmi hafızadan getirmesin.
        random_seed = random.randint(1, 999999999) 
        # Ekstra güvenlik: Linkin sonuna rastgele bir parametre daha ekliyoruz (cache-busting)
        cache_buster = random.randint(1, 10000)
        
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random_seed}&model=flux&cb={cache_buster}"
        
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
st.title("🇹🇷⚔️ FetihAI v4.6")
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
        hayal = st.text_input("Ne hayal ediyorsun abim?", key="hayal_input")
        if st.button("Hemen Çiz", use_container_width=True):
            if hayal:
                # Her çizimde spinner'ı farklı gösterelim ki takılmadığı anlaşılsın
                with st.spinner(f"FetihAI fırçayı kaptı, çiziyor... (İşlem No: {random.randint(100,999)})"):
                    img_bytes = resim_ciz_hizli(hayal)
                    if img_bytes:
                        # Resmi gösterirken de rastgele bir key atıyoruz
                        st.image(Image.open(io.BytesIO(img_bytes)), caption="Buyur abim!", key=f"img_{random.randint(1,99999)}")
                    else:
                        st.error("Sunucu anlık bir takılma yaşadı, tekrar bas abim.")

with col_foto:
    with st.expander("📸 Fotoğraf Ekle (Analiz)", expanded=False):
        st.caption("Kamera veya Galeri'den fotoğraf seç abim:")
        yuklenen_dosya = st.file_uploader(
            "Resim Yükle", 
            type=['png', 'jpg', 'jpeg'], 
            label_visibility="collapsed"
        )
        if yuklenen_dosya:
            st.image(yuklenen_dosya, width=200, caption="Bu resim analiz edilecek")

# --- MESAJ ÇUBUĞU ---
if prompt := st.chat_input("İstediğini yaz abim..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model_multi = genai.GenerativeModel(MODEL_ISMI)
            if yuklenen_dosya:
                img = Image.open(yuklenen_dosya)
                response = model_multi.generate_content([f"{kisilik}\nResmi yorumla. Soru: {prompt}", img])
            else:
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bir hata oldu abim: {e}")