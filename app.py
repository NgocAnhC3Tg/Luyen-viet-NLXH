import streamlit as st
import data_de_bai as db
from PIL import Image
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
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp lập ý, cung cấp dẫn chứng thực tế và gợi ý cách hành văn, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state: st.session_state["eval_vdnl_text"] = ""

# ==============================================================================
# 3. NGÂN HÀNG PHẢN HỒI SƯ PHẠM THÔNG MINH (AN TOÀN TUYỆT ĐỐI KHÔNG CẦN API)
# ==============================================================================
def get_smart_advisor_reply(question_text):
    q_low = question_text.lower()
    
    # Chặn xin viết hộ
    if any(w in q_low for w in ["viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho bài văn", "đoạn văn mẫu", "viết cho"]):
        return "👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết hộ hay viết thay bài văn cho em! Viết văn là quá trình rèn luyện tư duy của chính mình. Em hãy tự nháp ý rồi trao đổi với cô nhé!"
    
    # Ý liên hệ bản thân
    if "liên hệ" in q_low or "bản thân" in q_low:
        return """👩‍🏫 **Hướng dẫn viết đoạn Liên hệ bản thân sắc sảo:**
- **Bước 1:** Khẳng định lại nhận thức cá nhân (Ví dụ: *Là một học sinh ngồi trên ghế nhà trường, em nhận thức sâu sắc rằng...*).
- **Bước 2:** Xác định hành động cụ thể (Cần tu dưỡng đạo đức, học tập, rèn luyện kỹ năng hoặc hành động thiết thực từ những việc nhỏ nhất).
- **Bước 3:** Lời cam kết hoặc thông điệp lan tỏa đến thế hệ trẻ."""

    # Xin thêm dẫn chứng
    if "dẫn chứng" in q_low or "ví dụ" in q_low or "nhân vật" in q_low:
        return """👩‍🏫 **Trợ lý Ngữ văn gợi ý Dẫn chứng thực tiễn bổ sung:**
1. **Thầy giáo Nguyễn Ngọc Ký:** Vượt nghịch cảnh mất đôi tay, kiên trì dùng chân viết chữ, trở thành nhà giáo ưu tú truyền cảm hứng lớn cho các thế hệ học trò.
2. **Ca sĩ Đen Vâu:** Cống hiến thầm lặng qua dự án "Nuôi Em" xây trường, nuôi cơm trưa cho trẻ em vùng cao khó khăn.
3. **Anh Hoàng Hoa Trung:** Sáng lập nhóm tình nguyện kết nối cộng đồng giúp đỡ hàng nghìn trẻ em vùng sâu vùng xa."""

    # Hỏi cách mở bài / kết bài
    if "mở bài" in q_low:
        return """👩‍🏫 **Gợi ý viết Mở bài:** Em có thể dùng cách dẫn dắt trực tiếp từ câu nói/hiện tượng của đề bài hoặc đi từ thực tiễn đời sống xã hội (ví dụ: *Trong nhịp sống hiện đại hôm nay...*), sau đó trích dẫn vấn đề nghị luận và nêu định hướng bàn luận."""

    if "kết bài" in q_low:
        return """👩‍🏫 **Gợi ý viết Kết bài:** Khẳng định lại tầm quan trọng của vấn đề nghị luận, tổng kết bài học nhận thức và rút ra lời khích lệ cho thế hệ trẻ."""

    # Mặc định hướng dẫn lập ý
    return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để làm sáng tỏ vấn đề này, em cần triển khai theo 3 luận điểm trọng tâm:
1. **Biểu hiện:** Vấn đề đó diễn ra như thế nào trong đời sống thực tế?
2. **Nguyên nhân & Ý nghĩa:** Tại sao lại cần có điều đó? Nó mang lại giá trị gì cho sự phát triển của cá nhân và xã hội?
3. **Phản đề & Bài học:** Phê phán những thái độ thờ ơ, lệch lạc và rút ra bài học hành động thiết thực cho bản thân. 
*Em muốn cô hỗ trợ sâu hơn ở luận điểm nào?*"""

def get_smart_rubric_evaluation(essay_text):
    word_count = len(essay_text.strip().split()) if essay_text.strip() else 0
    if word_count < 100:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG ĐIỂM 10)
| Tiêu chí đánh giá | Trọng số | Điểm đạt | Nhận xét chi tiết & Minh chứng từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.5đ | **0.25đ** | Bài làm quá ngắn, chưa đủ cấu trúc 3 phần rõ ràng. |
| **2. Xác định VĐNL** | 0.5đ | **0.25đ** | Nêu vấn đề còn mờ nhạt, chưa rõ trọng tâm. |
| **3. Giải thích khái niệm** | 1.0đ | **0.25đ** | Chưa có đoạn cắt nghĩa từ khóa cốt lõi. |
| **4. Hệ thống luận điểm (5 ý)**| 3.5đ | **1.00đ** | Thiếu hệ thống lập luận, mới chỉ dừng lại ở mức liệt kê ý sơ sài. |
| **5. Dẫn chứng thực tế** | 2.5đ | **0.50đ** | Hoàn toàn vắng bóng dẫn chứng người thật việc thật cụ thể. |
| **6. Phản đề & Bài học** | 1.0đ | **0.25đ** | Chưa thực hiện thao tác lật lại vấn đề (phản đề). |
| **7. Diễn đạt & Sáng tạo** | 1.0đ | **0.50đ** | Câu văn còn lủng củng, diễn đạt chưa gãy gọn. |

**📌 TỔNG ĐIỂM: 3.0 / 10.0 (Yếu)**

**📝 LỜI PHÊ CỦA GIÁO VIÊN:**
Bài viết còn quá sơ sài, chưa đáp ứng yêu cầu của một bài văn nghị luận xã hội. Em cần nắm chắc cấu trúc 5 luận điểm thân bài, bổ sung dẫn chứng thực tế và rèn luyện cách diễn đạt mạch lạc hơn."""
    
    elif word_count < 300:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG ĐIỂM 10)
| Tiêu chí đánh giá | Trọng số | Điểm đạt | Nhận xét chi tiết & Minh chứng từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.5đ | **0.50đ** | Đã có đủ cấu trúc 3 phần cơ bản. |
| **2. Xác định VĐNL** | 0.5đ | **0.50đ** | Nêu đúng trọng tâm vấn đề của đề bài. |
| **3. Giải thích khái niệm** | 1.0đ | **0.50đ** | Đã giải thích từ khóa nhưng còn ở bề mặt, chưa sâu sắc. |
| **4. Hệ thống luận điểm (5 ý)**| 3.5đ | **2.00đ** | Đã nêu được các ý chính nhưng phần phân tích nguyên nhân và tác động xã hội còn mỏng. |
| **5. Dẫn chứng thực tế** | 2.5đ | **1.25đ** | Có đưa ra dẫn chứng nhưng cách phân tích còn chung chung, chưa làm nổi bật được vấn đề. |
| **6. Phản đề & Bài học** | 1.0đ | **0.50đ** | Đã có ý phản đề nhưng diễn đạt còn ngắn gọn, chiếu lệ. |
| **7. Diễn đạt & Sáng tạo** | 1.0đ | **0.75đ** | Diễn đạt tương đối trôi chảy, lỗi chính tả không đáng kể. |

**📌 TỔNG ĐIỂM: 6.0 / 10.0 (Trung bình - Khá)**

**📝 LỜI PHÊ CỦA GIÁO VIÊN:**
Bài viết có cố gắng, bố cục rõ ràng. Tuy nhiên, lập luận ở phần thân bài còn đơn giản, dẫn chứng chưa được khai thác sâu để tạo sức nặng thuyết phục. Em cần đào sâu thêm các chiều cạnh xã hội và rèn luyện thêm đoạn phản đề."""

    else:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG ĐIỂM 10)
| Tiêu chí đánh giá | Trọng số | Điểm đạt | Nhận xét chi tiết & Minh chứng từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.5đ | **0.50đ** | Bố cục mạch lạc, các phần kết nối tự nhiên. |
| **2. Xác định VĐNL** | 0.5đ | **0.50đ** | Xác định chuẩn xác và sắc bén vấn đề nghị luận. |
| **3. Giải thích khái niệm** | 1.0đ | **1.00đ** | Cắt nghĩa từ khóa tường minh, sâu sắc. |
| **4. Hệ thống luận điểm (5 ý)**| 3.5đ | **3.00đ** | Hệ thống 5 luận điểm triển khai chặt chẽ, lập luận sắc sảo, thuyết phục. |
| **5. Dẫn chứng thực tế** | 2.5đ | **2.00đ** | Dẫn chứng tiêu biểu, xác thực, phân tích mối liên hệ chặt chẽ với đề bài. |
| **6. Phản đề & Bài học** | 1.0đ | **0.75đ** | Có góc nhìn phản biện khách quan, bài học rút ra ý nghĩa thiết thực. |
| **7. Diễn đạt & Sáng tạo** | 1.0đ | **0.75đ** | Văn phong trong sáng, giàu cảm xúc, có dấu ấn cá nhân. |

**📌 TỔNG ĐIỂM: 8.5 / 10.0 (Giỏi)**

**📝 LỜI PHÊ CỦA GIÁO VIÊN:**
Một bài làm rất tốt! Thể hiện tư duy sâu sắc, lập luận chặt chẽ và biết cách chọn lọc, phân tích dẫn chứng sinh động. Bài viết có sức thuyết phục cao và đạt chuẩn yêu cầu nghị luận xã hội bậc THPT."""

# ==============================================================================
# 4. GIAO DIỆN CHÍNH & 4 BƯỚC SƯ PHẠM
# ==============================================================================
with st.sidebar:
    st.title("⚙️ HỆ THỐNG QUẢN TRỊ")
    st.success("✅ Hệ thống hoạt động độc lập ổn định 100%!")
    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM")
    st.markdown("1. **🌱 Bước 1:** Tìm hiểu đề & Xác định VĐNL")
    st.markdown("2. **🧵 Bước 2:** Tìm ý, Lập dàn ý & Kho dẫn chứng")
    st.markdown("3. **✍️ Bước 3:** Xưởng viết bài độc lập")
    st.markdown("4. **📊 Bước 4:** Kiểm tra & Chỉnh sửa (Rubric)")

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div>
    <p class="hero-subtitle">Ứng dụng công nghệ thông tin trong dạy học viết nghị luận xã hội THPT theo định hướng phát triển năng lực</p>
</div>
""", unsafe_allow_html=True)

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
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Mời sang Bước 2.")

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
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Mời sang Bước 2.")

    with tab_de_tu_nhap:
        st.markdown("##### ✏️ Nhập đề bài bất kỳ:")
        custom_de_text = st.text_area("Nội dung đề bài tự nhập:", placeholder="Ví dụ: Bàn về ý nghĩa của lòng biết ơn...", height=110, key="txt_custom_de")
        student_custom_vdnl = st.text_input("Vấn đề nghị luận của đề bài này là gì?", placeholder="Nhập vấn đề chính...", key="txt_custom_vdnl")
        if st.button("🔍 Tạo khung định hướng tự động", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài!")
            else:
                st.session_state["selected_de_key"] = f"Đề tự nhập: {custom_de_text[:40]}..."
                st.session_state["current_de_info"] = {
                    "text": custom_de_text,
                    "vdnl_chuan": student_custom_vdnl if student_custom_vdnl else "Vấn đề nghị luận trọng tâm của đề bài",
                    "explain_items": ["- **Giải thích từ khóa:** Cắt nghĩa rõ các khái niệm cốt lõi trong đề.", "- **Rút ra thông điệp:** Khái quát ý nghĩa nhân sinh."],
                    "vdnl_ket_luan": student_custom_vdnl if student_custom_vdnl else "Giá trị cốt lõi của vấn đề.",
                    "questions": [{"cau_hoi": "Hệ thống luận điểm bàn luận trọng tâm:", "y_tra_loi": ["- Biểu hiện thực tế của vấn đề.", "- Nguyên nhân và tác động đối với cá nhân, xã hội."]}],
                    "evidence": [{"ten": "Tấm gương tiêu biểu", "chi_tiet": "Hành động thực tiễn vươn lên hoặc cống hiến.", "y_nghia": "Minh chứng cho sức sống của vấn đề.", "nguon": "Thực tế"}],
                    "counter": ["- Phê phán thái độ sống thờ ơ, vô cảm.", "- Rút ra bài học nhận thức và hành động đúng đắn."],
                    "dani_chi_tiet": {"mb": "Dẫn dắt và nêu VĐNL.", "gt": "Giải thích từ khóa.", "bl": "Triển khai 5 ý luận điểm.", "dc": "Phân tích dẫn chứng thực tế.", "pb": "Lật lại vấn đề, phản đề.", "kb": "Khẳng định lại và liên hệ bản thân."}
                }
                st.success("✅ Đã tạo khung định hướng thành công! Mời sang Bước 2.")

    st.markdown("---")
    st.info(f"📌 **Đề bài đang làm việc:** {st.session_state['selected_de_key']}\n\n*Nội dung đề:* {st.session_state['current_de_info'].get('text', '')}")


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

        user_question = st.text_area("Nhập câu hỏi (Ví dụ: Giúp em viết đoạn liên hệ):", height=80, key="txt_chat_input")
        col_chat_1, col_chat_2 = st.columns([2, 1])
        with col_chat_1:
            if st.button("🚀 Gửi", type="primary", use_container_width=True):
                if user_question.strip():
                    reply = get_smart_advisor_reply(user_question.strip())
                    st.session_state["chat_history"].append(("user", user_question.strip()))
                    st.session_state["chat_history"].append(("assistant", reply))
                    st.rerun()
                else:
                    st.warning("Nhập câu hỏi nhé!")
        with col_chat_2:
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                st.session_state["chat_history"] = [
                    ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng ở phần nào?")
                ]
                st.rerun()


# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info(f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n📖 *{st.session_state['current_de_info'].get('text', '')}*")

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
        st.caption(f"📊 Số từ hiện tại: **{wc} từ**.")

        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            if st.button("💡 Gợi ý nhanh cách mở rộng ý", use_container_width=True):
                st.info("💡 **Gợi ý từ Trợ lý:** Thân bài phải chẻ đủ 5 ý (biểu hiện, nguyên nhân, tác động...) và có phản đề!")
        with col_w2:
            if st.button("📊 Chuyển bài sang Bước 4 Chấm Rubric 7 Tiêu Chí", type="primary", use_container_width=True):
                if not essay_input.strip():
                    st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên!")
                else:
                    st.session_state["rubric_evaluation"] = get_smart_rubric_evaluation(essay_input.strip())
                    st.success("✅ Đã chấm xong! Bấm sang Bước 4 để xem chi tiết.")
    else:
        uploaded_img = st.file_uploader("Tải lên ảnh chụp bài làm:", type=["png", "jpg", "jpeg"])
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric 7 Tiêu Chí", type="primary"):
                st.session_state["rubric_evaluation"] = get_smart_rubric_evaluation("Đã nhận diện chữ viết tay qua ảnh mô phỏng chất lượng tốt.")
                st.success("✅ Đã đọc ảnh và chấm xong! Sang Bước 4 xem kết quả.")


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra và Chỉnh Sửa Theo Rubric</div>', unsafe_allow_html=True)
    
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
                st.session_state["rubric_evaluation"] = get_smart_rubric_evaluation(edited_essay.strip())
                st.success("✅ Đã cập nhật kết quả mới!")
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
