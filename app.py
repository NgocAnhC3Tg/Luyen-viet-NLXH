import streamlit as st
import data_de_bai as db
from PIL import Image
import google.generativeai as genai
import json
import re

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN
# ==============================================================================
st.set_page_config(
    page_title="HỆ THỐNG LUYỆN VIẾT NLXH",
    page_icon="🖊️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }
    .hero-banner { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%); padding: 24px 30px; border-radius: 16px; color: white; box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.15); margin-bottom: 22px; }
    .hero-title { font-size: 1.8rem !important; font-weight: 800 !important; letter-spacing: -0.5px; margin-bottom: 4px !important; color: #ffffff !important; }
    .hero-subtitle { font-size: 0.92rem; color: #dbeafe; margin: 0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #ffffff; padding: 8px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] { height: 48px; border-radius: 10px; font-weight: 700; font-size: 0.92rem; color: #475569; padding: 0 16px; border: 1px solid #e2e8f0; background-color: #f8fafc; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important; color: #ffffff !important; border-color: #2563eb !important; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important; }
    .section-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 16px; }
    .evidence-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #16a34a; padding: 14px 18px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
</style>
""", unsafe_allow_html=True
)

# ==============================================================================
# 2. QUẢN LÝ SESSION STATE AN TOÀN
# ==============================================================================
if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng ở phần nào?")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""

def get_api_key():
    return st.session_state.get("gemini_api_key", "").strip()

# ==============================================================================
# 3. HỆ THỐNG GỌI AI AN TOÀN TUYỆT ĐỐI
# ==============================================================================
def call_ai(prompt, image=None):
    key = get_api_key()
    if not key:
        return "⚠️ Thầy/cô chưa nhập mã Gemini API Key ở thanh bên trái (Sidebar). Vui lòng nhập mã để sử dụng tính năng AI!"
    try:
        genai.configure(api_key=key)
        for m_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
            try:
                model = genai.GenerativeModel(m_name)
                contents = [prompt]
                if image: contents.append(image)
                res = model.generate_content(contents)
                if res and res.text: return res.text
            except Exception:
                continue
        return "⚠️ Không kết nối được với các mô hình AI. Vui lòng kiểm tra lại API Key."
    except Exception as e:
        return f"⚠️ Lỗi hệ thống AI: {str(e)}"

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    key_in = st.text_input("Nhập mã Gemini API Key:", type="password", value=st.session_state["gemini_api_key"])
    if key_in != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = key_in
    if key_in: st.success("✅ Đã lưu API Key!")
    else: st.warning("⚠️ Cần nhập API Key để kích hoạt Trợ lý và Chấm bài.")
    
    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM\n1. Chọn/Nhập đề & Xác định VĐNL\n2. Lập ý & Hỏi Trợ lý Ngữ văn\n3. Viết bài độc lập (Gõ/Ảnh)\n4. Kiểm tra theo Rubric 7 tiêu chí")

st.markdown("""<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div><p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT</p></div>""", unsafe_allow_html=True)

tabs = st.tabs(["🌱 BƯỚC 1: TÌM HIỂU ĐỀ", "🧵 BƯỚC 2: TÌM Ý & CHAT AI", "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI", "📊 BƯỚC 4: CHẤM BÀI (RUBRIC)"])

with tabs[0]:
    st.markdown('<div class="section-title">🔍 Bước 1: Lựa chọn đề bài & Xác định vấn đề nghị luận</div>', unsafe_allow_html=True)
    t_cb, t_nc, t_tu = st.tabs(["🟢 Đề Cơ Bản", "🔴 Đề Nâng Cao", "✏️ Đề Tự Nhập"])
    
    with t_cb:
        c1, c2 = st.columns([1, 2])
        sel_cb = c1.selectbox("Chọn đề Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="s_cb")
        c2.info(db.DE_BAI_CO_BAN[sel_cb]["text"])
        if c2.button("📌 Chọn đề Cơ bản này", type="primary"):
            st.session_state["selected_de_key"] = sel_cb
            st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[sel_cb]
            st.success(f"Đã chọn: {sel_cb}")

    with t_nc:
        c1, c2 = st.columns([1, 2])
        sel_nc = c1.selectbox("Chọn đề Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="s_nc")
        c2.info(db.DE_BAI_NANG_CAO[sel_nc]["text"])
        if c2.button("📌 Chọn đề Nâng cao này", type="primary"):
            st.session_state["selected_de_key"] = sel_nc
            st.session_state["current_de_info"] = db.DE_BAI_NANG_CAO[sel_nc]
            st.success(f"Đã chọn: {sel_nc}")

    with t_tu:
        custom_t = st.text_area("Nhập nội dung đề bài tự do:", height=100)
        custom_v = st.text_input("Vấn đề nghị luận chính là gì?")
        if st.button("🚀 Tạo khung định hướng tự động", type="primary"):
            if not custom_t.strip():
                st.warning("Vui lòng nhập nội dung đề bài!")
            else:
                prompt_gen = f"""Phân tích đề bài NLXH sau và trả về MỘT CHUỖI JSON HỢP LỆ (không markdown):
Đề: "{custom_t}"
Cấu trúc JSON:
{{
  "text": "{custom_t}",
  "vdnl_chuan": "{custom_v if custom_v else 'Vấn đề nghị luận'}",
  "explain_items": ["- Giải thích từ khóa trọng tâm...", "- Làm rõ thông điệp..."],
  "vdnl_ket_luan": "Ý nghĩa cốt lõi...",
  "questions": [{{"cau_hoi": "Ý nghĩa và biểu hiện?", "y_tra_loi": ["- Ý 1...", "- Ý 2..."]}}],
  "evidence": [{{"ten": "Nhân vật tiêu biểu", "chi_tiet": "Hành động", "y_nghia": "Ý nghĩa", "nguon": "Thực tế"}}],
  "counter": ["- Phê phán lối sống lệch lạc...", "- Lưu ý tránh cực đoan..."],
  "dani_chi_tiet": {{"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản đề", "kb": "Kết bài"}}
}}"""
                res = call_ai(prompt_gen)
                try:
                    match = re.search(r'\{.*\}', res, re.DOTALL)
                    if match:
                        data_json = json.loads(match.group(0))
                        st.session_state["selected_de_key"] = f"Đề tự nhập: {custom_t[:40]}..."
                        st.session_state["current_de_info"] = data_json
                        st.success("✅ Đã tạo khung định hướng thành công! Mời sang Bước 2.")
                except Exception:
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {custom_t[:40]}..."
                    st.session_state["current_de_info"] = {
                        "text": custom_t, "vdnl_chuan": custom_v or "Vấn đề nghị luận",
                        "explain_items": ["- Giải thích các khái niệm cốt lõi trong đề."],
                        "vdnl_ket_luan": "Giá trị thực tiễn.", "questions": [{"cau_hoi": "Ý nghĩa?", "y_tra_loi": ["- Phân tích biểu hiện."]}],
                        "evidence": [{"ten": "Tấm gương tiêu biểu", "chi_tiet": "Hành động", "y_nghia": "Ý nghĩa", "nguon": "Thực tế"}],
                        "counter": ["- Phê phán thái độ vô cảm."], "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản đề", "kb": "Kết bài"}
                    }
                    st.success("✅ Đã tạo khung định hướng!")

    st.markdown("---")
    st.info(f"📌 **Đề đang làm việc:** {st.session_state['selected_de_key']}\n\n*Nội dung:* {st.session_state['current_de_info'].get('text', '')}")

with tabs[1]:
    cur_info = st.session_state["current_de_info"]
    col1, col2 = st.columns([1.2, 0.8], gap="large")
    
    with col1:
        st.markdown("#### 🛠️ Khung định hướng tư duy")
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            for i in cur_info.get("explain_items", []): st.markdown(i)
        with st.expander("💡 Thao tác 2: Bàn luận (5 ý)", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                for ans in q.get("y_tra_loi", []): st.markdown(ans)
        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế", expanded=True):
            for ev in cur_info.get("evidence", []):
                if isinstance(ev, dict): st.markdown(f"**👤 {ev.get('ten', '')}**: {ev.get('chi_tiet', '')} -> *{ev.get('y_nghia', '')}*")
        with st.expander("🔄 Thao tác 4: Phản đề", expanded=True):
            for c in cur_info.get("counter", []): st.markdown(c)

    with col2:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn (Tư vấn phương pháp)")
        box = st.container(height=380, border=True)
        for role, msg in st.session_state["chat_history"]:
            box.markdown(f"**{'🧑‍🎓 Học sinh' if role=='user' else '👩‍🏫 Trợ lý'}:** {msg}")
            box.markdown("---")
        
        q_text = st.text_area("Hỏi Trợ lý (Tuyệt đối không viết hộ bài):", height=80, key="q_chat")
        b_send, b_clear = st.columns(2)
        if b_send.button("🚀 Gửi câu hỏi", type="primary", use_container_width=True):
            if q_text.strip():
                # Chặn xin viết hộ
                low_q = q_text.lower()
                if any(w in low_q for w in ["viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho bài văn", "đoạn văn mẫu"]):
                    reply = "👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết hộ hay viết thay bài văn cho em! Viết văn là rèn luyện tư duy chính mình. Em hãy tự nháp ý rồi cô sẽ góp ý nhé!"
                else:
                    prompt_chat = f"""Đóng vai giáo viên Ngữ văn THPT hướng dẫn học sinh viết NLXH.
Đề: "{cur_info.get('text', '')}"
Vấn đề: "{cur_info.get('vdnl_chuan', '')}"
Câu hỏi học sinh: "{q_text}"
Nguyên tắc: KHÔNG BAO GIỜ viết hộ. Hướng dẫn phương pháp, cung cấp ý hoặc dẫn chứng cụ thể. Ngắn gọn, tận tâm."""
                    reply = call_ai(prompt_chat)
                
                st.session_state["chat_history"].append(("user", q_text))
                st.session_state["chat_history"].append(("assistant", reply))
                st.rerun()
        if b_clear.button("🗑️ Xóa lịch sử", use_container_width=True):
            st.session_state["chat_history"] = [("assistant", "Chào em! Cô sẵn sàng hỗ trợ phương pháp lập ý và dẫn chứng.")]
            st.rerun()

with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    mode = st.radio("Chọn hình thức nộp bài:", ["✍️ Gõ bài trực tiếp", "📷 Tải ảnh chụp viết tay"], horizontal=True)
    
    if mode == "✍️ Gõ bài trực tiếp":
        essay = st.text_area("Khung soạn thảo bài làm của học sinh:", value=st.session_state.get("user_essay", ""), height=350)
        st.session_state["user_essay"] = essay
        if st.button("📊 Chấm Rubric Khắt Khe (Thang 10)", type="primary"):
            if not essay.strip(): st.warning("Vui lòng nhập bài viết!")
            else:
                with st.spinner("Đang chấm điểm khắt khe theo Rubric 7 tiêu chí..."):
                    prompt_grade = f"""Đóng vai giáo viên Ngữ văn THPT chấm bài cực kỳ khắt khe. Chấm bài NLXH sau theo Rubric 7 tiêu chí (Thang 10, bước nhảy 0.25/0.5/1.0).
BẮT BUỘC: Lập bảng Markdown gồm 4 cột (Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét & Trích dẫn câu văn lủng củng của HS để trừ điểm).
Đề: "{cur_info.get('text', '')}"
Bài làm:
{essay}
Cuối bảng ghi TỔNG ĐIỂM và LỜI PHÊ SẮC SÉN."""
                    st.session_state["rubric_evaluation"] = call_ai(prompt_grade)
                    st.success("✅ Đã chấm xong! Mời sang Bước 4 xem kết quả chi tiết.")
    else:
        img_file = st.file_uploader("Tải lên ảnh chụp bài viết tay:", type=["png", "jpg", "jpeg"])
        if img_file:
            pil_img = Image.open(img_file)
            st.image(pil_img, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric Khắt Khe", type="primary"):
                with st.spinner("AI đang đọc chữ viết tay và chấm điểm..."):
                    prompt_grade_img = f"""Đóng vai giáo viên Ngữ văn THPT chấm thi khắt khe. Hãy đọc chữ viết tay trong ảnh và chấm bài theo Rubric 7 tiêu chí (Thang 10).
Lập bảng Markdown gồm 4 cột: Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét & Trích dẫn lỗi.
Cuối bảng ghi TỔNG ĐIỂM và LỜI PHÊ."""
                    st.session_state["rubric_evaluation"] = call_ai(prompt_grade_img, image=pil_img)
                    st.success("✅ Đã chấm xong ảnh! Mời sang Bước 4 xem kết quả.")

with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra Theo Rubric (Chấm Thực Chất)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.3], gap="large")
    with c1:
        edit_es = st.text_area("Chỉnh sửa bài làm tại đây:", value=st.session_state.get("user_essay", ""), height=400)
        st.session_state["user_essay"] = edit_es
        if st.button("🔍 Nộp lại để chấm điểm", type="primary"):
            with st.spinner("Đang chấm lại..."):
                prompt_re = f"""Chấm lại bài NLXH sau theo Rubric 7 tiêu chí (Thang 10, khắt khe, trích dẫn lỗi trong bài):
{edit_es}"""
                st.session_state["rubric_evaluation"] = call_ai(prompt_re)
                st.success("✅ Đã cập nhật kết quả mới!")
    with c2:
        st.markdown("##### 📋 Bảng Điểm & Nhận Xét Chi Tiết:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info("💡 Chưa có bảng điểm. Hãy hoàn thành Bước 3 để chấm bài.")
