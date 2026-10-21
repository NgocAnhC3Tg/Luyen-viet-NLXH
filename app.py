import streamlit as st
import json
import re
from google import genai
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP & BÔI XANH ĐÚNG TAB BƯỚC ĐANG CHỌN
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

    /* Hero Banner Đỉnh Trang */
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

    /* Khung danh sách Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #ffffff;
        padding: 8px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
    }

    /* Kiểu dáng Tab trạng thái bình thường (Chưa chọn - Màu xám chìm) */
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

    /* BÔI XANH ĐẬM BẮT MẮT KHI BẤM CHỌN BẤT KỲ TAB NÀO */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    /* Tiêu đề mục gọn gàng */
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
# 2. NGÂN HÀNG ĐỀ THI ĐẦY ĐỦ 30 ĐỀ ĐA DẠNG & PHONG PHÚ
# ==============================================================================
DE_BAI_DATA = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:
> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*
Từ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "topic_tag": "Trách nhiệm – Cống hiến – Tình người",
        "explain_core": ["Lối sống có trách nhiệm: Nhận thức rõ bổn phận, nghĩa vụ đối với gia đình, cộng đồng.", "Gắn bó với cộng đồng: Tinh thần hòa nhập, sẻ chia và cống hiến cho tập thể."],
        "questions": [{"cau_hoi": "Vì sao người trẻ cần sống có trách nhiệm?", "y_tra_loi": ["Mỗi cá nhân là một tế bào của xã hội.", "Đẩy lùi căn bệnh vô cảm, tạo lập môi trường sống nhân ái."]}],
        "counter": ["Phê phán lối sống vị kỷ, thờ ơ trước nỗi đau của đồng loại."]
    },
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.
Hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "topic_tag": "Thấu cảm – Lắng nghe – Hàn gắn",
        "explain_core": ["Sự thấu cảm: Đặt mình vào vị trí của người khác để hiểu thấu và chia sẻ.", "Lắng nghe chân thành: Thái độ lắng nghe không phán xét bằng sự tôn trọng."],
        "questions": [{"cau_hoi": "Vì sao con người hiện đại cần lắng nghe?", "y_tra_loi": ["Xoa dịu những tổn thương tinh thần và hàn gắn mối quan hệ."]}],
        "counter": ["Phê phán thói vô cảm, công kích cá nhân trên mạng xã hội."]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh toàn cầu hóa.",
        "topic_tag": "Bản sắc văn hóa – Nguồn cội – Hội nhập",
        "explain_core": ["Bản sắc văn hóa: Những giá trị tinh hoa cốt lõi được hun đúc qua lịch sử.", "Chiếc mỏ neo: Điểm tựa vững chãi giữ cho quốc gia không bị hòa tan."],
        "questions": [{"cau_hoi": "Người trẻ làm gì để giữ gìn bản sắc?", "y_tra_loi": ["Tôn trọng tiếng Việt, tìm hiểu lịch sử, ứng dụng công nghệ để quảng bá văn hóa."]}],
        "counter": ["Phê phán tâm lý sính ngoại mù quáng, xem thường cội nguồn."]
    },
    "Đề 04 (Cơ bản): Ý nghĩa của lòng biết ơn trong đời sống": {
        "text": """Danh ngôn có câu: *"Uống nước nhớ nguồn, ăn quả nhớ kẻ trồng cây."* 
Từ cội nguồn đạo lý truyền thống đó, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lòng biết ơn trong đời sống con người hôm nay.""",
        "vdnl_chuan": "Ý nghĩa và giá trị đạo đức của lòng biết ơn trong đời sống con người.",
        "topic_tag": "Đạo lý – Lòng biết ơn – Nhân cách",
        "explain_core": ["Lòng biết ơn: Sự trân trọng và đền đáp những ân huệ, công sức mà người khác dành cho mình."],
        "questions": [{"cau_hoi": "Vì sao con người cần có lòng biết ơn?", "y_tra_loi": ["Giúp tâm hồn thanh thản, nuôi dưỡng lòng trắc ẩn và sự tử tế."]}],
        "counter": ["Phê phán thói vô ơn, ăn cháo đá bát, vô cảm trước công sức người khác."]
    },
    "Đề 05 (Cơ bản): Sức mạnh của niềm tin vào bản thân": {
        "text": """Có câu nói: *"Tin rằng bạn có thể làm được là bạn đã đi được nửa đường."* (Theodore Roosevelt)
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của niềm tin vào bản thân trong hành trình vươn tới thành công.""",
        "vdnl_chuan": "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong cuộc sống.",
        "topic_tag": "Niềm tin – Bản lĩnh – Thành công",
        "explain_core": ["Niềm tin vào bản thân: Sự tự tin vào năng lực, giá trị và tiềm năng của chính mình."],
        "questions": [{"cau_hoi": "Vì sao niềm tin bản thân lại quan trọng?", "y_tra_loi": ["Là ngọn đuốc soi đường khi đối mặt nghịch cảnh, vượt qua nỗi sợ hãi."]}],
        "counter": ["Phê phán sự tự ti, ba hoa kiêu ngạo hoặc ảo tưởng sức mạnh."]
    },
    "Đề 06 (Cơ bản): Giá trị của sự kiên trì và bền bỉ": {
        "text": """Ngạn ngữ có câu: *"Nước chảy đá mòn."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự kiên trì, bền bỉ trong hành trình chinh phục mục tiêu của người trẻ.""",
        "vdnl_chuan": "Giá trị của sự kiên trì, bền bỉ và ý chí vượt qua gian khó để đạt ước mơ.",
        "topic_tag": "Kiên trì – Ý chí – Thành quả",
        "explain_core": ["Kiên trì: Sự bền chí, không lùi bước trước thất bại ban đầu."],
        "questions": [{"cau_hoi": "Vì sao kiên trì quyết định thành công?", "y_tra_loi": ["Mọi thành quả lớn lao đều đòi hỏi quá trình rèn luyện dài lâu."]}],
        "counter": ["Phê phán lối sống cả thèm chóng chán, dễ nản lòng khi gặp khó khăn."]
    },
    "Đề 07 (Cơ bản): Trân trọng những giá trị bình dị quanh ta": {
        "text": """Có ý kiến cho rằng: *"Hạnh phúc đôi khi không phải là những điều lớn lao, mà ẩn giấu trong những điều bình dị nhất của đời thường."*
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của việc biết trân trọng những giá trị bình dị xung quanh cuộc sống.""",
        "vdnl_chuan": "Ý nghĩa của việc trân trọng những giá trị bình dị để tìm thấy hạnh phúc đích thực.",
        "topic_tag": "Hạnh phúc – Sự bình dị – Tỉnh thức",
        "explain_core": ["Giá trị bình dị: Những điều nhỏ bé hằng ngày nhưng nuôi dưỡng tâm hồn."],
        "questions": [{"cau_hoi": "Vì sao cần trân trọng điều bình dị?", "y_tra_loi": ["Giúp con người an yên, biết ơn hiện tại thay vì cuốn theo tham vọng xa vời."]}],
        "counter": ["Phê phán lối sống thực dụng, chạy theo hư vinh ảo tưởng."]
    },
    "Đề 08 (Cơ bản): Vai trò của sách và văn hóa đọc": {
        "text": """Maxim Gorky từng khẳng định: *"Sách mở ra trước mắt tôi những chân trời mới."* 
Trong thời đại bùng nổ công nghệ số, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò và giá trị của việc đọc sách.""",
        "vdnl_chuan": "Vai trò, ý nghĩa của sách và văn hóa đọc đối với sự phát triển nhân cách con người.",
        "topic_tag": "Sách – Tri thức – Văn hóa đọc",
        "explain_core": ["Sách là kho tàng tri thức nhân loại, bồi dưỡng tư tưởng và cảm xúc."],
        "questions": [{"cau_hoi": "Vì sao đọc sách vẫn quan trọng?", "y_tra_loi": ["Giúp rèn luyện tư duy sâu (deep thinking) thay vì đọc lướt hời hợt."]}],
        "counter": ["Phê phán tình trạng lười đọc sách, chỉ chuộng thông tin mì ăn liền trên mạng."]
    },
    "Đề 09 (Cơ bản): Ý nghĩa của lòng dũng cảm bảo vệ cái đúng": {
        "text": """Có ý kiến cho rằng: *"Lòng dũng cảm không phải là không sợ hãi, mà là sự chiến thắng nỗi sợ hãi."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải và công lý.""",
        "vdnl_chuan": "Vai trò của lòng dũng cảm trong đấu tranh bảo vệ cái đúng, cái thiện và lẽ công bằng.",
        "topic_tag": "Dũng cảm – Lẽ phải – Công lý",
        "explain_core": ["Lòng dũng cảm: Bản lĩnh dám đối mặt với hiểm nguy và tiêu cực để bảo vệ chân lý."],
        "questions": [{"cau_hoi": "Vì sao cần có lòng dũng cảm?", "y_tra_loi": ["Sự im lặng trước cái ác đồng nghĩa với việc tiếp tay cho cái xấu."]}],
        "counter": ["Phê phán thái độ hèn nhát, dĩ hòa vi quý, thờ ơ trước bất công."]
    },
    "Đề 10 (Cơ bản): Ứng xử thông minh trên không gian mạng": {
        "text": """Mạng xã hội giống như con dao hai lưỡi vừa kết nối toàn cầu vừa tiềm ẩn nhiều hệ lụy. 
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về cách ứng xử thông minh của người trẻ trước không gian mạng.""",
        "vdnl_chuan": "Cách ứng xử thông minh, làm chủ công nghệ và bản lĩnh trước tác động của mạng xã hội.",
        "topic_tag": "Công nghệ – Mạng xã hội – Bản lĩnh",
        "explain_core": ["Mạng xã hội mang lại thông tin nhưng cũng dễ gây nghiện và mất kết nối thật."],
        "questions": [{"cau_hoi": "Làm sao để làm chủ mạng xã hội?", "y_tra_loi": ["Sử dụng có chọn lọc, tỉnh táo trước tin giả và giữ văn hóa ứng xử."]}],
        "counter": ["Phê phán hiện tượng nghiện ảo, dùng mạng để lăng mạ người khác."]
    },
    "Đề 11 (Cơ bản): Ý nghĩa của sự trung thực trong cuộc sống": {
        "text": """Trung thực là nền tảng của mọi mối quan hệ bền vững. Viết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự trung thực đối với sự trưởng thành của mỗi cá nhân.""",
        "vdnl_chuan": "Ý nghĩa và giá trị của phẩm chất trung thực trong đời sống con người.",
        "topic_tag": "Trung thực – Nhân cách – Niềm tin",
        "explain_core": ["Trung thực: Tôn trọng sự thật, không gian dối, nói và làm đúng với lương tâm."],
        "questions": [{"cau_hoi": "Vì sao trung thực lại quan trọng?", "y_tra_loi": ["Tạo dựng uy tín, niềm tin và sự trân trọng từ cộng đồng."]}],
        "counter": ["Phê phán thói dối trá, gian lận trong học tập và cuộc sống."]
    },
    "Đề 12 (Cơ bản): Giá trị của tinh thần tự học": {
        "text": """Chủ tịch Hồ Chí Minh là tấm gương sáng ngời về tinh thần tự học. Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của năng lực tự học đối với học sinh hôm nay.""",
        "vdnl_chuan": "Tầm quan trọng và giá trị của tinh thần tự học đối với sự phát triển của người trẻ.",
        "topic_tag": "Tự học – Tri thức – Chủ động",
        "explain_core": ["Tự học: Chủ động tìm tòi, tiếp thu kiến thức không phụ thuộc hoàn toàn vào thầy cô."],
        "questions": [{"cau_hoi": "Tự học mang lại giá trị gì?", "y_tra_loi": ["Giúp mở rộng hiểu biết không giới hạn và làm chủ tương lai."]}],
        "counter": ["Phê phán thói quen thụ động, ỷ lại, chờ đợi kiến thức từ người khác."]
    },
    "Đề 13 (Cơ bản): Sức mạnh của lời nói tử tế": {
        "text": """Ca dao có câu: *"Lời nói không mất tiền mua / Lựa lời mà nói cho vừa lòng nhau."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của lời nói tử tế và văn hóa giao tiếp ứng xử hiện đại.""",
        "vdnl_chuan": "Sức mạnh của lời nói tử tế và tầm quan trọng của văn hóa ứng xử trong giao tiếp.",
        "topic_tag": "Giao tiếp – Lời nói tử tế – Văn hóa",
        "explain_core": ["Lời nói tử tế: Lời nói chân thành, tôn trọng, mang năng lượng tích cực và xây dựng."],
        "questions": [{"cau_hoi": "Vì sao cần cẩn trọng trong lời nói?", "y_tra_loi": ["Lời nói có thể xoa dịu tổn thương nhưng cũng có thể trở thành vũ khí gieo đau khổ."]}],
        "counter": ["Phê phán thói miệt thị ngoại hình, phát ngôn độc hại trên mạng."]
    },
    "Đề 14 (Cơ bản): Vai trò của tính tự lập ở tuổi trẻ": {
        "text": """Rèn luyện tính tự lập là bước đi đầu tiên để con người trưởng thành. Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của tính tự lập đối với bạn trẻ hôm nay.""",
        "vdnl_chuan": "Vai trò và ý nghĩa của tính tự lập trong hành trình trưởng thành của tuổi trẻ.",
        "topic_tag": "Tự lập – Trưởng thành – Bản lĩnh",
        "explain_core": ["Tự lập: Tự mình thực hiện các công việc, tự chịu trách nhiệm về quyết định của mình."],
        "questions": [{"cau_hoi": "Tự lập giúp ích gì cho người trẻ?", "y_tra_loi": ["Xây dựng bản lĩnh vững vàng, không bị gục ngã trước biến cố."]}],
        "counter": ["Phê phán lối sống bao cấp, dựa dẫm quá mức vào cha mẹ."]
    },
    "Đề 15 (Cơ bản): Sức mạnh của tinh thần đoàn kết": {
        "text": """Bác Hồ từng dạy: *"Đoàn kết, đoàn kết, đại đoàn kết / Thành công, thành công, đại thành công."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của tinh thần đoàn kết trong việc vượt qua thử thách.""",
        "vdnl_chuan": "Sức mạnh to lớn của tinh thần đoàn kết trong việc tạo nên sức mạnh tập thể.",
        "topic_tag": "Đoàn kết – Sức mạnh tập thể – Hợp tác",
        "explain_core": ["Đoàn kết: Sự gắn kết, hợp lực giữa các cá nhân vì mục tiêu chung."],
        "questions": [{"cau_hoi": "Vì sao đoàn kết tạo nên sức mạnh?", "y_tra_loi": ["Gộp nhặt sức mạnh nhỏ thành nguồn sức mạnh vĩ đại vượt qua thiên tai, dịch bệnh."]}],
        "counter": ["Phê phán tư tưởng chia rẽ, cục bộ, ích kỷ cá nhân."]
    },

    # --- DẠNG ĐỀ NÂNG CAO (ĐỀ 16 - ĐỀ 30) ---
    "Đề 16 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực của số đông trong kỷ nguyên số.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng, chính kiến cá nhân trước áp lực của đám đông trong thời đại số.",
        "topic_tag": "Bản lĩnh – Tư duy độc lập – Bản sắc",
        "explain_core": ["Bản sắc riêng: Cá tính độc đáo, tư duy độc lập làm nên phẩm giá cá nhân.", "Áp lực số đông: Sự lôi kéo, phán xét từ đám đông dễ đẩy con người vào lối sống hòa tan."],
        "questions": [{"cau_hoi": "Vì sao giữ bản sắc riêng lại khó khăn?", "y_tra_loi": ["Thuật toán mạng xã hội tạo tâm lý bầy đàn, sợ bị tẩy chay."]}],
        "counter": ["Phê phán lối sống hùa theo phong trào, a dua thiếu suy nghĩ."]
    },
    "Đề 17 (Nâng cao): Trách nhiệm với di sản văn hóa truyền thống": {
        "text": """Nhà văn Nguyên Ngọc từng trăn trở về việc giữ gìn hồn cốt dân tộc qua thời gian. 
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm và cách thức làm sống dậy di sản văn hóa truyền thống trong tâm hồn thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm và sứ mệnh của thế hệ trẻ trong việc bảo tồn, phát huy giá trị di sản văn hóa truyền thống.",
        "topic_tag": "Di sản – Văn hóa – Trách nhiệm thế hệ",
        "explain_core": ["Di sản văn hóa: Dòng sữa nuôi dưỡng tâm hồn dân tộc qua các thế hệ."],
        "questions": [{"cau_hoi": "Làm thế nào để đưa di sản đến gần giới trẻ?", "y_tra_loi": ["Kết hợp công nghệ số, sáng tạo trong cách tiếp cận thay vì bảo thủ xơ cứng."]}],
        "counter": ["Phê phán thái độ hững hờ, xem nhẹ di sản cha ông."]
    },
    "Đề 18 (Nâng cao): Tinh thần dấn thân và khát vọng phụng sự": {
        "text": """Đặng Thùy Trâm từng viết trong nhật ký: *"Đời phải trải qua giông tố nhưng chớ cúi đầu trước giông tố."*
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về tinh thần dấn thân và khát vọng phụng sự cộng đồng của thanh niên thời đại mới.""",
        "vdnl_chuan": "Ý nghĩa của tinh thần dấn thân, sống cống hiến và trách nhiệm phụng sự cộng đồng của tuổi trẻ.",
        "topic_tag": "Dấn thân – Phụng sự – Lý tưởng sống",
        "explain_core": ["Dấn thân: Dám đương đầu khó khăn, đem tài năng nhiệt huyết xây dựng đất nước."],
        "questions": [{"cau_hoi": "Vì sao người trẻ cần có lý tưởng dấn thân?", "y_tra_loi": ["Tuổi trẻ là thời gian đẹp nhất để cống hiến, giúp cuộc đời có ý nghĩa sâu sắc."]}],
        "counter": ["Phê phán lối sống ích kỷ, thực dụng, chỉ biết hưởng thụ cá nhân."]
    },
    "Đề 19 (Nâng cao): Tư duy phản biện trong thời đại AI": {
        "text": """Trong kỷ nguyên trí tuệ nhân tạo (AI) và thông tin bùng nổ, ranh giới giữa sự thật và giả mạo trở nên mỏng manh hơn bao giờ hết.
Viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tư duy phản biện và năng lực tự chủ tri thức của người trẻ.""",
        "vdnl_chuan": "Tầm quan trọng của tư duy phản biện và năng lực chắt lọc thông tin trước sự bùng nổ của công nghệ và AI.",
        "topic_tag": "Tư duy phản biện – Trí tuệ – Tự chủ",
        "explain_core": ["Tư duy phản biện: Năng lực phân tích, đánh giá vấn đề một cách khách quan, đa chiều."],
        "questions": [{"cau_hoi": "Vì sao tư duy phản biện sống còn thời AI?", "y_tra_loi": ["Tránh bị thao túng bởi thông tin độc hại, tin giả (fake news) lan tràn."]}],
        "counter": ["Phê phán thói quen tiếp nhận thông tin thụ động, cả tin."]
    },
    "Đề 20 (Nâng cao): Lối sống tử tế và sức mạnh hàn gắn": {
        "text": """Có câu danh ngôn: *"Hãy đối xử tử tế với mọi người bạn gặp, bởi vì ai cũng đang phải trải qua một cuộc chiến khốc liệt."*
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự tử tế và lòng trắc ẩn trong việc hàn gắn những rạn nứt xã hội.""",
        "vdnl_chuan": "Sức mạnh của sự tử tế và lòng nhân ái trong việc xoa dịu tổn thương và kết nối con người.",
        "topic_tag": "Tử tế – Lòng trắc ẩn – Hàn gắn",
        "explain_core": ["Sự tử tế: Thứ ngôn ngữ mà người điếc có thể nghe và người mù có thể thấy."],
        "questions": [{"cau_hoi": "Sự tử tế đem lại điều kỳ diệu gì?", "y_tra_loi": ["Xóa nhòa khoảng cách, tạo ra bầu không khí nhân văn và ấm áp tình người."]}],
        "counter": ["Phê phán sự lạnh lùng, ích kỷ, cư xử bạo lực với đồng loại."]
    },
    "Đề 21 (Nâng cao): Ý nghĩa của việc vượt qua vùng an toàn": {
        "text": """Có ý kiến cho rằng: *"Một con tàu an toàn nhất khi ở trong cảng, nhưng đó không phải là mục đích người ta đóng ra nó."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của việc bước ra khỏi vùng an toàn để khám phá tiềm năng bản thân.""",
        "vdnl_chuan": "Ý nghĩa của việc bứt phá khỏi vùng an toàn để rèn luyện bản lĩnh và khai phá tiềm năng.",
        "topic_tag": "Vùng an toàn – Bứt phá – Trưởng thành",
        "explain_core": ["Vùng an toàn: Trạng thái tâm lý thoải mái, quen thuộc nhưng dễ triệt tiêu sáng tạo."],
        "questions": [{"cau_hoi": "Vì sao cần dũng cảm bước ra khỏi vùng an toàn?", "y_tra_loi": ["Chỉ qua thử thách mới khám phá hết giới hạn và sức mạnh tiềm ẩn của chính mình."]}],
        "counter": ["Phê phán tâm lý an phận thủ thường, sợ thất bại mà không dám dấn thân."]
    },
    "Đề 22 (Nâng cao): Sự nguy hại của thái độ thờ ơ vô cảm": {
        "text": """Albert Einstein từng nói: *"Thế giới bị đe dọa không phải bởi những kẻ làm điều ác, mà bởi những người đứng nhìn mà không làm gì cả."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về tác hại của thái độ thờ ơ, vô cảm đối với sự phát triển của xã hội.""",
        "vdnl_chuan": "Sự nguy hại của căn bệnh vô cảm, thờ ơ và trách nhiệm lên tiếng trước cái xấu.",
        "topic_tag": "Vô cảm – Trách nhiệm – Lên tiếng",
        "explain_core": ["Thái độ vô cảm: Sự dửng dưng, quay lưng trước nỗi đau và sự bất công trong đời sống."],
        "questions": [{"cau_hoi": "Sự vô cảm gây nên hậu quả gì?", "y_tra_loi": ["Dung dưỡng cho cái xấu hoành hành, làm xói mòn các giá trị đạo đức căn bản."]}],
        "counter": ["Lật lại vấn đề: Lên tiếng bảo vệ lẽ phải cần đi liền với sự tỉnh táo."]
    },
    "Đề 23 (Nâng cao): Ý thức trách nhiệm bảo vệ môi trường sống": {
        "text": """Trái Đất đang gánh chịu tổn thương cực lớn. Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về lối sống xanh và trách nhiệm bảo vệ hành tinh xanh của thế hệ trẻ.""",
        "vdnl_chuan": "Ý thức trách nhiệm và hành động thiết thực của tuổi trẻ trong việc bảo vệ môi trường.",
        "topic_tag": "Lối sống xanh – Môi trường – Tương lai",
        "explain_core": ["Lối sống xanh: Lối sống giảm thiểu tác hại đến thiên nhiên, phát triển bền vững."],
        "questions": [{"cau_hoi": "Vì sao bảo vệ môi trường là việc cấp bách?", "y_tra_loi": ["Biến đổi khí hậu trực tiếp đe dọa sự sống còn của nhân loại."]}],
        "counter": ["Phê phán thói quen xả rác bừa bãi, tàn phá thiên nhiên vì lợi ích ngắn hạn."]
    },
    "Đề 24 (Nâng cao): Nhìn nhận đúng đắn về thất bại": {
        "text": """Thất bại không phải là đối lập của thành công, nó là một phần của thành công. Viết bài văn nghị luận (khoảng 600 chữ) bàn về thái độ tích cực cần có khi đối diện với thất bại ở người trẻ.""",
        "vdnl_chuan": "Thái độ tích cực, coi thất bại là bài học vô giá trên đường tới thành công.",
        "topic_tag": "Th thất bại – Bài học – Vươn lên",
        "explain_core": ["Đối diện thất bại: Nhìn nhận lỗi sai bằng sự bình tĩnh để rút ra bài học."],
        "questions": [{"cau_hoi": "Thất bại dạy cho ta điều gì?", "y_tra_loi": ["Rèn luyện sự kiên cường, giúp ta nhìn lại những lỗ hổng trong tư duy."]}],
        "counter": ["Phê phán tâm lý suy sụp, đổ lỗi cho hoàn cảnh khi gặp thất bại."]
    },
    "Đề 25 (Nâng cao): Ý nghĩa của sự khoan dung và lòng vị tha": {
        "text": """Danh ngôn có câu: *"Mặt trời chiếu sáng không phân biệt ai, lòng khoan dung cũng vậy."* Viết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự khoan dung trong việc tháo gỡ mâu thuẫn con người.""",
        "vdnl_chuan": "Ý nghĩa và giá trị của lòng khoan dung, vị tha trong việc cởi bỏ hận thù.",
        "topic_tag": "Khoan dung – Vị tha – Giải thoát",
        "explain_core": ["Khoan dung: Sự rộng lượng, sẵn sàng tha thứ cho lỗi lầm của người khác."],
        "questions": [{"cau_hoi": "Khoan dung mang lại lợi ích gì?", "y_tra_loi": ["Giải thoát bản thân khỏi gánh nặng oán hận, mang lại bình yên tâm hồn."]}],
        "counter": ["Phê phán thói chấp nhặt, thù lâu nhớ dai, luôn muốn trả đũa."]
    },
    "Đề 26 (Nâng cao): Bản lĩnh tự học và thích ứng trong tương lai": {
        "text": """Toàn cầu hóa đòi hỏi con người không ngừng học lại từ đầu. Viết bài văn nghị luận (khoảng 600 chữ) bàn về khả năng học hỏi suốt đời và năng lực thích ứng với sự thay đổi.""",
        "vdnl_chuan": "Tầm quan trọng của năng lực học hỏi suốt đời và khả năng thích ứng trước thế giới biến động.",
        "topic_tag": "Học suốt đời – Thích ứng – Tương lai",
        "explain_core": ["Thích ứng: Năng lực linh hoạt điều chỉnh bản thân để phù hợp môi trường mới."],
        "questions": [{"cau_hoi": "Vì sao học hỏi suốt đời lại bắt buộc?", "y_tra_loi": ["Kiến thức cũ nhanh chóng lỗi thời, sự chủ động học mới giúp không bị đào thải."]}],
        "counter": ["Phê phán thái độ tự mãn với kiến thức hiện có, lười đổi mới."]
    },
    "Đề 27 (Nâng cao): Sức mạnh của tinh thần lạc quan": {
        "text": """Người lạc quan nhìn thấy cơ hội trong mỗi khó khăn. Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của thái độ sống lạc quan đối với sức khỏe tinh thần của bạn trẻ.""",
        "vdnl_chuan": "Vai trò và sức mạnh của tinh thần lạc quan trong việc vượt qua áp lực cuộc sống.",
        "topic_tag": "Lạc quan – Tinh thần – Hy vọng",
        "explain_core": ["Lạc quan: Cách nhìn nhận đời sống bằng niềm tin, hy vọng và hướng về điều tích cực."],
        "questions": [{"cau_hoi": "Lạc quan giúp ích gì?", "y_tra_loi": ["Tạo nguồn năng lượng mạnh mẽ, giảm thiểu rủi ro trầm cảm và bế tắc."]}],
        "counter": ["Phê phán thói quen than vắn thở dài, nhìn đời qua con mắt xám xịt."]
    },
    "Đề 28 (Nâng cao): Trách nhiệm tôn trọng sự khác biệt": {
        "text": """Mỗi bông hoa có một hương sắc riêng, mỗi con người có một cá tính riêng. Viết bài văn nghị luận (khoảng 600 chữ) bàn về thái độ tôn trọng sự khác biệt trong xã hội đa dạng.""",
        "vdnl_chuan": "Trách nhiệm và thái độ văn minh khi biết tôn trọng sự khác biệt của người khác.",
        "topic_tag": "Tôn trọng – Đa dạng – Văn minh",
        "explain_core": ["Tôn trọng sự khác biệt: Chấp nhận những quan điểm, tính cách, hoàn cảnh khác mình."],
        "questions": [{"cau_hoi": "Vì sao cần tôn trọng sự khác biệt?", "y_tra_loi": ["Tạo nên bức tranh xã hội phong phú, hạn chế định kiến."]}],
        "counter": ["Phê phán thói áp đặt góc nhìn cá nhân, kỳ thị những người khác biệt."]
    },
    "Đề 29 (Nâng cao): Tầm quan trọng của việc quản lý thời gian": {
        "text": """Thời gian là tài sản công bằng nhất của nhân loại. Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về kỹ năng quản lý thời gian hiệu quả đối với sự thành công của giới trẻ.""",
        "vdnl_chuan": "Tầm quan trọng của kỹ năng quản lý thời gian đối với việc nâng cao hiệu suất sống.",
        "topic_tag": "Thời gian – Kỹ năng – Giá trị",
        "explain_core": ["Quản lý thời gian: Biết sắp xếp công việc hợp lý theo thứ tự ưu tiên."],
        "questions": [{"cau_hoi": "Vì sao cần trân trọng thời gian?", "y_tra_loi": ["Thời gian một đi không trở lại, làm chủ thời gian là làm chủ cuộc đời."]}],
        "counter": ["Phê phán thói quen trì hoãn, lãng phí thời gian vào việc vô bổ."]
    },
    "Đề 30 (Nâng cao): Khát vọng cống hiến và giá trị của tuổi trẻ": {
        "text": """Tuổi trẻ không tính bằng số tuổi mà tính bằng khát vọng trong tim. Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về khát vọng cống hiến và ý nghĩa sống của tuổi trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của khát vọng cống hiến đối với việc tạo dựng giá trị sống cho tuổi trẻ.",
        "topic_tag": "Tuổi trẻ – Khát vọng – Cống hiến",
        "explain_core": ["Khát vọng cống hiến: Ước mơ được đóng góp sức mình cho sự phát triển chung."],
        "questions": [{"cau_hoi": "Khát vọng mang lại điều gì?", "y_tra_loi": ["Thắp sáng ngọn lửa nhiệt huyết, biến những năm tháng thanh xuân trở nên rực rỡ."]}],
        "counter": ["Phê phán lối sống nhạt nhòa, sống hoài sống phí."]
    }
}

# ==============================================================================
# 3. KẾT NỐI GEMINI AI & SESSION STATE
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "last_selected_de" not in st.session_state:
    st.session_state["last_selected_de"] = ""
if "custom_de_analyzed" not in st.session_state:
    st.session_state["custom_de_analyzed"] = False
if "custom_de_data" not in st.session_state:
    st.session_state["custom_de_data"] = None

def kiem_tra_va_reset_khi_doi_de(ten_de_moi):
    if st.session_state["last_selected_de"] != ten_de_moi:
        st.session_state["last_selected_de"] = ten_de_moi
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Chào em! Đề bài hiện tại là: '{ten_de_moi}'. Em hãy xem khung định hướng bên trái, cần cô gợi mở thêm phần nào thì nhắn cô nhé!"}
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
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw)
    except Exception:
        return {"status": "DUNG", "feedback": "Cô nhận thấy em đã nắm bắt khá tốt tinh thần của đề bài!", "suggested_fix": vdnl_chuan}

def ai_analyze_custom_exam(exam_text, student_guess=""):
    """
    HÀM NÀY ĐÃ ĐƯỢC VIẾT LẠI CHUYÊN SÂU: 
    AI phân tích sâu sắc nội dung đề do người dùng tự nhập để tạo giàn giáo Bước 2 chi tiết, thực chất.
    """
    prompt = f"""
Bạn là chuyên gia khảo thí và giáo dục môn Ngữ văn THPT GDPT 2018. 
Học sinh tự dán một đề bài nghị luận xã hội riêng vào hệ thống. Nội dung đề bài như sau:
\"\"\"{exam_text}\"\"\"

Học sinh đã phán đoán vấn đề nghị luận (VĐNL) là: \"{student_guess}\"

Nhiệm vụ của bạn:
1. Đọc kỹ đề bài, bóc tách chính xác Vấn đề nghị luận cốt lõi của đề này.
2. Thẩm định phán đoán của học sinh xem đã chính xác chưa (DUNG, LECH, hoặc SAI) và viết lời nhận xét sư phạm ân cần (xưng cô - em).
3. Xây dựng một khung giàn giáo tư duy CỰC KỲ CHI TIẾT VÀ THỰC CHẤT cho đề bài này để hỗ trợ học sinh ở Bước 2, bao gồm:
   - Cắt nghĩa các từ khóa/mệnh đề cốt lõi.
   - Các câu hỏi bàn luận trọng tâm bám sát đề.
   - Gợi ý phản biện / lật ngược vấn đề sắc sảo.

BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON (không kèm thêm markdown rườm rà ngoài chuỗi JSON):
{{
  "status": "DUNG" | "LECH" | "SAI",
  "teacher_evaluation": "Lời nhận xét sư phạm phân tích rõ học sinh đúng/chưa đúng chỗ nào (xưng cô - em)",
  "vdnl_chuan": "Vấn đề nghị luận chuẩn xác và sâu sắc nhất của đề này",
  "topic_tag": "Chủ điểm bài học cụ thể",
  "explain_core": [
     "Cắt nghĩa vế 1 hoặc từ khóa quan trọng trong đề",
     "Cắt nghĩa vế 2 hoặc mối quan hệ giữa các yếu tố trong đề"
  ],
  "questions": [
     {{
       "cau_hoi": "Câu hỏi bàn luận trọng tâm 1 (Ví dụ: Vì sao vấn đề này đặt ra cấp thiết trong đời sống?)",
       "y_tra_loi": ["Ý phân tích a", "Ý phân tích b"]
     }},
     {{
       "cau_hoi": "Câu hỏi bàn luận trọng tâm 2 (Ví dụ: Ý nghĩa/tác động của vấn đề đối với tuổi trẻ?)",
       "y_tra_loi": ["Ý phân tích a", "Ý phân tích b"]
     }}
  ],
  "counter": [
     "Gợi ý phản biện 1: Phê phán biểu hiện trái ngược hoặc cực đoan",
     "Gợi ý phản biện 2: Lật lại vấn đề để thấy tính đa chiều"
  ]
}}
"""
    raw_res = call_gemini_engine(prompt)
    try:
        match = re.search(r"\{.*\}", raw_res, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw_res)
    except Exception:
        return {
            "status": "LECH",
            "teacher_evaluation": "Cô nhận thấy em đã bước đầu tiếp cận được hướng đi của đề, nhưng cần phân tích sâu hơn các từ khóa trọng tâm.",
            "vdnl_chuan": "Vấn đề nghị luận rút ra từ đề bài tự nhập",
            "topic_tag": "Đề tự chọn",
            "explain_core": ["Làm rõ các từ ngữ, hình ảnh hoặc thông điệp cốt lõi trong đề bài."],
            "questions": [{"cau_hoi": "Vì sao vấn đề này có ý nghĩa đối với nhận thức của thế hệ trẻ?", "y_tra_loi": ["Giúp bồi dưỡng nhân cách sống", "Thúc đẩy hành động thiết thực"]}],
            "counter": ["Phê phán nhận thức lệch lạc hoặc thái độ thờ ơ trước vấn đề."]
        }

# ==============================================================================
# 4. GIAO DIỆN CHÍNH (HERO BANNER & TABS TỰ ĐỘNG BÔI XANH KHI BẤM CHỌN)
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
        st.session_state["is_custom_de"] = True
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
        kiem_tra_va_reset_khi_doi_de(ten_de_hien_tai)
        
        st.markdown("---")
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi theo ý hiểu của em:", placeholder="Gõ vấn đề nghị luận ở đây...")
        
        if st.button("🔍 Thẩm định Vấn đề nghị luận & Tạo giàn giáo Bước 2 cho đề này", type="primary"):
            if not custom_de_input.strip():
                st.warning("Em chưa dán đề bài vào ô phía trên!")
            elif not student_vdnl.strip():
                st.warning("Em hãy tự gõ phán đoán Vấn đề nghị luận trước nhé!")
            else:
                with st.spinner("AI đang phân tích sâu đề bài và thiết kế giàn giáo..."):
                    analyzed = ai_analyze_custom_exam(custom_de_input, student_vdnl)
                    st.session_state["custom_de_data"] = analyzed
                    st.session_state["custom_de_analyzed"] = True
                    st.session_state["eval_vdnl_result"] = {
                        "status": analyzed.get("status", "LECH"),
                        "feedback": analyzed.get("teacher_evaluation", ""),
                        "suggested_fix": analyzed.get("vdnl_chuan", "")
                    }
                    
        if st.session_state.get("custom_de_analyzed") and st.session_state.get("custom_de_data"):
            data = st.session_state["custom_de_data"]
            res = st.session_state.get("eval_vdnl_result", {})
            if res.get("status") == "DUNG":
                st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}\n\n👉 *VĐNL Cốt lõi:* {data['vdnl_chuan']}")
            else:
                st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *VĐNL Cốt lõi chuẩn:* {data['vdnl_chuan']}")
                
            de_info = {
                "text": custom_de_input,
                "vdnl_chuan": data["vdnl_chuan"],
                "explain_core": data["explain_core"],
                "questions": data["questions"],
                "counter": data["counter"]
            }
        else:
            de_info = {
                "text": custom_de_input if custom_de_input.strip() else "Chưa có nội dung đề bài.",
                "vdnl_chuan": "Đề tự nhập",
                "explain_core": ["Dán đề bài và bấm nút phân tích phía trên."],
                "questions": [{"cau_hoi": "Câu hỏi gợi mở", "y_tra_loi": ["Đang chờ phân tích đề"]}],
                "counter": ["Đang chờ phân tích đề"]
            }
            
    else:
        st.session_state["is_custom_de"] = False
        st.session_state["custom_de_analyzed"] = False
        
        col_de1, col_de2 = st.columns([1, 2], gap="medium")
        with col_de1:
            filtered_de_keys = [k for k in DE_BAI_DATA.keys() if ("(Nâng cao)" if muc_do_de == "Đề nâng cao" else "(Cơ bản)") in k]
            selected_de_key = st.selectbox("Chọn đề bài có sẵn trong thư viện:", filtered_de_keys)
            kiem_tra_va_reset_khi_doi_de(selected_de_key)
            de_info = DE_BAI_DATA[selected_de_key]
            
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

    st.session_state["current_de_info"] = de_info
    st.session_state["current_de_key"] = selected_de_key if muc_do_de != "Tự nhập đề bài riêng cần hỗ trợ" else ten_de_hien_tai

# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý & LẬP DÀN Ý
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">🧵 Xây Dựng Hệ Thống Luận Điểm & Tự Hoàn Thiện Dàn Ý</div>', unsafe_allow_html=True)
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_DATA[list(DE_BAI_DATA.keys())[0]])
    
    c_left, c_right = st.columns([1.2, 0.8], gap="large")
    with c_left:
        st.markdown("#### 🛠️ Khung Gợi Ý Tư Duy")
        with st.expander("📌 Thao tác 1: Giải thích bản chất", expanded=True):
            for item in cur_de_info.get("explain_core", []):
                st.markdown(f"- {item}")
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**{q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")
                    
        st.markdown("#### 📝 Dàn Ý Của Em")
        default_outline = f"I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề: {cur_de_info['vdnl_chuan']}\n\nII. THÂN BÀI:\n1. Giải thích:\n2. Bàn luận:\n3. Dẫn chứng:\n4. Phản biện:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động:"
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
