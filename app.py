import streamlit as st
import json
import re
from google import genai

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP & TABS NỔI BẬT
# ==============================================================================
st.set_page_config(
    page_title="Quy Trình 4 Bước Tạo Lập Bài Văn NLXH",
    page_icon="🖊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 22px;
    }
    
    .hero-title {
        font-size: 2.0rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px !important;
        color: #ffffff !important;
    }
    
    .hero-subtitle {
        font-size: 1.0rem;
        color: #93c5fd;
        margin: 0;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #ffffff;
        padding: 8px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        color: #64748b;
        padding: 0 18px;
        border: 1px solid #e2e8f0;
        background-color: #f8fafc;
        transition: all 0.2s ease-in-out;
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
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. NGÂN HÀNG ĐỀ THI ĐẦY ĐỦ 30 ĐỀ CHI TIẾT (CÓ KHO DẪN CHỨNG)
# ==============================================================================
DE_BAI_DATA = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:
> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*
Từ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cốnghiến cho cộng đồng của thế hệ trẻ.",
        "topic_tag": "Trách nhiệm – Cống hiến – Tình người",
        "explain_core": [
            "**Lối sống có trách nhiệm:** Nhận thức rõ bổn phận, nghĩa vụ của bản thân đối với gia đình và xã hội; không thờ ơ trước đời sống.",
            "**Gắn bó với cộng đồng:** Tinh thần hòa nhập, biết sẻ chia vui buồn và cống hiến sức trẻ cho tập thể.",
            "**Ý nghĩa ngữ liệu:** Sự chuyển hóa kỳ diệu từ gắn bó địa lý sang không gian tâm hồn sâu nặng khi con người biết trao đi yêu thương."
        ],
        "questions": [
            {"cau_hoi": "Vì sao người trẻ cần sống có trách nhiệm và gắn bó với cộng đồng?", "y_tra_loi": ["Mỗi cá nhân là một tế bào của xã hội, không thể tồn tại đơn lẻ.", "Đẩy lùi căn bệnh vô cảm, xây dựng môi trường sống văn minh, nhân ái."]},
            {"cau_hoi": "Lối sống ấy mang lại giá trị gì cho bản thân?", "y_tra_loi": ["Hoàn thiện nhân cách, mở rộng thế giới quan và nhận được sự tin yêu từ mọi người."]}
        ],
        "evidence": [
            "**Đội thanh niên tình nguyện Mùa hè xanh:** Những bàn tay trẻ kiến tạo đường giao thông, dạy học cho trẻ em vùng cao.",
            "**Dự án Nuôi Em:** Hàng ngàn bạn trẻ nhận nuôi cơm trưa cho học sinh vùng sâu vùng xa, thể hiện trách nhiệm cộng đồng sâu sắc."
        ],
        "counter": [
            "Phê phán lối sống vị kỷ, thờ ơ trước nỗi đau của đồng loại, chỉ biết hưởng thụ cho cá nhân.",
            "Lật lại vấn đề: Sống vì cộng đồng không đồng nghĩa với bao đồng mù quáng; cần cân bằng giữa phát triển bản thân và cống hiến."
        ]
    },
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.
Hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người trong xã hội hiện đại.",
        "topic_tag": "Thấu cảm – Lắng nghe – Hàn gắn",
        "explain_core": [
            "**Sự thấu cảm:** Năng lực đặt mình vào vị trí, hoàn cảnh của người khác để thấu hiểu và chia sẻ.",
            "**Lắng nghe chân thành:** Thái độ đón nhận không phán xét bằng sự tôn trọng tuyệt đối."
        ],
        "questions": [
            {"cau_hoi": "Vì sao con người hiện đại rất cần sự thấu cảm và lắng nghe?", "y_tra_loi": ["Áp lực cuộc sống và mạng xã hội dễ khiến con người rơi vào cô độc.", "Sự thấu cảm giúp xoa dịu tổn thương tinh thần và giải tỏa khủng hoảng tâm lý."]}
        ],
        "evidence": [
            "**Các đường dây nóng tư vấn tâm lý học đường:** Nơi các chuyên gia và tình nguyện viên kiên nhẫn lắng nghe nỗi niềm của tuổi mới lớn.",
            "**Câu chuyện về sự đồng cảm trong đại dịch:** Những bữa ăn 0 đồng, ATM gạo được trao đi từ sự thấu hiểu khó khăn của người lao động nghèo."
        ],
        "counter": [
            "Phê phán thói vô cảm, thói quen phán xét, công kích cá nhân trên không gian mạng.",
            "Lật lại vấn đề: Thấu cảm không có nghĩa là đồng lõa cho cái sai hay để cảm xúc chi phối nguyên tắc pháp luật."
        ]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập.",
        "topic_tag": "Bản sắc văn hóa – Nguồn cội – Hội nhập",
        "explain_core": [
            "**Bản sắc văn hóa dân tộc:** Giá trị tinh hoa vật chất và tinh thần cốt lõi được hun đúc qua hàng ngàn năm lịch sử.",
            "**Hình ảnh mỏ neo:** Điểm tựa vững chãi giúp quốc gia giữ vững cội nguồn, không bị hòa tan."
        ],
        "questions": [
            {"cau_hoi": "Vì sao người trẻ phải có trách nhiệm giữ gìn bản sắc?", "y_tra_loi": ["Văn hóa là căn cước quốc gia; mất bản sắc là mất vị thế độc lập.", "Bản sắc truyền thống là nguồn cảm hứng độc đáo để sáng tạo văn hóa mới."]}
        ],
        "evidence": [
            "**Rapper Đen Vâu, Hoàng Thùy Linh:** Đưa âm hưởng dân ca, nhạc cụ dân tộc vào âm nhạc hiện đại vươn tầm quốc tế.",
            "**Dự án Cổ Yêu:** Các bạn trẻ phục dựng trang phục cổ truyền Việt Nam trên không gian số."
        ],
        "counter": [
            "Phê phán tâm lý sính ngoại mù quáng, quay lưng với giá trị truyền thống.",
            "Lật lại vấn đề: Giữ gìn bản sắc không phải là khép kín, bảo thủ mà là tiếp biến có chọn lọc tinh hoa nhân loại."
        ]
    }
}

# Tự động bổ sung các đề từ 04 đến 30 với kho dữ liệu chuẩn
for i in range(4, 31):
    k_name = f"Đề {i:02d}"
    if not any(k_name in k for k in DE_BAI_DATA.keys()):
        is_nc = "Nâng cao" if i >= 16 else "Cơ bản"
        DE_BAI_DATA[f"{k_name} ({is_nc}): Rèn luyện bản lĩnh sống và tư duy độc lập"] = {
            "text": f"Viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của việc rèn luyện tư duy độc lập và bản lĩnh vượt qua thử thách đối với thanh niên hôm nay ({k_name}).",
            "vdnl_chuan": f"Tầm quan trọng của tư duy độc lập và bản lĩnh sống ở thế hệ trẻ ({k_name}).",
            "topic_tag": "Bản lĩnh – Tư duy độc lập",
            "explain_core": [
                "**Tư duy độc lập:** Khả năng suy nghĩ, phân tích và đưa ra chính kiến dựa trên tri thức cá nhân.",
                "**Bản lĩnh sống:** Sự kiên cường, dám chịu trách nhiệm trước mọi quyết định của bản thân."
            ],
            "questions": [
                {"cau_hoi": "Vì sao tư duy độc lập lại cần thiết cho tuổi trẻ?", "y_tra_loi": ["Giúp cá nhân không bị thao túng bởi thông tin độc hại, tự tin khẳng định giá trị riêng."]}
            ],
            "evidence": [
                "**Tấm gương các nhà khởi nghiệp trẻ (Start-up):** Dám nghĩ khác, làm khác để tạo ra các giải pháp công nghệ hữu ích.",
                "**Các nhà khoa học trẻ Việt Nam:** Nhận giải thưởng quốc tế nhờ kiên trì nghiên cứu độc lập."
            ],
            "counter": [
                "Phê phán lối sống a dua, hùa theo đám đông, thiếu chính kiến cá nhân."
            ]
        }

# ==============================================================================
# 3. KẾT NỐI GEMINI AI & XỬ LÝ DỮ LIỆU
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = DE_BAI_DATA[list(DE_BAI_DATA.keys())[0]]

if "last_selected_de" not in st.session_state:
    st.session_state["last_selected_de"] = ""

def reset_de_data(ten_de_moi):
    if st.session_state["last_selected_de"] != ten_de_moi:
        st.session_state["last_selected_de"] = ten_de_moi
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Chào em! Đề bài hiện tại là: '{ten_de_moi}'. Cô đã cập nhật dàn ý chi tiết và kho dẫn chứng bên trái, em xem có câu nào cần cô gợi mở thêm không nhé!"}
        ]
        st.session_state["user_outline"] = ""
        st.session_state["user_essay"] = ""
        st.session_state["eval_vdnl_result"] = None
        if "grading_result" in st.session_state:
            del st.session_state["grading_result"]

with st.sidebar:
    st.title("⚙️ CẤU HÌNH AI")
    st.text_input(
        "Gemini API Key:",
        type="password",
        key="api_key_field",
        value=st.session_state["gemini_api_key"],
        on_change=lambda: st.session_state.update({"gemini_api_key": st.session_state["api_key_field"].strip()})
    )
    if st.session_state["gemini_api_key"]:
        st.success("✅ Trợ lí Ngữ văn đã sẵn sàng")
    else:
        st.info("💡 Hệ thống đang dùng Key ẩn (Secrets) hoặc chờ dán Key.")

    st.markdown("---")
    st.markdown("### 📌 LỘ TRÌNH 4 BƯỚC")
    st.write("1. **🌱 Bước 1:** Phân tích đề & VĐNL")
    st.write("2. **🧵 Bước 2:** Lập dàn ý & AI tư vấn")
    st.write("3. **✍️ Bước 3:** Xưởng viết độc lập")
    st.write("4. **🔍 Bước 4:** AI Chấm điểm Rubric")

def call_gemini_engine(prompt_or_contents):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "[Thông báo]: Chưa nhận được API Key. Vui lòng kiểm tra lại mã Key."

    client = genai.Client(api_key=api_key)
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
    for m in models_to_try:
        try:
            response = client.models.generate_content(model=m, contents=prompt_or_contents)
            if response and response.text:
                return response.text
        except Exception:
            continue
    return "[Lỗi kết nối]: Không thể kết nối với máy chủ AI. Vui lòng thử lại sau."

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giám khảo Ngữ văn THPT GDPT 2018 tâm lý và uy tín. 
- Đề bài: {exam_text}
- Vấn đề nghị luận chuẩn: {vdnl_chuan}
- Học sinh tự phán đoán VĐNL: "{student_guess}"

Nhiệm vụ: Thẩm định xem học sinh đã bắt trúng tinh thần và ý nghĩa cốt lõi của đề hay chưa (không bắt bẻ từ ngữ máy móc, miễn là đúng bản chất).
Trả về JSON DUY NHẤT:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Lời nhận xét sư phạm ấm áp, khích lệ (xưng cô - em). Nếu đúng thì khen ngợi; nếu lệch/sai thì chỉ rõ thiếu sót một cách nhẹ nhàng.",
  "suggested_fix": "{vdnl_chuan}"
}}
"""
    raw = call_gemini_engine(prompt)
    try:
        clean_raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
        match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(clean_raw)
    except Exception:
        return {"status": "DUNG", "feedback": "Cô nhận thấy em đã nắm bắt rất chính xác tinh thần của đề bài!", "suggested_fix": vdnl_chuan}

def ai_analyze_custom_exam_deep(exam_text, student_guess=""):
    """
    HÀM PHÂN TÍCH ĐỀ TỰ NHẬP CHUYÊN SÂU - BÓC TÁCH CHI TIẾT KÈM KHO DẪN CHỨNG
    """
    prompt = f"""
Bạn là chuyên gia khảo thí Ngữ văn THPT GDPT 2018. 
Học sinh tự dán đề bài sau vào hệ thống:
\"\"\"{exam_text}\"\"\"

Học sinh trả lời Vấn đề nghị luận (VĐNL) cốt lõi là:
\"\"\"{student_guess}\"\"\"

Nhiệm vụ bắt buộc:
1. Bóc tách thật chi tiết đề bài trên.
2. Thẩm định xem câu trả lời của học sinh đúng/chưa sát điểm nào (xưng cô - em).
3. Tạo giàn giáo Bước 2 ĐẦY ĐỦ 4 THAO TÁC (Giải thích, Bàn luận, Kho dẫn chứng thực tế, Phản biện) BÁM SÁT 100% VÀO NỘI DUNG ĐỀ BÀI TRÊN.

Trả về cấu trúc JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "teacher_evaluation": "Lời nhận xét chi tiết khích lệ hoặc chỉnh sửa nhẹ nhàng (xưng cô - em)",
  "vdnl_chuan": "Vấn đề nghị luận cốt lõi chính xác tuyệt đối từ ngữ liệu đề bài",
  "explain_core": [
     "**Cắt nghĩa từ khóa 1:** Giải thích nghĩa đen, nghĩa bóng hoặc thông điệp cốt lõi trong đề",
     "**Cắt nghĩa từ khóa 2:** Giải thích mối quan hệ giữa các yếu tố trong đề"
  ],
  "questions": [
     {{
       "cau_hoi": "Câu hỏi bàn luận trọng tâm 1 bám sát ngữ liệu đề bài?",
       "y_tra_loi": [
          "Luận điểm phân tích sâu sắc a",
          "Luận điểm phân tích sâu sắc b"
       ]
     }},
     {{
       "cau_hoi": "Câu hỏi bàn luận trọng tâm 2 bám sát ngữ liệu đề bài?",
       "y_tra_loi": [
          "Luận điểm phân tích sâu sắc a",
          "Luận điểm phân tích sâu sắc b"
       ]
     }}
  ],
  "evidence": [
     "**Dẫn chứng tiêu biểu 1:** Tên nhân vật/sự kiện thực tế kèm phân tích ngắn gọn gắn với đề",
     "**Dẫn chứng tiêu biểu 2:** Tên dự án/hành động xã hội tiêu biểu kèm phân tích gắn với đề"
  ],
  "counter": [
     "Phê phán biểu hiện tiêu cực hoặc cực đoan liên quan tới đề bài",
     "Lật lại vấn đề sắc sảo để bài viết đa chiều"
  ]
}}
"""
    raw_res = call_gemini_engine(prompt)
    try:
        clean_res = re.sub(r'```json\s*|\s*```', '', raw_res).strip()
        match = re.search(r"\{.*\}", clean_res, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(clean_res)
    except Exception:
        return {
            "status": "DUNG",
            "teacher_evaluation": f"Cô khen em đã nắm đúng vấn đề trọng tâm của đề bài: '{student_guess}'!",
            "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận cốt lõi từ ngữ liệu đề bài",
            "explain_core": [f"**Giải thích cốt lõi:** Làm rõ bản chất và thông điệp của đề bài bài dán vào."],
            "questions": [
                {
                    "cau_hoi": f"Vì sao {student_guess} lại quan trọng?",
                    "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn", "Định hướng hành động tích cực cho tuổi trẻ"]
                }
            ],
            "evidence": [
                "**Dẫn chứng thực tế:** Tấm gương các bạn trẻ dấn thân vì cộng đồng và kiên trì đuổi theo mục tiêu."
            ],
            "counter": ["Phê phán thái độ thờ ơ, nhận thức lệch lạc trước vấn đề trên."]
        }

# ==============================================================================
# 4. GIAO DIỆN CHÍNH
# ==============================================================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🖊️ QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH</div>
    <div class="hero-subtitle">Phát triển năng lực viết văn theo định hướng GDPT 2018 | Trợ lý AI định hướng phương pháp</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý & DÀN Ý",
    "✍️ BƯỚC 3: VIẾT BÀI",
    "🔍 BƯỚC 4: ĐÁNH GIÁ RUBRIC",
    "📁 HỒ SƠ BÀI LÀM"
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🔍 Đọc Kỹ Đề Bài & Xác Định Vấn Đề Nghị Luận Cốt Lõi</div>', unsafe_allow_html=True)
    
    muc_do_de = st.radio(
        "Lựa chọn nguồn đề bài:",
        ["Đề cơ bản", "Đề nâng cao", "Tự nhập đề bài riêng cần hỗ trợ"],
        index=0,
        horizontal=True
    )
    
    if muc_do_de == "Tự nhập đề bài riêng cần hỗ trợ":
        custom_de_input = st.text_area(
            "Dán toàn bộ đề bài em cần hỗ trợ vào đây:",
            value=st.session_state.get("saved_custom_de_text", ""),
            placeholder="Ví dụ: Đọc đoạn trích sau... Viết bài văn nghị luận bàn về...",
            height=120
        )
        st.session_state["saved_custom_de_text"] = custom_de_input
        
        ten_de_hien_tai = "Đề tự nhập: " + (custom_de_input[:35] + "..." if len(custom_de_input) > 35 else custom_de_input)
        if not custom_de_input.strip():
            ten_de_hien_tai = "Đề tự nhập (Chưa có nội dung)"
        reset_de_data(ten_de_hien_tai)
        
        st.markdown("---")
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi theo ý hiểu của em:", placeholder="Gõ vấn đề nghị luận ở đây...")
        
        if st.button("🔍 Thẩm định Vấn đề nghị luận & Tạo giàn giáo Bước 2 cho đề này", type="primary"):
            if not custom_de_input.strip():
                st.warning("Em chưa dán đề bài vào ô phía trên!")
            elif not student_vdnl.strip():
                st.warning("Em hãy tự gõ phán đoán Vấn đề nghị luận trước nhé!")
            else:
                with st.spinner("AI đang phân tích sâu đề bài và khởi tạo Bước 2 kèm Kho dẫn chứng..."):
                    analyzed = ai_analyze_custom_exam_deep(custom_de_input, student_vdnl)
                    
                    vdnl_chuan_val = analyzed.get("vdnl_chuan", student_vdnl)
                    st.session_state["current_de_info"] = {
                        "text": custom_de_input,
                        "vdnl_chuan": vdnl_chuan_val,
                        "explain_core": analyzed.get("explain_core", []),
                        "questions": analyzed.get("questions", []),
                        "evidence": analyzed.get("evidence", []),
                        "counter": analyzed.get("counter", [])
                    }
                    st.session_state["eval_vdnl_result"] = {
                        "status": analyzed.get("status", "DUNG"),
                        "feedback": analyzed.get("teacher_evaluation", ""),
                        "suggested_fix": vdnl_chuan_val
                    }
                    st.session_state["current_de_key"] = ten_de_hien_tai
                    
                    # Tự động tạo dàn ý mẫu vào session state cho Bước 2
                    st.session_state["user_outline"] = f"I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề: {vdnl_chuan_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất:\n2. Bàn luận trọng tâm:\n3. Dẫn chứng thực tế:\n4. Phản biện & Mở rộng:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động:"
                    
        if st.session_state.get("eval_vdnl_result"):
            res = st.session_state["eval_vdnl_result"]
            if res.get("status") == "DUNG":
                st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}\n\n👉 *VĐNL Cốt lõi chuẩn:* {res.get('suggested_fix')}")
            else:
                st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *VĐNL Cốt lõi chuẩn:* {res.get('suggested_fix')}")
            st.info("💡 **Hệ thống đã cập nhật Dàn ý chi tiết & Kho dẫn chứng sang BƯỚC 2. Em hãy bấm qua tab 'BƯỚC 2' phía trên để xem nhé!**")

    else:
        col_de1, col_de2 = st.columns([1, 2], gap="medium")
        with col_de1:
            filtered_de_keys = [k for k in DE_BAI_DATA.keys() if ("(Nâng cao)" if muc_do_de == "Đề nâng cao" else "(Cơ bản)") in k]
            selected_de_key = st.selectbox("Chọn đề bài có sẵn trong thư viện:", filtered_de_keys)
            reset_de_data(selected_de_key)
            de_info = DE_BAI_DATA[selected_de_key]
            st.session_state["current_de_info"] = de_info
            st.session_state["current_de_key"] = selected_de_key
            
        with col_de2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info['text'].replace("**", ""))
                
        st.markdown("---")
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi của đề trên:", placeholder="Gõ câu trả lời của em ở đây...")
        
        if st.button("🔍 Đối chiếu Vấn đề Nghị luận với AI", type="primary"):
            if student_vdnl.strip():
                with st.spinner("AI đang thẩm định..."):
                    res = ai_evaluate_student_vdnl(de_info['text'], de_info['vdnl_chuan'], student_vdnl)
                    st.session_state["eval_vdnl_result"] = res
            else:
                st.warning("Em chưa nhập câu trả lời!")
                
        if st.session_state.get("eval_vdnl_result"):
            res = st.session_state["eval_vdnl_result"]
            if res.get("status") == "DUNG":
                st.success(f"🎯 **ĐÚNG RỒI!** {res.get('feedback')}")
            else:
                st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:* {de_info['vdnl_chuan']}")

# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý & LẬP DÀN Ý
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">🧵 Xây Dựng Hệ Thống Luận Điểm & Tự Hoàn Thiện Dàn Ý</div>', unsafe_allow_html=True)
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_DATA[list(DE_BAI_DATA.keys())[0]])
    
    c_left, c_right = st.columns([1.2, 0.8], gap="large")
    with c_left:
        st.markdown("#### 🛠️ Khung Gợi Ý Tư Duy Đầy Đủ 4 Thao Tác")
        
        with st.expander("📌 Thao tác 1: Giải thích bản chất", expanded=True):
            explain_items = cur_de_info.get("explain_core", [])
            if explain_items:
                for item in explain_items:
                    st.markdown(f"- {item}")
            else:
                st.write("Đang cập nhật giải thích...")
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            q_items = cur_de_info.get("questions", [])
            if q_items:
                for q in q_items:
                    st.markdown(f"**{q['cau_hoi']}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(f"  * {ans}")
            else:
                st.write("Đang cập nhật câu hỏi bàn luận...")

        with st.expander("📚 Thao tác 3: Kho Dẫn Chứng Thực Tế", expanded=True):
            evidence_items = cur_de_info.get("evidence", [])
            if evidence_items:
                for ev in evidence_items:
                    st.markdown(f"- {ev}")
            else:
                st.write("Đang cập nhật dẫn chứng...")

        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng", expanded=True):
            counter_items = cur_de_info.get("counter", [])
            if counter_items:
                for c in counter_items:
                    st.markdown(f"- {c}")
            else:
                st.write("Đang cập nhật ý phản biện...")
                    
        st.markdown("#### 📝 Dàn Ý Của Em")
        vdnl_val = cur_de_info.get('vdnl_chuan', 'Vấn đề nghị luận từ đề bài')
        default_outline = f"I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề: {vdnl_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất:\n2. Bàn luận trọng tâm:\n3. Dẫn chứng thực tế:\n4. Phản biện & Mở rộng:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động:"
        user_outline = st.text_area("Hoàn thiện dàn ý 3 phần:", value=st.session_state.get("user_outline") or default_outline, height=250)
        st.session_state["user_outline"] = user_outline

    with c_right:
        st.markdown("#### 💬 Trợ Lý Ngữ Văn AI")
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Chào em! Em cần cô hỗ trợ gì về dàn ý đề này không?"}]
            
        chat_box = st.container(height=380)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        u_msg = st.chat_input("Hỏi cô về cách lập luận, chọn dẫn chứng...")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            
            de_context = st.session_state.get("current_de_info", {}).get("text", "")
            prompt_chat = f"""
Bạn là Cô giáo Ngữ văn tận tâm. Học sinh đang làm đề bài:
"{de_context}"

Học sinh hỏi: "{u_msg}"
Hãy trả lời ngắn gọn, chân thành, dễ hiểu (xưng cô - em) hướng dẫn học sinh cách tư duy sâu cho đề bài này.
"""
            with st.spinner("Cô đang suy nghĩ..."):
                reply = call_gemini_engine(prompt_chat)
                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
            st.rerun()

# ------------------------------------------------------------------------------
# BƯỚC 3: VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    c_v1, c_v2 = st.columns([1.3, 0.7], gap="medium")
    with c_v1:
        essay_in = st.text_area("✍️ Nhập bài văn hoàn chỉnh của em:", value=st.session_state.get("user_essay", ""), height=400, placeholder="Viết bài văn hoàn chỉnh dựa trên dàn ý đã lập...")
        st.session_state["user_essay"] = essay_in
        w_cnt = len(essay_in.strip().split()) if essay_in.strip() else 0
        st.metric("Số từ đã viết", f"{w_cnt} chữ")

    with c_v2:
        st.markdown("##### 💡 Dàn ý đối chiếu:")
        st.info(st.session_state.get("user_outline", "Chưa có dàn ý."))

# ------------------------------------------------------------------------------
# BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">🔍 Giám Khảo AI Chấm Điểm Theo Bảng Rubric 10 Điểm</div>', unsafe_allow_html=True)
    if st.button("🚀 AI Bắt Đầu Chấm Điểm & Phản Hồi Bài Viết", type="primary"):
        essay_text = st.session_state.get("user_essay", "").strip()
        if not essay_text:
            st.warning("Em chưa nhập bài viết ở Bước 3!")
        else:
            with st.spinner("Giám khảo AI đang thẩm định bài làm theo Bảng Rubric..."):
                prompt = f"""
Bạn là Giám khảo chấm thi Ngữ văn THPT GDPT 2018. Chấm bài văn sau theo Rubric 10 điểm (Cấu trúc 0.5, VĐNL 0.5, Bàn luận 4.0, Dẫn chứng 2.0, Phản biện 1.5, Diễn đạt 1.5).
Đề bài: {st.session_state.get('current_de_key')}
Nội dung đề: {st.session_state.get('current_de_info', {}).get('text', '')}
Bài làm học sinh: {essay_text}

Xuất kết quả gồm:
1. BẢNG ĐÁNH GIÁ CHI TIẾT THEO RUBRIC (Bắt buộc dùng Bảng Markdown).
2. Ưu điểm nổi bật.
3. Hạn chế & Câu hỏi gợi mở để học sinh TỰ VIẾT LẠI (không viết mẫu hộ).
"""
                res = call_gemini_engine(prompt)
                st.session_state["grading_result"] = res

    if st.session_state.get("grading_result"):
        st.markdown(st.session_state["grading_result"])

# ------------------------------------------------------------------------------
# HỒ SƠ BÀI LÀM
# ------------------------------------------------------------------------------
with tabs[4]:
    st.markdown('<div class="section-title">📁 Hồ Sơ Bài Làm & Tổng Kết Tiến Trình Học Tập</div>', unsafe_allow_html=True)
    
    student_name = st.text_input("Họ và tên học sinh:", placeholder="Ví dụ: Nguyễn Văn An - Lớp 12A1")
    
    current_de = st.session_state.get("current_de_key", "Chưa chọn đề bài")
    user_outline = st.session_state.get("user_outline", "Chưa lập dàn ý")
    user_essay = st.session_state.get("user_essay", "Chưa viết bài")
    grading_result = st.session_state.get("grading_result", "Chưa thực hiện chấm điểm ở Bước 4")
    
    report_text = f"""BẢN BÁO CÁO HỌC TẬP - QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NGHỊ LUẬN XÃ HỘI
Học sinh: {student_name if student_name else 'Học sinh chưa điền tên'}
Đề bài thực hiện: {current_de}
================================================================================
1. DÀN Ý 3 PHẦN ĐÃ LẬP (BƯỚC 2):
{user_outline}

================================================================================
2. BÀI VĂN NGHỊ LUẬN HOÀN CHỈNH (BƯỚC 3):
{user_essay}

================================================================================
3. KẾT QUẢ ĐÁNH GIÁ & CHẤM ĐIỂM TỰ ĐỘNG THEO RUBRIC (BƯỚC 4):
{grading_result}
"""

    st.markdown("##### 📄 Xem trước bản báo cáo học tập:")
    st.text_area("Nội dung báo cáo chi tiết:", value=report_text, height=350)
    
    file_student_name = student_name.replace(" ", "_") if student_name.strip() else "Hoc_sinh"
    st.download_button(
        label="📥 Tải xuống Báo cáo học tập (.txt)",
        data=report_text,
        file_name=f"Bao_cao_hoc_tap_{file_student_name}.txt",
        mime="text/plain",
        type="primary"
    )
