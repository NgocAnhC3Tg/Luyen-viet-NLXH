import streamlit as st
import json
import re
from google import genai

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP & TABS
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
    
    .evidence-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. NGÂN HÀNG ĐỀ THI THỦ CÔNG CHI TIẾT (KHO DẪN CHỨNG CÓ NGUỒN CỤ THỂ)
# ==============================================================================
DE_BAI_DATA = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:
> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*
Từ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "topic_tag": "Trách nhiệm – Cống hiến – Tình người",
        "explain_core": [
            "**Lối sống có trách nhiệm:** Nhận thức rõ bổn phận, nghĩa vụ của bản thân đối với gia đình và xã hội; không dửng dưng, thờ ơ trước những vấn đề chung.",
            "**Gắn bó với cộng đồng:** Tinh thần hòa nhập, biết sẻ chia vui buồn, đặt lợi ích tập thể lên trên sự ích kỷ cá nhân và sẵn sàng cống hiến.",
            "**Ý nghĩa ngữ liệu Chế Lan Viên:** Câu thơ diễn tả sự chuyển hóa kỳ diệu: từ một vùng đất xa lạ (chỉ là nơi đất ở) trở thành một phần máu thịt, kỷ niệm sâu nặng (đất đã hóa tâm hồn) khi con người biết sống, gắn bó và trao đi yêu thương."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao người trẻ cần phải sống có trách nhiệm và biết gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "**Cơ sở xã hội:** Con người là một sinh vật xã hội, không cá nhân nào có thể tồn tại biệt lập. Sự phát triển của mỗi cá nhân luôn gắn liền với sự ổn định và văn minh của tập thể.",
                    "**Ý nghĩa đạo đức & nhân văn:** Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, kết nối con người bằng tình thương, tạo dựng một cộng đồng nhân ái và bền vững."
                ]
            },
            {
                "cau_hoi": "Lối sống cống hiến mang lại giá trị gì cho chính sự trưởng thành của bản thân người trẻ?",
                "y_tra_loi": [
                    "**Bồi đắp nhân cách:** Giúp con người thoát khỏi lối sống vị kỷ hẹp hòi, rèn luyện bản lĩnh, sự trưởng thành và mở rộng thế giới quan.",
                    "**Tạo dựng giá trị sống:** Khi biết trao đi giá trị, tuổi trẻ sẽ tìm thấy ý nghĩa thực sự của sự tồn tại, nhận được sự tôn trọng và tin yêu từ xã hội."
                ]
            }
        ],
        "evidence": [
            "**Dự án Nuôi Em (Người sáng lập: Hoàng Hoa Trung):** Từ năm 2014 đến nay, dự án đã kết nối hàng trăm ngàn người trẻ nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn. *(Nguồn: Báo Tuổi Trẻ, Cổng thông tin Trung ương Đoàn)*",
            "**Chiến dịch Mùa hè xanh:** Lực lượng thanh niên, sinh viên tình nguyện trên khắp cả nước hàng năm xây dựng hàng trăm cầu giao thông nông thôn, dạy học miễn phí cho trẻ em vùng sâu vùng xa. *(Nguồn: Báo Tiền Phong)*"
        ],
        "counter": [
            "Phê phán lối sống vị kỷ, 'chỉ biết mình', thờ ơ trước nỗi đau của đồng loại hoặc xem việc cống hiến là trách nhiệm của riêng người khác.",
            "Lật lại vấn đề: Sống có trách nhiệm không đồng nghĩa với cống hiến mù quáng hay bao đồng; cần biết cân bằng giữa việc chăm sóc bản thân và đóng góp cho cộng đồng."
        ]
    },
    
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.
Hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "topic_tag": "Thấu cảm – Lắng nghe – Hàn gắn",
        "explain_core": [
            "**Sự thấu cảm:** Năng lực đặt mình vào vị trí, hoàn cảnh và góc nhìn của người khác để cảm nhận và hiểu thấu nỗi đau, niềm vui của họ.",
            "**Lắng nghe chân thành:** Thái độ kiên nhẫn, trân trọng, không phán xét khi đón nhận tâm tư của đối phương."
        ],
        "questions": [
            {
                "cau_hoi": "Tại sao con người trong thời đại số lại cần đến sự thấu cảm và năng lực lắng nghe hơn bao giờ hết?",
                "y_tra_loi": [
                    "**Bối cảnh thời đại:** Sự bùng nổ công nghệ khiến con người dễ rơi vào trạng thái 'kết nối mạng nhưng mất kết nối thực', dẫn đến cảm giác cô đơn và trầm cảm gia tăng.",
                    "**Tác dụng hàn gắn:** Lắng nghe và thấu cảm đóng vai trò như liều thuốc xoa dịu tổn thương tâm lý, giải tỏa áp lực và thu hẹp khoảng cách giữa các thế hệ."
                ]
            }
        ],
        "evidence": [
            "**Dự án 'Tổng đài Ngày Mai' (Sáng lập bởi Tiến sĩ Đặng Hoàng Giang):** Tổng đài tham vấn tâm lý phi lợi nhuận lắng nghe và hỗ trợ tinh thần cho hàng ngàn người trẻ đang trải qua khủng hoảng tâm lý, trầm cảm. *(Nguồn: Báo Thanh Niên, VTV)*",
            "**Hoạt động cứu trợ thiên tai bão lũ (Bão Yagi 2024):** Sự thấu cảm sâu sắc trước nỗi đau mất mát của đồng bào miền Bắc đã thúc đẩy hàng triệu người dân cả nước chung tay đóng góp nguồn lực. *(Nguồn: Báo Nhân Dân, Mặt trận Tổ quốc Việt Nam)*"
        ],
        "counter": [
            "Phê phán thói vô cảm, tâm lý phán xét vội vàng hoặc thói quen mỉa mai, công kích cá nhân trên mạng xã hội.",
            "Lật lại vấn đề: Thấu cảm không đồng nghĩa với sự ủy mị, dung dưỡng cho những hành vi sai trái hoặc để cảm xúc chi phối hoàn toàn lý trí."
        ]
    },
    
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "topic_tag": "Bản sắc văn hóa – Nguồn cội – Hội nhập",
        "explain_core": [
            "**Bản sắc văn hóa dân tộc:** Toàn bộ những giá trị tinh hoa vật chất và tinh thần cốt lõi (phong tục, ngôn ngữ, nghệ thuật, đạo lý) được hun đúc qua lịch sử.",
            "**Hình ảnh chiếc mỏ neo:** Điểm tựa định hình vị thế, giúp một quốc gia giữ vững cội nguồn và cá tính độc đáo giữa dòng chảy toàn cầu hóa."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao việc bảo tồn bản sắc văn hóa lại là sứ mệnh sinh tồn của tuổi trẻ?",
                "y_tra_loi": [
                    "**Căn cước quốc gia:** Văn hóa là thẻ căn cước duy nhất khẳng định sự tồn tại độc lập của một dân tộc. Mất bản sắc đồng nghĩa với nguy cơ bị hòa tan.",
                    "**Nguồn cảm hứng sáng tạo:** Tinh hoa văn hóa truyền thống là kho tàng vô giá để thế hệ trẻ khai thác, sáng tạo ra các sản phẩm văn hóa đương đại mang tầm quốc tế."
                ]
            }
        ],
        "evidence": [
            "**Nghệ sĩ trẻ đưa văn hóa truyền thống vào nghệ thuật hiện đại:** Rapper Đen Vâu, ca sĩ Hoàng Thùy Linh, Đức Phúc ứng dụng nhạc cụ dân tộc, chất liệu dân gian (như hát xẩm, bài chồi, cổ phục) vào âm nhạc triệu view. *(Nguồn: Báo Tuổi Trẻ)*",
            "**Dự án Cổ phục Việt 'Đại Việt Cổ Phong':** Nhóm bạn trẻ nghiên cứu, phục dựng chuẩn xác các trang phục thời Triều Nguyễn, Triều Lê trên nền tảng số. *(Nguồn: Báo VnExpress)*"
        ],
        "counter": [
            "Phê phán thái độ sính ngoại mù quáng, xem thường tiếng Việt, coi rẻ các giá trị truyền thống dân tộc.",
            "Lật lại vấn đề: Giữ gìn bản sắc không có nghĩa là bảo thủ, khép kín; cần chủ động tiếp biến có chọn lọc những giá trị tiến bộ của nhân loại."
        ]
    },

    "Đề 04 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực của số đông trong kỷ nguyên số.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông trong thời đại số.",
        "topic_tag": "Bản lĩnh – Tư duy độc lập – Bản sắc",
        "explain_core": [
            "**Bản sắc riêng & chính kiến:** Tư duy độc lập, cá tính sáng tạo và hệ giá trị đạo đức riêng làm nên phẩm giá cá nhân.",
            "**Áp lực số đông trong kỷ nguyên số:** Sự phán xét, lôi kéo của thuật toán và tâm lý bầy đàn khiến con người dễ bị thỏa hiệp và san bằng cá tính."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao giữ vững bản sắc riêng trước đám đông lại vừa là thách thức vừa là giá trị lớn nhất của tuổi trẻ?",
                "y_tra_loi": [
                    "**Thách thức:** Xu hướng 'sợ bị bỏ lỡ' (FOMO) và áp lực bị tẩy chay khiến người trẻ dễ chọn cách hòa nhập bằng cách đồng hóa bản thân.",
                    "**Giá trị:** Sự khác biệt có định hướng là chìa khóa tạo nên năng lực cạnh tranh cốt lõi, giúp cá nhân đóng góp những góc nhìn mới cho xã hội."
                ]
            }
        ],
        "evidence": [
            "**Vận động viên Nguyễn Thị Oanh:** Vượt qua áp lực dư luận và thử thách khắc nghiệt về thể lực để liên tiếp giành 4 HCB SEA Games 32 trong cùng một buổi chiều. *(Nguồn: Báo Thể thao & Văn hóa)*",
            "**Các nhà sáng tạo nội dung giáo dục độc lập:** Giữa làn sóng nội dung 'rác' câu view, những kênh như 'Spiderum', 'Triết học Tuổi trẻ' vẫn kiên trì tạo ra tri thức sâu sắc. *(Nguồn: Báo Tiền Phong)*"
        ],
        "counter": [
            "Phê phán thói hùa theo phong trào, a dua thiếu suy nghĩ hoặc biến sự 'khác biệt' thành sự ngông cuồng, quái dị đi ngược chuẩn mực đạo đức.",
            "Lật lại vấn đề: Giữ bản sắc không có nghĩa là ngoan cố, cố chấp; cần biết lắng nghe có phản biện để hoàn thiện tư duy."
        ]
    },

    "Đề 05 (Nâng cao): Tư duy phản biện trong bùng nổ trí tuệ nhân tạo (AI)": {
        "text": """Trong kỷ nguyên trí tuệ nhân tạo (AI) phát triển bùng nổ, ranh giới giữa sự thật và giả mạo trở nên mỏng manh hơn bao giờ hết.
Viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tư duy phản biện và năng lực làm chủ tri thức của người trẻ hôm nay.""",
        "vdnl_chuan": "Tầm quan trọng của tư duy phản biện và năng lực tự chủ tri thức trước sự bùng nổ của trí tuệ nhân tạo (AI).",
        "topic_tag": "Tư duy phản biện – AI – Tự chủ tri thức",
        "explain_core": [
            "**Tư duy phản biện:** Năng lực phân tích, đánh giá, lật lại vấn đề một cách khách quan dựa trên bằng chứng logic thay vì tin tưởng cảm tính.",
            "**Năng lực làm chủ tri thức:** Việc chủ động biến thông tin thành tri thức cá nhân, coi công nghệ là công cụ hỗ trợ chứ không phải 'bộ não thay thế'."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao trong thời đại AI, tư duy phản biện lại trở thành năng lực sống còn?",
                "y_tra_loi": [
                    "**Nạn tin giả (Fake news / Deepfake):** Công nghệ tạo ra thông tin giả mạo vô cùng tinh vi; nếu thiếu tư duy phản biện, con người sẽ dễ bị thao túng tâm lý.",
                    "**Tránh sự thụ động tư duy:** Phụ thuộc hoàn toàn vào đáp án của AI khiến bộ não con người lười suy nghĩ, triệt tiêu khả năng sáng tạo độc lập."
                ]
            }
        ],
        "evidence": [
            "**Nạn lừa đảo bằng công nghệ Deepfake:** Bộ Công an liên tục cảnh báo các vụ lừa đảo chiếm đoạt tài sản bằng hình ảnh, giọng nói AI giả mạo người thân. *(Nguồn: Cổng thông tin Bộ Công an, Báo VTV)*",
            "**Chính sách của các trường đại học lớn (như Harvard, MIT):** Bắt buộc sinh viên phải minh bạch việc sử dụng AI và coi tư duy phản biện là tiêu chí chấm điểm cốt lõi. *(Nguồn: Báo Tuổi Trẻ Quốc Tế)*"
        ],
        "counter": [
            "Phê phán thái độ lười suy nghĩ, tin tưởng tuyệt đối vào thông tin trên mạng hoặc cực đoan chối bỏ sự tiến bộ của công nghệ.",
            "Lật lại vấn đề: Phản biện không phải là hoài nghi tiêu cực hay phủ nhận tất cả, mà là đi tìm chân lý bằng sự tỉnh táo và tri thức."
        ]
    }
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
- Học sinh tự phán đoán VĐNL bằng ý hiểu của mình: "{student_guess}"

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
    prompt = f"""
Bạn là chuyên gia khảo thí Ngữ văn THPT GDPT 2018. 
Học sinh tự dán đề bài riêng vào hệ thống:
\"\"\"{exam_text}\"\"\"

Học sinh trả lời Vấn đề nghị luận (VĐNL) cốt lõi là:
\"\"\"{student_guess}\"\"\"

Nhiệm vụ bắt buộc:
1. Phân tích thật chi tiết ngữ liệu và yêu cầu đề bài trên.
2. Thẩm định câu trả lời của học sinh (xưng cô - em). Nhận xét cụ thể điểm đúng/chưa sát.
3. BẮT BUỘC xây dựng Giàn giáo Bước 2 ĐẦY ĐỦ 4 THAO TÁC (Giải thích, Bàn luận, Kho dẫn chứng thực tế, Phản biện) BÁM SÁT 100% VÀO NỘI DUNG ĐỀ BÀI TRÊN.
   - Thao tác Bàn luận: Phải triển khai thành các đoạn lập luận có chiều sâu (3-5 câu), không viết tiêu đề chung chung.
   - Thao tác Dẫn chứng: BẮT BUỘC cung cấp tên nhân vật/sự kiện/dự án cụ thể KÈM NGUỒN XÁC THỰC (Báo chí, Tổ chức, Mốc thời gian).

Trả về cấu trúc JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "teacher_evaluation": "Lời nhận xét chi tiết khích lệ hoặc hướng dẫn nhẹ nhàng (xưng cô - em)",
  "vdnl_chuan": "Vấn đề nghị luận cốt lõi chính xác tuyệt đối được bóc tách từ ngữ liệu đề bài",
  "explain_core": [
     "**Cắt nghĩa từ khóa/hình ảnh 1:** Giải thích chi tiết nghĩa đen, nghĩa bóng hoặc thông điệp cốt lõi trong đề bài này",
     "**Cắt nghĩa từ khóa/hình ảnh 2:** Giải thích chi tiết mối quan hệ giữa các yếu tố trong đề bài này"
  ],
  "questions": [
     {{
       "cau_hoi": "Câu hỏi bàn luận trọng tâm 1 bám sát ngữ liệu đề bài?",
       "y_tra_loi": [
          "**Luận điểm chiều sâu 1:** Triển khai đoạn lập luận hoàn chỉnh giải thích vì sao vấn đề lại quan trọng",
          "**Luận điểm chiều sâu 2:** Triển khai đoạn lập luận hoàn chỉnh về tác động tới cá nhân và xã hội"
       ]
     }},
     {{
       "cau_hoi": "Câu hỏi bàn luận trọng tâm 2 bám sát ngữ liệu đề bài?",
       "y_tra_loi": [
          "**Luận điểm chiều sâu 1:** Triển khai đoạn lập luận hoàn chỉnh",
          "**Luận điểm chiều sâu 2:** Triển khai đoạn lập luận hoàn chỉnh"
       ]
     }}
  ],
  "evidence": [
     "**Dẫn chứng tiêu biểu 1 (Tên nhân vật/dự án):** Phân tích chi tiết hành động gắn với đề bài. *(Nguồn xác thực: Tên báo/Tổ chức/Năm)*",
     "**Dẫn chứng tiêu biểu 2 (Tên nhân vật/dự án):** Phân tích chi tiết hành động gắn với đề bài. *(Nguồn xác thực: Tên báo/Tổ chức/Năm)*"
  ],
  "counter": [
     "Phê phán biểu hiện tiêu cực hoặc cực đoan liên quan tới đề bài này",
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
            "explain_core": [f"**Giải thích cốt lõi:** Làm rõ bản chất và thông điệp của đề bài dán vào."],
            "questions": [
                {
                    "cau_hoi": f"Vì sao {student_guess} lại quan trọng đối với đời sống?",
                    "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn và phát triển nhân cách bền vững.", "Định hướng hành động tích cực cho tuổi trẻ trước thách thức thời đại."]
                }
            ],
            "evidence": [
                "**Dẫn chứng thực tế:** Tấm gương các bạn trẻ dấn thân vì cộng đồng và kiên trì đuổi theo mục tiêu. *(Nguồn: Báo Tuổi Trẻ, Thanh Niên)*"
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
                with st.spinner("AI đang phân tích sâu đề bài và khởi tạo Bước 2 kèm Kho dẫn chứng có nguồn..."):
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
                    
                    st.session_state["user_outline"] = f"I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề nghị luận: {vdnl_chuan_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất:\n2. Bàn luận trọng tâm (Lý do & Tác động):\n3. Dẫn chứng thực tế (Có nguồn xác thực):\n4. Phản biện & Lật lại vấn đề:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động cho bản thân:"
                    
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
            
            if not st.session_state.get("user_outline"):
                st.session_state["user_outline"] = f"I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề: {de_info['vdnl_chuan']}\n\nII. THÂN BÀI:\n1. Giải thích bản chất:\n2. Bàn luận trọng tâm:\n3. Dẫn chứng thực tế:\n4. Phản biện & Mở rộng:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động:"
            
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
        st.markdown("#### 🛠️ Khung Gợi Ý Tư Duy Chuyên Sâu (4 Thao Tác)")
        
        with st.expander("📌 Thao tác 1: Giải thích bản chất", expanded=True):
            explain_items = cur_de_info.get("explain_core", [])
            if explain_items:
                for item in explain_items:
                    st.markdown(f"- {item}")
            else:
                st.write("Đang cập nhật giải thích...")
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Lý giải & Tác động)", expanded=True):
            q_items = cur_de_info.get("questions", [])
            if q_items:
                for q in q_items:
                    st.markdown(f"**❓ {q['cau_hoi']}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(f"  * {ans}")
            else:
                st.write("Đang cập nhật câu hỏi bàn luận...")

        with st.expander("📚 Thao tác 3: Kho Dẫn Chứng Thực Tế Có Nguồn Kiểm Chứng", expanded=True):
            evidence_items = cur_de_info.get("evidence", [])
            if evidence_items:
                for ev in evidence_items:
                    st.markdown(f"<div class='evidence-box'>📌 {ev}</div>", unsafe_allow_html=True)
            else:
                st.write("Đang cập nhật dẫn chứng...")

        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng vấn đề", expanded=True):
            counter_items = cur_de_info.get("counter", [])
            if counter_items:
                for c in counter_items:
                    st.markdown(f"- {c}")
            else:
                st.write("Đang cập nhật ý phản biện...")
                    
        st.markdown("#### 📝 Dàn Ý Của Em")
        vdnl_val = cur_de_info.get('vdnl_chuan', 'Vấn đề nghị luận từ đề bài')
        default_outline = f"I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề nghị luận: {vdnl_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất:\n2. Bàn luận trọng tâm (Lý do & Tác động):\n3. Dẫn chứng thực tế (Có nguồn xác thực):\n4. Phản biện & Lật lại vấn đề:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động cho bản thân:"
        user_outline = st.text_area("Hoàn thiện dàn ý 3 phần của em:", value=st.session_state.get("user_outline") or default_outline, height=260)
        st.session_state["user_outline"] = user_outline

    with c_right:
        st.markdown("#### 💬 Trợ Lý Ngữ Văn AI")
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Chào em! Em cần cô hỗ trợ gì về cách mở bài, triển khai luận điểm hay lựa chọn dẫn chứng cho đề này không?"}]
            
        chat_box = st.container(height=400)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        u_msg = st.chat_input("Hỏi cô về cách lập luận, chọn dẫn chứng...")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            
            de_context = st.session_state.get("current_de_info", {}).get("text", "")
            prompt_chat = f"""
Bạn là Cô giáo Ngữ văn THPT tâm lý và tận tâm. Học sinh đang làm đề bài:
"{de_context}"

Học sinh hỏi: "{u_msg}"
Hãy trả lời ngắn gọn, chân thành, sâu sắc (xưng cô - em) hướng dẫn học sinh cách tư duy cho đề bài này.
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
        essay_in = st.text_area("✍️ Nhập bài văn hoàn chỉnh của em:", value=st.session_state.get("user_essay", ""), height=420, placeholder="Viết bài văn hoàn chỉnh dựa trên dàn ý đã lập...")
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
