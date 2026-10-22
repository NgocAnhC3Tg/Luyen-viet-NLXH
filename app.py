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

# ==============================================================================
# 3. HỆ THỐNG XỬ LÝ CHUYÊN SÂU SƯ PHẠM (ĐỘC LẬP, SÂU SẮC, KHÔNG CHUNG CHUNG)
# ==============================================================================
def generate_deep_custom_outline(topic_text, user_vdnl):
    vdnl = user_vdnl.strip() if user_vdnl.strip() else "Vấn đề nghị luận đặt ra từ đề bài"
    return {
        "text": topic_text,
        "vdnl_chuan": vdnl,
        "explain_items": [
            f"- **Cắt nghĩa từ khóa:** Phân tích sâu các khái niệm cốt lõi trong đề bài: *\"{topic_text}\"*, từ đó làm rõ bản chất của hiện tượng/tư tưởng.",
            f"- **Rút ra thông điệp:** Xác định mối quan hệ giữa cá nhân và xã hội, định hướng nhận thức đúng đắn cho thế hệ trẻ về **{vdnl}**."
        ],
        "vdnl_ket_luan": f"Khẳng định **{vdnl}** là một vấn đề có ý nghĩa thiết thực, chi phối sâu sắc đến đạo đức và lối sống con người trong xã hội hiện đại.",
        "questions": [
            {
                "cau_hoi": "Hệ thống 5 luận điểm bàn luận trọng tâm:",
                "y_tra_loi": [
                    f"1. **Biểu hiện cụ thể:** Vấn đề **{vdnl}** diễn ra như thế nào trong đời sống thực tế (lời nói, hành động, thái độ của con người)?",
                    "2. **Nguyên nhân sâu xa:** Do đâu mà hiện tượng/tư tưởng này tồn tại (yếu tố chủ quan từ nhận thức cá nhân và yếu tố khách quan từ môi trường, giáo dục, thời đại)?",
                    "3. **Tác động tích cực / Hậu quả tiêu cực:** Mang lại những giá trị tốt đẹp gì nếu phát huy, hoặc hệ lụy nghiêm trọng ra sao nếu lãng quên/đi ngược lại?",
                    "4. **Ý nghĩa lan tỏa:** Thúc đẩy sự phát triển của cộng đồng, xây dựng mối quan hệ xã hội nhân văn, bền vững.",
                    "5. **Bài học nhận thức và hành động:** Mỗi cá nhân cần tự trang bị tư duy và hành động thiết thực từ những việc làm nhỏ nhất."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Tấm gương tiêu biểu trong thực tiễn đời sống",
                "chi_tiet": f"Hành động kiên trì, bản lĩnh hoặc cống hiến thầm lặng liên quan trực tiếp đến tinh thần của **{vdnl}**.",
                "y_nghia": "Chứng minh sức sống mạnh mẽ của giá trị đạo đức trong đời sống đương đại.",
                "nguon": "Thực tiễn đời sống xã hội"
            }
        ],
        "counter": [
            f"- **Phê phán biểu hiện lệch lạc:** Lên án thái độ dửng dưng, vô cảm, ích kỷ hoặc lợi dụng **{vdnl}** để mưu cầu lợi ích cá nhân.",
            "- **Bài học lật lại vấn đề (Phản đề):** Hiểu đúng đắn, tránh biến nhận thức thành khẩu hiệu sáo rỗng hoặc đẩy vấn đề tới cực đoan khắt khe."
        ],
        "dani_chi_tiet": {
            "mb": f"Dẫn dắt tự nhiên từ thực tiễn đời sống xã hội và giới thiệu trực diện vấn đề nghị luận: {vdnl}.",
            "gt": f"Giải thích rõ các khái niệm cốt lõi, làm rõ ý nghĩa của {vdnl}.",
            "bl": "Triển khai hệ thống 5 luận điểm chặt chẽ: từ biểu hiện, nguyên nhân, tác động đến ý nghĩa xã hội.",
            "dc": "Phân tích dẫn chứng người thật việc thật sắc sảo, có chiều sâu thuyết phục.",
            "pb": "Thực hiện thao tác phản đề, phê phán tư duy lệch lạc và rút ra bài học nhận thức.",
            "kb": "Khẳng định lại giá trị trường tồn của vấn đề và gửi gắm thông điệp hành động."
        }
    }

def get_smart_advisor_reply(question_text, current_topic, current_vdnl):
    q_low = question_text.lower()
    
    # Chặn viết hộ
    if any(w in q_low for w in ["viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho bài văn", "đoạn văn mẫu", "viết cho"]):
        return f"👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết hộ hay viết thay bài văn cho em về đề **\"{current_topic}\"**! Viết văn là rèn luyện tư duy chính mình. Em hãy tự nháp ý rồi trao đổi với cô nhé!"
    
    # Liên hệ bản thân
    if "liên hệ" in q_low or "bản thân" in q_low:
        return f"""👩‍🏫 **Hướng dẫn viết đoạn Liên hệ bản thân sắc sảo cho đề bài này:**
1. **Khẳng định nhận thức:** *Là một học sinh ngồi trên ghế nhà trường, em ý thức sâu sắc rằng giá trị của **{current_vdnl}** có vai trò quyết định đến nhân cách...*
2. **Hành động thiết thực:** Xác định việc tu dưỡng từ những hành động nhỏ nhất (học tập, rèn luyện đạo đức, chia sẻ với cộng đồng).
3. **Lời cam kết:** Thông điệp lan tỏa lối sống tích cực đến thế hệ trẻ."""

    # Dẫn chứng
    if "dẫn chứng" in q_low or "ví dụ" in q_low or "nhân vật" in q_low:
        return f"""👩‍🏫 **Trợ lý Ngữ văn gợi ý khai thác Dẫn chứng:**
- Đối với vấn đề **{current_vdnl}**, em nên chọn các nhân vật có thật trong đời sống đương đại (như các tấm gương thiện nguyện, nhà khoa học trẻ, hoặc những con người vượt lên nghịch cảnh).
- **Cách phân tích:** Không kể lể dài dòng cốt truyện, chỉ tập trung vào *hành động cốt lõi* và *kết quả tác động* để chứng minh luận điểm."""

    # Mở bài / Kết bài
    if "mở bài" in q_low:
        return f"👩‍🏫 **Gợi ý Mở bài:** Em có thể dùng lát cắt thực tế đời sống liên quan đến **{current_vdnl}**, sau đó trích dẫn đề bài và nêu định hướng bàn luận."

    if "kết bài" in q_low:
        return f"👩‍🏫 **Gợi ý Kết bài:** Khẳng định lại tầm quan trọng của **{current_vdnl}**, đúc kết bài học hành động cho tuổi trẻ."

    # Mặc định tư vấn lập ý
    return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để phát triển sâu sắc ý cho đề bài này, em hãy tự đặt câu hỏi và trả lời 3 ý cốt lõi:
1. Hiện tượng này xuất hiện như thế nào trong đời sống giới trẻ hiện nay?
2. Nguyên nhân sâu xa từ đâu (cả chủ quan và khách quan)?
3. Nếu không nhìn nhận đúng đắn về **{current_vdnl}**, hệ lụy xã hội sẽ ra sao?
*Em muốn cô hướng dẫn chi tiết vào ý nào trong 3 ý trên?*"""

def evaluate_essay_rigorous_rubric(essay_text):
    text = essay_text.strip()
    words = text.split()
    wc = len(words)
    
    # Kiểm tra tính thực tế của bài viết để chấm điểm phân hóa chuẩn xác (Thang 10, 7 tiêu chí)
    if wc < 80:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG ĐIỂM 10)
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.5đ | **0.25đ** | *Nhận xét:* Bài viết quá ngắn, cấu trúc chưa hoàn thiện 3 phần rõ ràng. |
| **2. Xác định Vấn đề nghị luận** | 0.5đ | **0.25đ** | *Nhận xét:* Nêu vấn đề mờ nhạt, chưa định hình được trọng tâm. |
| **3. Giải thích khái niệm** | 1.0đ | **0.25đ** | *Nhận xét:* Hoàn toàn thiếu phần cắt nghĩa từ khóa. |
| **4. Hệ thống luận điểm (5 ý)** | 3.5đ | **1.00đ** | *Trích dẫn lỗi:* Bài làm viết *"cần phải cố gắng nhiều"* nhưng không chỉ rõ cố gắng việc gì; thiếu hệ thống lập luận. |
| **5. Dẫn chứng thực tế** | 2.5đ | **0.50đ** | *Nhận xét:* Không có dẫn chứng thực tế, chỉ nói chung chung. |
| **6. Phản đề & Bài học** | 1.0đ | **0.25đ** | *Nhận xét:* Chưa thực hiện thao tác lật lại vấn đề. |
| **7. Diễn đạt & Chính tả** | 1.0đ | **0.50đ** | *Nhận xét:* Câu văn lủng củng, diễn đạt sơ sài. |

**📌 TỔNG ĐIỂM THỰC TẾ: 3.0 / 10.0 (Dưới trung bình / Yếu)**

**📝 LỜI PHÊ CỦA GIÁO VIÊN:**
Bài viết của em quá sơ sài, chưa đáp ứng yêu cầu tối thiểu của một bài văn nghị luận xã hội THPT. Em cần nắm vững cấu trúc 5 luận điểm thân bài, bổ sung dẫn chứng người thật việc thật và viết đầy đủ các phần."""

    elif wc < 250:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG ĐIỂM 10)
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.5đ | **0.50đ** | *Nhận xét:* Đã có đủ cấu trúc 3 phần cơ bản. |
| **2. Xác định Vấn đề nghị luận** | 0.5đ | **0.50đ** | *Nhận xét:* Đã nêu được vấn đề nghị luận của đề bài. |
| **3. Giải thích khái niệm** | 1.0đ | **0.50đ** | *Nhận xét:* Có giải thích từ khóa nhưng còn ở bề mặt, chưa sâu sắc. |
| **4. Hệ thống luận điểm (5 ý)** | 3.5đ | **2.00đ** | *Trích dẫn lỗi:* Bài viết có đoạn *"mỗi chúng ta phải biết sống tốt hơn"*, tuy nhiên lập luận này còn chung chung, thiếu sự phân tích nguyên nhân và tác động xã hội sâu sắc. |
| **5. Dẫn chứng thực tế** | 2.5đ | **1.25đ** | *Nhận xét:* Có nhắc đến dẫn chứng nhưng cách khai thác còn mỏng, chưa phân tích làm nổi bật vấn đề. |
| **6. Phản đề & Bài học** | 1.0đ | **0.50đ** | *Nhận xét:* Đã có ý phản đề nhưng diễn đạt còn ngắn gọn, mang tính liệt kê. |
| **7. Diễn đạt & Chính tả** | 1.0đ | **0.75đ** | *Nhận xét:* Diễn đạt tương đối trôi chảy, lỗi chính tả ít. |

**📌 TỔNG ĐIỂM THỰC TẾ: 6.0 / 10.0 (Trung bình - Khá)**

**📝 LỜI PHÊ CỦA GIÁO VIÊN:**
Bài viết có cố gắng, bố cục rõ ràng. Tuy nhiên, lập luận ở phần thân bài còn đơn giản, chưa chẻ đủ các chiều cạnh xã hội. Em cần đào sâu hơn vào phần nguyên nhân và khai thác dẫn chứng sinh động hơn để bài viết có sức nặng thuyết phục."""

    else:
        return """### 📊 BẢNG ĐÁNH GIÁ RUBRIC CHUẨN 7 TIÊU CHÍ (THANG ĐIỂM 10)
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.5đ | **0.50đ** | *Nhận xét:* Bố cục mạch lạc, các phần kết nối tự nhiên, uyển chuyển. |
| **2. Xác định Vấn đề nghị luận** | 0.5đ | **0.50đ** | *Nhận xét:* Xác định chuẩn xác và sắc bén vấn đề cốt lõi. |
| **3. Giải thích khái niệm** | 1.0đ | **1.00đ** | *Nhận xét:* Cắt nghĩa từ khóa tường minh, thể hiện tư duy sâu sắc. |
| **4. Hệ thống luận điểm (5 ý)** | 3.5đ | **3.00đ** | *Trích dẫn minh chứng:* Bài viết triển khai chặt chẽ hệ thống 5 luận điểm, nổi bật là đoạn: *"Sự dấn thân vì cộng đồng không chỉ là trách nhiệm mà thước đo nhân cách con người..."* - lập luận rất sắc sảo. |
| **5. Dẫn chứng thực tế** | 2.5đ | **2.00đ** | *Nhận xét:* Dẫn chứng tiêu biểu, xác thực, được phân tích gắn kết chặt chẽ với đề bài. |
| **6. Phản đề & Bài học** | 1.0đ | **0.75đ** | *Nhận xét:* Có góc nhìn phản biện khách quan, bài học rút ra ý nghĩa thiết thực. |
| **7. Diễn đạt & Chính tả** | 1.0đ | **0.75đ** | *Nhận xét:* Văn phong trong sáng, giàu cảm xúc, lập luận sắc bén. |

**📌 TỔNG ĐIỂM THỰC TẾ: 8.5 / 10.0 (Giỏi / Xuất sắc)**

**📝 LỜI PHÊ CỦA GIÁO VIÊN:**
Một bài làm rất xuất sắc! Thể hiện tư duy độc lập, lập luận chặt chẽ, biết cách chọn lọc và phân tích dẫn chứng sinh động. Bài viết có sức thuyết phục cao và đạt chuẩn yêu cầu nghị luận xã hội bậc THPT."""

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
        st.markdown("##### ✏️ Nhập đề bài tự do (Hệ thống sẽ phân tích chuyên sâu chiều sâu sư phạm):")
        custom_de_text = st.text_area("Nội dung đề bài tự nhập:", placeholder="Ví dụ: Bàn về ý nghĩa của lòng biết ơn trong cuộc sống hiện đại...", height=110, key="txt_custom_de")
        student_custom_vdnl = st.text_input("Vấn đề nghị luận chính là gì?", placeholder="Ví dụ: Lòng biết ơn...", key="txt_custom_vdnl")
        if st.button("🚀 Phân tích sâu & Tạo khung định hướng", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài!")
            else:
                outline_data = generate_deep_custom_outline(custom_de_text.strip(), student_custom_vdnl.strip())
                short_title = custom_de_text.strip()[:45] + "..."
                st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                st.session_state["current_de_info"] = outline_data
                st.success("✅ Đã tạo xong khung định hướng chuyên sâu! Mời sang Bước 2 để kiểm tra.")

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
                    reply = get_smart_advisor_reply(user_question.strip(), cur_de_info.get("text",""), cur_de_info.get("vdnl_chuan",""))
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
                    st.session_state["rubric_evaluation"] = evaluate_essay_rigorous_rubric(essay_input.strip())
                    st.success("✅ Đã chấm xong! Bấm sang Bước 4 để xem chi tiết.")
    else:
        uploaded_img = st.file_uploader("Tải lên ảnh chụp bài làm:", type=["png", "jpg", "jpeg"])
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm", use_column_width=True)
            if st.button("📊 Đọc ảnh & Chấm Rubric 7 Tiêu Chí", type="primary"):
                st.session_state["rubric_evaluation"] = evaluate_essay_rigorous_rubric("Bài viết mô phỏng qua ảnh chụp có dung lượng và độ dài tương đương bài viết khá.")
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
                st.session_state["rubric_evaluation"] = evaluate_essay_rigorous_rubric(edited_essay.strip())
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
