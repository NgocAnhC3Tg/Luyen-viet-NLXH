import json
import re
import google.generativeai as genai
import streamlit as st
import data_de_bai as db
from PIL import Image

st.set_page_config(page_title="Hệ Thống Luyện Viết NLXH", page_icon="🖊️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }
    .hero-banner { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%); padding: 24px 30px; border-radius: 16px; color: white; margin-bottom: 22px; }
    .hero-title { font-size: 2.0rem !important; font-weight: 800 !important; color: #ffffff !important; }
    .section-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 16px; }
    .evidence-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #16a34a; padding: 16px 20px; border-radius: 10px; margin-bottom: 14px; }
    .explain-box-clean { background-color: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; padding: 18px 22px; border-radius: 10px; line-height: 1.75; color: #1e293b; }
    .counter-box { background-color: #fef2f2; border: 1px solid #fecaca; border-left: 5px solid #dc2626; padding: 16px 20px; border-radius: 10px; color: #7f1d1d; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em có thắc mắc gì về phương pháp lập dàn ý hay chọn dẫn chứng cứ hỏi cô nhé!")
    ]

with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input("Gemini API Key:", type="password", value=st.session_state["gemini_api_key"])
    if api_key_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = api_key_input.strip()

    if st.session_state["gemini_api_key"]:
        st.success("✅ Trợ lí Ngữ văn đã sẵn sàng")
    else:
        st.warning("⚠️ Vui lòng nhập API Key để kích hoạt AI.")

    st.markdown("---")
    st.markdown("### 📌 4 BƯỚC SƯ PHẠM")
    st.write("1. **🌱 Bước 1:** Phân tích đề & VĐNL")
    st.write("2. **🧵 Bước 2:** Lập dàn ý & Kho dẫn chứng")
    st.write("3. **✍️ Bước 3:** Xưởng viết bài")
    st.write("4. **📁 Bước 4:** Hồ sơ bài làm")

def call_gemini_engine(prompt_text, image_obj=None):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "❌ Bạn chưa nhập Gemini API Key ở thanh bên trái!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        if image_obj:
            response = model.generate_content([prompt_text, image_obj])
        else:
            response = model.generate_content(prompt_text)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return "⚠️ AI đã tiếp nhận nhưng không trả về nội dung."
    except Exception as e:
        return f"❌ Lỗi kết nối AI: {str(e)}"

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giám khảo Ngữ văn THPT.
- Đề bài: "{exam_text}"
- VĐNL chuẩn: "{vdnl_chuan}"
- Câu trả lời HS: "{student_guess}"
Xuất ra JSON duy nhất:
{{"status": "DUNG" | "LECH" | "SAI", "feedback": "Nhận xét sư phạm xưng cô em", "suggested_fix": "{vdnl_chuan}"}}
"""
    raw = call_gemini_engine(prompt)
    try:
        clean_raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(clean_raw)
    except Exception:
        return {"status": "LECH", "feedback": "Câu trả lời chưa hoàn toàn sát trọng tâm.", "suggested_fix": vdnl_chuan}

st.markdown('<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG 50 ĐỀ NGHỊ LUẬN XÃ HỘI THPT</div></div>', unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "📁 HỒ SƠ BÀI LÀM",
])

with tabs[0]:
    st.markdown('<div class="section-title">🔍 Lựa chọn đề bài & Xác định vấn đề nghị luận</div>', unsafe_allow_html=True)
    tab_cb, tab_nc, tab_tn = st.tabs(["🟢 Cơ Bản (01–25)", "🔴 Nâng Cao (26–50)", "✏️ Nhập Đề Riêng"])

    with tab_cb:
        c1, c2 = st.columns([1, 2], gap="medium")
        with c1:
            sel_cb = st.selectbox("Chọn đề Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="sb_cb")
            info_cb = db.DE_BAI_CO_BAN[sel_cb]
        with c2:
            with st.container(border=True):
                st.info(info_cb["text"])
            if st.button("📌 Chọn đề này & Chuyển sang Bước 2", key="btn_cb", type="primary"):
                st.session_state["selected_de_key"] = sel_cb
                st.session_state["current_de_info"] = info_cb
                st.session_state["eval_vdnl_result"] = None
                st.success(f"Đã chọn: {sel_cb}!")

    with tab_nc:
        c1, c2 = st.columns([1, 2], gap="medium")
        with c1:
            sel_nc = st.selectbox("Chọn đề Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="sb_nc")
            info_nc = db.DE_BAI_NANG_CAO[sel_nc]
        with c2:
            with st.container(border=True):
                st.info(info_nc["text"])
            if st.button("📌 Chọn đề này & Chuyển sang Bước 2", key="btn_nc", type="primary"):
                st.session_state["selected_de_key"] = sel_nc
                st.session_state["current_de_info"] = info_nc
                st.session_state["eval_vdnl_result"] = None
                st.success(f"Đã chọn: {sel_nc}!")

    with tab_tn:
        custom_txt = st.text_area("Nội dung đề bài tự chọn:", placeholder="Viết bài văn nghị luận bàn về...")
        if st.button("🔍 Tạo giàn giáo Bước 2", type="primary"):
            if custom_txt.strip():
                st.session_state["selected_de_key"] = "Đề tự nhập"
                st.session_state["current_de_info"] = {
                    "text": custom_txt, "vdnl_chuan": "Vấn đề tự chọn",
                    "explain_guide": "Giải thích từ khóa trọng tâm.", "explain_items": ["1. Cắt nghĩa khái niệm."],
                    "vdnl_ket_luan": "Chốt vấn đề.", "questions": [{"cau_hoi": "Ý nghĩa?", "y_tra_loi": ["Giá trị tích cực"]}],
                    "evidence": [{"ten": "Dẫn chứng thực tế", "chi_tiet": "Sự kiện tiêu biểu", "y_nghia": "Ý nghĩa", "nguon": "Báo chí"}],
                    "counter": ["Phản biện mặt trái."], "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản biện", "kb": "Kết bài"}
                }
                st.success("Đã tạo xong giàn giáo!")

    st.markdown("---")
    cur_key = st.session_state["selected_de_key"]
    cur_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề đang chọn:** {cur_key}")

    student_vdnl = st.text_input("⚡ Xác định vấn đề nghị luận:", placeholder="Gõ câu trả lời...")
    if st.button("🔍 Đối chiếu với AI", type="primary"):
        if student_vdnl.strip():
            with st.spinner("AI đang thẩm định..."):
                st.session_state["eval_vdnl_result"] = ai_evaluate_student_vdnl(cur_info["text"], cur_info["vdnl_chuan"], student_vdnl)

    if st.session_state.get("eval_vdnl_result"):
        res = st.session_state["eval_vdnl_result"]
        if res.get("status") == "DUNG":
            st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}")
        else:
            st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:* {res.get('suggested_fix')}")

with tabs[1]:
    cur_key = st.session_state["selected_de_key"]
    cur_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.1, 0.9], gap="large")

    with c_left:
        st.markdown(f"#### 🛠️ Gợi ý khung tư duy cho: <span style='color:#2563eb;'>{cur_key}</span>", unsafe_allow_html=True)
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            items_html = "".join([f"<p>• {i}</p>" for i in cur_info.get("explain_items", [])])
            st.markdown(f"<div class='explain-box-clean'>{items_html}</div>", unsafe_allow_html=True)

        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi')}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        with st.expander("📚 Thao tác 3: Kho dẫn chứng trọng tâm & 9 chủ điểm", expanded=True):
            for ev in cur_info.get("evidence", []):
                st.markdown(f"<div class='evidence-card'><b>{ev.get('ten')}</b>: {ev.get('chi_tiet')}</div>", unsafe_allow_html=True)
            
            sel_top = st.selectbox("Chọn chủ điểm dẫn chứng mở rộng:", options=list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()))
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[sel_top]:
                with st.container(border=True):
                    st.markdown(f"**{dc['ten']}**: {dc['noi_dung']}")

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        
        # Khung hiển thị lịch sử trò chuyện ổn định tuyệt đối
        chat_container = st.container(height=350)
        with chat_container:
            for role, text in st.session_state["chat_history"]:
                if role == "user":
                    st.markdown(f"**👤 Học sinh:** {text}")
                else:
                    st.markdown(f"🤖 **Trợ lý Ngữ văn:** {text}")
                st.markdown("---")

        # Sử dụng text_input + button truyền thống thay cho chat_input để tránh bị treo
        with st.form(key="chat_form", clear_on_submit=True):
            user_question = st.text_input("Nhập câu hỏi cho Trợ lý Ngữ văn:", placeholder="Ví dụ: Gợi ý thêm cho em phần bàn luận...")
            submit_btn = st.form_submit_button("Gửi câu hỏi 🚀", type="primary")
            
            if submit_btn and user_question.strip():
                st.session_state["chat_history"].append(("user", user_question))
                prompt_chat = f"Bạn là GV Ngữ văn THPT sư phạm (xưng cô-em), không làm hộ bài. Đề: {cur_key}. HS hỏi: {user_question}. Hãy gợi mở."
                with st.spinner("Trợ lý Ngữ văn đang suy nghĩ..."):
                    bot_reply = call_gemini_engine(prompt_chat)
                st.session_state["chat_history"].append(("assistant", bot_reply))
                st.rerun()

with tabs[2]:
    st.markdown('<div class="section-title">✍️ Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    write_mode = st.radio("Chọn hình thức nộp bài:", ["✍️ Tự gõ bài viết trực tiếp", "📷 Gửi ảnh chụp bài viết tay"], horizontal=True)

    if write_mode == "✍️ Tự gõ bài viết trực tiếp":
        st.session_state["user_essay"] = st.text_area("Nhập bài viết:", value=st.session_state.get("user_essay", ""), height=380)
    else:
        up_img = st.file_uploader("Tải lên ảnh chụp bài viết tay:", type=["png", "jpg", "jpeg"])
        if up_img:
            img = Image.open(up_img)
            st.image(img, caption="Ảnh bài làm", use_column_width=True)
            if st.button("🔍 Nhờ AI nhận xét bài viết tay", type="primary"):
                with st.spinner("AI đang phân tích ảnh..."):
                    feedback = call_gemini_engine(f"Nhận xét bài làm cho đề: {cur_key}", image_obj=img)
                    st.success(feedback)

with tabs[3]:
    st.markdown('<div class="section-title">📁 Hồ Sơ Bài Làm & Xuất File</div>', unsafe_allow_html=True)
    if st.session_state.get("user_essay"):
        st.text_area("Nội dung bài làm:", value=st.session_state["user_essay"], height=250, disabled=True)
