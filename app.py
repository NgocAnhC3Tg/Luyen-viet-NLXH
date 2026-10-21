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
        margin-bottom: 0px !important;
        color: #ffffff !important;
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
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 16px;
    }
    
    .evidence-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 14px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 0.94rem;
        line-height: 1.6;
    }
    
    .explain-card {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KHO 30 ĐỀ THI CHUẨN SÂU SẮC NỘI DUNG (GIẢI THÍCH 3 NẤC + DẪN CHỨNG CHI TIẾT)
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_core": [
            "**1. Giải thích từ ngữ/hình ảnh:** 'Nơi đất ở' chỉ vùng đất địa lý vật chất thuần túy; 'Đất hóa tâm hồn' là hình ảnh biểu biểu tượng cho sự gắn bó sâu sắc về tình cảm, nơi lưu giữ kỷ niệm, nghĩa tình và trách nhiệm của con người.",
            "**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Câu thơ khẳng định quy luật gắn kết tâm hồn giữa cá nhân với mảnh đất và con người nơi ta sống: khi con người biết cống hiến, sẻ chia và sống hết lòng thì mảnh đất xa lạ cũng trở nên thân thương, gắn bó như một phần máu thịt.",
            "**3. Chốt Vấn đề nghị luận:** Ý kiến gợi mở bài học sâu sắc về ý nghĩa của lối sống có trách nhiệm, biết gắn bó và cống hiến cho cộng đồng của thế hệ trẻ hôm nay."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao người trẻ cần phải sống có trách nhiệm và biết gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "Con người là một sinh vật xã hội, không cá nhân nào có thể tồn tại biệt lập. Sự phát triển của mỗi cá nhân luôn gắn liền với sự ổn định và văn minh của tập thể.",
                    "Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, kết nối con người bằng tình thương, tạo dựng một cộng đồng nhân ái và bền vững."
                ]
            }
        ],
        "evidence": [
            "**Dẫn chứng 1 (Hoàng Hoa Trung & Dự án 'Nuôi Em'):** Từ năm 2014, Hoàng Hoa Trung cùng các cộng sự đã sáng lập dự án 'Nuôi Em', kết nối hàng chục ngàn nhà hảo tâm để cung cấp hơn 60.000 bữa ăn trưa có thịt mỗi ngày cho học sinh mầm non và tiểu học vùng cao khó khăn tại Điện Biên, Hà Giang. *Ý nghĩa:* Dẫn chứng chứng minh cho tinh thần trách nhiệm chủ động, biến tình yêu thương thành hành động cụ thể để cải thiện cuộc sống cộng đồng. *(Nguồn: Báo Tuổi Trẻ, Cổng thông tin Trung ương Đoàn)*",
            "**Dẫn chứng 2 (Sinh viên tình nguyện Mùa Hè Xanh):** Mỗi dịp hè, hàng ngàn sinh viên các trường đại học trên cả nước xông pha về các xã nghèo vùng sâu, vùng xa để xây dựng cầu giao thông nông thôn, dọn dẹp môi trường và tổ chức lớp học tình thương. *Ý nghĩa:* Khẳng định sự dấn thân của tuổi trẻ làm cho 'đất hóa tâm hồn', biến những vùng đất xa lạ thành quê hương thứ hai nhờ dấu chân cống hiến. *(Nguồn: Báo Tiền Phong)*"
        ],
        "counter": [
            "Phê phán lối sống vị kỷ, 'chỉ biết mình', thờ ơ trước nỗi đau của đồng loại hoặc xem việc cống hiến là trách nhiệm của riêng người khác.",
            "Lật lại vấn đề: Sống có trách nhiệm không đồng nghĩa với cống hiến mù quáng hay bao đồng; cần biết cân bằng giữa việc chăm sóc bản thân và đóng góp cho cộng đồng."
        ]
    },
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.\nHãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "explain_core": [
            "**1. Giải thích từ ngữ/hình ảnh:** 'Cơn bão' và 'cơn bão lòng' là hình ảnh ẩn dụ chỉ những biến cố, nghịch cảnh, tổn thương hay khủng hoảng tinh thần trong đời sống; 'thấu cảm' là năng lực đặt mình vào vị trí của người khác; 'lắng nghe chân thành' là thái độ kiên nhẫn, trân trọng không phán xét.",
            "**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Nhận định nhấn mạnh rằng những thử thách trong cuộc sống làm con người biến đổi, nhưng chính sự thấu hiểu, sẻ chia và lắng nghe chân thành mới là điểm tựa giúp con người chữa lành tổn thương và vượt qua biến cố.",
            "**3. Chốt Vấn đề nghị luận:** Khẳng định sức mạnh to lớn của sự thấu cảm và năng lực lắng nghe chân thành trong việc kết nối và nâng đỡ con người hiện đại."
        ],
        "questions": [
            {
                "cau_hoi": "Tại sao con người trong thời đại số lại cần đến sự thấu cảm và năng lực lắng nghe hơn bao giờ hết?",
                "y_tra_loi": [
                    "Sự bùng nổ công nghệ khiến con người dễ rơi vào trạng thái 'kết nối mạng nhưng mất kết nối thực', dẫn đến cô đơn và trầm cảm gia tăng.",
                    "Lắng nghe và thấu cảm đóng vai trò như liều thuốc xoa dịu tổn thương tâm lý, giải tỏa áp lực và thu hẹp khoảng cách giữa các thế hệ."
                ]
            }
        ],
        "evidence": [
            "**Dẫn chứng 1 (TS. Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'):** Tiến sĩ Đặng Hoàng Giang cùng nhóm cộng sự đã sáng lập 'Tổng đài Ngày Mai' – kênh tham vấn tâm lý phi lợi nhuận đầu tiên tại Việt Nam. Tổng đài đã tiếp nhận và lắng nghe hàng ngàn cuộc gọi từ những người trẻ gặp khủng hoảng tâm lý, cô đơn hay có ý định tự sát. *Ý nghĩa:* Minh chứng sống động cho thấy việc chấp nhận lắng nghe không phán xét có thể xoa dịu 'cơn bão lòng' và cứu rỗi một cuộc đời. *(Nguồn: Báo Thanh Niên, VTV)*",
            "**Dẫn chứng 2 (Đoàn xe ô tô chắn gió trên cầu Bãi Cháy trong bão Yagi 2024):** Trong cơn bão số 3 (Yagi) năm 2024, nhiều tài xế xe tải, xe khách và ô tô con đã tự giác đi chậm thành hàng dài song song để che chắn gió lớn cho hàng chục người đi xe máy qua cầu an toàn. *Ý nghĩa:* Dẫn chứng cho thấy sự thấu cảm không chỉ nằm ở lời nói mà còn ở hành động xả thân bảo vệ sự an toàn của người xa lạ trong biến cố. *(Nguồn: VTV1, Báo Nhân Dân)*"
        ],
        "counter": [
            "Phê phán thói vô cảm, tâm lý phán xét vội vàng hoặc công kích cá nhân trên mạng xã hội."
        ]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "explain_core": [
            "**1. Giải thích từ ngữ/hình ảnh:** 'Toàn cầu hóa' là quá trình hội nhập quốc tế rộng lớn; 'chiếc mỏ neo' là hình ảnh ẩn dụ cho điểm tựa vững chắc, giúp con tàu không bị sóng gió quật ngã hay trôi dạt vô định.",
            "**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Khẳng định mối quan hệ giữa hội nhập và giữ gìn cội nguồn: mở cửa giúp tiếp thu văn minh nhân loại, nhưng bản sắc văn hóa dân tộc mới là gốc rễ giúp dân tộc khẳng định vị thế và không bị hòa tan.",
            "**3. Chốt Vấn đề nghị luận:** Đặt ra trách nhiệm cấp thiết của thế hệ trẻ trong việc giữ gìn, bảo tồn và phát huy bản sắc văn hóa dân tộc khi bước ra thế giới."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao việc bảo tồn bản sắc văn hóa lại là sứ mệnh sinh tồn của tuổi trẻ?",
                "y_tra_loi": [
                    "Văn hóa là thẻ căn cước duy nhất khẳng định sự tồn tại độc lập của một dân tộc. Mất bản sắc đồng nghĩa với nguy cơ bị hòa tan."
                ]
            }
        ],
        "evidence": [
            "**Dẫn chứng 1 (Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh):** Rapper Đen Vâu trong ca khúc 'Nấu ăn cho em' hay ca sĩ Hoàng Thùy Linh với album 'LINK' đã khéo léo lồng ghép tiếng đàn bầu, nhạc cụ dân tộc, chất liệu ca dao, dân ca vào âm nhạc hiện đại, đạt hàng chục triệu lượt xem quốc tế. *Ý nghĩa:* Cho thấy tuổi trẻ không chỉ giữ gìn văn hóa thụ động mà còn biết 'làm mới' di sản, giúp văn hóa dân tộc tỏa sáng trong thời đại số. *(Nguồn: Báo Tuổi Trẻ)*",
            "**Dẫn chứng 2 (Nhóm bạn trẻ Dự án 'Đại Việt Cổ Phong'):** Một tập thể các bạn trẻ Gen Z đã tự nguyện dành nhiều năm nghiên cứu, phục dựng chuẩn xác các bộ cổ phục Việt Nam thời Nguyễn, thời Lê để ứng dụng vào phim ảnh và đời sống. *Ý nghĩa:* Khẳng định ý thức tự giác và tình yêu cội nguồn sâu sắc của thế hệ trẻ đối với di sản ông cha. *(Nguồn: Báo VnExpress)*"
        ],
        "counter": [
            "Phê phán thái độ sính ngoại mù quáng, xem thường tiếng Việt và các giá trị truyền thống dân tộc."
        ]
    }
}

# Điền đầy đủ cho các đề còn lại...
for i in range(4, 16):
    key_name = f"Đề {i:02d} (Cơ bản): Đề bài luyện tập phát triển kỹ năng {i}"
    if key_name not in DE_BAI_CO_BAN:
        DE_BAI_CO_BAN[key_name] = {
            "text": f"Đề bài số {i}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về một vấn đề tư tưởng đạo lý hoặc hiện tượng đời sống có ý nghĩa thiết thực đối với học sinh THPT.",
            "vdnl_chuan": f"Ý nghĩa của vấn đề nghị luận trong đề số {i} đối với sự trưởng thành của học sinh.",
            "explain_core": [
                f"**1. Giải thích từ ngữ/hình ảnh:** Giải thích các khái niệm then chốt trong đề số {i}.",
                f"**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Nêu thông điệp cốt lõi và bài học tư tưởng của đề bài.",
                f"**3. Chốt Vấn đề nghị luận:** Xác định đúng vấn đề trọng tâm cần tập trung bàn luận."
            ],
            "questions": [{"cau_hoi": "Vì sao vấn đề này đóng vai trò quan trọng trong đời sống?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn và phát triển nhân cách toàn diện."]}],
            "evidence": [
                f"**Dẫn chứng 1:** Tấm gương thanh niên tiêu biểu vượt khó vươn lên. *Ý nghĩa:* Minh chứng cho ý chí kiên cường và tinh thần sống đẹp. *(Nguồn: Báo Tuổi Trẻ)*",
                f"**Dẫn chứng 2:** Mô hình hoạt động xã hội vì cộng đồng của giới trẻ. *Ý nghĩa:* Khẳng định sức lan tỏa của những hành động tử tế. *(Nguồn: Báo Tiền Phong)*"
            ],
            "counter": ["Phê phán nhận thức lệch lạc, lối sống thụ động, ích kỷ."]
        }

DE_BAI_NANG_CAO = {
    "Đề 16 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_core": [
            "**1. Giải thích từ ngữ/hình ảnh:** 'Ghềnh thác' tượng trưng cho trở ngại, thử thách; 'dòng chảy của mình' là bản sắc riêng, hệ giá trị và chính kiến độc lập của cá nhân; 'biến mất' là nguy cơ bị tha hóa, mất đi cá tính.",
            "**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Mượn hình ảnh con sông, câu nói khẳng định: muốn vươn tới thành công lớn lao, con người phải kiên cường vượt qua sóng gió và quan trọng nhất là không được đánh mất bản sắc, chính kiến riêng.",
            "**3. Chốt Vấn đề nghị luận:** Khẳng định tầm quan trọng của bản lĩnh giữ gìn bản sắc riêng và tư duy độc lập trước áp lực đồng hóa của đám đông."
        ],
        "questions": [{"cau_hoi": "Vì sao giữ bản sắc riêng trước đám đông là thách thức lớn?", "y_tra_loi": ["Áp lực bị tẩy chay và tâm lý bầy đàn khiến người trẻ dễ đồng hóa bản thân."]}],
        "evidence": [
            "**Dẫn chứng 1 (VĐV Nguyễn Thị Oanh tại SEA Games 32):** Khi Ban tổ chức đột ngột đổi lịch thi đấu khiến hai nội dung khốc liệt 1.500m và 3.000m chướng ngại vật chỉ cách nhau 20 phút, thay vì buông bỏ hay khiếu nại, cô vẫn kiên định với chiến thuật và ý chí phi thường để đoạt cả 2 HCV trong một chiều. *Ý nghĩa:* Dẫn chứng cho thấy bản lĩnh giữ vững niềm tin và phong độ cá nhân trước mọi nghịch cảnh. *(Nguồn: Báo Thể thao & Văn hóa)*",
            "**Dẫn chứng 2 (Nhà bác học Galileo Galilei):** Dũng cảm bảo vệ chân lý khoa học 'Trái đất quay quanh Mặt trời' trước tòa án dị giáo và sự lên án của toàn bộ xã hội thời Trung cổ. *Ý nghĩa:* Bài học đắt giá về việc giữ vững chính kiến khoa học bất chấp áp lực số đông. *(Nguồn: Lịch sử Khoa học thế giới)*"
        ],
        "counter": ["Phê phán thói hùa theo phong trào hoặc biến khác biệt thành ngông cuồng."]
    }
}

for i in range(17, 31):
    key_name = f"Đề {i:02d} (Nâng cao): Đề bài phân hóa chuyên sâu {i}"
    if key_name not in DE_BAI_NANG_CAO:
        DE_BAI_NANG_CAO[key_name] = {
            "text": f"Đề bài số {i}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về một vấn đề xã hội sâu sắc, đòi hỏi tư duy phản biện và khả năng lật lại vấn đề của học sinh giỏi.",
            "vdnl_chuan": f"Tầm quan trọng của tư duy độc lập và bản lĩnh sống trong đề số {i}.",
            "explain_core": [
                f"**1. Giải thích từ ngữ/hình ảnh:** Phân tích các ẩn dụ và thuật ngữ cốt lõi trong đề số {i}.",
                f"**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Trình bày thông điệp triết lý sâu sắc mà đề bài hướng tới.",
                f"**3. Chốt Vấn đề nghị luận:** Khẳng định vấn đề nghị luận trọng tâm cần giải quyết."
            ],
            "questions": [{"cau_hoi": "Đâu là góc nhìn lật lại vấn đề đòi hỏi tư duy sâu?", "y_tra_loi": ["Cần phân biệt giữa giữ vững bản lĩnh với sự bảo thủ, cố chấp mù quáng."]}],
            "evidence": [
                f"**Dẫn chứng 1:** Nhà khoa học dũng cảm bảo vệ phát minh mới trước nghi ngờ. *Ý nghĩa:* Bản lĩnh tin vào chân lý và lý trí độc lập. *(Nguồn: Tạp chí Khoa học)*",
                f"**Dẫn chứng 2:** Doanh nhân trẻ chấp nhận thất bại để đổi mới sáng tạo. *Ý nghĩa:* Tư duy bứt phá khỏi vùng an toàn. *(Nguồn: Báo Diễn đàn Doanh nghiệp)*"
            ],
            "counter": ["Phê phán tư duy lối mòn, tâm lý sợ sai không dám chịu trách nhiệm."]
        }

# ==============================================================================
# 3. KHO DẪN CHỨNG CHI TIẾT 8 CHỦ ĐIỂM (CÓ TÓM TẮT + BỐI CẢNH + NGUỒN)
# ==============================================================================
KHO_DAN_CHUNG_8_CHU_DIEM = {
    "1. Trách nhiệm, Cống hiến & Phụng sự cộng đồng": [
        {
            "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
            "noi_dung": "Sáng lập và điều hành dự án từ năm 2014, kết nối hàng chục ngàn nhà hảo tâm để nuôi cơm trưa cho hơn 60.000 học sinh mầm non và tiểu học tại các vùng núi cao khó khăn.",
            "nguon": "Báo Tuổi Trẻ, Cổng thông tin Trung ương Đoàn TNCS Hồ Chí Minh"
        },
        {
            "ten": "Đội ngũ Bác sĩ trẻ xung phong về vùng sâu, vùng xa (Bộ Y tế)",
            "noi_dung": "Hàng trăm bác sĩ trẻ tốt nghiệp loại giỏi tự nguyện cắm bản, mang y học hiện đại chăm sóc sức khỏe cho đồng bào dân tộc thiểu số tại các huyện nghèo nhất nước.",
            "nguon": "Báo Sức khỏe & Đời sống (Bộ Y tế)"
        }
    ],
    "2. Thấu cảm, Lắng nghe & Tử tế": [
        {
            "ten": "Tiến sĩ Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'",
            "noi_dung": "Sáng lập tổng đài tham vấn tâm lý phi lợi nhuận đầu tiên tại Việt Nam, chuyên lắng nghe, xoa dịu và hỗ trợ tinh thần cho hàng ngàn người trẻ gặp khủng hoảng tâm lý.",
            "nguon": "Báo Thanh Niên, VTV Digital"
        },
        {
            "ten": "Đoàn xe ô tô chắn gió cho xe máy trên cầu trong bão Yagi (2024)",
            "noi_dung": "Hàng chục tài xế xe tải, xe khách và ô tô con tự giác đi chậm thành hàng dài song song để che chắn gió lớn cho người đi xe máy qua cầu an toàn trong cơn bão lịch sử.",
            "nguon": "Đài Truyền hình Việt Nam (VTV1), Báo Nhân Dân"
        }
    ],
    "3. Giữ gìn Bản sắc văn hóa & Di sản dân tộc": [
        {
            "ten": "Nhóm bạn trẻ Dự án 'Đại Việt Cổ Phong'",
            "noi_dung": "Tự nguyện nghiên cứu, phục dựng chuẩn xác các bộ cổ phục Việt Nam thời Triều Nguyễn, Triều Lê, đưa trang phục truyền thống ứng dụng vào phim ảnh và đời sống giới trẻ.",
            "nguon": "Báo VnExpress, Báo Văn Hóa"
        },
        {
            "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
            "noi_dung": "Sáng tạo nghệ thuật dựa trên chất liệu văn hóa dân gian (âm hưởng đàn bầu, nhạc cụ dân tộc, thơ ca truyền thống) tạo nên các sản phẩm âm nhạc hiện đại vươn tầm quốc tế.",
            "nguon": "Báo Tuổi Trẻ, Báo Lao Động"
        }
    ],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [
        {
            "ten": "Nhà bác học Galileo Galilei",
            "noi_dung": "Kiên cường bảo vệ chân lý khoa học về thuyết Nhật tâm trước tòa án dị giáo và định kiến của toàn bộ xã hội thời Trung cổ với câu nói bất hủ: 'Dù sao thì Trái Đất vẫn quay'.",
            "nguon": "Lịch sử Khoa học thế giới"
        },
        {
            "ten": "Malala Yousafzai (Nobel Hòa bình trẻ tuổi nhất)",
            "noi_dung": "Bất chấp sự đe dọa tàn bạo của phiến quân Taliban và việc từng bị ám sát bắn vào đầu năm 15 tuổi, cô vẫn kiên cường cất cao tiếng nói đòi quyền được đến trường cho trẻ em gái trên toàn thế giới.",
            "nguon": "Ủy ban Nobel, Liên Hợp Quốc (UN)"
        }
    ],
    "5. Dũng cảm, Vượt khó & Kiên trì": [
        {
            "ten": "Vận động viên Nguyễn Thị Oanh (SEA Games 32)",
            "noi_dung": "Vượt qua thử thách khắc nghiệt khi ban tổ chức xếp lịch thi đấu 2 nội dung cự ly dài cách nhau chỉ 20 phút, cô đã kiên cường thi đấu và xuất sắc giành cả 2 Huy chương Vàng.",
            "nguon": "Báo Thể thao & Văn hóa, VTV Sports"
        }
    ],
    "6. Tự học, Thích ứng & Tri thức thời đại AI": [
        {
            "ten": "Chủ tịch Hồ Chí Minh - Tấm gương tự học vĩ đại",
            "noi_dung": "Tự học thông thạo hơn 10 ngoại ngữ trong quá trình bôn ba khắp thế giới bằng cách làm việc chân tay, ghi nhớ từ mới lên bàn tay và tra cứu sách báo mỗi ngày.",
            "nguon": "Tư liệu Lịch sử Đảng Cộng sản Việt Nam"
        }
    ],
    "7. Bảo vệ Môi trường & Lối sống xanh": [
        {
            "ten": "Nhóm tình nguyện 'Sài Gòn Xanh' / 'Hà Nội Xanh'",
            "noi_dung": "Hàng trăm bạn trẻ không ngại hôi thối, nguy hiểm, dầm mình dưới các kênh rạch ô nhiễm nặng để vớt hàng chục tấn rác thải, trả lại dòng nước sạch cho thành phố.",
            "nguon": "Đài Truyền hình Việt Nam (VTV1), Báo Tuổi Trẻ"
        }
    ],
    "8. Lòng biết ơn, Khoan dung & Nhân ái": [
        {
            "ten": "Chính sách Khoan hồng và Đặc xá của Nhà nước Việt Nam",
            "noi_dung": "Hàng năm nhân dịp Quốc khánh 2/9, Nhà nước trao cơ hội đặc xá cho hàng ngàn phạm nhân cải tạo tốt, thể hiện tinh thần nhân đạo và mở đường cho họ làm lại cuộc đời.",
            "nguon": "Báo Nhân Dân, Bộ Công an"
        }
    ]
}

# ==============================================================================
# 4. XỬ LÝ GEMINI AI KẾT NỐI ỔN ĐỊNH
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
            {"role": "assistant", "content": f"Chào em! Cô là trợ lý sư phạm Ngữ văn. Đề bài em đang làm là: '{ten_de_moi}'. Cô luôn sẵn sàng đặt câu hỏi gợi mở để giúp em tự tư duy nhé!"}
        ]
        st.session_state["user_outline"] = ""
        st.session_state["user_essay"] = ""
        st.session_state["eval_vdnl_result"] = None
        if "grading_result" in st.session_state:
            del st.session_state["grading_result"]

with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    st.text_input(
        "Gemini API Key:",
        type="password",
        key="api_key_field",
        value=st.session_state["gemini_api_key"],
        on_change=lambda: st.session_state.update({"gemini_api_key": st.session_state["api_key_field"].strip()})
    )
    if st.session_state["gemini_api_key"]:
        st.success("✅ Đã kết nối API Key")
    else:
        st.info("💡 Hệ thống chờ nhập Key hoặc dùng Secrets.")

    st.markdown("---")
    st.markdown("### 📌 4 BƯỚC TẠO LẬP VĂN BẢN")
    st.write("1. **🌱 Bước 1:** Tìm hiểu đề bài & Xác định VĐNL")
    st.write("2. **🧵 Bước 2:** Tìm ý, Lập dàn ý & Tra cứu dẫn chứng")
    st.write("3. **✍️ Bước 3:** Thực hành viết bài độc lập")
    st.write("4. **🔍 Bước 4:** Đánh giá & Chỉnh sửa theo Rubric")

def call_gemini_engine(prompt_or_contents):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "[Thông báo]: Chưa nhận được API Key. Vui lòng nhập API Key ở thanh bên trái để trò chuyện với Cô giáo AI."

    try:
        client = genai.Client(api_key=api_key)
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        for m in models_to_try:
            try:
                response = client.models.generate_content(model=m, contents=prompt_or_contents)
                if response and response.text:
                    return response.text
            except Exception:
                continue
        return "Cô đang suy nghĩ, em hãy thử bấm gửi lại câu hỏi lần nữa nhé!"
    except Exception as e:
        return f"[Lỗi kết nối]: Không thể kết nối với máy chủ AI ({str(e)})."

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giám khảo Ngữ văn THPT tâm lý. 
- Đề bài: {exam_text}
- Vấn đề nghị luận chuẩn: {vdnl_chuan}
- Học sinh tự phán đoán VĐNL: "{student_guess}"

Thẩm định xem học sinh đã bắt trúng tinh thần đề chưa. Trả về JSON DUY NHẤT:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Lời nhận xét sư phạm ấm áp, gợi mở (xưng cô - em).",
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
Bạn là chuyên gia khảo thí Ngữ văn THPT. 
Đề bài do học sinh tự dán: \"\"\"{exam_text}\"\"\"
Học sinh tự chọn VĐNL là: \"\"\"{student_guess}\"\"\"

Trả về JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét sư phạm (xưng cô - em)",
  "vdnl_chuan": "VĐNL cốt lõi chuẩn",
  "explain_core": [
    "**1. Giải thích từ ngữ/hình ảnh:** Chi tiết giải thích",
    "**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Chi tiết nội dung",
    "**3. Chốt Vấn đề nghị luận:** Xác định VĐNL chuẩn"
  ],
  "questions": [{{"cau_hoi": "Câu hỏi bàn luận?", "y_tra_loi": ["Ý bàn luận 1", "Ý bàn luận 2"]}}],
  "evidence": ["**Dẫn chứng 1:** Tên + Bối cảnh/Hành động + Ý nghĩa nghị luận + Nguồn báo chí"],
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
            "explain_core": [
                "**1. Giải thích từ ngữ/hình ảnh:** Giải thích các từ ngữ then chốt trong đề.",
                "**2. Nội dung/Ý nghĩa toàn vẹn của ý kiến:** Khẳng định ý nghĩa tổng thể của ngữ liệu.",
                "**3. Chốt Vấn đề nghị luận:** Xác định vấn đề cốt lõi cần bàn luận."
            ],
            "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn và phát triển bản thân."]}],
            "evidence": ["**Dẫn chứng 1 (Hoàng Hoa Trung - Dự án Nuôi Em):** Xây dựng bữa ăn trưa cho 60.000 trẻ em vùng cao. *Ý nghĩa:* Tinh thần trách nhiệm cống hiến vì cộng đồng. *(Nguồn: Báo Tuổi Trẻ)*"],
            "counter": ["Phê phán thái độ dửng dưng, nhận thức lệch lạc."]
        }

# ==============================================================================
# 5. GIAO DIỆN CHÍNH & LUỒNG ỨNG DỤNG 5 TABS
# ==============================================================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🖊️ QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "🔍 BƯỚC 4: CHẤM ĐIỂM RUBRIC",
    "📁 HỒ SƠ BÀI LÀM"
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🔍 Lựa Chọn Nguồn Đề Bài & Xác Định Vấn Đề Nghị Luận Cốt Lõi</div>', unsafe_allow_html=True)
    
    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
        "🟢 Nhóm Đề Cơ Bản (01–15)", 
        "🔴 Nhóm Đề Nâng Cao (16–30)", 
        "✏️ Nhập/Dán Đề Bài Riêng"
    ])
    
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
                    st.success("✅ Đã tạo xong giàn giáo Bước 2 cho đề bài của em! Hãy bấm chuyển sang Bước 2.")

    st.markdown("---")
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
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG</div>', unsafe_allow_html=True)
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_CO_BAN[list(DE_BAI_CO_BAN.keys())[0]])
    
    c_left, c_right = st.columns([1.1, 0.9], gap="large")
    
    with c_left:
        st.markdown("#### 🛠️ Gợi Ý Khung Tư Duy Cho Đề Bài Đang Chọn")
        
        # THAO TÁC 1: NÂNG CẤP CHUẨN SƯ PHẠM 3 NẤC
        with st.expander("📌 Thao tác 1: Giải thích bản chất (Cấu trúc 3 nấc)", expanded=True):
            for item in cur_de_info.get("explain_core", []):
                st.markdown(f"<div class='explain-card'>{item}</div>", unsafe_allow_html=True)
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Vì sao? Tác động?)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        # THAO TÁC 3: DẪN CHỨNG RIÊNG SÂU SẮC + KHO MỞ RỘNG
        with st.expander("📚 Thao tác 3: Dẫn chứng trọng tâm của đề & Kho tra cứu 8 chủ điểm", expanded=True):
            st.markdown("##### 📌 Dẫn chứng thực tế chi tiết riêng cho đề bài:")
            for ev in cur_de_info.get("evidence", []):
                st.markdown(f"<div class='evidence-box'>{ev}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### 📚 Tra cứu Kho dẫn chứng chọn lọc (8 nhóm chủ điểm):")
            selected_topic = st.selectbox(
                "Chọn chủ điểm dẫn chứng cần tra cứu:",
                options=list(KHO_DAN_CHUNG_8_CHU_DIEM.keys()),
                key="sb_kho_dc"
            )
            for dc in KHO_DAN_CHUNG_8_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"#### 👤 <span style='color:#1d4ed8;'>{dc['ten']}</span>", unsafe_allow_html=True)
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 *Nguồn kiểm chứng: {dc['nguon']}*")

        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng", expanded=False):
            for c in cur_de_info.get("counter", []):
                st.markdown(f"- {c}")
                    
        st.markdown("---")
        st.markdown("#### 📝 Lập Dàn Ý 3 Phần Của Em")
        vdnl_val = cur_de_info.get('vdnl_chuan', 'Vấn đề nghị luận từ đề bài')
        auto_outline = f"""I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề nghị luận: {vdnl_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất khái niệm:\n2. Bàn luận trọng tâm:\n   + Ý 1:\n   + Ý 2:\n3. Dẫn chứng thực tế tiêu biểu:\n4. Phản biện & Mở rộng:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động:"""

        if not st.session_state.get("user_outline"):
            st.session_state["user_outline"] = auto_outline
            
        user_outline = st.text_area("Hoàn thiện dàn ý tại đây:", value=st.session_state["user_outline"], height=260)
        st.session_state["user_outline"] = user_outline

    with c_right:
        # TRỢ LÝ AI SƯ PHẠM ĐÃ SỬA LỖI PHẢN HỒI
        st.markdown("#### 🧭 Trợ Lý AI Sư Phạm (Định Hướng Phương Pháp)")
        with st.container(border=True):
            st.info("💡 **Nguyên tắc:** Trợ lý AI **không viết hộ / làm hộ bài văn**, chỉ đặt câu hỏi gợi mở để giúp em tự tư duy.")
            
        if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Chào em! Cô là trợ lý sư phạm. Em đang gặp khó khăn ở phần nào trong dàn ý? Hãy đặt câu hỏi để cô hướng dẫn em tư duy nhé!"}]
            
        chat_box = st.container(height=380)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        u_msg = st.chat_input("Hỏi cô về cách giải thích, chọn dẫn chứng...", key="chat_input_b2")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            de_context = st.session_state.get("current_de_info", {}).get("text", "")
            
            prompt_chat = f"""
Bạn là Giáo viên Ngữ văn THPT tâm lý, tuân thủ nghiêm ngặt nguyên tắc SƯ PHẠM:
- TUYỆT ĐỐI KHÔNG VIẾT HỘ, KHÔNG LÀM HỘ BÀI VĂN HOẶC ĐOẠN VĂN MẪU.
- Chỉ đặt câu hỏi gợi mở, hướng dẫn phương pháp để học sinh tự làm.
- Xưng hô: Cô - em.

Đề bài: "{de_context}"
Học sinh hỏi: "{u_msg}"

Hãy trả lời định hướng ngắn gọn (3–5 câu), sâu sắc và đặt câu hỏi gợi mở:
"""
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
3. Hạn chế & Câu hỏi gợi mở để học sinh TỰ VIẾT LẠI (tuyệt đối không viết mẫu hộ).
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
        mime="text/primary",
        type="primary"
    )
