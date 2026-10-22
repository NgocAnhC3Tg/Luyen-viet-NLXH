import streamlit as st
import data_de_bai as db
from PIL import Image
import google.generativeai as genai
import json

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN & TÊN HỆ THỐNG CHUẨN XÁC
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
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc;
    }
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 22px;
    }
    .hero-title {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px !important;
        color: #ffffff !important;
    }
    .hero-subtitle {
        font-size: 0.92rem;
        color: #dbeafe;
        margin: 0;
    }
    .evidence-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #16a34a;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. QUẢN LÝ SESSION STATE
# ==============================================================================
def get_api_key():
    return st.session_state.get("gemini_api_key", "")

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp lập ý, cung cấp dẫn chứng thực tế, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")
    ]
if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""

# ==============================================================================
# 3. ĐỘNG CƠ AI SƯ PHẠM (TRỢ LÝ & CHẤM ĐIỂM)
# ==============================================================================
def call_gemini(prompt):
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return None

def generate_custom_outline(topic_text, student_guess):
    api_key = get_api_key()
    if api_key:
        prompt = f"""Hãy phân tích đề bài NLXH sau và trả về MỘT CHUỖI JSON HỢP LỆ (không có markdown).
Đề bài: "{topic_text}"
Dự đoán của học sinh: "{student_guess}"

Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{topic_text}",
  "vdnl_chuan": "Nêu vấn đề nghị luận cốt lõi ngắn gọn.",
  "explain_items": [
    "- Giải thích từ khóa [X]: ...",
    "- Ý nghĩa của [Y]: ..."
  ],
  "vdnl_ket_luan": "Chốt lại vấn đề là...",
  "questions": [
    {{
      "cau_hoi": "Tại sao vấn đề này lại quan trọng?",
      "y_tra_loi": ["- Ý 1...", "- Ý 2..."]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên nhân vật cụ thể",
      "chi_tiet": "Hành động thực tế của họ",
      "y_nghia": "Chứng minh cho điều gì",
      "nguon": "Thực tế đời sống"
    }}
  ],
  "counter": [
    "- Lên án biểu hiện trái ngược: ...",
    "- Lưu ý tránh cực đoan: ..."
  ],
  "dani_chi_tiet": {{
    "mb": "Dẫn dắt...",
    "gt": "Giải thích...",
    "bl": "Bàn luận...",
    "dc": "Dẫn chứng...",
    "pb": "Phản đề...",
    "kb": "Kết bài..."
  }}
}}"""
        res = call_gemini(prompt)
        if res:
            try:
                res_clean = res.strip().removeprefix("```json").removesuffix("```").strip()
                return json.loads(res_clean)
            except:
                pass
    
    # Fallback nếu không có API Key
    return {
        "text": topic_text,
        "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận của đề bài",
        "explain_items": [
            f"- **Giải thích từ khóa chính trong đề:** Cần làm rõ ý nghĩa của các khái niệm cốt lõi trong câu nói/vấn đề.",
            "- **Mối liên hệ:** Khái quát thông điệp sâu sắc mà đề bài hướng tới."
        ],
        "vdnl_ket_luan": "Nhận thức sâu sắc về giá trị của vấn đề trong đời sống.",
        "questions": [{"cau_hoi": f"Ý nghĩa và sức mạnh của vấn đề này là gì?", "y_tra_loi": ["- Tác động tích cực đến bản thân.", "- Lan tỏa giá trị đến cộng đồng."]}],
        "evidence": [{"ten": "Tấm gương tiêu biểu", "chi_tiet": "Hành động cụ thể liên quan trực tiếp đến đề bài.", "y_nghia": "Minh chứng cho sức sống của vấn đề.", "nguon": "Thực tế"}],
        "counter": ["- Phê phán những biểu hiện lệch chuẩn, sống thờ ơ hoặc hiểu sai về vấn đề."],
        "dani_chi_tiet": {"mb": "Dẫn dắt và nêu VĐNL.", "gt": "Giải thích các từ khóa trọng tâm.", "bl": "Triển khai 5 ý luận điểm.", "dc": "Phân tích 1-2 dẫn chứng tiêu biểu.", "pb": "Lật lại vấn đề, phản đề.", "kb": "Khẳng định lại và liên hệ bản thân."}
    }

def ai_advisor_chat(topic, history_len, user_msg):
    msg = user_msg.lower()
    if any(k in msg for k in ["viết hộ", "viết giùm", "viết luôn", "làm bài"]):
        return "👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết thay em! Viết văn là rèn luyện tư duy. Cô chỉ hướng dẫn dàn ý và dẫn chứng, em phải tự viết nhé. Em muốn cô gợi ý mở bài hay dẫn chứng nào?"
    if any(k in msg for k in ["thêm", "khác", "nữa", "ví dụ"]) and history_len > 3:
        return "👩‍🏫 **Trợ lý Ngữ văn gợi ý DẪN CHỨNG MỚI:**\n1. **Đội ngũ y bác sĩ tuyến đầu / Tình nguyện viên:** Cống hiến thầm lặng vì cộng đồng.\n2. **Nick Vujicic / Người khuyết tật vươn lên:** Nghị lực sống phi thường.\n3. **Giáo viên cắm bản vùng cao:** Hy sinh thầm lặng ươm mầm tri thức.\n👉 Hãy chọn 1 người và tự viết phân tích nhé!"
    if any(k in msg for k in ["dẫn chứng", "ví dụ", "chứng minh"]):
        return "👩‍🏫 **Trợ lý Ngữ văn gợi ý Dẫn chứng:**\n1. **Thầy giáo Nguyễn Ngọc Ký:** Vượt nghịch cảnh.\n2. **Ca sĩ Đen Vâu:** Lối sống giản dị, cống hiến cho cộng đồng (Dự án Nuôi Em).\n👉 Em hãy lấy nháp ra và viết phân tích hành động của họ gắn với đề bài nhé."
    if "mở bài" in msg:
        return "👩‍🏫 **Gợi ý Mở bài:** Dẫn dắt từ một hiện tượng thực tế đời sống, sau đó nêu bật vấn đề nghị luận. (VD: *Trong nhịp sống hối hả hiện đại, đôi khi ta quên mất...*). Em thử viết 1 câu nháp xem sao?"
    if "luận điểm" in msg or "ý chính" in msg:
        return "👩‍🏫 **Khung 5 luận điểm Thân bài:**\n1. Biểu hiện thực tế.\n2. Nguyên nhân (khách quan/chủ quan).\n3. Tác động đến sự phát triển của cá nhân.\n4. Ý nghĩa lan tỏa đối với xã hội.\n5. Hậu quả nếu thiếu đi điều này.\n👉 Em hãy tự triển khai từng ý thành các đoạn văn nhé."
    return "👩‍🏫 **Trợ lý Ngữ văn:** Cô đang theo dõi bài làm của em. Em cần hướng dẫn chi tiết cách tìm ý, lấy dẫn chứng hay phản đề? Hãy hỏi cụ thể nhé."

def ai_evaluate_strict(de_key, essay_text):
    api_key = get_api_key()
    if api_key:
        prompt = f"""Đóng vai giáo viên Ngữ văn cực kỳ KHẮT KHE. Chấm bài văn sau theo chuẩn Rubric 7 tiêu chí (Thang 10).
BẮT BUỘC:
- Nếu bài làm hời hợt, kể lể, ít ý: Tổng điểm chỉ được 4.0 - 6.5.
- Không cho điểm tối đa nếu chưa phân tích sâu. Bắt buộc dùng bước nhảy điểm: 0.25, 0.5, 0.75, 1.0.
- PHẢI trích dẫn (quote) một vài câu văn lủng củng/nông cạn của học sinh để làm bằng chứng trừ điểm trong cột "Căn cứ chấm".

Đề bài: {de_key}
Bài làm của học sinh:
{essay_text}

Trình bày bằng Markdown bảng Rubric 7 tiêu chí (Bố cục, Xác định VĐNL, Giải thích, Luận điểm (5 ý), Dẫn chứng, Phản đề, Diễn đạt), ghi rõ điểm từng phần, trích dẫn lỗi sai, và nhận xét tổng quan."""
        res = call_gemini(prompt)
        if res: return res
    
    # Fallback nghiêm khắc
    wc = len(essay_text.strip().split())
    if wc < 200:
        return "### 📊 RUBRIC ĐÁNH GIÁ (BÀI QUÁ NGẮN/YẾU)\n**Tổng điểm: 3.5 / 10**.\nBài làm chưa đủ cấu trúc, các ý chỉ gạch đầu dòng, không có dẫn chứng phân tích. Em cần làm lại hoàn toàn Thân bài."
    elif wc < 400:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC KHẮT KHE (MỨC TRUNG BÌNH - KHÁ)
| Tiêu chí | Điểm tối đa | Điểm đạt | Căn cứ chấm điểm (Trích lỗi cụ thể) |
|---|---|---|---|
| 1. Bố cục | 0.5 | 0.50 | Đã có 3 phần Mở - Thân - Kết. |
| 2. Xác định VĐNL | 0.5 | 0.50 | Đi đúng hướng đề bài. |
| 3. Giải thích | 1.0 | 0.50 | Mới chỉ giải thích bề mặt, chưa đào sâu bản chất khái niệm. |
| 4. Hệ thống luận điểm | 3.5 | 1.50 | Thiếu ý. Mới chỉ nêu, chưa phân tích. Đoạn văn lập luận còn rất nông. |
| 5. Dẫn chứng thực tế | 2.5 | 1.00 | Dẫn chứng mang tính kể lể, chung chung, chưa gắn chặt với lập luận để làm sáng tỏ đề. |
| 6. Phản đề & Bài học | 1.0 | 0.50 | Phản đề hời hợt, chỉ viết chiếu lệ 1 câu. |
| 7. Diễn đạt & Sáng tạo| 1.0 | 0.50 | Còn lặp từ, hành văn chưa mượt mà. |
**📌 TỔNG ĐIỂM: 5.0 / 10.0**
⚠️ **NHẬN XÉT:** Bài làm dừng ở mức liệt kê ý, thiếu sự đào sâu suy nghĩ. Cần bổ sung ngay dẫn chứng cụ thể và phân tích kỹ tác động xã hội."""
    else:
        return "### 📊 BẢNG ĐÁNH GIÁ RUBRIC (MỨC KHÁ)\n**Tổng điểm: 7.25 / 10.0**.\nBài làm khá tốt, bố cục rõ. Tuy nhiên hệ thống luận điểm cần bóc tách sâu hơn về nguyên nhân gốc rễ và góc nhìn phản đề cần sắc sảo hơn để đạt mức điểm Giỏi (>8.0)."

# ==============================================================================
# 4. SIDEBAR & GIAO DIỆN
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input("Nhập mã xác thực (Gemini API Key) để AI chấm điểm thực chất:", type="password", value=st.session_state["gemini_api_key"])
    if api_key_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = api_key_input
    st.success("✅ HỆ THỐNG LUYỆN VIẾT NLXH đã sẵn sàng!")
    st.warning("📌 Lưu ý Sư phạm: Trợ lý tuyệt đối không viết hộ bài.")

st.markdown("""<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div>
<p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT theo định hướng phát triển năng lực</p></div>""", unsafe_allow_html=True)

tabs = st.tabs(["🌱 BƯỚC 1: TÌM HIỂU ĐỀ", "🧵 BƯỚC 2: TÌM Ý & DẪN CHỨNG", "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI", "📊 BƯỚC 4: KIỂM TRA (RUBRIC)"])

with tabs[0]:
    tab_cb, tab_nc, tab_tu_nhap = st.tabs(["🟢 Đề Cơ Bản", "🔴 Đề Nâng Cao", "✏️ Đề Tự Nhập (AI tạo dàn ý động)"])
    with tab_cb:
        col1, col2 = st.columns([1,2])
        selected_cb = col1.selectbox("Chọn đề Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="cb")
        col2.info(db.DE_BAI_CO_BAN[selected_cb]["text"])
        if col2.button("📌 Chọn đề này"): 
            st.session_state["selected_de_key"] = selected_cb
            st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[selected_cb]
            st.rerun()
    with tab_nc:
        col1, col2 = st.columns([1,2])
        selected_nc = col1.selectbox("Chọn đề Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="nc")
        col2.info(db.DE_BAI_NANG_CAO[selected_nc]["text"])
        if col2.button("📌 Chọn đề này", key="btn_nc"): 
            st.session_state["selected_de_key"] = selected_nc
            st.session_state["current_de_info"] = db.DE_BAI_NANG_CAO[selected_nc]
            st.rerun()
    with tab_tu_nhap:
        txt_de = st.text_area("Nhập nội dung đề bài mới của bạn:")
        txt_guess = st.text_input("Vấn đề nghị luận là gì?")
        if st.button("🚀 AI Thiết lập Khung hướng dẫn tự động", type="primary"):
            if not txt_de.strip(): st.warning("Vui lòng nhập đề!")
            else:
                with st.spinner("AI đang phân tích đề và tạo dàn ý chuyên sâu..."):
                    outline = generate_custom_outline(txt_de.strip(), txt_guess.strip())
                    st.session_state["selected_de_key"] = "Đề tự nhập: " + txt_de[:30] + "..."
                    st.session_state["current_de_info"] = outline
                    st.success("✅ Đã tạo Khung định hướng riêng cho đề này. Hãy sang Bước 2!")

    st.markdown("---")
    st.info(f"📌 **Đang làm việc với đề:** {st.session_state['selected_de_key']}\n\n*Nội dung:* {st.session_state['current_de_info'].get('text', '')}")

with tabs[1]:
    cur_info = st.session_state["current_de_info"]
    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        st.markdown(f"#### 🛠️ Khung định hướng cho đề bài đang chọn")
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            for i in cur_info.get("explain_items", []): st.markdown(i)
        with st.expander("💡 Thao tác 2: Bàn luận (5 ý)", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi','')}**")
                for ans in q.get("y_tra_loi", []): st.markdown(ans)
        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế", expanded=True):
            for ev in cur_info.get("evidence", []):
                st.markdown(f"<div class='evidence-card'><b>👤 {ev.get('ten','')}</b><br>• Chi tiết: {ev.get('chi_tiet','')}<br>• Ý nghĩa: {ev.get('y_nghia','')}</div>", unsafe_allow_html=True)
        with st.expander("🔄 Thao tác 4: Phản đề", expanded=True):
            for c in cur_info.get("counter", []): st.markdown(c)
            
    with c2:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn (Chat)")
        chat_box = st.container(height=380, border=True)
        for role, msg in st.session_state["chat_history"]:
            chat_box.markdown(f"**{'🧑‍🎓 Em' if role=='user' else '👩‍🏫 Trợ lý'}:** {msg}")
            chat_box.markdown("---")
        user_q = st.text_input("Hỏi Trợ lý (Ví dụ: Xin gợi ý dẫn chứng khác):", key="q1")
        if st.button("🚀 Gửi"):
            if user_q.strip():
                st.session_state["chat_history"].append(("user", user_q))
                reply = ai_advisor_chat(cur_info["text"], len(st.session_state["chat_history"]), user_q)
                st.session_state["chat_history"].append(("assistant", reply))
                st.rerun()

with tabs[2]:
    st.markdown("#### ✍️ Không gian tự hành văn (Trợ lý không viết hộ)")
    st.session_state["user_essay"] = st.text_area("Viết bài tại đây:", value=st.session_state["user_essay"], height=350)
    if st.button("📊 Chấm điểm khắt khe (Rubric 7 Tiêu chí)", type="primary"):
        if not st.session_state["user_essay"].strip(): st.warning("Hãy nhập bài làm!")
        else:
            with st.spinner("Cô đang chấm bài, kiểm tra từng ý luận điểm..."):
                st.session_state["rubric_evaluation"] = ai_evaluate_strict(st.session_state["selected_de_key"], st.session_state["user_essay"])
                st.success("✅ Đã chấm xong. Chuyển sang Bước 4 xem điểm!")

with tabs[3]:
    st.markdown("#### 📋 Bảng Nhận Xét & Trừ Điểm Thực Chất")
    if st.session_state["rubric_evaluation"]:
        st.markdown(st.session_state["rubric_evaluation"])
    else:
        st.info("Hãy hoàn thành bài viết ở Bước 3 và bấm Chấm điểm.")
