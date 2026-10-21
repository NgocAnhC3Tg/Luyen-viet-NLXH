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
# 2. DỮ LIỆU ĐỀ THI ĐỘC LẬP CHUẨN MỰC
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01: Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:\n> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*\nTừ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Nơi đất ở & Đất hóa tâm hồn:** 'Nơi đất ở' chỉ không gian địa lý thuần túy; 'Đất hóa tâm hồn' ẩn dụ cho sự gắn kết sâu sắc về tình cảm, nghĩa tình.",
            "**Sống có trách nhiệm & Gắn bó cộng đồng:** Nhận thức rõ bổn phận với tập thể, sẵn sàng cống hiến vì sự phát triển chung."
        ],
        "vdnl_ket_luan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ hôm nay.",
        "questions": [
            {
                "cau_hoi": "Vì sao con người, đặc biệt là thế hệ trẻ, cần phải sống có trách nhiệm và gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "Con người là thực thể xã hội, sự phát triển cá nhân luôn bắt nguồn từ nền tảng vững chắc của tập thể.",
                    "Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, tạo dựng một cộng đồng nhân ái, phát triển bền vững."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
                "chi_tiet": "Sáng lập mô hình kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó khăn tại Điện Biên, Hà Giang.",
                "y_nghia": "Chứng minh trách nhiệm được chuyển hóa thành hành động thực tế thay đổi đời sống cộng đồng.",
                "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn"
            }
        ],
        "counter": ["Phê phán lối sống ích kỷ, thực dụng, 'chỉ biết mình', thờ ơ trước nỗi đau đồng loại."]
    },
    "Đề 02: Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.\nHãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong xã hội hiện đại.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Cơn bão & Cơn bão lòng:** Ẩn dụ cho những biến cố dữ dội, tổn thương và khủng hoảng tinh thần.",
            "**Thấu cảm & Lắng nghe chân thành:** Năng lực đặt mình vào vị trí người khác và thái độ kiên nhẫn, không phán xét để xoa dịu nỗi đau."
        ],
        "vdnl_ket_luan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "questions": [
            {
                "cau_hoi": "Tại sao trong thời đại số, con người lại khao khát sự thấu cảm và lắng nghe?",
                "y_tra_loi": [
                    "Công nghệ tạo ra hiện tượng 'kết nối mạng nhưng mất kết nối thực', làm gia tăng sự cô đơn.",
                    "Lắng nghe là liều thuốc xoa dịu tổn thương tâm lý, giải tỏa áp lực cho người trẻ."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "TS. Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'",
                "chi_tiet": "Sáng lập tổng đài tham vấn tâm lý phi lợi nhuận hỗ trợ tinh thần cho hàng ngàn người trẻ khủng hoảng.",
                "y_nghia": "Không gian an toàn để được lắng nghe có thể cứu rỗi một cuộc đời.",
                "nguon": "Báo Thanh Niên, VTV"
            }
        ],
        "counter": ["Phê phán thói vô cảm, tâm lý phán xét vội vàng, bạo lực ngôn từ trên mạng."]
    },
    "Đề 03: Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Toàn cầu hóa & Mỏ neo:** 'Toàn cầu hóa' là hội nhập quốc tế; 'mỏ neo' là điểm tựa cội nguồn giữ con tàu không bị trôi dạt.",
            "**Bản sắc văn hóa dân tộc:** Toàn bộ giá trị tinh hoa cốt lõi được hun đúc qua lịch sử."
        ],
        "vdnl_ket_luan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "questions": [
            {
                "cau_hoi": "Vì sao bảo tồn bản sắc văn hóa là sứ mệnh sinh tồn của tuổi trẻ?",
                "y_tra_loi": [
                    "Văn hóa là thẻ căn cước định danh dân tộc; mất văn hóa là mất tất cả.",
                    "Giữ gìn bản sắc giúp tự tin hội nhập mà không bị hòa tan."
                ]
            }
        ],
        "evidence": [
            {
                "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
                "chi_tiet": "Lồng ghép chất liệu ca dao, dân ca, nhạc cụ dân tộc vào âm nhạc hiện đại đạt triệu view.",
                "y_nghia": "Cách làm mới di sản giúp văn hóa truyền thống tỏa sáng trong thời đại số.",
                "nguon": "Báo Tuổi Trẻ"
            }
        ],
        "counter": ["Phê phán thái độ sính ngoại mù quáng, coi thường tiếng Việt và truyền thống."]
    }
}

# Tự động tạo dữ liệu chuẩn cho các đề 4 - 15
for idx in range(4, 16):
    ten = f"Đề {idx:02d}: Ý nghĩa của tinh thần tự học và ý chí vượt khó"
    if ten not in DE_BAI_CO_BAN:
        DE_BAI_CO_BAN[ten] = {
            "text": f"Đề bài số {idx}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tinh thần tự học và ý chí vươn lên trong cuộc sống.",
            "vdnl_chuan": "Tầm quan trọng của tinh thần tự học và ý chí vượt khó trong cuộc sống.",
            "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
            "explain_items": [
                "**Tinh thần tự học:** Quá trình chủ động tiếp thu tri thức không cần ai đôn đốc.",
                "**Ý chí vượt khó:** Bản lĩnh kiên cường, không gục ngã trước trở ngại."
            ],
            "vdnl_ket_luan": "Tầm quan trọng của tinh thần tự học và ý chí vươn lên trong đời sống.",
            "questions": [{"cau_hoi": "Vì sao tự học và ý chí là chìa khóa thành công?", "y_tra_loi": ["Giúp con người chủ động kiến tạo tương lai và vượt qua nghịch cảnh."]}],
            "evidence": [{"ten": "Chủ tịch Hồ Chí Minh", "chi_tiet": "Tự học ngoại ngữ và lý luận cách mạng khi bôn ba nước ngoài.", "y_nghia": "Tấm gương sáng ngời về tinh thần tự học.", "nguon": "Lịch sử Đảng"}],
            "counter": ["Phê phán thói thụ động, ỷ lại và sợ hãi thất bại."]
        }

DE_BAI_NANG_CAO = {
    "Đề 16: Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*\nViết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông.",
        "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
        "explain_items": [
            "**Bản sắc riêng & chính kiến:** Cá tính độc đáo, tư duy độc lập và hệ giá trị riêng biệt làm nên phẩm giá cá nhân.",
            "**Áp lực số đông:** Sự lôi kéo, phán xét từ đám đông (đặc biệt trên mạng xã hội) dễ đẩy con người vào lối sống rập khuôn."
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
        "counter": ["Phê phán thói hùa theo phong trào vô thức hoặc biến khác biệt thành ngông cuồng."]
    }
}

for idx in range(17, 31):
    ten = f"Đề {idx:02d}: Tư duy phản biện và bản lĩnh tự chủ thời đại AI"
    if ten not in DE_BAI_NANG_CAO:
        DE_BAI_NANG_CAO[ten] = {
            "text": f"Đề bài chuyên sâu số {idx}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tư duy phản biện và năng lực tự chủ tri thức trong kỷ nguyên số.",
            "vdnl_chuan": "Tầm quan trọng của tư duy phản biện và năng lực tự chủ tri thức trong kỷ nguyên số.",
            "explain_guide": "*Định hướng sư phạm: Cắt nghĩa từ khóa then chốt rồi chốt để trả lời câu hỏi 'Vấn đề này thực chất là gì?'*",
            "explain_items": [
                "**Tư duy phản biện:** Khả năng phân tích, đánh giá thông tin đa chiều.",
                "**Tự chủ tri thức:** Không bị thao túng bởi thông tin rác và thuật toán AI."
            ],
            "vdnl_ket_luan": "Bản lĩnh tự chủ tri thức và tư duy phản biện sắc bén trong bối cảnh bùng nổ công nghệ.",
            "questions": [{"cau_hoi": "Vì sao tư duy phản biện là năng lực sinh tồn thời AI?", "y_tra_loi": ["Giúp con người gạn đục khơi trong giữa biển thông tin thật giả lẫn lộn."]}],
            "evidence": [{"ten": "Cảnh báo lừa đảo Deepfake", "chi_tiet": "Yêu cầu người dùng rèn luyện kỹ năng xác thực nguồn tin.", "y_nghia": "Bản lĩnh phản biện bảo vệ bản thân.", "nguon": "Bộ Công an"}],
            "counter": ["Phê phán thói lười tư duy, tin sái cổ thông tin mạng xã hội."]
        }

# ==============================================================================
# 3. KHO DẪN CHỨNG 8 CHỦ ĐIỂM
# ==============================================================================
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
# 4. KẾT NỐI AI & SỬA TẬN GỐC LỖI ĐỒNG BỘ ĐỀ / LỖI ĐÁNH GIÁ VĐNL
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

# KHỞI TẠO MẶC ĐỊNH BẮT BUỘC LÀ ĐỀ 01
if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(DE_BAI_CO_BAN.keys())[0]

# Hàm chuyển đổi đề thông minh - ĐỒNG BỘ TẬN GỐC CẢ 4 BƯỚC
def on_change_de_selected(new_key, de_dict):
    st.session_state["selected_de_key"] = new_key
    st.session_state["current_de_info"] = de_dict[new_key]
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": f"Chào em! Cô là Trợ lý Ngữ văn. Đề bài em đang chọn là: '{new_key}'. Em cần cô hướng dẫn thêm ở phần nào trong dàn ý?"}
    ]
    st.session_state["user_outline"] = ""
    st.session_state["user_essay"] = ""
    st.session_state["eval_vdnl_result"] = None
    if "grading_result" in st.session_state:
        del st.session_state["grading_result"]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = DE_BAI_CO_BAN[st.session_state["selected_de_key"]]

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

# KHẮC PHỤC TRIỆT ĐỂ LỖI AUTO KHEN ĐÚNG DÙ HỌC SINH TRẢ LỜI SAI
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
        # Kiểm tra nhanh từ khóa cơ bản nếu AI lỗi JSON
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
  "feedback": "Nhận xét sư phạm khách quan (xưng cô - em)",
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
            selected_cb_key = st.selectbox(
                "Chọn đề Cơ bản:", 
                list(DE_BAI_CO_BAN.keys()), 
                key="sb_coban",
                on_change=lambda: on_change_de_selected(st.session_state["sb_coban"], DE_BAI_CO_BAN)
            )
            de_info_cb = DE_BAI_CO_BAN[st.session_state["selected_de_key"] if st.session_state["selected_de_key"] in DE_BAI_CO_BAN else selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài Cơ bản:")
                st.info(de_info_cb['text'].replace("**", ""))
                
    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox(
                "Chọn đề Nâng cao:", 
                list(DE_BAI_NANG_CAO.keys()), 
                key="sb_nangcao",
                on_change=lambda: on_change_de_selected(st.session_state["sb_nangcao"], DE_BAI_NANG_CAO)
            )
            de_info_nc = DE_BAI_NANG_CAO[st.session_state["selected_de_key"] if st.session_state["selected_de_key"] in DE_BAI_NANG_CAO else selected_nc_key]
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
                        "explain_guide": res_custom.get("explain_guide", ""),
                        "explain_items": res_custom.get("explain_items", []),
                        "vdnl_ket_luan": res_custom.get("vdnl_ket_luan", student_custom_vdnl),
                        "questions": res_custom.get("questions", []),
                        "evidence": res_custom.get("evidence", []),
                        "counter": res_custom.get("counter", [])
                    }
                    st.session_state["selected_de_key"] = ten_de_custom
                    st.session_state["current_de_info"] = info_custom
                    st.session_state["eval_vdnl_result"] = {
                        "status": res_custom.get("status", "LECH"),
                        "feedback": res_custom.get("feedback", ""),
                        "suggested_fix": res_custom.get("vdnl_chuan", "")
                    }
                    st.success("✅ Đã đồng bộ sang Bước 2 cho đề bài tự nhập của em! Bấm chuyển sang Bước 2.")

    st.markdown("---")
    if "Đề tự nhập" not in st.session_state.get("selected_de_key", ""):
        student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi của đề đang chọn:", placeholder="Gõ câu trả lời của em ở đây...")
        if st.button("🔍 Đối chiếu Vấn đề Nghị luận với AI", type="primary"):
            if student_vdnl.strip():
                with st.spinner("AI đang thẩm định nghiêm túc..."):
                    de_cur = st.session_state["current_de_info"]
                    res = ai_evaluate_student_vdnl(de_cur['text'], de_cur['vdnl_chuan'], student_vdnl)
                    st.session_state["eval_vdnl_result"] = res
            else:
                st.warning("Em chưa nhập câu trả lời!")

    # PHÂN LOẠI HIỂN THỊ KẾT QUẢ ĐÁNH GIÁ CHÍNH XÁC KHOA HỌC
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
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG (ĐỒNG BỘ NGHÊM NGẶT CẢ 4 BƯỚC)
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state.get("selected_de_key", list(DE_BAI_CO_BAN.keys())[0])
    cur_de_info = st.session_state.get("current_de_info", DE_BAI_CO_BAN[cur_de_key])
    
    st.markdown(f'<div class="section-title">🧵 BƯỚC 2: TÌM Ý & THAM KHẢO CHO: <span style="color:#2563eb;">{cur_de_key}</span></div>', unsafe_allow_html=True)
    
    c_left, c_right = st.columns([1.1, 0.9], gap="large")
    
    with c_left:
        st.markdown("#### 🛠️ Gợi Ý Khung Tư Duy Chuẩn Sư Phạm")
        
        # THAO TÁC 1: ĐÚNG MẪU ĐỊNH HƯỚNG CỦA THẦY/CÔ
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
                
        # THAO TÁC 2: BÀN LUẬN DÀY DẶN ĐA CHIỀU
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Hệ thống ý sâu sắc, đa chiều)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q['cau_hoi']}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  * {ans}")

        # THAO TÁC 3: DẪN CHỨNG CỤ THỂ CHI TIẾT
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
        # TRỢ LÝ NGỮ VĂN HOẠT ĐỘNG MƯỢT MÀ BÁM SÁT ĐỀ DANG CHỌN
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
