import streamlit as st
import data_de_bai as db
from PIL import Image
import google.generativeai as genai
import json
import re

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
</style>
""", unsafe_allow_html=True
)

# ==============================================================================
# 2. QUẢN LÝ SESSION STATE
# ==============================================================================
if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng mắc ở phần nào trong quá trình lập ý và tìm dẫn chứng? Hãy trao đổi cụ thể với cô nhé!")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""

def get_api_key():
    return st.session_state.get("gemini_api_key", "").strip()

# ==============================================================================
# 3. ĐỘNG CƠ AI THÔNG MINH (BÁM SÁT NGỮ CẢNH & DÀN Ý ĐỘNG SÂU SẮC)
# ==============================================================================
def call_ai(prompt, image=None):
    key = get_api_key()
    if not key:
        return "⚠️ Thầy/cô vui lòng nhập mã Gemini API Key ở thanh bên trái (Sidebar) để kích hoạt toàn bộ năng lực phân tích sâu của Trợ lý Ngữ văn!"
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
        return "⚠️ Không kết nối được với mô hình AI. Vui lòng kiểm tra lại API Key."
    except Exception as e:
        return f"⚠️ Lỗi hệ thống AI: {str(e)}"

def generate_custom_outline(topic_text, student_guess):
    key = get_api_key()
    if not key:
        return {
            "text": topic_text, "vdnl_chuan": student_guess or "Vấn đề nghị luận",
            "explain_items": ["- ⚠️ Chưa nhập API Key nên AI chưa thể tạo dàn ý động chi tiết cho đề này."],
            "vdnl_ket_luan": "Vui lòng nhập API Key ở sidebar.", "questions": [], "evidence": [], "counter": [], "dani_chi_tiet": {}
        }
    
    prompt = f"""Đóng vai chuyên gia sư phạm Ngữ văn THPT. Hãy phân tích thật sâu sắc đề bài nghị luận xã hội sau và trả về MỘT CHUỖI JSON HỢP LỆ (không dùng markdown code block, chỉ xuất chuỗi json thuần túy):
Đề bài: "{topic_text}"
Dự đoán vấn đề của học sinh/giáo viên: "{student_guess}"

YÊU CẦU: Xây dựng một dàn ý định hướng tư duy ĐẦY ĐỦ, RÕ RÀNG, ĐÚNG TRỌNG TÂM, KHÔNG CHUNG CHUNG.

Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{topic_text}",
  "vdnl_chuan": "Xác định rõ ràng và sắc bén vấn đề nghị luận cốt lõi",
  "explain_items": [
    "- Giải thích rõ ý nghĩa từ khóa cốt lõi trong đề...",
    "- Làm rõ thông điệp/mối quan hệ nhân sinh đặt ra..."
  ],
  "vdnl_ket_luan": "Khái quát ý nghĩa nhân sinh sâu sắc của vấn đề",
  "questions": [
    {{
      "cau_hoi": "Hệ thống luận điểm bàn luận trọng tâm (tối thiểu 4-5 ý sâu sắc)",
      "y_tra_loi": [
        "- Ý 1 (Biểu hiện cụ thể trong đời sống)...",
        "- Ý 2 (Nguyên nhân sâu xa/chủ quan/khách quan)...",
        "- Ý 3 (Tác động tích cực đối với cá nhân)...",
        "- Ý 4 (Ý nghĩa lan tỏa đối với cộng đồng, xã hội)...",
        "- Ý 5 (Hậu quả nếu lãng quên hoặc đi ngược lại vấn đề)..."
      ]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên nhân vật/sự kiện thực tế tiêu biểu",
      "chi_tiet": "Hành động cụ thể chứng minh",
      "y_nghia": "Ý nghĩa kết nối trực tiếp với đề bài",
      "nguon": "Thực tiễn đời sống"
    }}
  ],
  "counter": [
    "- Phê phán những biểu hiện lệch lạc, thờ ơ, ích kỷ liên quan đến đề...",
    "- Bài học lật lại vấn đề (phản đề) để nhận thức toàn diện, tránh cực đoan..."
  ],
  "dani_chi_tiet": {{
    "mb": "Dẫn dắt tự nhiên từ thực tiễn và nêu bật vấn đề nghị luận.",
    "gt": "Giải thích tường minh từ khóa và thông điệp ngữ liệu.",
    "bl": "Triển khai hệ thống 5 luận điểm chặt chẽ, sâu sắc.",
    "dc": "Phân tích dẫn chứng người thật việc thật sắc sảo.",
    "pb": "Lật lại vấn đề (phản đề) và rút ra bài học nhận thức, hành động.",
    "kb": "Khẳng định lại giá trị trường tồn của vấn đề."
  }}
}}"""
    res = call_ai(prompt)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass
    
    return {
        "text": topic_text, "vdnl_chuan": student_guess or "Vấn đề nghị luận",
        "explain_items": ["- **Giải thích từ khóa:** Cần cắt nghĩa rõ ràng các khái niệm trọng tâm trong đề."],
        "vdnl_ket_luan": "Giá trị cốt lõi của vấn đề.",
        "questions": [{"cau_hoi": "Hệ thống luận điểm phân tích:", "y_tra_loi": ["- Biểu hiện thực tế.", "- Nguyên nhân và tác động."]}],
        "evidence": [{"ten": "Tấm gương tiêu biểu", "chi_tiet": "Hành động thực tế", "y_nghia": "Minh chứng", "nguon": "Thực tế"}],
        "counter": ["- Phê phán lối sống hời hợt."], "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản đề", "kb": "Kết bài"}
    }

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    key_in = st.text_input("Nhập mã Gemini API Key:", type="password", value=st.session_state["gemini_api_key"])
    if key_in != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = key_in
    if key_in: st.success("✅ Đã lưu API Key!")
    else: st.warning("⚠️ Vui lòng nhập API Key để Trợ lý AI phân tích sâu sắc.")
    
    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM\n1. Chọn/Nhập đề & Xác định VĐNL\n2. Lập ý, Dẫn chứng & Hỏi Trợ lý Ngữ văn\n3. Viết bài độc lập (Gõ/Ảnh)\n4. Kiểm tra và chỉnh sửa theo Rubric")

st.markdown("""<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div><p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT</p></div>""", unsafe_allow_html=True)

tabs = st.tabs(["🌱 BƯỚC 1: TÌM HIỂU ĐỀ", "🧵 BƯỚC 2: TÌM Ý & CHAT AI", "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI", "📊 BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA"])

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
        custom_t = st.text_area("Nhập nội dung đề bài tự do:", height=100, placeholder="Ví dụ: Bàn về ý nghĩa của lòng biết ơn trong cuộc sống hiện đại...")
        custom_v = st.text_input("Vấn đề nghị luận chính là gì?", placeholder="Ví dụ: Lòng biết ơn...")
        if st.button("🚀 AI Phân tích & Tạo khung định hướng sâu sắc", type="primary"):
            if not custom_t.strip():
                st.warning("Vui lòng nhập nội dung đề bài!")
            else:
                with st.spinner("AI đang phân tích từ khóa, xây dựng hệ thống luận điểm và tìm dẫn chứng riêng cho đề này..."):
                    outline_data = generate_custom_outline(custom_t.strip(), custom_v.strip())
                    short_title = custom_t.strip()[:45] + "..."
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                    st.session_state["current_de_info"] = outline_data
                    st.success("✅ Đã tạo xong khung định hướng tư duy đầy đủ, rõ ràng, đúng trọng tâm cho đề của thầy/cô! Mời sang Bước 2.")

    st.markdown("---")
    st.info(f"📌 **Đề đang làm việc:** {st.session_state['selected_de_key']}\n\n*Nội dung:* {st.session_state['current_de_info'].get('text', '')}")

with tabs[1]:
    cur_info = st.session_state["current_de_info"]
    col1, col2 = st.columns([1.2, 0.8], gap="large")
    
    with col1:
        st.markdown("#### 🛠️ Khung định hướng tư duy chi tiết")
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            for i in cur_info.get("explain_items", []): st.markdown(i)
            st.markdown(f"**👉 Chốt lại vấn đề nghị luận:** {cur_info.get('vdnl_ket_luan', '')}")
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Từ 5 ý)", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                for ans in q.get("y_tra_loi", []): st.markdown(ans)
        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế", expanded=True):
            for ev in cur_info.get("evidence", []):
                if isinstance(ev, dict):
                    st.markdown(f"""
                    <div class='evidence-card'>
                        <h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>
                        <p style='margin:0 0 6px 0;'><b>• Chi tiết hành động:</b> {ev.get('chi_tiet', '')}</p>
                        <p style='margin:0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p>
                    </div>""", unsafe_allow_html=True)
        with st.expander("🔄 Thao tác 4: Phản đề & Bài học", expanded=True):
            for c in cur_info.get("counter", []): st.markdown(c)

    with col2:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn (Bám sát câu hỏi học sinh)")
        box = st.container(height=380, border=True)
        for role, msg in st.session_state["chat_history"]:
            box.markdown(f"**{'🧑‍🎓 Học sinh' if role=='user' else '👩‍🏫 Trợ lý Ngữ văn'}:** {msg}")
            box.markdown("---")
        
        q_text = st.text_area("Hỏi Trợ lý (Ví dụ: Gợi ý cách triển khai luận điểm 2 hoặc cho thêm dẫn chứng về lòng biết ơn):", height=80, key="q_chat")
        b_send, b_clear = st.columns(2)
        if b_send.button("🚀 Gửi câu hỏi", type="primary", use_container_width=True):
            if q_text.strip():
                low_q = q_text.lower()
                if any(w in low_q for w in ["viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho bài văn", "đoạn văn mẫu"]):
                    reply = "👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết hộ hay viết thay bài văn cho em! Viết văn là quá trình rèn luyện tư duy chính mình. Em hãy tự nháp ý rồi cô sẽ hướng dẫn cách hành văn nhé!"
                else:
                    prompt_chat = f"""Đóng vai giáo viên Ngữ văn THPT sắc sảo, tận tâm. Học sinh đang hỏi trong quá trình tìm hiểu đề và lập ý (Bước 2).
Đề bài hiện tại: "{cur_info.get('text', '')}"
Vấn đề nghị luận: "{cur_info.get('vdnl_chuan', '')}"
Câu hỏi/Yêu cầu cụ thể của học sinh: "{q_text}"

NGUYÊN TẮC QUAN TRỌNG:
1. TUYỆT ĐỐI KHÔNG VIẾT HỘ, KHÔNG CHO VĂN MẪU.
2. Trả lời cực kỳ bám sát, thẳng vào câu hỏi của học sinh. Nếu học sinh hỏi về biểu hiện, hãy phân tích biểu hiện. Nếu hỏi dẫn chứng, cung cấp ngay nhân vật thực tế sắc bén. Nếu hỏi phản biện, hướng dẫn cách lật vấn đề. Trả lời chi tiết, chuyên sâu, không chung chung mập mờ."""
                    reply = call_ai(prompt_chat)
                
                st.session_state["chat_history"].append(("user", q_text))
                st.session_state["chat_history"].append(("assistant", reply))
                st.rerun()
        if b_clear.button("🗑️ Xóa lịch sử", use_container_width=True):
            st.session_state["chat_history"] = [("assistant", "Chào em! Cô sẵn sàng hỗ trợ em bóc tách ý nghĩa và tìm dẫn chứng phù hợp nhất với đề bài.")]
            st.rerun()

with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    mode = st.radio("Chọn hình thức nộp bài:", ["✍️ Gõ bài trực tiếp", "📷 Tải ảnh chụp viết tay"], horizontal=True)
    
    if mode == "✍️ Gõ bài trực tiếp":
        essay = st.text_area("Khung soạn thảo bài làm của học sinh:", value=st.session_state.get("user_essay", ""), height=350, placeholder="Tự viết bài văn nghị luận xã hội của em tại đây...")
        st.session_state["user_essay"] = essay
        if st.button("📊 Chấm Rubric 7 Tiêu Chí (Đánh giá thực chất)", type="primary"):
            if not essay.strip(): st.warning("Vui lòng nhập bài viết!")
            else:
                with st.spinner("AI đang chấm bài, phân tích từng tiêu chí và tìm câu văn lủng củng để góp ý..."):
                    prompt_grade = f"""Đóng vai giáo viên Ngữ văn THPT chấm thi chuẩn mực, khách quan. Chấm bài NLXH sau theo Rubric 7 tiêu chí (Thang 10, bước nhảy 0.25/0.5/1.0).
YÊU CẦU: Lập bảng Markdown gồm 4 cột (Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn câu văn của HS để làm minh chứng góp ý).
Đề: "{cur_info.get('text', '')}"
Bài làm:
{essay}
Cuối bảng ghi TỔNG ĐIỂM và LỜI PHÊ SÂU SẮC giúp học sinh hoàn thiện hơn."""
                    st.session_state["rubric_evaluation"] = call_ai(prompt_grade)
                    st.success("✅ Đã chấm xong! Mời sang Bước 4 xem kết quả chi tiết.")
    else:
        img_file = st.file_uploader("Tải lên ảnh chụp bài viết tay:", type=["png", "jpg", "jpeg"])
        if img_file:
            pil_img = Image.open(img_file)
            st.image(pil_img, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric 7 Tiêu Chí", type="primary"):
                with st.spinner("AI đang nhận diện chữ viết tay và đánh giá thực chất..."):
                    prompt_grade_img = f"""Đóng vai giáo viên Ngữ văn THPT chấm thi chuẩn mực. Hãy đọc chữ viết tay trong ảnh và chấm bài theo Rubric 7 tiêu chí (Thang 10).
Lập bảng Markdown gồm 4 cột: Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn lỗi.
Cuối bảng ghi TỔNG ĐIỂM và LỜI PHÊ."""
                    st.session_state["rubric_evaluation"] = call_ai(prompt_grade_img, image=pil_img)
                    st.success("✅ Đã chấm xong ảnh! Mời sang Bước 4 xem kết quả.")

with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra và Chỉnh Sửa Theo Rubric</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.3], gap="large")
    with c1:
        edit_es = st.text_area("Chỉnh sửa bài làm tại đây sau khi nhận góp ý:", value=st.session_state.get("user_essay", ""), height=400)
        st.session_state["user_essay"] = edit_es
        if st.button("🔍 Nộp lại để chấm điểm", type="primary"):
            with st.spinner("Đang chấm lại theo Rubric..."):
                prompt_re = f"""Chấm lại bài NLXH sau theo Rubric 7 tiêu chí (Thang 10, trích dẫn lỗi cụ thể):
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
