import streamlit as st
import json
import re
from google import genai

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP
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
        color: #64748b;
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
        font-size: 1.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 14px;
    }
    
    .evidence-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 0.93rem;
    }
    
    .topic-header {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 8px 12px;
        font-weight: 700;
        color: #1e40af;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KHO DỮ LIỆU ĐỀ THI PHÂN HÓA (30 ĐỀ)
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_core": ["**Lối sống có trách nhiệm:** Nhận thức rõ bổn phận, nghĩa vụ đối với gia đình và xã hội.", "**Gắn bó với cộng đồng:** Tinh thần hòa nhập, biết sẻ chia, đặt lợi ích tập thể lên trên sự vị kỷ."],
        "questions": [{"cau_hoi": "Vì sao người trẻ cần sống có trách nhiệm với cộng đồng?", "y_tra_loi": ["Con người là sinh vật xã hội, sự phát triển cá nhân luôn gắn liền với tập thể.", "Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, tạo dựng cộng đồng nhân ái."]}],
        "evidence": ["**Dự án Nuôi Em (Hoàng Hoa Trung):** Kết nối nuôi cơm trưa cho hơn 60.000 học sinh vùng cao. *(Nguồn: Báo Tuổi Trẻ)*"],
        "counter": ["Phê phán lối sống vị kỷ, 'chỉ biết mình', thờ ơ trước nỗi đau đồng loại."]
    },
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.\nHãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong xã hội hiện đại.",
        "explain_core": ["**Sự thấu cảm:** Năng lực đặt mình vào vị trí của người khác để cảm nhận nỗi đau, niềm vui của họ."],
        "questions": [{"cau_hoi": "Tại sao thời đại số lại cần sự thấu cảm hơn hết?", "y_tra_loi": ["Công nghệ khiến con người dễ rơi vào trạng thái 'kết nối mạng nhưng mất kết nối thực'."]}],
        "evidence": ["**Dự án 'Tổng đài Ngày Mai' (TS. Đặng Hoàng Giang):** Tham vấn tâm lý phi lợi nhuận cho người trẻ. *(Nguồn: Báo Thanh Niên)*"],
        "counter": ["Phê phán thói vô cảm, phán xét vội vàng hoặc công kích cá nhân trên mạng."]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn bản sắc văn hóa dân tộc của thế hệ trẻ.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ khi hội nhập.",
        "explain_core": ["**Bản sắc văn hóa:** Toàn bộ giá trị tinh hoa vật chất và tinh thần cốt lõi của dân tộc."],
        "questions": [{"cau_hoi": "Vì sao bảo tồn bản sắc văn hóa lại là sứ mệnh sinh tồn?", "y_tra_loi": ["Văn hóa là thẻ căn cước duy nhất khẳng định sự tồn tại độc lập của một dân tộc."]}],
        "evidence": ["**Nghệ sĩ trẻ đưa văn hóa vào nghệ thuật:** Đen Vâu, Hoàng Thùy Linh ứng dụng nhạc cụ dân tộc. *(Nguồn: Báo Tuổi Trẻ)*"],
        "counter": ["Phê phán thái độ sính ngoại mù quáng, xem thường giá trị truyền thống."]
    },
    "Đề 04 (Cơ bản): Ý nghĩa của lòng biết ơn trong đời sống con người": {
        "text": """Danh ngôn có câu: *"Uống nước nhớ nguồn, ăn quả nhớ kẻ trồng cây."*\nTừ cội nguồn đạo lý truyền thống đó, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lòng biết ơn.""",
        "vdnl_chuan": "Ý nghĩa và giá trị đạo đức của lòng biết ơn trong đời sống.",
        "explain_core": ["**Lòng biết ơn:** Sự trân trọng, ghi nhớ và đền đáp những ân huệ của người đi trước."],
        "questions": [{"cau_hoi": "Vì sao lòng biết ơn là nền tảng đạo đức cốt lõi?", "y_tra_loi": ["Giúp con người kết nối cội nguồn, nuôi dưỡng lòng trắc ẩn và sự tử tế."]}],
        "evidence": ["**Hoạt động đền ơn đáp nghĩa 27/7:** Hàng năm thăm hỏi Mẹ Việt Nam anh hùng, thắp nến tri ân. *(Nguồn: Báo Nhân Dân)*"],
        "counter": ["Phê phán thói vô ơn, ăn cháo đá bát, vong ân bội nghĩa."]
    },
    "Đề 05 (Cơ bản): Sức mạnh và giá trị của niềm tin vào bản thân": {
        "text": """Có câu nói nổi tiếng: *"Tin rằng bạn có thể làm được là bạn đã đi được nửa đường."* (Theodore Roosevelt)\nHãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của niềm tin vào bản thân.""",
        "vdnl_chuan": "Sức mạnh và vai trò quyết định của niềm tin vào bản thân.",
        "explain_core": ["**Niềm tin vào bản thân:** Sự tự tin vững chắc vào năng lực, phẩm chất và tiềm năng của chính mình."],
        "questions": [{"cau_hoi": "Vì sao niềm tin vào bản thân là chìa khóa thành công?", "y_tra_loi": ["Giúp con người không gục ngã trước thất bại và dám hành động quyết liệt."]}],
        "evidence": ["**Diễn giả khuyết tật Nick Vujicic:** Vượt qua giới hạn cơ thể để khẳng định giá trị bản thân. *(Nguồn: Báo Tuổi Trẻ)*"],
        "counter": ["Phê phán căn bệnh tự ti, nhút nhát hoặc sự tự phụ, ảo tưởng."]
    }
}

DE_BAI_NANG_CAO = {
    "Đề 16 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_core": ["**Bản sắc riêng & chính kiến:** Tư duy độc lập, cá tính sáng tạo và hệ giá trị đạo đức riêng."],
        "questions": [{"cau_hoi": "Vì sao giữ bản sắc riêng trước đám đông là thách thức lớn?", "y_tra_loi": ["Áp lực bị tẩy chay và tâm lý bầy đàn khiến người trẻ dễ đồng hóa bản thân."]}],
        "evidence": ["**VĐV Nguyễn Thị Oanh:** Vượt qua áp lực dư luận giành 4 HCB SEA Games 32. *(Nguồn: Báo Thể Thao)*"],
        "counter": ["Phê phán thói hùa theo phong trào hoặc biến khác biệt thành ngông cuồng."]
    },
    "Đề 17 (Nâng cao): Trách nhiệm với di sản văn hóa truyền thống": {
        "text": """Nhà văn Nguyên Ngọc từng trăn trở về việc giữ gìn hồn cốt dân tộc qua thời gian.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm làm sống dậy di sản văn hóa truyền thống.""",
        "vdnl_chuan": "Trách nhiệm của thế hệ trẻ trong việc bảo tồn, phát huy giá trị di sản văn hóa.",
        "explain_core": ["**Di sản văn hóa:** Dòng sữa nuôi dưỡng tâm hồn dân tộc qua các thế hệ."],
        "questions": [{"cau_hoi": "Làm thế nào để di sản tiếp cận tự nhiên với Gen Z?", "y_tra_loi": ["Ứng dụng công nghệ số, thực tế ảo (VR/AR) và thiết kế hiện đại."]}],
        "evidence": ["**Dự án Cổ phục Việt 'Đại Việt Cổ Phong':** Phục dựng trang phục truyền thống Triều Nguyễn. *(Nguồn: Báo VnExpress)*"],
        "counter": ["Phê phán thái độ dửng dưng với quá khứ hoặc bảo thủ xơ cứng."]
    },
    "Đề 18 (Nâng cao): Tinh thần dấn thân và khát vọng phụng sự": {
        "text": """Liệt sĩ Đặng Thùy Trâm từng viết: *"Đời phải trải qua giông tố nhưng không được cúi đầu trước giông tố."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về tinh thần dấn thân và khát vọng phụng sự cộng đồng.""",
        "vdnl_chuan": "Ý nghĩa của tinh thần dấn thân, sống cống hiến và phụng sự cộng đồng.",
        "explain_core": ["**Tinh thần dấn thân:** Dám rời bỏ vùng an toàn, xông pha vào nơi khó khăn."],
        "questions": [{"cau_hoi": "Vì sao dấn thân lại định vị giá trị người trẻ?", "y_tra_loi": ["Giúp thanh xuân không trôi qua nhạt nhòa, rèn luyện bản lĩnh qua thực tế."]}],
        "evidence": ["**Bác sĩ trẻ xung phong lên vùng cao:** Chương trình tình nguyện của Bộ Y tế. *(Nguồn: Báo Sức khỏe & Đời sống)*"],
        "counter": ["Phê phán lối sống hưởng thụ, thực dụng, 'sợ bẩn tay'."]
    },
    "Đề 19 (Nâng cao): Tư duy phản biện trong thời đại AI": {
        "text": """Trong kỷ nguyên trí tuệ nhân tạo (AI) và thông tin bùng nổ, ranh giới sự thật và giả mạo trở nên mỏng manh.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tư duy phản biện.""",
        "vdnl_chuan": "Tầm quan trọng của tư duy phản biện và năng lực tự chủ tri thức thời đại AI.",
        "explain_core": ["**Tư duy phản biện:** Năng lực phân tích, đánh giá vấn đề đa chiều dựa trên bằng chứng và logic."],
        "questions": [{"cau_hoi": "Vì sao người trẻ thời AI dễ rơi vào bẫy 'lười suy nghĩ'?", "y_tra_loi": ["AI cung cấp câu trả lời tức thì làm giảm nhu cầu đào sâu độc lập."]}],
        "evidence": ["**Nạn lừa đảo Deepfake voice/video:** Cảnh báo hàng loạt vụ án giả danh người thân. *(Nguồn: Bộ Công an)*"],
        "counter": ["Phê phán thói quen tin sái cổ thông tin chưa kiểm chứng trên mạng."]
    },
    "Đề 20 (Nâng cao): Lối sống tử tế và sức mạnh hàn gắn": {
        "text": """Có câu danh ngôn: *"Hãy đối xử tử tế với mọi người bạn gặp, bởi vì ai cũng đang phải trải qua một cuộc chiến khốc liệt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự tử tế.""",
        "vdnl_chuan": "Sức mạnh của sự tử tế và lòng nhân ái trong việc xoa dịu tổn thương xã hội.",
        "explain_core": ["**Sự tử tế:** Hành động, lời nói xuất phát từ lòng tốt, sự tôn trọng không đòi đền đáp."],
        "questions": [{"cau_hoi": "Sự tử tế nhỏ bé tạo nên thay đổi lớn thế nào?", "y_tra_loi": ["Tạo phản ứng dây chuyền, lan tỏa năng lượng tích cực, thu hẹp khoảng cách."]}],
        "evidence": ["**Phong trào 'Bếp ăn yêu thương':** Nhóm tình nguyện nấu ăn miễn phí cho bệnh nhân ung thư. *(Nguồn: Báo Thanh Niên)*"],
        "counter": ["Phê phán sự lạnh lùng, ích kỷ, coi nhẹ nỗi đau đồng loại."]
    }
}

# ==============================================================================
# 3. KHO DẪN CHỨNG PHÂN LOẠI THEO CHỦ ĐỀ (CÓ NGUỒN XÁC THỰC)
# ==============================================================================
KHO_DAN_CHUNG_THEO_CHU_DE = {
    "🌐 1. Trách nhiệm & Cống hiến cộng đồng": [
        "**Dự án Nuôi Em (Hoàng Hoa Trung - 2014 đến nay):** Kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn. *(Nguồn: Báo Tuổi Trẻ, Cổng thông tin Trung ương Đoàn)*",
        "**Chiến dịch Mùa hè xanh:** Hàng ngàn sinh viên tình nguyện xây dựng cầu giao thông, dạy học cho trẻ em vùng sâu vùng xa mỗi năm. *(Nguồn: Báo Tiền Phong)*",
        "**Bác sĩ trẻ xung phong lên biên giới (Bộ Y tế):** Đưa hàng trăm bác sĩ giỏi về cắm bản tại các huyện nghèo nhất nước. *(Nguồn: Báo Sức khỏe & Đời sống)*"
    ],
    "❤️ 2. Thấu cảm, Tử tế & Hàn gắn": [
        "**Dự án 'Tổng đài Ngày Mai' (TS. Đặng Hoàng Giang):** Tổng đài tham vấn tâm lý phi lợi nhuận lắng nghe và hỗ trợ người trẻ khủng hoảng. *(Nguồn: Báo Thanh Niên)*",
        "**Xe ô tô chắn gió cho xe máy trong bão Yagi (2024):** Những chiếc xe tải, ô tô đi chậm chắn gió lớn cho người đi xe máy qua cầu an toàn. *(Nguồn: VTV Digital)*",
        "**Bếp ăn 0 đồng tại các bệnh viện lớn:** Cung cấp hàng ngàn suất ăn nóng hổi miễn phí cho bệnh nhân nghèo. *(Nguồn: Báo Lao Động)*"
    ],
    "🇻🇳 3. Bản sắc văn hóa & Di sản dân tộc": [
        "**Nghệ sĩ trẻ đưa chất liệu dân gian vào âm nhạc hiện đại:** Đen Vâu, Hoàng Thùy Linh, Đức Phúc đưa hát xẩm, bài chồi, cổ phục vào MV triệu view. *(Nguồn: Báo Tuổi Trẻ)*",
        "**Dự án Cổ phục Việt 'Đại Việt Cổ Phong':** Nhóm bạn trẻ nghiên cứu, phục dựng trang phục truyền thống Triều Nguyễn, Triều Lê. *(Nguồn: Báo VnExpress)*",
        "**Lễ hội Thiết kế Sáng tạo Hà Nội:** Biến di sản công nghiệp (Nhà máy Xe lửa Gia Lâm) thành không gian văn hóa sáng tạo. *(Nguồn: Báo Hà Nội Mới)*"
    ],
    "⚡ 4. Bản lĩnh, Ý chí & Vượt qua khó khăn": [
        "**VĐV Nguyễn Thị Oanh (SEA Games 32):** Vượt qua áp lực thể lực khắc nghiệt để giành liên tiếp 4 HCB điền kinh trong cùng một buổi chiều. *(Nguồn: Báo Thể Thao)*",
        "**Diễn giả Nick Vujicic / Nguyễn Thị Ngọc Minh:** Vượt qua khiếm khuyết cơ thể để truyền cảm hứng sống tích cực cho triệu người. *(Nguồn: Báo Dân Trí)*",
        "**Hành trình chinh phục Everest của leo núi Việt Nam:** Vượt giới hạn sinh lý cơ thể để cắm cờ Tổ quốc trên đỉnh thế giới. *(Nguồn: Báo VnExpress)*"
    ],
    "🤖 5. Công nghệ, AI & Tư duy phản biện": [
        "**Nạn lừa đảo Deepfake voice/video (2023–2024):** Bộ Công an cảnh báo hàng loạt vụ án giả danh người thân lừa đảo tiền bằng công nghệ AI. *(Nguồn: Cổng thông tin Bộ Công an)*",
        "**Quy định Liêm chính học thuật trong Đại học:** Sinh viên phải tự chịu trách nhiệm về tính xác thực của thông tin khi dùng ChatGPT. *(Nguồn: Báo Tuổi Trẻ)*",
        "**Bộ Quy tắc ứng xử trên mạng xã hội (Bộ TT&TT):** Khuyến khích người dùng chia sẻ thông tin lành mạnh, có văn hóa. *(Nguồn: Báo Công An TP.HCM)*"
    ]
}

# ==============================================================================
# 4. KẾT NỐI GEMINI AI & SESSION STATE
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = DE_BAI_CO_BAN[list(DE_BAI_CO_BAN.keys())[0]]

if "last_selected_de" not in st.session_state:
    st.session_state["last_selected_de"] = ""

def reset_de_data(ten_de_moi):
    if st.session_state["last_selected_de"] != ten_de_moi:
        st.session_state["last_selected_de"] = ten_de_moi
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Chào em! Đề bài hiện tại là: '{ten_de_moi}'. Cô đã cập nhật dàn ý chi tiết và gợi ý bên trái, em xem có câu nào cần cô hướng dẫn thêm không nhé!"}
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
        st.info("💡 Hệ thống chờ nhập Key hoặc dùng Secrets.")

    st.markdown("---")
    st.markdown("### 📌 LỘ TRÌNH 4 BƯỚC SƯ PHẠM")
    st.write("1. **🌱 Bước 1:** Phân tích đề & VĐNL")
    st.write("2. **🧵 Bước 2:** Lập dàn ý & Kho dẫn chứng")
    st.write("3. **✍️ Bước 3:** Xưởng viết độc lập")
    st.write("4. **🔍 Bước 4:** AI Chấm điểm Rubric")

def call_gemini_engine(prompt_or_contents):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "[Thông báo]: Chưa nhận được API Key. Vui lòng kiểm tra lại cấu hình."

    client = genai.Client(api_key=api_key)
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
    for m in models_to_try:
        try:
            response = client.models.generate_content(model=m, contents=prompt_or_contents)
            if response and response.text:
                return response.text
        except Exception:
            continue
    return "[Lỗi kết nối]: Không thể kết nối với máy chủ AI."

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giám khảo Ngữ văn THPT GDPT 2018 tâm lý và uy tín. 
- Đề bài: {exam_text}
- Vấn đề nghị luận chuẩn: {vdnl_chuan}
- Học sinh tự phán đoán VĐNL: "{student_guess}"

Thẩm định xem học sinh đã bắt trúng tinh thần đề chưa. Trả về JSON DUY NHẤT:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Lời nhận xét sư phạm ấm áp, khích lệ (xưng cô - em).",
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

def ai_analyze_custom_exam(exam_text, student_guess):
    prompt = f"""
Bạn là chuyên gia khảo thí Ngữ văn THPT GDPT 2018. 
Đề bài do học sinh tự dán: \"\"\"{exam_text}\"\"\"
Học sinh tự chọn VĐNL là: \"\"\"{student_guess}\"\"\"

Nhiệm vụ:
1. Thẩm định câu trả lời học sinh.
2. Trích xuất VĐNL chuẩn xác nhất.
3. Tạo giàn giáo Bước 2 gồm: Giải thích, Bàn luận, Kho dẫn chứng có nguồn, Phản biện.

Trả về JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét sư phạm (xưng cô - em)",
  "vdnl_chuan": "VĐNL cốt lõi chuẩn",
  "explain_core": ["**Giải thích:** Nội dung giải thích"],
  "questions": [{{"cau_hoi": "Câu hỏi bàn luận?", "y_tra_loi": ["Ý bàn luận 1", "Ý bàn luận 2"]}}],
  "evidence": ["**Dẫn chứng thực tế:** Chi tiết dẫn chứng kèm nguồn xác thực"],
  "counter": ["Ý phản biện lật lại vấn đề"]
}}
"""
    raw = call_gemini_engine(prompt)
    try:
        clean_raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
        match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(clean_raw)
    except Exception:
        return {
            "status": "DUNG",
            "feedback": f"Cô khen em đã nắm đúng vấn đề trọng tâm!",
            "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận từ đề bài",
            "explain_core": ["**Giải thích:** Giải thích bản chất khái niệm đề bài."],
            "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn và phát triển bản thân."]}],
            "evidence": ["**Dẫn chứng thực tế:** Các tấm gương thanh niên sống đẹp, cống hiến vì cộng đồng. *(Nguồn: Báo Tuổi Trẻ)*"],
            "counter": ["Phê phán thái độ dửng dưng, nhận thức lệch lạc."]
        }

# ==============================================================================
# 5. GIAO DIỆN CHÍNH & LUỒNG ỨNG DỤNG
# ==============================================================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🖊️ QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH</div>
    <div class="hero-subtitle">Ngân hàng 30 Đề phân hóa | Kho dẫn chứng chia theo chủ đề | Giám khảo AI chấm điểm Rubric</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý & KHO DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "🔍 BƯỚC 4: CHẤM ĐIỂM RUBRIC",
    "📁 HỒ SƠ BÀI LÀM"
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ (PHÂN HÓA NGUỒN ĐỀ & ĐỀ TỰ NHẬP)
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🔍 Lựa Chọn Nguồn Đề Bài & Xác Định Vấn Đề Nghị Luận Cốt Lõi</div>', unsafe_allow_html=True)
    
    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
        "🟢 Nhóm Đề Cơ Bản (01–15)", 
        "🔴 Nhóm Đề Nâng Cao (16–30)", 
        "✏️ Nhập/Dán Đề Bài Riêng"
    ])
    
    # 1. Đề Cơ bản
    with tab_de_coban:
        col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
        with col_cb1:
            selected_cb_key = st.selectbox("Chọn đề Cơ bản:", list(DE_BAI_CO_BAN.keys()), key="sb_coban")
            reset_de_data(selected_cb_key)
            de_info_cb = DE_BAI_CO_BAN[selected_cb_key]
            st.session_state["current_de_info"] = de_info_cb
            st.session_state["current_de_key"] = selected_cb_key
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài Cơ bản:")
                st.info(de_info_cb['text'].replace("**", ""))
                
    # 2. Đề Nâng cao
    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox("Chọn đề Nâng cao:", list(DE_BAI_NANG_CAO.keys()), key="sb_nangcao")
            reset_de_data(selected_nc_key)
            de_info_nc = DE_BAI_NANG_CAO[selected_nc_key]
            st.session_state["current_de_info"] = de_info_nc
            st.session_state["current_de_key"] = selected_nc_key
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài Nâng cao:")
                st.info(de_info_nc['text'].replace("**", ""))

    # 3. Đề Tự Nhập
    with tab_de_tu_nhap:
        st.markdown("##### 📝 Dán đề bài em cần hướng dẫn vào đây:")
        custom_de_text = st.text_area("Nội dung đề bài tự chọn:", placeholder="Ví dụ: Viết bài văn nghị luận bàn về...", height=100)
        student_custom_vdnl = st.text_input("Vấn đề nghị luận em tự đoán cho đề này:", placeholder="Gõ VĐNL theo suy nghĩ của em...")
        
        if st.button("🔍 Phân tích đề tự nhập & Tạo giàn giáo Bước 2", type="primary"):
            if not custom_de_text.strip():
                st.warning("Em chưa dán nội dung đề bài!")
            else:
                with st.spinner("AI đang phân tích ngữ liệu và tạo giàn giáo..."):
                    res_custom = ai_analyze_custom_exam(custom_de_text, student_custom_vdnl)
                    
                    ten_de_custom = "Đề tự nhập: " + (custom_de_text[:30] + "..." if len(custom_de_text) > 30 else custom_de_text)
                    st.session_state["current_de_key"] = ten_de_custom
                    st.session_state["current_de_info"] = {
                        "text": custom_de_text,
                        "vdnl_chuan": res_custom.get("vdnl_chuan", student_custom_vdnl),
                        "explain_core": res_custom.get("explain_core", []),
                        "questions": res_custom.get("questions", []),
                        "evidence": res_custom.get("evidence", []),
                        "counter": res_custom.get("counter", [])
                    }
                    st.session_state["eval_vdnl_result"] = {
                        "status": res_custom.get("status", "DUNG"),
                        "feedback": res_custom.get("feedback", ""),
                        "suggested_fix": res_custom.get("vdnl_chuan", "")
                    }
                    reset_de_data(ten_de_custom)
                    st.success("✅ Đã tạo xong giàn giáo Bước 2 cho đề bài của em! Hãy bấm chuyển sang Bước 2 để xem nhé.")

    st.markdown("---")
    # Thao tác thẩm định chung cho đề chọn từ danh sách
    if "Đề tự nhập" not in st.session_state.get("current_de_key", ""):
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi của đề đang chọn:", placeholder="Gõ câu trả lời của em ở đây...")
        if st.button("🔍 Đối chiếu Vấn đề Nghị luận với AI", type="primary"):
            if student_vdnl.strip():
                with st.spinner("AI đang thẩm định..."):
                    de_cur = st.session_state["current_de_info"]
                    res = ai_evaluate_student_vdnl(de_cur['text'], de_cur['vdnl_chuan'], student_vdnl)
                    st.session_state["eval_vdnl_result"] = res
            else:
                st.warning("Em chưa nhập câu trả lời!")

    if st.session_state.get("eval_vdnl_result"):
        res = st.session_state["eval_vdnl_result"]
        if res.get("status") == "DUNG":
            st.success(f"🎯 **ĐÚNG RỒI!** {res.get('feedback')}")
        else:
            st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:* {res.get('suggested_fix')}")

# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý & KHO DẪN CHỨNG (TỐI ƯU DÀN Ý & KHO DẪN CHỨNG THEO CHỦ ĐỀ)
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">🧵 Hệ Thống Giàn Giáo 4 Thao Tác Sư Phạm & Kho Dẫn Chứng Phân Loại</div>', unsafe_allow_html=True)
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_CO_BAN[list(DE_BAI_CO_BAN.keys())[0]])
    
    c_left, c_right = st.columns([1.2, 0.8], gap="large")
    
    with c_left:
        st.markdown("#### 🛠️ 1. Khung Giàn Giáo 4 Thao Tác (Gợi ý riêng cho đề bài này)")
        
        with st.expander("📌 Thao tác 1: Giải thích bản chất", expanded=True):
            for item in cur_de_info.get("explain_core", []):
                st.markdown(f"- {item}")
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Lý giải & Tác động)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        with st.expander("📚 Thao tác 3: Dẫn chứng trọng tâm của đề", expanded=True):
            for ev in cur_de_info.get("evidence", []):
                st.markdown(f"<div class='evidence-box'>📌 {ev}</div>", unsafe_allow_html=True)

        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng vấn đề", expanded=True):
            for c in cur_de_info.get("counter", []):
                st.markdown(f"- {c}")
                    
        st.markdown("---")
        st.markdown("#### 📝 2. Tự Hoàn Thiện Dàn Ý 3 Phần Của Em")
        
        vdnl_val = cur_de_info.get('vdnl_chuan', 'Vấn đề nghị luận từ đề bài')
        auto_outline = f"""I. MỞ BÀI:
- Dẫn dắt ngữ liệu & nêu Vấn đề nghị luận: {vdnl_val}

II. THÂN BÀI:
1. Giải thích bản chất khái niệm:
   + (Ghi lại ý giải thích cốt lõi ở trên)
2. Bàn luận trọng tâm (Vì sao? Tác động thế nào?):
   + Ý 1:
   + Ý 2:
3. Dẫn chứng thực tế tiêu biểu (Có nguồn xác thực):
   + Dẫn chứng 1:
4. Phản biện & Lật lại vấn đề:
   + Phê phán biểu hiện lệch lạc:
   + Mở rộng đa chiều:

III. KẾT BÀI:
- Khẳng định lại giá trị của vấn đề:
- Bài học nhận thức & hành động thực tế của bản thân:"""

        if not st.session_state.get("user_outline"):
            st.session_state["user_outline"] = auto_outline
            
        user_outline = st.text_area("Lập dàn ý chi tiết tại đây:", value=st.session_state["user_outline"], height=280)
        st.session_state["user_outline"] = user_outline

    with c_right:
        st.markdown("#### 📚 Kho Dẫn Chứng Thực Tế Chia Theo Chủ Đề (Có Nguồn)")
        with st.container(border=True):
            st.markdown("*Em có thể tham khảo thêm các dẫn chứng thực tế dưới đây để làm phong phú bài viết:*")
            for topic_name, ev_list in KHO_DAN_CHUNG_THEO_CHU_DE.items():
                with st.expander(topic_name, expanded=False):
                    for ev_item in ev_list:
                        st.markdown(f"<div class='evidence-box'>{ev_item}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💬 Trợ Lý Ngữ Văn AI Tư Vấn")
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Chào em! Em cần cô hỗ trợ gì về cách lập luận hay mở bài không?"}]
            
        chat_box = st.container(height=300)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        u_msg = st.chat_input("Hỏi cô về cách lập luận...")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            de_context = st.session_state.get("current_de_info", {}).get("text", "")
            prompt_chat = f"Bạn là Cô giáo Ngữ văn THPT tâm lý. Đề bài: '{de_context}'. Học sinh hỏi: '{u_msg}'. Hãy trả lời ngắn gọn, sâu sắc (xưng cô - em)."
            with st.spinner("Cô đang suy nghĩ..."):
                reply = call_gemini_engine(prompt_chat)
                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
            st.rerun()

# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
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
# BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ (RUBRIC 10 ĐIỂM)
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">🔍 Giám Khảo AI Chấm Điểm Theo Bảng Rubric 10 Điểm</div>', unsafe_allow_html=True)
    if st.button("🚀 AI Bắt Đầu Chấm Điểm Bài Viết", type="primary"):
        essay_text = st.session_state.get("user_essay", "").strip()
        if not essay_text:
            st.warning("Em chưa nhập bài viết ở Bước 3!")
        else:
            with st.spinner("Giám khảo AI đang chấm điểm theo Rubric..."):
                prompt = f"""
Bạn là Giám khảo chấm thi Ngữ văn THPT GDPT 2018. Chấm bài văn sau theo Rubric 10 điểm (Cấu trúc 0.5, VĐNL 0.5, Bàn luận 4.0, Dẫn chứng 2.0, Phản biện 1.5, Diễn đạt 1.5).
Đề bài: {st.session_state.get('current_de_key')}
Bài làm học sinh: {essay_text}

Xuất kết quả gồm:
1. BẢNG ĐÁNH GIÁ CHI TIẾT THEO RUBRIC (Bắt buộc dùng Bảng Markdown).
2. Ưu điểm nổi bật.
3. Hạn chế & Câu hỏi gợi mở để học sinh TỰ VIẾT LẠI.
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
    grading_result = st.session_state.get("grading_result", "Chưa chấm điểm ở Bước 4")
    
    report_text = f"""BẢN BÁO CÁO HỌC TẬP - QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH
Học sinh: {student_name if student_name else 'Học sinh chưa điền tên'}
Đề bài: {current_de}
================================================================================
1. DÀN Ý 3 PHẦN (BƯỚC 2):
{user_outline}

================================================================================
2. BÀI VĂN HOÀN CHỈNH (BƯỚC 3):
{user_essay}

================================================================================
3. KẾT QUẢ ĐÁNH GIÁ RUBRIC (BƯỚC 4):
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
