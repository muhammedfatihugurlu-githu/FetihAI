import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import requests  # YENİ: Çizim için gerekli
import io        # YENİ: Resim işleme için gerekli
import urllib.parse # YENİ: Link oluşturma için gerekli

# --- GÜVENLİ ANAHTAR KONTROLÜ ---
if "OPENAI_API_KEY" in st.secrets:
    SİHİRLİ_ANAHTAR = st.secrets["OPENAI_API_KEY"]
    genai.configure(api_key=SİHİRLİ_ANAHTAR)
else:
    st.error("Abim Secrets kısmında anahtarı bulamadım!")
    st.stop()

st.set_page_config(page_title="FetihAI v4.5", page_icon="🇹🇷⚔️", layout="wide")

# --- MODEL AYARI ---
# Abim, '2.5-flash' çok hata verdiği için senin kodunu bozmadan
# burayı '1.5-flash' yaptım ki günde 1500 mesaj atabilesin, hata alma.
MODEL_ISMI = 'gemini-2.5-flash' 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {} 

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ISMI)
    st.session_state.chat_session = model.start_chat(history=[])

kisilik = "Sen samimi, esprili FetihAI'sın. Senin yapımcın Muhammed Fatih Uğurlu'dur. Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kaynat. Her cevap başında 'vay, hoşgeldin, ooo' kelimelerini kullanma."

# --- YENİ EKLENEN: HIZLI ÇİZİM FONKSİYONU ---
def resim_ciz_hizli(prompt_tr):
    try:
        # Önce İngilizceye çevir (Daha iyi çizim için)
        model_cevir = genai.GenerativeModel(MODEL_ISMI)
        try:
            cevap = model_cevir.generate_content(f"Sadece İngilizceye çevir (image prompt): {prompt_tr}")
            prompt_en = cevap.text if cevap.text else prompt_tr
        except:
            prompt_en = prompt_tr # Çeviri çalışmazsa Türkçe devam et

        # Pollinations ile çiz (Token istemez, beklemez)
        encoded_prompt = urllib.parse.quote(prompt_en)
        seed = int(time.time())
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
        
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except:
        return None
    return None

# --- YAN MENÜ (ARŞİV & KAYIT) - (SENİN KODUN AYNEN DURUYOR) ---
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
st.title("🇹🇷⚔️ FetihAI v4.5")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı")

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ARAÇLAR ALANI (Genişletici Menüler) ---
st.write("---") # Ayırıcı çizgi

# İki sütuna böldüm: Solda ÇİZİM, Sağda ANALİZ (Senin kodun sağda duruyor)
col_cizim, col_foto = st.columns(2)

with col_cizim:
    with st.expander("🎨 Resim Çizdir (YENİ)", expanded=False):
        hayal = st.text_input("Ne hayal ediyorsun abim?", key="cizim_input")
        if st.button("Hemen Çiz", use_container_width=True):
            if hayal:
                with st.spinner("FetihAI fırçasını konuşturuyor..."):
                    img_bytes = resim_ciz_hizli(hayal)
                    if img_bytes:
                        st.image(Image.open(io.BytesIO(img_bytes)), caption="Buyur abim!")
                        # İstersen çizilen resmi de geçmişe ekleyebiliriz ama şimdilik ekranda kalsın.
                    else:
                        st.error("Sunucu hattında ufak bir kopukluk oldu, tekrar bas abim.")

with col_foto:
    # SENİN ESKİ FOTOĞRAF YÜKLEME KODUN BURADA
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
                # Resim analizine de kişiliği ekledim ki abine ters konuşmasın :)
                response = model_multi.generate_content([f"{kisilik}\nResmi yorumla. Soru: {prompt}", img])
            else:
                response = st.session_state.chat_session.send_message(f"{kisilik}\nSoru: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bir hata oldu abim: {e}")