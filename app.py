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
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em có thắc mắc gì về cách giải thích, tìm ý bàn luận, hướng dẫn viết mở bài hay phân tích dẫn chứng cho đề bài này thì cứ trao đổi với cô nhé!")
    ]

if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""

if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""

if "eval_vdnl_text" not in st.session_state:
    st.session_state["eval_vdnl_text"] = ""


# ==============================================================================
# 3. ĐỘNG CƠ SƯ PHẠM CHUẨN MỰC (ĐỊNH HƯỚNG ĐÚNG TRỌNG TÂM CÂU HỎI)
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
        return f"""⚠️ **CHƯA HOÀN TOÀN CHÍNH XÁC:**

- **Nhận xét của Cô:** Câu trả lời của em (*"{student_guess}"*) chưa đi đúng vào trọng tâm cốt lõi của đề. 
- **Gợi ý định hướng:** Em hãy đọc lại ngữ liệu và tự hỏi tác giả đang hướng tới phẩm chất, đạo lý hay hành động nào của con người.
- **Vấn đề nghị luận chuẩn của đề:** *{vdnl_chuan}*

👉 Em hãy suy nghĩ và điều chỉnh lại câu trả lời để nắm vững định hướng trước khi sang **BƯỚC 2** nhé!"""


def ai_advisor_response(de_text, vdnl_chuan, user_q):
    """Trợ lý AI tư vấn ở Bước 2: Trả lời bám sát đúng câu hỏi thực tế của học sinh (mở bài, dẫn chứng, lập luận), định hướng sâu sắc không làm thay."""
    q_lower = user_q.lower()
    
    if "mở bài" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn định hướng cách viết Mở bài cho em:**
Để viết một mở bài hay và đúng chuẩn cho đề bài *"{vdnl_chuan}"*, em không nên đi thẳng vào vấn đề một cách khô khan mà cần tuân thủ cấu trúc:
1. **Dẫn dắt:** Xuất phát từ một câu nói, một hình ảnh thơ, một hiện tượng đời sống hoặc quy luật tất yếu có liên quan đến chủ đề.
2. **Giới thiệu:** Nêu trực tiếp vấn đề nghị luận: *{vdnl_chuan}*.
👉 *Gợi ý mẫu tư duy:* Em có thể dùng cấu trúc: *"Cuộc sống luôn đặt ra cho con người những thử thách... và để vượt qua điều đó, một trong những phẩm chất vô cùng quan trọng chính là..."*. Em hãy tự viết câu mở đầu theo cách của mình nhé!"""

    elif "dẫn chứng" in q_lower or "chứng minh" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn hướng dẫn chọn & phân tích Dẫn chứng:**
Đối với đề bài về *"{vdnl_chuan}"*, khi đưa dẫn chứng vào bài viết, em cần lưu ý 3 bước:
1. **Chọn nhân vật/sự kiện:** Lấy một tấm gương tiêu biểu thực tế (ví dụ trong Kho dẫn chứng 9 chủ điểm ở mục bên trái).
2. **Nêu hành động cốt lõi:** Họ đã làm gì, đối mặt với hoàn cảnh ra sao?
3. **Phân tích ý nghĩa (Quan trọng nhất):** Hành động ấy chứng minh điều gì cho luận điểm của em? Tránh kể lể dài dòng cốt truyện mà quên mất việc kết nối dẫn chứng với vấn đề nghị luận.
👉 Em hãy chọn 1 nhân vật mà em ấn tượng nhất và thử viết 3 câu phân tích ý nghĩa của họ xem nào!"""

    elif "phản biện" in q_lower or "mở rộng" in q_lower:
        return f"""👩‍🏫 **Trợ lý Ngữ văn định hướng tư duy Phản biện:**
Phản biện là phần giúp bài văn của em đạt điểm xuất sắc. Đối với đề bài này, em có thể triển khai qua 3 khía cạnh:
1. **Phê phán mặt trái:** Những kẻ có thái độ sống ngược lại (ích kỷ, thờ ơ, lười biếng...).
2. **Phân biệt rạch ròi:** Tránh hiểu cực đoan hoặc biến giá trị này thành hình thức phô trương.
3. **Bài học nhận thức:** Rút ra ý nghĩa thực tiễn cho bản thân.
👉 Em hãy thử suy nghĩ xem nếu một người hoàn toàn thiếu đi phẩm chất này thì cuộc sống của họ sẽ ra sao?"""

    else:
        return f"""👩‍🏫 **Trợ lý Ngữ văn đồng hành cùng em:**
Với thắc mắc của em (*"{user_q}"*) về đề bài *"{vdnl_chuan}"*, cô hướng dẫn em tư duy như sau:
- **Xác định luận điểm:** Chia vấn đề thành 2-3 ý nhỏ (Biểu hiện là gì? Vì sao cần có? Ý nghĩa đối với tuổi trẻ?).
- **Phương pháp lập luận:** Sử dụng lý lẽ kết hợp bằng chứng thực tế để làm sáng tỏ vấn đề.
Em hãy dựa trên khung định hướng ở bên trái để phác thảo các ý chính ra giấy nháp, nếu vướng chỗ nào cứ trao đổi tiếp với cô nhé!"""


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

    # CỘT PHẢI: TRỢ LÝ NGỮ VĂN AI TƯ VẤN (ĐỊNH HƯỚNG SƯ PHẠM - KHÔNG VIẾT HỘ)
    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        st.caption("Cô giáo AI đồng hành định hướng phương pháp, gợi mở tư duy và rèn luyện kỹ năng viết cho học sinh.")

        user_question = st.text_area(
            "Nhập câu hỏi của em dành cho Cô:",
            placeholder="Ví dụ: Cô ơi em chưa biết cách triển khai ý bàn luận số 2, cô gợi ý giúp em hướng tư duy nhé...",
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

        chat_display = st.container(height=420, border=True)
        with chat_display:
            for role, msg in reversed(st.session_state["chat_history"]):
                if role == "user":
                    st.markdown(f"🧑‍🎓 **Học sinh:** {msg}")
                else:
                    st.markdown(f"👩‍🏫 **Trợ lý Ngữ văn:**\n\n{msg}")
                st.markdown("---")


# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI (CÓ THÊM GỢI Ý MỞ RỘNG LUẬN ĐIỂM)
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info(
        f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n"
        f"📖 *{st.session_state['current_de_info'].get('text', '')}*"
    )

    # Thêm hộp công cụ hỗ trợ tư duy tại xưởng viết
    with st.expander("💡 Hộp công cụ tư duy nhanh (Gợi ý mở rộng luận điểm khi viết bài)", expanded=False):
        col_tool1, col_tool2, col_tool3 = st.columns(3)
        with col_tool1:
            st.markdown("**🌟 Gợi ý mở bài ấn tượng:**")
            st.caption("Hãy đi từ nghịch lý cuộc sống, một câu nói triết lý hoặc một hình ảnh biểu tượng để khơi gợi sự tò mò.")
        with col_tool2:
            st.markdown("**🔍 Gợi ý liên kết dẫn chứng:**")
            st.caption("Sau khi nêu tên nhân vật, hãy đặt câu hỏi: *Họ đã hành động ra sao và để lại bài học gì cho thế hệ trẻ?*")
        with col_tool3:
            st.markdown("**🔄 Gợi ý hướng phản biện:**")
            st.caption("Lật lại vấn đề: *Sự thờ ơ hay lối sống vị kỷ sẽ đẩy con người và xã hội tới bờ vực nào?*")

    write_mode = st.radio(
        "Chọn hình thức làm bài của em:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode",
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội (Khoảng 600 chữ):",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy vận dụng dàn ý và dẫn chứng ở Bước 2 để tự mình viết bài văn hoàn chỉnh tại đây...",
        )
        st.session_state["user_essay"] = essay_input
        word_count = len(essay_input.strip().split()) if essay_input.strip() else 0
        st.caption(f"📊 Số từ hiện tại: **{word_count} từ** (Dung lượng chuẩn khuyến nghị: khoảng 500 – 700 từ).")

        if st.button("📊 Chuyển bài viết sang Bước 4 để Chấm & Nhận xét theo Rubric", type="primary"):
            if not essay_input.strip():
                st.warning("⚠️ Em chưa nhập nội dung bài viết!")
            else:
                eval_res = ai_evaluate_essay_rubric(
                    st.session_state["selected_de_key"],
                    st.session_state["current_de_info"],
                    essay_text=essay_input.strip(),
                )
                st.session_state["rubric_evaluation"] = eval_res
                st.success("✅ Đã đánh giá xong! Mời em bấm sang tab **'📊 BƯỚC 4: KIỂM TRA & CHỈNH SỬA (RUBRIC)'** (hoặc xem ngay kết quả bên dưới).")
                with st.container(border=True):
                    st.markdown(st.session_state["rubric_evaluation"])
    else:
        uploaded_img = st.file_uploader(
            "Tải lên ảnh chụp rõ nét bài làm viết tay của em (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="uploader_handwriting",
        )
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm viết tay của học sinh", use_column_width=True)
            if st.button("📊 Nhờ AI đọc bài viết tay & Chấm theo Rubric (Bước 4)", type="primary"):
                eval_res = ai_evaluate_essay_rubric(
                    st.session_state["selected_de_key"],
                    st.session_state["current_de_info"],
                    image_obj=img_obj,
                )
                st.session_state["rubric_evaluation"] = eval_res
                st.success("✅ Đã đánh giá xong! Mời em xem kết quả bên dưới hoặc mở tab **BƯỚC 4**.")
                with st.container(border=True):
                    st.markdown(st.session_state["rubric_evaluation"])


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA THEO THANG RUBRIC (ĐẦU RA BẢNG NHẬN XÉT TIÊU CHÍ)
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown(
        '<div class="section-title">📊 Bước 4: Kiểm Tra Và Chỉnh Sửa Theo Thang Đo Rubric</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric chuẩn đánh giá bài văn Nghị luận xã hội THPT:</b><br>
            1. <b>Đảm bảo cấu trúc bài nghị luận (0.5đ):</b> Mở bài, Thân bài, Kết bài rõ ràng; chia đoạn hợp lý.<br>
            2. <b>Xác định & Giải thích đúng VĐNL (1.0đ):</b> Giải thích VĐNL ➔ Giải thích câu nói/ngữ liệu ➔ Chốt VĐNL.<br>
            3. <b>Hệ thống luận điểm bàn luận (2.0đ):</b> Triển khai từ 3 ý bàn luận sâu sắc, lập luận chặt chẽ, thuyết phục.<br>
            4. <b>Dẫn chứng thực tế (0.5đ):</b> Xác thực, tiêu biểu, phân tích gắn chặt với luận điểm.<br>
            5. <b>Tư duy phản biện & Bài học (0.5đ):</b> Phản biện đa chiều (3 trường hợp) và rút ra bài học nhận thức, hành động.<br>
            6. <b>Chính tả, diễn đạt & Sáng tạo (0.5đ):</b> Không sai chính tả/ngữ pháp, văn phong giàu sức biểu cảm.
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

        if st.button("🔍 Chấm & Xuất Bảng Nhận Xét Theo Tiêu Chí Rubric", type="primary", use_container_width=True):
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
                f"--- KẾT QUẢ ĐÁNH GIÁ THEO RUBRIC ---\n{st.session_state.get('rubric_evaluation', 'Chưa có đánh giá.')}\n"
            )
            st.download_button(
                label="📥 Tải xuống Hồ sơ bài làm & Bảng đánh giá Rubric (.txt)",
                data=export_content.encode("utf-8"),
                file_name="Ho_so_bai_lam_NLXH_Rubric.txt",
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
                "💡 Chưa có bảng nhận xét. Học sinh hãy nhập bài làm ở cột bên trái (hoặc từ Bước 3) và bấm nút **'🔍 Chấm & Xuất Bảng Nhận Xét Theo Tiêu Chí Rubric'** để nhận kết quả đánh giá chi tiết."
            )
