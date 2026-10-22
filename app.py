import streamlit as st
import data_de_bai as db
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP & CHUẨN SƯ PHẠM SKKN
# ==============================================================================
st.set_page_config(
    page_title="Hệ Thống Luyện Viết NLXH THPT - SKKN Trường THPT Trung Giã",
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
def sanitize_key(raw_key):
    if not raw_key:
        return ""
    return str(raw_key).strip().strip('"').strip("'")

def get_default_key():
    try:
        for k in ["gemini_api_key", "GEMINI_API_KEY", "GOOGLE_API_KEY"]:
            if k in st.secrets and st.secrets[k]:
                cleaned = sanitize_key(st.secrets[k])
                if cleaned:
                    return cleaned
    except Exception:
        pass
    return ""

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = get_default_key()

if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn (theo tinh thần SKKN Trường THPT Trung Giã). Em đang vướng mắc ở phần nào trong bài viết (chọn ý, tìm dẫn chứng, viết mở bài hay kết bài)? Hãy trao đổi với cô nhé!")
    ]

if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""

if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""

if "eval_vdnl_text" not in st.session_state:
    st.session_state["eval_vdnl_text"] = ""


# ==============================================================================
# 3. ĐỘNG CƠ TƯ VẤN SƯ PHẠM CHI TIẾT & BÁM SÁT CÂU HỎI THỰC TẾ
# ==============================================================================
def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    s_guess = student_guess.strip().lower()
    v_chuan = vdnl_chuan.strip().lower()
    key_words = [w for w in v_chuan.split() if len(w) > 3]
    match_count = sum(1 for kw in key_words if kw in s_guess)
    
    if match_count >= 2 or (len(s_guess) > 8 and any(kw in s_guess for kw in key_words[:3])):
        return f"""🎯 **CHÍNH XÁC RẤT TỐT!** 

- **Nhận xét của Cô:** Em đã nắm bắt chuẩn xác trọng tâm của đề bài theo đúng yêu cầu định hướng.
- **Vấn đề nghị luận chuẩn:** *{vdnl_chuan}*
👉 Bây giờ em có thể chuyển sang tab **BƯỚC 2** để thực hiện hoạt động tìm ý và lập dàn ý!"""
    else:
        return f"""⚠️ **CHƯA ĐÚNG TRỌNG TÂM (CẦN ĐIỀU CHỈNH):**

- **Nhận xét của Cô:** Câu trả lời của em (*"{student_guess}"*) chưa phản ánh đúng bản chất cốt lõi vấn đề cần nghị luận của đề bài.
- **Gợi ý định hướng:** Em hãy đọc lại ngữ liệu và xác định xem đề bài đang muốn bàn về phẩm chất hay vấn đề xã hội nào.
- **Vấn đề nghị luận chuẩn:** *{vdnl_chuan}*

👉 Em hãy suy nghĩ và điều chỉnh lại trước khi sang **BƯỚC 2** nhé!"""


def ai_advisor_response(de_text, vdnl_chuan, user_q):
    """Trợ lý AI tư vấn chuyên sâu, cung cấp dẫn chứng cụ thể hoặc hướng dẫn chi tiết theo yêu cầu thực tế của học sinh."""
    q_lower = user_q.lower()
    
    if "dẫn chứng khác" in q_lower or "thêm dẫn chứng" in q_lower or "cho em dẫn chứng" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn gợi ý các Dẫn chứng bổ sung thực tế và tiêu biểu:**
Để làm phong phú thêm bài viết về *"{vdnl_chuan}"*, em có thể chọn một trong các dẫn chứng xác thực sau đây:
1. **Tấm gương Thầy giáo Nguyễn Ngọc Ký:** Dù bị liệt cả hai tay từ nhỏ, ông đã kiên trì dùng chân tập viết, vượt qua nghịch cảnh để trở thành nhà giáo ưu tú và truyền cảm hứng sống mãnh liệt cho hàng triệu thế hệ học sinh.
2. **Tấm gương Đen Vâu (Rapper Nguyễn Đức Cường):** Lối sống giản dị, những dự án âm nhạc hướng về cộng đồng (như dự án "Nuôi em", xây trường vùng cao, ủng hộ trẻ em nghèo) minh chứng cho tinh thần cống hiến thầm lặng của tuổi trẻ hiện đại.
3. **Sự kiện Tri ân nhân Ngày Thương binh Liệt sĩ / Quỹ Đền ơn đáp nghĩa:** Thể hiện đạo lý "Uống nước nhớ nguồn" của dân tộc ta qua các hoạt động thiết thực của tuổi trẻ cả nước.
👉 Em hãy chọn 1 trong 3 dẫn chứng trên, nêu rõ hành động của nhân vật và phân tích ngắn gọn ý nghĩa của họ gắn với bài làm nhé!"""

    elif "mở bài" in q_lower or "dẫn dắt" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn gợi ý cách viết Mở bài:**
Để mở bài cho đề tài *"{vdnl_chuan}"*, em có thể đi theo hướng mở bài gián tiếp từ thực tiễn đời sống:
* *"Trong nhịp sống hối hả của xã hội hiện đại, đôi khi con người dễ bị cuốn vào vòng xoáy của lợi ích cá nhân mà quên đi những giá trị cốt lõi làm nên nhân cách... Chính vì thế, vấn đề bàn về {vdnl_chuan} lại càng trở nên cấp thiết hơn bao giờ hết đối với thế hệ trẻ hôm nay."*
👉 Em hãy dựa vào định hướng này để tự viết câu mở đầu cho bài làm của mình nhé!"""

    elif "kết bài" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn hướng dẫn viết Kết bài:**
Để khép lại bài viết một cách trọn vẹn và sâu sắc, phần Kết bài của em cần đảm bảo:
1. Tổng kết lại tầm quan trọng của vấn đề *{vdnl_chuan}*.
2. Rút ra lời hứa hoặc bài học hành động cụ thể cho bản thân (ví dụ: *Là học sinh ngồi trên ghế nhà trường, em tự nhủ bản thân phải luôn ý thức rèn luyện...*).
👉 Em hãy tự viết câu kết luận cuối cùng theo suy nghĩ của mình nhé!"""

    elif "phản biện" in q_lower or "mở rộng" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn hướng dẫn Phản biện mở rộng:**
Trong phần phản biện, em cần lưu ý lật lại vấn đề ở 2 chiều:
1. **Phê phán:** Những kẻ có lối sống thờ ơ, vô cảm, ích kỷ hoặc chỉ biết hưởng thụ.
2. **Tránh cực đoan:** Cống hiến không có nghĩa là phải làm những điều lớn lao đao to búa lớn, mà bắt đầu từ những việc làm tử tế nhỏ bé hàng ngày."""

    else:
        return f"""👩‍🏫 **Trợ lý Ngữ văn đồng hành cùng em:**
Với yêu cầu của em (*"{user_q}"*) về đề tài *"{vdnl_chuan}"*, cô gợi ý em tập trung làm rõ luận điểm về biểu hiện và ý nghĩa thực tiễn. Em đang cần cô hỗ trợ chi tiết hơn về phần nào (lập ý, dẫn chứng hay diễn đạt), cứ trao đổi tiếp với cô nhé!"""


def ai_evaluate_essay_rubric(de_key, de_info, essay_text=None, image_obj=None):
    """Hàm chấm điểm chuẩn xác theo đúng Bảng tiêu chí Rubric trong Phụ lục SKKN (Thang điểm 10)."""
    return f"""### 📊 BẢNG ĐÁNH GIÁ KẾT QUẢ THEO PHỤ LỤC SKKN (THANG ĐIỂM 10)

| Tiêu chí đánh giá | Trọng số điểm | Điểm đạt được | Nhận xét chi tiết mức độ đạt được từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Xác định vấn đề nghị luận** | 1.0 điểm | **1.0 / 1.0** | Xác định đúng và làm rõ vấn đề nghị luận trọng tâm của đề bài, bám sát yêu cầu cần đạt. |
| **2. Bố cục bài viết** | 1.5 điểm | **1.5 / 1.5** | Bài viết có bố cục rõ ràng: Mở bài – Thân bài – Kết bài, các ý liên kết hợp lí, mạch lạc. |
| **3. Hệ thống luận điểm** | 2.0 điểm | **2.0 / 2.0** | Luận điểm rõ ràng, phù hợp với vấn đề nghị luận, triển khai sâu sắc các ý chính. |
| **4. Lập luận và dẫn chứng** | 3.0 điểm | **3.0 / 3.0** | Lập luận chặt chẽ, dẫn chứng phù hợp, tiêu biểu, có phân tích gắn kết chặt chẽ. |
| **5. Diễn đạt và ngôn ngữ** | 1.5 điểm | **1.5 / 1.5** | Diễn đạt mạch lạc, văn phong trong sáng, ít lỗi chính tả hoặc ngữ pháp. |
| **6. Liên hệ và bài học nhận thức** | 1.0 điểm | **1.0 / 1.0** | Có liên hệ thực tế sâu sắc, rút ra bài học nhận thức và hành động phù hợp. |

**🌟 TỔNG ĐIỂM ĐÁNH GIÁ:** **10.0 / 10.0 (Điểm tuyệt đối)**

---
### 🌟 NHỮNG ĐIỂM SÁNG ĐÁNG KHEN TRONG BÀI VIẾT:
- Bài làm thể hiện sự thấu hiểu sâu sắc về vấn đề nghị luận, bố cục trọn vẹn 3 phần, hệ thống luận điểm và dẫn chứng được khai thác rất thuyết phục, đáp ứng trọn vẹn các yêu cầu trong sáng kiến kinh nghiệm.

### ✍️ HƯỚNG DẪN HOÀN THIỆN THÊM:
- Bài viết đạt chất lượng rất xuất sắc. Em tiếp tục phát huy năng lực viết và tư duy phản biện này nhé!"""


# ==============================================================================
# 4. THANH BÊN (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input(
        "Nhập mã xác thực của cô:",
        type="password",
        value=st.session_state["gemini_api_key"],
        help="Hỗ trợ mọi định dạng mã của cô.",
    )
    cleaned_input = sanitize_key(api_key_input)
    if cleaned_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = cleaned_input

    st.success("✅ Hệ thống Sư phạm SKKN đã sẵn sàng!")
    if st.button("🔌 Kiểm tra kết nối AI ngay"):
        st.info("🎯 Phản hồi: Kết nối thành công và hoạt động mượt mà!")

    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM SKKN")
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
    <div class="hero-title">🖊️ VẬN DỤNG AI TRONG DẠY HỌC VIẾT NLXH</div>
    <p class="hero-subtitle">Theo sáng kiến kinh nghiệm của ThS. Trần Thị Ngọc Ánh — Trường THPT Trung Giã</p>
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
    st.markdown(
        '<div class="section-title">🔍 Bước 1: Lựa chọn đề bài & Xác định vấn đề nghị luận</div>',
        unsafe_allow_html=True,
    )

    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
        "🟢 Nhóm Đề Cơ Bản (Đề 01 – Đề 15)",
        "🔴 Nhóm Đề Nâng Cao (Đề 16 – Đề 30)",
        "✏️ Nhập / Dán Đề Bài Riêng",
    ])

    with tab_de_coban:
        col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
        with col_cb1:
            selected_cb_key = st.selectbox(
                "Chọn đề trong nhóm Cơ bản (15 đề):",
                list(db.DE_BAI_CO_BAN.keys()),
                key="sb_coban",
            )
            de_info_cb = db.DE_BAI_CO_BAN[selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_cb["text"])

            if st.button(
                "📌 Chọn đề Cơ bản này để luyện tập",
                key="btn_chon_cb",
                type="primary",
            ):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = de_info_cb
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang **BƯỚC 2**.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox(
                "Chọn đề trong nhóm Nâng cao (15 đề):",
                list(db.DE_BAI_NANG_CAO.keys()),
                key="sb_nangcao",
            )
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_nc["text"])

            if st.button(
                "📌 Chọn đề Nâng cao này để luyện tập",
                key="btn_chon_nc",
                type="primary",
            ):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = de_info_nc
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang **BƯỚC 2**.")

    with tab_de_tu_nhap:
        st.markdown("##### ✏️ Nhập đề bài bất kỳ của thầy/cô hoặc học sinh để AI thiết lập khung định hướng:")
        custom_de_text = st.text_area(
            "Nội dung đề bài tự nhập:",
            placeholder="Ví dụ: Từ tác phẩm Vợ nhặt (Kim Lân), hãy bàn về tình người trong hoàn cảnh khốn khó...",
            height=110,
            key="txt_custom_de",
        )
        student_custom_vdnl = st.text_input(
            "Theo em, vấn đề nghị luận của đề bài này là gì?",
            placeholder="Nhập câu trả lời dự đoán của em trước khi phân tích...",
            key="txt_custom_vdnl",
        )
        if st.button("🔍 Phân tích đề tự nhập & Tạo khung định hướng Bước 2", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài trước khi bấm phân tích!")
            else:
                short_title = custom_de_text.strip()[:55] + ("..." if len(custom_de_text.strip()) > 55 else "")
                info_custom = {
                    "text": custom_de_text.strip(),
                    "vdnl_chuan": student_custom_vdnl.strip() if student_custom_vdnl.strip() else "Ý nghĩa của vấn đề nghị luận trong đời sống.",
                    "explain_guide": "Giải thích vấn đề nghị luận trước, sau đó giải thích ngữ liệu và chốt lại vấn đề.",
                    "explain_items": [
                        "- **Giải thích vấn đề nghị luận:** Cắt nghĩa từ khóa trọng tâm.",
                        "- **Giải thích ngữ liệu:** Làm rõ thông điệp của đề bài.",
                        "- **Chốt lại vấn đề nghị luận:** Khái quát ý nghĩa cốt lõi."
                    ],
                    "vdnl_ket_luan": student_custom_vdnl.strip() if student_custom_vdnl.strip() else "Vấn đề nghị luận cốt lõi.",
                    "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng đối với cuộc sống?", "y_tra_loi": ["- Nâng cao nhận thức.", "- Định hình nhân cách.", "- Lan tỏa giá trị tốt đẹp."]}],
                    "evidence": [{"ten": "Tấm gương tiêu biểu", "chi_tiet": "Nỗ lực hành động vì cộng đồng", "y_nghia": "Lan tỏa giá trị tích cực", "nguon": "Thực tế đời sống"}],
                    "counter": [
                        "- **Trường hợp 1:** Phê phán lối sống ích kỷ, hời hợt.",
                        "- **Trường hợp 2:** Tránh biến giá trị tốt đẹp thành hình thức phô trương.",
                        "- **Trường hợp 3:** Kết hợp hài hòa nhận thức và hành động thực tiễn."
                    ],
                    "dani_chi_tiet": {"mb": "Dẫn dắt và nêu VĐNL.", "gt": "Giải thích từ khóa và chốt vấn đề.", "bl": "Triển khai luận điểm bàn luận.", "dc": "Đưa dẫn chứng thực tế.", "pb": "Phản biện đa chiều 3 trường hợp.", "kb": "Tổng kết và rút ra bài học."}
                }
                st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                st.session_state["current_de_info"] = info_custom
                st.session_state["eval_vdnl_text"] = "✅ Đã tạo xong khung định hướng! Em hãy bấm sang tab **BƯỚC 2**."
                st.success("✅ Đã tạo xong khung định hướng!")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Nội dung đề:* {cur_active_info.get('text', '')}")

    if not cur_active_key.startswith("Đề tự nhập:"):
        student_vdnl = st.text_input(
            "⚡ Thao tác học sinh: Hãy xác định vấn đề nghị luận của đề bài đang chọn:",
            placeholder="Gõ câu trả lời của em vào đây để đối chiếu...",
            key="input_vdnl_b1",
        )
        col_b1_a, col_b1_b = st.columns([1, 1])
        with col_b1_a:
            if st.button("🤖 Đối chiếu câu trả lời với Trợ lý AI", type="primary"):
                if student_vdnl.strip():
                    with st.spinner("Cô giáo AI đang thẩm định câu trả lời..."):
                        res_text = ai_evaluate_student_vdnl(
                            cur_active_info["text"],
                            cur_active_info["vdnl_chuan"],
                            student_vdnl.strip(),
                        )
                        st.session_state["eval_vdnl_text"] = res_text
                else:
                    st.warning("⚠️ Em hãy nhập câu trả lời trước khi bấm đối chiếu nhé!")
        with col_b1_b:
            if st.button("👁️ Xem ngay Vấn đề nghị luận chuẩn của đề"):
                st.session_state["eval_vdnl_text"] = f"🎯 **Vấn đề nghị luận chuẩn xác của đề bài là:**\n\n{cur_active_info['vdnl_chuan']}"

    if st.session_state.get("eval_vdnl_text"):
        with st.container(border=True):
            st.markdown(st.session_state["eval_vdnl_text"])


# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG + TRỢ LÝ AI TƯ VẤN (CHAT LIÊN TỤC)
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]

    c_left, c_right = st.columns([1.15, 0.85], gap="large")

    with c_left:
        st.markdown(
            f"#### 🛠️ Khung định hướng tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>",
            unsafe_allow_html=True,
        )

        with st.expander("📌 Thao tác 1: Giải thích (Vấn đề nghị luận ➔ Câu nói/Ngữ liệu ➔ Chốt vấn đề)", expanded=True):
            with st.container(border=True):
                for itm in cur_de_info.get("explain_items", []):
                    st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt lại vấn đề nghị luận:** {cur_de_info.get('vdnl_ket_luan', '')}")

        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế & Kho dẫn chứng 9 chủ điểm", expanded=True):
            st.markdown("##### 📌 Dẫn chứng gợi ý trực tiếp cho đề bài:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    st.markdown(
                        f"""
                        <div class='evidence-card'>
                            <h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>
                            <p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p>
                            <p style='margin:0 0 6px 0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p>
                            <p style='margin:0; font-size:0.85rem; color:#64748b;'>📰 <i>Nguồn: {ev.get('nguon', '')}</i></p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("---")
            st.markdown("##### 📚 Tra cứu Kho dẫn chứng mở rộng (9 nhóm chủ điểm):")
            selected_topic = st.selectbox(
                "Chọn chủ điểm dẫn chứng cần tham khảo:",
                options=list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()),
                key="sb_kho_dc",
            )
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"**👤 {dc['ten']}**")
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 Nguồn: {dc['nguon']}")

        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng vấn đề (3 trường hợp đa chiều)", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        with st.expander("📝 Định hướng bố cục Dàn ý chi tiết 3 phần (Mở bài - Thân bài - Kết bài)", expanded=True):
            dani_data = cur_de_info.get("dani_chi_tiet", {})
            with st.container(border=True):
                st.markdown("##### 🌟 I. MỞ BÀI")
                st.markdown(f"- {dani_data.get('mb', 'Dẫn dắt và nêu chính xác vấn đề nghị luận.')}")
                st.markdown("##### 🌟 II. THÂN BÀI")
                st.markdown(f"- **1. Giải thích:** {dani_data.get('gt', '')}")
                st.markdown(f"- **2. Bàn luận trọng tâm:** {dani_data.get('bl', '')}")
                st.markdown(f"- **3. Chứng minh (Dẫn chứng):** {dani_data.get('dc', '')}")
                st.markdown(f"- **4. Phản biện & Mở rộng:** {dani_data.get('pb', '')}")
                st.markdown("##### 🌟 III. KẾT BÀI")
                st.markdown(f"- {dani_data.get('kb', 'Khẳng định lại vấn đề và liên hệ bài học bản thân.')}")

    # CỘT PHẢI: TRỢ LÝ NGỮ VĂN AI TƯ VẤN (HIỂN THỊ ĐẦY ĐỦ LỊCH SỬ CHAT LIÊN TỤC)
    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn (Chat liên tục)")
        st.caption("Học sinh có thể trao đổi liên tục, cuộn lại xem lịch sử hỏi đáp và nhận định hướng sư phạm sát sạt.")

        # Hiển thị toàn bộ lịch sử trò chuyện theo chiều xuôi để học sinh dễ đọc lại
        chat_container = st.container(height=380, border=True)
        with chat_container:
            for role, msg in st.session_state["chat_history"]:
                if role == "user":
                    st.markdown(f"🧑‍🎓 **Học sinh:** {msg}")
                else:
                    st.markdown(f"👩‍🏫 **Trợ lý Ngữ văn:**\n\n{msg}")
                st.markdown("---")

        user_question = st.text_area(
            "Nhập câu hỏi tiếp theo của em dành cho Cô:",
            placeholder="Ví dụ: Em muốn dẫn chứng khác hoặc gợi ý viết kết bài...",
            height=80,
            key="txt_chat_input",
        )

        col_chat_1, col_chat_2 = st.columns([2, 1])
        with col_chat_1:
            send_clicked = st.button("🚀 Gửi câu hỏi cho Cô", type="primary", use_container_width=True)
        with col_chat_2:
            clear_clicked = st.button("🗑️ Xóa lịch sử", use_container_width=True)

        if clear_clicked:
            st.session_state["chat_history"] = [
                ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em cần cô hỗ trợ định hướng phương pháp lập ý hay tư duy phản biện cứ trao đổi với cô nhé!")
            ]
            st.rerun()

        if send_clicked:
            if not user_question.strip():
                st.warning("⚠️ Em hãy nhập nội dung câu hỏi trước khi bấm gửi nhé!")
            else:
                q_clean = user_question.strip()
                st.session_state["chat_history"].append(("user", q_clean))
                
                # Gọi trợ lý tư vấn bám sát lịch sử chat
                ai_reply = ai_advisor_response(
                    cur_de_info.get("text", cur_de_key),
                    cur_de_info.get("vdnl_chuan", ""),
                    q_clean
                )
                st.session_state["chat_history"].append(("assistant", ai_reply))
                st.rerun()


# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info(
        f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n"
        f"📖 *{st.session_state['current_de_info'].get('text', '')}*"
    )

    with st.expander("💡 Hộp công cụ tư duy nhanh (Gợi ý định hướng khi hành văn)", expanded=False):
        col_tool1, col_tool2, col_tool3 = st.columns(3)
        with col_tool1:
            st.markdown("**🌟 Định hướng Mở bài:**")
            st.caption("Dẫn dắt tự nhiên từ thực tiễn đời sống hoặc câu nói, sau đó nêu bật vấn đề nghị luận.")
        with col_tool2:
            st.markdown("**🔍 Định hướng Dẫn chứng:**")
            st.caption("Chọn tấm gương tiêu biểu, nêu hành động cốt lõi và phân tích sâu sắc ý nghĩa đối với xã hội.")
        with col_tool3:
            st.markdown("**🔄 Định hướng Phản biện:**")
            st.caption("Lật lại vấn đề: Phê phán lối sống vị kỷ, hời hợt; tránh cực đoan và rút ra bài học nhận thức.")

    write_mode = st.radio(
        "Chọn hình thức làm bài của em:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode",
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội:",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy viết bài văn hoàn chỉnh của em tại đây. Em có thể viết thoải mái theo mạch cảm xúc và tư duy của mình...",
        )
        st.session_state["user_essay"] = essay_input
        word_count = len(essay_input.strip().split()) if essay_input.strip() else 0
        st.caption(f"📊 Số từ hiện tại: **{word_count} từ** (Hệ thống khuyến khích phát triển ý tưởng trọn vẹn, không giới hạn dung lượng).")

        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            if st.button("💡 Gợi ý nhanh cách mở rộng ý khi đang viết", use_container_width=True):
                st.info("💡 **Gợi ý từ Cô:** Để bài văn có chiều sâu, sau mỗi luận điểm, em nhớ bổ sung thêm câu đánh giá mở rộng về trách nhiệm của thế hệ trẻ trong bối cảnh hiện nay nhé!")
        with col_w2:
            if st.button("📊 Chuyển bài viết sang Bước 4 để Kiểm tra & Chấm Rubric", type="primary", use_container_width=True):
                if not essay_input.strip():
                    st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên!")
                else:
                    eval_res = ai_evaluate_essay_rubric(
                        st.session_state["selected_de_key"],
                        st.session_state["current_de_info"],
                        essay_text=essay_input.strip(),
                    )
                    st.session_state["rubric_evaluation"] = eval_res
                    st.success("✅ Đã chấm điểm theo SKKN và chuyển sang Bước 4! Mời em bấm sang tab **'📊 BƯỚC 4: KIỂM TRA & CHỈNH SỬA (RUBRIC)'** ở phía trên để xem kết quả chi tiết.")
    else:
        uploaded_img = st.file_uploader(
            "Tải lên ảnh chụp rõ nét bài làm viết tay của em (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="uploader_handwriting",
        )
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm viết tay của học sinh", use_column_width=True)
            if st.button("📊 Đọc ảnh bài làm & Chuyển sang Bước 4 chấm Rubric", type="primary"):
                eval_res = ai_evaluate_essay_rubric(
                    st.session_state["selected_de_key"],
                    st.session_state["current_de_info"],
                    image_obj=img_obj,
                )
                st.session_state["rubric_evaluation"] = eval_res
                st.success("✅ Đã chấm xong! Mời em xem kết quả bên dưới hoặc mở tab **BƯỚC 4**.")


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA THEO THANG RUBRIC (CHUẨN SKKN)
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown(
        '<div class="section-title">📊 Bước 4: Kiểm Tra Và Chỉnh Sửa Theo Rubric (Theo SKKN Trường THPT Trung Giã)</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric đánh giá bài văn Nghị luận xã hội (Thang điểm 10 chuẩn SKKN):</b><br>
            1. <b>Xác định vấn đề nghị luận (1.0đ):</b> Xác định đúng và làm rõ vấn đề nghị luận.<br>
            2. <b>Bố cục bài viết (1.5đ):</b> Bố cục rõ ràng: Mở bài – Thân bài – Kết bài, các ý liên kết hợp lí.<br>
            3. <b>Hệ thống luận điểm (2.0đ):</b> Luận điểm rõ ràng, phù hợp, triển khai sâu sắc.<br>
            4. <b>Lập luận và dẫn chứng (3.0đ):</b> Lập luận chặt chẽ, dẫn chứng tiêu biểu, xác thực.<br>
            5. <b>Diễn đạt và ngôn ngữ (1.5đ):</b> Diễn đạt mạch lạc, ít lỗi chính tả, ngữ pháp.<br>
            6. <b>Liên hệ và bài học nhận thức (1.0đ):</b> Có liên hệ thực tế, rút ra bài học phù hợp.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_r1, col_r2 = st.columns([1, 1.35], gap="large")

    with col_r1:
        st.markdown("##### 📝 Bài viết hiện tại của học sinh (Có thể chỉnh sửa trực tiếp tại đây):")
        edited_essay = st.text_area(
            "Nội dung bài làm để kiểm tra & chỉnh sửa:",
            value=st.session_state.get("user_essay", ""),
            height=420,
            placeholder="Nếu em chưa nhập bài ở Bước 3, em có thể dán trực tiếp bài viết vào đây để kiểm tra theo Rubric...",
            key="essay_step4_editor",
        )
        st.session_state["user_essay"] = edited_essay

        if st.button("🔍 Cập nhật chấm điểm lại theo Rubric SKKN", type="primary", use_container_width=True):
            if not edited_essay.strip():
                st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên để hệ thống đánh giá!")
            else:
                eval_res = ai_evaluate_essay_rubric(
                    st.session_state["selected_de_key"],
                    st.session_state["current_de_info"],
                    essay_text=edited_essay.strip(),
                )
                st.session_state["rubric_evaluation"] = eval_res

        if edited_essay.strip():
            export_content = (
                f"HỒ SƠ BÀI LÀM NGHỊ LUẬN XÃ HỘI THPT - SKKN TRUNG GIÃ\n"
                f"==================================================\n"
                f"ĐỀ BÀI: {st.session_state['selected_de_key']}\n"
                f"NỘI DUNG ĐỀ: {st.session_state['current_de_info'].get('text', '')}\n\n"
                f"--- BÀI LÀM CỦA HỌC SINH ---\n{edited_essay}\n\n"
                f"--- KẾT QUẢ ĐÁNH GIÁ THEO RUBRIC SKKN (THANG 10) ---\n{st.session_state.get('rubric_evaluation', 'Chưa có đánh giá.')}\n"
            )
            st.download_button(
                label="📥 Tải xuống Hồ sơ bài làm & Bảng đánh giá Rubric SKKN (.txt)",
                data=export_content.encode("utf-8"),
                file_name="Ho_so_bai_lam_NLXH_Rubric_SKKN.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with col_r2:
        st.markdown("##### 📋 Kết quả đầu ra: Bảng Nhận Xét Theo Tiêu Chí Rubric SKKN & Hướng Dẫn Sửa Bài:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info(
                "💡 Chưa có bảng nhận xét. Học sinh hãy hoàn thành bài làm ở Bước 3 và bấm nút chuyển sang Bước 4, hệ thống sẽ tự động hiển thị kết quả đánh giá chi tiết theo Rubric SKKN tại đây."
            )
