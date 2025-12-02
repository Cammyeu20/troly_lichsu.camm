import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components
import requests

# ======================
# ⚙️ CẤU HÌNH TRANG
# ======================
st.set_page_config(page_title="Trợ lý Lịch sử", layout="centered")

# ======================
# 🧠 KHỞI TẠO TRẠNG THÁI
# ======================
if "audio_unlocked" not in st.session_state:
    st.session_state["audio_unlocked"] = False

st.title("📚 TRỢ LÝ LỊCH SỬ")
st.write("👉 Bấm *BẬT ÂM THANH* (chỉ 1 lần), sau đó nhập câu hỏi rồi bấm *Trả lời*.")
st.write("📱 Trên hệ điều hành IOS, bạn cần bấm nút ▶ để nghe giọng nói (quy định của Safari).")
st.write("📱 Trên hệ điều hành android,máy tính bảng,laptop,máy tính bàn không cần bấm nút ▶ để nghe vì nó tự nói .")
# ======================
# 🔓 NÚT BẬT ÂM THANH
# ======================
if st.button("🔊 BẬT ÂM THANH (1 lần)"):
    js = """
    <script>
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            if (ctx.state === 'suspended') ctx.resume();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            gain.gain.value = 0;
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.05);
        } catch(e) {}
    </script>
    """
    components.html(js, height=0)
    st.session_state["audio_unlocked"] = True
    st.success("Âm thanh đã mở khoá!")

# ======================
# 📜 Tích hợp AI
# ======================
def tra_loi_lich_su(cau_hoi: str):
    if not cau_hoi:
        return "Vui lòng nhập câu hỏi."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": (
                    "Bạn là một trợ lý lịch sử Việt Nam. "
                    "Hãy trả lời chính xác, rõ ràng và dễ hiểu.\n\n"
                    f"Câu hỏi: {cau_hoi}"
                ),
                "stream": False
            }
        )

        data = response.json()
        return data.get("response", "Không nhận được phản hồi từ AI.")

    except Exception as e:
        return f"Lỗi khi kết nối AI: {e}"
# ======================
# 💬 GIAO DIỆN
# ======================
cau_hoi = st.text_input("❓ Nhập câu hỏi lịch sử:")

if st.button("📖 Trả lời"):
    tra_loi = tra_loi_lich_su(cau_hoi)
    st.success(tra_loi)

    # Tạo giọng nói
    try:
        mp3_fp = BytesIO()
        gTTS(text=tra_loi, lang="vi").write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode()

    except Exception as e:
        st.error("Lỗi tạo giọng nói.")
        audio_b64 = None

    # Phát âm thanh
    if audio_b64:
        unlocked = "true" if st.session_state["audio_unlocked"] else "false"

        audio_html = f"""
        <div id="tts"></div>
        <script>
          (function(){{
            const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
            const unlocked = {unlocked};
            const audio = document.createElement('audio');
            audio.src = "data:audio/mp3;base64,{audio_b64}";
            audio.controls = true;
            audio.playsInline = true;
            document.getElementById("tts").appendChild(audio);

            if (!isIOS && unlocked) {{
                audio.autoplay = true;
                audio.play().catch(()=>{{}});
            }}
        }})();
    </script>
    """

        components.html(audio_html, height=120)

        if st.session_state["audio_unlocked"]:
            st.info("🔊 Tự động phát (Android/PC).")
        else:
            st.warning("⚠️ iPhone phải bấm ▶.")

