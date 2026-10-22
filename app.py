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
    .rubric-info-box { background-color: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; padding: 16px 20px; border-radius: 10px; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True
)

# ==============================================================================
# 2. QUẢN LÝ SESSION STATE
# ==============================================================================
def get_api_key():
    return st.session_state.get("gemini_api_key", "").strip()

if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state: st.session_state["eval_vdnl_text"] = ""

# ==============================================================================
# 3. ĐỘNG CƠ AI THỰC CHẤT VÀ KHẮT KHE
# ==============================================================================
def call_gemini_api(prompt_text, image_obj=None, max_tokens=2000):
    api_key = get_api_key()
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        contents = [prompt_text]
        if image_obj: contents.append(image_obj)
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        return f"⚠️ Lỗi kết nối AI: {str(e)}"

def generate_custom_outline(topic_text, student_guess):
    prompt = f"""Đóng vai chuyên gia sư phạm Ngữ văn. Phân tích đề bài NLXH sau và trả về MỘT CHUỖI JSON HỢP LỆ (chỉ xuất JSON, không text thừa).
Đề bài: "{topic_text}"
Dự đoán của học sinh: "{student_guess}"

YÊU CẦU NGHIÊM NGẶT: Đi thẳng vào nội dung cốt lõi của đề này. TUYỆT ĐỐI KHÔNG dùng các câu văn mẫu chung chung như "Cắt nghĩa từ khóa", "Rút ra thông điệp". Phải trích xuất và chỉ rõ từ khóa đó là gì, biểu hiện cụ thể ra sao.

Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{topic_text}",
  "vdnl_chuan": "[Xác định trực diện vấn đề cốt lõi]",
  "explain_items": [
    "- Giải thích cụ thể khái niệm [A] trong đề nghĩa là...",
    "- Giải thích ý nghĩa của hình ảnh/nhận định [B]..."
  ],
  "vdnl_ket_luan": "Vấn đề trên muốn nhấn mạnh điều gì...",
  "questions": [
    {{
      "cau_hoi": "Nguyên nhân/Biểu hiện/Sức mạnh của vấn đề này trong thực tế?",
      "y_tra_loi": ["- Ý sâu sắc 1...", "- Ý sâu sắc 2...", "- Ý sâu sắc 3..."]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên một nhân vật/sự kiện CÓ THẬT và RẤT NỔI TIẾNG",
      "chi_tiet": "Mô tả sắc bén hành động của họ liên quan mật thiết đến đề",
      "y_nghia": "Hành động đó chứng minh điều gì cho luận điểm",
      "nguon": "Thực tiễn đời sống/Lịch sử"
    }}
  ],
  "counter": [
    "- Lên án cụ thể hạng người nào trong xã hội hiện nay?...",
    "- Bài học lật lại vấn đề để tránh hiểu cực đoan..."
  ],
  "dani_chi_tiet": {{"mb": "...", "gt": "...", "bl": "...", "dc": "...", "pb": "...", "kb": "..."}}
}}"""
    res = call_gemini_api(prompt)
    if res:
        try:
            match = re.search(r'\{.*\}', res, re.DOTALL)
            if match: return json.loads(match.group(0))
        except Exception:
            pass
    
    return {
        "text": topic_text, "vdnl_chuan": student_guess if student_guess else "Chưa xác định",
        "explain_items": ["⚠️ Lỗi: Không thể tải AI động do chưa cấu hình API Key. Vui lòng nhập API Key để tạo dàn ý thực chất."],
        "vdnl_ket_luan": "Vui lòng nhập API Key.", "questions": [], "evidence": [], "counter": [], "dani_chi_tiet": {}
    }

def ai_advisor_response(de_text, vdnl_chuan, user_q, chat_history):
    # Lọc yêu cầu viết hộ cực mạnh
    h_verb = any(v in user_q.lower() for v in ["viết", "làm", "soạn", "giải"])
    h_obj = any(o in user_q.lower() for o in ["hộ", "giùm", "giúp", "cho em", "cho mình", "mẫu", "liên hệ đi"])
    if (h_verb and h_obj) or "bài văn mẫu" in user_q.lower():
        return "👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết thay hay làm hộ em bất cứ đoạn văn nào. Việc ỷ lại sẽ giết chết tư duy của em. Cô chỉ gợi ý phương pháp, dẫn chứng hoặc lập dàn ý. Em hãy tự cầm bút lên và nháp thử suy nghĩ của mình trước đi!"

    # Gọi AI thực sự để chat
    history_text = "\n".join([f"{'HS' if r=='user' else 'GV'}: {m}" for r, m in chat_history[-4:]])
    prompt = f"""Đóng vai giáo viên Ngữ văn THPT xuất sắc, nghiêm khắc nhưng tận tâm. Bạn đang chat với học sinh để hướng dẫn làm bài nghị luận.
Đề bài: "{de_text}"
Vấn đề nghị luận: "{vdnl_chuan}"
Lịch sử chat gần nhất:
{history_text}
Câu hỏi hiện tại của học sinh: "{user_q}"

NGUYÊN TẮC TRẢ LỜI CỦA BẠN:
1. KHÔNG BAO GIỜ viết hộ, viết thành đoạn văn mẫu hoàn chỉnh cho học sinh chép.
2. TRẢ LỜI ĐÚNG TRỌNG TÂM CÂU HỎI. Nếu HS xin dẫn chứng, cung cấp 2 nhân vật có thật cụ thể và phân tích sâu sắc hành động của họ khớp với đề bài như thế nào. Không dùng dẫn chứng sáo rỗng.
3. Nếu HS hỏi cách lập ý, hãy cung cấp 3-5 gạch đầu dòng luận điểm CỤ THỂ, sâu sắc về nguyên nhân, biểu hiện, tác động của riêng đề bài này.
4. Xưng "Cô" và gọi "em". Trả lời ngắn gọn, khúc chiết, mang tính khơi gợi tư duy."""
    
    res = call_gemini_api(prompt)
    if res: 
        return res
    return "👩‍🏫 **Trợ lý Ngữ văn:** ⚠️ Hệ thống chưa kết nối não bộ AI. Thầy/cô vui lòng nhập mã Gemini API Key ở menu bên trái để kích hoạt tính năng vấn đáp chuyên sâu."

def ai_evaluate_strict_rubric(de_key, de_info, essay_text, image_obj=None):
    prompt = f"""Đóng vai giáo viên Ngữ văn THPT chấm thi CỰC KỲ KHẮT KHE, SOI MÓI TỪNG LỖI SAI. Chấm bài văn nghị luận sau theo chuẩn Rubric 7 tiêu chí (Thang 10).

LUẬT CHẤM ĐIỂM (BẮT BUỘC TUÂN THỦ 100%):
1. Bước nhảy điểm khắt khe: Chỉ cho 0.25, 0.5, 0.75, 1.0. 
2. Đánh giá THỰC CHẤT: Bài viết ngắn, lủng củng, ít luận điểm tuyệt đối KHÔNG ĐƯỢC QUÁ 6.0 điểm. 
3. YÊU CẦU BẮT BUỘC TRONG BẢNG: Cột "Nhận xét & Minh chứng", BẠN PHẢI COPY & DÁN (trong ngoặc kép "") chính xác câu văn ngô nghê, lủng củng, sáo rỗng hoặc sai kiến thức của học sinh từ bài làm để làm bằng chứng trừ điểm. Không được nhận xét chung chung.

Đề bài: "{de_key}" - {de_info.get('text', '')}
Bài làm của học sinh:
---
{essay_text if essay_text else '[Học sinh nộp ảnh bài viết tay, hãy đọc chữ trong ảnh để chấm]'}
---

TRẢ VỀ ĐÚNG ĐỊNH DẠNG MARKDOWN SAU:
### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN (CHẤM THỰC CHẤT)
| Tiêu chí | Điểm tối đa | Điểm đạt | Nhận xét & Trích dẫn lỗi trực tiếp từ bài |
|---|---|---|---|
| **1. Bố cục (Mở-Thân-Kết)** | 0.5 | [Điểm] | [Nhận xét + quote lỗi] |
| **2. Xác định VĐNL** | 0.5 | [Điểm] | [Nhận xét + quote lỗi] |
| **3. Giải thích khái niệm** | 1.0 | [Điểm] | [Nhận xét + quote lỗi] |
| **4. Hệ thống luận điểm** | 3.5 | [Điểm] | [Chỉ rõ HS thiếu ý nào, quote câu văn lập luận nông cạn] |
| **5. Dẫn chứng thực tế** | 2.5 | [Điểm] | [Chỉ rõ dẫn chứng bị sai/cũ/kể lể ở đâu, quote lại] |
| **6. Phản đề & Bài học** | 1.0 | [Điểm] | [Nhận xét + quote lỗi] |
| **7. Diễn đạt & Chính tả** | 1.0 | [Điểm] | [Quote chính xác từ/câu dùng sai, lủng củng] |

**📌 TỔNG ĐIỂM THỰC TẾ: [X]/10.0**

**📝 LỜI PHÊ CỦA GIÁO VIÊN (SẮC BÉN, THỰC TẾ):**
[Chỉ ra tử huyệt trong bài viết của học sinh, khuyên học sinh phải sửa ngay điều gì để không ảo tưởng sức mạnh]"""
    
    res = call_gemini_api(prompt, image_obj)
    if res: return res
    return "⚠️ Lỗi: Không thể chấm bài. Vui lòng nhập Gemini API Key ở menu trái."

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input("Nhập mã Gemini API Key để kết nối lõi AI:", type="password", value=st.session_state["gemini_api_key"])
    if api_key_input != st.session_state["gemini_api_key"]: st.session_state["gemini_api_key"] = api_key_input
    if st.session_state["gemini_api_key"]:
        st.success("✅ Đã kết nối AI chuyên sâu!")
    else:
        st.error("⚠️ Cần nhập API Key để dùng web!")
    
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC\n1. Xác định VĐNL\n2. Lập dàn ý & Chat AI\n3. Xưởng viết bài\n4. Chấm điểm khắt khe")

st.markdown("""<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div><p class="hero-subtitle">Ứng dụng AI phân tích sâu sắc, chấm điểm khắt khe, không bao giờ viết hộ</p></div>""", unsafe_allow_html=True)

tabs = st.tabs(["🌱 BƯỚC 1: TÌM HIỂU ĐỀ", "🧵 BƯỚC 2: TÌM Ý & CHAT AI", "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI", "📊 BƯỚC 4: CHẤM BÀI (RUBRIC)"])

with tabs[0]:
    tab_cb, tab_nc, tab_tu_nhap = st.tabs(["🟢 Đề Cơ Bản", "🔴 Đề Nâng Cao", "✏️ Nhập Đề Bài Riêng"])
    with tab_cb:
        col_cb1, col_cb2 = st.columns([1, 2])
        selected_cb = col_cb1.selectbox("Chọn đề Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="cb")
        col_cb2.info(db.DE_BAI_CO_BAN[selected_cb]["text"])
        if col_cb2.button("📌 Chọn đề này", key="b_cb"): 
            st.session_state["selected_de_key"], st.session_state["current_de_info"] = selected_cb, db.DE_BAI_CO_BAN[selected_cb]; st.rerun()
    with tab_nc:
        col_nc1, col_nc2 = st.columns([1, 2])
        selected_nc = col_nc1.selectbox("Chọn đề Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="nc")
        col_nc2.info(db.DE_BAI_NANG_CAO[selected_nc]["text"])
        if col_nc2.button("📌 Chọn đề này", key="b_nc"): 
            st.session_state["selected_de_key"], st.session_state["current_de_info"] = selected_nc, db.DE_BAI_NANG_CAO[selected_nc]; st.rerun()
    with tab_tu_nhap:
        custom_de = st.text_area("Nhập đề bài:", height=110)
        custom_vdnl = st.text_input("Vấn đề nghị luận là gì?")
        if st.button("🔍 AI Tạo khung định hướng Sắc bén", type="primary"):
            if not get_api_key(): st.error("⚠️ Cần nhập Gemini API Key để AI phân tích!")
            elif not custom_de.strip(): st.warning("Vui lòng nhập đề!")
            else:
                with st.spinner("Đang bóc tách từ khóa và lập dàn ý thực chất..."):
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {custom_de[:55]}..."
                    st.session_state["current_de_info"] = generate_custom_outline(custom_de.strip(), custom_vdnl.strip())
                    st.success("✅ Đã tạo xong Khung định hướng sâu sắc!")

    st.markdown("---")
    st.info(f"📌 **Đề đang chọn:** {st.session_state['selected_de_key']}\n\n*Nội dung:* {st.session_state['current_de_info'].get('text', '')}")

with tabs[1]:
    cur_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.15, 0.85], gap="large")
    with c_left:
        st.markdown("#### 🛠️ Khung định hướng phân tích sâu")
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            for itm in cur_info.get("explain_items", []): st.markdown(itm)
        with st.expander("💡 Thao tác 2: Bàn luận (Sâu sắc)", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                for a in q.get("y_tra_loi", []): st.markdown(a)
        with st.expander("📚 Thao tác 3: Dẫn chứng thực tiễn", expanded=True):
            for ev in cur_info.get("evidence", []):
                if isinstance(ev, dict): st.markdown(f"**👤 {ev.get('ten', '')}**: {ev.get('chi_tiet', '')} -> *{ev.get('y_nghia', '')}*")
        with st.expander("🔄 Thao tác 4: Phản đề", expanded=True):
            for c in cur_info.get("counter", []): st.markdown(c)
    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn (Chat Thông Minh)")
        chat_box = st.container(height=380, border=True)
        for role, msg in st.session_state["chat_history"]:
            chat_box.markdown(f"**{'🧑‍🎓 Em' if role=='user' else '👩‍🏫 Trợ lý'}:** {msg}")
            chat_box.markdown("---")
        u_q = st.text_area("Hỏi Trợ lý (Tuyệt đối không viết hộ):", height=80, key="chat_in")
        c1, c2 = st.columns([2,1])
        if c1.button("🚀 Gửi", type="primary", use_container_width=True):
            if not get_api_key(): st.error("⚠️ Vui lòng nhập API Key!")
            elif u_q.strip():
                st.session_state["chat_history"].append(("user", u_q.strip()))
                reply = ai_advisor_response(cur_info["text"], cur_info.get("vdnl_chuan", ""), u_q.strip(), st.session_state["chat_history"])
                st.session_state["chat_history"].append(("assistant", reply))
                st.rerun()
        if c2.button("🗑️ Xóa", use_container_width=True):
            st.session_state["chat_history"] = [("assistant", "Chào em! Cô sẵn sàng hướng dẫn, nhưng em tự viết nhé!")]
            st.rerun()

with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    write_mode = st.radio("Chọn hình thức nộp bài:", ["✍️ Gõ trực tiếp", "📷 Tải ảnh chụp viết tay (AI đọc chữ)"], horizontal=True)
    if write_mode == "✍️ Gõ trực tiếp":
        essay_input = st.text_area("Viết bài tại đây:", value=st.session_state.get("user_essay", ""), height=380)
        st.session_state["user_essay"] = essay_input
        if st.button("📊 Chấm Rubric Khắt Khe", type="primary"):
            if not get_api_key(): st.error("⚠️ Vui lòng nhập API Key để chấm điểm!")
            elif not essay_input.strip(): st.warning("Vui lòng nhập bài viết!")
            else:
                with st.spinner("AI đang soi từng câu chữ để trừ điểm..."):
                    st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(st.session_state["selected_de_key"], st.session_state["current_de_info"], essay_input.strip())
                    st.success("✅ Đã chấm xong! Xem kết quả ở Bước 4.")
    else:
        uploaded_img = st.file_uploader("Tải ảnh bài làm (Hỗ trợ Vision AI):", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric Khắt Khe", type="primary"):
                if not get_api_key(): st.error("⚠️ Vui lòng nhập API Key để đọc ảnh!")
                else:
                    with st.spinner("AI đang nhận diện chữ viết tay và vạch lá tìm sâu..."):
                        st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(st.session_state["selected_de_key"], st.session_state["current_de_info"], "", image_obj=img_obj)
                        st.success("✅ Đã chấm xong ảnh! Xem kết quả ở Bước 4.")

with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra Theo Rubric (Bắt Lỗi Bằng Dẫn Chứng)</div>', unsafe_allow_html=True)
    c_r1, c_r2 = st.columns([1, 1.35], gap="large")
    with c_r1:
        edited = st.text_area("Chỉnh sửa bài viết sau khi bị trừ điểm:", value=st.session_state.get("user_essay", ""), height=420)
        st.session_state["user_essay"] = edited
        if st.button("🔍 Nộp lại để chấm", type="primary"):
            with st.spinner("Đang chấm lại khắt khe..."):
                st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(st.session_state["selected_de_key"], st.session_state["current_de_info"], edited.strip())
    with c_r2:
        st.markdown("##### 📋 Bảng Điểm & Trích Dẫn Câu Văn Lỗi Của Em:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True): st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info("Chưa có bảng điểm. Hãy nộp bài ở Bước 3.")
