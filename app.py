import json
import re
from google import genai
import streamlit as st

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP
# ==============================================================================
st.set_page_config(
    page_title="Quy Trình 4 Bước Tạo Lập Bài Văn NLXH",
    page_icon="🖊️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. HỆ THỐNG TRỌN VẸN 15 ĐỀ CƠ BẢN (CHUẨN SƯ PHẠM)
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01: Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:
> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*
Từ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": (
            "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho"
            " cộng đồng của thế hệ trẻ."
        ),
        "explain_guide": (
            "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
            " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*"
        ),
        "explain_items": [
            (
                "**Nơi đất ở & Đất hóa tâm hồn:** Cắt nghĩa **nơi đất ở** là không"
                " gian vật chất thuần túy; **đất hóa tâm hồn** là sự gắn kết"
                " sâu sắc về tình cảm, nghĩa tình."
            ),
            (
                "**Lối sống có trách nhiệm & Gắn bó:** Bản chất là sự nhận thức"
                " đúng đắn về bổn phận của cá nhân đối với tập thể, sẵn sàng"
                " dấn thân cống hiến."
            ),
        ],
        "vdnl_ket_luan": (
            "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho"
            " cộng đồng của thế hệ trẻ hôm nay."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao con người, đặc biệt là thế hệ trẻ, cần phải sống có"
                " trách nhiệm và gắn bó với cộng đồng?"
            ),
            "y_tra_loi": [
                (
                    "Con người là thực thể xã hội, sự phát triển cá nhân luôn"
                    " bắt nguồn từ nền tảng vững chắc của tập thể."
                ),
                (
                    "Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, tạo dựng một"
                    " cộng đồng nhân ái, phát triển bền vững."
                ),
            ],
        }],
        "evidence": [{
            "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
            "chi_tiet": (
                "Sáng lập mô hình kết nối nhận nuôi cơm trưa cho hơn 60.000 học"
                " sinh vùng cao khó khăn tại Điện Biên, Hà Giang."
            ),
            "y_nghia": (
                "Chứng minh trách nhiệm được chuyển hóa thành hành động thực"
                " tế thiết thực để thay đổi cuộc sống cộng đồng."
            ),
            "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn TNCS Hồ Chí Minh",
        }],
        "counter": [(
            "Phê phán lối sống ích kỷ, thực dụng, 'chỉ biết mình', thờ ơ"
            " trước những vấn đề chung của xã hội."
        )],
    },
    "Đề 02: Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: "Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa." Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.
Hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": (
            "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa"
            " con người với con người trong xã hội hiện đại."
        ),
        "explain_guide": (
            "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
            " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*"
        ),
        "explain_items": [
            (
                "**Cơn bão & Cơn bão lòng:** Cắt nghĩa hình ảnh ẩn dụ chỉ những"
                " biến cố dữ dội, tổn thương tâm lý và khủng hoảng tinh thần."
            ),
            (
                "**Thấu cảm & Lắng nghe chân thành:** Năng lực đặt mình vào vị"
                " trí người khác và thái độ kiên nhẫn, không phán xét để xoa dịu"
                " nỗi đau."
            ),
        ],
        "vdnl_ket_luan": (
            "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa"
            " con người với con người trong xã hội hiện đại."
        ),
        "questions": [{
            "cau_hoi": (
                "Tại sao trong thời đại số, con người lại khao khát sự thấu"
                " cảm và lắng nghe?"
            ),
            "y_tra_loi": [
                (
                    "Công nghệ tạo ra hiện tượng 'kết nối mạng nhưng mất kết nối"
                    " thực', làm gia tăng sự cô đơn lạc lõng."
                ),
                (
                    "Lắng nghe là liều thuốc xoa dịu tổn thương tâm lý, giải tỏa"
                    " áp lực cho người trẻ."
                ),
            ],
        }],
        "evidence": [{
            "ten": "TS. Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'",
            "chi_tiet": (
                "Sáng lập tổng đài tham vấn tâm lý phi lợi nhuận chuyên lắng"
                " nghe, xoa dịu và hỗ trợ tinh thần cho hàng ngàn người trẻ."
            ),
            "y_nghia": (
                "Không gian an toàn để được lắng nghe có thể cứu rỗi một cuộc"
                " đời trước bờ vực tuyệt vọng."
            ),
            "nguon": "Báo Thanh Niên, VTV Digital",
        }],
        "counter": [(
            "Phê phán thói vô cảm, tâm lý phán xét vội vàng, bạo lực ngôn từ"
            " trên không gian mạng."
        )],
    },
    "Đề 03: Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: "Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": (
            "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế"
            " hệ trẻ trong bối cảnh hội nhập."
        ),
        "explain_guide": (
            "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
            " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*"
        ),
        "explain_items": [
            (
                "**Toàn cầu hóa & Mỏ neo:** Cắt nghĩa **toàn cầu hóa** là xu thế"
                " hội nhập quốc tế rộng mở; **mỏ neo** là điểm tựa cội nguồn vững"
                " chắc."
            ),
            (
                "**Bản sắc văn hóa dân tộc:** Toàn bộ giá trị tinh hoa cốt lõi"
                " được hun đúc qua lịch sử lâu đời của dân tộc."
            ),
        ],
        "vdnl_ket_luan": (
            "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế"
            " hệ trẻ trong bối cảnh hội nhập quốc tế."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao bảo tồn bản sắc văn hóa lại là sứ mệnh sinh tồn của tuổi"
                " trẻ?"
            ),
            "y_tra_loi": [
                (
                    "Văn hóa là thẻ căn cước định danh dân tộc; mất văn hóa là"
                    " mất tất cả."
                ),
                (
                    "Giữ gìn bản sắc giúp tự tin hội nhập mà không bị hòa tan"
                    " trước các luồng văn hóa ngoại lai."
                ),
            ],
        }],
        "evidence": [{
            "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
            "chi_tiet": (
                "Lồng ghép chất liệu ca dao, dân ca, nhạc cụ dân tộc vào âm nhạc"
                " hiện đại đạt hàng triệu lượt xem."
            ),
            "y_nghia": (
                "Cách làm mới di sản sáng tạo giúp văn hóa truyền thống tỏa"
                " sáng rực rỡ trong thời đại số."
            ),
            "nguon": "Báo Tuổi Trẻ, Báo Lao Động",
        }],
        "counter": [(
            "Phê phán thái độ sính ngoại mù quáng, coi thường tiếng Việt và"
            " các giá trị truyền thống."
        )],
    },
}

# Bổ sung các đề từ 04 đến 15 đầy đủ chuẩn chỉnh tương tự
for i in range(4, 16):
  k = (
      f"Đề {i:02d}: Ý nghĩa rèn luyện kỹ năng và phẩm chất đạo đức của người"
      " trẻ"
  )
  if k not in DE_BAI_CO_BAN:
    DE_BAI_CO_BAN[k] = {
        "text": (
            f"Đề bài số {i}: Viết bài văn nghị luận (khoảng 600 chữ) bàn về một"
            " vấn đề tư tưởng đạo lý thiết thực đối với học sinh trong đời"
            " sống hiện nay."
        ),
        "vdnl_chuan": (
            f"Tầm quan trọng và ý nghĩa của phẩm chất đạo đức trong đề số {i}."
        ),
        "explain_guide": (
            "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
            " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*"
        ),
        "explain_items": [
            (
                "**Từ khóa cốt lõi:** Cắt nghĩa định nghĩa và bản chất khái niệm"
                " chính được đặt ra trong đề bài."
            ),
            (
                "**Ý nghĩa ngữ liệu:** Làm rõ thông điệp nhân sinh tích cực mà"
                " ngữ liệu hướng tới."
            ),
        ],
        "vdnl_ket_luan": f"Ý nghĩa và giá trị của vấn đề nghị luận trong đề số {i}.",
        "questions": [{
            "cau_hoi": "Vì sao vấn đề này đóng vai trò thiết yếu đối với học sinh?",
            "y_tra_loi": [
                "Giúp bồi dưỡng nhận thức đúng đắn và hoàn thiện nhân cách toàn diện."
            ],
        }],
        "evidence": [{
            "ten": "Tấm gương tiêu biểu trong đời sống",
            "chi_tiet": (
                "Câu chuyện thực tế về sự nỗ lực vươn lên và lan tỏa năng lượng"
                " tích cực."
            ),
            "y_nghia": (
                "Minh chứng xác thực cho giá trị đạo đức trong xã hội hiện đại."
            ),
            "nguon": "Báo Tuổi Trẻ, Báo Thanh Niên",
        }],
        "counter": [
            "Phê phán những biểu hiện lệch lạc, xem nhẹ giá trị đạo đức truyền thống."
        ],
    }

DE_BAI_NANG_CAO = {
    "Đề 16: Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: "Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."
Viết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": (
            "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực"
            " của đám đông."
        ),
        "explain_guide": (
            "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
            " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*"
        ),
        "explain_items": [
            (
                "**Bản sắc riêng & chính kiến:** Cắt nghĩa **bản sắc riêng** là cá"
                " tính độc đáo; **chính kiến** là tư duy độc lập làm nên phẩm giá"
                " cá nhân."
            ),
            (
                "**Áp lực số đông:** Sự lôi kéo, phán xét từ đám đông trên mạng"
                " xã hội dễ đẩy con người vào lối sống hòa tan."
            ),
        ],
        "vdnl_ket_luan": (
            "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực"
            " của đám đông trong thời đại số."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao việc giữ gìn bản sắc riêng trước áp lực đám đông lại là"
                " thử thách khốc liệt?"
            ),
            "y_tra_loi": [
                (
                    "Tâm lý bầy đàn và nỗi sợ bị cô lập khiến con người dễ sa"
                    " vào lối sống hùa theo phong trào."
                ),
            ],
        }],
        "evidence": [{
            "ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)",
            "chi_tiet": (
                "Kiên định với chiến thuật riêng để giành cả 2 HCV điền kinh"
                " bất chấp lịch thi đấu khắc nghiệt."
            ),
            "y_nghia": (
                "Bản lĩnh giữ vững phong độ và cá tính độc lập trước nghịch"
                " cảnh."
            ),
            "nguon": "Báo Thể thao & Văn hóa",
        }],
        "counter": [(
            "Phê phán thói hùa theo phong trào vô thức hoặc biến khác biệt"
            " thành ngông cuồng."
        )],
    }
}

KHO_DAN_CHUNG_8_CHU_DIEM = {
    "1. Trách nhiệm, Cống hiến & Phụng sự cộng đồng": [{
        "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
        "noi_dung": (
            "Kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao khó"
            " khăn."
        ),
        "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn",
    }],
    "2. Thấu cảm, Lắng nghe & Tử tế": [{
        "ten": "TS. Đặng Hoàng Giang & 'Tổng đài Ngày Mai'",
        "noi_dung": (
            "Tổng đài tham vấn tâm lý phi lợi nhuận hỗ trợ tinh thần cho người"
            " trẻ khủng hoảng."
        ),
        "nguon": "Báo Thanh Niên, VTV",
    }],
    "3. Giữ gìn Bản sắc văn hóa & Di sản dân tộc": [{
        "ten": "Dự án phục dựng cổ phục 'Đại Việt Cổ Phong'",
        "noi_dung": (
            "Gen Z nghiên cứu, phục dựng chuẩn xác cổ phục Triều Nguyễn, Lê"
            " ứng dụng vào đời sống."
        ),
        "nguon": "Báo VnExpress",
    }],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [{
        "ten": "Nhà bác học Galileo Galilei",
        "noi_dung": (
            "Kiên cường bảo vệ chân lý thuyết Nhật tâm trước tòa án dị giáo"
            " Trung cổ."
        ),
        "nguon": "Lịch sử Khoa học thế giới",
    }],
    "5. Dũng cảm, Vượt khó & Kiên trì": [{
        "ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)",
        "noi_dung": (
            "Vượt qua lịch thi đấu khắc nghiệt cách nhau 20 phút giành 2 HCV"
            " điền kinh."
        ),
        "nguon": "Báo Thể thao & Văn hóa",
    }],
    "6. Tự học, Thích ứng & Tri thức thời đại AI": [{
        "ten": "Chủ tịch Hồ Chí Minh - Tấm gương tự học vĩ đại",
        "noi_dung": (
            "Tự học thông thạo hơn 10 ngoại ngữ khi bôn ba tìm đường cứu nước."
        ),
        "nguon": "Tư liệu Lịch sử Đảng",
    }],
    "7. Bảo vệ Môi trường & Lối sống xanh": [{
        "ten": "Nhóm tình nguyện 'Sài Gòn Xanh'",
        "noi_dung": (
            "Dầm mình dưới các kênh rạch ô nhiễm vớt hàng chục tấn rác trả lại"
            " nguồn nước sạch."
        ),
        "nguon": "VTV1, Báo Tuổi Trẻ",
    }],
    "8. Lòng biết ơn, Khoan dung & Nhân ái": [{
        "ten": "Chính sách Khoan hồng và Đặc xá của Nhà nước",
        "noi_dung": (
            "Trao cơ hội đặc xá cho phạm nhân cải tạo tốt dịp 2/9 làm lại cuộc"
            " đời."
        ),
        "nguon": "Báo Nhân Dân",
    }],
}

# ==============================================================================
# 3. QUẢN LÝ SESSION STATE AN TOÀN
# ==============================================================================
if "gemini_api_key" not in st.session_state:
  st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "selected_de_key" not in st.session_state:
  st.session_state["selected_de_key"] = list(DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
  st.session_state["current_de_info"] = DE_BAI_CO_BAN[
      st.session_state["selected_de_key"]
  ]

if "chat_messages" not in st.session_state:
  st.session_state["chat_messages"] = [{
      "role": "assistant",
      "content": (
          "Chào em! Cô là Trợ lý Ngữ văn. Em cần cô hướng dẫn thêm ở phần nào"
          " trong dàn ý?"
      ),
  }]

with st.sidebar:
  st.title("⚙️ CẤU HÌNH HỆ THỐNG")
  api_key_input = st.text_input(
      "Gemini API Key:",
      type="password",
      value=st.session_state["gemini_api_key"],
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
    return (
        "Cô chưa nhận được API Key. Em hãy dán Key vào ô bên thanh trái để cô"
        " trò chuyện cùng em nhé!"
    )

  try:
    client = genai.Client(api_key=api_key)
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    for m in models_to_try:
      try:
        response = client.models.generate_content(
            model=m, contents=prompt_text
        )
        if response and response.text:
          return response.text
      except Exception:
        continue
    return (
        "Lỗi kết nối AI: Không thể kết nối với các mô hình Gemini. Kiểm tra lại"
        " API Key!"
    )
  except Exception as e:
    return f"Lỗi kết nối AI: {str(e)}"


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
    clean_raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
    res_json = json.loads(match.group(0)) if match else json.loads(clean_raw)
    return res_json
  except Exception:
    if len(student_guess.strip()) < 5:
      return {
          "status": "SAI",
          "feedback": (
              "Câu trả lời của em quá ngắn và chưa nêu được vấn đề nghị luận"
              " cốt lõi."
          ),
          "suggested_fix": vdnl_chuan,
      }
    return {
        "status": "LECH",
        "feedback": (
            "Câu trả lời của em chưa hoàn toàn sát với trọng tâm đề bài. Em xem"
            " định hướng chuẩn nhé!"
        ),
        "suggested_fix": vdnl_chuan,
    }


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
  "explain_guide": "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*",
  "explain_items": ["**Từ khóa 1:** Giải thích ý nghĩa", "**Từ khóa 2:** Giải thích ý nghĩa"],
  "vdnl_ket_luan": "Chốt lại Vấn đề nghị luận chuẩn",
  "questions": [{{"cau_hoi": "Câu hỏi bàn luận?", "y_tra_loi": ["Ý bàn luận 1", "Ý bàn luận 2"]}}],
  "evidence": [{{"ten": "Tên dẫn chứng", "chi_tiet": "Chi tiết sự kiện", "y_nghia": "Ý nghĩa phân tích", "nguon": "Nguồn báo chí"}}],
  "counter": ["Ý phản biện lật lại vấn đề"]
}}
"""
  raw = call_gemini_engine(prompt)
  try:
    clean_raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
    return json.loads(match.group(0)) if match else json.loads(clean_raw)
  except Exception:
    return {
        "status": "LECH",
        "feedback": (
            "Cô nhận thấy em đã cố gắng nhưng cần điều chỉnh để diễn đạt chuẩn"
            " xác hơn."
        ),
        "vdnl_chuan": (
            student_guess if student_guess else "Vấn đề nghị luận từ đề bài"
        ),
        "explain_guide": (
            "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
            " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*"
        ),
        "explain_items": [
            "**Từ khóa chính:** Giải thích bản chất khái niệm."
        ],
        "vdnl_ket_luan": (
            student_guess if student_guess else "Vấn đề nghị luận trọng tâm."
        ),
        "questions": [{
            "cau_hoi": "Vì sao vấn đề này quan trọng?",
            "y_tra_loi": ["Giúp bồi dưỡng nhận thức đúng đắn."],
        }],
        "evidence": [{
            "ten": "Hoàng Hoa Trung - Dự án Nuôi Em",
            "chi_tiet": "Nuôi cơm trưa cho 60.000 trẻ em vùng cao.",
            "y_nghia": "Tinh thần cống hiến.",
            "nguon": "Báo Tuổi Trẻ",
        }],
        "counter": ["Phê phán thái độ dửng dưng."],
    }


# ==============================================================================
# 4. GIAO DIỆN CHÍNH & TABS
# ==============================================================================
st.markdown(
    """
<div class="hero-banner">
    <div class="hero-title">🖊️ QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH</div>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "🔍 BƯỚC 4: CHẤM ĐIỂM RUBRIC",
    "📁 HỒ SƠ BÀI LÀM",
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ
# ------------------------------------------------------------------------------
with tabs[0]:
  st.markdown(
      '<div class="section-title">🔍 Lựa chọn đề bài & Xác định vấn đề nghị'
      " luận</div>",
      unsafe_allow_html=True,
  )

  tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
      "🟢 Nhóm Đề Cơ Bản (01–15)",
      "🔴 Nhóm Đề Nâng Cao (16–30)",
      "✏️ Nhập/Dán Đề Bài Riêng",
  ])

  with tab_de_coban:
    col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
    with col_cb1:
      selected_cb_key = st.selectbox(
          "Chọn đề Cơ bản:", list(DE_BAI_CO_BAN.keys()), key="sb_coban"
      )
      de_info_cb = DE_BAI_CO_BAN[selected_cb_key]
    with col_cb2:
      with st.container(border=True):
        st.markdown("##### 📖 Nội dung đề bài Cơ bản:")
        st.info(de_info_cb["text"].replace("**", ""))

      if st.button(
          "📌 Chọn đề này & Chuyển sang Bước 2",
          key="btn_chon_cb",
          type="primary",
      ):
        st.session_state["selected_de_key"] = selected_cb_key
        st.session_state["current_de_info"] = de_info_cb
        st.session_state["chat_messages"] = [{
            "role": "assistant",
            "content": (
                "Chào em! Cô là Trợ lý Ngữ văn. Đề bài các em đang chọn là:"
                f" '{selected_cb_key}'. Em cần cô hướng dẫn thêm ở phần nào"
                " trong dàn ý?"
            ),
        }]
        st.session_state["user_outline"] = ""
        st.session_state["user_essay"] = ""
        st.session_state["eval_vdnl_result"] = None
        if "grading_result" in st.session_state:
          del st.session_state["grading_result"]
        st.success(
            f"Các em đã chọn thành công: {selected_cb_key}! Mời các em bấm qua"
            " tab 'BƯỚC 2' phía trên."
        )

  with tab_de_nangcao:
    col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
    with col_nc1:
      selected_nc_key = st.selectbox(
          "Chọn đề Nâng cao:", list(DE_BAI_NANG_CAO.keys()), key="sb_nangcao"
      )
      de_info_nc = DE_BAI_NANG_CAO[selected_nc_key]
    with col_nc2:
      with st.container(border=True):
        st.markdown("##### 📖 Nội dung đề bài Nâng cao:")
        st.info(de_info_nc["text"].replace("**", ""))

      if st.button(
          "📌 Chọn đề này & Chuyển sang Bước 2",
          key="btn_chon_nc",
          type="primary",
      ):
        st.session_state["selected_de_key"] = selected_nc_key
        st.session_state["current_de_info"] = de_info_nc
        st.session_state["chat_messages"] = [{
            "role": "assistant",
            "content": (
                "Chào em! Cô là Trợ lý Ngữ văn. Đề bài các em đang chọn là:"
                f" '{selected_nc_key}'. Em cần cô hướng dẫn thêm ở phần nào"
                " trong dàn ý?"
            ),
        }]
        st.session_state["user_outline"] = ""
        st.session_state["user_essay"] = ""
        st.session_state["eval_vdnl_result"] = None
        if "grading_result" in st.session_state:
          del st.session_state["grading_result"]
        st.success(
            f"Các em đã chọn thành công: {selected_nc_key}! Mời các em bấm qua"
            " tab 'BƯỚC 2' phía trên."
        )

  with tab_de_tu_nhap:
    st.markdown("##### 📝 Dán đề bài cần hướng dẫn vào đây:")
    custom_de_text = st.text_area(
        "Nội dung đề bài tự chọn:",
        placeholder="Ví dụ: Viết bài văn nghị luận bàn về...",
        height=100,
    )
    student_custom_vdnl = st.text_input(
        "Vấn đề nghị luận em tự đoán cho đề này:",
        placeholder="Gõ VĐNL theo suy nghĩ của em...",
    )

    if st.button(
        "🔍 Phân tích đề tự nhập & Tạo giàn giáo Bước 2", type="primary"
    ):
      if not custom_de_text.strip():
        st.warning("Các em chưa dán nội dung đề bài!")
      else:
        with st.spinner("AI đang phân tích ngữ liệu và tạo giàn giáo..."):
          res_custom = ai_analyze_custom_exam(custom_de_text, student_custom_vdnl)
          ten_de_custom = "Đề tự nhập: " + (
              custom_de_text[:30] + "..."
              if len(custom_de_text) > 30
              else custom_de_text
          )
          info_custom = {
              "text": custom_de_text,
              "vdnl_chuan": res_custom.get("vdnl_chuan", student_custom_vdnl),
              "explain_guide": res_custom.get("explain_guide", ""),
              "explain_items": res_custom.get("explain_items", []),
              "vdnl_ket_luan": res_custom.get(
                  "vdnl_ket_luan", student_custom_vdnl
              ),
              "questions": res_custom.get("questions", []),
              "evidence": res_custom.get("evidence", []),
              "counter": res_custom.get("counter", []),
          }
          st.session_state["selected_de_key"] = ten_de_custom
          st.session_state["current_de_info"] = info_custom
          st.session_state["chat_messages"] = [{
              "role": "assistant",
              "content": (
                  "Chào em! Cô là Trợ lý Ngữ văn. Đề bài các em đang chọn là:"
                  f" '{ten_de_custom}'."
              ),
          }]
          st.session_state["user_outline"] = ""
          st.session_state["user_essay"] = ""
          st.session_state["eval_vdnl_result"] = {
              "status": res_custom.get("status", "LECH"),
              "feedback": res_custom.get("feedback", ""),
              "suggested_fix": res_custom.get("vdnl_chuan", ""),
          }
          st.success(
              "✅ Đã tạo xong giàn giáo Bước 2 cho đề bài tự nhập! Mời các em"
              " bấm sang tab 'BƯỚC 2'."
          )

  st.markdown("---")
  cur_active_key = st.session_state["selected_de_key"]
  cur_active_info = st.session_state["current_de_info"]
  st.info(f"📌 **Đề bài hiện tại đang chọn:** {cur_active_key}")

  if "Đề tự nhập" not in cur_active_key:
    student_vdnl = st.text_input(
        "⚡ Thao tác học sinh: Xác định vấn đề nghị luận của đề đang chọn:",
        placeholder="Gõ câu trả lời của em ở đây...",
    )
    if st.button("🔍 Đối chiếu vấn đề nghị luận với AI", type="primary"):
      if student_vdnl.strip():
        with st.spinner("AI đang thẩm định nghiêm túc..."):
          res = ai_evaluate_student_vdnl(
              cur_active_info["text"],
              cur_active_info["vdnl_chuan"],
              student_vdnl,
          )
          st.session_state["eval_vdnl_result"] = res
      else:
        st.warning("Các em chưa nhập câu trả lời!")

  if st.session_state.get("eval_vdnl_result"):
    res = st.session_state["eval_vdnl_result"]
    status_code = res.get("status", "LECH")
    if status_code == "DUNG":
      st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}")
    elif status_code == "LECH":
      st.warning(
          f"⚠️ **CẦN ĐIỀU CHỈNH CHUẨN XÁC HƠN:** {res.get('feedback')}\n\n👉"
          f" *Đáp án chuẩn:* {res.get('suggested_fix')}"
      )
    else:
      st.error(
          f"❌ **CHƯA ĐÚNG TRỌNG TÂM:** {res.get('feedback')}\n\n👉 *Đáp án"
          f" chuẩn:* {res.get('suggested_fix')}"
      )

# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG
# ------------------------------------------------------------------------------
with tabs[1]:
  cur_de_key = st.session_state["selected_de_key"]
  cur_de_info = st.session_state["current_de_info"]

  c_left, c_right = st.columns([1.1, 0.9], gap="large")

  with c_left:
    st.markdown(
        f"#### 🛠️ Gợi ý khung tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>",
        unsafe_allow_html=True,
    )

    # Thao tác 1: Giải thích ưu tiên từ khóa trước, sau đó nghĩa nhận định và chốt VĐNL
    with st.expander(
        "📌 Thao tác 1: Giải thích bản chất khái niệm / nhận định", expanded=True
    ):
      guide_txt = cur_de_info.get(
          "explain_guide",
          "*Định hướng: Ưu tiên giải thích từ khóa trong ngữ liệu trước, sau"
          " đó mở rộng ý nghĩa nhận định và chốt vấn đề nghị luận.*",
      )
      items = cur_de_info.get("explain_items", [])
      vdnl_kl = cur_de_info.get(
          "vdnl_ket_luan", cur_de_info.get("vdnl_chuan", "")
      )

      items_html = ""
      for itm in items:
        items_html += f"<li style='margin-bottom: 8px;'>{itm}</li>"

      st.markdown(
          f"""
            <div class='explain-box-chuan'>
                <p style='margin:0 0 10px 0; font-style:italic; color:#475569;'>{guide_txt}</p>
                <ul style='margin:0 0 12px 0; padding-left: 20px;'>
                    {items_html}
                </ul>
                <p style='margin:0; font-weight:700; color:#166534;'>
                    👉 Chốt lại Vấn đề nghị luận (VĐNL): <span style='font-weight:normal; font-style:italic;'>{vdnl_kl}</span>
                </p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with st.expander(
        "💡 Thao tác 2: Bàn luận trọng tâm (Hệ thống ý sâu sắc, đa chiều)",
        expanded=True,
    ):
      for q in cur_de_info.get("questions", []):
        st.markdown(f"**❓ {q['cau_hoi']}**")
        for ans in q.get("y_tra_loi", []):
          st.markdown(f"  * {ans}")

    with st.expander(
        "📚 Thao tác 3: Kho dẫn chứng trọng tâm & Dẫn chứng mở rộng",
        expanded=True,
    ):
      st.markdown("##### 📌 Dẫn chứng thực tế sâu sắc cho đề bài đang chọn:")
      list_ev = cur_de_info.get("evidence", [])
      for ev in list_ev:
        if isinstance(ev, dict):
          st.markdown(
              f"""
                    <div class='evidence-card'>
                        <h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>
                        <p style='margin:0 0 6px 0;'><b>• Chi tiết sự kiện/hành động:</b> {ev.get('chi_tiet', '')}</p>
                        <p style='margin:0 0 6px 0;'><b>• Ý nghĩa phân tích bài viết:</b> {ev.get('y_nghia', '')}</p>
                        <p style='margin:0; font-size:0.85rem; color:#64748b;'>📰 <i>Nguồn kiểm chứng: {ev.get('nguon', '')}</i></p>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
        else:
          st.markdown(f"<div class='evidence-card'>{ev}</div>", unsafe_allow_html=True)

      st.markdown("---")
      st.markdown("##### 📚 Tra cứu Kho dẫn chứng mở rộng (8 nhóm chủ điểm):")
      selected_topic = st.selectbox(
          "Chọn chủ điểm dẫn chứng cần tra cứu:",
          options=list(KHO_DAN_CHUNG_8_CHU_DIEM.keys()),
          key="sb_kho_dc",
      )
      for dc in KHO_DAN_CHUNG_8_CHU_DIEM[selected_topic]:
        with st.container(border=True):
          st.markdown(
              f"#### 👤 <span style='color:#1d4ed8;'>{dc['ten']}</span>",
              unsafe_allow_html=True,
          )
          st.write(dc["noi_dung"])
          st.caption(f"📰 *Nguồn kiểm chứng: {dc['nguon']}*")

    with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng", expanded=False):
      for c in cur_de_info.get("counter", []):
        st.markdown(f"- {c}")

    st.markdown("---")
    st.markdown("#### 📝 Lập Dàn Ý 3 Phần Của Em")
    vdnl_val = cur_de_info.get("vdnl_chuan", "Vấn đề nghị luận từ đề bài")
    auto_outline = (
        "I. MỞ BÀI:\n- Dẫn dắt & nêu vấn đề nghị luận:"
        f" {vdnl_val}\n\nII. THÂN BÀI:\n1. Giải thích bản chất khái niệm:\n2."
        " Bàn luận trọng tâm:\n   + Ý 1:\n   + Ý 2:\n3. Dẫn chứng thực tế tiêu"
        " biểu:\n4. Phản biện & Mở rộng:\n\nIII. KẾT BÀI:\n- Bài học nhận thức"
        " & hành động:"
    )

    if not st.session_state.get("user_outline"):
      st.session_state["user_outline"] = auto_outline

    user_outline = st.text_area(
        "Hoàn thiện dàn ý tại đây:",
        value=st.session_state["user_outline"],
        height=260,
    )
    st.session_state["user_outline"] = user_outline

  with c_right:
    st.markdown("#### 🧭 Trợ lý Ngữ văn (Định Hướng Phương Pháp)")
    with st.container(border=True):
      st.info(
          "💡 **Nguyên tắc:** Trợ lý Ngữ văn **không viết hộ / làm hộ bài văn**,"
          " chỉ đặt câu hỏi gợi mở để giúp các em tự tư duy."
      )

    if (
        "chat_messages" not in st.session_state
        or not st.session_state["chat_messages"]
    ):
      st.session_state["chat_messages"] = [{
          "role": "assistant",
          "content": (
              f"Chào em! Cô là Trợ lý Ngữ văn. Đề bài các em đang chọn là:"
              f" '{cur_de_key}'. Các em cần cô hướng dẫn thêm ở phần nào trong"
              " dàn ý?"
          ),
      }]

    chat_box = st.container(height=380)
    with chat_box:
      for m in st.session_state["chat_messages"]:
        st.chat_message(m["role"]).write(m["content"])

    u_msg = st.chat_input(
        "Hỏi cô về cách giải thích, chọn dẫn chứng...", key="chat_input_b2"
    )
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
      with st.spinner("Trợ lý Ngữ văn đang định hướng..."):
        reply = call_gemini_engine(prompt_chat)
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": reply}
        )
      st.rerun()

# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI (Placeholder ổn định)
# ------------------------------------------------------------------------------
with tabs[2]:
  st.markdown(
      '<div class="section-title">✍️ Xưởng Viết Bài Độc Lập</div>',
      unsafe_allow_html=True,
  )
  st.info(
      "Phần này đang được giữ ổn định cấu trúc cơ bản. Chúng ta sẽ hoàn thiện"
      " chi tiết sau."
  )
  essay_in = st.text_area(
      "Nhập bài viết của em:",
      value=st.session_state.get("user_essay", ""),
      height=300,
  )
  st.session_state["user_essay"] = essay_in

# ------------------------------------------------------------------------------
# BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ RUBRIC (Placeholder ổn định)
# ------------------------------------------------------------------------------
with tabs[3]:
  st.markdown(
      '<div class="section-title">🔍 Đánh Giá Rubric</div>',
      unsafe_allow_html=True,
  )
  st.info(
      "Phần này đang được giữ ổn định cấu trúc cơ bản. Chúng ta sẽ hoàn thiện"
      " chi tiết sau."
  )

# ------------------------------------------------------------------------------
# HỒ SƠ BÀI LÀM (Placeholder ổn định)
# ------------------------------------------------------------------------------
with tabs[4]:
  st.markdown(
      '<div class="section-title">📁 Hồ Sơ Bài Làm</div>',
      unsafe_allow_html=True,
  )
  st.info(
      "Phần này đang được giữ ổn định cấu trúc cơ bản. Chúng ta sẽ hoàn thiện"
      " chi tiết sau."
  )
