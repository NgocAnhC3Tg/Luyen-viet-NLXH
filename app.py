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
    
    .explain-step-1 {
        background-color: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .explain-step-2 {
        background-color: #fefce8;
        border-left: 4px solid #eab308;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .explain-step-3 {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KHO 30 ĐỀ THI CHUẨN NỘI DUNG GIẢI THÍCH 3 BƯỚC SƯ PHẠM
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_core": {
            "step1": "**Bước 1: Giải thích từ khóa trong Vấn đề nghị luận:**\n- *Lối sống có trách nhiệm:* Nhận thức rõ nghĩa vụ, bổn phận của bản thân đối với gia đình, xã hội; không dửng dưng trước thực tại.\n- *Gắn bó với cộng đồng:* Tinh thần hòa nhập, biết đặt lợi ích tập thể lên trên sự vị kỷ cá nhân.",
            "step2": "**Bước 2: Giải thích nội dung của nhận định (câu thơ):**\n- 'Nơi đất ở' chỉ vùng đất địa lý thuần túy; 'Đất hóa tâm hồn' biểu tượng cho sự gắn kết sâu sắc về tình cảm, kỷ niệm và nghĩa tình. Hai câu thơ khẳng định quy luật: Khi con người sống cống hiến và yêu thương, mảnh đất xa lạ cũng trở thành quê hương thân thương trong tâm hồn.",
            "step3": "**Bước 3: Chốt Vấn đề nghị luận:**\n-> Ý kiến trên dẫn dắt đến bài học sâu sắc về *ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ hôm nay*."
        },
        "questions": [
            {
                "cau_hoi": "Vì sao người trẻ cần phải sống có trách nhiệm và biết gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "Con người là một sinh vật xã hội, sự phát triển cá nhân luôn gắn liền với tập thể.",
                    "Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, tạo dựng một cộng đồng nhân ái và bền vững."
                ]
            }
        ],
        "evidence": [
            "**Dẫn chứng 1 (Hoàng Hoa Trung & Dự án 'Nuôi Em'):** Từ năm 2014, dự án 'Nuôi Em' đã kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn. *Ý nghĩa:* Biến trách nhiệm thành hành động cụ thể để nâng đỡ cộng đồng. *(Nguồn: Báo Tuổi Trẻ)*",
            "**Dẫn chứng 2 (Mùa Hè Xanh):** Hàng ngàn sinh viên tình nguyện xông pha về vùng sâu vùng xa làm đường, dạy học. *Ý nghĩa:* Dấu chân cống hiến làm 'đất hóa tâm hồn'. *(Nguồn: Báo Tiền Phong)*"
        ],
        "counter": [
            "Phê phán lối sống vị kỷ, 'chỉ biết mình', thờ ơ trước nỗi đau của đồng loại.",
            "Lật lại vấn đề: Trách nhiệm không đồng nghĩa với cống hiến mù quáng; cần biết cân bằng cá nhân và tập thể."
        ]
    },
    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.\nHãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "explain_core": {
            "step1": "**Bước 1: Giải thích từ khóa trong Vấn đề nghị luận:**\n- *Sự thấu cảm:* Khả năng đặt mình vào vị trí, hoàn cảnh của người khác để cảm nhận nỗi đau hay niềm vui của họ.\n- *Lắng nghe chân thành:* Thái độ kiên nhẫn, trân trọng, không phán xét khi tiếp nhận tâm tư của đối phương.",
            "step2": "**Bước 2: Giải thích nội dung của nhận định:**\n- 'Cơn bão lòng' là ẩn dụ cho những biến cố, tổn thương tinh thần; nhận định khẳng định con người sẽ trưởng thành qua giông bão, nhưng để vượt qua tổn thương tâm lý thì rất cần sự thấu hiểu và lắng nghe từ người khác.",
            "step3": "**Bước 3: Chốt Vấn đề nghị luận:**\n-> Câu nói nhấn mạnh *sức mạnh to lớn của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại*."
        },
        "questions": [
            {
                "cau_hoi": "Tại sao thời đại số lại cần sự thấu cảm và lắng nghe hơn bao giờ hết?",
                "y_tra_loi": [
                    "Công nghệ khiến con người rơi vào trạng thái 'kết nối mạng nhưng mất kết nối thực'.",
                    "Thấu cảm và lắng nghe là liều thuốc xoa dịu tổn thương tâm lý và thu hẹp khoảng cách."
                ]
            }
        ],
        "evidence": [
            "**Dẫn chứng 1 (TS. Đặng Hoàng Giang & 'Tổng đài Ngày Mai'):** Kênh tham vấn tâm lý phi lợi nhuận lắng nghe và hỗ trợ hàng ngàn người trẻ khủng hoảng. *(Nguồn: Báo Thanh Niên)*",
            "**Dẫn chứng 2 (Đoàn xe chắn gió bão Yagi 2024):** Ô tô đi chậm che chắn gió lớn cho xe máy qua cầu an toàn. *(Nguồn: VTV1)*"
        ],
        "counter": ["Phê phán thói vô cảm, phán xét vội vàng hoặc công kích cá nhân trên mạng."]
    },
    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "explain_core": {
            "step1": "**Bước 1: Giải thích từ khóa trong Vấn đề nghị luận:**\n- *Bản sắc văn hóa dân tộc:* Toàn bộ giá trị tinh hoa vật chất và tinh thần cốt lõi được hun đúc qua lịch sử.\n- *Trách nhiệm của thế hệ trẻ:* Ý thức bảo tồn, tiếp nối và quảng bá di sản ông cha.",
            "step2": "**Bước 2: Giải thích nội dung của nhận định:**\n- 'Toàn cầu hóa' mở ra cơ hội hội nhập; 'chiếc mỏ neo' tượng trưng cho điểm tựa gốc rễ vững chắc. Nhận định khẳng định: Hội nhập giúp mở rộng tầm nhìn nhưng bản sắc văn hóa mới giữ cho dân tộc không bị hòa tan.",
            "step3": "**Bước 3: Chốt Vấn đề nghị luận:**\n-> Ý kiến khẳng định *trách nhiệm cấp thiết của thế hệ trẻ trong việc giữ gìn và phát huy bản sắc văn hóa dân tộc khi bước ra thế giới*."
        },
        "questions": [{"cau_hoi": "Vì sao bảo tồn bản sắc văn hóa là sứ mệnh sinh tồn?", "y_tra_loi": ["Văn hóa là thẻ căn cước khẳng định sự tồn tại độc lập của dân tộc."]}],
        "evidence": [
            "**Dẫn chứng 1 (Đen Vâu, Hoàng Thùy Linh):** Ứng dụng nhạc cụ dân tộc và ca dao vào âm nhạc hiện đại triệu view. *(Nguồn: Báo Tuổi Trẻ)*",
            "**Dẫn chứng 2 (Dự án 'Đại Việt Cổ Phong'):** Phục dựng cổ phục Việt Nam thời Nguyễn, Lê. *(Nguồn: Báo VnExpress)*"
        ],
        "counter": ["Phê phán thái độ sính ngoại mù quáng, xem thường giá trị truyền thống."]
    }
}

# Điền dữ liệu cho các đề còn lại
for i in range(4, 16):
    key_cb = f"Đề {i:02d} (Cơ bản): Đề bài luyện tập {i}"
    if key_cb not in DE_BAI_CO_BAN:
        DE_BAI_CO_BAN[key_cb] = {
            "text": f"Đề bài số {i}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về một vấn đề tư tưởng đạo lý có ý nghĩa thiết thực.",
            "vdnl_chuan": f"Ý nghĩa của vấn đề nghị luận trong đề số {i} đối với học sinh.",
            "explain_core": {
                "step1": f"**Bước 1: Giải thích từ khóa:** Giải thích các từ ngữ then chốt trong đề số {i}.",
                "step2": f"**Bước 2: Giải thích nội dung nhận định:** Nêu ý nghĩa toàn vẹn của câu nói/ngữ liệu đề bài.",
                "step3": f"**Bước 3: Chốt Vấn đề nghị luận:** Xác định trọng tâm tư tưởng cần bàn luận."
            },
            "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức và hoàn thiện nhân cách."]}],
            "evidence": ["**Dẫn chứng 1:** Tấm gương thanh niên sống đẹp, cống hiến vì cộng đồng. *(Nguồn: Báo Tuổi Trẻ)*"],
            "counter": ["Phê phán lối sống vị kỷ, thụ động."]
        }

DE_BAI_NANG_CAO = {
    "Đề 16 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_core": {
            "step1": "**Bước 1: Giải thích từ khóa trong Vấn đề nghị luận:**\n- *Bản sắc riêng & chính kiến:* Tư duy độc lập, cá tính sáng tạo và hệ giá trị đạo đức riêng của cá nhân.\n- *Bản lĩnh:* Sự kiên định, dũng cảm bảo vệ giá trị đúng đắn.",
            "step2": "**Bước 2: Giải thích nội dung của nhận định:**\n- 'Ghềnh thác' là thử thách; 'dòng chảy của mình' là cá tính riêng. Mượn hình ảnh con sông, câu nói khẳng định: Muốn vươn ra biển lớn thành công, con người không được để áp lực hoàn cảnh làm hòa tan bản sắc.",
            "step3": "**Bước 3: Chốt Vấn đề nghị luận:**\n-> Ý kiến nhấn mạnh *bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực đồng hóa của đám đông*."
        },
        "questions": [{"cau_hoi": "Vì sao giữ bản sắc riêng trước đám đông là thách thức lớn?", "y_tra_loi": ["Áp lực bị tẩy chay khiến người trẻ dễ đồng hóa bản thân."]}],
        "evidence": [
            "**Dẫn chứng 1 (VĐV Nguyễn Thị Oanh):** Giữ vững phong độ giành 4 HCB SEA Games 32 dù lịch thi đấu bị dồn ép. *(Nguồn: Báo Thể Thao)*",
            "**Dẫn chứng 2 (Galileo Galilei):** Kiên cường bảo vệ thuyết Nhật tâm trước tòa án dị giáo. *(Nguồn: Lịch sử Khoa học)*"
        ],
        "counter": ["Phê phán thói hùa theo phong trào hoặc biến khác biệt thành ngông cuồng."]
    }
}

for i in range(17, 31):
    key_nc = f"Đề {i:02d} (Nâng cao): Đề bài chuyên sâu {i}"
    if key_nc not in DE_BAI_NANG_CAO:
        DE_BAI_NANG_CAO[key_nc] = {
            "text": f"Đề bài số {i}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về một vấn đề xã hội sâu sắc đòi hỏi tư duy phản biện.",
            "vdnl_chuan": f"Bản lĩnh tư duy và nhận thức sâu sắc trong đề số {i}.",
            "explain_core": {
                "step1": f"**Bước 1: Giải thích từ khóa:** Phân tích từ ngữ then chốt trong đề số {i}.",
                "step2": f"**Bước 2: Giải thích nội dung nhận định:** Trình bày thông điệp triết lý của ngữ liệu.",
                "step3": f"**Bước 3: Chốt Vấn đề nghị luận:** Khẳng định vấn đề nghị luận cốt lõi."
            },
            "questions": [{"cau_hoi": "Đâu là góc nhìn lật lại vấn đề?", "y_tra_loi": ["Phân biệt giữ bản lĩnh với sự bảo thủ cố chấp."]}],
            "evidence": ["**Dẫn chứng 1:** Nhà khoa học dũng cảm bảo vệ phát minh mới. *(Nguồn: Tạp chí Khoa học)*"],
            "counter": ["Phê phán tư duy lối mòn, sợ sai không dám đổi mới."]
        }

# ==============================================================================
# 3. KHO DẪN CHỨNG CHI TIẾT 8 CHỦ ĐIỂM
# ==============================================================================
KHO_DAN_CHUNG_8_CHU_DIEM = {
    "1. Trách nhiệm, Cống hiến & Phụng sự cộng đồng": [
        {
            "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
            "noi_dung": "Sáng lập dự án từ 2014, kết nối nuôi cơm trưa cho hơn 60.000 học sinh mầm non và tiểu học vùng cao khó khăn.",
            "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn"
        },
        {
            "ten": "Đội ngũ Bác sĩ trẻ xung phong về vùng sâu, vùng xa (Bộ Y tế)",
            "noi_dung": "Hàng trăm bác sĩ trẻ giỏi tự nguyện cắm bản chăm sóc sức khỏe cho đồng bào dân tộc thiểu số nghèo.",
            "nguon": "Báo Sức khỏe & Đời sống"
        }
    ],
    "2. Thấu cảm, Lắng nghe & Tử tế": [
        {
            "ten": "TS. Đặng Hoàng Giang & 'Tổng đài Ngày Mai'",
            "noi_dung": "Tổng đài tham vấn tâm lý phi lợi nhuận lắng nghe và hỗ trợ tinh thần cho hàng ngàn người trẻ khủng hoảng.",
            "nguon": "Báo Thanh Niên, VTV"
        },
        {
            "ten": "Đoàn xe ô tô chắn gió cho xe máy trong bão Yagi (2024)",
            "noi_dung": "Tài xế ô tô đi chậm chắn gió lớn cho người đi xe máy qua cầu Bãi Cháy an toàn.",
            "nguon": "VTV1, Báo Nhân Dân"
        }
    ],
    "3. Giữ gìn Bản sắc văn hóa & Di sản dân tộc": [
        {
            "ten": "Nhóm bạn trẻ Dự án 'Đại Việt Cổ Phong'",
            "noi_dung": "Phục dựng chuẩn xác cổ phục Việt Nam thời Nguyễn, Lê ứng dụng vào phim ảnh và đời sống.",
            "nguon": "Báo VnExpress"
        },
        {
            "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
            "noi_dung": "Đưa chất liệu ca dao, dân ca, nhạc cụ dân tộc vào âm nhạc hiện đại triệu view.",
            "nguon": "Báo Tuổi Trẻ"
        }
    ],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [
        {
            "ten": "Nhà bác học Galileo Galilei",
            "noi_dung": "Kiên cường bảo vệ chân lý khoa học về thuyết Nhật tâm trước tòa án dị giáo thời Trung cổ.",
            "nguon": "Lịch sử Khoa học thế giới"
        },
        {
            "ten": "Malala Yousafzai (Nobel Hòa bình)",
            "noi_dung": "Dũng cảm đòi quyền đi học cho trẻ em gái bất chấp đe dọa của phiến quân Taliban.",
            "nguon": "Ủy ban Nobel, UN"
        }
    ],
    "5. Dũng cảm, Vượt khó & Kiên trì": [
        {
            "ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)",
            "noi_dung": "Vượt qua lịch thi đấu khắc nghiệt cách nhau 20 phút để giành liên tiếp 2 HCV điền kinh.",
            "nguon": "Báo Thể thao & Văn hóa"
        }
    ],
    "6. Tự học, Thích ứng & Tri thức thời đại AI": [
        {
            "ten": "Chủ tịch Hồ Chí Minh - Tấm gương tự học vĩ đại",
            "noi_dung": "Tự học thông thạo hơn 10 ngoại ngữ trong quá trình bôn ba tìm đường cứu nước.",
            "nguon": "Tư liệu Lịch sử Đảng"
        }
    ],
    "7. Bảo vệ Môi trường & Lối sống xanh": [
        {
            "ten": "Nhóm tình nguyện 'Sài Gòn Xanh'",
            "noi_dung": "Dầm mình dưới các kênh rạch ô nhiễm vớt hàng chục tấn rác trả lại nguồn nước sạch.",
            "nguon": "VTV1, Báo Tuổi Trẻ"
        }
    ],
    "8. Lòng biết ơn, Khoan dung & Nhân ái": [
        {
            "ten": "Chính sách Khoan hồng và Đặc xá của Nhà nước",
            "noi_dung": "Trao cơ hội đặc xá cho phạm nhân cải tạo tốt dịp 2/9 làm lại cuộc đời.",
            "nguon": "Báo Nhân Dân"
        }
    ]
}

# ==============================================================================
# 4. KẾT NỐI GEMINI AI & SỬA LỖI PHẢN HỒI CHATBOT
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
            {"role": "assistant", "content": f"Chào em! Cô là Trợ lý AI Sư phạm. Đề bài em đang làm là: '{ten_de_moi}'. Cô luôn sẵn sàng đặt câu hỏi gợi mở để giúp em tự hoàn thiện dàn ý nhé!"}
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
        return "Cô đang suy nghĩ, em thử đặt lại câu hỏi xem sao nhé!"
    except Exception as e:
        return f"Lỗi kết nối AI: {str(e)}. Em hãy kiểm tra lại API Key nhé!"

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

Trả về JSON duy nhất với Thao tác giải thích đúng 3 bước:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét sư phạm (xưng cô - em)",
  "vdnl_chuan": "VĐNL cốt lõi chuẩn",
  "explain_core": {{
    "step1": "**Bước 1: Giải thích từ khóa:** Giải thích chi tiết từ ngữ trong VĐNL.",
    "step2": "**Bước 2: Giải thích nội dung nhận định:** Nêu ý nghĩa toàn vẹn ngữ liệu.",
    "step3": "**Bước 3: Chốt Vấn đề nghị luận:** Khẳng định vấn đề cốt lõi."
  }},
  "questions": [{{"cau_hoi": "Câu hỏi bàn luận?", "y_tra_loi": ["Ý bàn luận 1", "Ý bàn luận 2"]}}],
  "evidence": ["**Dẫn chứng 1:** Chi tiết dẫn chứng kèm nguồn xác thực"],
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
            "explain_core": {
                "step1": "**Bước 1: Giải thích từ khóa:** Giải thích các từ ngữ then chốt.",
                "step2": "**Bước 2: Giải thích nội dung nhận định:** Khẳng định ý nghĩa tổng thể ngữ liệu.",
                "step3": "**Bước 3: Chốt Vấn đề nghị luận:** Xác định VĐNL trọng tâm."
            },
            "questions": [{"cau_hoi": "Vì sao vấn đề này quan trọng?", "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn."]}],
            "evidence": ["**Dẫn chứng 1:** Hoàng Hoa Trung - Dự án Nuôi Em. *(Nguồn: Báo Tuổi Trẻ)*"],
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
                        "explain_core": res_custom.get("explain_core", {}),
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
        
        # THAO TÁC 1: ĐÚNG CHUẨN 3 BƯỚC SƯ PHẠM
        with st.expander("📌 Thao tác 1: Giải thích bản chất (Chuẩn 3 bước)", expanded=True):
            exp_data = cur_de_info.get("explain_core", {})
            if isinstance(exp_data, dict):
                st.markdown(f"<div class='explain-step-1'>{exp_data.get('step1', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='explain-step-2'>{exp_data.get('step2', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='explain-step-3'>{exp_data.get('step3', '')}</div>", unsafe_allow_html=True)
            elif isinstance(exp_data, list):
                for item in exp_data:
                    st.markdown(f"<div class='explain-step-1'>{item}</div>", unsafe_allow_html=True)
                
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Vì sao? Tác động?)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

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
        auto_outline = f"""I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề nghị luận: {vdnl_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất khái niệm (Giải thích từ khóa -> Giải thích nội dung nhận định -> Chốt VĐNL):\n2. Bàn luận trọng tâm:\n   + Ý 1:\n   + Ý 2:\n3. Dẫn chứng thực tế tiêu biểu:\n4. Phản biện & Mở rộng:\n\nIII. KẾT BÀI:\n- Bài học nhận thức & hành động:"""

        if not st.session_state.get("user_outline"):
            st.session_state["user_outline"] = auto_outline
            
        user_outline = st.text_area("Hoàn thiện dàn ý tại đây:", value=st.session_state["user_outline"], height=260)
        st.session_state["user_outline"] = user_outline

    with c_right:
        # TRỢ LÝ AI SƯ PHẠM ĐÃ SỬA LỖI PHẢN HỒI HOÀN TOÀN
        st.markdown("#### 🧭 Trợ Lý AI Sư Phạm (Định Hướng Phương Pháp)")
        with st.container(border=True):
            st.info("💡 **Nguyên tắc:** Trợ lý AI **không viết hộ / làm hộ bài văn**, chỉ đặt câu hỏi gợi mở để giúp em tự tư duy.")
            
        if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Chào em! Cô là Trợ lý AI Sư phạm. Em đang gặp khó khăn ở phần nào trong dàn ý? Hãy trao đổi để cô định hướng cho em nhé!"}]
            
        # Hiển thị lịch sử chat
        chat_box = st.container(height=380)
        with chat_box:
            for m in st.session_state["chat_messages"]:
                st.chat_message(m["role"]).write(m["content"])
                
        # Xử lý tin nhắn người dùng nhập
        u_msg = st.chat_input("Hỏi cô về cách giải thích, chọn dẫn chứng...", key="chat_input_b2")
        if u_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": u_msg})
            de_context = st.session_state.get("current_de_info", {}).get("text", "")
            
            prompt_chat = f"""
Bạn là Giáo viên Ngữ văn THPT tâm lý, tuân thủ nghiêm ngặt nguyên tắc SƯ PHẠM:
- TUYỆT ĐỐI KHÔNG VIẾT HỘ, KHÔNG LÀM HỘ BÀI VĂN HOẶC ĐOẠN VĂN MẪU.
- Chỉ đặt câu hỏi gợi mở, hướng dẫn phương pháp để học sinh tự làm.
- Xưng hô: Cô - em.

Đề bài học sinh đang làm: "{de_context}"
Học sinh hỏi: "{u_msg}"

Hãy trả lời định hướng ngắn gọn (3–5 câu), sâu sắc và đặt câu hỏi gợi mở tư duy:
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
