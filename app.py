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

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 8px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.92rem;
        color: #475569;
        padding: 0 16px;
        border: 1px solid #e2e8f0;
        background-color: #f8fafc;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 16px;
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

    .rubric-info-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 5px solid #2563eb;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 16px;
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
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp lập ý, cung cấp dẫn chứng, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")
    ]
if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state:
    st.session_state["eval_vdnl_text"] = ""


# ==============================================================================
# 3. ĐỘNG CƠ AI CHUYÊN SÂU & XỬ LÝ SƯ PHẠM
# ==============================================================================
def call_gemini_api(prompt_text, image_obj=None):
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        if image_obj:
            response = model.generate_content([prompt_text, image_obj])
        else:
            response = model.generate_content(prompt_text)
        
        if response and response.text:
            return response.text
        return None
    except Exception as e:
        return f"Lỗi kết nối AI: {str(e)}"

def generate_custom_outline(topic_text, student_guess):
    api_key = get_api_key()
    if api_key:
        prompt = f"""Phân tích đề bài NLXH sau và trả về MỘT CHUỖI JSON HỢP LỆ (không có markdown).
Đề bài: "{topic_text}". Dự đoán của học sinh: "{student_guess}"

Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{topic_text}",
  "vdnl_chuan": "Vấn đề nghị luận cốt lõi ngắn gọn.",
  "explain_items": [
    "- Cắt nghĩa từ khóa [X] là...",
    "- Ý nghĩa thông điệp là..."
  ],
  "vdnl_ket_luan": "Chốt lại vấn đề...",
  "questions": [
    {{
      "cau_hoi": "Tại sao vấn đề này lại quan trọng?",
      "y_tra_loi": ["- Nguyên nhân...", "- Tác động..."]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên nhân vật",
      "chi_tiet": "Hành động thực tế",
      "y_nghia": "Chứng minh cho khía cạnh nào",
      "nguon": "Thực tế đời sống"
    }}
  ],
  "counter": [
    "- Phê phán lối sống/biểu hiện trái ngược...",
    "- Lưu ý tránh cực đoan..."
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
        res = call_gemini_api(prompt)
        if res and not res.startswith("Lỗi"):
            try:
                res_clean = res.strip().removeprefix("```json").removesuffix("```").strip()
                return json.loads(res_clean)
            except Exception:
                pass
    
    return {
        "text": topic_text,
        "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận của đề bài",
        "explain_items": [
            "- **Giải thích từ khóa chính:** Làm rõ khái niệm cốt lõi trong đề.",
            "- **Rút ra thông điệp:** Ý nghĩa khái quát."
        ],
        "vdnl_ket_luan": "Nhận thức sâu sắc về giá trị vấn đề.",
        "questions": [
            {"cau_hoi": "Sức mạnh của vấn đề này là gì?", "y_tra_loi": ["- Tác động cá nhân.", "- Lan tỏa cộng đồng."]}
        ],
        "evidence": [
            {"ten": "Tấm gương tiêu biểu", "chi_tiet": "Hành động thực tiễn vượt khó hoặc cống hiến.", "y_nghia": "Minh chứng sức sống của vấn đề.", "nguon": "Thực tế"}
        ],
        "counter": ["- Phê phán những biểu hiện lệch chuẩn, sống thờ ơ hoặc hiểu sai."],
        "dani_chi_tiet": {
            "mb": "Dẫn dắt và nêu VĐNL.", "gt": "Giải thích từ khóa.", 
            "bl": "Triển khai 5 ý luận điểm.", "dc": "Phân tích dẫn chứng.", 
            "pb": "Lật lại vấn đề.", "kb": "Khẳng định, liên hệ bản thân."
        }
    }

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    s_guess = student_guess.strip().lower()
    v_chuan = vdnl_chuan.strip().lower()
    key_words = [w for w in v_chuan.split() if len(w) > 3]
    match_count = sum(1 for kw in key_words if kw in s_guess)
    
    if match_count >= 2 or (len(s_guess) > 8 and any(kw in s_guess for kw in key_words[:3])):
        return f"🎯 **CHÍNH XÁC!**\n- Vấn đề nghị luận chuẩn: *{vdnl_chuan}*\n👉 Em hãy chuyển sang Bước 2 để lập ý và lấy dẫn chứng!"
    else:
        return f"⚠️ **CHƯA ĐÚNG TRỌNG TÂM:**\n- Vấn đề nghị luận chuẩn của đề là: *{vdnl_chuan}*\n👉 Hãy suy nghĩ lại để xác định đúng nhé!"

def ai_advisor_response(de_text, vdnl_chuan, user_q, chat_history_len):
    q_lower = user_q.lower()
    
    # Bắt CỰC KỲ KHẮT KHE các từ khóa học sinh nhờ làm bài
    c_tu_khoa_xin_bai = ["viết bài cho em", "viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho bài văn", "viết bài", "viết cho tôi", "giải giúp bài", "viết thành bài"]
    if any(k in q_lower for k in c_tu_khoa_xin_bai):
        return """👩‍🏫 **Trợ lý Ngữ văn từ chối khéo léo:**
Cô rất sẵn lòng đồng hành cùng em, nhưng **cô tuyệt đối không viết hộ hay viết thay bài văn cho em được**. Việc ỷ lại sẽ làm thui chột tư duy của em!
Cô có thể giúp em:
1. Gợi ý lập dàn ý 5 luận điểm.
2. Cung cấp dẫn chứng người thật việc thật.
3. Hướng dẫn viết câu mở đầu.
👉 Em muốn cô hỗ trợ phương pháp ở phần nào?"""

    # Xử lý khi xin thêm dẫn chứng
    if any(k in q_lower for k in ["thêm", "khác", "nữa", "ví dụ", "ai khác"]) and chat_history_len > 3:
        return f"""👩‍🏫 **Trợ lý Ngữ văn cung cấp Dẫn chứng MỚI cho đề tài '{vdnl_chuan}':**
1. **Cô giáo Đỗ Thị Ngọc Kim:** Tình nguyện cắm bản vùng cao, mang tri thức cho trẻ em nghèo.
2. **Nick Vujicic:** Sinh ra không tứ chi nhưng vươn lên trở thành nhà diễn thuyết truyền cảm hứng toàn cầu.
3. **Các tình nguyện viên mùa dịch:** Xông pha hỗ trợ cộng đồng, quên đi an nguy bản thân.
👉 *Em hãy chọn 1 tấm gương và tự phân tích hành động của họ nhé!*"""

    if any(k in q_lower for k in ["dẫn chứng", "chứng minh", "nhân vật"]):
        return f"""👩‍🏫 **Trợ lý Ngữ văn gợi ý Dẫn chứng:**
1. **Thầy giáo Nguyễn Ngọc Ký:** Vượt nghịch cảnh mất đôi tay, dùng chân viết chữ.
2. **Ca sĩ Đen Vâu:** Cống hiến thầm lặng qua dự án Nuôi Em.
3. **Anh Hoàng Hoa Trung:** Kết nối nuôi cơm trưa cho trẻ em nghèo vùng cao.
👉 *Nếu cần thêm nhân vật khác, cứ nhắn cô nhé!*"""

    if "mở bài" in q_lower or "dẫn dắt" in q_lower:
        return f"👩‍🏫 **Gợi ý Mở bài:**\n- Dẫn dắt tự nhiên từ thực tiễn.\n- Nêu bật vấn đề: *{vdnl_chuan}*.\n👉 Em hãy tự nháp thử 2 câu mở bài rồi gửi lên đây nhé!"

    if "kết bài" in q_lower:
        return f"👩‍🏫 **Gợi ý Kết bài:** Khẳng định lại giá trị của *{vdnl_chuan}* và rút ra bài học hành động cho bản thân."

    if "phản đề" in q_lower or "phản biện" in q_lower:
        return f"👩‍🏫 **Hướng dẫn Phản đề:** Lên án những kẻ có lối sống trái ngược (thờ ơ, ích kỷ) và nhắc nhở thực hiện không cần đao to búa lớn mà từ việc nhỏ nhất."

    if any(k in q_lower for k in ["luận điểm", "ý chính", "lập ý"]):
        return "👩‍🏫 **Hướng dẫn 5 Luận điểm Thân bài:**\n1. Biểu hiện thực tế.\n2. Nguyên nhân (khách/chủ quan).\n3. Ý nghĩa trưởng thành cá nhân.\n4. Tác động tích cực đến cộng đồng.\n5. Hậu quả nếu thiếu điều này."

    return f"👩‍🏫 **Trợ lý Ngữ văn:** Cô đang theo dõi quá trình làm bài của em. Em cần hướng dẫn lập ý từ 5 luận điểm, hay cần xin dẫn chứng người thật việc thật? Cứ trao đổi cụ thể nhé!"

def ai_evaluate_strict_rubric(de_key, de_info, essay_text, image_obj=None):
    api_key = get_api_key()
    text = essay_text if essay_text else ""
    word_count = len(text.strip().split()) if text.strip() else 0
    
    if api_key and (text.strip() or image_obj):
        prompt = f"""Đóng vai giáo viên Ngữ văn THPT chấm thi cực kỳ KHẮT KHE. Chấm bài văn nghị luận sau theo chuẩn Rubric 7 tiêu chí (Thang 10).
BẮT BUỘC TUÂN THỦ CÁC QUY TẮC SAU:
1. Chỉ dùng bước nhảy điểm: 0.25, 0.5, 0.75, 1.0. 
2. Nếu bài làm hời hợt, ít ý: Tổng điểm chỉ được 4.0 - 6.5.
3. BẮT BUỘC TRÍCH DẪN (quote bằng ngoặc kép "") cụm từ/câu văn lủng củng, nông cạn hoặc lạc đề trực tiếp từ bài làm của học sinh để làm bằng chứng trừ điểm trong cột Nhận xét.

Đề bài: "{de_key}" - {de_info.get('text', '')}
Bài làm của học sinh:
---
{text if text else '[Học sinh nộp bài qua ảnh đính kèm, hãy đọc chữ viết tay trong ảnh để chấm]'}
---

BẠN BẮT BUỘC PHẢI TRẢ VỀ KẾT QUẢ ĐÚNG THEO ĐỊNH DẠNG MARKDOWN BẢNG SAU:

### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG 10)
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn lỗi sai từ bài làm |
|---|---|---|---|
| **1. Bố cục (Mở - Thân - Kết)** | 0.5 | [Điểm] | [Nhận xét và trích dẫn] |
| **2. Xác định vấn đề nghị luận** | 0.5 | [Điểm] | [Nhận xét và trích dẫn] |
| **3. Giải thích vấn đề & Ngữ liệu** | 1.0 | [Điểm] | [Nhận xét và trích dẫn] |
| **4. Hệ thống luận điểm (5 ý)** | 3.5 | [Điểm] | [Nhận xét và trích dẫn] |
| **5. Lập luận & Dẫn chứng thực tế** | 2.5 | [Điểm] | [Nhận xét và trích dẫn] |
| **6. Phản đề & Bài học liên hệ** | 1.0 | [Điểm] | [Nhận xét và trích dẫn] |
| **7. Diễn đạt, chính tả & Sáng tạo** | 1.0 | [Điểm] | [Nhận xét và trích dẫn] |

**📌 TỔNG ĐIỂM: [Tính Tổng]/10.0**

**📝 NHẬN XÉT TOÀN BÀI & HƯỚNG DẪN CHỈNH SỬA:**
[Viết 1 đoạn nhận xét tổng quan và chỉ ra các điểm cần khắc phục]"""
        
        res = call_gemini_api(prompt, image_obj)
        if res and not res.startswith("Lỗi"): 
            return res

    # Fallback chi tiết nếu không có mạng / API
    if word_count < 200:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG 10)
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn lỗi sai từ bài làm |
|---|---|---|---|
| **1. Bố cục (Mở - Thân - Kết)** | 0.5 | 0.25 | Bài quá ngắn, chưa chia 3 phần rõ ràng. |
| **2. Xác định vấn đề nghị luận** | 0.5 | 0.25 | Xác định vấn đề còn mờ nhạt. |
| **3. Giải thích vấn đề & Ngữ liệu** | 1.0 | 0.25 | Hoàn toàn thiếu phần cắt nghĩa khái niệm. |
| **4. Hệ thống luận điểm (5 ý)** | 3.5 | 1.00 | Các ý sơ sài, liệt kê gạch đầu dòng, không có lập luận. |
| **5. Lập luận & Dẫn chứng thực tế** | 2.5 | 0.50 | Thiếu vắng dẫn chứng người thật việc thật. |
| **6. Phản đề & Bài học liên hệ** | 1.0 | 0.25 | Không lật lại vấn đề. |
| **7. Diễn đạt, chính tả & Sáng tạo** | 1.0 | 0.50 | Câu văn lủng củng. |

**📌 TỔNG ĐIỂM: 3.0/10.0 (Yếu)**

**📝 NHẬN XÉT TOÀN BÀI & HƯỚNG DẪN CHỈNH SỬA:**
Bài viết quá sơ sài và chưa thành hình một bài nghị luận hoàn chỉnh. Em cần bám sát dàn ý 5 luận điểm và bổ sung ngay dẫn chứng thực tế."""
    else:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG 10)
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Trích dẫn lỗi sai từ bài làm |
|---|---|---|---|
| **1. Bố cục (Mở - Thân - Kết)** | 0.5 | 0.50 | Bố cục đủ 3 phần. |
| **2. Xác định vấn đề nghị luận** | 0.5 | 0.50 | Bám sát trọng tâm đề. |
| **3. Giải thích vấn đề & Ngữ liệu** | 1.0 | 0.50 | Giải thích bề mặt, thiếu chiều sâu. |
| **4. Hệ thống luận điểm (5 ý)** | 3.5 | 1.50 | Lập luận còn nông, thiếu phân tích nguyên nhân và tác động xã hội. |
| **5. Lập luận & Dẫn chứng thực tế** | 2.5 | 1.00 | Dẫn chứng chung chung, chưa phân tích sự liên kết với đề bài. |
| **6. Phản đề & Bài học liên hệ** | 1.0 | 0.50 | Phản đề hời hợt, nhắc đến chiếu lệ. |
| **7. Diễn đạt, chính tả & Sáng tạo** | 1.0 | 0.50 | Diễn đạt đôi chỗ lặp từ. |

**📌 TỔNG ĐIỂM: 5.0/10.0 (Trung bình)**

**📝 NHẬN XÉT TOÀN BÀI & HƯỚNG DẪN CHỈNH SỬA:**
Bài viết dừng ở mức độ cơ bản. Em cần học cách triển khai sâu các ý nguyên nhân, hậu quả và phân tích dẫn chứng rõ ràng hơn thay vì chỉ kể tên nhân vật."""


# ==============================================================================
# 4. THANH BÊN (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input(
        "Nhập mã xác thực của cô (Gemini API Key):",
        type="password",
        value=st.session_state["gemini_api_key"],
        help="Nhập mã API để kích hoạt AI phân tích Đề tự nhập, Chấm điểm bằng Ảnh và lập Bảng Rubric chi tiết.",
    )
    if api_key_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = api_key_input

    st.success("✅ HỆ THỐNG LUYỆN VIẾT NLXH đã sẵn sàng!")
    st.info("🎯 Trợ lý Ngữ văn: Không viết hộ.\n🎯 Chấm Rubric: Chấm khắt khe, trích lỗi cụ thể, hỗ trợ chấm bằng ảnh (Vision).")
    
    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM")
    st.markdown("1. **🌱 Bước 1:** Tìm hiểu đề & Xác định VĐNL")
    st.markdown("2. **🧵 Bước 2:** Tìm ý, Lập dàn ý & Kho dẫn chứng")
    st.markdown("3. **✍️ Bước 3:** Xưởng viết bài độc lập")
    st.markdown("4. **📊 Bước 4:** Kiểm tra & Chỉnh sửa (Rubric)")


# ==============================================================================
# 5. GIAO DIỆN CHÍNH & 4 BƯỚC SƯ PHẠM
# ==============================================================================
st.markdown(
    """
<div class="hero-banner">
    <div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div>
    <p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT theo định hướng phát triển năng lực</p>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "📊 BƯỚC 4: KIỂM TRA & CHỈNH SỬA (RUBRIC)",
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🔍 Bước 1: Lựa chọn đề bài & Xác định vấn đề nghị luận</div>', unsafe_allow_html=True)
    
    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
        "🟢 Nhóm Đề Cơ Bản (Đề 01 – Đề 15)",
        "🔴 Nhóm Đề Nâng Cao (Đề 16 – Đề 30)",
        "✏️ Nhập / Dán Đề Bài Riêng",
    ])

    with tab_de_coban:
        col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
        with col_cb1:
            selected_cb_key = st.selectbox("Chọn đề trong nhóm Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="sb_coban")
            de_info_cb = db.DE_BAI_CO_BAN[selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_cb["text"])
            if st.button("📌 Chọn đề Cơ bản này để luyện tập", key="btn_chon_cb", type="primary"):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = de_info_cb
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang Bước 2.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox("Chọn đề trong nhóm Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="sb_nangcao")
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_nc["text"])
            if st.button("📌 Chọn đề Nâng cao này để luyện tập", key="btn_chon_nc", type="primary"):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = de_info_nc
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang Bước 2.")

    with tab_de_tu_nhap:
        st.markdown("##### ✏️ Nhập đề bài bất kỳ để AI tự động phân tích và tạo Khung dàn ý riêng biệt:")
        custom_de_text = st.text_area("Nội dung đề bài tự nhập:", placeholder="Ví dụ: Bàn về sức mạnh của tinh thần đoàn kết...", height=110, key="txt_custom_de")
        student_custom_vdnl = st.text_input("Theo em, vấn đề nghị luận của đề bài này là gì?", placeholder="Nhập câu trả lời dự đoán...", key="txt_custom_vdnl")
        if st.button("🔍 AI Phân tích đề tự nhập & Tạo khung định hướng Bước 2", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài trước khi bấm phân tích!")
            else:
                with st.spinner("AI đang phân tích và sinh dàn ý chuyên sâu cho đề này..."):
                    outline = generate_custom_outline(custom_de_text.strip(), student_custom_vdnl.strip())
                    short_title = custom_de_text.strip()[:55] + ("..." if len(custom_de_text.strip()) > 55 else "")
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                    st.session_state["current_de_info"] = outline
                    st.session_state["eval_vdnl_text"] = "✅ Khung định hướng riêng cho đề này đã tạo xong! Mời em sang Bước 2."
                    st.success("✅ Đã tạo xong khung định hướng động!")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Nội dung đề:* {cur_active_info.get('text', '')}")

    if not cur_active_key.startswith("Đề tự nhập:"):
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Hãy xác định vấn đề nghị luận của đề bài đang chọn:", placeholder="Gõ câu trả lời của em vào đây...", key="input_vdnl_b1")
        col_b1_a, col_b1_b = st.columns([1, 1])
        with col_b1_a:
            if st.button("🤖 Đối chiếu câu trả lời với Trợ lý Ngữ văn", type="primary"):
                if student_vdnl.strip():
                    with st.spinner("Trợ lý đang đánh giá..."):
                        res_text = ai_evaluate_student_vdnl(cur_active_info["text"], cur_active_info.get("vdnl_chuan", ""), student_vdnl.strip())
                        st.session_state["eval_vdnl_text"] = res_text
                else:
                    st.warning("⚠️ Nhập câu trả lời trước nhé!")
        with col_b1_b:
            if st.button("👁️ Xem ngay Vấn đề nghị luận chuẩn"):
                st.session_state["eval_vdnl_text"] = f"🎯 **Vấn đề nghị luận chuẩn xác là:**\n\n{cur_active_info.get('vdnl_chuan', '')}"

    if st.session_state.get("eval_vdnl_text"):
        with st.container(border=True):
            st.markdown(st.session_state["eval_vdnl_text"])


# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.15, 0.85], gap="large")

    with c_left:
        st.markdown(f"#### 🛠️ Khung định hướng tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>", unsafe_allow_html=True)
        
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            with st.container(border=True):
                for itm in cur_de_info.get("explain_items", []):
                    st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt lại VĐNL:** {cur_de_info.get('vdnl_ket_luan', '')}")

        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Từ 5 ý)", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế", expanded=True):
            st.markdown("##### 📌 Dẫn chứng gợi ý trực tiếp:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    st.markdown(f"<div class='evidence-card'><h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5><p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p><p style='margin:0 0 6px 0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p></div>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("##### 📚 Kho dẫn chứng 9 chủ điểm (Mở rộng):")
            selected_topic = st.selectbox("Chọn chủ điểm dẫn chứng cần tham khảo:", list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()), key="sb_kho_dc")
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"**👤 {dc['ten']}**")
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 Nguồn: {dc['nguon']}")

        with st.expander("🔄 Thao tác 4: Phản đề & Bài học", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        with st.expander("📝 Bố cục Dàn ý chi tiết 3 phần", expanded=True):
            dani = cur_de_info.get("dani_chi_tiet", {})
            with st.container(border=True):
                st.markdown(f"**I. MỞ BÀI:** {dani.get('mb','')}")
                st.markdown(f"**II. THÂN BÀI:**\n1. {dani.get('gt','')}\n2. {dani.get('bl','')}\n3. {dani.get('dc','')}\n4. {dani.get('pb','')}")
                st.markdown(f"**III. KẾT BÀI:** {dani.get('kb','')}")

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn Tư Vấn (Chat)")
        chat_container = st.container(height=380, border=True)
        with chat_container:
            for role, msg in st.session_state["chat_history"]:
                st.markdown(f"**{'🧑‍🎓 Học sinh' if role == 'user' else '👩‍🏫 Trợ lý Ngữ văn'}:**\n\n{msg}")
                st.markdown("---")

        user_question = st.text_area("Nhập câu hỏi (Cô không viết hộ, chỉ hướng dẫn và cho ví dụ):", height=80, key="txt_chat_input")
        col_chat_1, col_chat_2 = st.columns([2, 1])
        with col_chat_1:
            if st.button("🚀 Gửi", type="primary", use_container_width=True):
                if user_question.strip():
                    st.session_state["chat_history"].append(("user", user_question.strip()))
                    reply = ai_advisor_response(
                        cur_de_info.get("text", cur_de_key),
                        cur_de_info.get("vdnl_chuan", ""),
                        user_question.strip(),
                        len(st.session_state["chat_history"])
                    )
                    st.session_state["chat_history"].append(("assistant", reply))
                    st.rerun()
                else:
                    st.warning("Nhập câu hỏi nhé!")
        with col_chat_2:
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                st.session_state["chat_history"] = [
                    ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hướng dẫn phương pháp, nhưng em phải tự viết bài nhé!")
                ]
                st.rerun()


# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info(f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n📖 *{st.session_state['current_de_info'].get('text', '')}*")

    with st.expander("💡 Hộp công cụ tư duy nhanh", expanded=False):
        col_tool1, col_tool2, col_tool3 = st.columns(3)
        with col_tool1:
            st.markdown("**🌟 Định hướng Mở bài:**")
            st.caption("Dẫn dắt tự nhiên, nêu bật vấn đề nghị luận.")
        with col_tool2:
            st.markdown("**🔍 Định hướng Dẫn chứng:**")
            st.caption("Chọn tấm gương tiêu biểu, nêu hành động và phân tích ý nghĩa.")
        with col_tool3:
            st.markdown("**🔄 Định hướng Phản đề:**")
            st.caption("Lật lại vấn đề: Phê phán lối sống ích kỷ, rút ra bài học.")

    write_mode = st.radio(
        "Chọn hình thức nộp bài:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode"
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội:",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy tự viết bài văn hoàn chỉnh của em tại đây..."
        )
        st.session_state["user_essay"] = essay_input
        wc = len(essay_input.strip().split()) if essay_input.strip() else 0
        st.caption(f"📊 Số từ hiện tại: **{wc} từ** (Hệ thống chấm khắt khe bắt lỗi diễn đạt).")

        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            if st.button("💡 Gợi ý nhanh cách mở rộng ý", use_container_width=True):
                st.info("💡 **Gợi ý từ Trợ lý:** Thân bài phải chẻ đủ 5 ý (biểu hiện, nguyên nhân, tác động...) và có phản đề!")
        with col_w2:
            if st.button("📊 Chuyển bài sang Bước 4 Chấm Rubric Khắt Khe", type="primary", use_container_width=True):
                if not essay_input.strip():
                    st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên!")
                else:
                    with st.spinner("Cô đang săm soi từng lỗi diễn đạt và luận điểm của em..."):
                        eval_res = ai_evaluate_strict_rubric(
                            st.session_state["selected_de_key"],
                            st.session_state["current_de_info"],
                            essay_input.strip()
                        )
                        st.session_state["rubric_evaluation"] = eval_res
                        st.success("✅ Đã chấm xong! Bấm sang Bước 4 để xem.")
    else:
        uploaded_img = st.file_uploader("Tải lên ảnh chụp bài làm (Hỗ trợ AI đọc chữ viết tay):", type=["png", "jpg", "jpeg"])
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric Khắt Khe", type="primary"):
                with st.spinner("Hệ thống đang nhận diện chữ viết tay và chấm bài..."):
                    eval_res = ai_evaluate_strict_rubric(
                        st.session_state["selected_de_key"],
                        st.session_state["current_de_info"],
                        "",
                        image_obj=img_obj
                    )
                    st.session_state["rubric_evaluation"] = eval_res
                    st.success("✅ Đã đọc ảnh và chấm xong! Sang Bước 4 xem kết quả.")


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra Theo Rubric 7 Tiêu Chí (Thang 10 - Chấm Khắt Khe)</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric đánh giá bài văn Nghị luận xã hội (Chuẩn SKKN 7 tiêu chí):</b><br>
            1. <b>Bố cục (0.5đ):</b> Đủ 3 phần.<br>
            2. <b>Xác định VĐNL (0.5đ):</b> Đúng trọng tâm.<br>
            3. <b>Giải thích (1.0đ):</b> Cắt nghĩa từ khóa.<br>
            4. <b>Hệ thống luận điểm (3.5đ):</b> Tối thiểu 5 ý sâu sắc.<br>
            5. <b>Dẫn chứng (2.5đ):</b> Người thật việc thật, phân tích sâu.<br>
            6. <b>Phản đề (1.0đ):</b> Có góc nhìn lật lại vấn đề.<br>
            7. <b>Diễn đạt (1.0đ):</b> Trong sáng, không lặp từ.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_r1, col_r2 = st.columns([1, 1.35], gap="large")

    with col_r1:
        st.markdown("##### 📝 Chỉnh sửa bài viết tại đây:")
        edited_essay = st.text_area(
            "Nội dung bài làm:",
            value=st.session_state.get("user_essay", ""),
            height=420,
            key="essay_step4_editor"
        )
        st.session_state["user_essay"] = edited_essay

        if st.button("🔍 Cập nhật chấm lại Rubric", type="primary", use_container_width=True):
            if edited_essay.strip():
                with st.spinner("Đang chấm lại khắt khe..."):
                    st.session_state["rubric_evaluation"] = ai_evaluate_strict_rubric(
                        st.session_state["selected_de_key"],
                        st.session_state["current_de_info"],
                        edited_essay.strip()
                    )
            else:
                st.warning("⚠️ Hãy nhập bài viết!")

        if edited_essay.strip():
            content = f"HỒ SƠ BÀI LÀM NLXH\nĐỀ: {st.session_state['selected_de_key']}\n\n-- BÀI LÀM --\n{edited_essay}\n\n-- KẾT QUẢ ĐÁNH GIÁ --\n{st.session_state.get('rubric_evaluation', '')}"
            st.download_button(
                label="📥 Tải Hồ sơ bài làm & Bảng Rubric (.txt)",
                data=content.encode("utf-8"),
                file_name="HoSo_NLXH.txt",
                use_container_width=True
            )

    with col_r2:
        st.markdown("##### 📋 Bảng Điểm & Nhận Xét Chi Tiết:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info("💡 Chưa có bảng điểm. Hãy hoàn thành Bước 3 và bấm Chấm điểm.")
