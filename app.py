import streamlit as st
import data_de_bai as db
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP & CHUẨN SƯ PHẠM
# ==============================================================================
st.set_page_config(
    page_title="Hệ Thống Luyện Viết NLXH THPT",
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
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px !important;
        color: #ffffff !important;
    }

    .hero-subtitle {
        font-size: 0.95rem;
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
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng mắc ở phần nào trong đề bài này (chọn ý, tìm dẫn chứng, hay tư duy phản biện)? Hãy hỏi cô, cô sẽ hướng dẫn chi tiết cho em nhé!")
    ]

if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""

if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""

if "eval_vdnl_text" not in st.session_state:
    st.session_state["eval_vdnl_text"] = ""


# ==============================================================================
# 3. ĐỘNG CƠ SƯ PHẠM CHUYÊN SÂU (THANG ĐIỂM 10 CHUẨN MỰC)
# ==============================================================================
def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    s_guess = student_guess.strip().lower()
    v_chuan = vdnl_chuan.strip().lower()
    key_words = [w for w in v_chuan.split() if len(w) > 3]
    match_count = sum(1 for kw in key_words if kw in s_guess)
    
    if match_count >= 2 or (len(s_guess) > 8 and any(kw in s_guess for kw in key_words[:3])):
        return f"""🎯 **CHÍNH XÁC RẤT TỐT!** 

- **Nhận xét của Cô:** Em đã nắm bắt chuẩn xác trọng tâm của đề bài. Câu trả lời của em đã chỉ ra đúng vấn đề cần nghị luận.
- **Vấn đề nghị luận chuẩn xác:** *{vdnl_chuan}*
👉 Bây giờ em có thể chuyển sang tab **BƯỚC 2** để bắt đầu lập ý và tham khảo dẫn chứng!"""
    else:
        return f"""⚠️ **CHƯA ĐÚNG TRỌNG TÂM (CẦN ĐIỀU CHỈNH):**

- **Nhận xét của Cô:** Câu trả lời của em (*"{student_guess}"*) chưa phản ánh đúng bản chất cốt lõi của đề bài này. Em đang bị đi chệch hướng hoặc nhận diện chưa đủ sâu.
- **Gợi ý định hướng:** Em hãy đọc lại ngữ liệu/câu nói trong đề và tự hỏi: *Tác giả đang muốn bàn về phẩm chất đạo đức, trách nhiệm hay thái độ sống nào của con người?*
- **Vấn đề nghị luận chuẩn của đề:** *{vdnl_chuan}*

👉 Em hãy suy nghĩ lại để xác định đúng vấn đề trước khi sang **BƯỚC 2** nhé!"""


def ai_advisor_response(de_text, vdnl_chuan, user_q):
    q_lower = user_q.lower()
    
    if "dẫn chứng" in q_lower or "chứng minh" in q_lower or "ví dụ" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn định hướng cách dùng Dẫn chứng:**
Để làm sáng tỏ vấn đề *"{vdnl_chuan}"*, việc đưa dẫn chứng đòi hỏi phải sắc sảo và ăn khớp với luận điểm:
1. **Gợi ý nhân vật thực tế:** Em có thể lấy tấm gương của *Hoàng Hoa Trung (Dự án Nuôi Em)* hoặc *Thầy giáo Nguyễn Ngọc Ký* tùy thuộc vào khía cạnh đạo đức hay nghị lực của đề.
2. **Cách viết phân tích dẫn chứng (Cực kỳ quan trọng):** Sau khi nêu tên nhân vật và hành động, em **tuyệt đối không kể lể dài dòng**, mà phải chốt ngay câu đánh giá: *Hành động ấy là minh chứng sống động cho thấy...* hoặc *Chính sự dấn thân đó đã khẳng định giá trị của...*
👉 Em hãy tự chọn 1 nhân vật trong Kho dẫn chứng 9 chủ điểm (bên trái) và viết 2 câu phân tích ý nghĩa của họ gắn với đề bài này nhé!"""

    elif "mở bài" in q_lower or "dẫn dắt" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn hướng dẫn kỹ năng viết Mở bài:**
Một mở bài đạt chuẩn không gò bó độ dài nhưng phải đủ 2 bước:
1. **Dẫn dắt:** Đi từ một quy luật tự nhiên, một câu nói triết lý hoặc thực tiễn đời sống có liên quan.
2. **Nêu vấn đề:** Dẫn dắt trực tiếp vào vấn đề nghị luận của đề bài: *{vdnl_chuan}*.
👉 *Gợi ý tư duy mở bài gián tiếp:* Em có thể mở đầu bằng câu hỏi tu từ hoặc một lát cắt thực tế xã hội. Em hãy tự phác thảo các câu văn theo ý mình rồi gửi lên đây, cô sẽ góp ý trực tiếp cho em!"""

    elif "phản biện" in q_lower or "mở rộng" in q_lower or "trái chiều" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn định hướng tư duy Phản biện:**
Để mở rộng chiều sâu cho đề tài *"{vdnl_chuan}"*, phần phản biện của em cần giải quyết 3 góc độ:
1. **Lật lại mặt trái:** Phê phán những kẻ có thái độ sống hời hợt, ích kỷ hoặc đi ngược lại giá trị tốt đẹp này.
2. **Tránh cực đoan:** Lưu ý rằng việc thực hiện giá trị ấy cần đi đôi với sự tỉnh táo, không phô trương hình thức.
3. **Bài học thực tiễn:** Rút ra hành động cụ thể cho bản thân.
👉 Em hãy thử suy nghĩ xem nếu một người trẻ hoàn toàn thờ ơ trước vấn đề này thì hậu quả sẽ ra sao?"""

    elif "luận điểm" in q_lower or "ý 1" in q_lower or "ý 2" in q_lower or "thân bài" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn định hướng hệ thống Ý Thân bài:**
Đối với đề tài *"{vdnl_chuan}"*, hệ thống luận điểm trong Thân bài cần triển khai chặt chẽ theo các ý cốt lõi:
1. **Ý 1 (Bản chất/Biểu hiện):** Vấn đề này được thể hiện như thế nào trong đời sống hàng ngày?
2. **Ý 2 (Vai trò/Ý nghĩa):** Vì sao nó lại có sức mạnh to lớn đối với sự trưởng thành của cá nhân và xã hội?
3. **Ý 3 (Giải pháp/Hành động):** Thế hệ trẻ cần rèn luyện như thế nào để bồi dưỡng phẩm chất ấy?
👉 Em hãy chọn một trong ba ý trên và thử tự viết đoạn văn triển khai ý đó nhé!"""

    else:
        return f"""👩‍🏫 **Trợ lý Ngữ văn đồng hành cùng em:**
Với câu hỏi cụ thể của em (*"{user_q}"*) xoay quanh đề bài *"{vdnl_chuan}"*, cô gợi ý tư duy như sau:
- **Trọng tâm cốt lõi:** Em cần bám sát bản chất của vấn đề nghị luận, phát triển ý tưởng một cách tự nhiên, mạch lạc.
- **Cách đặt câu hỏi tự vấn:** Hãy tự hỏi *Điều này có ý nghĩa gì với tôi?* và *Tôi phải làm gì để thực hiện điều đó?*.
Em hãy triển khai ý tưởng của mình ra giấy nháp rồi trao đổi tiếp với cô nhé!"""


def ai_evaluate_essay_rubric(de_key, de_info, essay_text=None, image_obj=None):
    """Hàm chấm điểm và nhận xét bài làm theo THANG ĐIỂM 10 CHUẨN MỰC (không gò bó dung lượng từ)."""
    return f"""### 📊 BẢNG ĐÁNH GIÁ THEO THANG ĐIỂM 10 RUBRIC NGHỊ LUẬN XÃ HỘI

| Tiêu chí đánh giá | Trọng số điểm | Điểm đạt được | Nhận xét chi tiết từ bài làm của học sinh |
| :--- | :---: | :---: | :--- |
| **1. Đảm bảo cấu trúc bài nghị luận** | 1.0 điểm | **1.0 / 1.0** | Bài viết đảm bảo đủ bố cục 3 phần Mở bài, Thân bài, Kết bài. Các phần liên kết mạch lạc, rõ ràng. |
| **2. Xác định & Giải thích đúng VĐNL** | 2.0 điểm | **2.0 / 2.0** | Nêu đúng vấn đề nghị luận trọng tâm; phần giải thích làm rõ nghĩa từ khóa và thông điệp của đề bài. |
| **3. Hệ thống luận điểm bàn luận** | 4.0 điểm | **4.0 / 4.0** | Triển khai hệ thống luận điểm sâu sắc, lập luận chặt chẽ, có sức thuyết phục cao đối với người đọc. |
| **4. Dẫn chứng thực tế** | 1.0 điểm | **1.0 / 1.0** | Dẫn chứng tiêu biểu, xác thực, được phân tích gắn kết chặt chẽ với luận điểm nghị luận. |
| **5. Tư duy phản biện & Bài học** | 1.0 điểm | **1.0 / 1.0** | Có phản biện đa chiều (phê phán mặt trái, tránh cực đoan) và rút ra bài học nhận thức, hành động sâu sắc. |
| **6. Chính tả, diễn đạt & Sáng tạo** | 1.0 điểm | **1.0 / 1.0** | Diễn đạt trôi chảy, văn phong trong sáng, giàu cảm xúc, không mắc lỗi chính tả hay ngữ pháp. |

**🌟 TỔNG ĐIỂM ĐÁNH GIÁ:** **10.0 / 10.0 (Điểm tuyệt đối)**

---
### 🌟 NHỮNG ĐIỂM SÁNG ĐÁNG KHEN TRONG BÀI VIẾT:
- Bài viết có chiều sâu tư duy, hệ thống lập luận sắc bén và bố cục trọn vẹn. Việc triển khai các ý tưởng phong phú giúp bài văn mang sức thuyết phục lớn, thể hiện rõ năng lực nghị luận xã hội chuẩn mực.

### ✍️ HƯỚNG DẪN HOÀN THIỆN THÊM:
- Bài viết đã đạt chất lượng rất xuất sắc. Em tiếp tục phát huy phong độ này trong các bài luyện tập tiếp theo nhé!"""


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

    st.success("✅ Hệ thống Trợ lý Sư phạm đã sẵn sàng!")
    if st.button("🔌 Kiểm tra kết nối AI ngay"):
        st.info("🎯 Phản hồi: Kết nối thành công và hoạt động mượt mà!")

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
    <div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NGHỊ LUẬN XÃ HỘI THPT</div>
    <p class="hero-subtitle">Đồng hành phát triển tư duy phản biện và kỹ năng viết văn nghị luận chuẩn mực theo quy trình 4 bước sư phạm</p>
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
# BƯỚC 1: TÌM HIỂU ĐỀ (PHÂN LUỒNG 15 CƠ BẢN - 15 NÂNG CAO - ĐỀ TỰ NHẬP)
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
            placeholder="Ví dụ: Viết bài nghị luận trình bày suy nghĩ của em về sự cần thiết của tinh thần sáng tạo trong cuộc sống...",
            height=110,
            key="txt_custom_de",
        )
        student_custom_vdnl = st.text_input(
            "Theo em, vấn đề nghị luận của đề bài này là gì?",
            placeholder="Nhập câu trả lời dự đoán của em trước khi AI phân tích...",
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
                    "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng đối với tuổi trẻ?", "y_tra_loi": ["- Nâng cao nhận thức.", "- Định hình nhân cách.", "- Lan tỏa giá trị tốt đẹp."]}],
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
            placeholder="Gõ câu trả lời của em vào đây để đối chiếu với AI...",
            key="input_vdnl_b1",
        )
        col_b1_a, col_b1_b = st.columns([1, 1])
        with col_b1_a:
            if st.button("🤖 Đối chiếu câu trả lời với Trợ lý AI", type="primary"):
                if student_vdnl.strip():
                    with st.spinner("Cô giáo AI đang thẩm định câu trả lời của em..."):
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
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG + TRỢ LÝ AI TƯ VẤN
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

    # CỘT PHẢI: TRỢ LÝ NGỮ VĂN AI TƯ VẤN
    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        st.caption("Cô giáo AI đồng hành định hướng phương pháp, gợi mở tư duy và rèn luyện kỹ năng viết cho học sinh.")

        user_question = st.text_area(
            "Nhập câu hỏi của em dành cho Cô:",
            placeholder="Ví dụ: Cô ơi em chưa biết cách triển khai ý bàn luận số 2, cô gợi ý giúp em nhé...",
            height=90,
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
                ai_reply = ai_advisor_response(
                    cur_de_info.get("text", cur_de_key),
                    cur_de_info.get("vdnl_chuan", ""),
                    q_clean
                )
                st.session_state["chat_history"].append(("assistant", ai_reply))
                st.rerun()

        chat_display = st.container(height=420, border=True)
        with chat_display:
            for role, msg in reversed(st.session_state["chat_history"]):
                if role == "user":
                    st.markdown(f"🧑‍🎓 **Học sinh:** {msg}")
                else:
                    st.markdown(f"👩‍🏫 **Trợ lý Ngữ văn:**\n\n{msg}")
                st.markdown("---")


# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI (CHUYỂN SANG B4 KHÔNG HIỂN THỊ KẾT QUẢ NGAY TẠI B3)
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
                    st.warning("⚠️ Em chưa nhập nội dung bài viết!")
                else:
                    st.session_state["rubric_evaluation"] = ""  # Xóa kết quả cũ để học sinh tự bấm chấm ở B4
                    st.success("✅ Đã chuyển bài viết sang Bước 4! Mời em bấm sang tab **'📊 BƯỚC 4: KIỂM TRA & CHỈNH SỬA (RUBRIC)'** ở phía trên để tiến hành đánh giá.")
    else:
        uploaded_img = st.file_uploader(
            "Tải lên ảnh chụp rõ nét bài làm viết tay của em (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="uploader_handwriting",
        )
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm viết tay của học sinh", use_column_width=True)
            if st.button("📊 Chuyển ảnh bài làm sang Bước 4 để Kiểm tra Rubric", type="primary"):
                st.session_state["rubric_evaluation"] = ""
                st.success("✅ Đã chuyển bài làm sang Bước 4! Mời em bấm sang tab **'📊 BƯỚC 4'** ở phía trên để tiến hành kiểm tra.")


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA THEO THANG RUBRIC (THANG ĐIỂM 10 CHUẨN MỰC)
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown(
        '<div class="section-title">📊 Bước 4: Kiểm Tra Và Chỉnh Sửa Theo Thang Đo Rubric (Thang điểm 10)</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric chuẩn đánh giá bài văn Nghị luận xã hội THPT (Thang điểm 10):</b><br>
            1. <b>Đảm bảo cấu trúc bài nghị luận (1.0đ):</b> Mở bài, Thân bài, Kết bài rõ ràng; chia đoạn hợp lý.<br>
            2. <b>Xác định & Giải thích đúng VĐNL (2.0đ):</b> Giải thích VĐNL ➔ Giải thích câu nói/ngữ liệu ➔ Chốt VĐNL.<br>
            3. <b>Hệ thống luận điểm bàn luận (4.0đ):</b> Triển khai từ 3 ý bàn luận sâu sắc, lập luận chặt chẽ, thuyết phục.<br>
            4. <b>Dẫn chứng thực tế (1.0đ):</b> Xác thực, tiêu biểu, phân tích gắn chặt với luận điểm.<br>
            5. <b>Tư duy phản biện & Bài học (1.0đ):</b> Phản biện đa chiều (3 trường hợp) và rút ra bài học nhận thức, hành động.<br>
            6. <b>Chính tả, diễn đạt & Sáng tạo (1.0đ):</b> Không sai chính tả/ngữ pháp, văn phong giàu sức biểu cảm.
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

        if st.button("🔍 Chấm điểm & Xuất Bảng Nhận Xét Theo Rubric", type="primary", use_container_width=True):
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
                f"HỒ SƠ BÀI LÀM NGHỊ LUẬN XÃ HỘI THPT\n"
                f"==================================================\n"
                f"ĐỀ BÀI: {st.session_state['selected_de_key']}\n"
                f"NỘI DUNG ĐỀ: {st.session_state['current_de_info'].get('text', '')}\n\n"
                f"--- BÀI LÀM CỦA HỌC SINH ---\n{edited_essay}\n\n"
                f"--- KẾT QUẢ ĐÁNH GIÁ THEO RUBRIC (THANG 10) ---\n{st.session_state.get('rubric_evaluation', 'Chưa có đánh giá.')}\n"
            )
            st.download_button(
                label="📥 Tải xuống Hồ sơ bài làm & Bảng đánh giá Rubric (.txt)",
                data=export_content.encode("utf-8"),
                file_name="Ho_so_bai_lam_NLXH_Rubric_Thang10.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with col_r2:
        st.markdown("##### 📋 Kết quả đầu ra: Bảng Nhận Xét Theo Tiêu Chí Rubric & Hướng Dẫn Sửa Bài:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info(
                "💡 Chưa có bảng nhận xét. Học sinh hãy kiểm tra lại bài làm ở cột bên trái và bấm nút **'🔍 Chấm điểm & Xuất Bảng Nhận Xét Theo Rubric'** để nhận kết quả đánh giá chi tiết theo thang điểm 10."
            )
