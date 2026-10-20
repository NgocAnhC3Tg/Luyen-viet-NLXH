import streamlit as st
import json
import re
from google import genai
from PIL import Image

# ==============================================================================
# CẤU HÌNH TRANG WEB VÀ GIAO DIỆN SƯ PHẠM
# ==============================================================================
st.set_page_config(
    page_title="Quy Trình 4 Bước Tạo Lập Bài Văn NLXH",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .step-badge {
        background-color: #e8f0fe;
        color: #1a73e8;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 12px;
        font-size: 0.88rem;
        border: 1px solid #c2e7ff;
    }
    .step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .next-step-card {
        background: linear-gradient(135deg, #f0f7ff 0%, #e6f0fa 100%);
        border: 2px dashed #1a73e8;
        border-radius: 14px;
        padding: 22px 25px;
        margin-top: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(26, 115, 232, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# NGÂN HÀNG 30 ĐỀ THI NGHỊ LUẬN XÃ HỘI (GDPT 2018)
# ==============================================================================
DE_BAI_DATA = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:

> *"Khi ta ở, chỉ là nơi đất ở  
> Khi ta đi, đất đã hóa tâm hồn!"*

Từ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (từ 600 đến 1000 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "topic_tag": "Trách nhiệm – Cống hiến – Tình người",
        "explain_core": [
            "**Lối sống có trách nhiệm:** Nhận thức rõ bổn phận, nghĩa vụ của bản thân đối với gia đình, cộng đồng; không thờ ơ, bàng quan trước đời sống.",
            "**Gắn bó với cộng đồng:** Tinh thần hòa nhập, sẻ chia niềm vui, nỗi buồn và cống hiến công sức cho tập thể.",
            "**Ý nghĩa ngữ liệu:** Sự chuyển hóa kỳ diệu từ không gian địa lý đơn thuần sang không gian tâm hồn thiêng liêng khi con người biết sống hết mình và trao đi yêu thương."
        ],
        "questions": [
            {"cau_hoi": "Câu hỏi 1: Vì sao người trẻ cần sống có trách nhiệm và gắn bó với cộng đồng?", "y_tra_loi": ["Mỗi cá nhân là một tế bào của xã hội; không ai có thể tồn tại và phát triển độc lập như một ốc đảo.", "Mọi điều kiện học tập, tiện nghi ta thụ hưởng đều được xây đắp từ công sức của bao thế hệ đi trước.", "Sự gắn bó giúp đẩy lùi căn bệnh vô cảm, tạo lập môi trường sống nhân ái, an toàn."]},
            {"cau_hoi": "Câu hỏi 2: Lối sống trách nhiệm mang lại giá trị gì cho chính bản thân em?", "y_tra_loi": ["Giúp hoàn thiện nhân cách, nuôi dưỡng lòng thấu cảm và mở rộng thế giới quan.", "Khẳng định giá trị thực chất và phẩm giá của bản thân thông qua những hành động hữu ích.", "Tạo dựng các mối quan hệ chân thành, nhận được sự tin yêu và trợ lực từ cộng đồng."]},
            {"cau_hoi": "Câu hỏi 3: Lối sống ấy tạo nên tác động gì cho tập thể và xã hội?", "y_tra_loi": ["Huy động sức mạnh đại đoàn kết để cùng vượt qua thiên tai, dịch bệnh, hoạn nạn.", "Lan tỏa nguồn năng lượng sống tích cực, hình thành chuẩn mực văn hóa ứng xử nhân văn.", "Là bệ phóng vững chắc để đất nước phát triển bền vững và hội nhập quốc tế."]}
        ],
        "counter": ["Phê phán lối sống vị kỷ, thờ ơ trước nỗi đau của đồng loại, xem việc chung là chuyện của người khác.", "Lật lại vấn đề: Sống vì cộng đồng không đồng nghĩa với bao đồng mù quáng hay đánh mất bản thân; cần biết cân bằng giữa phát triển cá nhân và phụng sự xã hội."]
    },
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa. Đó chính là ý nghĩa của cơn bão."* Nhưng để cùng nhau đi qua những 'cơn bão lòng', con người rất cần sự thấu hiểu.

Hãy viết một bài văn nghị luận (từ 600 đến 1000 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "topic_tag": "Thấu cảm – Lắng nghe – Hàn gắn",
        "explain_core": [
            "**Sự thấu cảm:** Năng lực đặt mình vào vị trí, hoàn cảnh và cảm xúc của người khác để hiểu thấu và chia sẻ sâu sắc.",
            "**Lắng nghe chân thành:** Thái độ lắng nghe không phán xét, đón nhận bằng sự tôn trọng và thấu hiểu thực chất.",
            "**Ý nghĩa kết hợp:** Chiếc cầu nối tâm hồn giúp xoa dịu những tổn thương tinh thần và hàn gắn các mối quan hệ rạn nứt."
        ],
        "questions": [
            {"cau_hoi": "Câu hỏi 1: Vì sao con người hiện đại có xu hướng ngày càng ít lắng nghe và khó thấu cảm?", "y_tra_loi": ["Nhịp sống gấp gáp và sự chi phối của thiết bị thông minh làm giảm thời gian tương tác trực tiếp.", "Cái tôi cá nhân quá lớn khiến con người thích bày tỏ, tranh biện hơn là kiên nhẫn lắng nghe.", "Thói quen phán xét nhanh chóng trên mạng xã hội làm xói mòn lòng trắc ẩn tự nhiên."]},
            {"cau_hoi": "Câu hỏi 2: Sự thấu cảm đem lại ý nghĩa gì cho bản thân và người nhận?", "y_tra_loi": ["Người trao đi: Nuôi dưỡng tâm hồn bao dung, giải tỏa định kiến và hoàn thiện trí tuệ cảm xúc (EQ).", "Người được lắng nghe: Cảm nhận được sự tôn trọng, giải tỏa bế tắc tinh thần và tìm lại điểm tựa vượt qua khủng hoảng."]},
            {"cau_hoi": "Câu hỏi 3: Lối sống thấu cảm tác động như thế nào đến cộng đồng?", "y_tra_loi": ["Giảm thiểu xung đột, mâu thuẫn thế hệ và các hiện tượng bạo lực học đường/bạo lực mạng.", "Xây dựng một xã hội văn minh, nhân ái, nơi không ai bị bỏ lại phía sau bởi sự cô đơn."]}
        ],
        "counter": ["Phê phán thói vô cảm, công kích cá nhân, dửng dưng trước nỗi đau hoặc sự bế tắc của đồng loại.", "Lật lại vấn đề: Thấu cảm không đồng nghĩa với đồng lõa cho cái sai hay bị cảm xúc chi phối làm mất đi tính kỷ cương của pháp luật."]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc trong dòng chảy toàn cầu hóa": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*

Viết bài văn nghị luận (từ 600 đến 1000 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh toàn cầu hóa.",
        "topic_tag": "Bản sắc văn hóa – Nguồn cội – Hội nhập",
        "explain_core": [
            "**Bản sắc văn hóa dân tộc:** Những giá trị tinh hoa vật chất và tinh thần cốt lõi, độc đáo được hun đúc qua hàng nghìn năm lịch sử.",
            "**Hình ảnh chiếc mỏ neo:** Điểm tựa vững chãi giữ cho quốc gia, dân tộc giữ vững cội nguồn, không bị hòa tan khi hội nhập thế giới."
        ],
        "questions": [
            {"cau_hoi": "Câu hỏi 1: Vì sao người trẻ cần giữ gìn bản sắc văn hóa trong thời đại hội nhập?", "y_tra_loi": ["Văn hóa là căn cước của quốc gia; đánh mất bản sắc là mất đi vị thế độc lập trên trường quốc tế.", "Sự du nhập ồ ạt của các sản phẩm ngoại lai dễ dẫn đến nguy cơ lai căng, lãng quên truyền thống.", "Bản sắc truyền thống chính là nguồn cảm hứng độc đáo để sáng tạo nên các sản phẩm văn hóa mới."]},
            {"cau_hoi": "Câu hỏi 2: Thế hệ trẻ có thể giữ gìn và làm mới văn hóa dân tộc bằng cách nào?", "y_tra_loi": ["Tôn trọng và giữ gìn sự trong sáng của tiếng Việt, tích cực tìm hiểu lịch sử và phong tục tập quán.", "Ứng dụng công nghệ số và truyền thông hiện đại để quảng bá văn hóa Việt Nam ra thế giới.", "Hòa nhập nhưng không hòa tan: tiếp thu có chọn lọc văn minh nhân loại mà vẫn giữ cốt cách dân tộc."]},
            {"cau_hoi": "Câu hỏi 3: Việc giữ gìn bản sắc đóng góp gì cho sự phát triển của đất nước?", "y_tra_loi": ["Tạo nên sức mạnh mềm quốc gia và nội lực phát triển bền vững cho đất nước.", "Khẳng định niềm tự hào và sự tự tôn của dân tộc Việt Nam trên bản đồ văn hóa thế giới."]}
        ],
        "counter": ["Phê phán tâm lý sính ngoại mù quáng, quay lưng với văn hóa truyền thống, xem thường cội nguồn dân tộc.", "Lật lại vấn đề: Giữ gìn bản sắc không phải là khép kín, bảo thủ hay bài trừ tinh hoa thế giới; mà là tiếp biến có chọn lọc."]
    },
    "Đề 16 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*

Viết bài văn nghị luận (từ 600 đến 1000 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực của số đông đối với người trẻ trong kỷ nguyên số.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng, chính kiến cá nhân trước áp lực của đám đông trong thời đại số.",
        "topic_tag": "Bản lĩnh – Tư duy độc lập – Bản sắc",
        "explain_core": [
            "**Bản sắc riêng & chính kiến:** Cá tính độc đáo, tư duy độc lập và hệ giá trị riêng biệt làm nên phẩm giá cá nhân.",
            "**Áp lực số đông:** Sự lôi kéo, phán xét từ đám đông (đặc biệt trên không gian mạng) dễ đẩy con người vào lối sống hòa tan, rập khuôn."
        ],
        "questions": [
            {"cau_hoi": "Vì sao giữ bản sắc riêng lại khó khăn trong kỷ nguyên số?", "y_tra_loi": ["Thuật toán và mạng xã hội dễ tạo tâm lý bầy đàn, sợ bị tẩy chay nếu đi ngược đám đông."]},
            {"cau_hoi": "Bản sắc riêng đem lại giá trị gì?", "y_tra_loi": ["Giúp cá nhân tự tin tỏa sáng bằng năng lực thật, thúc đẩy xã hội đa dạng và sáng tạo."]}
        ],
        "counter": ["Phê phán lối sống hùa theo phong trào, a dua thiếu suy nghĩ.", "Lật lại vấn đề: Giữ bản sắc không đồng nghĩa với lập dị, chống đối cực đoan hay coi thường chuẩn mực cộng đồng."]
    }
}

for i in range(4, 31):
    k_name = f"Đề {i:02d}"
    if not any(k_name in k for k in DE_BAI_DATA.keys()):
        is_nc = "Nâng cao" if i >= 16 else "Cơ bản"
        DE_BAI_DATA[f"{k_name} ({is_nc}): Rèn luyện năng lực tư duy thực tiễn"] = {
            "text": f"Hãy viết một bài văn nghị luận (từ 600 đến 1000 chữ) bàn về một phẩm chất sống hoặc vấn đề xã hội thiết thực của thanh niên hôm nay ({k_name}).",
            "vdnl_chuan": f"Tư duy độc lập và trách nhiệm công dân của người trẻ ({k_name}).",
            "topic_tag": "Kỹ năng sống – Bản lĩnh",
            "explain_core": ["Làm rõ bản chất khái niệm then chốt trong đề bài và ý nghĩa định hướng đời sống."],
            "questions": [{"cau_hoi": "Vì sao vấn đề này có ý nghĩa với em?", "y_tra_loi": ["Giúp hoàn thiện tư duy và nhân cách sống."]}],
            "counter": ["Phê phán nhận thức lệch lạc và hành vi tiêu cực."]
        }

# ==============================================================================
# KHO DẪN CHỨNG ĐẦY ĐỦ 8 NHÓM CHỦ ĐIỂM
# ==============================================================================
KHO_DAN_CHUNG = {
    "1. Lòng nhân ái – Trách nhiệm cộng đồng": [
        {
            "nv": "Trưởng thôn Ma Seo Chứ (Lào Cai)",
            "nd": "Trong cơn bão số 3 (Yagi) năm 2024, bằng linh cảm nhạy bén và tinh thần trách nhiệm với sinh mạng của bà con, anh đã chủ động đi khảo sát đồi nứt và kiên quyết di dời 115 người dân thôn Kho Vàng lên núi dựng lán trú ẩn trước khi trận lũ quét kinh hoàng san phẳng làng xóm.",
            "nguon": "Báo Dân Trí, Tiền Phong, VTV (09/2024)"
        },
        {
            "nv": "Bé Nguyễn Hải An (7 tuổi, Hà Nội)",
            "nd": "Trước khi qua đời vì căn bệnh u thần kinh đệm cầu não lan tỏa năm 2018, bé và mẹ đã tình nguyện hiến tặng giác mạc để mang lại ánh sáng cho 2 người khác. Hành động nhân văn của 'thiên thần nhỏ' đã mở đầu làn sóng đăng ký hiến tạng rộng khắp cả nước.",
            "nguon": "Báo VnExpress, Tuổi Trẻ (2018)"
        },
        {
            "nv": "Thầy giáo James Joseph Kendall & Nhóm Keep Hanoi Clean",
            "nd": "Chàng trai người Mỹ cùng hàng ngàn tình nguyện viên bền bỉ nhiều năm lội xuống những mương nước ô nhiễm ở Hà Nội dọn rác, lan tỏa ý thức trách nhiệm bảo vệ môi trường đến đông đảo bạn trẻ Việt Nam.",
            "nguon": "VTV, Báo Lao Động"
        },
        {
            "nv": "Quán cơm Yên Vui & Quán cơm nụ cười 2.000 đồng",
            "nd": "Mô hình những bữa cơm giá chỉ 2.000 đồng xuất hiện tại nhiều thành phố lớn, được duy trì bền bỉ từ sự đóng góp thầm lặng của cộng đồng nhằm trao gửi sự tôn trọng và chở che cho người lao động nghèo, bệnh nhân cơ nhỡ.",
            "nguon": "Báo Thanh Niên, Đài Truyền hình TP.HCM"
        }
    ],
    "2. Ý chí – Nghị lực – Vượt nghịch cảnh": [
        {
            "nv": "Vận động viên Derek Redmond (Olympic Barcelona 1992)",
            "nd": "Bị rách gân khoeo đau đớn gục ngã trên đường chạy bán kết 400m, nhưng anh kiên quyết đứng dậy. Dưới sự dìu đỡ của người cha vượt qua lực lượng an ninh, anh đã bước từng bước khập khiễng về đích trong sự xúc động của 65.000 khán giả.",
            "nguon": "Olympic Channel, BBC Sport"
        },
        {
            "nv": "Christine Hà (Quán quân MasterChef Mỹ mùa 3)",
            "nd": "Mất đi hoàn toàn thị giác do căn bệnh viêm tủy thị thần kinh, cô không từ bỏ đam mê ẩm thực mà dùng xúc giác, khứu giác, sự nhạy cảm và một ý chí phi thường để vượt qua hàng ngàn đầu bếp sáng mắt, đoạt ngôi vị quán quân thế giới.",
            "nguon": "MasterChef USA - Fox TV, The New York Times"
        },
        {
            "nv": "Nguyễn Sơn Lâm (Chàng trai nạng gỗ)",
            "nd": "Dù cơ thể chỉ cao chưa đầy 1m, teo tóp hai chân do di chứng chất độc da cam và phải di chuyển bằng nạng, anh đã nỗ lực tự học thông thạo 3 ngoại ngữ và trở thành người khuyết tật đầu tiên của Việt Nam chinh phục thành công đỉnh Fansipan.",
            "nguon": "Báo Thanh Niên, VTV Special"
        },
        {
            "nv": "Họa sĩ vẽ tranh bằng chân Lê Minh Châu",
            "nd": "Bị khuyết tật cả tay lẫn chân do chất độc da cam, anh ngậm cọ vào miệng để vẽ nên những bức tranh tràn đầy khát vọng sống. Câu chuyện của anh đã truyền cảm hứng tới bộ phim tài liệu 'Chau, Beyond the Lines' từng được đề cử giải Oscar.",
            "nguon": "Viện Hàn lâm Điện ảnh Mỹ (Oscars), Báo Tuổi Trẻ"
        }
    ],
    "3. Sáng tạo – Đổi mới – Tinh thần tiên phong": [
        {
            "nv": "Kỹ sư Eiji Nakatsu (Tàu siêu tốc Shinkansen Nhật Bản)",
            "nd": "Khi tàu siêu tốc chạy qua hầm gây ra tiếng nổ sóng âm lớn làm phiền khu dân cư, kỹ sư Nakatsu đã quan sát cấu tạo chiếc mỏ chim bói cá khi lao xuống nước bắt mồi không gây tiếng động. Ông thiết kế lại mũi tàu Shinkansen theo hình mỏ chim bói cá, giúp tàu chạy êm hơn, tăng tốc 10% và tiết kiệm 15% điện năng.",
            "nguon": "Japan Railway Journal, Biomimicry Institute"
        },
        {
            "nv": "Triết lý sáng tạo khác biệt của Steve Jobs (Apple)",
            "nd": "Từ chối đi theo lối mòn tạo ra những chiếc máy tính văn phòng thô cứng, Steve Jobs kiên trì theo đuổi sự giao thoa giữa nghệ thuật và công nghệ (Liberal Arts & Technology), tạo nên giao diện đồ họa, chuột máy tính, iPod và iPhone định hình lại cách nhân loại sống và giao tiếp.",
            "nguon": "Tiểu sử Steve Jobs - Walter Isaacson"
        },
        {
            "nv": "Nhà nông học Hồ Quang Cua và giống gạo ST25",
            "nd": "Dành trọn hơn 25 năm bền bỉ lội ruộng, lai tạo và thử nghiệm hàng nghìn tổ hợp giống tại vùng đất ngập mặn Sóc Trăng để tạo nên giống gạo ST25 được vinh danh là 'Gạo ngon nhất thế giới', nâng tầm giá trị nông sản Việt Nam.",
            "nguon": "The World's Best Rice, Báo Nông nghiệp Việt Nam"
        },
        {
            "nv": "Nhóm sinh viên Đại học Bách Khoa chế tạo Robot y tế Vibot",
            "nd": "Trước tình thế cấp bách của các khu cách ly Covid-19, nhóm kỹ sư trẻ đã tự nghiên cứu, cải tiến và sản xuất thành công robot vận chuyển đồ ăn, thuốc men và hỗ trợ y bác sĩ thăm khám bệnh nhân từ xa, giảm thiểu rủi ro lây nhiễm chéo.",
            "nguon": "Bộ Khoa học và Công nghệ, Báo Nhân Dân"
        },
        {
            "nv": "Boyan Slat và Dự án làm sạch đại dương (The Ocean Cleanup)",
            "nd": "Năm 18 tuổi, chứng kiến biển Hy Lạp ngập rác nhựa, Boyan Slat đã bỏ học đại học để sáng lập hệ thống rào chắn nổi tận dụng dòng hải lưu tự nhiên gom rác tự động giữa Thái Bình Dương, mở ra hướng đi đột phá xử lý ô nhiễm rác thải nhựa toàn cầu.",
            "nguon": "BBC News, Time Magazine"
        }
    ],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [
        {
            "nv": "Nhà bác học Galileo Galilei",
            "nd": "Kiên cường bảo vệ chân lý khoa học về thuyết Nhật tâm trước tòa án dị giáo và định kiến của toàn bộ xã hội thời Trung cổ với câu nói bất hủ: 'Dù sao thì Trái Đất vẫn quay'.",
            "nguon": "Lịch sử Khoa học thế giới"
        },
        {
            "nv": "Malala Yousafzai (Nobel Hòa bình trẻ tuổi nhất)",
            "nd": "Bất chấp sự đe dọa tàn bạo của phiến quân Taliban và việc từng bị ám sát bắn vào đầu năm 15 tuổi, cô vẫn kiên cường cất cao tiếng nói đòi quyền được đến trường cho trẻ em gái trên toàn thế giới.",
            "nguon": "Ủy ban Nobel, Liên Hợp Quốc (UN)"
        },
        {
            "nv": "Bác sĩ Ignaz Semmelweis (Cha đẻ của việc rửa tay vô trùng)",
            "nd": "Thế kỷ 19, khi y học chưa biết tới vi khuẩn, ông phát hiện việc bác sĩ rửa tay bằng dung dịch khử trùng trước khi đỡ đẻ giúp giảm tỷ lệ tử vong sản phụ từ 18% xuống dưới 1%. Dù bị cả giới y khoa đương thời chế giễu và cô lập, ông vẫn kiên định bảo vệ quan điểm khoa học cứu người.",
            "nguon": "Lịch sử Y học phương Tây, Tạp chí The Lancet"
        }
    ],
    "5. Cống hiến thầm lặng & Trách nhiệm với Tổ quốc": [
        {
            "nv": "Những chiến sĩ Hải quân tại Nhà giàn DK1",
            "nd": "Gác lại tuổi thanh xuân và hơi ấm gia đình, kiên cường bám trụ trên những 'pháo đài thép' giữa ngút ngàn sóng gió Biển Đông, vượt qua bão tố khắc nghiệt để canh giữ từng tấc biển đảo thiêng liêng của Tổ quốc.",
            "nguon": "Báo Quân đội Nhân dân, Truyền hình Quốc phòng"
        },
        {
            "nv": "Đội ngũ rà phá bom mìn tại Quảng Trị (Dự án RENEW / MAG)",
            "nd": "Hàng trăm công nhân và chuyên gia lặng lẽ dò tìm, xử lý hàng triệu tấn vật liệu nổ còn sót lại sau chiến tranh, chấp nhận nguy hiểm tính mạng mỗi ngày để trả lại những mảnh đất bình yên cho nhân dân canh tác.",
            "nguon": "Báo Tuổi Trẻ, Thông tấn xã Việt Nam"
        },
        {
            "nv": "Những người gác chắn đường tàu & Công nhân vệ sinh môi trường ban đêm",
            "nd": "Lao động miệt mài trong đêm tĩnh lặng, bảo đảm an toàn cho những chuyến tàu bình yên và giữ gìn đường phố sạch đẹp trước mỗi sớm mai mà không đòi hỏi sự tung hô.",
            "nguon": "Báo Người Lao Động"
        }
    ],
    "6. Hiện tượng tâm lý – Không gian mạng đương đại": [
        {
            "nv": "Hội chứng sợ bỏ lỡ (FOMO) & Nữ sinh Madison Holleran",
            "nd": "Một vận động viên, sinh viên tài năng của Đại học Pennsylvania (Mỹ) với trang Instagram luôn tràn ngập những bức ảnh lung linh, tươi cười nhưng đã tự vẫn vì không chịu nổi áp lực phải gồng mình diễn sự hoàn hảo trước đám đông.",
            "nguon": "The New York Times, Tạp chí Psychology Today"
        },
        {
            "nv": "Hiệu ứng người ngoài cuộc (Bystander Effect)",
            "nd": "Hiện tượng tâm lý xã hội khi ở chốn đông người, trách nhiệm cá nhân bị phân tán khiến không ai ra tay giúp đỡ nạn nhân khi gặp hoạn nạn, cảnh báo căn bệnh thờ ơ, ỷ lại và vô cảm của thời hiện đại.",
            "nguon": "Thực nghiệm tâm lý học Darley & Latané"
        },
        {
            "nv": "Văn hóa hủy bẩy (Cancel Culture) và bắt nạt trên không gian mạng",
            "nd": "Hiện tượng đám đông mạng nhân danh công lý hùa nhau tấn công trang cá nhân, xúc phạm danh dự một cá nhân khi chưa kiểm chứng rõ sự thật, đẩy nhiều người trẻ vào bước đường trầm cảm, bế tắc.",
            "nguon": "Báo Giáo dục & Thời đại, UNESCO Digital Safety"
        }
    ],
    "7. Bản sắc văn hóa & Tinh thần hội nhập": [
        {
            "nv": "Dự án phục dựng cổ phục Việt của các nhóm bạn trẻ",
            "nd": "Các nhóm nghiên cứu trẻ (Đại Việt Cổ Phong, Ỷ Vân Hiên, Hoa Niên) dành nhiều năm tra cứu sử liệu, khôi phục lại trang phục cung đình và dân gian các triều đại Lý, Trần, Lê, Nguyễn; đưa di sản cổ phong xuất hiện tự hào trong MV ca nhạc, phim ảnh hiện đại.",
            "nguon": "Báo Tuổi Trẻ, VTV4"
        },
        {
            "nv": "Nghệ sĩ trẻ đưa âm hưởng dân tộc vươn ra thế giới",
            "nd": "Những sản phẩm âm nhạc như ca khúc 'See Tình' (Hoàng Thùy Linh) hay các bản hòa tấu kết hợp nhạc cụ dân tộc (đàn bầu, đàn tranh, sáo trúc) với nhạc điện tử hiện đại, chứng minh văn hóa bản địa chính là căn cước độc đáo để hội nhập toàn cầu.",
            "nguon": "Báo Tiền Phong, VietnamPlus"
        },
        {
            "nv": "Các lớp học tiếng Việt miễn phí của kiều bào ở hải ngoại",
            "nd": "Các thầy cô giáo tình nguyện bền bỉ mở lớp dạy tiếng mẹ đẻ cho thế hệ con em sinh ra ở nước ngoài, gìn giữ sợi dây kết nối văn hóa cội nguồn dẫu ở cách xa Tổ quốc.",
            "nguon": "Ủy ban Nhà nước về người Việt Nam ở nước ngoài"
        }
    ],
    "8. Thấu cảm – Lắng nghe – Đối diện thất bại": [
        {
            "nv": "J.K. Rowling và hành trình ra đời của Harry Potter",
            "nd": "Từng là người mẹ đơn thân rơi vào trầm cảm và sống nhờ trợ cấp xã hội, bản thảo Harry Potter của bà bị liên tiếp 12 nhà xuất bản từ chối. Bà không nản lòng mà kiên định gõ cửa nhà xuất bản thứ 13, mở ra một trong những bộ tiểu thuyết vĩ đại nhất thế giới.",
            "nguon": "The Guardian, Tự truyện J.K. Rowling"
        },
        {
            "nv": "Nguyên lý lắng nghe tích cực (Active Listening) & Đường dây nóng tâm lý",
            "nd": "Các mô hình tham vấn tâm lý học đường xây dựng văn hóa lắng nghe không phán xét, tạo điểm tựa cảm xúc an toàn để các bạn trẻ trút bỏ bế tắc và tìm lại niềm tin trong cuộc sống.",
            "nguon": "Tổ chức Y tế Thế giới (WHO), UNICEF"
        },
        {
            "nv": "Nhà sáng lập KFC - Đại tá Harland Sanders",
            "nd": "Bắt đầu khởi nghiệp công thức gà rán ở tuổi 65 sau khi thất bại qua nhiều công việc, ông đã bị từ chối hơn 1.000 lần trước khi tìm được đối tác nhượng quyền đầu tiên, trở thành minh chứng bất hủ cho sự kiên trì.",
            "nguon": "Tiểu sử Harland Sanders, Forbes"
        }
    ]
}

# ==============================================================================
# QUẢN LÝ SESSION STATE & DỌN DẸP KHI ĐỔI ĐỀ
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""
if "last_selected_de" not in st.session_state:
    st.session_state["last_selected_de"] = ""
if "custom_de_analyzed" not in st.session_state:
    st.session_state["custom_de_analyzed"] = False
if "custom_de_data" not in st.session_state:
    st.session_state["custom_de_data"] = None
if "eval_vdnl_result" not in st.session_state:
    st.session_state["eval_vdnl_result"] = None

def kiem_tra_va_reset_khi_doi_de(ten_de_moi):
    if st.session_state["last_selected_de"] != ten_de_moi:
        st.session_state["last_selected_de"] = ten_de_moi
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Chào em! Đề bài hiện tại của chúng ta là: '{ten_de_moi}'. Em hãy đọc kỹ khung định hướng bên trái, nếu cần cô gợi mở thêm phần nào thì nhắn cô nhé!"}
        ]
        st.session_state["user_outline"] = ""
        st.session_state["user_essay"] = ""
        st.session_state["eval_vdnl_result"] = None
        if "grading_result" in st.session_state:
            del st.session_state["grading_result"]

with st.sidebar:
    st.header("🔑 Kích Hoạt Trợ Lý AI")
    st.text_input(
        "Dán Gemini API Key vào đây:",
        type="password",
        key="api_key_field",
        value=st.session_state["gemini_api_key"],
        on_change=lambda: st.session_state.update({"gemini_api_key": st.session_state["api_key_field"].strip()}),
        help="Lấy API Key miễn phí tại: https://aistudio.google.com/"
    )
    if st.session_state["gemini_api_key"]:
        st.success("✅ Đã kết nối với Trợ lí Ngữ văn!")
    else:
        st.warning("Dán API Key vào ô trên rồi bấm Enter để AI hoạt động.")

    st.markdown("---")
    st.markdown("### 🧭 Quy Trình 4 Bước Tạo Lập Văn Bản")
    st.markdown("""
    1. **Bước 1 (Tìm hiểu đề):** Cắt nghĩa lệnh đề & nhận diện vấn đề nghị luận cốt lõi.
    2. **Bước 2 (Tìm ý & Lập dàn ý):** Trợ lí gợi mở câu hỏi tư duy theo từng đề bài cụ thể, tra cứu dẫn chứng & tự hoàn thiện dàn ý 3 phần (Không viết hộ).
    3. **Bước 3 (Viết bài):** Xưởng viết độc lập (từ 600 đến 1000 chữ) & Nộp ảnh bài viết tay.
    4. **Bước 4 (Chỉnh sửa & Đánh giá):** Giám khảo AI chấm điểm theo Bảng Rubric & gợi ý tự sửa câu văn.
    """)

# ==============================================================================
# HÀM KẾT NỐI GEMINI AI DÙNG MODEL CHUẨN GEMINI-3.8-FLASH
# ==============================================================================
def call_gemini_engine(prompt_or_contents):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "[Thông báo]: Chưa nhận được API Key. Hãy dán mã Gemini API Key vào ô bên trái (Sidebar) rồi nhấn Enter để kích hoạt nhé!"

    client = genai.Client(api_key=api_key)
    models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
    last_error = ""
    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=prompt_or_contents,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            continue
    return f"[Lỗi kết nối]: {last_error}\n\nHãy kiểm tra lại mã API Key ở cột bên trái nhé!"

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    """Giáo viên AI thẩm định công tâm phán đoán VĐNL của học sinh (phân 3 mức DUNG, LECH, SAI)"""
    prompt = f"""
Bạn là Giám khảo chấm thi môn Ngữ văn THPT theo định hướng GDPT 2018.
- Đề bài: {exam_text}
- Vấn đề nghị luận chuẩn (đáp án): {vdnl_chuan}
- Câu trả lời của học sinh: "{student_guess}"

Hãy thẩm định công tâm xem học sinh trả lời Đúng, Lệch (thiếu vế) hay Sai hoàn toàn:
1. 'status': Bắt buộc chọn 1 trong 3 giá trị: "DUNG", "LECH", "SAI"
   - "DUNG": Nắm trúng vấn đề cốt lõi.
   - "LECH": Chỉ nói được khía cạnh phụ, hiểu bề nổi, hoặc thiếu vế đối ứng then chốt trong đề.
   - "SAI": Lạc đề hoàn toàn, hiểu sai bản chất câu nói/lệnh đề.
2. 'feedback': Lời nhận xét sư phạm trực tiếp (xưng cô - em):
   - Nếu DUNG: Khẳng định ngắn gọn điểm trúng và khen ngợi.
   - Nếu LECH hoặc SAI: Chỉ rõ ngay lập tức em đang nhầm lẫn ở đâu, từ ngữ nào trong đề bị em bỏ sót hoặc hiểu sai, và đặt 1 câu hỏi dẫn dắt để học sinh tư duy lại.

BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "lời nhận xét cụ thể của giáo viên",
  "suggested_fix": "{vdnl_chuan}"
}}
"""
    raw_res = call_gemini_engine(prompt)
    try:
        match = re.search(r"\{.*\}", raw_res, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw_res)
    except Exception:
        return {
            "status": "LECH",
            "feedback": "Em hãy đọc kỹ lại từ khóa chính trong câu lệnh đề và đối chiếu lại nhé!",
            "suggested_fix": vdnl_chuan
        }

def ai_analyze_custom_exam(exam_text, student_guess=""):
    """Phân tích tự động đề tự nhập của học sinh, thẩm định VĐNL và tự sinh giàn giáo Bước 2"""
    prompt = f"""
Bạn là chuyên gia giáo dục Ngữ văn THPT định hướng GDPT 2018.
Học sinh tự mang đến một đề bài Nghị luận xã hội mới:
\"\"\"{exam_text}\"\"\"

Học sinh phán đoán Vấn đề nghị luận (VĐNL) là: \"{student_guess}\"

Nhiệm vụ của bạn:
1. Thẩm định câu trả lời của học sinh theo 3 mức: "DUNG", "LECH", "SAI":
   - "status": "DUNG" | "LECH" | "SAI"
   - "teacher_evaluation": Lời nhận xét sư phạm thẳng thắn (xưng cô - em). Nếu sai/lệch thì chỉ rõ tại sao và vì sao chưa trúng.
2. Tự động bóc tách và phân tích toàn diện đề thi này để tạo dữ liệu giàn giáo học tập cho học sinh ở Bước 2.

BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON DUY NHẤT:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "teacher_evaluation": "Lời nhận xét thẩm định của giáo viên",
  "vdnl_chuan": "Vấn đề nghị luận chuẩn xác nhất của đề này",
  "topic_tag": "Chủ điểm bài học (Ví dụ: Bản lĩnh – Trách nhiệm – Lối sống...)",
  "explain_core": [
     "Cắt nghĩa từ khóa/mệnh đề then chốt thứ 1 trong đề",
     "Cắt nghĩa từ khóa/mệnh đề then chốt thứ 2 (hoặc ý nghĩa câu nói/câu thơ trích dẫn nếu có)"
  ],
  "questions": [
     {{
       "cau_hoi": "Câu hỏi gợi mở 1 (Vì sao vấn đề này lại quan trọng/cần thiết trong đời sống?)",
       "y_tra_loi": ["Gợi ý luận điểm a", "Gợi ý luận điểm b"]
     }},
     {{
       "cau_hoi": "Câu hỏi gợi mở 2 (Vấn đề này mang lại giá trị/sự trưởng thành gì cho bản thân người trẻ?)",
       "y_tra_loi": ["Gợi ý luận điểm a", "Gợi ý luận điểm b"]
     }},
     {{
       "cau_hoi": "Câu hỏi gợi mở 3 (Vấn đề này tác động tích cực gì cho cộng đồng và xã hội?)",
       "y_tra_loi": ["Gợi ý luận điểm a", "Gợi ý luận điểm b"]
     }}
  ],
  "counter": [
     "Gợi ý phê phán biểu hiện tiêu cực hoặc lối sống đi ngược lại",
     "Gợi ý lật lại vấn đề: phân biệt ranh giới đúng - sai thấu đáo"
  ]
}}
"""
    raw_res = call_gemini_engine(prompt)
    try:
        match = re.search(r"\{.*\}", raw_res, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw_res)
    except Exception:
        return {
            "status": "LECH",
            "teacher_evaluation": "Cô nhận thấy em đã bước đầu nắm được tinh thần của đề bài nhưng cần đào sâu hơn vào từ khóa cốt lõi.",
            "vdnl_chuan": "Vấn đề nghị luận rút ra từ đề bài tự nhập",
            "topic_tag": "Đề tự chọn",
            "explain_core": ["Làm rõ các từ ngữ/mệnh đề quan trọng nhất trong đề bài."],
            "questions": [
                {"cau_hoi": "Vì sao vấn đề này lại cần thiết trong cuộc sống?", "y_tra_loi": ["Là phẩm chất/nhận thức quan trọng giúp hoàn thiện nhân cách."]},
                {"cau_hoi": "Ý nghĩa đối với sự trưởng thành của cá nhân?", "y_tra_loi": ["Giúp cá nhân sống bản lĩnh, có định hướng rõ ràng."]},
                {"cau_hoi": "Tác động đối với cộng đồng và xã hội?", "y_tra_loi": ["Lan tỏa giá trị nhân văn và xây dựng xã hội tiến bộ."]}
            ],
            "counter": ["Phê phán nhận thức lệch lạc và hành vi tiêu cực.", "Lật lại vấn đề: ranh giới đúng - sai."]
        }

def call_gemini_tutor(messages_history, prompt_context=""):
    su_pham_instruction = f"""
[VAI TRÒ VÀ NGUYÊN TẮC SƯ PHẠM - BƯỚC 2: TRỢ LÝ TRUY VẤN TƯ DUY, KHÔNG LÀM THAY]
Bạn là 'Trợ lí Ngữ văn' đồng hành cùng học sinh THPT theo định hướng GDPT 2018.
Khung kiến thức giàn giáo của đề bài học sinh đang làm:
{prompt_context}

NGUYÊN TẮC TƯ VẤN SƯ PHẠM:
1. Bạn phải đọc kỹ nội dung đề bài và khung giàn giáo trên. Khi học sinh hỏi về khâu nào, hãy dùng chính các từ ngữ trong đề bài đó để gợi ý câu hỏi tư duy.
2. TUYỆT ĐỐI KHÔNG VIẾT HỘ bài văn, đoạn văn mở bài/kết bài mẫu hoàn chỉnh.
3. KHÔNG làm thay cả dàn ý chi tiết.
4. Xưng hô 'cô' - 'em'. Ngắn gọn, ấm áp, sâu sắc và luôn kết thúc bằng 1 câu hỏi dẫn dắt cụ thể để học sinh tự làm tiếp.
"""
    conversation_text = ""
    for msg in messages_history[:-1]:
        role_label = "Học sinh: " if msg["role"] == "user" else "Trợ lí Ngữ văn: "
        conversation_text += f"{role_label}{msg['content']}\n\n"
    latest_query = messages_history[-1]["content"]
    full_prompt = f"{su_pham_instruction}\n\n[LỊCH SỬ TRAO ĐỔI]:\n{conversation_text}\nHọc sinh: {latest_query}\nTrợ lí Ngữ văn:"
    return call_gemini_engine(full_prompt)

# ==============================================================================
# GIAO DIỆN CHÍNH: TIÊU ĐỀ & ĐIỀU HƯỚNG 4 BƯỚC + HỒ SƠ
# ==============================================================================
st.markdown("""
<div class="main-header">
    <h2 style="margin:0; font-size:1.85rem; font-weight:800;">QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NGHỊ LUẬN XÃ HỘI</h2>
    <p style="margin:8px 0 0 0; opacity:0.92; font-size:1.02rem;">
        Phát triển năng lực tạo lập văn bản theo định hướng GDPT 2018 | Rèn luyện tư duy độc lập – Trợ lí AI định hướng phương pháp
    </p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý & LẬP DÀN Ý",
    "✍️ BƯỚC 3: VIẾT BÀI",
    "🔍 BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ",
    "📁 HỒ SƠ BÀI LÀM"
])

# ==============================================================================
# BƯỚC 1: TÌM HIỂU ĐỀ
# ==============================================================================
with tabs[0]:
    st.markdown('<span class="step-badge">BƯỚC 1: TÌM HIỂU ĐỀ</span>', unsafe_allow_html=True)
    st.subheader("Đọc Kỹ Đề Bài & Xác Định Vấn Đề Nghị Luận Cốt Lõi")
    
    muc_do_de = st.radio(
        "Lựa chọn dạng đề bài:",
        ["Đề cơ bản", "Đề nâng cao", "Tự nhập đề bài riêng"],
        index=0,
        horizontal=True
    )
    
    if muc_do_de == "Tự nhập đề bài riêng":
        st.session_state["is_custom_de"] = True
        custom_de_input = st.text_area(
            "Dán toàn bộ đề bài văn nghị luận xã hội của em vào đây:",
            value=st.session_state.get("saved_custom_de_text", ""),
            placeholder="Ví dụ: Đọc đoạn trích sau... Viết bài văn nghị luận từ 600 đến 1000 chữ bàn về...",
            height=130,
            key="input_custom_de_key"
        )
        st.session_state["saved_custom_de_text"] = custom_de_input
        
        ten_de_hien_tai = "Đề bài tự nhập: " + (custom_de_input[:35] + "..." if len(custom_de_input) > 35 else custom_de_input)
        if not custom_de_input.strip():
            ten_de_hien_tai = "Đề tự nhập (Chưa có nội dung)"
        kiem_tra_va_reset_khi_doi_de(ten_de_hien_tai)
        
        st.markdown("##### ⚡ Thao tác tư duy của học sinh:")
        student_vdnl = st.text_input(
            "Hãy xác định vấn đề nghị luận cốt lõi để bắt tay tìm ý và xây dựng luận điểm cho bài viết nhé:",
            placeholder="Gõ ngắn gọn vấn đề nghị luận theo cách hiểu của em tại đây..."
        )
        
        if st.button("🔍 Thẩm định Vấn đề nghị luận & Tự động tạo giàn giáo Bước 2"):
            if not custom_de_input.strip():
                st.warning("⚠️ Em chưa dán nội dung đề bài vào ô phía trên!")
            elif not student_vdnl.strip():
                st.warning("⚠️ Em hãy tự gõ phán đoán Vấn đề nghị luận của mình trước nhé!")
            elif not st.session_state.get("gemini_api_key"):
                st.warning("⚠️ Cần dán Gemini API Key ở cột bên trái để kích hoạt tính năng thẩm định đề tự nhập nhé!")
            else:
                with st.spinner("Cô đang phân tích đề bài và thẩm định câu trả lời của em..."):
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
            status = res.get("status", "LECH")
            
            if status == "DUNG":
                st.success("🎯 **CHÍNH XÁC! CÔ KHEN EM ĐÃ BẮT TRÚNG VẤN ĐỀ:**")
                st.markdown(f"> *{res.get('feedback')}*")
                st.markdown(f"- **Vấn đề nghị luận cốt lõi chuẩn:** *{data['vdnl_chuan']}*")
                st.markdown(f"- **Chủ điểm bài học:** *{data['topic_tag']}*")
                st.info("✅ Giàn giáo cho đề này đã sẵn sàng! Hãy bấm chuyển sang **BƯỚC 2: TÌM Ý & LẬP DÀN Ý** để bắt đầu dệt ý.")
            elif status == "LECH":
                st.warning("⚠️ **CHƯA ĐỦ / CÒN LỆCH Ý: EM CẦN ĐIỀU CHỈNH LẠI:**")
                st.markdown(f"> *{res.get('feedback')}*")
                st.markdown(f"- **Vấn đề nghị luận thực sự của đề bài là:** *{data['vdnl_chuan']}*")
                st.markdown(f"- **Chủ điểm bài học:** *{data['topic_tag']}*")
                st.error("👉 **Lời khuyên sư phạm:** Hãy đọc kỹ nhận xét trên để chỉnh lại cách hiểu trước khi sang Bước 2, tránh việc bài viết bị lệch trọng tâm!")
            else:
                st.error("❌ **CHƯA ĐÚNG / CÓ DẤU HIỆU LẠC ĐỀ:**")
                st.markdown(f"> *{res.get('feedback')}*")
                st.markdown(f"- **Vấn đề nghị luận thực sự của đề bài là:** *{data['vdnl_chuan']}*")
                st.warning("👉 Hãy đọc kỹ phân tích của cô ở trên và gõ lại câu trả lời để rèn luyện thói quen đọc đề cẩn thận nhé!")
            
            de_info = {
                "text": custom_de_input,
                "vdnl_chuan": data["vdnl_chuan"],
                "topic_tag": data["topic_tag"],
                "explain_core": data["explain_core"],
                "questions": data["questions"],
                "counter": data["counter"]
            }
        else:
            de_info = {
                "text": custom_de_input if custom_de_input.strip() else "Chưa có nội dung đề bài.",
                "vdnl_chuan": "Đề tự nhập (Chưa bấm thẩm định)",
                "topic_tag": "Đề tự chọn",
                "explain_core": ["Hãy nhập đề và bấm nút thẩm định ở trên để hệ thống tự động sinh giàn giáo nhé."],
                "questions": [{"cau_hoi": "Câu hỏi bản chất", "y_tra_loi": ["Đang chờ phân tích đề..."]}],
                "counter": ["Đang chờ phân tích đề..."]
            }
        selected_de_key = ten_de_hien_tai
        
    else:
        st.session_state["is_custom_de"] = False
        st.session_state["custom_de_analyzed"] = False
        if muc_do_de == "Đề nâng cao":
            st.session_state["muc_tieu_hoc_tap"] = "nang_cao"
            filtered_de_keys = [k for k in DE_BAI_DATA.keys() if "(Nâng cao)" in k]
        else:
            st.session_state["muc_tieu_hoc_tap"] = "co_ban"
            filtered_de_keys = [k for k in DE_BAI_DATA.keys() if "(Cơ bản)" in k]
            
        selected_de_key = st.selectbox("Chọn đề bài trong danh sách:", filtered_de_keys)
        kiem_tra_va_reset_khi_doi_de(selected_de_key)
        de_info = DE_BAI_DATA[selected_de_key]
        
        st.info("📖 **NỘI DUNG ĐỀ BÀI:**")
        clean_exam_text = de_info['text'].replace("**", "")
        st.markdown(clean_exam_text)
        
        st.markdown("##### ⚡ Thao tác tư duy của học sinh:")
        student_vdnl = st.text_input(
            "Hãy xác định vấn đề nghị luận cốt lõi để bắt tay tìm ý và xây dựng luận điểm cho bài viết nhé:",
            placeholder="Gõ ngắn gọn vấn đề nghị luận theo cách hiểu của em tại đây..."
        )
        
        if st.button("🔍 Đối chiếu & Thẩm định Vấn đề nghị luận cùng Giáo viên"):
            if not student_vdnl.strip():
                st.warning("⚠️ Em hãy tự mình gõ thử câu trả lời vào ô phía trên trước khi bấm đối chiếu nhé!")
            elif not st.session_state.get("gemini_api_key"):
                st.warning("⚠️ Cần dán Gemini API Key ở cột bên trái để AI thẩm định nhé!")
            else:
                with st.spinner("Cô đang đọc kỹ câu trả lời và đối chiếu với lệnh đề..."):
                    eval_res = ai_evaluate_student_vdnl(
                        exam_text=de_info['text'],
                        vdnl_chuan=de_info.get('vdnl_chuan', ''),
                        student_guess=student_vdnl
                    )
                    st.session_state["eval_vdnl_result"] = eval_res
                    
        if "eval_vdnl_result" in st.session_state and st.session_state["eval_vdnl_result"]:
            res = st.session_state["eval_vdnl_result"]
            status = res.get("status", "DUNG")
            feedback = res.get("feedback", "")
            
            if status == "DUNG":
                st.success("🎯 **CHÍNH XÁC! CÔ KHEN EM ĐÃ BẮT TRÚNG VẤN ĐỀ:**")
                st.markdown(f"> *{feedback}*")
                st.markdown(f"- **Vấn đề nghị luận cốt lõi:** *{de_info['vdnl_chuan']}*")
                st.markdown(f"- **Chủ điểm bài học:** *{de_info['topic_tag']}*")
                st.info("👉 Vấn đề cốt lõi đã sáng tỏ! Em hãy bấm chuyển sang **BƯỚC 2: TÌM Ý & LẬP DÀN Ý** để bắt đầu dệt ý.")
            elif status == "LECH":
                st.warning("⚠️ **CHƯA ĐỦ / CÒN LỆCH Ý: EM CẦN ĐIỀU CHỈNH LẠI:**")
                st.markdown(f"> *{feedback}*")
                st.markdown(f"- **Vấn đề nghị luận cốt lõi chuẩn:** *{de_info['vdnl_chuan']}*")
                st.markdown(f"- **Chủ điểm bài học:** *{de_info['topic_tag']}*")
                st.error("👉 **Lời khuyên sư phạm:** Hãy điều chỉnh lại câu trả lời ở trên cho trúng vế trước khi chuyển sang Bước 2, tránh việc bài viết bị lệch trọng tâm!")
            else:
                st.error("❌ **CHƯA ĐÚNG / CÓ DẤU HIỆU LẠC ĐỀ:**")
                st.markdown(f"> *{feedback}*")
                st.markdown(f"- **Vấn đề nghị luận thực sự của đề bài là:** *{de_info['vdnl_chuan']}*")
                st.warning("👉 Em hãy đọc kỹ lại phân tích trên của cô và nhập lại câu trả lời để rèn luyện thói quen đọc đề cẩn thận nhé!")
                
    st.session_state["current_prompt"] = de_info['text']
    st.session_state["current_de_key"] = selected_de_key
    st.session_state["current_de_info"] = de_info

# ==============================================================================
# BƯỚC 2: TÌM Ý & LẬP DÀN Ý
# ==============================================================================
with tabs[1]:
    st.markdown('<span class="step-badge">BƯỚC 2: TÌM Ý & LẬP DÀN Ý</span>', unsafe_allow_html=True)
    st.subheader("Xây Dựng Hệ Thống Luận Điểm, Tra Cứu Dẫn Chứng & Tự Hoàn Thiện Dàn Ý")
    
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_DATA[list(DE_BAI_DATA.keys())[0]])
    is_custom = st.session_state.get("is_custom_de", False)
    
    col_left, col_right = st.columns([1.18, 0.82], gap="large")
    
    with col_left:
        st.markdown("#### 🛠️ Các Bước Tư Duy & Tìm Ý")
        
        with st.expander("📌 Thao tác 1: Làm rõ bản chất vấn đề nghị luận", expanded=True):
            st.markdown("*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*")
            for item in cur_de_info.get("explain_core", []):
                st.markdown(f"- {item}")
            st.markdown(f"👉 **Chốt lại Vấn đề nghị luận (VĐNL):** *{cur_de_info['vdnl_chuan']}*")
                
        with st.expander("💡 Thao tác 2: Bàn luận & Làm sáng tỏ vấn đề", expanded=True):
            st.markdown("*Gợi ý 3 trục câu hỏi bản chất sát với đề bài (Em hãy tham khảo để phát triển ý):*")
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**{q['cau_hoi']}**")
                for item in q.get("y_tra_loi", []):
                    st.markdown(f"- {item}")
                st.write("")
                
        with st.expander("🔄 Thao tác 3: Mở rộng vấn đề (Phản biện đa chiều)", expanded=False):
            st.markdown("*Gợi ý hướng lật lại vấn đề để bài viết có chiều sâu:*")
            for c in cur_de_info.get("counter", []):
                st.markdown(f"- {c}")
                
        with st.expander("📚 Thao tác 4: Kho dẫn chứng chọn lọc (8 nhóm chủ điểm)", expanded=False):
            selected_topic = st.selectbox("Chọn chủ điểm dẫn chứng cần tra cứu:", list(KHO_DAN_CHUNG.keys()))
            for dc in KHO_DAN_CHUNG[selected_topic]:
                st.markdown(f"""
                <div class="step-card">
                    <strong style="color:#1a73e8; font-size:1.05rem;">👤 {dc['nv']}</strong><br>
                    <p style="margin:6px 0; color:#334155; line-height:1.5;">{dc['nd']}</p>
                    <span style="font-size:0.85rem; color:#64748b;">📰 <em>Nguồn kiểm chứng: {dc['nguon']}</em></span>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("#### 📝 Khung Lập Dàn Ý Hoàn Chỉnh (Học sinh tự điền nội dung)")
        default_outline = f"""I. MỞ BÀI:
- Ý định dẫn dắt của em:
- Vấn đề nghị luận cần nêu: {cur_de_info['vdnl_chuan']}

II. THÂN BÀI:
1. Giải thích bản chất vấn đề:
- Cắt nghĩa từ khóa/mệnh đề cốt lõi:

2. Bàn luận & Làm sáng tỏ:
- Luận điểm 1 (Bản chất/Vì sao?):
- Luận điểm 2 (Ý nghĩa đối với bản thân cá nhân):
- Luận điểm 3 (Tác động tích cực đối với xã hội):
- Dẫn chứng thực tế tiêu biểu em chọn & phân tích bài học:

3. Mở rộng vấn đề (Phản biện đa chiều):
- Phê phán hiện tượng lệch lạc ngược lại:
- Nhìn nhận ranh giới đúng - sai:

III. KẾT BÀI:
- Khẳng định lại giá trị của vấn đề:
- Bài học nhận thức và hành động thiết thực của em:"""

        user_outline = st.text_area(
            "Em hãy điền và hoàn thiện dàn ý 3 phần của mình trước khi chuyển sang viết bài:",
            value=st.session_state.get("user_outline") or default_outline,
            height=300
        )
        st.session_state["user_outline"] = user_outline
        
    with col_right:
        st.markdown("#### 🤖 Trợ lí Ngữ văn")
        st.caption("*(Hỏi cô khi em cần làm rõ thêm các gợi ý bên trái – Cô không viết hộ bài)*")
        
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": f"Chào em! Cô đã chuẩn bị sẵn khung gợi ý cho đề: '{cur_de_info.get('vdnl_chuan', '')}'. Em đọc khung bên trái thấy băn khoăn ở chỗ nào thì nhắn cô nhé!"}
            ]
            
        chat_container = st.container(height=520)
        with chat_container:
            for message in st.session_state["chat_messages"]:
                avatar = "👩‍🏫" if message["role"] == "assistant" else "🧑‍🎓"
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])
                    
        user_query = st.chat_input("Hỏi cô thêm về cách tìm ý, cách lập luận cho đề này...")
        if user_query:
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            with chat_container:
                with st.chat_message("user", avatar="🧑‍🎓"):
                    st.markdown(user_query)
            
            with st.spinner("Cô đang suy nghĩ định hướng cho em..."):
                muc_do = "Học sinh ôn luyện Nâng cao / HSG" if st.session_state.get("muc_tieu_hoc_tap") == "nang_cao" else "Học sinh ôn luyện Cơ bản"
                context_payload = f"""
Đề bài: {cur_de_info['text']}
VĐNL chuẩn: {cur_de_info['vdnl_chuan']}
Các luận điểm gợi ý: {cur_de_info.get('questions', [])}
Mức độ yêu cầu: {muc_do}
"""
                ai_reply = call_gemini_tutor(
                    messages_history=st.session_state["chat_messages"],
                    prompt_context=context_payload
                )
            
            st.session_state["chat_messages"].append({"role": "assistant", "content": ai_reply})
            st.rerun()
            
        if st.button("🔄 Làm mới cuộc trò chuyện với cô"):
            refresh_msg = f"Chào em! Cuộc trò chuyện đã được làm mới. Em cần cô giải đáp thêm điểm nào trong khung gợi ý của đề này?"
            st.session_state["chat_messages"] = [{"role": "assistant", "content": refresh_msg}]
            st.rerun()

# ==============================================================================
# BƯỚC 3: VIẾT BÀI
# ==============================================================================
with tabs[2]:
    st.markdown('<span class="step-badge">BƯỚC 3: VIẾT BÀI</span>', unsafe_allow_html=True)
    st.subheader("Xưởng Viết Độc Lập (Dung lượng từ 600 đến 1000 chữ)")
    
    col_t3_left, col_t3_right = st.columns([1.2, 0.8], gap="large")
    
    with col_t3_left:
        st.markdown("##### 📝 Phương thức làm bài của em:")
        phuong_thuc_viet = st.radio(
            "Em muốn làm bài theo hình thức nào?",
            ["💻 Viết trực tiếp trên máy tính", "📸 Viết tay ra giấy & Tải ảnh bài viết lên"],
            index=0,
            horizontal=True
        )
        
        words_count = 0
        if "Viết trực tiếp" in phuong_thuc_viet:
            essay_content = st.text_area(
                "Em hãy tự mình tập trung viết bài văn hoàn chỉnh vào khung dưới đây:",
                value=st.session_state.get("user_essay", ""),
                height=420,
                placeholder="Mở bài: Dẫn dắt và nêu đúng vấn đề...\nThân bài: Làm rõ bản chất -> Bàn luận 3 câu hỏi -> Dẫn chứng xác thực -> Phản biện lật ngược...\nKết bài: Khẳng định ý nghĩa và liên hệ bản thân..."
            )
            st.session_state["user_essay"] = essay_content
            words_count = len(essay_content.strip().split()) if essay_content.strip() else 0
            st.caption(f"📊 **Số lượng từ hiện tại:** {words_count} chữ (Yêu cầu: từ 600 đến 1000 chữ)")
        else:
            st.info("💡 **Hướng dẫn:** Em hãy viết bài ra giấy kiểm tra (độ dài tương đương 600 - 1000 chữ), dùng điện thoại chụp ảnh rõ nét và tải các trang lên đây nhé!")
            uploaded_images = st.file_uploader(
                "📸 Tải ảnh chụp các trang bài viết tay của em lên (hỗ trợ JPG, PNG):",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
            if uploaded_images:
                st.session_state["uploaded_images_count"] = len(uploaded_images)
                st.session_state["uploaded_image_files"] = uploaded_images
                st.success(f"Đã tải lên thành công {len(uploaded_images)} trang ảnh bài làm!")
                img_cols = st.columns(min(len(uploaded_images), 2))
                for idx, img_file in enumerate(uploaded_images):
                    image = Image.open(img_file)
                    with img_cols[idx % 2]:
                        st.image(image, caption=f"Trang {idx + 1}: {img_file.name}", use_container_width=True)
            else:
                st.session_state["uploaded_images_count"] = 0
                st.session_state["uploaded_image_files"] = []
                st.write("*(Chưa có ảnh nào được tải lên)*")

        so_anh = st.session_state.get("uploaded_images_count", 0)
        has_done = bool(words_count > 50 or so_anh > 0)
        status_badge = "🟢 BÀI LÀM ĐÃ SẴN SÀNG ĐỂ CHẤM" if has_done else "🟡 ĐANG TRONG QUÁ TRÌNH VIẾT BÀI"
        
        st.markdown(f"""
        <div class="next-step-card">
            <span style="background:#1a73e8; color:white; font-size:0.8rem; font-weight:700; padding:4px 12px; border-radius:12px; letter-spacing:0.5px;">
                {status_badge}
            </span>
            <h3 style="color:#1e3c72; margin:12px 0 6px 0; font-size:1.35rem; font-weight:800;">
                🎯 BƯỚC TIẾP THEO: CHỈNH SỬA & ĐÁNH GIÁ
            </h3>
            <p style="color:#475569; font-size:1.0rem; margin:0 auto 12px auto; max-width:620px; line-height:1.5;">
                Khi đã hoàn thiện bài viết trực tiếp hoặc tải ảnh bài viết tay lên (dung lượng từ 600 đến 1000 chữ), em hãy <strong>nhấp chuột chọn tab BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ</strong> ở trên thanh menu để Giám khảo AI tiến hành thẩm định và chấm điểm theo Rubric nhé!
            </p>
            <div style="display:inline-block; background:#ffffff; border:1px solid #bfdbfe; border-radius:8px; padding:8px 18px; color:#1a73e8; font-weight:700; font-size:0.95rem;">
                👉 Bấm chọn tab <strong>[🔍 BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ]</strong> ở phía trên đỉnh trang
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    with col_t3_right:
        st.markdown("##### 💡 Đối chiếu Dàn ý tự lập ở Bước 2:")
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:15px; max-height:480px; overflow-y:auto; font-size:0.9rem; line-height:1.5;">
            {st.session_state.get('user_outline', 'Chưa có dàn ý. Hãy sang Bước 2 hoàn thiện dàn ý trước em nhé!').replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ
# ==============================================================================
with tabs[3]:
    st.markdown('<span class="step-badge">BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ</span>', unsafe_allow_html=True)
    st.subheader("Giám Khảo AI Chấm Điểm Theo Rubric 6 Tiêu Chí & Gợi Ý Tự Nâng Cấp")
    
    st.markdown("""
    *Hệ thống đối chiếu trực tiếp bài viết của em với **Đề bài**, **Vấn đề nghị luận** và **Dàn ý** đã lập để đánh giá công tâm theo chuẩn khảo thí GDPT 2018.*
    """)
    
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_DATA[list(DE_BAI_DATA.keys())[0]])
    essay_text = st.session_state.get("user_essay", "").strip()
    image_files = st.session_state.get("uploaded_image_files", [])
    has_submission = bool(essay_text or image_files)
    
    col_cham_btn, col_cham_status = st.columns([1.1, 1.9])
    with col_cham_btn:
        start_grading = st.button("📝 Bắt đầu Chấm điểm & Nhận xét bài làm bằng AI", type="primary", use_container_width=True)
        
    if start_grading:
        if not has_submission:
            st.error("⚠️ Em chưa viết bài hoặc chưa tải ảnh bài làm ở Bước 3. Hãy quay lại Bước 3 hoàn thành bài viết trước nhé!")
        elif not st.session_state.get("gemini_api_key", "").strip():
            st.warning("⚠️ Chưa nhận được API Key. Em hãy dán mã Gemini API Key vào cột bên trái (Sidebar) để kích hoạt chức năng chấm nhé!")
        else:
            with st.spinner("Giám khảo AI đang đối chiếu tiêu chí Rubric và thẩm định bài làm của em..."):
                grading_prompt = f"""
Bạn là Giám khảo chấm thi môn Ngữ văn THPT theo định hướng chương trình GDPT 2018.
Hãy chấm điểm và đánh giá bài làm của học sinh theo chuẩn thang Rubric 6 tiêu chí (Thang điểm 10.0).

[NGUYÊN TẮC SƯ PHẠM BẮT BUỘC - TUYỆT ĐỐI KHÔNG LÀM THAY HỌC SINH]
1. Tuyệt đối KHÔNG viết lại bài văn, KHÔNG viết lại đoạn văn mẫu hoàn chỉnh cho học sinh.
2. Ở phần Lời khuyên nâng cấp (Feedforward): Chỉ trích dẫn 1 câu/đoạn văn còn yếu nhất của học sinh, chỉ ra lỗi và ĐẶT CÂU HỎI TƯ DUY hoặc GỢI Ý TỪ KHÓA để học sinh TỰ VIẾT LẠI. Không viết sẵn câu mẫu.
3. Dung lượng yêu cầu là từ 600 đến 1000 chữ. Tuyệt đối không trừ điểm nếu học sinh viết đủ trong khoảng này (miễn lập luận không lan man).

[THÔNG TIN ĐỀ THI]
- Đề bài: {cur_de_info['text']}
- Vấn đề nghị luận cốt lõi: {cur_de_info['vdnl_chuan']}
- Dàn ý học sinh đã lập ở Bước 2:
{st.session_state.get('user_outline', 'Học sinh không ghi dàn ý')}

[THANG ĐIỂM RUBRIC 6 TIÊU CHÍ (PHƯƠNG ÁN B - TỔNG 10 ĐIỂM)]:
1. Cấu trúc bài văn 3 phần [0.5 điểm]: Bố cục Mở - Thân - Kết rõ ràng; Thân bài biết tách đoạn mạch lạc.
2. Xác định vấn đề nghị luận [0.5 điểm]: Nêu đúng và trúng vấn đề cốt lõi ngay từ mở bài, không lệch đề hay lạc đề.
3. Giải thích & Bàn luận vấn đề [4.0 điểm]: Cắt nghĩa từ khóa/bản chất vấn đề (1.0đ); Bàn luận bám sát các câu hỏi Vì sao - Ý nghĩa bản thân - Tác động xã hội có chiều sâu (3.0đ).
4. Dẫn chứng thực tế đời sống [2.0 điểm]: Người thật việc thật xác thực, có phân tích gắn kết với luận điểm (không kể lể sự việc dài dòng).
5. Mở rộng & Phản biện đa chiều [1.5 điểm]: Phê phán lối sống lệch lạc và nhìn nhận ranh giới đúng - sai thấu đáo.
6. Chính tả, Diễn đạt & Sáng tạo [1.5 điểm]: Chuẩn chính tả, ngữ pháp (0.5đ); Văn phong có cảm xúc, lập luận sắc sảo, góc nhìn độc lập (1.0đ).

[ĐỊNH DẠNG ĐẦU RA BẮT BUỘC]:
Xuất ra đúng cấu trúc sau (bắt buộc dùng bảng Markdown ở phần điểm số):

### 📋 BẢNG ĐÁNH GIÁ CHI TIẾT THEO RUBRIC (THANG 10 ĐIỂM)

| STT | Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét của Giám khảo |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **Cấu trúc bài văn 3 phần** | 0.5 | **[Điểm]** | [Nhận xét ngắn gọn 1-2 câu] |
| **2** | **Xác định VĐNL** | 0.5 | **[Điểm]** | [Nhận xét ngắn gọn 1-2 câu] |
| **3** | **Giải thích & Bàn luận** | 4.0 | **[Điểm]** | [Nhận xét ngắn gọn 1-2 câu] |
| **4** | **Dẫn chứng thực tế** | 2.0 | **[Điểm]** | [Nhận xét ngắn gọn 1-2 câu] |
| **5** | **Phản biện đa chiều** | 1.5 | **[Điểm]** | [Nhận xét ngắn gọn 1-2 câu] |
| **6** | **Chính tả, Diễn đạt & Sáng tạo** | 1.5 | **[Điểm]** | [Nhận xét ngắn gọn 1-2 câu] |
| 🏆 | **TỔNG ĐIỂM** | **10.0** | **[Tổng điểm] / 10** | **Mức độ đạt được: [Xuất sắc / Tốt / Khá / Trung bình / Cần cố gắng]** |

---

### 🌟 Ưu điểm nổi bật trong bài viết của em:
- (Ghi nhận cụ thể 2 điểm làm tốt nhất mà học sinh đã tự viết được)

### ⚠️ Những điểm còn hạn chế cần lưu ý:
- (Chỉ rõ 1-2 lỗi lập luận còn non, dẫn chứng thiếu phân tích hoặc đoạn văn còn mỏng ý)

### 💡 Hướng dẫn nâng cấp bài viết (Tự rèn luyện, không làm thay):
- **Câu/đoạn văn cần cải thiện trong bài của em:** "[Trích nguyên văn 1 câu/đoạn văn yếu nhất trong bài học sinh]"
- **Vấn đề tồn tại:** [Chỉ rõ lý do vì sao câu này chưa thuyết phục, diễn đạt còn vụng hoặc thiếu chiều sâu]
- **Câu hỏi gợi mở & Từ khóa định hướng để em tự viết lại:** [Đặt 1-2 câu hỏi gợi ý và đưa ra 2-3 cụm từ khóa định hướng để học sinh TỰ VIẾT LẠI câu đó, TUYỆT ĐỐI KHÔNG VIẾT MẪU HỘ].
"""
                content_payload = [grading_prompt]
                if essay_text:
                    content_payload.append(f"\n[BÀI VĂN HỌC SINH VIẾT TRỰC TIẾP]:\n{essay_text}")
                if image_files:
                    for img_f in image_files:
                        img_f.seek(0)
                        pil_img = Image.open(img_f)
                        content_payload.append(pil_img)
                        
                ai_evaluation = call_gemini_engine(content_payload)
                st.session_state["grading_result"] = ai_evaluation

    if "grading_result" in st.session_state:
        st.markdown("---")
        with st.container(border=True):
            st.markdown(st.session_state['grading_result'])
    else:
        st.info("💡 Khi em đã hoàn tất bài viết hoặc nộp ảnh bài làm ở Bước 3, hãy bấm nút màu xanh phía trên để Giám khảo AI tiến hành thẩm định bài làm nhé!")

# ==============================================================================
# HỒ SƠ BÀI LÀM
# ==============================================================================
with tabs[4]:
    st.markdown('<span class="step-badge">📁 HỒ SƠ BÀI LÀM</span>', unsafe_allow_html=True)
    st.subheader("Hồ Sơ Học Tập & Bản Lưu Bài Làm Của Học Sinh")
    
    student_name = st.text_input("Họ và tên học sinh:", placeholder="Ví dụ: Nguyễn Văn An - Lớp 12A1")
    so_anh = st.session_state.get("uploaded_images_count", 0)
    bai_viet_hien_thi = st.session_state.get('user_essay', '')
    if so_anh > 0:
        bai_viet_hien_thi += f"\n[Học sinh đã nộp đính kèm {so_anh} ảnh bài viết tay trực tiếp trên hệ thống]"
        
    ket_qua_cham = st.session_state.get("grading_result", "Chưa thực hiện chấm điểm ở Bước 4.")
    clean_grading_for_txt = ket_qua_cham.replace("**", "")
    
    report_text = f"""BẢN BÁO CÁO HỌC TẬP - QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NGHỊ LUẬN XÃ HỘI
Học sinh: {student_name}
Mức độ rèn luyện: {st.session_state.get('muc_tieu_hoc_tap', '')}
Đề bài thực hiện: {st.session_state.get('current_de_key', '')}
Vấn đề nghị luận cốt lõi: {st.session_state.get('current_de_info', {}).get('vdnl_chuan', '')}
================================================================================
1. DÀN Ý 3 PHẦN ĐÃ LẬP (BƯỚC 2):
{st.session_state.get('user_outline', '')}

================================================================================
2. BÀI VĂN NGHỊ LUẬN HOÀN CHỈNH (BƯỚC 3):
{bai_viet_hien_thi}

================================================================================
3. KẾT QUẢ ĐÁNH GIÁ & CHẤM ĐIỂM TỰ ĐỘNG THEO RUBRIC (BƯỚC 4):
{clean_grading_for_txt}
“””4
    st.text_area("Xem trước nội dung hồ sơ học tập:", value=report_text, height=280)
    
    st.download_button(
        label="📥 Tải xuống Hồ sơ bài làm (.txt)",
        data=report_text,
        file_name=f"Bai_lam_NLXH_{student_name.replace(' ', '_')}.txt" if student_name.strip() else "Bai_lam_NLXH.txt",
        mime="text/plain"
    )