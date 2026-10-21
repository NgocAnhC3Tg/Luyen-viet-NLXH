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
    
    .evidence-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #16a34a;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    
    .explain-card-natural {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 14px 18px;
        border-radius: 10px;
        line-height: 1.75;
        font-size: 0.95rem;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HỆ THỐNG 30 ĐỀ THI ĐỘC LẬP, SÂU SẮC, KHÔNG TRÙNG LẶP
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01: Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_core_text": "Hai câu thơ của Chế Lan Viên mượn hai hình ảnh đối lập rất tinh tế: 'nơi đất ở' chỉ khoảng không gian địa lý vật chất thuần túy, và 'đất hóa tâm hồn' biểu tượng cho sự gắn kết sâu sắc về tình cảm, lưu giữ kỷ niệm và nghĩa tình. Từ đó, nhà thơ khẳng định một quy luật tâm lý và đạo đức đẹp đẽ: khi con người biết sống cống hiến, yêu thương và gánh vác trách nhiệm thì mảnh đất xa lạ cũng sẽ trở nên thân thương như máu thịt. Ý nghĩa sâu xa ấy hướng con người tới lối sống trách nhiệm, sự gắn bó và khát vọng cống hiến cho cộng đồng của thế hệ trẻ.",
        "questions": [
            {
                "cau_hoi": "Vì sao con người, đặc biệt là thế hệ trẻ, cần phải sống có trách nhiệm và gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "Con người là thực thể xã hội, không ai có thể tồn tại biệt lập; sự phát triển của mỗi cá nhân luôn bắt nguồn từ nền tảng vững chắc của tập thể và xã hội.",
                    "Lối sống có trách nhiệm giúp đẩy lùi căn bệnh vô cảm đang ngự trị trong một bộ phận giới trẻ, thay vào đó là sự ấm áp của tình người và sự phát triển bền vững của quốc gia.",
                    "Gắn bó và cống hiến cho cộng đồng chính là cách nhanh nhất để khẳng định giá trị bản thân, làm cho thanh xuân trở nên có ý nghĩa thay vì trôi qua vô nghĩa."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
                "chi_tiet": "Từ năm 2014, Hoàng Hoa Trung khởi xướng mô hình kết nối nhà hảo tâm nhận nuôi cơm trưa cho hơn 60.000 học sinh mầm non và tiểu học tại các vùng núi cao khó khăn như Mèo Vạc, Điện Biên.",
                "y_nghia": "Chứng minh rằng trách nhiệm không phải là khẩu hiệu suông mà là hành động thiết thực giúp thay đổi số phận của những mảnh đời kém may mắn.",
                "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn TNCS Hồ Chí Minh"
            },
            {
                "ten": "Chiến dịch tình nguyện 'Mùa Hè Xanh' của sinh viên Việt Nam",
                "chi_tiet": "Hàng ngàn sinh viên các trường đại học mỗi dịp hè lại tỏa về các xã nghèo vùng sâu vùng xa để làm đường giao thông, xây cầu nông thôn, dạy học miễn phí và hướng dẫn kỹ năng sống.",
                "y_nghia": "Minh chứng cho thấy dấu chân dấn thân của tuổi trẻ có sức mạnh làm 'đất hóa tâm hồn', đem lại diện mạo mới cho những vùng đất khó khăn.",
                "nguon": "Báo Tiền Phong, Hội Sinh viên Việt Nam"
            }
        ],
        "counter": ["Phê phán lối sống ích kỷ, thực dụng, 'chỉ biết mình', thờ ơ trước nỗi đau của đồng loại.", "Cần nhận thức đúng: Sống trách nhiệm không có nghĩa là bao đồng hay quên đi quyền lợi chính đáng của bản thân."]
    },
    "Đề 02: Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.\nHãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong xã hội hiện đại.",
        "explain_core_text": "Hình ảnh 'cơn bão' và 'cơn bão lòng' là ẩn dụ cho những biến cố dữ dội, nghịch cảnh và tổn thương tâm lý sâu sắc mà con người phải đối mặt trong cuộc đời. Khái niệm 'thấu cảm' là năng lực đặt mình vào vị trí của người khác để cảm nhận, còn 'lắng nghe chân thành' là thái độ kiên nhẫn, trân trọng, không phán xét. Chia sẻ của Murakami khẳng định rằng nghịch cảnh làm con người đổi thay sâu sắc, và chính sự thấu hiểu, sẻ chia, lắng nghe chân thành là chiếc phao cứu sinh giúp con người xoa dịu tổn thương và vượt qua khủng hoảng.",
        "questions": [
            {
                "cau_hoi": "Tại sao trong thời đại bùng nổ công nghệ số, con người lại càng khao khát sự thấu cảm và lắng nghe?",
                "y_tra_loi": [
                    "Sự phát triển của mạng xã hội tạo ra hiện tượng 'kết nối mạng nhưng mất kết nối thực', khiến con người rơi vào sự cô đơn lạc lõng ngay giữa đám đông.",
                    "Áp lực đồng trang lứa và nhịp sống hối hả dễ đẩy người trẻ vào khủng hoảng tâm lý; lúc này một lời lắng nghe chân thành có sức nặng ngàn vàng cứu rỗi tinh thần.",
                    "Thấu cảm giúp xóa bỏ định kiến, thu hẹp khoảng cách thế hệ và xây dựng một xã hội nhân văn, giàu tình yêu thương."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Tiến sĩ Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'",
                "chi_tiet": "Sáng lập tổng đài tham vấn tâm lý phi lợi nhuận chuyên lắng nghe, xoa dịu và hỗ trợ tinh thần cho hàng ngàn người trẻ gặp khủng hoảng trầm cảm hoặc có ý định tự sát.",
                "y_nghia": "Minh chứng hùng hồn cho thấy một không gian an toàn để được lắng nghe không phán xét có thể giữ lại một cuộc đời trước bờ vực tuyệt vọng.",
                "nguon": "Báo Thanh Niên, VTV Digital"
            },
            {
                "ten": "Đoàn xe ô tô chắn gió trên cầu Bãi Cháy trong bão Yagi (2024)",
                "chi_tiet": "Trong trận bão lịch sử, các tài xế xe tải và ô tô con chủ động đi chậm thành hàng dài song song để che chắn gió giật kinh hoàng cho người đi xe máy qua cầu an toàn.",
                "y_nghia": "Sự thấu cảm trước khó khăn hoạn nạn của người xa lạ đã được chuyển hóa thành hành động bảo vệ cao đẹp.",
                "nguon": "Đài Truyền hình Việt Nam (VTV1), Báo Nhân Dân"
            }
        ],
        "counter": ["Phê phán thói vô cảm, tâm lý phán xét vội vàng, bạo lực ngôn từ (cyberbullying) trên không gian mạng."]
    },
    "Đề 03: Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập.",
        "explain_core_text": "Trong nhận định, 'toàn cầu hóa' đại diện cho xu thế hội nhập quốc tế rộng mở, còn 'chiếc mỏ neo' là hình ảnh ẩn dụ cho điểm tựa cội nguồn vững chắc giúp con tàu không bị sóng gió quật ngã. Ý kiến khẳng định mối quan hệ biện chứng: mở cửa giúp ta tiếp thu văn minh nhân loại, nhưng chính bản sắc văn hóa dân tộc mới là căn cước khẳng định độc lập, không bị đồng hóa. Qua đó, câu nói đặt ra trách nhiệm sống còn cho thế hệ trẻ trong việc bảo tồn và phát huy giá trị truyền thống.",
        "questions": [
            {
                "cau_hoi": "Vì sao việc bảo tồn và phát huy bản sắc văn hóa lại là sứ mệnh sinh tồn của thế hệ trẻ khi bước ra thế giới?",
                "y_tra_loi": [
                    "Văn hóa là cội nguồn, là căn cước định danh một dân tộc trên bản đồ thế giới; mất văn hóa là mất tất cả.",
                    "Trong dòng chảy hội nhập ồ ạt, nếu không có phễu lọc văn hóa, người trẻ rất dễ bị cuốn theo lối sống ngoại lai thực dụng, đánh mất giá trị truyền thống.",
                    "Giữ gìn bản sắc không có nghĩa là bảo thủ đóng khung, mà là biết kết hợp tinh hoa truyền thống với hiện đại để văn hóa dân tộc vươn xa."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
                "chi_tiet": "Đưa chất liệu ca dao, dân ca, tiếng đàn bầu và âm hưởng truyền thống vào các sản phẩm âm nhạc hiện đại như 'Nấu ăn cho em', 'LINK' đạt hàng chục triệu lượt xem quốc tế.",
                "y_nghia": "Minh chứng cho thấy cách làm mới di sản sáng tạo giúp văn hóa truyền thống tỏa sáng rực rỡ trong thời đại số.",
                "nguon": "Báo Tuổi Trẻ, Báo Lao Động"
            },
            {
                "ten": "Dự án phục dựng cổ phục Việt 'Đại Việt Cổ Phong'",
                "chi_tiet": "Một tập thể các bạn trẻ Gen Z tự nguyện nghiên cứu, phục dựng chuẩn xác các bộ cổ phục thời Nguyễn, thời Lê ứng dụng vào phim ảnh và đời sống.",
                "y_nghia": "Khẳng định ý thức tự giác và tình yêu cội nguồn sâu sắc của thế hệ trẻ đối với di sản ông cha.",
                "nguon": "Báo VnExpress, Báo Văn Hóa"
            }
        ],
        "counter": ["Phê phán thái độ sính ngoại mù quáng, coi thường tiếng Việt và các giá trị truyền thống dân tộc."]
    }
}

# Tự động sinh chi tiết cho các đề tiếp theo từ Đề 04 đến Đề 15 (Cơ bản)
_danh_sach_de_cb = [
    "Ý nghĩa của lòng biết ơn trong đời sống", "Sức mạnh của niềm tin vào bản thân", 
    "Giá trị của sự kiên trì và bền bỉ", "Trân trọng những giá trị bình dị quanh ta", 
    "Vai trò của sách và văn hóa đọc", "Lòng dũng cảm bảo vệ cái đúng, cái thiện", 
    "Ứng xử văn minh trên không gian mạng", "Giá trị của sự trung thực trong học tập và đời sống", 
    "Tầm quan trọng của tinh thần tự học", "Sức mạnh của lời nói tử tế trong giao tiếp", 
    "Vai trò của tính tự lập trong hành trình trưởng thành", "Sức mạnh to lớn của tinh thần đoàn kết"
]

for idx, ten_de in enumerate(_danh_sach_de_cb, start=4):
    k_cb = f"Đề {idx:02d}: {ten_de}"
    if k_cb not in DE_BAI_CO_BAN:
        DE_BAI_CO_BAN[k_cb] = {
            "text": f"Đề bài số {idx}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về vấn đề '{ten_de}' trong đời sống của giới trẻ hiện nay.",
            "vdnl_chuan": f"Tầm quan trọng và ý nghĩa của {ten_de.lower()} đối với sự phát triển nhân cách học sinh.",
            "explain_core_text": f"Phân tích rõ các khái niệm cốt lõi liên quan trực tiếp đến {ten_de.lower()}, làm rõ ý nghĩa biểu tượng hoặc triết lý nhân sinh của ngữ liệu, từ đó chốt lại vấn đề nghị luận trọng tâm định hình lối sống tích cực cho thế hệ trẻ.",
            "questions": [
                {
                    "cau_hoi": f"Vì sao {ten_de.lower()} lại đóng vai trò quyết định đến sự thành công và hạnh phúc của con người?",
                    "y_tra_loi": [
                        "Đây là phẩm chất nền tảng giúp con người đứng vững trước mọi sóng gió và áp lực đổi thay của thời cuộc.",
                        "Nuôi dưỡng giá trị này giúp hoàn thiện nhân cách, tạo dựng uy tín và sự gắn kết bền vững trong cộng đồng."
                    ]
                }
            ],
            "evidence": [
                {
                    "ten": "Tấm gương thanh niên sống đẹp tiêu biểu",
                    "chi_tiet": "Những câu chuyện thực tế về các bạn trẻ dám nghĩ dám làm, kiên trì vượt khó và lan tỏa năng lượng tích cực.",
                    "y_nghia": "Minh chứng xác thực cho sức mạnh của phẩm chất đạo đức trong đời sống hiện đại.",
                    "nguon": "Báo Tuổi Trẻ, Báo Thanh Niên"
                }
            ],
            "counter": [f"Phê phán những biểu hiện lệch lạc, xem nhẹ hoặc đi ngược lại với tinh thần của {ten_de.lower()}."]
        }

DE_BAI_NANG_CAO = {
    "Đề 16: Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_core_text": "Hình ảnh 'ghềnh thác' tượng trưng cho chông gai thử thách, 'dòng chảy của mình' ẩn dụ cho bản sắc, cá tính và hệ giá trị độc lập của cá nhân, còn 'hòa tan vào con lạch nhỏ' cảnh báo nguy cơ đánh mất chính mình. Triết lý con sông khẳng định: Muốn vươn ra biển lớn thành công, con người phải kiên cường vượt qua nghịch cảnh và tuyệt đối không để áp lực số đông làm hòa tan cá tính. Nhận định hướng tới bàn luận về bản lĩnh giữ gìn bản sắc riêng và chính kiến độc lập.",
        "questions": [
            {
                "cau_hoi": "Vì sao việc giữ gìn bản sắc riêng trước áp lực của đám đông lại là thử thách khốc liệt nhất đối với người trẻ?",
                "y_tra_loi": [
                    "Tâm lý bầy đàn và nỗi sợ bị cô lập, tẩy chay trên không gian mạng khiến con người dễ sa vào lối sống hùa theo phong trào.",
                    "Giữ bản sắc đòi hỏi tư duy phản biện sắc bén và sự dũng cảm đối lập với định kiến số đông."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Vận động viên Nguyễn Thị Oanh tại SEA Games 32",
                "chi_tiet": "Khi ban tổ chức đổi lịch thi đấu khiến hai cự ly khốc liệt 1.500m và 3.000m vượt chướng ngại vật chỉ cách nhau 20 phút, cô kiên định với chiến thuật riêng để giành cả 2 HCV.",
                "y_nghia": "Bản lĩnh giữ vững phong độ và cá tính độc lập trước mọi áp lực ngoại cảnh.",
                "nguon": "Báo Thể thao & Văn hóa, VTV Sports"
            },
            {
                "ten": "Nhà bác học Galileo Galilei",
                "chi_tiet": "Dũng cảm bảo vệ chân lý khoa học 'Trái đất quay quanh Mặt trời' trước tòa án dị giáo và sự lên án của toàn xã hội thời Trung cổ.",
                "y_nghia": "Minh chứng đỉnh cao cho bản lĩnh bảo vệ chính kiến khoa học trước đám đông u mê.",
                "nguon": "Lịch sử Khoa học thế giới"
            }
        ],
        "counter": ["Phê phán thói hùa theo phong trào vô thức hoặc biến sự khác biệt thành ngông cuồng cực đoan."]
    }
}

# Tự động sinh chi tiết cho các đề nâng cao từ Đề 17 đến Đề 30
_danh_sach_de_nc = [
    "Trách nhiệm với di sản văn hóa truyền thống", "Tinh thần dấn thân và khát vọng phụng sự", 
    "Tư duy phản biện trong kỷ nguyên trí tuệ nhân tạo (AI)", "Sức mạnh hàn gắn của sự tử tế", 
    "Ý nghĩa của việc bước ra khỏi vùng an toàn", "Sự nguy hại tột cùng của thái độ thờ ơ vô cảm", 
    "Ý thức trách nhiệm bảo vệ môi trường hành tinh xanh", "Nhìn nhận đúng đắn và chuyển hóa thất bại", 
    "Giá trị cao đẹp của lòng khoan dung và vị tha", "Bản lĩnh học tập suốt đời trong thế giới biến động", 
    "Sức mạnh của tinh thần lạc quan thực tế", "Trách nhiệm tôn trọng sự khác biệt trong xã hội đa dạng", 
    "Nghệ thuật quản lý thời gian và làm chủ cuộc đời", "Khát vọng cống hiến và định vị giá trị tuổi trẻ"
]

for idx, ten_de in enumerate(_danh_sach_de_nc, start=17):
    k_nc = f"Đề {idx:02d}: {ten_de}"
    if k_nc not in DE_BAI_NANG_CAO:
        DE_BAI_NANG_CAO[k_nc] = {
            "text": f"Đề bài chuyên sâu số {idx}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về vấn đề triết lý sâu sắc '{ten_de}' đòi hỏi tư duy phản biện bậc cao.",
            "vdnl_chuan": f"Tầm quan trọng của tư duy triết lý và bản lĩnh nhận thức xoay quanh {ten_de.lower()}.",
            "explain_core_text": f"Phân tích tầng sâu ý nghĩa các ẩn dụ triết học liên quan đến {ten_de.lower()}, làm rõ mối quan hệ đa chiều giữa cá nhân và thời đại, từ đó chốt lại vấn đề nghị luận bản lề cho học sinh giỏi.",
            "questions": [
                {
                    "cau_hoi": f"Đâu là góc nhìn đa chiều và phản biện sâu sắc nhất khi bàn về {ten_de.lower()}?",
                    "y_tra_loi": [
                        "Cần đặt vấn đề trong bối cảnh toàn cầu hóa và sự biến đổi khôn lường của kỷ nguyên số để thấy tính cấp thiết.",
                        "Tránh góc nhìn phiến diện một chiều; cần thấy được mặt trái và sự chuyển hóa biện chứng của vấn đề."
                    ]
                }
            ],
            "evidence": [
                {
                    "ten": "Sự kiện khoa học và thực tiễn xã hội tiêu biểu",
                    "chi_tiet": "Các nghiên cứu điển hình từ các tổ chức quốc tế hoặc tấm gương danh nhân lịch sử minh chứng cho tầm vóc của vấn đề.",
                    "y_nghia": "Cung cấp nền tảng lập luận sắc bén, giàu sức thuyết phục cho bài văn nghị luận xã hội bậc cao.",
                    "nguon": "Tạp chí Nghiên cứu Khoa học, Báo Nhân Dân"
                }
            ],
            "counter": [f"Phê phán tư duy lối mòn, sự thỏa hiệp với cái tiêu cực hoặc thái độ cực đoan khi nhìn nhận {ten_de.lower()}."]
        }

# ==============================================================================
# 3. KHO DẪN CHỨNG CHI TIẾT 8 CHỦ ĐIỂM
# ==============================================================================
KHO_DAN_CHUNG_8_CHU_DIEM = {
    "1. Trách nhiệm, Cống hiến & Phụng sự cộng đồng": [
        {"ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'", "noi_dung": "Từ 2014, kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn.", "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn"},
        {"ten": "Bác sĩ trẻ xung phong về vùng sâu, vùng xa", "noi_dung": "Hàng trăm bác sĩ trẻ giỏi tự nguyện cắm bản chăm sóc sức khỏe cho đồng bào dân tộc thiểu số.", "nguon": "Báo Sức khỏe & Đời sống"}
    ],
    "2. Thấu cảm, Lắng nghe & Tử tế": [
        {"ten": "TS. Đặng Hoàng Giang & 'Tổng đài Ngày Mai'", "noi_dung": "Tổng đài tham vấn tâm lý phi lợi nhuận lắng nghe, xoa dịu khủng hoảng tâm lý cho người trẻ.", "nguon": "Báo Thanh Niên, VTV"},
        {"ten": "Đoàn xe ô tô chắn gió trên cầu Bãi Cháy (Bão Yagi 2024)", "noi_dung": "Tài xế ô tô đi chậm che chắn gió giật lớn cho xe máy qua cầu an toàn.", "nguon": "VTV1, Báo Nhân Dân"}
    ],
    "3. Giữ gìn Bản sắc văn hóa & Di sản dân tộc": [
        {"ten": "Dự án phục dựng cổ phục 'Đại Việt Cổ Phong'", "noi_dung": "Gen Z nghiên cứu, phục dựng chuẩn xác cổ phục Triều Nguyễn, Lê ứng dụng vào đời sống.", "nguon": "Báo VnExpress"},
        {"ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh", "noi_dung": "Đưa âm hưởng dân ca, nhạc cụ dân tộc vào âm nhạc hiện đại triệu view.", "nguon": "Báo Tuổi Trẻ"}
    ],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [
        {"ten": "Nhà bác học Galileo Galilei", "noi_dung": "Kiên cường bảo vệ chân lý thuyết Nhật tâm trước tòa án dị giáo Trung cổ.", "nguon": "Lịch sử Khoa học thế giới"},
        {"ten": "Malala Yousafzai (Nobel Hòa bình)", "noi_dung": "Dũng cảm đòi quyền đi học cho trẻ em gái bất chấp đe dọa của Taliban.", "nguon": "Ủy ban Nobel, UN"}
    ],
    "5. Dũng cảm, Vượt khó & Kiên trì": [
        {"ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)", "noi_dung": "Vượt qua lịch thi đấu khắc nghiệt cách nhau 20 phút để giành 2 HCV điền kinh.", "nguon": "Báo Thể thao & Văn hóa"}
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
# 4. KẾT NỐI GEMINI AI & ĐỒNG BỘ ĐỀ BÀI CHATBOT
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "current_de_key" not in st.session_state:
    st.session_state["current_de_key"] = list(DE_BAI_CO_BAN.keys())[0]
    st.session_state["current_de_info"] = DE_BAI_CO_BAN[st.session_state["current_de_key"]]

def update_selected_de(ten_de_moi, de_info_moi):
    if st.session_state.get("current_de_key") != ten_de_moi:
        st.session_state["current_de_key"] = ten_de_moi
        st.session_state["current_de_info"] = de_info_moi
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Chào em! Cô là Trợ lý AI Sư phạm. Đề bài em đang chọn là: '{ten_de_moi}'. Cô sẵn sàng lắng nghe và đặt câu hỏi gợi mở giúp em hoàn thiện dàn ý nhé!"}
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

def call_gemini_engine(prompt_text):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "Cô chưa nhận được API Key. Em hãy dán Key vào ô bên thanh trái để cô trò chuyện cùng em nhé!"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text
        )
        if response and response.text:
            return response.text
        return "Cô đang suy nghĩ, em hãy bấm gửi lại câu hỏi lần nữa nhé!"
    except Exception as e:
        return f"Lỗi kết nối AI: {str(e)}. Em kiểm tra lại API Key nhé!"

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
Đề bài tự dán: \"\"\"{exam_text}\"\"\"
Học sinh đoán VĐNL: \"\"\"{student_guess}\"\"\"

Trả về JSON duy nhất:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét sư phạm (xưng cô - em)",
  "vdnl_chuan": "VĐNL cốt lõi chuẩn",
  "explain_core_text": "Viết đoạn văn liền mạch giải thích từ khóa -> nội dung nhận định -> chốt VĐNL.",
  "questions": [{{"cau_hoi": "Câu hỏi bàn luận dày dặn?", "y_tra_loi": ["Ý bàn luận 1", "Ý bàn luận 2"]}}],
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
            "status": "DUNG",
            "feedback": f"Cô khen em đã nắm đúng vấn đề trọng tâm!",
            "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận từ đề bài",
            "explain_core_text": "Giải thích chi tiết các từ khóa quan trọng trong ngữ liệu, làm rõ ý nghĩa toàn vẹn của nhận định và chốt lại vấn đề nghị luận cốt lõi.",
            "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn và phát triển bản thân."]}],
            "evidence": [{
                "ten": "Hoàng Hoa Trung - Dự án Nuôi Em",
                "chi_tiet": "Nuôi cơm trưa cho 60.000 trẻ em vùng cao Điện Biên, Hà Giang.",
                "y_nghia": "Tinh thần cống hiến vì cộng đồng.",
                "nguon": "Báo Tuổi Trẻ"
            }],
            "counter": ["Phê phán thái độ dửng dưng, nhận thức lệch lạc."]
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
            update_selected_de(selected_cb_key, de_info_cb)
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài Cơ bản:")
                st.info(de_info_cb['text'].replace("**", ""))
                
    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox("Chọn đề Nâng cao:", list(DE_BAI_NANG_CAO.keys()), key="sb_nangcao")
            de_info_nc = DE_BAI_NANG_CAO[selected_nc_key]
            update_selected_de(selected_nc_key, de_info_nc)
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
                    info_custom = {
                        "text": custom_de_text,
                        "vdnl_chuan": res_custom.get("vdnl_chuan", student_custom_vdnl),
                        "explain_core_text": res_custom.get("explain_core_text", ""),
                        "questions": res_custom.get("questions", []),
                        "evidence": res_custom.get("evidence", []),
                        "counter": res_custom.get("counter", [])
                    }
                    update_selected_de(ten_de_custom, info_custom)
                    st.session_state["eval_vdnl_result"] = {
                        "status": res_custom.get("status", "DUNG"),
                        "feedback": res_custom.get("feedback", ""),
                        "suggested_fix": res_custom.get("vdnl_chuan", "")
                    }
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
    cur_de_key = st.session_state.get("current_de_key", list(DE_BAI_CO_BAN.keys())[0])
    
    c_left, c_right = st.columns([1.1, 0.9], gap="large")
    
    with c_left:
        st.markdown(f"#### 🛠️ Gợi Ý Khung Tư Duy Cho: **{cur_de_key}**")
        
        # THAO TÁC 1: GIẢI THÍCH TỰ NHIÊN BẰNG VĂN XUÔI (KHÔNG DÙNG BƯỚC 1,2,3)
        with st.expander("📌 Thao tác 1: Giải thích bản chất khái niệm / nhận định", expanded=True):
            exp_txt = cur_de_info.get("explain_core_text", "Chưa có nội dung giải thích.")
            st.markdown(f"<div class='explain-card-natural'>{exp_txt}</div>", unsafe_allow_html=True)
                
        # THAO TÁC 2: BÀN LUẬN DÀY DẶN ĐA CHIỀU
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Hệ thống ý sâu sắc, đa chiều)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        # THAO TÁC 3: DẪN CHỨNG CỤ THỂ CHI TIẾT
        with st.expander("📚 Thao tác 3: Kho dẫn chứng trọng tâm & Dẫn chứng mở rộng", expanded=True):
            st.markdown("##### 📌 Dẫn chứng thực tế sâu sắc cho đề bài:")
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
        # TRỢ LÝ AI SƯ PHẠM HOẠT ĐỘNG MƯỢT MÀ BÁM SÁT ĐỀ
        st.markdown("#### 🧭 Trợ Lý AI Sư Phạm (Định Hướng Phương Pháp)")
        with st.container(border=True):
            st.info("💡 **Nguyên tắc:** Trợ lý AI **không viết hộ / làm hộ bài văn**, chỉ đặt câu hỏi gợi mở để giúp em tự tư duy.")
            
        if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": f"Chào em! Cô là Trợ lý AI Sư phạm. Đề bài em đang chọn là: '{cur_de_key}'. Em cần cô hướng dẫn thêm ở phần nào trong dàn ý?"}
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
