import streamlit as st
import json
import re
import google.generativeai as genai

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
    
    .evidence-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #16a34a;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    
    .explain-box-chuan {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #16a34a;
        padding: 16px 20px;
        border-radius: 10px;
        line-height: 1.7;
        font-size: 0.95rem;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HỆ THỐNG TRỌN VẸN 15 ĐỀ CƠ BẢN (ĐƯỢC BIÊN SOẠN TƯỜNG MINH, SÂU SẮC)
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01: Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Nơi đất ở & Đất hóa tâm hồn:** 'Nơi đất ở' chỉ không gian địa lý vật chất thuần túy; 'Đất hóa tâm hồn' ẩn dụ cho sự gắn kết sâu sắc về tình cảm, nghĩa tình và sự bồi đắp tâm hồn.",
            "**Sống có trách nhiệm & Gắn bó cộng đồng:** Nhận thức rõ bổn phận của cá nhân đối với tập thể, không dửng dưng trước nỗi đau đồng loại mà sẵn sàng dấn thân cống hiến."
        ],
        "vdnl_ket_luan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ hôm nay.",
        "questions": [
            {
                "cau_hoi": "Vì sao con người, đặc biệt là thế hệ trẻ, cần phải sống có trách nhiệm và gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "Con người là thực thể xã hội, không ai có thể tồn tại biệt lập; sự phát triển của mỗi cá nhân luôn bắt nguồn từ nền tảng vững chắc của tập thể.",
                    "Lối sống có trách nhiệm giúp đẩy lùi căn bệnh vô cảm, tạo dựng một cộng đồng nhân ái, kết nối con người bằng tình thương.",
                    "Cống hiến cho cộng đồng chính là con đường ngắn nhất để định vị giá trị bản thân, làm cho thanh xuân trở nên rực rỡ và có ý nghĩa sâu sắc."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
                "chi_tiet": "Sáng lập mô hình kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn tại Điện Biên, Hà Giang.",
                "y_nghia": "Chứng minh trách nhiệm được chuyển hóa thành hành động thực tế thiết thực để thay đổi cuộc sống cộng đồng.",
                "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn TNCS Hồ Chí Minh"
            },
            {
                "ten": "Chiến dịch tình nguyện 'Mùa Hè Xanh'",
                "chi_tiet": "Hàng ngàn sinh viên tình nguyện về các xã nghèo vùng sâu vùng xa làm đường giao thông, xây cầu nông thôn, dạy học miễn phí.",
                "y_nghia": "Minh chứng cho thấy dấu chân cống hiến của tuổi trẻ làm cho 'đất hóa tâm hồn', đem lại diện mạo mới cho vùng khó khăn.",
                "nguon": "Báo Tiền Phong, Hội Sinh viên Việt Nam"
            }
        ],
        "counter": [
            "Phê phán lối sống ích kỷ, thực dụng, 'chỉ biết mình', thờ ơ trước những vấn đề chung của xã hội.",
            "Lật lại vấn đề: Sống có trách nhiệm không đồng nghĩa với cống hiến mù quáng hay bao đồng; cần biết cân bằng giữa chăm sóc bản thân và đóng góp xã hội."
        ]
    },
    "Đề 02: Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.\nHãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Cơn bão & Cơn bão lòng:** Ẩn dụ cho những biến cố dữ dội, tổn thương tâm lý và khủng hoảng tinh thần sâu sắc.",
            "**Thấu cảm & Lắng nghe chân thành:** Năng lực đặt mình vào vị trí người khác và thái độ kiên nhẫn, không phán xét để xoa dịu nỗi đau."
        ],
        "vdnl_ket_luan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "questions": [
            {
                "cau_hoi": "Tại sao trong thời đại số, con người lại khao khát sự thấu cảm và lắng nghe?",
                "y_tra_loi": [
                    "Sự bùng nổ mạng xã hội tạo ra hiện tượng 'kết nối mạng nhưng mất kết nối thực', làm gia tăng sự cô đơn lạc lõng ngay giữa đám đông.",
                    "Áp lực đồng trang lứa và nhịp sống hối hả dễ đẩy người trẻ vào khủng hoảng; một lời lắng nghe chân thành có sức nặng cứu rỗi tinh thần.",
                    "Thấu cảm giúp xóa bỏ định kiến, thu hẹp khoảng cách thế hệ và xây dựng một xã hội nhân văn."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "TS. Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'",
                "chi_tiet": "Sáng lập tổng đài tham vấn tâm lý phi lợi nhuận chuyên lắng nghe, xoa dịu và hỗ trợ tinh thần cho hàng ngàn người trẻ gặp khủng hoảng trầm cảm.",
                "y_nghia": "Minh chứng hùng hồn cho thấy một không gian an toàn để được lắng nghe không phán xét có thể giữ lại một cuộc đời trước bờ vực tuyệt vọng.",
                "nguon": "Báo Thanh Niên, VTV Digital"
            },
            {
                "ten": "Đoàn xe ô tô chắn gió trên cầu Bãi Cháy trong bão Yagi (2024)",
                "chi_tiet": "Trong trận bão lịch sử, các tài xế xe tải và ô tô con chủ động đi chậm thành hàng dài song song để che chắn gió giật kinh hoàng cho người đi xe máy qua cầu an toàn.",
                "y_nghia": "Sự thấu cảm trước hoạn nạn của người xa lạ đã được chuyển hóa thành hành động bảo vệ cao đẹp.",
                "nguon": "Đài Truyền hình Việt Nam (VTV1), Báo Nhân Dân"
            }
        ],
        "counter": [
            "Phê phán thói vô cảm, tâm lý phán xét vội vàng, bạo lực ngôn từ (cyberbullying) trên không gian mạng."
        ]
    },
    "Đề 03: Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Toàn cầu hóa & Mỏ neo:** 'Toàn cầu hóa' là hội nhập quốc tế rộng mở; 'mỏ neo' là điểm tựa cội nguồn vững chắc giữ con tàu không bị trôi dạt.",
            "**Bản sắc văn hóa dân tộc:** Toàn bộ giá trị tinh hoa cốt lõi (tiếng nói, phong tục, đạo lý) được hun đúc qua lịch sử."
        ],
        "vdnl_ket_luan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "questions": [
            {
                "cau_hoi": "Vì sao việc bảo tồn và phát huy bản sắc văn hóa lại là sứ mệnh sinh tồn của tuổi trẻ?",
                "y_tra_loi": [
                    "Văn hóa là cội nguồn, là căn cước định danh dân tộc; mất văn hóa là mất tất cả.",
                    "Trong dòng chảy hội nhập ồ ạt, nếu không có phễu lọc văn hóa, người trẻ rất dễ bị cuốn theo lối sống ngoại lai, đánh mất truyền thống.",
                    "Giữ gìn bản sắc không phải là bảo thủ đóng khung, mà là kết hợp tinh hoa truyền thống với hiện đại để văn hóa vươn xa."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
                "chi_tiet": "Lồng ghép chất liệu ca dao, dân ca, nhạc cụ dân tộc vào âm nhạc hiện đại như 'Nấu ăn cho em', 'LINK' đạt hàng chục triệu lượt xem quốc tế.",
                "y_nghia": "Chứng minh cách làm mới di sản sáng tạo giúp văn hóa truyền thống tỏa sáng rực rỡ trong thời đại số.",
                "nguon": "Báo Tuổi Trẻ, Báo Lao Động"
            },
            {
                "ten": "Dự án phục dựng cổ phục Việt 'Đại Việt Cổ Phong'",
                "chi_tiet": "Một tập thể các bạn trẻ Gen Z tự nguyện nghiên cứu, phục dựng chuẩn xác các bộ cổ phục thời Nguyễn, thời Lê ứng dụng vào đời sống.",
                "y_nghia": "Khẳng định ý thức tự giác và tình yêu cội nguồn sâu sắc của thế hệ trẻ đối với di sản ông cha.",
                "nguon": "Báo VnExpress, Báo Văn Hóa"
            }
        ],
        "counter": [
            "Phê phán thái độ sính ngoại mù quáng, coi thường tiếng Việt và các giá trị truyền thống dân tộc."
        ]
    },
    "Đề 04: Ý nghĩa của lòng biết ơn trong đời sống con người": {
        "text": """Danh ngôn dân gian có câu:\n> *"Uống nước nhớ nguồn, ăn quả nhớ kẻ trồng cây."*\nTừ cội nguồn đạo lý ấy, hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lòng biết ơn trong đời sống con người hôm nay.""",
        "vdnl_chuan": "Ý nghĩa và giá trị đạo đức của lòng biết ơn trong đời sống con người.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Uống nước nhớ nguồn & Ăn quả nhớ kẻ trồng cây:** Hình ảnh ẩn dụ tượng trưng cho việc hưởng thụ thành quả phải nhớ đến công sức của người tạo dựng.",
            "**Lòng biết ơn:** Sự trân trọng, ghi nhớ và đền đáp những ân huệ, công lao của thế hệ đi trước hoặc những người giúp đỡ mình."
        ],
        "vdnl_ket_luan": "Ý nghĩa và giá trị đạo đức cốt lõi của lòng biết ơn trong đời sống con người.",
        "questions": [
            {
                "cau_hoi": "Vì sao lòng biết ơn lại là nền tảng đạo đức bền vững nhất của nhân cách?",
                "y_tra_loi": [
                    "Lòng biết ơn giúp con người kết nối với cội nguồn, nuôi dưỡng lòng trắc ẩn và sự tử tế.",
                    "Biết ơn giúp xã hội gắn kết bằng tình nghĩa, ngăn chặn sự lạnh lùng và tính toán thiệt hơn."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Hoạt động Đền ơn đáp nghĩa nhân ngày Thương binh Liệt sĩ 27/7",
                "chi_tiet": "Hàng năm, toàn xã hội và thế hệ trẻ tổ chức thăm hỏi Mẹ Việt Nam anh hùng, thắp nến tri ân các anh hùng liệt sĩ.",
                "y_nghia": "Truyền thống uống nước nhớ nguồn được thể hiện sinh động bằng hành động thiết thực.",
                "nguon": "Báo Nhân Dân, Cổng thông tin Chính phủ"
            }
        ],
        "counter": [
            "Phê phán thói vô ơn, ăn cháo đá bát, vong ân bội nghĩa, xem công sức người khác là điều hiển nhiên."
        ]
    },
    "Đề 05: Sức mạnh và giá trị của niềm tin vào bản thân": {
        "text": """Có câu nói nổi tiếng: *"Tin rằng bạn có thể làm được là bạn đã đi được nửa đường."* (Theodore Roosevelt)\nHãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của niềm tin vào bản thân trong hành trình vươn tới thành công.""",
        "vdnl_chuan": "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong cuộc sống.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Tin rằng bạn có thể làm được:** Sự tự tin vững chắc vào năng lực, phẩm chất và tiềm năng của chính mình.",
            "**Đã đi được nửa đường:** Khẳng định vai trò bàn đạp, bệ phóng tâm lý quyết định biến ý chí thành hành động."
        ],
        "vdnl_ket_luan": "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong hành trình vươn tới thành công.",
        "questions": [
            {
                "cau_hoi": "Vì sao niềm tin vào bản thân lại là chiếc chìa khóa vạn năng mở cánh cửa thành công?",
                "y_tra_loi": [
                    "Niềm tin giúp con người chiến thắng nỗi sợ thất bại, dám đương đầu với thử thách lớn.",
                    "Khi mất niềm tin, con người sẽ bỏ cuộc ngay trước vạch xuất phát; niềm tin chính là ngọn đuốc soi đường trong nghịch cảnh."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Diễn giả khuyết tật Nick Vujicic",
                "chi_tiet": "Sinh ra không có cả tay lẫn chân, ông đã chiến thắng sự tuyệt vọng, tin vào giá trị bản thân để trở thành diễn giả truyền cảm hứng toàn cầu.",
                "y_nghia": "Minh chứng hùng hồn cho thấy niềm tin vào bản thân có thể chiến thắng mọi giới hạn thể xác.",
                "nguon": "Báo Tuổi Trẻ"
            }
        ],
        "counter": [
            "Phê phán căn bệnh tự ti, nhút nhát, rụt rè hoặc ngược lại là sự ảo tưởng sức mạnh, tự phụ mù quáng."
        ]
    },
    "Đề 06: Giá trị của sự kiên trì và bền bỉ trong cuộc sống": {
        "text": """Ngạn ngữ dân gian có câu: *"Nước chảy đá mòn."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự kiên trì, bền bỉ trong hành trình chinh phục mục tiêu của người trẻ.""",
        "vdnl_chuan": "Giá trị của sự kiên trì, bền bỉ và ý chí vượt qua gian khó để đạt ước mơ.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Nước chảy đá mòn:** Hình ảnh thiên nhiên tượng trưng cho sức mạnh bền bỉ của giọt nước nhỏ tích tụ lâu ngày có thể làm thủng cả đá cứng.",
            "**Kiên trì, bền bỉ:** Phẩm chất đeo bám mục tiêu đến cùng, không nản lòng trước trở ngại."
        ],
        "vdnl_ket_luan": "Giá trị của sự kiên trì, bền bỉ và ý chí vượt qua gian khó trong hành trình chinh phục mục tiêu.",
        "questions": [
            {
                "cau_hoi": "Vì sao thành công thực sự trong đời sống luôn đòi hỏi sự kiên trì và bền bỉ?",
                "y_tra_loi": [
                    "Mọi giá trị lớn lao đều cần thời gian hun đúc; không có thành công đích thực nào đạt được sau một đêm.",
                    "Sự kiên trì giúp rèn luyện bản lĩnh thép, biến sức ép thành động lực hoàn thiện."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Vận động viên Nguyễn Thị Ánh Viên",
                "chi_tiet": "Dậy từ 4 giờ sáng mỗi ngày, bơi lội hàng chục km suốt nhiều năm liền không nghỉ để giành hàng trăm huy chương vàng cho thể thao Việt Nam.",
                "y_nghia": "Minh chứng cho thấy thành tích đỉnh cao chỉ đến từ sự kiên trì luyện tập khổ hạnh.",
                "nguon": "Báo Thể Thao & Văn Hóa"
            }
        ],
        "counter": [
            "Phê phán lối sống cả thèm chóng chán, dễ nản lòng, gặp khó khăn là buông xuôi bỏ cuộc."
        ]
    },
    "Đề 07: Ý nghĩa của việc trân trọng những giá trị bình dị quanh ta": {
        "text": """Có ý kiến cho rằng: *"Hạnh phúc đôi khi không phải là những điều lớn lao, mà ẩn giấu trong những điều bình dị nhất của đời thường."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của việc biết trân trọng những giá trị bình dị xung quanh cuộc sống.""",
        "vdnl_chuan": "Ý nghĩa của việc trân trọng những giá trị bình dị để tìm thấy hạnh phúc đích thực.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Điều lớn lao & Điều bình dị:** 'Điều lớn lao' là sự nghiệp, tiền tài xa vời; 'điều bình dị' là bữa cơm gia đình, nụ cười, thiên nhiên mộc mạc.",
            "**Trân trọng giá trị bình dị:** Thái độ biết ơn, tận hưởng từng khoảnh khắc hiện tại."
        ],
        "vdnl_ket_luan": "Ý nghĩa của việc biết trân trọng những giá trị bình dị để tìm thấy hạnh phúc đích thực trong đời sống.",
        "questions": [
            {
                "cau_hoi": "Vì sao con người hiện đại thường hay đánh mất sự trân trọng đối với những điều bình dị?",
                "y_tra_loi": [
                    "Nhịp sống hối hả và áp lực thành công vật chất ảo khiến con người lao đi tìm kiếm những điều xa vời mà quên mất hiện tại.",
                    "Chỉ khi trải qua mất mát hoặc khủng hoảng, con người mới nhận ra sự bình yên trong những điều nhỏ bé mới là tài sản quý giá nhất."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Trào lưu 'Chữa lành' (Healing) và lối sống tối giản (Minimalism)",
                "chi_tiet": "Giới trẻ ngày nay có xu hướng tìm về thiên nhiên, tự nấu ăn, chăm sóc cây cối để tìm lại sự cân bằng nội tâm.",
                "y_nghia": "Minh chứng cho thấy sự thức tỉnh về việc quay về trân trọng những giá trị bình dị nguyên bản.",
                "nguon": "Báo Dân Trí"
            }
        ],
        "counter": [
            "Phê phán lối sống thực dụng, chạy theo hư vinh ảo tưởng, xem thường những hạnh phúc mộc mạc xung quanh."
        ]
    },
    "Đề 08: Vai trò của sách và văn hóa đọc trong thời đại số": {
        "text": """Maxim Gorky từng khẳng định: *"Sách mở ra trước mắt tôi những chân trời mới."*\nTrong thời đại bùng nổ công nghệ số, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò và giá trị của việc đọc sách.""",
        "vdnl_chuan": "Vai trò, ý nghĩa của sách và văn hóa đọc đối với sự phát triển nhân cách con người.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Chân trời mới:** Biểu tượng của tri thức, tầm nhìn bao la và thế giới tư tưởng rộng lớn.",
            "**Sách & Văn hóa đọc:** Kho tàng lưu giữ tinh hoa nhân loại, công cụ rèn luyện tư duy sâu (deep thinking)."
        ],
        "vdnl_ket_luan": "Vai trò, ý nghĩa của sách và văn hóa đọc đối với sự phát triển nhân cách con người trong thời đại số.",
        "questions": [
            {
                "cau_hoi": "Vì sao trong thời đại Internet bùng nổ, sách giấy và văn hóa đọc vẫn giữ giá trị độc tôn?",
                "y_tra_loi": [
                    "Internet cung cấp thông tin bề mặt nhanh chóng nhưng rời rạc; sách mang lại tri thức có hệ thống và chiều sâu tư duy.",
                    "Đọc sách là quá trình tương tác tĩnh lặng giúp bồi dưỡng tâm hồn, rèn luyện sự tập trung và trí tưởng tượng phong phú."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Đường sách TP.HCM và Hà Nội",
                "chi_tiet": "Thu hút hàng triệu lượt bạn trẻ đến tham quan, đọc sách, mua sắm và giao lưu văn hóa mỗi năm.",
                "y_nghia": "Minh chứng cho sức sống bền bỉ của văn hóa đọc giữa lòng đô thị hiện đại.",
                "nguon": "Sở Thông tin và Truyền thông TP.HCM"
            }
        ],
        "counter": [
            "Phê phán tình trạng lười đọc sách, nghiện mạng xã hội, chỉ chuộng thông tin 'mì ăn liền' nông cạn."
        ]
    },
    "Đề 09: Lòng dũng cảm bảo vệ cái đúng, cái thiện": {
        "text": """Có ý kiến cho rằng: *"Lòng dũng cảm không phải là không sợ hãi, mà là sự chiến thắng nỗi sợ hãi."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải và công lý.""",
        "vdnl_chuan": "Vai trò của lòng dũng cảm trong đấu tranh bảo vệ cái đúng, cái thiện và lẽ công bằng.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Không sợ hãi & Chiến thắng nỗi sợ:** Lòng dũng cảm không phải sự vô cảm trước hiểm nguy, mà là bản lĩnh vượt qua nỗi sợ cá nhân.",
            "**Bảo vệ lẽ phải:** Đứng về phía sự thật, công lý và cái thiện bất chấp áp lực đe dọa."
        ],
        "vdnl_ket_luan": "Vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải, công lý và thúc đẩy xã hội văn minh.",
        "questions": [
            {
                "cau_hoi": "Vì sao sự im lặng trước cái xấu đôi khi còn nguy hiểm hơn cả cái ác?",
                "y_tra_loi": [
                    "Sự im lặng, dĩ hòa vi quý, sợ liên lụy chính là tấm áo giáp dung dưỡng, tiếp tay cho cái ác lộng hành.",
                    "Lòng dũng cảm lên tiếng bảo vệ lẽ phải là thước đo phẩm giá làm người."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Những tấm gương cứu người trong lũ dữ",
                "chi_tiet": "Nhiều người dân bình thường không quản hiểm nguy lao mình vào dòng nước xiết để cứu học sinh, người già mắc kẹt trong mưa bão.",
                "y_nghia": "Lòng dũng cảm xả thân vì đồng loại tỏa sáng rực rỡ trong nghịch cảnh.",
                "nguon": "Báo Công An Nhân Dân"
            }
        ],
        "counter": [
            "Phê phán thái độ hèn nhát, vô cảm, 'thấy việc nghĩa không làm', sợ chuốc họa vào thân."
        ]
    },
    "Đề 10: Ứng xử văn minh trên không gian mạng": {
        "text": """Mạng xã hội giống như con dao hai lưỡi vừa kết nối toàn cầu vừa tiềm ẩn nhiều hệ lụy văn hóa.\nHãy viết bài văn nghị luận (khoảng 600 chữ) bàn về cách ứng xử thông minh và văn minh của người trẻ trên không gian mạng.""",
        "vdnl_chuan": "Cách ứng xử thông minh, làm chủ công nghệ và bản lĩnh văn hóa trên không gian mạng.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Con dao hai lưỡi:** Mạng xã hội vừa mở ra không gian kết nối vô tận vừa chứa đựng tin giả và văn hóa độc hại.",
            "**Ứng xử văn minh:** Tác phong giao tiếp lịch sự, có trách nhiệm pháp lý và đạo đức khi đăng tải, chia sẻ thông tin."
        ],
        "vdnl_ket_luan": "Cách ứng xử thông minh, làm chủ công nghệ và bản lĩnh văn hóa của người trẻ trên không gian mạng.",
        "questions": [
            {
                "cau_hoi": "Vì sao người trẻ dễ sa ngã trở thành 'anh hùng bàn phím' trên không gian mạng?",
                "y_tra_loi": [
                    "Tính ẩn danh của tài khoản ảo tạo ra cảm giác vô trách nhiệm, phóng thích những bức xúc cá nhân.",
                    "Tâm lý đám đông thiếu tư duy phản biện khiến nhiều người hùa theo tấn công người khác."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Bộ Quy tắc ứng xử trên mạng xã hội (Bộ TT&TT)",
                "chi_tiet": "Ban hành nhằm định hướng người dùng hành xử chuẩn mực, tôn trọng pháp luật và đạo đức trực tuyến.",
                "y_nghia": "Khung pháp lý và đạo đức thiết thực xây dựng môi trường mạng lành mạnh.",
                "nguon": "Cổng thông tin Bộ Thông tin và Truyền thông"
            }
        ],
        "counter": [
            "Phê phán hiện tượng miệt thị ngoại hình, lăng mạ, tung tin giả câu view trên mạng xã hội."
        ]
    },
    "Đề 11: Giá trị của sự trung thực trong học tập và đời sống": {
        "text": """Có ý kiến cho rằng: *"Sự thật có thể gây tổn thương trong chốc lát, nhưng dối trá để lại vết sẹo vĩnh viễn."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị và ý nghĩa của phẩm chất trung thực trong học tập và đời sống.""",
        "vdnl_chuan": "Ý nghĩa và giá trị của phẩm chất trung thực đối với sự trưởng thành nhân cách.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Sự thật & Dối trá:** Sự thật đôi khi phũ phàng nhưng chóng qua; dối trá phá hủy lòng tin và để lại vết thương lòng vĩnh viễn.",
            "**Trung thực:** Phẩm chất tôn trọng sự thật, nói và làm đúng với lương tâm."
        ],
        "vdnl_ket_luan": "Ý nghĩa và giá trị của phẩm chất trung thực đối với sự trưởng thành nhân cách con người.",
        "questions": [
            {
                "cau_hoi": "Vì sao bệnh gian lận trong học tập và đời sống lại là mối nguy hại lớn?",
                "y_tra_loi": [
                    "Gian lận làm thui chột năng lực thực chất, tạo ra 'giả học thức, thật bằng cấp', làm xói mòn kỷ cương đạo đức.",
                    "Sự dối trá một khi bị lật tẩy sẽ phá vỡ hoàn toàn uy tín và sự tôn trọng."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Cuộc vận động 'Nói không với tiêu cực trong thi cử'",
                "chi_tiet": "Do Bộ GD&ĐT phát động nhằm siết chặt kỷ luật phòng thi, đề cao giá trị thực chất.",
                "y_nghia": "Khẳng định nền tảng trung thực trong giáo dục là cốt lõi của quốc gia.",
                "nguon": "Bộ Giáo dục và Đào tạo"
            }
        ],
        "counter": [
            "Phê phán thói gian lận thi cử, đạo văn (plagiarism) và bệnh thành tích dối trá."
        ]
    },
    "Đề 12: Tầm quan trọng của tinh thần tự học đối với học sinh": {
        "text": """Chủ tịch Hồ Chí Minh từng căn dặn: *"Học ở trường, học ở sách vở, học lẫn nhau và học nhân dân."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tinh thần tự học đối với học sinh trong thời đại mới.""",
        "vdnl_chuan": "Tầm quan trọng và giá trị của tinh thần tự học đối với sự phát triển của người trẻ.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Học ở nhiều nguồn:** Lời căn dặn của Bác chỉ ra phương pháp học toàn diện (trường lớp, sách, bạn bè, nhân dân).",
            "**Tinh thần tự học:** Quá trình chủ động tìm tòi, tiếp thu tri thức bằng tư duy độc lập."
        ],
        "vdnl_ket_luan": "Tầm quan trọng và giá trị quyết định của tinh thần tự học đối với học sinh.",
        "questions": [
            {
                "cau_hoi": "Vì sao học sinh ngày nay buộc phải trang bị năng lực tự học làm kim chỉ nam?",
                "y_tra_loi": [
                    "Sự bùng nổ tri thức khiến sách giáo khoa chỉ là nền tảng cơ bản; thế giới thay đổi từng ngày đòi hỏi phải học suốt đời.",
                    "Tự học giúp rèn luyện tư duy độc lập, khả năng thích ứng và sự sáng tạo."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Tấm gương tự học của Chủ tịch Hồ Chí Minh",
                "chi_tiet": "Người tự học thông thạo hơn 10 ngoại ngữ và nghiên cứu chính trị khi bôn ba khắp thế giới.",
                "y_nghia": "Biểu tượng vĩ đại về tinh thần tự học suốt đời vì sự nghiệp cứu nước.",
                "nguon": "Tư liệu Lịch sử Đảng Cộng sản Việt Nam"
            }
        ],
        "counter": [
            "Phê phán thói quen ỷ lại, học vẹt, lười suy nghĩ, chờ 'dọn sẵn mâm' kiến thức từ thầy cô."
        ]
    },
    "Đề 13: Sức mạnh của lời nói tử tế trong giao tiếp": {
        "text": """Ca dao dân gian có câu:\n> *"Lời nói không mất tiền mua / Lựa lời mà nói cho vừa lòng nhau."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của lời nói tử tế và văn hóa ứng xử trong đời sống hiện đại.""",
        "vdnl_chuan": "Sức mạnh của lời nói tử tế và tầm quan trọng của văn hóa ứng xử trong giao tiếp.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Không mất tiền mua:** Lời nói là thứ tài sản vô hình ai cũng sở hữu, không tốn tiền mua nhưng giá trị vô giá.",
            "**Lựa lời mà nói:** Nhắc nhở ý thức trách nhiệm chọn lựa ngôn từ lịch sự, tôn trọng người nghe."
        ],
        "vdnl_ket_luan": "Sức mạnh của lời nói tử tế và tầm quan trọng của văn hóa ứng xử trong giao tiếp hiện đại.",
        "questions": [
            {
                "cau_hoi": "Vì sao con người đôi khi dễ thốt ra lời cay độc thay vì sự tử tế?",
                "y_tra_loi": [
                    "Áp lực cuộc sống và cái tôi ích kỷ khiến con người dễ phóng thích sự cáu giận lên người khác.",
                    "Lời nói sắc nhọn có sức sát thương tâm lý sâu sắc; ngược lại lời tử tế là liều thuốc chữa lành."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Mô hình 'Quán ăn 0 đồng' cho người nghèo",
                "chi_tiet": "Nơi người lao động nghèo nhận bữa ăn miễn phí kèm theo những lời chào hỏi, cử chỉ tôn trọng ấm áp.",
                "y_nghia": "Minh chứng cho sức mạnh của lời nói tử tế sưởi ấm những phận đời bất hạnh.",
                "nguon": "Báo Thanh Niên"
            }
        ],
        "counter": [
            "Phê phán thói chửi tục, miệt thị, dùng ngôn từ thô lỗ sát thương tâm lý người khác."
        ]
    },
    "Đề 14: Vai trò của tính tự lập trong hành trình trưởng thành": {
        "text": """Có ý kiến cho rằng: *"Chim non muốn bay cao phải tự vẫy đôi cánh của chính mình."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của tính tự lập đối với bạn trẻ trong hành trình bước vào đời.""",
        "vdnl_chuan": "Vai trò và ý nghĩa của tính tự lập trong hành trình trưởng thành của tuổi trẻ.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Chim non & Đôi cánh chính mình:** Hình ảnh ẩn dụ sinh động về con cái và gia đình; muốn trưởng thành phải tự vươn lên bằng sức mình.",
            "**Tính tự lập:** Khả năng tự chủ trong sinh hoạt, suy nghĩ và quyết định cuộc đời."
        ],
        "vdnl_ket_luan": "Vai trò và ý nghĩa quyết định của tính tự lập trong hành trình trưởng thành của tuổi trẻ.",
        "questions": [
            {
                "cau_hoi": "Vì sao hội chứng ỷ lại vào gia đình lại là nỗi trăn trở lớn của thế hệ trẻ?",
                "y_tra_loi": [
                    "Sự bao bọc quá mức của cha mẹ tước đi cơ hội va vấp, tự chịu trách nhiệm của con cái.",
                    "Tự lập là chiếc vé thông hành duy nhất giúp người trẻ đứng vững trên đôi chân của mình."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Lối sống tự lập của thanh niên các nước phát triển",
                "chi_tiet": "Từ 18 tuổi, thanh niên chủ động đi làm thêm trang trải học phí, tự thuê nhà và tự quyết định tương lai.",
                "y_nghia": "Bài học về tinh thần tự lập giúp trưởng thành vững vàng.",
                "nguon": "Báo Dân Trí"
            }
        ],
        "counter": [
            "Phê phán thói quen 'công tử bột', 'bám váy mẹ', lười biếng, ỷ lại mọi thứ vào cha mẹ."
        ]
    },
    "Đề 15: Sức mạnh to lớn của tinh thần đoàn kết": {
        "text": """Chủ tịch Hồ Chí Minh từng đúc kết chân lý lịch sử:\n> *"Đoàn kết, đoàn kết, đại đoàn kết / Thành công, thành công, đại thành công."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của tinh thần đoàn kết trong việc vượt qua thử thách.""",
        "vdnl_chuan": "Sức mạnh to lớn của tinh thần đoàn kết trong việc tạo nên sức mạnh tập thể.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Đoàn kết & Đại đoàn kết:** Sự gắn kết, đồng lòng, thống nhất ý chí và hành động giữa các cá nhân.",
            "**Thành công & Đại thành công:** Khẳng định quả ngọt tất yếu khi tập thể đồng sức đồng lòng."
        ],
        "vdnl_ket_luan": "Sức mạnh to lớn của tinh thần đoàn kết trong việc vượt qua nghịch cảnh và xây dựng đất nước.",
        "questions": [
            {
                "cau_hoi": "Vì sao đoàn kết luôn là vũ khí tối thượng của dân tộc Việt Nam qua các thời kỳ?",
                "y_tra_loi": [
                    "Lịch sử dựng nước và giữ nước của ta luôn phải đối mặt với thiên tai và ngoại xâm khốc liệt; chỉ đoàn kết mới tạo thành bức tường thành bất bại.",
                    "Đoàn kết nhân đôi sức mạnh, biến điều không thể thành có thể."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Tinh thần chống dịch Covid-19 và cứu trợ bão lũ lịch sử",
                "chi_tiet": "Hàng ngàn chuyến xe cứu trợ, ATM gạo, bếp ăn 0 đồng ra đời từ sự chung tay của toàn xã hội.",
                "y_nghia": "Minh chứng hùng hồn cho sức mạnh đại đoàn kết dân tộc trong hoạn nạn.",
                "nguon": "Báo Nhân Dân"
            }
        ],
        "counter": [
            "Phê phán tư tưởng cục bộ, ích kỷ, chia rẽ bè phái làm suy yếu sức mạnh tập thể."
        ]
    }
}

DE_BAI_NANG_CAO = {
    "Đề 16: Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Bản sắc riêng & chính kiến:** Cá tính độc đáo, tư duy độc lập và hệ giá trị riêng biệt làm nên phẩm giá cá nhân.",
            "**Áp lực số đông:** Sự lôi kéo, phán xét từ đám đông (đặc biệt trên không gian mạng) dễ đẩy con người vào lối sống rập khuôn."
        ],
        "vdnl_ket_luan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông trong thời đại số.",
        "questions": [
            {
                "cau_hoi": "Vì sao việc giữ gìn bản sắc riêng trước áp lực đám đông lại là thử thách khốc liệt?",
                "y_tra_loi": [
                    "Tâm lý bầy đàn và nỗi sợ bị cô lập khiến con người dễ sa vào lối sống hùa theo phong trào.",
                    "Giữ bản sắc đòi hỏi tư duy phản biện sắc bén và sự dũng cảm đối lập với định kiến."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)",
                "chi_tiet": "Bất chấp lịch thi đấu đổi đột ngột cách nhau 20 phút, cô kiên định chiến thuật riêng để giành cả 2 HCV.",
                "y_nghia": "Bản lĩnh giữ vững phong độ và cá tính độc lập trước nghịch cảnh.",
                "nguon": "Báo Thể thao & Văn hóa"
            }
        ],
        "counter": [
            "Phê phán thói hùa theo phong trào vô thức hoặc biến khác biệt thành ngông cuồng."
        ]
    }
}

# Kho dẫn chứng 8 chủ điểm
KHO_DAN_CHUNG_8_CHU_DIEM = {
    "1. Trách nhiệm, Cống hiến & Phụng sự cộng đồng": [
        {"ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'", "noi_dung": "Kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn.", "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn"}
    ],
    "2. Thấu cảm, Lắng nghe & Tử tế": [
        {"ten": "TS. Đặng Hoàng Giang & 'Tổng đài Ngày Mai'", "noi_dung": "Tổng đài tham vấn tâm lý phi lợi nhuận hỗ trợ tinh thần cho người trẻ khủng hoảng.", "nguon": "Báo Thanh Niên, VTV"}
    ],
    "3. Giữ gìn Bản sắc văn hóa & Di sản dân tộc": [
        {"ten": "Dự án phục dựng cổ phục 'Đại Việt Cổ Phong'", "noi_dung": "Gen Z nghiên cứu, phục dựng chuẩn xác cổ phục Triều Nguyễn, Lê ứng dụng vào đời sống.", "nguon": "Báo VnExpress"}
    ],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [
        {"ten": "Nhà bác học Galileo Galilei", "noi_dung": "Kiên cường bảo vệ chân lý thuyết Nhật tâm trước tòa án dị giáo Trung cổ.", "nguon": "Lịch sử Khoa học thế giới"}
    ],
    "5. Dũng cảm, Vượt khó & Kiên trì": [
        {"ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)", "noi_dung": "Vượt qua lịch thi đấu khắc nghiệt cách nhau 20 phút giành 2 HCV điền kinh.", "nguon": "Báo Thể thao & Văn hóa"}
    ],
    "6. Tự học, Thích ứng & Tri thức thời đại AI": [
        {"ten": "Chủ tịch Hồ Chí Minh - Tấm gương tự học vĩ đại", "noi_dung": "Tự học thông thạo hơn 10 ngoại ngữ khi bôn ba tìm đường cứu nước.", "nguon": "Tư liệu Lịch sử Đảng"}
    ],
    "7. Bảo vệ Môi trường & Lối sống xanh": [
        {"ten": "Nhóm tình nguyện 'Sài Gòn Xanh'", "noi_dung": "Dầm mình dưới các kênh rạch ô nhiễm vớt hàng chục tấn rác trả lại nguồn nước sạch.", "nguon": "VTV1, Báo Tuổi Trẻ"}
    ],
    "8. Lòng biết ơn, Khoan dung & Nhân ái": [
        {"ten": "Chính sách Khoan hồng và Đặc xá của Nhà nước", "noi_dung": "Trao cơ hội đặc xá cho phạm nhân cải tạo tốt dịp 2/9 làm lại cuộc đời.", "nguon": "Báo Nhân Dân"}
    ]
}

# ==============================================================================
# 4. QUẢN LÝ SESSION STATE AN TOÀN
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = DE_BAI_CO_BAN[st.session_state["selected_de_key"]]

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Chào em! Cô là Trợ lý Ngữ văn. Em cần cô hướng dẫn thêm ở phần nào trong dàn ý?"}
    ]

with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input(
        "Gemini API Key:",
        type="password",
        value=st.session_state["gemini_api_key"]
    )
    if api_key_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = api_key_input.strip()

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

def call_gemini_engine(prompt_text):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "Cô chưa nhận được API Key. Em hãy dán Key vào ô bên thanh trái để cô trò chuyện cùng em nhé!"

    try:
        genai.configure(api_key=api_key)
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        for m in models_to_try:
            try:
                model = genai.GenerativeModel(m)
                response = model.generate_content(prompt_text)
                if response and response.text:
                    return response.text
            except Exception:
                continue
        return "Cô đang suy nghĩ, em hãy bấm gửi lại câu hỏi lần nữa nhé!"
    except Exception as e:
        return f"Lỗi kết nối AI: {str(e)}. Em kiểm tra lại API Key nhé!"

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giám khảo Ngữ văn THPT cực kỳ nghiêm túc và công bằng.
- Đề bài: "{exam_text}"
- Vấn đề nghị luận chuẩn: "{vdnl_chuan}"
- Câu trả lời của học sinh: "{student_guess}"

Nhiệm vụ: So sánh ngữ nghĩa câu trả lời của học sinh với VĐNL chuẩn.
- Nếu học sinh nêu đúng bản chất trọng tâm -> status: "DUNG"
- Nếu học sinh nêu thiếu ý, còn chung chung hoặc lệch nhẹ -> status: "LECH"
- Nếu học sinh nêu sai hoàn toàn vấn đề -> status: "SAI"

Yêu cầu xuất ra JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Lời nhận xét thẳng thắn, khách quan, sư phạm (xưng cô - em). Chỉ rõ chỗ đúng hoặc chỗ sai lệch.",
  "suggested_fix": "{vdnl_chuan}"
}}
"""
    raw = call_gemini_engine(prompt)
    try:
        clean_raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
        match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
        res_json = json.loads(match.group(0)) if match else json.loads(clean_raw)
        return res_json
    except Exception:
        if len(student_guess.strip()) < 5:
            return {"status": "SAI", "feedback": "Câu trả lời của em quá ngắn và chưa nêu được vấn đề nghị luận cốt lõi.", "suggested_fix": vdnl_chuan}
        return {"status": "LECH", "feedback": "Câu trả lời của em chưa hoàn toàn sát với trọng tâm đề bài. Em xem định hướng chuẩn nhé!", "suggested_fix": vdnl_chuan}

def ai_analyze_custom_exam(exam_text, student_guess):
    prompt = f"""
Bạn là chuyên gia khảo thí Ngữ văn THPT.
Đề bài tự dán: \"\"\"{exam_text}\"\"\"
Học sinh đoán VĐNL: \"\"\"{student_guess}\"\"\"

Trả về JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét sư phạm (xưng cô - em)",
  "vdnl_chuan": "VĐNL cốt lõi chuẩn",
  "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
  "explain_items": ["**Từ khóa 1:** Giải thích ý nghĩa", "**Từ khóa 2:** Giải thích ý nghĩa"],
  "vdnl_ket_luan": "Chốt lại Vấn đề nghị luận chuẩn",
  "questions": [{{"cau_hoi": "Câu hỏi bàn luận?", "y_tra_loi": ["Ý bàn luận 1", "Ý bàn luận 2"]}}],
  "evidence": [{{"ten": "Tên dẫn chứng", "chi_tiet": "Chi tiết sự kiện", "y_nghia": "Ý nghĩa phân tích", "nguon": "Nguồn báo chí"}}],
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
            "status": "LECH",
            "feedback": "Cô nhận thấy em đã cố gắng nhưng cần điều chỉnh để diễn đạt chuẩn xác hơn.",
            "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận từ đề bài",
            "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
            "explain_items": ["**Từ khóa chính:** Giải thích bản chất khái niệm."],
            "vdnl_ket_luan": student_guess if student_guess else "Vấn đề nghị luận trọng tâm.",
            "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn."]}],
            "evidence": [{"ten": "Hoàng Hoa Trung - Dự án Nuôi Em", "chi_tiet": "Nuôi cơm trưa cho 60.000 trẻ em vùng cao.", "y_nghia": "Tinh thần cống hiến.", "nguon": "Báo Tuổi Trẻ"}],
            "counter": ["Phê phán thái độ dửng dưng."]
        }

# ==============================================================================
# 5. GIAO DIỆN CHÍNH & TABS
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
            de_info_cb = DE_BAI_CO_BAN[selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài Cơ bản:")
                st.info(de_info_cb['text'].replace("**", ""))
                
            if st.button("📌 Chọn Đề Cơ Bản Này & Chuyển sang Bước 2", key="btn_chon_cb", type="primary"):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = de_info_cb
                st.session_state["chat_messages"] = [{"role": "assistant", "content": f"Chào em! Cô là Trợ lý Ngữ văn. Đề bài em đang chọn là: '{selected_cb_key}'. Em cần cô hướng dẫn thêm ở phần nào trong dàn ý?"}]
                st.session_state["user_outline"] = ""
                st.session_state["user_essay"] = ""
                st.session_state["eval_vdnl_result"] = None
                if "grading_result" in st.session_state:
                    del st.session_state["grading_result"]
                st.success(f"Đã chọn thành công: {selected_cb_key}! Mời thầy/cô bấm qua tab 'BƯỚC 2' phía trên.")
                
    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox("Chọn đề Nâng cao:", list(DE_BAI_NANG_CAO.keys()), key="sb_nangcao")
            de_info_nc = DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài Nâng cao:")
                st.info(de_info_nc['text'].replace("**", ""))
                
            if st.button("📌 Chọn Đề Nâng Cao Này & Chuyển sang Bước 2", key="btn_chon_nc", type="primary"):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = de_info_nc
                st.session_state["chat_messages"] = [{"role": "assistant", "content": f"Chào em! Cô là Trợ lý Ngữ văn. Đề bài em đang chọn là: '{selected_nc_key}'. Em cần cô hướng dẫn thêm ở phần nào trong dàn ý?"}]
                st.session_state["user_outline"] = ""
                st.session_state["user_essay"] = ""
                st.session_state["eval_vdnl_result"] = None
                if "grading_result" in st.session_state:
                    del st.session_state["grading_result"]
                st.success(f"Đã chọn thành công: {selected_nc_key}! Mời thầy/cô bấm qua tab 'BƯỚC 2' phía trên.")

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
                    info_custom = {
                        "text": custom_de_text,
                        "vdnl_chuan": res_custom.get("vdnl_chuan", student_custom_vdnl),
                        "explain_guide": res_custom.get("explain_guide", ""),
                        "explain_items": res_custom.get("explain_items", []),
                        "vdnl_ket_luan": res_custom.get("vdnl_ket_luan", student_custom_vdnl),
                        "questions": res_custom.get("questions", []),
                        "evidence": res_custom.get("evidence", []),
                        "counter": res_custom.get("counter", [])
                    }
                    st.session_state["selected_de_key"] = ten_de_custom
                    st.session_state["current_de_info"] = info_custom
                    st.session_state["chat_messages"] = [{"role": "assistant", "content": f"Chào em! Cô là Trợ lý Ngữ văn. Đề bài em đang chọn là: '{ten_de_custom}'."}]
                    st.session_state["user_outline"] = ""
                    st.session_state["user_essay"] = ""
                    st.session_state["eval_vdnl_result"] = {
                        "status": res_custom.get("status", "LECH"),
                        "feedback": res_custom.get("feedback", ""),
                        "suggested_fix": res_custom.get("vdnl_chuan", "")
                    }
                    st.success("✅ Đã tạo xong giàn giáo Bước 2 cho đề bài tự nhập! Mời bấm sang tab 'BƯỚC 2'.")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài hiện tại đang chọn:** {cur_active_key}")

    if "Đề tự nhập" not in cur_active_key:
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi của đề đang chọn:", placeholder="Gõ câu trả lời của em ở đây...")
        if st.button("🔍 Đối chiếu Vấn đề Nghị luận với AI", type="primary"):
            if student_vdnl.strip():
                with st.spinner("AI đang thẩm định nghiêm túc..."):
                    res = ai_evaluate_student_vdnl(cur_active_info['text'], cur_active_info['vdnl_chuan'], student_vdnl)
                    st.session_state["eval_vdnl_result"] = res
            else:
                st.warning("Em chưa nhập câu trả lời!")

    if st.session_state.get("eval_vdnl_result"):
        res = st.session_state["eval_vdnl_result"]
        status_code = res.get("status", "LECH")
        if status_code == "DUNG":
            st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}")
        elif status_code == "LECH":
            st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH CHUẨN XÁC HƠN:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:* {res.get('suggested_fix')}")
        else:
            st.error(f"❌ **CHƯA ĐÚNG TRỌNG TÂM:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:* {res.get('suggested_fix')}")

# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]
    
    st.markdown(f'<div class="section-title">🧵 BƯỚC 2: TÌM Ý & THAM KHẢO CHO: <span style="color:#2563eb;">{cur_de_key}</span></div>', unsafe_allow_html=True)
    
    c_left, c_right = st.columns([1.1, 0.9], gap="large")
    
    with c_left:
        st.markdown(f"#### 🛠️ Gợi Ý Khung Tư Duy Chuẩn Sư Phạm")
        
        with st.expander("📌 Thao tác 1: Giải thích bản chất khái niệm / nhận định", expanded=True):
            guide_txt = cur_de_info.get("explain_guide", "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*")
            items = cur_de_info.get("explain_items", [])
            vdnl_kl = cur_de_info.get("vdnl_ket_luan", cur_de_info.get("vdnl_chuan", ""))
            
            items_html = ""
            for itm in items:
                items_html += f"<li style='margin-bottom: 8px;'>{itm}</li>"
                
            st.markdown(f"""
            <div class='explain-box-chuan'>
                <p style='margin:0 0 10px 0; font-style:italic; color:#475569;'>{guide_txt}</p>
                <ul style='margin:0 0 12px 0; padding-left: 20px;'>
                    {items_html}
                </ul>
                <p style='margin:0; font-weight:700; color:#166534;'>
                    👉 Chốt lại Vấn đề nghị luận (VĐNL): <span style='font-weight:normal; font-style:italic;'>{vdnl_kl}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Hệ thống ý sâu sắc, đa chiều)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        with st.expander("📚 Thao tác 3: Kho dẫn chứng trọng tâm & Dẫn chứng mở rộng", expanded=True):
            st.markdown("##### 📌 Dẫn chứng thực tế sâu sắc cho đề bài đang chọn:")
            list_ev = cur_de_info.get("evidence", [])
            for ev in list_ev:
                if isinstance(ev, dict):
                    st.markdown(f"""
                    <div class='evidence-card'>
                        <h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>
                        <p style='margin:0 0 6px 0;'><b>• Chi tiết sự kiện/hành động:</b> {ev.get('chi_tiet', '')}</p>
                        <p style='margin:0 0 6px 0;'><b>• Ý nghĩa phân tích bài viết:</b> {ev.get('y_nghia', '')}</p>
                        <p style='margin:0; font-size:0.85rem; color:#64748b;'>📰 <i>Nguồn kiểm chứng: {ev.get('nguon', '')}</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='evidence-card'>{ev}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### 📚 Tra cứu Kho dẫn chứng mở rộng (8 nhóm chủ điểm):")
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
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn (Định Hướng Phương Pháp)")
        with st.container(border=True):
            st.info("💡 **Nguyên tắc:** Trợ lý Ngữ văn **không viết hộ / làm hộ bài văn**, chỉ đặt câu hỏi gợi mở để giúp em tự tư duy.")
            
        if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": f"Chào em! Cô là Trợ lý Ngữ văn. Đề bài em đang chọn là: '{cur_de_key}'. Em cần cô hướng dẫn thêm ở phần nào trong dàn ý?"}
            ]
            
        chat_box = st.container(height=380)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        u_msg = st.chat_input("Hỏi cô về cách giải thích, chọn dẫn chứng...", key="chat_input_b2")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            
            prompt_chat = f"""
Bạn là Giáo viên Ngữ văn THPT tâm lý, tuân thủ nghiêm ngặt nguyên tắc SƯ PHẠM:
- TUYỆT ĐỐI KHÔNG VIẾT HỘ, KHÔNG LÀM HỘ BÀI VĂN HOẶC ĐOẠN VĂN MẪU.
- Chỉ đặt câu hỏi gợi mở, hướng dẫn phương pháp để học sinh tự làm.
- Xưng hô: Cô - em.

Đề bài học sinh đang chọn làm: "{cur_de_key}"
Nội dung đề bài: "{cur_de_info.get('text', '')}"
Học sinh hỏi: "{u_msg}"

Hãy trả lời định hướng ngắn gọn (3–5 câu), sâu sắc bám sát đúng đề bài này và đặt câu hỏi gợi mở tư duy:
"""
            with st.spinner("Trợ lý Ngữ văn đang suy nghĩ..."):
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
Đề bài: {st.session_state.get('selected_de_key')}
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
    
    current_de = st.session_state.get("selected_de_key", "Chưa chọn đề bài")
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
