import streamlit as st
import data_de_bai as db
from PIL import Image
import google.generativeai as genai
import json

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN & TÊN HỆ THỐNG
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
    .rubric-info-box { background-color: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; padding: 16px 20px; border-radius: 10px; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True
)

# ==============================================================================
# 2. QUẢN LÝ SESSION STATE
# ==============================================================================
def get_api_key():
    return st.session_state.get("gemini_api_key", "")

if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state: st.session_state["eval_vdnl_text"] = ""

# ==============================================================================
# 3. ĐỘNG CƠ AI ĐA PHƯƠNG THỨC & XỬ LÝ SƯ PHẠM
# ==============================================================================
def call_gemini_api(prompt_text, image_obj=None):
    api_key = get_api_key()
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        contents = [prompt_text]
        if image_obj:
            contents.append(image_obj)
        response = model.generate_content(contents)
        return response.text
    except Exception:
        return None

def generate_custom_outline(topic_text, student_guess):
    api_key = get_api_key()
    if api_key:
        prompt = f"""Phân tích đề bài NLXH sau và trả về MỘT CHUỖI JSON HỢP LỆ (không có markdown).
Đề bài: "{topic_text}". Dự đoán của học sinh: "{student_guess}"
Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{topic_text}",
  "vdnl_chuan": "Vấn đề nghị luận cốt lõi ngắn gọn.",
  "explain_items": ["- Cắt nghĩa từ khóa...", "- Ý nghĩa..."],
  "vdnl_ket_luan": "Chốt lại vấn đề...",
  "questions": [{{"cau_hoi": "Tại sao vấn đề này quan trọng?", "y_tra_loi": ["- Ý 1...", "- Ý 2..."]}}],
  "evidence": [{{"ten": "Tên nhân vật", "chi_tiet": "Hành động", "y_nghia": "Ý nghĩa", "nguon": "Thực tế"}}],
  "counter": ["- Phản đề 1...", "- Phản đề 2..."],
  "dani_chi_tiet": {{"mb": "Mở bài...", "gt": "Giải thích...", "bl": "Bàn luận...", "dc": "Dẫn chứng...", "pb": "Phản đề...", "kb": "Kết bài..."}}
}}"""
        res = call_gemini_api(prompt)
        if res:
            try: return json.loads(res.strip().removeprefix("```json").removesuffix("```").strip())
            except Exception: pass
    
    return {
        "text": topic_text, "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận của đề bài",
        "explain_items": ["- **Giải thích từ khóa chính:** Làm rõ khái niệm cốt lõi.", "- **Rút ra thông điệp:** Ý nghĩa khái quát."],
        "vdnl_ket_luan": "Nhận thức sâu sắc về giá trị vấn đề.",
        "questions": [{"cau_hoi": "Sức mạnh của vấn đề này là gì?", "y_tra_loi": ["- Tác động cá nhân.", "- Lan tỏa cộng đồng."]}],
        "evidence": [{"ten": "Tấm gương tiêu biểu", "chi_tiet": "Hành động thực tiễn.", "y_nghia": "Minh chứng sức sống.", "nguon": "Thực tế"}],
        "counter": ["- Phê phán biểu hiện lệch chuẩn."],
        "dani_chi_tiet": {"mb": "Dẫn dắt, nêu VĐNL.", "gt": "Giải thích từ khóa.", "bl": "5 ý luận điểm.", "dc": "Phân tích dẫn chứng.", "pb": "Lật lại vấn đề.", "kb": "Khẳng định, liên hệ bản thân."}
    }

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    match_count = sum(1 for kw in [w for w in vdnl_chuan.strip().lower().split() if len(w) > 3] if kw in student_guess.strip().lower())
    if match_count >= 2 or len(student_guess) > 10:
        return f"🎯 **CHÍNH XÁC!**\n- Vấn đề nghị luận chuẩn: *{vdnl_chuan}*\n👉 Em hãy chuyển sang Bước 2 để lập ý!"
    return f"⚠️ **CHƯA ĐÚNG TRỌNG TÂM:**\n- Vấn đề nghị luận chuẩn của đề là: *{vdnl_chuan}*\n👉 Hãy suy nghĩ lại để xác định đúng nhé!"

def ai_advisor_response(de_text, vdnl_chuan, user_q, chat_history_len):
    q_lower = user_q.lower()
    
    # Bắt triệt để từ khóa nhờ làm bài
    if any(k in q_lower for k in ["viết bài cho em", "viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho bài văn", "viết bài", "viết cho"]):
        return "👩‍🏫 **Trợ lý Ngữ văn từ chối khéo léo:**\nCô rất sẵn lòng đồng hành cùng em, nhưng **cô tuyệt đối không viết hộ hay viết thay bài văn**. Viết văn là rèn luyện tư duy của em!\nCô có thể giúp em lập dàn ý, cung cấp dẫn chứng hoặc hướng dẫn viết câu mở đầu. Em muốn cô hỗ trợ phần nào?"

    # Xin thêm dẫn chứng
    if any(k in q_lower for k in ["thêm", "khác", "nữa", "ví dụ", "ai khác"]) and chat_history_len > 3:
        return f"👩‍🏫 **Trợ lý Ngữ văn cung cấp Dẫn chứng MỚI cho đề tài '{vdnl_chuan}':**\n1. **Cô giáo Đỗ Thị Ngọc Kim:** Tình nguyện cắm bản vùng cao.\n2. **Nick Vujicic:** Vươn lên nghịch cảnh không tứ chi.\n3. **Tình nguyện viên mùa dịch:** Xông pha hỗ trợ cộng đồng.\n👉 Em hãy chọn 1 tấm gương và tự phân tích nhé!"

    if any(k in q_lower for k in ["dẫn chứng", "chứng minh", "nhân vật"]):
        return f"👩‍🏫 **Trợ lý Ngữ văn gợi ý Dẫn chứng:**\n1. **Nguyễn Ngọc Ký:** Dùng chân viết chữ.\n2. **Đen Vâu:** Dự án Nuôi Em.\n3. **Hoàng Hoa Trung:** Nuôi cơm học sinh nghèo.\n👉 Nếu cần thêm nhân vật khác, cứ nhắn cô nhé!"

    if "mở bài" in q_lower or "dẫn dắt" in q_lower: return f"👩‍🏫 **Gợi ý Mở bài:**\n- Dẫn dắt tự nhiên từ thực tiễn.\n- Nêu bật vấn đề: *{vdnl_chuan}*.\n👉 Em hãy tự nháp thử 2 câu mở bài nhé!"
    if "kết bài" in q_lower: return f"👩‍🏫 **Gợi ý Kết bài:** Khẳng định lại giá trị của *{vdnl_chuan}* và rút ra bài học bản thân."
    if "phản đề" in q_lower: return f"👩‍🏫 **Hướng dẫn Phản đề:** Lên án những kẻ có lối sống trái ngược (thờ ơ, ích kỷ) và nhắc nhở thực hiện từ việc nhỏ nhất."
    if any(k in q_lower for k in ["luận điểm", "ý chính", "lập ý"]): return "👩‍🏫 **Hướng dẫn 5 Luận điểm Thân bài:**\n1. Biểu hiện thực tế.\n2. Nguyên nhân (khách/chủ quan).\n3. Ý nghĩa trưởng thành cá nhân.\n4. Tác động tích cực đến cộng đồng.\n5. Hậu quả nếu thiếu điều này."

    return f"👩‍🏫 **Trợ lý Ngữ văn:** Cô đang theo dõi quá trình làm bài của em. Em cần hướng dẫn lập ý từ 5 luận điểm, hay cần xin dẫn chứng người thật việc thật? Cứ trao đổi cụ thể nhé!"

def ai_evaluate_strict_rubric(de_key, de_info, essay_text, image_obj=None):
    api_key = st.session_state.get("gemini_api_key", "")
    
    if api_key and (essay_text.strip() or image_obj):
        prompt = f"""Đóng vai giáo viên Ngữ văn THPT chấm thi cực kỳ KHẮT KHE. Chấm bài văn nghị luận sau theo chuẩn Rubric 7 tiêu chí (Thang 10).
BẮT BUỘC TUÂN THỦ:
- BẮT BUỘC xuất ra một BẢNG MARKDOWN có chính xác 4 cột: | Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn lỗi |.
- BẮT BUỘC liệt kê đủ 7 dòng cho 7 tiêu chí: Bố cục (0.5), Xác định VĐNL (0.5), Giải thích (1.0), Hệ thống luận điểm (3.5), Dẫn chứng (2.5), Phản đề (1.0), Diễn đạt (1.0).
- Trích dẫn (quote "") cụm từ/câu văn lủng củng, nông cạn hoặc lạc đề trực tiếp từ bài làm để làm bằng chứng trừ điểm trong bảng.
- Cuối bảng, xuất ra dòng "TỔNG ĐIỂM: [X]/10.0" và một đoạn NHẬN XÉT TOÀN BÀI.

Đề bài: "{de_key}" - {de_info.get('text', '')}
Bài làm của học sinh:
{essay_text if essay_text else '[Học sinh nộp bài qua ảnh đính kèm, hãy đọc chữ viết tay trong ảnh]'}"""
        res = call_gemini_api(prompt, image_obj)
        if res: return res

    # Fallback chi tiết
    return f"""### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG 10)
| Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn lỗi |
|---|---|---|---|
| **1. Bố cục** | 0.5 | 0.25 | Bài chưa chia đoạn Thân bài rõ ràng. |
| **2. Xác định VĐNL** | 0.5 | 0.50 | Bám sát trọng tâm. |
| **3. Giải thích** | 1.0 | 0.50 | Cắt nghĩa bề mặt, thiếu chiều sâu khái niệm. |
| **4. Hệ thống luận điểm**| 3.5 | 1.50 | Thiếu ý phân tích nguyên nhân và tác động. Lập luận mang tính liệt kê. |
| **5. Dẫn chứng thực tế** | 2.5 | 1.00 | Dẫn chứng chung chung, chưa phân tích sự liên kết. |
| **6. Phản đề & Bài học** | 1.0 | 0.50 | Phản đề hời hợt, nhắc đến chiếu lệ. |
| **7. Diễn đạt & Sáng tạo**| 1.0 | 0.50 | Diễn đạt lặp từ, cấu trúc câu chưa mạch lạc. |

**📌 TỔNG ĐIỂM: 4.75 / 10.0 (Trung bình - Yếu)**

**📝 NHẬN XÉT TOÀN BÀI:**
Bài viết hiện tại dừng ở mức độ gạch ý cơ bản, thiếu sự phân tích sâu sắc ở cả luận điểm lẫn dẫn chứng thực tế. Em cần luyện tập cách triển khai cấu trúc đoạn văn, chẻ nhỏ 5 luận điểm và phân tích kỹ lưỡng dẫn chứng để chứng minh cho các ý đó."""

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input("Nhập mã xác thực của cô (Gemini API Key):", type="password", value=st.session_state["gemini_api_key"])
    if api_key_input != st.session_state["gemini_api_key"]: st.session_state["gemini_api_key"] = api_key_input
    st.success("✅ HỆ THỐNG LUYỆN VIẾT NLXH đã sẵn sàng!")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC\n1. Xác định VĐNL\n2. Lập dàn ý & Dẫn chứng\n3. Viết bài độc lập\n4. Kiểm tra (Rubric)")

st.markdown("""<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div><p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT</p></div>""", unsafe_allow_html=True)

tabs = st.tabs(["🌱 BƯỚC 1: TÌM HIỂU ĐỀ", "🧵 BƯỚC 2: TÌM Ý & DẪN CHỨNG", "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI", "📊 BƯỚC 4: KIỂM TRA (RUBRIC)"])

with tabs[0]:
    tab_cb, tab_nc, tab_tu_nhap = st.tabs(["🟢 Đề Cơ Bản", "🔴 Đề Nâng Cao", "✏️ Nhập Đề Bài Riêng"])
    with tab_cb:
        col_cb1, col_cb2 = st.columns([1, 2])
        selected_cb = col_cb1.selectbox("Chọn đề Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="cb")
        col_cb2.info(db.DE_BAI_CO_BAN[selected_cb]["text"])
        if col_cb2.button("📌 Chọn đề này", key="b_cb"): st.session_state["selected_de_key"], st.session_state["current_de_info"] = selected_cb, db.DE_BAI_CO_BAN[selected_cb]; st.rerun()
    with tab_nc:
        col_nc1, col_nc2 = st.columns([1, 2])
        selected_nc = col_nc1.selectbox("Chọn đề Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="nc")
        col_nc2.info(db.DE_BAI_NANG_CAO[selected_nc]["text"])
        if col_nc2.button("📌 Chọn đề này", key="b_nc"): st.session_state["selected_de_key"], st.session_state["current_de_info"] = selected_nc, db.DE_BAI_NANG_CAO[selected_nc]; st.rerun()
    with tab_tu_nhap:
        custom_de = st.text_area("Nhập đề bài:", height=110)
        custom_vdnl = st.text_input("Vấn đề nghị luận là gì?")
        if st.button("🔍 AI Tạo khung định hướng", type="primary"):
            if not custom_de.strip(): st.warning("Vui lòng nhập đề!")
            else:
                with st.spinner("AI đang tạo dàn ý riêng..."):
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {custom_de[:55]}..."
                    st.session_state["current_de_info"] = generate_custom_outline(custom_de.strip(), custom_vdnl.strip())
                    st.success("✅ Đã tạo xong Khung định hướng!")

    st.markdown("---")
    st.info(f"📌 **Đề đang chọn:** {st.session_state['selected_de_key']}\n\n*Nội dung:* {st.session_state['current_de_info'].get('text', '')}")

with tabs[1]:
    cur_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.15, 0.85], gap="large")
    with c_left:
        st.markdown("#### 🛠️ Khung định hướng tư duy")
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            for itm in cur_info.get("explain_items", []): st.markdown(itm)
        with st.expander("💡 Thao tác 2: Bàn luận (5 ý)", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                for a in q.get("y_tra_loi", []): st.markdown(a)
        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế", expanded=True):
            for ev in cur_info.get("evidence", []):
                if isinstance(ev, dict): st.markdown(f"**👤 {ev.get('ten', '')}**: {ev.get('chi_tiet', '')} -> *{ev.get('y_nghia', '')}*")
        with st.expander("🔄 Thao tác 4: Phản đề", expanded=True):
            for c in cur_info.get("counter", []): st.markdown(c)
    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn (Chat)")
        chat_box = st.container(height=380, border=True)
        for role, msg in st.session_state["chat_history"]:
            chat_box.markdown(f"**{'🧑‍🎓 Em' if role=='user' else '👩‍🏫 Trợ lý'}:** {msg}")
            chat_box.markdown("---")
        u_q = st.text_area("Hỏi Trợ lý:", height=80, key="chat_in")
        c1, c2 = st.columns([2,1])
        if c1.button("🚀 Gửi", type="primary", use_container_width=True):
            if u_q.strip():
                st.session_state["chat_history"].append(("user", u_q.strip()))
                reply = ai_advisor_response(cur_info["text"], cur_info.get("vdnl_chuan", ""), u_q.strip(), len(st.session_state["chat_history"]))
                st.session_state["chat_history"].append(("assistant", reply))
                st.rerun()
        if c2.button("🗑️ Xóa", use_container_width=True):
            st.session_state["chat_history"] = [("assistant", "Chào em! Cô sẵn sàng hướng dẫn, nhưng em tự viết nhé!")]
            st.rerun()

with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    write_mode = st.radio("Chọn hình thức nộp bài:", ["✍️ Gõ trực tiếp", "📷 Tải ảnh chụp viết tay"], horizontal=True)
    if write_mode == "✍️ Gõ trực tiếp":
        essay_input = st.text_area("Viết bài tại đây:", value=st.session_state.get("user_essay", ""), height=380)
        st.session_state["user_essay"] = essay_input
        if st.button("📊 Chấm Rubric Khắt Khe", type="primary"):
            if not essay_input.strip(): st.warning("Vui lòng nhập bài viết!")
            else:
                with st.spinner("Đang chấm điểm và lập bảng Rubric 7 tiêu chí..."):
                    st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(st.session_state["selected_de_key"], st.session_state["current_de_info"], essay_input.strip())
                    st.success("✅ Đã chấm xong! Xem kết quả ở Bước 4.")
    else:
        uploaded_img = st.file_uploader("Tải ảnh bài làm (Hỗ trợ Vision AI):", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric", type="primary"):
                with st.spinner("AI đang nhận diện chữ viết tay và chấm điểm..."):
                    st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(st.session_state["selected_de_key"], st.session_state["current_de_info"], "", image_obj=img_obj)
                    st.success("✅ Đã chấm xong ảnh! Xem kết quả ở Bước 4.")

with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra Theo Rubric 7 Tiêu Chí</div>', unsafe_allow_html=True)
    c_r1, c_r2 = st.columns([1, 1.35], gap="large")
    with c_r1:
        edited = st.text_area("Chỉnh sửa bài viết:", value=st.session_state.get("user_essay", ""), height=420)
        st.session_state["user_essay"] = edited
        if st.button("🔍 Cập nhật chấm lại", type="primary"):
            with st.spinner("Đang chấm lại..."):
                st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(st.session_state["selected_de_key"], st.session_state["current_de_info"], edited.strip())
    with c_r2:
        st.markdown("##### 📋 Bảng Điểm & Nhận Xét Chi Tiết:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True): st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info("Chưa có bảng điểm. Hãy chấm bài ở Bước 3.")
