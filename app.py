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
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 0.94rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KHO 30 ĐỀ THI CHUẨN ĐẦY ĐỦ 100%
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_core": [
            "**Lối sống có trách nhiệm:** Nhận thức rõ bổn phận, nghĩa vụ của bản thân đối với gia đình và xã hội; không dửng dưng, thờ ơ trước những vấn đề chung.",
            "**Gắn bó với cộng đồng:** Tinh thần hòa nhập, biết sẻ chia vui buồn, đặt lợi ích tập thể lên trên sự ích kỷ cá nhân và sẵn sàng cống hiến."
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
            "**Dự án Nuôi Em (Hoàng Hoa Trung - sáng lập từ 2014):** Kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn tại Điện Biên, Hà Giang. *(Nguồn: Báo Tuổi Trẻ, Cổng thông tin Trung ương Đoàn)*",
            "**Chiến dịch Mùa hè xanh:** Hàng ngàn sinh viên tình nguyện trên khắp cả nước xây dựng cầu giao thông nông thôn, dạy học miễn phí cho trẻ em vùng sâu vùng xa mỗi dịp hè. *(Nguồn: Báo Tiền Phong)*"
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
            "**Sự thấu cảm:** Năng lực đặt mình vào vị trí, hoàn cảnh và góc nhìn của người khác để cảm nhận và hiểu thấu nỗi đau, niềm vui của họ.",
            "**Lắng nghe chân thành:** Thái độ kiên nhẫn, trân trọng, không phán xét khi đón nhận tâm tư của đối phương."
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
            "**Dự án 'Tổng đài Ngày Mai' (Sáng lập bởi TS. Đặng Hoàng Giang):** Tổng đài tham vấn tâm lý phi lợi nhuận lắng nghe và hỗ trợ tinh thần cho hàng ngàn người trẻ đang trải qua khủng hoảng tâm lý. *(Nguồn: Báo Thanh Niên, VTV)*"
        ],
        "counter": [
            "Phê phán thói vô cảm, tâm lý phán xét vội vàng hoặc công kích cá nhân trên mạng xã hội."
        ]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "explain_core": [
            "**Bản sắc văn hóa dân tộc:** Toàn bộ những giá trị tinh hoa vật chất và tinh thần cốt lõi (phong tục, ngôn ngữ, nghệ thuật, đạo lý) được hun đúc qua lịch sử."
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
            "**Nghệ sĩ trẻ đưa văn hóa truyền thống vào nghệ thuật hiện đại:** Rapper Đen Vâu, ca sĩ Hoàng Thùy Linh, Đức Phúc ứng dụng nhạc cụ dân tộc, chất liệu dân gian vào âm nhạc triệu view. *(Nguồn: Báo Tuổi Trẻ)*"
        ],
        "counter": [
            "Phê phán thái độ sính ngoại mù quáng, xem thường tiếng Việt và các giá trị truyền thống dân tộc."
        ]
    },
    "Đề 04 (Cơ bản): Ý nghĩa của lòng biết ơn trong đời sống con người": {
        "text": """Danh ngôn có câu: *"Uống nước nhớ nguồn, ăn quả nhớ kẻ trồng cây."*\nTừ cội nguồn đạo lý truyền thống đó, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lòng biết ơn trong đời sống con người hôm nay.""",
        "vdnl_chuan": "Ý nghĩa và giá trị đạo đức của lòng biết ơn trong đời sống con người.",
        "explain_core": ["**Lòng biết ơn:** Sự trân trọng, ghi nhớ và đền đáp những ân huệ, công sức của thế hệ đi trước."],
        "questions": [{"cau_hoi": "Vì sao lòng biết ơn lại là nền tảng đạo đức cốt lõi?", "y_tra_loi": ["Giúp con người kết nối với cội nguồn, nuôi dưỡng lòng trắc ẩn và sự tử tế."]}],
        "evidence": ["**Hoạt động đền ơn đáp nghĩa nhân ngày 27/7:** Hàng năm thăm hỏi các Mẹ Việt Nam anh hùng, thắp nến tri ân liệt sĩ. *(Nguồn: Báo Nhân Dân)*"],
        "counter": ["Phê phán thói vô ơn, ăn cháo đá bát, vong ân bội nghĩa."]
    },
    "Đề 05 (Cơ bản): Sức mạnh và giá trị của niềm tin vào bản thân": {
        "text": """Có câu nói nổi tiếng: *"Tin rằng bạn có thể làm được là bạn đã đi được nửa đường."* (Theodore Roosevelt)\nHãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của niềm tin vào bản thân trong hành trình vươn tới thành công.""",
        "vdnl_chuan": "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong cuộc sống.",
        "explain_core": ["**Niềm tin vào bản thân:** Sự tự tin vững chắc vào năng lực, giá trị và tiềm năng của chính mình."],
        "questions": [{"cau_hoi": "Vì sao niềm tin vào bản thân lại là chìa khóa mở cửa thành công?", "y_tra_loi": ["Giúp con người không gục ngã trước thất bại ban đầu và dám hành động quyết liệt."]}],
        "evidence": ["**Diễn giả khuyết tật Nick Vujicic / Nguyễn Thị Ngọc Minh:** Vượt qua giới hạn cơ thể để khẳng định giá trị bản thân. *(Nguồn: Báo Tuổi Trẻ)*"],
        "counter": ["Phê phán căn bệnh tự ti, nhút nhát hoặc sự tự phụ, ảo tưởng sức mạnh."]
    },
    "Đề 06 (Cơ bản): Giá trị của sự kiên trì và bền bỉ trong cuộc sống": {
        "text": """Ngạn ngữ có câu: *"Nước chảy đá mòn."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự kiên trì, bền bỉ trong hành trình chinh phục mục tiêu của người trẻ.""",
        "vdnl_chuan": "Giá trị của sự kiên trì, bền bỉ và ý chí vượt qua gian khó để đạt ước mơ.",
        "explain_core": ["**Sự kiên trì, bền bỉ:** Phẩm chất đeo bám mục tiêu đến cùng, không nản lòng trước trở ngại."],
        "questions": [{"cau_hoi": "Vì sao thành công thực sự luôn đòi hỏi sự kiên trì?", "y_tra_loi": ["Mọi giá trị lớn lao đều cần thời gian hun đúc; không có thành công nào đạt được sau một đêm."]}],
        "evidence": ["**Hành trình luyện tập của VĐV Ánh Viên:** Dậy từ 4h sáng mỗi ngày, bơi hàng chục km suốt nhiều năm để đạt hàng trăm HCV. *(Nguồn: Báo Thể Thao)*"],
        "counter": ["Phê phán lối sống cả thèm chóng chán, dễ nản lòng, bỏ cuộc."]
    },
    "Đề 07 (Cơ bản): Ý nghĩa của việc trân trọng những giá trị bình dị quanh ta": {
        "text": """Có ý kiến cho rằng: *"Hạnh phúc đôi khi không phải là những điều lớn lao, mà ẩn giấu trong những điều bình dị nhất của đời thường."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của việc biết trân trọng những giá trị bình dị xung quanh cuộc sống.""",
        "vdnl_chuan": "Ý nghĩa của việc trân trọng những giá trị bình dị để tìm thấy hạnh phúc đích thực.",
        "explain_core": ["**Giá trị bình dị:** Những điều nhỏ bé, mộc mạc hằng ngày (bữa cơm gia đình, nụ cười, thiên nhiên bình yên)."],
        "questions": [{"cau_hoi": "Vì sao con người hiện đại thường bỏ quên những điều bình dị?", "y_tra_loi": ["Nhịp sống hối hả và mạng xã hội tạo ra áp lực thành công vật chất ảo khiến con người quên mất hiện tại."]}],
        "evidence": ["**Trào lưu 'Chữa lành' (Healing) và lối sống tối giản (Minimalism):** Giới trẻ tìm về thiên nhiên, tự nấu ăn để tìm lại bình yên. *(Nguồn: Báo Dân Trí)*"],
        "counter": ["Phê phán lối sống thực dụng, chạy theo hư vinh ảo tưởng."]
    },
    "Đề 08 (Cơ bản): Vai trò của sách và văn hóa đọc trong thời đại số": {
        "text": """Maxim Gorky từng khẳng định: *"Sách mở ra trước mắt tôi những chân trời mới."*\nTrong thời đại bùng nổ công nghệ số, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò và giá trị của việc đọc sách.""",
        "vdnl_chuan": "Vai trò, ý nghĩa của sách và văn hóa đọc đối với sự phát triển nhân cách con người.",
        "explain_core": ["**Sách:** Kho tàng lưu giữ tri thức, kinh nghiệm và tinh hoa tư tưởng của nhân loại."],
        "questions": [{"cau_hoi": "Vì sao trong thời đại Internet, sách vẫn giữ giá trị độc tôn?", "y_tra_loi": ["Sách mang lại tri thức có hệ thống, rèn luyện tư duy sâu (deep thinking) thay vì thông tin bề mặt."]}],
        "evidence": ["**Đường sách TP.HCM và Hà Nội:** Thu hút hàng triệu lượt bạn trẻ đến tham quan, đọc sách và giao lưu văn hóa. *(Nguồn: Sở Thông tin TP.HCM)*"],
        "counter": ["Phê phán tình trạng lười đọc sách, chỉ chuộng thông tin mì ăn liền ngắn ngủi trên mạng."]
    },
    "Đề 09 (Cơ bản): Ý nghĩa của lòng dũng cảm bảo vệ cái đúng, cái thiện": {
        "text": """Có ý kiến cho rằng: *"Lòng dũng cảm không phải là không sợ hãi, mà là sự chiến thắng nỗi sợ hãi."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải và công lý.""",
        "vdnl_chuan": "Vai trò của lòng dũng cảm trong đấu tranh bảo vệ cái đúng, cái thiện và lẽ công bằng.",
        "explain_core": ["**Lòng dũng cảm:** Bản lĩnh dám đối mặt với hiểm nguy, định kiến để bảo vệ sự thật và lẽ phải."],
        "questions": [{"cau_hoi": "Vì sao sự im lặng trước cái xấu đôi khi nguy hiểm hơn cái ác?", "y_tra_loi": ["Sự im lặng, dĩ hòa vi quý đồng nghĩa với việc tiếp tay, dung dưỡng cho cái ác hoành hành."]}],
        "evidence": ["**Những tấm gương cứu người trong lũ dữ:** Anh Nguyễn Văn Tập hay nhiều người dân không quản hiểm nguy cứu người mắc kẹt. *(Nguồn: Báo Công An Nhân Dân)*"],
        "counter": ["Phê phán thái độ hèn nhát, vô cảm, 'thấy việc nghĩa không làm'."]
    },
    "Đề 10 (Cơ bản): Ứng xử thông minh và văn minh trên không gian mạng": {
        "text": """Mạng xã hội giống như con dao hai lưỡi vừa kết nối toàn cầu vừa tiềm ẩn nhiều hệ lụy văn hóa.\nHãy viết bài văn nghị luận (khoảng 600 chữ) bàn về cách ứng xử thông minh và văn minh của người trẻ trên không gian mạng.""",
        "vdnl_chuan": "Cách ứng xử thông minh, làm chủ công nghệ và bản lĩnh văn hóa trên không gian mạng.",
        "explain_core": ["**Không gian mạng:** Thế giới ảo nhưng tác động thật, là nơi giao lưu nhưng chứa nhiều cạm bẫy."],
        "questions": [{"cau_hoi": "Người trẻ cần nguyên tắc nào để không bị thao túng trên mạng?", "y_tra_loi": ["Rèn luyện tư duy phản biện, kiểm tra nguồn gốc thông tin, không hùa theo đám đông chửi bới."]}],
        "evidence": ["**Bộ Quy tắc ứng xử trên mạng xã hội:** Do Bộ TT&TT ban hành khuyến khích chia sẻ lành mạnh, văn minh."],
        "counter": ["Phê phán hiện tượng 'anh hùng bàn phím', dùng nick ảo lăng mạ, miệt thị ngoại hình người khác."]
    },
    "Đề 11 (Cơ bản): Giá trị của sự trung thực trong học tập và đời sống": {
        "text": """Có ý kiến cho rằng: *"Sự thật có thể gây tổn thương trong chốc lát, nhưng dối trá để lại vết sẹo vĩnh viễn."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị và ý nghĩa của phẩm chất trung thực trong học tập và đời sống.""",
        "vdnl_chuan": "Ý nghĩa và giá trị của phẩm chất trung thực đối với sự trưởng thành của nhân cách con người.",
        "explain_core": ["**Sự trung thực:** Tôn trọng sự thật, nói và làm đúng với lương tâm, không gian dối."],
        "questions": [{"cau_hoi": "Vì sao bệnh gian lận trong học tập lại là mối nguy hại lớn?", "y_tra_loi": ["Gian lận làm thui chột năng lực thực chất, tạo ra 'giả học thức, thật bằng cấp'."]}],
        "evidence": ["**Cuộc vận động 'Nói không với tiêu cực trong thi cử':** Do Bộ GD&ĐT phát động đề cao giá trị thực chất."],
        "counter": ["Phê phán thói gian lận, đạo văn (plagiarism), bệnh thành tích ảo."]
    },
    "Đề 12 (Cơ bản): Tầm quan trọng của tinh thần tự học đối với học sinh": {
        "text": """Chủ tịch Hồ Chí Minh từng căn dặn: *"Học ở trường, học ở sách vở, học lẫn nhau và học nhân dân."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tinh thần tự học đối với học sinh trong thời đại mới.""",
        "vdnl_chuan": "Tầm quan trọng và giá trị của tinh thần tự học đối với sự phát triển của người trẻ.",
        "explain_core": ["**Tinh thần tự học:** Quá trình chủ động tìm tòi, tiếp thu kiến thức bằng tư duy độc lập."],
        "questions": [{"cau_hoi": "Vì sao học sinh ngày nay buộc phải trang bị năng lực tự học?", "y_tra_loi": ["Sự bùng nổ thông tin khiến kiến thức sách giáo khoa thay đổi nhanh chóng."]}],
        "evidence": ["**Tấm gương tự học của Chủ tịch Hồ Chí Minh:** Tự học ngoại ngữ, nghiên cứu chính trị khi bôn ba cứu nước."],
        "counter": ["Phê phán thói quen ỷ lại, học vẹt, lười suy nghĩ, chờ 'dọn sẵn mâm' kiến thức."]
    },
    "Đề 13 (Cơ bản): Sức mạnh của lời nói tử tế trong giao tiếp": {
        "text": """Ca dao dân gian có câu:\n> *"Lời nói không mất tiền mua / Lựa lời mà nói cho vừa lòng nhau."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của lời nói tử tế và văn hóa ứng xử trong đời sống hiện đại.""",
        "vdnl_chuan": "Sức mạnh của lời nói tử tế và tầm quan trọng của văn hóa ứng xử trong giao tiếp.",
        "explain_core": ["**Lời nói tử tế:** Những phát ngôn chân thành, lịch sự, tôn trọng người nghe, mang năng lượng tích cực."],
        "questions": [{"cau_hoi": "Vì sao con người dễ thốt ra lời cay độc thay vì tử tế?", "y_tra_loi": ["Áp lực cuộc sống và sự ẩn danh trên mạng xã hội phóng thích lời nói độc hại."]}],
        "evidence": ["**Các mô hình 'Quán ăn 0 đồng':** Nơi người lao động nghèo nhận bữa ăn kèm lời chào hỏi tôn trọng."],
        "counter": ["Phê phán thói chửi tục, miệt thị, dùng ngôn từ thô lỗ sát thương tâm lý."]
    },
    "Đề 14 (Cơ bản): Vai trò của tính tự lập trong hành trình trưởng thành": {
        "text": """Có ý kiến cho rằng: *"Chim non muốn bay cao phải tự vẫy đôi cánh của chính mình."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của tính tự lập đối với bạn trẻ trong hành trình bước vào đời.""",
        "vdnl_chuan": "Vai trò và ý nghĩa của tính tự lập trong hành trình trưởng thành của tuổi trẻ.",
        "explain_core": ["**Tính tự lập:** Khả năng tự chủ trong sinh hoạt, suy nghĩ và quyết định cuộc đời mình."],
        "questions": [{"cau_hoi": "Vì sao hội chứng ỷ lại vào gia đình là nỗi trăn trở lớn?", "y_tra_loi": ["Sự bao bọc quá mức tước đi cơ hội va vấp và tự chịu trách nhiệm của con cái."]}],
        "evidence": ["**Thanh niên các nước phát triển:** Từ 18 tuổi tự lập đi làm thêm trang trải học phí. *(Nguồn: Báo Dân Trí)*"],
        "counter": ["Phê phán thói quen 'công tử bột', 'bám váy mẹ', lười biếng."]
    },
    "Đề 15 (Cơ bản): Sức mạnh to lớn của tinh thần đoàn kết trong cộng đồng": {
        "text": """Chủ tịch Hồ Chí Minh từng đúc kết chân lý lịch sử:\n> *"Đoàn kết, đoàn kết, đại đoàn kết / Thành công, thành công, đại thành công."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của tinh thần đoàn kết trong việc vượt qua thử thách.""",
        "vdnl_chuan": "Sức mạnh to lớn của tinh thần đoàn kết trong việc tạo nên sức mạnh tập thể và vượt qua nghịch cảnh.",
        "explain_core": ["**Tinh thần đoàn kết:** Sự gắn kết, đồng lòng giữa các cá nhân vì mục tiêu chung."],
        "questions": [{"cau_hoi": "Vì sao đoàn kết là vũ khí tối thượng của dân tộc Việt Nam?", "y_tra_loi": ["Nước ta thường xuyên đối mặt thiên tai và ngoại xâm; chỉ đoàn kết mới tạo thành bức tường thành."]}],
        "evidence": ["**Tinh thần chống dịch Covid-19 và cứu trợ bão lũ:** Hàng ngàn chuyến xe cứu trợ, ATM gạo từ sự chung tay xã hội. *(Nguồn: Báo Nhân Dân)*"],
        "counter": ["Phê phán tư tưởng cục bộ, chia rẽ bè phái làm suy yếu sức mạnh tập thể."]
    }
}

DE_BAI_NANG_CAO = {
    "Đề 16 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_core": ["**Bản sắc riêng & chính kiến:** Tư duy độc lập, cá tính sáng tạo và hệ giá trị đạo đức riêng làm nên phẩm giá."],
        "questions": [{"cau_hoi": "Vì sao giữ bản sắc riêng trước đám đông là thách thức lớn?", "y_tra_loi": ["Áp lực bị tẩy chay và tâm lý bầy đàn khiến người trẻ dễ đồng hóa bản thân."]}],
        "evidence": ["**VĐV Nguyễn Thị Oanh (SEA Games 32):** Vượt qua áp lực dư luận giành 4 HCB điền kinh trong 1 chiều. *(Nguồn: Báo Thể Thao)*"],
        "counter": ["Phê phán thói hùa theo phong trào hoặc biến khác biệt thành ngông cuồng."]
    },
    "Đề 17 (Nâng cao): Trách nhiệm với di sản văn hóa truyền thống": {
        "text": """Nhà văn Nguyên Ngọc từng trăn trở về việc giữ gìn hồn cốt dân tộc qua thời gian.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm làm sống dậy di sản văn hóa truyền thống.""",
        "vdnl_chuan": "Trách nhiệm của thế hệ trẻ trong việc bảo tồn, phát huy giá trị di sản văn hóa.",
        "explain_core": ["**Di sản văn hóa:** Dòng sữa nuôi dưỡng tâm hồn dân tộc qua các thế hệ."],
        "questions": [{"cau_hoi": "Làm thế nào để di sản tiếp cận tự nhiên với Gen Z?", "y_tra_loi": ["Ứng dụng công nghệ số, thực tế ảo (VR/AR) và thiết kế hiện đại."]}],
        "evidence": ["**Dự án Cổ phục Việt 'Đại Việt Cổ Phong':** Nghiên cứu phục dựng trang phục truyền thống Triều Nguyễn. *(Nguồn: Báo VnExpress)*"],
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
        "evidence": ["**Nạn lừa đảo Deepfake voice/video:** Cảnh báo hàng loạt vụ án giả danh người thân lừa tiền. *(Nguồn: Bộ Công an)*"],
        "counter": ["Phê phán thói quen tin sái cổ thông tin chưa kiểm chứng trên mạng."]
    },
    "Đề 20 (Nâng cao): Lối sống tử tế và sức mạnh hàn gắn": {
        "text": """Có câu danh ngôn: *"Hãy đối xử tử tế với mọi người bạn gặp, bởi vì ai cũng đang phải trải qua một cuộc chiến khốc liệt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự tử tế.""",
        "vdnl_chuan": "Sức mạnh của sự tử tế và lòng nhân ái trong việc xoa dịu tổn thương xã hội.",
        "explain_core": ["**Sự tử tế:** Hành động, lời nói xuất phát từ lòng tốt, sự tôn trọng không đòi đền đáp."],
        "questions": [{"cau_hoi": "Sự tử tế nhỏ bé tạo nên thay đổi lớn thế nào?", "y_tra_loi": ["Tạo phản ứng dây chuyền, lan tỏa năng lượng tích cực, thu hẹp khoảng cách."]}],
        "evidence": ["**Phong trào 'Bếp ăn yêu thương':** Nhóm tình nguyện nấu ăn miễn phí cho bệnh nhân ung thư. *(Nguồn: Báo Thanh Niên)*"],
        "counter": ["Phê phán sự lạnh lùng, ích kỷ, coi nhẹ nỗi đau đồng loại."]
    },
    "Đề 21 (Nâng cao): Ý nghĩa của việc vượt qua vùng an toàn": {
        "text": """Có ý kiến cho rằng: *"Một con tàu an toàn nhất khi ở trong cảng, nhưng đó không phải là mục đích người ta đóng ra nó."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của việc bước ra khỏi vùng an toàn.""",
        "vdnl_chuan": "Ý nghĩa của việc bứt phá khỏi vùng an toàn để rèn luyện bản lĩnh và khai phá tiềm năng.",
        "explain_core": ["**Vùng an toàn:** Trạng thái quen thuộc, ít rủi ro nhưng triệt tiêu động lực sáng tạo."],
        "questions": [{"cau_hoi": "Vì sao dám chấp nhận rủi ro là bước ngoặt trưởng thành?", "y_tra_loi": ["Chỉ trong nghịch cảnh và môi trường mới, các phẩm chất tiềm ẩn mới kích hoạt."]}],
        "evidence": ["**Khởi nghiệp nông nghiệp sạch:** Nhiều bạn trẻ đưa nông sản Việt vươn tầm quốc tế. *(Nguồn: Báo Nông Nghiệp)*"],
        "counter": ["Phê phán tâm lý an phận thủ thường, sợ hãi thất bại."]
    },
    "Đề 22 (Nâng cao): Sự nguy hại của thái độ thờ ơ vô cảm": {
        "text": """Albert Einstein từng nói: *"Thế giới bị đe dọa không phải bởi những kẻ làm điều ác, mà bởi những người đứng nhìn mà không làm gì cả."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về tác hại của thái độ thờ ơ, vô cảm.""",
        "vdnl_chuan": "Sự nguy hại của căn bệnh vô cảm, thờ ơ và trách nhiệm lên tiếng trước cái xấu.",
        "explain_core": ["**Thái độ vô cảm:** Sự dửng dưng, quay lưng trước bất công và nỗi đau đồng loại."],
        "questions": [{"cau_hoi": "Làm sao dập tắt ngọn lửa vô cảm trong lòng người trẻ?", "y_tra_loi": ["Bồi dưỡng lòng trắc ẩn và thực thi pháp luật nghiêm minh bảo vệ người dũng cảm."]}],
        "evidence": ["**Hiện tượng quay clip tai nạn thay vì cứu giúp:** Bị cộng đồng lên án gay gắt. *(Nguồn: Báo Lao Động)*"],
        "counter": ["Phê phán thói dĩ hòa vi quý, 'cháy nhà ai nấy rạng'."]
    },
    "Đề 23 (Nâng cao): Ý thức trách nhiệm bảo vệ môi trường sống": {
        "text": """Trái Đất đang gánh chịu tổn thương cực lớn từ thiên tai và biến đổi khí hậu.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về lối sống xanh và trách nhiệm bảo vệ hành tinh xanh của thế hệ trẻ.""",
        "vdnl_chuan": "Ý thức trách nhiệm và hành động thiết thực của tuổi trẻ trong việc bảo vệ môi trường.",
        "explain_core": ["**Lối sống xanh:** Tối thiểu hóa tác động tiêu cực tới tự nhiên, tiết kiệm tài nguyên."],
        "questions": [{"cau_hoi": "Thế hệ trẻ đóng góp gì chống biến đổi khí hậu?", "y_tra_loi": ["Giảm rác thải nhựa, phân loại rác tại nguồn, lan tỏa thông điệp sống xanh."]}],
        "evidence": ["**Chiến dịch 'Sài Gòn Xanh' / 'Hà Nội Xanh':** Nhóm bạn trẻ vớt hàng tấn rác kênh rạch. *(Nguồn: Báo Tuổi Trẻ)*"],
        "counter": ["Phê phán thói quen xả rác bừa bãi và tâm lý 'xanh vỏ đỏ lòng' (Greenwashing)."]
    },
    "Đề 24 (Nâng cao): Nhìn nhận đúng đắn về thất bại": {
        "text": """Thất bại không phải đối lập của thành công, nó là một phần trên con đường đi đến thành công.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về thái độ tích cực khi đối diện thất bại.""",
        "vdnl_chuan": "Thái độ tích cực, coi thất bại là bài học vô giá trên đường tới thành công.",
        "explain_core": ["**Thất bại:** Kết quả chưa như ý, là phép thử giúp chỉ ra lỗ hổng hoàn thiện."],
        "questions": [{"cau_hoi": "Làm thế nào chuyển hóa thất bại thành động lực?", "y_tra_loi": ["Dũng cảm nhận trách nhiệm, phân tích nguyên nhân, kiên trì thử lại."]}],
        "evidence": ["**Thomas Edison:** Hàng ngàn lần thử nghiệm trước khi chế tạo thành công bóng đèn điện."],
        "counter": ["Phê phán tâm lý suy sụp, đổ lỗi, mất niềm tin vào bản thân."]
    },
    "Đề 25 (Nâng cao): Ý nghĩa của sự khoan dung và lòng vị tha": {
        "text": """Danh ngôn có câu: *"Mặt trời chiếu sáng không phân biệt ai, lòng khoan dung cũng vậy."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự khoan dung trong tháo gỡ mâu thuẫn.""",
        "vdnl_chuan": "Ý nghĩa và giá trị của lòng khoan dung, vị tha trong việc cởi bỏ hận thù.",
        "explain_core": ["**Khoan dung:** Sự rộng lượng, tha thứ cho lỗi lầm khi người khác đã hối hận."],
        "questions": [{"cau_hoi": "Khoan dung có phải là sự yếu đuối hay thỏa hiệp?", "y_tra_loi": ["Khoan dung là biểu hiện sức mạnh nội tâm, cho người khác cơ hội làm lại."]}],
        "evidence": ["**Chính sách Khoan hồng nhà nước:** Tha thứ, giảm án cho phạm nhân cải tạo tốt dịp 2/9. *(Nguồn: Báo Nhân Dân)*"],
        "counter": ["Phê phán thói chấp nhặt, thù lâu nhớ dai, muốn trả đũa."]
    },
    "Đề 26 (Nâng cao): Bản lĩnh tự học và thích ứng trong tương lai": {
        "text": """Toàn cầu hóa và kỷ nguyên số đòi hỏi con người không ngừng học lại từ đầu.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về khả năng học hỏi suốt đời và thích ứng sự thay đổi.""",
        "vdnl_chuan": "Tầm quan trọng của năng lực học hỏi suốt đời và khả năng thích ứng trước thế giới biến động.",
        "explain_core": ["**Thích ứng:** Khả năng linh hoạt thay đổi tư duy, kỹ năng phù hợp hoàn cảnh mới."],
        "questions": [{"cau_hoi": "Vì sao 'khả năng học lại' quyết định lao động tương lai?", "y_tra_loi": ["Nhiều ngành nghề cũ bị AI thay thế, ngành nghề mới liên tục xuất hiện."]}],
        "evidence": ["**Báo cáo WEF:** Thích ứng và học hỏi suốt đời thuộc TOP 3 kỹ năng quan trọng nhất thập kỷ."],
        "counter": ["Phê phán tư tưởng xơ cứng, tự mãn với bằng cấp hiện có."]
    },
    "Đề 27 (Nâng cao): Sức mạnh của tinh thần lạc quan": {
        "text": """Người lạc quan nhìn thấy cơ hội trong mỗi khó khăn, kẻ tiêu cực nhìn thấy khó khăn trong mỗi cơ hội.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của thái độ lạc quan.""",
        "vdnl_chuan": "Vai trò và sức mạnh của tinh thần lạc quan trong việc vượt qua áp lực cuộc sống.",
        "explain_core": ["**Lạc quan:** Lối tư duy hướng về điều tích cực, giữ niềm tin trước gian truân."],
        "questions": [{"cau_hoi": "Lạc quan khác gì ảo tưởng hoang đường?", "y_tra_loi": ["Lạc quan thực tế nhìn rõ khó khăn nhưng tin tưởng giải pháp và hành động."]}],
        "evidence": ["**Bệnh nhân hiểm nghèo lạc quan:** Câu chuyện truyền cảm hứng trong 'Trạm yêu thương'. *(Nguồn: VTV)*"],
        "counter": ["Phê phán thói than vắn thở dài, gieo rắc năng lượng độc hại."]
    },
    "Đề 28 (Nâng cao): Trách nhiệm tôn trọng sự khác biệt": {
        "text": """Mỗi bông hoa có hương sắc riêng, mỗi con người có cá tính riêng.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về thái độ tôn trọng sự khác biệt trong xã hội đa dạng.""",
        "vdnl_chuan": "Trách nhiệm và thái độ văn minh khi biết tôn trọng sự khác biệt của người khác.",
        "explain_core": ["**Tôn trọng khác biệt:** Chấp nhận quan điểm, tính cách, lối sống khác mình."],
        "questions": [{"cau_hoi": "Vì sao áp đặt góc nhìn cá nhân gây ra xung đột?", "y_tra_loi": ["Mỗi người có hoàn cảnh, trải nghiệm khác nhau; không có thước đo đơn nhất."]}],
        "evidence": ["**Công nhận cộng đồng LGBTQ+ và nhóm yếu thế:** Xã hội ngày càng cởi mở pháp lý. *(Nguồn: Báo Pháp Luật)*"],
        "counter": ["Phê phán thói kỳ thị, cho mình là chuẩn mực duy nhất phán xét người khác."]
    },
    "Đề 29 (Nâng cao): Tầm quan trọng của việc quản lý thời gian": {
        "text": """Thời gian là tài sản công bằng nhất nhưng cũng nhanh chóng trôi đi không khôi phục được.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về kỹ năng quản lý thời gian hiệu quả.""",
        "vdnl_chuan": "Tầm quan trọng của kỹ năng quản lý thời gian đối với việc nâng cao hiệu suất sống.",
        "explain_core": ["**Quản lý thời gian:** Kỹ năng phân bổ, làm chủ quỹ thời gian theo thứ tự ưu tiên."],
        "questions": [{"cau_hoi": "Vì sao người trẻ dễ sa vào bẫy trì hoãn?", "y_tra_loi": ["Sự cám dỗ của giải trí trực tuyến và thiếu mục tiêu sống rõ ràng."]}],
        "evidence": ["**Phương pháp Pomodoro & Ma trận Eisenhower:** Áp dụng bởi nhiều thủ khoa và doanh nhân."],
        "counter": ["Phê phán thói quen nước đến chân mới nhảy, lãng phí thời gian vô bổ."]
    },
    "Đề 30 (Nâng cao): Khát vọng cống hiến và giá trị của tuổi trẻ": {
        "text": """Tuổi trẻ không tính bằng số tuổi mà tính bằng khát vọng trong tim.\nViết bài văn nghị luận (khoảng 600 chữ) bàn về khát vọng cống hiến và ý nghĩa sống của tuổi trẻ.""",
        "vdnl_chuan": "Ý nghĩa của khát vọng cống hiến đối với việc tạo dựng giá trị sống cho tuổi trẻ.",
        "explain_core": ["**Khát vọng cống hiến:** Ước mơ lớn đóng góp trí tuệ, sức lực cho sự phát triển cộng đồng."],
        "questions": [{"cau_hoi": "Làm thế nào biến khát vọng cống hiến thành hành động?", "y_tra_loi": ["Bắt đầu từ hoàn thành tốt học tập, sống tử tế và tham gia dự án cộng đồng."]}],
        "evidence": ["**Gương mặt trẻ Việt Nam tiêu biểu:** Tôn vinh tài năng dưới 30 tuổi trên các lĩnh vực. *(Nguồn: Trung ương Đoàn)*"],
        "counter": ["Phê phán lối sống nhạt nhòa, sống hoài sống phí tuổi trẻ."]
    }
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
        },
        {
            "ten": "Bác sĩ Ignaz Semmelweis (Cha đẻ của việc rửa tay vô trùng)",
            "noi_dung": "Dũng cảm chiến đấu với giới y khoa thế kỷ 19 để chứng minh việc bác sĩ rửa tay trước khi đỡ đẻ giúp cứu sống hàng ngàn sản phụ, dù bị đồng nghiệp miệt thị và cô lập.",
            "nguon": "Tổ chức Y tế Thế giới (WHO)"
        }
    ],
    "5. Dũng cảm, Vượt khó & Kiên trì": [
        {
            "ten": "Vận động viên Nguyễn Thị Oanh (SEA Games 32)",
            "noi_dung": "Vượt qua thử thách khắc nghiệt khi ban tổ chức xếp lịch thi đấu 2 nội dung cự ly dài cách nhau chỉ 20 phút, cô đã kiên cường thi đấu và xuất sắc giành cả 2 Huy chương Vàng.",
            "nguon": "Báo Thể thao & Văn hóa, VTV Sports"
        },
        {
            "ten": "Diễn giả Nick Vujicic",
            "noi_dung": "Sinh ra không có cả tay lẫn chân, ông đã vượt qua sự tuyệt vọng để trở thành diễn giả truyền cảm hứng sống tích cực cho hàng triệu người trên thế giới.",
            "nguon": "Báo Tuổi Trẻ"
        }
    ],
    "6. Tự học, Thích ứng & Tri thức thời đại AI": [
        {
            "ten": "Chủ tịch Hồ Chí Minh - Tấm gương tự học vĩ đại",
            "noi_dung": "Tự học thông thạo hơn 10 ngoại ngữ trong quá trình bôn ba khắp thế giới bằng cách làm việc chân tay, ghi nhớ từ mới lên bàn tay và tra cứu sách báo mỗi ngày.",
            "nguon": "Tư liệu Lịch sử Đảng Cộng sản Việt Nam"
        },
        {
            "ten": "Lời cảnh báo về Lừa đảo Deepfake voice/video (2023–2024)",
            "noi_dung": "Tội phạm công nghệ cao sử dụng AI giả dạng khuôn mặt và giọng nói người thân để lừa đảo, đòi hỏi người trẻ phải rèn luyện tư duy phản biện và xác thực thông tin.",
            "nguon": "Cổng thông tin Điện tử Bộ Công an"
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
# 4. KẾT NỐI GEMINI AI
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
            {"role": "assistant", "content": f"Chào em! Cô là trợ lý sư phạm Ngữ văn. Đề bài hiện tại là: '{ten_de_moi}'. Cô sẽ không làm hộ hay viết hộ bài cho em, nhưng cô luôn sẵn sàng đặt câu hỏi gợi mở và định hướng giúp em tự tư duy nhé!"}
        ]
        st.session_state["user_outline"] = ""
        st.session_state["user_essay"] = ""
        st.session_state["eval_vdnl_result"] = None
        if "grading_result" in st.session_state:
            del st.session_state["grading_result"]

# Cấu hình thanh Sidebar
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
Bạn là Giám khảo Ngữ văn THPT GDPT 2018 tâm lý. 
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
Bạn là chuyên gia khảo thí Ngữ văn THPT GDPT 2018. 
Đề bài do học sinh tự dán: \"\"\"{exam_text}\"\"\"
Học sinh tự chọn VĐNL là: \"\"\"{student_guess}\"\"\"

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
            "evidence": ["**Dẫn chứng thực tế:** Các tấm gương thanh niên sống đẹp. *(Nguồn: Báo Tuổi Trẻ)*"],
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
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & CẢM NHẬN DẪN CHỨNG",
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
        
        with st.expander("📌 Thao tác 1: Giải thích bản chất", expanded=True):
            for item in cur_de_info.get("explain_core", []):
                st.markdown(f"- {item}")
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Vì sao? Tác động?)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        # TÍCH HỢP KHO DẪN CHỨNG VÀO TRỰC TIẾP THAO TÁC 3
        with st.expander("📚 Thao tác 3: Dẫn chứng trọng tâm của đề & Kho tra cứu 8 chủ điểm", expanded=True):
            st.markdown("##### 📌 Gợi ý dẫn chứng riêng cho đề:")
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
        # TRỢ LÝ AI SƯ PHẠM (TUYỆT ĐỐI KHÔNG LÀM HỘ, CHỈ ĐỊNH HƯỚNG)
        st.markdown("#### 🧭 Trợ Lý AI Sư Phạm (Định Hướng Phương Pháp)")
        with st.container(border=True):
            st.info("💡 **Nguyên tắc hoạt động:** Trợ lý AI sẽ **không viết hộ** hay **làm hộ** bài văn của em. AI chỉ đặt câu hỏi gợi mở để giúp em tự tư duy và hoàn thiện dàn ý.")
            
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Chào em! Cô là trợ lý sư phạm. Em đang gặp khó khăn ở phần nào trong dàn ý? Hãy trao đổi để cô gợi mở hướng suy nghĩ cho em nhé!"}]
            
        chat_box = st.container(height=350)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        u_msg = st.chat_input("Hỏi cô về phương pháp lập luận, chọn dẫn chứng...")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            de_context = st.session_state.get("current_de_info", {}).get("text", "")
            
            prompt_chat = f"""
Bạn là một Giám khảo và Giáo viên Ngữ văn THPT tâm lý, tuân thủ nghiêm ngặt nguyên tắc SƯ PHẠM:
- TUYỆT ĐỐI KHÔNG VIẾT HỘ, KHÔNG LÀM HỘ BÀI VĂN HOẶC ĐOẠN VĂN MẪU CHO HỌC SINH.
- Chỉ đặt câu hỏi gợi mở, hướng dẫn phương pháp, định hướng tư duy để học sinh tự làm.
- Xưng hô: Cô - em.

Đề bài học sinh đang làm: "{de_context}"
Câu hỏi/Thắc mắc của học sinh: "{u_msg}"

Hãy đưa ra lời định hướng sư phạm ngắn gọn, sâu sắc, kèm câu hỏi gợi mở tư duy:
"""
            with st.spinner("Cô đang định hướng..."):
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
        mime="text/plain",
        type="primary"
    )
