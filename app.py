import json
import re
import google.generativeai as genai
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
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    
    .explain-box-clean {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #16a34a;
        padding: 18px 22px;
        border-radius: 10px;
        line-height: 1.75;
        font-size: 0.96rem;
        color: #1e293b;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. HỆ THỐNG TRỌN VẸN 15 ĐỀ CƠ BẢN (ĐẦY ĐỦ 100% NỘI DUNG GỐC, KHÔNG LƯỢC BỚT)
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
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Lối sống có trách"
                " nhiệm</i> là sự nhận thức đúng đắn về bổn phận đối với tập"
                " thể; <i>gắn bó với cộng đồng</i> là sự sẻ chia, tình nghĩa và"
                " tinh thần dấn thân cống hiến."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Ý thơ Chế Lan Viên qua hình"
                " ảnh 'nơi đất ở' và 'đất hóa tâm hồn' làm nổi bật mối quan hệ"
                " gắn kết sâu sắc: khi con người biết sống cống hiến và trách"
                " nhiệm, không gian sống vô tri sẽ hóa thành nghĩa tình gắn"
                " bó."
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
        "evidence": [
            {
                "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
                "chi_tiet": (
                    "Sáng lập mô hình kết nối nhận nuôi cơm trưa cho hơn 60.000 học"
                    " sinh vùng cao khó khăn tại Điện Biên, Hà Giang."
                ),
                "y_nghia": (
                    "Chứng minh trách nhiệm được chuyển hóa thành hành động thực"
                    " tế thiết thực để thay đổi cuộc sống cộng đồng, làm cho 'đất"
                    " hóa tâm hồn'."
                ),
                "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn TNCS Hồ Chí Minh",
            },
            {
                "ten": "Đội cứu trợ thiện nguyện 'SOS Vũng Tàu'",
                "chi_tiet": (
                    "Hàng chục thành viên tự nguyện vá đường, hỗ trợ sửa xe và cấp"
                    " cứu người tai nạn đêm hôm hoàn toàn miễn phí suốt nhiều"
                    " năm."
                ),
                "y_nghia": (
                    "Biểu hiện sinh động cho lối sống đẹp, trách nhiệm cao cả vì"
                    " sự bình yên của cộng đồng."
                ),
                "nguon": "Báo Thanh Niên",
            },
        ],
        "counter": [(
            "Phê phán lối sống ích kỷ, thực dụng, 'chỉ biết mình', thờ ơ"
            " trước những vấn đề chung của xã hội."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ ý thơ 'Tiếng hát con tàu' của Chế Lan Viên; giới thiệu"
                " vấn đề nghị luận: Ý nghĩa của lối sống có trách nhiệm và biết"
                " gắn bó với cộng đồng."
            ),
            "gt": (
                "Giải thích từ khóa 'lối sống có trách nhiệm', 'gắn bó cộng đồng';"
                " làm rõ ý nghĩa 'đất hóa tâm hồn'."
            ),
            "bl": (
                "• Luận điểm 1: Con người là thực thể xã hội, sự phát triển cá"
                " nhân luôn cần bệ phóng từ tập thể.\n• Luận điểm 2: Sống trách"
                " nhiệm giúp đẩy lùi căn bệnh vô cảm, lan tỏa sự tử tế.\n• Luận"
                " điểm 3: Cống hiến là con đường khẳng định giá trị thanh xuân rực"
                " rỡ."
            ),
            "dc": (
                "• Dẫn chứng 1: Hoàng Hoa Trung và dự án 'Nuôi Em'.\n• Dẫn chứng"
                " 2: Đội cứu trợ thiện nguyện 'SOS Vũng Tàu'."
            ),
            "pb": (
                "Phê phán lối sống ích kỷ, vô cảm; đồng thời phân định rạch ròi"
                " giữa trách nhiệm chân chính với sự bao đồng, hình thức."
            ),
            "kb": (
                "Khẳng định lại giá trị của lối sống trách nhiệm; rút ra bài học"
                " nhận thức và hành động thiết thực cho bản thân."
            ),
        },
    },
    "Đề 02: Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.
Hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": (
            "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa"
            " con người với con người trong xã hội hiện đại."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Thấu cảm</i> là"
                " năng lực đặt mình vào vị trí người khác; <i>lắng nghe chân"
                " thành</i> là thái độ kiên nhẫn, không phán xét để xoa dịu nỗi"
                " đau."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Hình ảnh ẩn dụ 'cơn bão lòng'"
                " chỉ những biến cố dữ dội, tổn thương tâm lý; qua đó khẳng định"
                " sự cần thiết của sự thấu hiểu để cùng nhau vượt qua khủng"
                " hoảng."
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
        "evidence": [
            {
                "ten": "TS. Đặng Hoàng Giang & Dự án 'Tổng đài Ngày Mai'",
                "chi_tiet": (
                    "Sáng lập tổng đài tham vấn tâm lý phi lợi nhuận chuyên lắng"
                    " nghe, xoa dịu và hỗ trợ tinh thần cho hàng ngàn người trẻ"
                    " gặp khủng hoảng trầm cảm."
                ),
                "y_nghia": (
                    "Không gian an toàn để được lắng nghe không phán xét có thể"
                    " cứu rỗi một cuộc đời trước bờ vực tuyệt vọng."
                ),
                "nguon": "Báo Thanh Niên, VTV Digital",
            },
            {
                "ten": (
                    "Đoàn xe ô tô chắn gió trên cầu Bãi Cháy trong bão Yagi"
                    " (2024)"
                ),
                "chi_tiet": (
                    "Trong trận bão lịch sử, các tài xế xe tải chủ động đi chậm"
                    " thành hàng dài song song để che chắn gió giật kinh hoàng"
                    " cho người đi xe máy."
                ),
                "y_nghia": (
                    "Sự thấu cảm trước hoạn nạn chuyển hóa thành hành động bảo"
                    " vệ cao đẹp."
                ),
                "nguon": "Đài Truyền hình Việt Nam (VTV1)",
            },
        ],
        "counter": [(
            "Phê phán thói vô cảm, tâm lý phán xét vội vàng, bạo lực ngôn từ"
            " trên không gian mạng."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ quan điểm của Haruki Murakami; giới thiệu vấn đề"
                " nghị luận: Sức mạnh của sự thấu cảm và lắng nghe chân thành"
                " trong xã hội hiện đại."
            ),
            "gt": (
                "Cắt nghĩa 'thấu cảm', 'lắng nghe chân thành'; giải mã 'cơn bão"
                " lòng'."
            ),
            "bl": (
                "• Luận điểm 1: Trong thời đại số, con người dễ cô đơn ngay giữa"
                " đám đông, khao khát sự sẻ chia.\n• Luận điểm 2: Thấu cảm giúp"
                " xóa bỏ định kiến, xoa dịu nỗi đau tinh thần.\n• Luận điểm 3:"
                " Lắng nghe chân thành là cầu nối gắn kết tình người."
            ),
            "dc": (
                "• Dẫn chứng 1: TS. Đặng Hoàng Giang với Dự án 'Tổng đài Ngày"
                " Mai'.\n• Dẫn chứng 2: Các tài xế ô tô chắn gió trên cầu Bãi"
                " Cháy."
            ),
            "pb": (
                "Phê phán thói vô cảm, tâm lý phán xét hùa theo đám đông và bạo"
                " lực ngôn từ trực tuyến."
            ),
            "kb": (
                "Khẳng định vai trò của sự thấu hiểu; rút ra bài học tu dưỡng"
                " bản thân trong giao tiếp."
            ),
        },
    },
    "Đề 03: Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: "Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": (
            "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế"
            " hệ trẻ trong bối cảnh hội nhập."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Bản sắc văn hóa dân"
                " tộc</i> là giá trị cốt lõi, tinh hoa truyền thống; <i>trách"
                " nhiệm giữ gìn</i> là bổn phận bảo vệ và phát huy cội nguồn."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Hình ảnh 'toàn cầu hóa' và"
                " 'chiếc mỏ neo' đặt ra vấn đề: hội nhập quốc tế rộng mở nhưng"
                " cội nguồn văn hóa là điểm tựa giữ vững bản lĩnh dân tộc."
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
        "evidence": [
            {
                "ten": "Rapper Đen Vâu & Ca sĩ Hoàng Thùy Linh",
                "chi_tiet": (
                    "Lồng ghép chất liệu ca dao, dân ca, nhạc cụ dân tộc vào âm"
                    " nhạc hiện đại như 'Nấu ăn cho em', 'LINK' đạt hàng chục"
                    " triệu lượt xem."
                ),
                "y_nghia": (
                    "Cách làm mới di sản sáng tạo giúp văn hóa truyền thống tỏa"
                    " sáng rực rỡ trong thời đại số."
                ),
                "nguon": "Báo Tuổi Trẻ, Báo Lao Động",
            },
            {
                "ten": "Dự án phục dựng cổ phục Việt 'Đại Việt Cổ Phong'",
                "chi_tiet": (
                    "Tập thể Gen Z tự nguyện nghiên cứu, phục dựng chuẩn xác"
                    " các bộ cổ phục thời Nguyễn, Lê ứng dụng vào đời sống."
                ),
                "y_nghia": (
                    "Khẳng định tình yêu cội nguồn và ý thức tự giác giữ gìn di"
                    " sản của thế hệ trẻ."
                ),
                "nguon": "Báo VnExpress",
            },
        ],
        "counter": [(
            "Phê phán thái độ sính ngoại mù quáng, coi thường tiếng Việt và"
            " các giá trị truyền thống."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ xu thế toàn cầu hóa; giới thiệu vấn đề nghị luận:"
                " Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của"
                " thế hệ trẻ."
            ),
            "gt": (
                "Giải thích 'bản sắc văn hóa', 'trách nhiệm giữ gìn'; làm rõ hình"
                " ảnh 'mỏ neo'."
            ),
            "bl": (
                "• Luận điểm 1: Văn hóa là căn cước định danh dân tộc, mất văn"
                " hóa là mất tất cả.\n• Luận điểm 2: Hội nhập không có nghĩa là"
                " hòa tan; bản sắc là nội lực giúp vươn xa."
            ),
            "dc": (
                "• Dẫn chứng 1: Rapper Đen Vâu và Hoàng Thùy Linh.\n• Dẫn chứng"
                " 2: Dự án phục dựng cổ phục."
            ),
            "pb": (
                "Phê phán thái độ sính ngoại mù quáng, lai căng văn hóa hoặc"
                " bảo thủ đóng khung."
            ),
            "kb": (
                "Khẳng định sứ mệnh của tuổi trẻ với di sản dân tộc; rút ra bài"
                " học hành động thiết thực."
            ),
        },
    },
    "Đề 04: Ý nghĩa của lòng biết ơn trong đời sống con người": {
        "text": """Danh ngôn dân gian có câu:
> *"Uống nước nhớ nguồn, ăn quả nhớ kẻ trồng cây."*
Từ cội nguồn đạo lý ấy, hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lòng biết ơn trong đời sống con người hôm nay.""",
        "vdnl_chuan": (
            "Ý nghĩa và giá trị đạo đức của lòng biết ơn trong đời sống con"
            " người."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Lòng biết ơn</i> là"
                " sự trân trọng, ghi nhớ và đền đáp những ân huệ, công lao của"
                " người đi trước hoặc những người giúp đỡ mình."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Các hình ảnh 'uống nước'"
                " nhớ 'nguồn', ăn 'quả' nhớ 'kẻ trồng cây' là đạo lý truyền"
                " thống sâu sắc nhắc nhở con người về nguồn cội thành quả."
            ),
        ],
        "vdnl_ket_luan": (
            "Ý nghĩa và giá trị đạo đức cốt lõi của lòng biết ơn trong đời"
            " sống con người."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao lòng biết ơn lại là nền tảng đạo đức bền vững nhất của"
                " nhân cách?"
            ),
            "y_tra_loi": [
                (
                    "Lòng biết ơn giúp con người kết nối với cội nguồn, nuôi"
                    " dưỡng lòng trắc ẩn và sự tử tế."
                ),
                (
                    "Biết ơn giúp xã hội gắn kết bằng tình nghĩa, ngăn chặn sự"
                    " lạnh lùng và tính toán thiệt hơn."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": (
                    "Hoạt động Đền ơn đáp nghĩa nhân ngày Thương binh Liệt sĩ"
                    " 27/7"
                ),
                "chi_tiet": (
                    "Hàng năm, toàn xã hội và thế hệ trẻ tổ chức thăm hỏi Mẹ"
                    " Việt Nam anh hùng, thắp nến tri ân các anh hùng liệt sĩ."
                ),
                "y_nghia": (
                    "Truyền thống uống nước nhớ nguồn được thể hiện sinh động"
                    " bằng hành động thiết thực."
                ),
                "nguon": "Báo Nhân Dân, Cổng thông tin Chính phủ",
            },
            {
                "ten": "Lễ giỗ Tổ Hùng Vương hằng năm",
                "chi_tiet": (
                    "Hàng triệu con dân đất Việt hướng về Đền Hùng (Phú Thọ) dâng"
                    " hương tưởng niệm quốc tổ."
                ),
                "y_nghia": (
                    "Minh chứng rõ nét cho đạo lý tri ân cội nguồn dân tộc của"
                    " người Việt Nam."
                ),
                "nguon": "Báo Văn Hóa",
            },
        ],
        "counter": [(
            "Phê phán thói vô ơn, ăn cháo đá bát, vong ân bội nghĩa, xem công"
            " sức người khác là điều hiển nhiên."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu tục ngữ dân gian; giới thiệu vấn đề nghị luận:"
                " Ý nghĩa của lòng biết ơn trong đời sống con người."
            ),
            "gt": (
                "Giải thích 'lòng biết ơn'; làm rõ ý nghĩa hình ảnh 'uống nước"
                " nhớ nguồn', 'ăn quả nhớ kẻ trồng cây'."
            ),
            "bl": (
                "• Luận điểm 1: Biết ơn là đạo lý truyền thống làm nên phẩm giá"
                " con người.\n• Luận điểm 2: Lòng biết ơn giúp gắn kết xã hội bằng"
                " tình nghĩa, nuôi dưỡng lòng trắc ẩn."
            ),
            "dc": (
                "• Dẫn chứng 1: Hoạt động tri ân 27/7.\n• Dẫn chứng 2: Lễ giỗ Tổ"
                " Hùng Vương."
            ),
            "pb": (
                "Phê phán thói vô ơn, ăn cháo đá bát, vong ân bội nghĩa."
            ),
            "kb": (
                "Khẳng định tầm quan trọng của lòng biết ơn; rút ra bài học hành"
                " động cho thế hệ trẻ."
            ),
        },
    },
    "Đề 05: Sức mạnh và giá trị của niềm tin vào bản thân": {
        "text": """Có câu nói nổi tiếng: *"Tin rằng bạn có thể làm được là bạn đã đi được nửa đường."* (Theodore Roosevelt)
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của niềm tin vào bản thân trong hành trình vươn tới thành công.""",
        "vdnl_chuan": (
            "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong"
            " cuộc sống."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Niềm tin vào bản"
                " thân</i> là sự tự tin vững chắc vào năng lực, phẩm chất và"
                " tiềm năng của chính mình."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Câu nói của Theodore"
                " Roosevelt khẳng định niềm tin chính là bệ phóng tâm lý quyết"
                " định biến ý chí thành hành động."
            ),
        ],
        "vdnl_ket_luan": (
            "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong"
            " hành trình vươn tới thành công."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao niềm tin vào bản thân lại là chiếc chìa khóa vạn năng"
                " mở cánh cửa thành công?"
            ),
            "y_tra_loi": [
                (
                    "Niềm tin giúp con người chiến thắng nỗi sợ thất bại, dám"
                    " đương đầu với thử thách lớn."
                ),
                (
                    "Khi mất niềm tin, con người sẽ bỏ cuộc ngay trước vạch"
                    " xuất phát; niềm tin là ngọn đuốc soi đường."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Diễn giả khuyết tật Nick Vujicic",
                "chi_tiet": (
                    "Sinh ra không có cả tay lẫn chân, ông đã chiến thắng sự"
                    " tuyệt vọng, tin vào giá trị bản thân để trở thành diễn"
                    " giả truyền cảm hứng toàn cầu."
                ),
                "y_nghia": (
                    "Minh chứng hùng hồn cho thấy niềm tin vào bản thân có thể"
                    " vượt qua mọi giới hạn thể xác."
                ),
                "nguon": "Báo Tuổi Trẻ",
            },
            {
                "ten": "Thầy giáo Nguyễn Ngọc Ký",
                "chi_tiet": (
                    "Bị liệt cả hai tay từ nhỏ, vượt lên mặc cảm, ông kiên trì"
                    " dùng chân viết chữ và tốt nghiệp đại học."
                ),
                "y_nghia": (
                    "Sức mạnh của niềm tin và ý chí sắt đá chiến thắng nghịch"
                    " cảnh."
                ),
                "nguon": "Báo Giáo Dục & Thời Đại",
            },
        ],
        "counter": [(
            "Phê phán căn bệnh tự ti, nhút nhát, rụt rè hoặc ngược lại là sự"
            " ảo tưởng sức mạnh, tự phụ mù quáng."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu nói của Theodore Roosevelt; giới thiệu vấn đề"
                " nghị luận: Sức mạnh và giá trị của niềm tin vào bản thân."
            ),
            "gt": (
                "Giải thích 'niềm tin vào bản thân'; làm rõ ý nghĩa thông điệp"
                " 'đã đi được nửa đường'."
            ),
            "bl": (
                "• Luận điểm 1: Niềm tin là bệ phóng giúp con người vượt qua nỗi"
                " sợ hãi, dám nghĩ dám làm.\n• Luận điểm 2: Thất bại lớn nhất"
                " là đánh mất niềm tin vào chính mình."
            ),
            "dc": (
                "• Dẫn chứng 1: Diễn giả Nick Vujicic.\n• Dẫn chứng 2: Thầy giáo"
                " Nguyễn Ngọc Ký."
            ),
            "pb": (
                "Phê phán căn bệnh tự ti, nhút nhát hoặc ảo tưởng sức mạnh tự"
                " phụ."
            ),
            "kb": (
                "Khẳng định vai trò của niềm tin; rút ra bài học hành động cho"
                " tuổi trẻ."
            ),
        },
    },
    "Đề 06: Giá trị của sự kiên trì và bền bỉ trong cuộc sống": {
        "text": """Ngạn ngữ dân gian có câu: *"Nước chảy đá mòn."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị của sự kiên trì, bền bỉ trong hành trình chinh phục mục tiêu của người trẻ.""",
        "vdnl_chuan": (
            "Giá trị của sự kiên trì, bền bỉ và ý chí vượt qua gian khó để đạt"
            " ước mơ."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Kiên trì, bền bỉ</i>"
                " là phẩm chất đeo bám mục tiêu đến cùng, không nản lòng trước"
                " trở ngại."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Hình ảnh 'nước chảy đá"
                " mòn' tượng trưng cho sức mạnh bền bỉ của sự tích tụ lâu ngày"
                " có thể chiến thắng cả vật cản cứng nhắc."
            ),
        ],
        "vdnl_ket_luan": (
            "Giá trị của sự kiên trì, bền bỉ và ý chí vượt qua gian khó trong"
            " hành trình chinh phục mục tiêu."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao thành công thực sự trong đời sống luôn đòi hỏi sự kiên"
                " trì và bền bỉ?"
            ),
            "y_tra_loi": [
                (
                    "Mọi giá trị lớn lao đều cần thời gian hun đúc; không có"
                    " thành công đích thực nào đạt được sau một đêm."
                ),
                (
                    "Sự kiên trì giúp rèn luyện bản lĩnh thép, biến sức ép thành"
                    " động lực hoàn thiện."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Vận động viên Nguyễn Thị Ánh Viên",
                "chi_tiet": (
                    "Dậy từ 4 giờ sáng mỗi ngày, bơi lội hàng chục km suốt nhiều"
                    " năm liền không nghỉ để giành hàng trăm huy chương vàng."
                ),
                "y_nghia": (
                    "Thành tích đỉnh cao chỉ đến từ sự kiên trì luyện tập khổ"
                    " hạnh."
                ),
                "nguon": "Báo Thể Thao & Văn Hóa",
            },
            {
                "ten": "Nhà phát minh Thomas Edison",
                "chi_tiet": (
                    "Thực hiện hơn 10.000 thí nghiệm thất bại trước khi phát"
                    " minh ra chiếc bóng đèn điện thương mại."
                ),
                "y_nghia": (
                    "Minh chứng vĩ đại cho tinh thần bền bỉ không bao giờ bỏ"
                    " cuộc."
                ),
                "nguon": "Lịch sử Khoa học thế giới",
            },
        ],
        "counter": [(
            "Phê phán lối sống cả thèm chóng chán, dễ nản lòng, gặp khó khăn là"
            " buông xuôi bỏ cuộc."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu ngạn ngữ 'Nước chảy đá mòn'; giới thiệu vấn đề"
                " nghị luận: Giá trị của sự kiên trì và bền bỉ."
            ),
            "gt": (
                "Giải thích 'kiên trì, bền bỉ'; phân tích ý nghĩa hình ảnh tự"
                " nhiên 'nước chảy đá mòn'."
            ),
            "bl": (
                "• Luận điểm 1: Mọi thành công lớn đều đòi hỏi quá trình tôi"
                " luyện lâu dài.\n• Luận điểm 2: Kiên trì giúp rèn luyện bản"
                " lĩnh, biến trở ngại thành bước đệm."
            ),
            "dc": (
                "• Dẫn chứng 1: VĐV Nguyễn Thị Ánh Viên.\n• Dẫn chứng 2: Nhà"
                " phát minh Thomas Edison."
            ),
            "pb": (
                "Phê phán thói cả thèm chóng chán, dễ nản lòng trước thử thách."
            ),
            "kb": (
                "Khẳng định giá trị của sự bền bỉ; rút ra bài học hành động cho"
                " bản thân."
            ),
        },
    },
    "Đề 07: Ý nghĩa của việc trân trọng những giá trị bình dị quanh ta": {
        "text": """Có ý kiến cho rằng: *"Hạnh phúc đôi khi không phải là những điều lớn lao, mà ẩn giấu trong những điều bình dị nhất của đời thường."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của việc biết trân trọng những giá trị bình dị xung quanh cuộc sống.""",
        "vdnl_chuan": (
            "Ý nghĩa của việc trân trọng những giá trị bình dị để tìm thấy hạnh"
            " phúc đích thực."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Trân trọng giá trị"
                " bình dị</i> là thái độ biết ơn, tận hưởng từng khoảnh khắc"
                " mộc mạc, gần gũi trong đời sống."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Khẳng định chân lý: hạnh"
                " phúc đích thực không nằm ở những điều xa vời mà neo đậu ở"
                " chính những điều giản dị quanh ta."
            ),
        ],
        "vdnl_ket_luan": (
            "Ý nghĩa của việc biết trân trọng những giá trị bình dị để tìm"
            " thấy hạnh phúc đích thực trong đời sống."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao con người hiện đại thường hay đánh mất sự trân trọng"
                " đối với những điều bình dị?"
            ),
            "y_tra_loi": [
                (
                    "Nhịp sống hối hả và áp lực thành công vật chất ảo khiến"
                    " con người lao đi tìm kiếm những điều xa vời mà quên mất"
                    " hiện tại."
                ),
                (
                    "Chỉ khi trải qua mất mát, con người mới nhận ra sự bình"
                    " yên trong những điều nhỏ bé mới là tài sản quý giá nhất."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": (
                    "Trào lưu 'Chữa lành' (Healing) và lối sống tối giản"
                    " (Minimalism)"
                ),
                "chi_tiet": (
                    "Giới trẻ tìm về thiên nhiên, tự nấu ăn, chăm sóc cây cối,"
                    " trân trọng từng phút giây tĩnh tại."
                ),
                "y_nghia": (
                    "Sự thức tỉnh quay về trân trọng các giá trị bình dị nguyên"
                    " bản."
                ),
                "nguon": "Báo Dân Trí",
            },
            {
                "ten": "Bức tranh gia đình trong mùa dịch Covid-19",
                "chi_tiet": (
                    "Khoảng thời gian giãn cách xã hội giúp mỗi người nhận ra"
                    " bữa cơm nhà đầm ấm quý giá hơn mọi danh vọng xa hoa."
                ),
                "y_nghia": (
                    "Sự trân trọng những điều bình dị cứu rỗi tâm hồn con người."
                ),
                "nguon": "Báo Tuổi Trẻ",
            },
        ],
        "counter": [(
            "Phê phán lối sống thực dụng, chạy theo hư vinh ảo tưởng, xem"
            " thường những hạnh phúc mộc mạc xung quanh."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ nhịp sống hiện đại; giới thiệu vấn đề nghị luận: Ý"
                " nghĩa của việc trân trọng những giá trị bình dị."
            ),
            "gt": (
                "Giải thích 'trân trọng giá trị bình dị'; làm rõ quan niệm về"
                " hạnh phúc đích thực."
            ),
            "bl": (
                "• Luận điểm 1: Hạnh phúc không ở đâu xa mà nằm trong những điều"
                " mộc mạc nhất.\n• Luận điểm 2: Trân trọng bình dị giúp tâm hồn"
                " thanh thản, tránh xa cạm bẫy hư vinh."
            ),
            "dc": (
                "• Dẫn chứng 1: Trào lưu sống tối giản, chữa lành.\n• Dẫn chứng"
                " 2: Giá trị bữa cơm gia đình trong đại dịch."
            ),
            "pb": (
                "Phê phán lối sống thực dụng, chạy theo hư vinh ảo tưởng."
            ),
            "kb": (
                "Khẳng định ý nghĩa của sự trân trọng; rút ra bài học sống chậm"
                " lại và yêu thương."
            ),
        },
    },
    "Đề 08: Vai trò của sách và văn hóa đọc trong thời đại số": {
        "text": """Maxim Gorky từng khẳng định: *"Sách mở ra trước mắt tôi những chân trời mới."*
Trong thời đại bùng nổ công nghệ số, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò và giá trị của việc đọc sách.""",
        "vdnl_chuan": (
            "Vai trò, ý nghĩa của sách và văn hóa đọc đối với sự phát triển"
            " nhân cách con người."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Sách</i> là kho tàng"
                " lưu giữ tri thức nhân loại; <i>văn hóa đọc</i> là ứng xử, thói"
                " quen và giá trị thưởng thức sách của con người."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Câu nói của Maxim Gorky"
                " ví sách như chiếc chìa khóa mở ra những chân trời tri thức"
                " mới bao la."
            ),
        ],
        "vdnl_ket_luan": (
            "Vai trò, ý nghĩa của sách và văn hóa đọc đối với sự phát triển"
            " nhân cách con người trong thời đại số."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao trong thời đại Internet bùng nổ, sách giấy và văn hóa"
                " đọc vẫn giữ giá trị độc tôn?"
            ),
            "y_tra_loi": [
                (
                    "Internet cung cấp thông tin bề mặt nhanh chóng nhưng rời"
                    " rạc; sách mang lại tri thức có hệ thống và chiều sâu tư"
                    " duy."
                ),
                (
                    "Đọc sách là quá trình tương tác tĩnh lặng giúp bồi dưỡng"
                    " tâm hồn, rèn luyện sự tập trung."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Đường sách TP.HCM và Hà Nội",
                "chi_tiet": (
                    "Thu hút hàng triệu lượt bạn trẻ đến tham quan, đọc sách và"
                    " giao lưu văn hóa mỗi năm."
                ),
                "y_nghia": (
                    "Sức sống bền bỉ và sự lan tỏa mạnh mẽ của văn hóa đọc giữa"
                    " lòng đô thị hiện đại."
                ),
                "nguon": "Sở Thông tin và Truyền thông TP.HCM",
            },
            {
                "ten": "Đại sứ Văn hóa đọc Việt Nam (nhiều mùa)",
                "chi_tiet": (
                    "Cuộc thi thu hút hàng triệu học sinh tham gia viết cảm nhận"
                    " sách, lan tỏa tình yêu đọc sách rộng khắp."
                ),
                "y_nghia": (
                    "Khẳng định sức hút và vai trò của sách đối với thế hệ trẻ."
                ),
                "nguon": "Bộ Văn hóa, Thể thao và Du lịch",
            },
        ],
        "counter": [(
            "Phê phán tình trạng lười đọc sách, nghiện mạng xã hội, chỉ chuộng"
            " thông tin 'mì ăn liền' nông cạn."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu nói của Maxim Gorky; giới thiệu vấn đề nghị"
                " luận: Vai trò của sách và văn hóa đọc trong thời đại số."
            ),
            "gt": (
                "Giải thích 'sách', 'văn hóa đọc'; làm rõ hình ảnh 'chân trời mới'"
                " tượng trưng cho tri thức."
            ),
            "bl": (
                "• Luận điểm 1: Sách cung cấp tri thức có hệ thống, bồi dưỡng"
                " tâm hồn và nhân cách.\n• Luận điểm 2: Trong thời đại số, sách"
                " là khoảng lặng quý giá để rèn luyện tư duy sâu (deep"
                " thinking)."
            ),
            "dc": (
                "• Dẫn chứng 1: Đường sách TP.HCM và Hà Nội.\n• Dẫn chứng 2:"
                " Cuộc thi Đại sứ Văn hóa đọc."
            ),
            "pb": (
                "Phê phán tình trạng lười đọc sách, chìm đắm vào mạng xã hội"
                " nông cạn."
            ),
            "kb": (
                "Khẳng định giá trị của sách; rút ra bài học xây dựng thói quen"
                " đọc sách mỗi ngày."
            ),
        },
    },
    "Đề 09: Lòng dũng cảm bảo vệ cái đúng, cái thiện": {
        "text": """Có ý kiến cho rằng: *"Lòng dũng cảm không phải là không sợ hãi, mà là sự chiến thắng nỗi sợ hãi."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải và công lý.""",
        "vdnl_chuan": (
            "Vai trò của lòng dũng cảm trong đấu tranh bảo vệ cái đúng, cái"
            " thiện và lẽ công bằng."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Lòng dũng cảm</i> là"
                " bản lĩnh dám đối mặt với hiểm nguy, sự thật để bảo vệ lẽ"
                " phải và công lý."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Khẳng định lòng dũng cảm"
                " không phải sự vô cảm trước hiểm nguy mà là sự chiến thắng nỗi"
                " sợ hãi cá nhân."
            ),
        ],
        "vdnl_ket_luan": (
            "Vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải, công lý và"
            " thúc đẩy xã hội văn minh."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao sự im lặng trước cái xấu đôi khi còn nguy hiểm hơn cả"
                " cái ác?"
            ),
            "y_tra_loi": [
                (
                    "Sự im lặng, dĩ hòa vi quý, sợ liên lụy chính là tấm áo giáp"
                    " dung dưỡng, tiếp tay cho cái ác lộng hành."
                ),
                (
                    "Lòng dũng cảm lên tiếng bảo vệ lẽ phải là thước đo phẩm"
                    " giá làm người."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Những tấm gương cứu người trong lũ dữ (bão Yagi)",
                "chi_tiet": (
                    "Nhiều người dân bình thường không quản hiểm nguy lao mình"
                    " vào dòng nước xiết để cứu học sinh, người già mắc kẹt."
                ),
                "y_nghia": (
                    "Lòng dũng cảm xả thân vì đồng loại tỏa sáng rực rỡ trong"
                    " nghịch cảnh."
                ),
                "nguon": "Báo Công An Nhân Dân",
            },
            {
                "ten": "Nhà báo Đặng Loan đấu tranh chống tiêu cực",
                "chi_tiet": (
                    "Kiên quyết ngòi bút vạch trần tham nhũng bất chấp đe dọa"
                    " hiểm nguy."
                ),
                "y_nghia": (
                    "Minh chứng cho bản lĩnh dũng cảm bảo vệ công lý xã hội."
                ),
                "nguon": "Báo Tuổi Trẻ",
            },
        ],
        "counter": [(
            "Phê phán thái độ hèn nhát, vô cảm, 'thấy việc nghĩa không làm', sợ"
            " chuốc họa vào thân."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu nói về lòng dũng cảm; giới thiệu vấn đề nghị"
                " luận: Vai trò của lòng dũng cảm trong việc bảo vệ lẽ phải và"
                " công lý."
            ),
            "gt": (
                "Giải thích 'lòng dũng cảm'; làm rõ ý kiến: dũng cảm là chiến"
                " thắng nỗi sợ hãi."
            ),
            "bl": (
                "• Luận điểm 1: Lòng dũng cảm là tấm lá chắn bảo vệ công lý và"
                " những yếu thế.\n• Luận điểm 2: Sự im lặng trước cái xấu chính"
                " là sự tiếp tay cho cái ác lộng hành."
            ),
            "dc": (
                "• Dẫn chứng 1: Người dân cứu người trong lũ dữ.\n• Dẫn chứng 2:"
                " Nhà báo đấu tranh tiêu cực."
            ),
            "pb": (
                "Phê phán thái độ hèn nhát, vô cảm, thấy việc nghĩa không làm."
            ),
            "kb": (
                "Khẳng định ý nghĩa của lòng dũng cảm; rút ra bài học hành động"
                " cho thế hệ trẻ."
            ),
        },
    },
    "Đề 10: Ứng xử văn minh trên không gian mạng": {
        "text": """Mạng xã hội giống như con dao hai lưỡi vừa kết nối toàn cầu vừa tiềm ẩn nhiều hệ lụy văn hóa.
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về cách ứng xử thông minh và văn minh của người trẻ trên không gian mạng.""",
        "vdnl_chuan": (
            "Cách ứng xử thông minh, làm chủ công nghệ và bản lĩnh văn hóa"
            " trên không gian mạng."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Ứng xử văn minh trên"
                " mạng</i> là tác phong giao tiếp lịch sự, có trách nhiệm pháp"
                " lý và đạo đức khi đăng tải, chia sẻ thông tin."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Hình ảnh ẩn dụ 'con dao hai"
                " lưỡi' chỉ mặt tích cực (kết nối) và tiêu cực (tin giả, văn"
                " hóa độc hại) của mạng xã hội."
            ),
        ],
        "vdnl_ket_luan": (
            "Cách ứng xử thông minh, làm chủ công nghệ và bản lĩnh văn hóa của"
            " người trẻ trên không gian mạng."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao người trẻ dễ sa ngã trở thành 'anh hùng bàn phím' trên"
                " không gian mạng?"
            ),
            "y_tra_loi": [
                (
                    "Tính ẩn danh của tài khoản ảo tạo ra cảm giác vô trách"
                    " nhiệm, phóng thích những bức xúc cá nhân."
                ),
                (
                    "Tâm lý đám đông thiếu tư duy phản biện khiến nhiều người"
                    " hùa theo tấn công người khác."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Bộ Quy tắc ứng xử trên mạng xã hội (Bộ TT&TT)",
                "chi_tiet": (
                    "Ban hành nhằm định hướng người dùng hành xử chuẩn mực,"
                    " tôn trọng pháp luật và đạo đức trực tuyến."
                ),
                "y_nghia": (
                    "Khung pháp lý thiết thực xây dựng môi trường mạng lành"
                    " mạnh."
                ),
                "nguon": "Cổng thông tin Bộ Thông tin và Truyền thông",
            },
            {
                "ten": "Chiến dịch 'No Cyber Bullying' của học sinh sinh viên",
                "chi_tiet": (
                    "Nhiều trường học phát động phong trào nói không với miệt"
                    " thị ngoại hình và bạo lực mạng."
                ),
                "y_nghia": (
                    "Hành động thiết thực làm sạch không gian mạng của thế hệ"
                    " trẻ."
                ),
                "nguon": "Báo Thanh Niên",
            },
        ],
        "counter": [(
            "Phê phán hiện tượng miệt thị ngoại hình, lăng mạ, tung tin giả"
            " câu view trên mạng xã hội."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ sự bùng nổ mạng xã hội; giới thiệu vấn đề nghị luận:"
                " Cách ứng xử thông minh và văn minh của người trẻ trên không"
                " gian mạng."
            ),
            "gt": (
                "Giải thích 'ứng xử văn minh'; làm rõ hình ảnh 'con dao hai"
                " lưỡi' của mạng xã hội."
            ),
            "bl": (
                "• Luận điểm 1: Mạng xã hội mở ra thế giới kết nối nhưng cũng"
                " tiềm ẩn rác văn hóa.\n• Luận điểm 2: Người trẻ cần trang bị"
                " bản lĩnh, tư duy phản biện để làm chủ công nghệ thay vì để"
                " công nghệ giật dây."
            ),
            "dc": (
                "• Dẫn chứng 1: Bộ Quy tắc ứng xử trên mạng xã hội.\n• Dẫn chứng"
                " 2: Chiến dịch phản đối bạo lực mạng."
            ),
            "pb": (
                "Phê phán hiện tượng 'anh hùng bàn phím', tung tin giả, miệt thị"
                " ngoại hình."
            ),
            "kb": (
                "Khẳng định trách nhiệm khi tham gia mạng xã hội; rút ra bài"
                " học ứng xử cho bản thân."
            ),
        },
    },
    "Đề 11: Giá trị của sự trung thực trong học tập và đời sống": {
        "text": """Có ý kiến cho rằng: *"Sự thật có thể gây tổn thương trong chốc lát, nhưng dối trá để lại vết sẹo vĩnh viễn."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về giá trị và ý nghĩa của phẩm chất trung thực trong học tập và đời sống.""",
        "vdnl_chuan": (
            "Ý nghĩa và giá trị của phẩm chất trung thực đối với sự trưởng"
            " thành nhân cách."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Trung thực</i> là"
                " phẩm chất tôn trọng sự thật, nói và làm đúng với lương tâm,"
                " ngay thẳng và chân thành."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Sự thật có thể phũ phàng"
                " nhưng mau chóng qua đi, trong khi dối trá phá hủy niềm tin"
                " vĩnh viễn."
            ),
        ],
        "vdnl_ket_luan": (
            "Ý nghĩa và giá trị của phẩm chất trung thực đối với sự trưởng"
            " thành nhân cách con người."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao bệnh gian lận trong học tập và đời sống lại là mối nguy"
                " hại lớn?"
            ),
            "y_tra_loi": [
                (
                    "Gian lận làm thui chột năng lực thực chất, tạo ra 'giả học"
                    " thức, thật bằng cấp', làm xói mòn kỷ cương đạo đức."
                ),
                (
                    "Sự dối trá một khi bị lật tẩy sẽ phá vỡ hoàn toàn uy tín"
                    " và sự tôn trọng."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Cuộc vận động 'Nói không với tiêu cực trong thi cử'",
                "chi_tiet": (
                    "Do Bộ GD&ĐT phát động nhằm siết chặt kỷ luật phòng thi, đề"
                    " cao giá trị thực chất."
                ),
                "y_nghia": (
                    "Khẳng định nền tảng trung thực trong giáo dục là cốt lõi"
                    " của quốc gia."
                ),
                "nguon": "Bộ Giáo dục và Đào tạo",
            },
            {
                "ten": "Tấm gương nhặt được của rơi trả lại người mất",
                "chi_tiet": (
                    "Nhiều học sinh nghèo nhặt được ví tiền hàng trăm triệu đồng"
                    " đã chủ động tìm công an giao nộp trả lại."
                ),
                "y_nghia": (
                    "Phẩm chất trung thực tỏa sáng rực rỡ trong đời sống thường"
                    " nhật."
                ),
                "nguon": "Báo Tuổi Trẻ",
            },
        ],
        "counter": [(
            "Phê phán thói gian lận thi cử, đạo văn (plagiarism) và bệnh"
            " thành tích dối trá."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu nói về sự thật và dối trá; giới thiệu vấn đề"
                " nghị luận: Giá trị của sự trung thực trong học tập và đời"
                " sống."
            ),
            "gt": (
                "Giải thích 'trung thực'; làm rõ ý nghĩa: sự thật dẫu đau đớn còn"
                " hơn dối trá vĩnh viễn."
            ),
            "bl": (
                "• Luận điểm 1: Trung thực là gốc rễ của nhân cách, là nền tảng"
                " tạo dựng lòng tin giữa người với người.\n• Luận điểm 2: Gian"
                " lận, dối trá trong học tập và đời sống làm thui chột năng lực"
                " thực chất."
            ),
            "dc": (
                "• Dẫn chứng 1: Cuộc vận động nói không với tiêu cực thi cử của"
                " Bộ GD&ĐT.\n• Dẫn chứng 2: Học sinh nhặt được của rơi trả lại"
                " người mất."
            ),
            "pb": (
                "Phê phán bệnh thành tích, gian lận thi cử và đạo văn."
            ),
            "kb": (
                "Khẳng định giá trị của lòng trung thực; rút ra bài học rèn luyện"
                " cho học sinh."
            ),
        },
    },
    "Đề 12: Tầm quan trọng của tinh thần tự học đối với học sinh": {
        "text": """Chủ tịch Hồ Chí Minh từng căn dặn: *"Học ở trường, học ở sách vở, học lẫn nhau và học nhân dân."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về tầm quan trọng của tinh thần tự học đối với học sinh trong thời đại mới.""",
        "vdnl_chuan": (
            "Tầm quan trọng và giá trị của tinh thần tự học đối với sự phát"
            " triển của người trẻ."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Tinh thần tự học</i>"
                " là quá trình chủ động tìm tòi, tiếp thu tri thức bằng tư duy"
                " độc lập mà không phụ thuộc vào sự áp đặt."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Lời căn dặn của Bác Hồ"
                " chỉ ra phương pháp học toàn diện ở mọi lúc, mọi nơi, từ nhiều"
                " nguồn khác nhau."
            ),
        ],
        "vdnl_ket_luan": (
            "Tầm quan trọng và giá trị quyết định của tinh thần tự học đối với"
            " học sinh."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao học sinh ngày nay buộc phải trang bị năng lực tự học"
                " làm kim chỉ nam?"
            ),
            "y_tra_loi": [
                (
                    "Sự bùng nổ tri thức khiến sách giáo khoa chỉ là nền tảng"
                    " cơ bản; thế giới thay đổi từng ngày đòi hỏi phải học"
                    " suốt đời."
                ),
                (
                    "Tự học giúp rèn luyện tư duy độc lập, khả năng thích ứng"
                    " và sự sáng tạo."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Tấm gương tự học vĩ đại của Chủ tịch Hồ Chí Minh",
                "chi_tiet": (
                    "Người tự học thông thạo hơn 10 ngoại ngữ và nghiên cứu"
                    " chính trị khi bôn ba khắp thế giới."
                ),
                "y_nghia": (
                    "Biểu tượng vĩ đại về tinh thần tự học suốt đời vì sự"
                    " nghiệp cứu nước."
                ),
                "nguon": "Tư liệu Lịch sử Đảng Cộng sản Việt Nam",
            },
            {
                "ten": "Tỷ phú Bill Gates & Thói quen đọc sách tự nghiên cứu",
                "chi_tiet": (
                    "Dù đã thành công đỉnh cao, ông vẫn duy trì tự học, đọc hàng"
                    " chục cuốn sách mỗi tháng để cập nhật tri thức nhân loại."
                ),
                "y_nghia": (
                    "Tự học là chìa khóa duy nhất để duy trì thành công trong"
                    " kỷ nguyên số."
                ),
                "nguon": "Báo VnExpress",
            },
        ],
        "counter": [(
            "Phê phán thói quen ỷ lại, học vẹt, lười suy nghĩ, chờ 'dọn sẵn"
            " mâm' kiến thức từ thầy cô."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ lời căn dặn của Chủ tịch Hồ Chí Minh; giới thiệu vấn"
                " đề nghị luận: Tầm quan trọng của tinh thần tự học đối với học"
                " sinh."
            ),
            "gt": (
                "Giải thích 'tinh thần tự học'; phân tích quan điểm học toàn diện"
                " của Bác Hồ."
            ),
            "bl": (
                "• Luận điểm 1: Tri thức nhân loại vô tận trong khi ghế nhà"
                " trường có hạn, tự học là chìa khóa học suốt đời.\n• Luận"
                " điểm 2: Tự học giúp rèn luyện tư duy độc lập, khả năng thích"
                " ứng linh hoạt."
            ),
            "dc": (
                "• Dẫn chứng 1: Tấm gương tự học của Bác Hồ.\n• Dẫn chứng 2: Tỷ"
                " phú Bill Gates."
            ),
            "pb": (
                "Phê phán thói ỷ lại, học vẹt, lười suy nghĩ, chờ dọn sẵn mâm"
                " kiến thức."
            ),
            "kb": (
                "Khẳng định vai trò của tự học; rút ra bài học hành động cho"
                " học sinh."
            ),
        },
    },
    "Đề 13: Sức mạnh của lời nói tử tế trong giao tiếp": {
        "text": """Ca dao dân gian có câu:
> *\"Lời nói không mất tiền mua / Lựa lời mà nói cho vừa lòng nhau."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của lời nói tử tế và văn hóa ứng xử trong đời sống hiện đại.""",
        "vdnl_chuan": (
            "Sức mạnh của lời nói tử tế và tầm quan trọng của văn hóa ứng xử"
            " trong giao tiếp."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Lời nói tử tế</i> là"
                " những phát ngôn lịch sự, chân thành, mang năng lượng tích"
                " cực sưởi ấm người nghe."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Câu ca dao nhắc nhở: lời"
                " nói là tài sản vô hình không tốn tiền mua nhưng đòi hỏi ý"
                " thức chọn lựa ngôn từ chuẩn mực."
            ),
        ],
        "vdnl_ket_luan": (
            "Sức mạnh của lời nói tử tế và tầm quan trọng của văn hóa ứng xử"
            " trong giao tiếp hiện đại."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao con người đôi khi dễ thốt ra lời cay độc thay vì sự"
                " tử tế?"
            ),
            "y_tra_loi": [
                (
                    "Áp lực cuộc sống và cái tôi ích kỷ khiến con người dễ phóng"
                    " thích sự cáu giận lên người khác."
                ),
                (
                    "Lời nói sắc nhọn có sức sát thương tâm lý sâu sắc; ngược"
                    " lại lời tử tế là liều thuốc chữa lành."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Mô hình 'Quán ăn 0 đồng' cho người nghèo",
                "chi_tiet": (
                    "Nơi người lao động nghèo nhận bữa ăn miễn phí kèm theo"
                    " những lời chào hỏi, cử chỉ tôn trọng ấm áp."
                ),
                "y_nghia": (
                    "Lời nói tử tế và thái độ tôn trọng sưởi ấm những phận đời"
                    " bất hạnh."
                ),
                "nguon": "Báo Thanh Niên",
            },
            {
                "ten": "Dự án 'Tiếng nói tử tế' trên VTV",
                "chi_tiet": (
                    "Lan tỏa những câu chuyện đẹp, lời nói ấm áp giữa người với"
                    " người trong đời sống thường nhật."
                ),
                "y_nghia": (
                    "Khẳng định sức mạnh lan tỏa năng lượng tích cực của sự tử"
                    " tế."
                ),
                "nguon": "Đài Truyền hình Việt Nam (VTV)",
            },
        ],
        "counter": [(
            "Phê phán thói chửi tục, miệt thị, dùng ngôn từ thô lỗ sát thương"
            " tâm lý người khác."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu ca dao dân gian; giới thiệu vấn đề nghị luận:"
                " Sức mạnh của lời nói tử tế và văn hóa ứng xử."
            ),
            "gt": (
                "Giải thích 'lời nói tử tế'; làm rõ triết lý 'lựa lời mà nói"
                " cho vừa lòng nhau'."
            ),
            "bl": (
                "• Luận điểm 1: Lời nói không mất tiền mua nhưng có sức mạnh"
                " sát thương hoặc chữa lành tâm hồn.\n• Luận điểm 2: Văn hóa ứng"
                " xử lịch sự tạo nên sự gắn kết văn minh trong cộng đồng."
            ),
            "dc": (
                "• Dẫn chứng 1: Mô hình Quán ăn 0 đồng.\n• Dẫn chứng 2: Dự án"
                " Tiếng nói tử tế trên VTV."
            ),
            "pb": (
                "Phê phán thói chửi tục, dùng ngôn từ thô lỗ sát thương người"
                " khác."
            ),
            "kb": (
                "Khẳng định giá trị của lời nói tử tế; rút ra bài học giao tiếp"
                " cho bản thân."
            ),
        },
    },
    "Đề 14: Vai trò của tính tự lập trong hành trình trưởng thành": {
        "text": """Có ý kiến cho rằng: *"Chim non muốn bay cao phải tự vẫy đôi cánh của chính mình."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về vai trò của tính tự lập đối với bạn trẻ trong hành trình bước vào đời.""",
        "vdnl_chuan": (
            "Vai trò và ý nghĩa của tính tự lập trong hành trình trưởng thành"
            " của tuổi trẻ."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Tính tự lập</i> là"
                " khả năng tự chủ trong sinh hoạt, suy nghĩ và quyết định cuộc"
                " đời bằng chính sức lực của mình."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Hình ảnh ẩn dụ 'chim non'"
                " và 'đôi cánh chính mình' khẳng định quy luật trưởng thành:"
                " muốn bay cao phải tự vươn lên bằng đôi chân của mình."
            ),
        ],
        "vdnl_ket_luan": (
            "Vai trò và ý nghĩa quyết định của tính tự lập trong hành trình"
            " trưởng thành của tuổi trẻ."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao hội chứng ỷ lại vào gia đình lại là nỗi trăn trở lớn"
                " của thế hệ trẻ?"
            ),
            "y_tra_loi": [
                (
                    "Sự bao bọc quá mức của cha mẹ tước đi cơ hội va vấp, tự"
                    " chịu trách nhiệm của con cái."
                ),
                (
                    "Tự lập là chiếc vé thông hành duy nhất giúp người trẻ đứng"
                    " vững trên đôi chân của mình."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Lối sống tự lập của thanh niên các nước phát triển",
                "chi_tiet": (
                    "Từ 18 tuổi, thanh niên chủ động đi làm thêm trang trải học"
                    " phí, tự thuê nhà và tự quyết định tương lai."
                ),
                "y_nghia": (
                    "Bài học về tinh thần tự lập giúp trưởng thành vững vàng"
                    " trước giông bão."
                ),
                "nguon": "Báo Dân Trí",
            },
            {
                "ten": "Tấm gương khởi nghiệp tự lực của các doanh nhân trẻ",
                "chi_tiet": (
                    "Nhiều bạn trẻ tay trắng lập nghiệp, tự mình vượt qua muôn"
                    " vàn thất bại để xây dựng sự nghiệp thành công."
                ),
                "y_nghia": (
                    "Minh chứng rõ nét cho bản lĩnh tự lập của tuổi trẻ."
                ),
                "nguon": "Báo Thanh Niên",
            },
        ],
        "counter": [(
            "Phê phán thói quen 'công tử bột', 'bám váy mẹ', lười biếng, ỷ lại"
            " mọi thứ vào cha mẹ."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ hình ảnh chim non tập bay; giới thiệu vấn đề nghị"
                " luận: Vai trò của tính tự lập trong hành trình trưởng thành."
            ),
            "gt": (
                "Giải thích 'tính tự lập'; làm rõ ý nghĩa hình ảnh 'vẫy đôi cánh"
                " của chính mình'."
            ),
            "bl": (
                "• Luận điểm 1: Tự lập giúp người trẻ rèn luyện bản lĩnh, khả"
                " năng thích ứng trước mọi hoàn cảnh.\n• Luận điểm 2: Sự bao"
                " bọc thái quá của gia đình tước đi cơ hội trưởng thành của con"
                " cái."
            ),
            "dc": (
                "• Dẫn chứng 1: Lối sống tự lập của thanh niên quốc tế.\n• Dẫn"
                " chứng 2: Tấm gương lập nghiệp tự thân."
            ),
            "pb": (
                "Phê phán thói quen 'công tử bột', ỷ lại vào cha mẹ."
            ),
            "kb": (
                "Khẳng định giá trị của tính tự lập; rút ra bài học hành động"
                " cho học sinh."
            ),
        },
    },
    "Đề 15: Sức mạnh to lớn của tinh thần đoàn kết": {
        "text": """Chủ tịch Hồ Chí Minh từng đúc kết chân lý lịch sử:
> *"Đoàn kết, đoàn kết, đại đoàn kết / Thành công, thành công, đại thành công."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của tinh thần đoàn kết trong việc vượt qua thử thách.""",
        "vdnl_chuan": (
            "Sức mạnh to lớn của tinh thần đoàn kết trong việc tạo nên sức"
            " mạnh tập thể."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Đoàn kết</i> là sự"
                " gắn kết, đồng lòng, thống nhất ý chí và hành động giữa các"
                " cá nhân để hướng đến mục tiêu chung."
            ),
            (
                "<b>2. Phân tích ý nghĩa ngữ liệu:</b> Lời huấn thị của Bác Hồ"
                " khẳng định quy luật tất yếu: đoàn kết là cội nguồn của mọi"
                " thành công lớn lao."
            ),
        ],
        "vdnl_ket_luan": (
            "Sức mạnh to lớn của tinh thần đoàn kết trong việc vượt qua nghịch"
            " cảnh và xây dựng đất nước."
        ),
        "questions": [{
            "cau_hoi": (
                "Vì sao đoàn kết luôn là vũ khí tối thượng của dân tộc Việt"
                " Nam qua các thời kỳ?"
            ),
            "y_tra_loi": [
                (
                    "Lịch sử dựng nước và giữ nước luôn đối mặt với thiên tai và"
                    " giặc ngoại xâm; chỉ đoàn kết mới tạo thành bức tường"
                    " thành bất bại."
                ),
                (
                    "Đoàn kết nhân đôi sức mạnh, biến điều không thể thành có"
                    " thể."
                ),
            ],
        }],
        "evidence": [
            {
                "ten": "Tinh thần chống đại dịch Covid-19 toàn dân",
                "chi_tiet": (
                    "Hàng triệu trái tim hướng về tuyến đầu, các cây ATM gạo,"
                    " siêu thị 0 đồng ra đời từ sự chung tay của toàn xã hội."
                ),
                "y_nghia": (
                    "Minh chứng hùng hồn cho sức mạnh đại đoàn kết dân tộc"
                    " trong hoạn nạn."
                ),
                "nguon": "Báo Nhân Dân",
            },
            {
                "ten": "Công tác cứu trợ đồng bào vùng lũ lụt bão Yagi",
                "chi_tiet": (
                    "Cả nước hướng về miền Bắc với hàng ngàn chuyến xe cứu trợ"
                    " và sự sẻ chia nghĩa tình đồng bào."
                ),
                "y_nghia": (
                    "Truyền thống đoàn kết, tương thân tương ái ngàn đời của dân"
                    " tộc."
                ),
                "nguon": "VTV Digital",
            },
        ],
        "counter": [(
            "Phê phán tư tưởng cục bộ, ích kỷ, chia rẽ bè phái làm suy yếu sức"
            " mạnh tập thể."
        )],
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ câu nói lịch sử của Bác Hồ; giới thiệu vấn đề nghị"
                " luận: Sức mạnh to lớn của tinh thần đoàn kết."
            ),
            "gt": (
                "Giải thích 'đoàn kết'; phân tích ý nghĩa chân lý 'đại đoàn kết"
                " - đại thành công'."
            ),
            "bl": (
                "• Luận điểm 1: Đoàn kết nhân đôi sức mạnh, giúp vượt qua mọi"
                " nghịch cảnh thiên tai, giặc giã.\n• Luận điểm 2: Đoàn kết tạo"
                " nên sức mạnh vô địch của một tập thể, một quốc gia."
            ),
            "dc": (
                "• Dẫn chứng 1: Tinh thần chống dịch Covid-19.\n• Dẫn chứng 2:"
                " Công tác cứu trợ đồng bào lũ lụt."
            ),
            "pb": (
                "Phê phán tư tưởng cục bộ, ích kỷ, chia rẽ bè phái."
            ),
            "kb": (
                "Khẳng định giá trị của tinh thần đoàn kết; rút ra bài học hành"
                " động cho thế hệ trẻ."
            ),
        },
    },
}

DE_BAI_NANG_CAO = {
    "Đề 16: Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực số đông.""",
        "vdnl_chuan": (
            "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực"
            " của đám đông."
        ),
        "explain_guide": (
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            (
                "<b>1. Giải thích từ khóa trong VĐNL:</b> <i>Bản sắc riêng</i> là"
                " cá tính độc đáo; <i>chính kiến</i> là tư duy độc lập làm nên"
                " phẩm giá cá nhân."
            ),
            (
                "<b>2. Phân tích ý nghĩa ý kiến:</b> Hình ảnh ẩn dụ 'con sông' và"
                " 'ghềnh thác' tượng trưng cho thử thách; đòi hỏi bản lĩnh giữ"
                " vững dòng chảy cá nhân trước áp lực hòa tan."
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
        "dani_chi_tiet": {
            "mb": (
                "Dẫn dắt từ hình ảnh dòng sông chảy ra biển lớn; giới thiệu vấn"
                " đề nghị luận: Bản lĩnh giữ gìn bản sắc riêng và chính kiến"
                " trước áp lực số đông."
            ),
            "gt": (
                "Cắt nghĩa 'bản sắc riêng', 'chính kiến'; giải mã hình ảnh 'con"
                " sông', 'ghềnh thác'."
            ),
            "bl": (
                "• Luận điểm 1: Giữ bản sắc giúp khẳng định giá trị cá nhân độc"
                " lập.\n• Luận điểm 2: Áp lực đám đông và tâm lý bầy đàn dễ bóp"
                " nghẹt tư duy phản biện."
            ),
            "dc": (
                "Dẫn chứng về vận động viên Nguyễn Thị Oanh kiên định chiến"
                " thuật riêng giành HCV."
            ),
            "pb": (
                "Phê phán thói hùa theo phong trào vô thức hoặc biến sự khác"
                " biệt thành ngông cuồng cực đoan."
            ),
            "kb": (
                "Khẳng định tầm quan trọng của bản lĩnh cá nhân; rút ra bài học"
                " tu dưỡng trong thời đại số."
            ),
        },
    }
}

KHO_DAN_CHUNG_8_CHU_DIEM = {
    "1. Trách nhiệm, Cống hiến & Phụng sự cộng đồng": [
        {
            "ten": "Hoàng Hoa Trung & Dự án 'Nuôi Em'",
            "noi_dung": (
                "Kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao"
                " khó khăn."
            ),
            "nguon": "Báo Tuổi Trẻ, Trung ương Đoàn",
        },
        {
            "ten": "Đội cứu trợ thiện nguyện 'SOS Vũng Tàu'",
            "noi_dung": (
                "Hàng chục thành viên tự nguyện vá đường, hỗ trợ sửa xe và cấp"
                " cứu người tai nạn đêm hôm hoàn toàn miễn phí."
            ),
            "nguon": "Báo Thanh Niên",
        },
    ],
    "2. Thấu cảm, Lắng nghe & Tử tế": [
        {
            "ten": "TS. Đặng Hoàng Giang & 'Tổng đài Ngày Mai'",
            "noi_dung": (
                "Tổng đài tham vấn tâm lý phi lợi nhuận hỗ trợ tinh thần cho người"
                " trẻ khủng hoảng."
            ),
            "nguon": "Báo Thanh Niên, VTV",
        },
        {
            "ten": "Cây ATM gạo miễn phí trong đại dịch Covid-19",
            "noi_dung": (
                "Sáng kiến của Hoàng Tuấn Anh giúp hàng triệu người nghèo vượt"
                " qua cơn hoạn nạn ngặt nghèo."
            ),
            "nguon": "Báo Nhân Dân",
        },
    ],
    "3. Giữ gìn Bản sắc văn hóa & Di sản dân tộc": [
        {
            "ten": "Dự án phục dựng cổ phục 'Đại Việt Cổ Phong'",
            "noi_dung": (
                "Gen Z nghiên cứu, phục dựng chuẩn xác cổ phục Triều Nguyễn,"
                " Lê ứng dụng vào đời sống."
            ),
            "nguon": "Báo VnExpress",
        },
        {
            "ten": "Nghệ sĩ nhân dân Thanh Hải & Âm nhạc Cung đình Huế",
            "noi_dung": (
                "Cả đời miệt mài gìn giữ, truyền dạy nhã nhạc cung đình Huế cho"
                " thế hệ trẻ."
            ),
            "nguon": "Báo Văn Hóa",
        },
    ],
    "4. Bản lĩnh trước đám đông & Tư duy độc lập": [
        {
            "ten": "Nhà bác học Galileo Galilei",
            "noi_dung": (
                "Kiên cường bảo vệ chân lý thuyết Nhật tâm trước tòa án dị giáo"
                " Trung cổ."
            ),
            "nguon": "Lịch sử Khoa học thế giới",
        },
        {
            "ten": "Thiếu niên anh hùng Cù Huy Cận",
            "noi_dung": (
                "Bản lĩnh bảo vệ chính kiến và con đường học tập sáng tạo trước"
                " định kiến thời đại."
            ),
            "nguon": "Tư liệu Lịch sử Việt Nam",
        },
    ],
    "5. Dũng cảm, Vượt khó & Kiên trì": [
        {
            "ten": "VĐV Nguyễn Thị Oanh (SEA Games 32)",
            "noi_dung": (
                "Vượt qua lịch thi đấu khắc nghiệt cách nhau 20 phút giành 2 HCV"
                " điền kinh."
            ),
            "nguon": "Báo Thể thao & Văn hóa",
        },
        {
            "ten": "Thầy giáo mất đôi tay Nguyễn Ngọc Ký",
            "noi_dung": (
                "Kiên trì dùng chân tập viết, vượt qua nghịch cảnh nghiệt ngã để"
                " trở thành nhà giáo ưu tú."
            ),
            "nguon": "Báo Giáo dục & Thời đại",
        },
    ],
    "6. Tự học, Thích ứng & Tri thức thời đại AI": [
        {
            "ten": "Chủ tịch Hồ Chí Minh - Tấm gương tự học vĩ đại",
            "noi_dung": (
                "Tự học thông thạo hơn 10 ngoại ngữ khi bôn ba tìm đường cứu"
                " nước."
            ),
            "nguon": "Tư liệu Lịch sử Đảng",
        },
        {
            "ten": "GS. Ngô Bảo Châu",
            "noi_dung": (
                "Tinh thần tự nghiên cứu toán học đỉnh cao, giành giải thưởng"
                " Fields danh giá."
            ),
            "nguon": "Báo Khoa Học Phát Triển",
        },
    ],
    "7. Bảo vệ Môi trường & Lối sống xanh": [
        {
            "ten": "Nhóm tình nguyện 'Sài Gòn Xanh'",
            "noi_dung": (
                "Dầm mình dưới các kênh rạch ô nhiễm vớt hàng chục tấn rác trả"
                " lại nguồn nước sạch."
            ),
            "nguon": "VTV1, Báo Tuổi Trẻ",
        },
        {
            "ten": "Hành trình 'Green Generation' của giới trẻ",
            "noi_dung": (
                "Phong trào sống không rác thải nhựa, đổi rác lấy cây xanh lan"
                " tỏa mạnh mẽ trường học."
            ),
            "nguon": "Báo Môi Trường & Đời Sống",
        },
    ],
    "8. Lòng biết ơn, Khoan dung & Nhân ái": [
        {
            "ten": "Chính sách Khoan hồng và Đặc xá của Nhà nước",
            "noi_dung": (
                "Trao cơ hội đặc xá cho phạm nhân cải tạo tốt dịp 2/9 làm lại cuộc"
                " đời."
            ),
            "nguon": "Báo Nhân Dân",
        },
        {
            "ten": "Đại đức Thích Minh Phúc & Mái ấm tình thương",
            "noi_dung": (
                "Nhận nuôi hàng trăm trẻ mồ côi bằng tấm lòng bao dung, nhân ái"
                " vô điều kiện."
            ),
            "nguon": "Báo Giác Ngộ",
        },
    ],
}

# ==============================================================================
# 3. QUẢN LÝ SESSION STATE
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
          "Chào em! Cô là Trợ lý Ngữ văn. Em có thắc mắc gì về phương pháp lập"
          " dàn ý hay chọn dẫn chứng cứ hỏi cô nhé!"
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
    st.success("✅ Trợ lí Ngữ văn đã sẵn sàng")
  else:
    st.warning("⚠️ Vui lòng nhập API Key để kích hoạt AI.")

  st.markdown("---")
  st.markdown("### 📌 4 BƯỚC SƯ PHẠM")
  st.write("1. **🌱 Bước 1:** Phân tích đề & VĐNL")
  st.write("2. **🧵 Bước 2:** Lập dàn ý & Kho dẫn chứng")
  st.write("3. **✍️ Bước 3:** Xưởng viết độc lập")
  st.write("4. **🔍 Bước 4:** AI Chấm điểm Rubric")


def call_gemini_engine(prompt_text):
  api_key = st.session_state.get("gemini_api_key", "").strip()
  if not api_key:
    return "Cô chưa nhận được API Key. Thầy/cô vui lòng cấu hình API Key nhé!"
  try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_text)
    if response and response.text:
      return response.text
    return "Cô đang suy nghĩ, các em hãy bấm gửi lại nhé!"
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
  "explain_guide": "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ liệu/ý kiến -> Chốt vấn đề.",
  "explain_items": ["1. Giải thích từ khóa trong VĐNL: Cắt nghĩa...", "2. Phân tích ý nghĩa ngữ liệu: ..."],
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
            "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
            " liệu/ý kiến -> Chốt vấn đề."
        ),
        "explain_items": [
            "1. Giải thích từ khóa trong VĐNL: Cắt nghĩa bản chất khái niệm."
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
        f"#### 🛠️ Gợi ý khung tư duy cho: <span"
        f" style='color:#2563eb;'>{cur_de_key}</span>",
        unsafe_allow_html=True,
    )

    # Thao tác 1: Giải thích
    with st.expander(
        "📌 Thao tác 1: Giải thích bản chất khái niệm / nhận định", expanded=True
    ):
      guide_txt = cur_de_info.get(
          "explain_guide",
          "Định hướng: Giải thích từ khóa VĐNL trước -> Phân tích ý nghĩa ngữ"
          " liệu/ý kiến -> Chốt vấn đề.",
      )
      items = cur_de_info.get("explain_items", [])
      vdnl_kl = cur_de_info.get(
          "vdnl_ket_luan", cur_de_info.get("vdnl_chuan", "")
      )

      items_html = ""
      for itm in items:
        items_html += f"<p style='margin-bottom: 10px;'>• {itm}</p>"

      st.markdown(
          f"""
            <div class='explain-box-clean'>
                <p style='margin:0 0 10px 0; font-style:italic; color:#475569;'><i>{guide_txt}</i></p>
                <div style='margin:0 0 12px 0;'>
                    {items_html}
                </div>
                <p style='margin:0; font-weight:700; color:#166534;'>
                    👉 Chốt lại Vấn đề nghị luận (VĐNL): <span style='font-weight:normal; font-style:italic;'>{vdnl_kl}</span>
                </p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    # Thao tác 2: Bàn luận
    with st.expander(
        "💡 Thao tác 2: Bàn luận trọng tâm (Hệ thống ý sâu sắc, đa chiều)",
        expanded=True,
    ):
      for q in cur_de_info.get("questions", []):
        st.markdown(f"**❓ {q['cau_hoi']}**")
        for ans in q.get("y_tra_loi", []):
          st.markdown(f"  * {ans}")

    # Thao tác 3: Dẫn chứng
    with st.expander(
        "📚 Thao tác 3: Kho dẫn chứng trọng tâm & Dẫn chứng mở rộng",
        expanded=True,
    ):
      st.markdown(
          "##### 📌 Dẫn chứng thực tế tường minh cho đề bài đang chọn:"
      )
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
      st.markdown(
          "##### 📚 🔍 Tra cứu thêm Kho dẫn chứng mở rộng (8 nhóm chủ điểm):"
      )
      st.info(
          "👉 *Mẹo nhỏ:* Các em có thể bấm vào hộp chọn bên dưới để mở rộng thêm"
          " nhiều nhóm dẫn chứng thực tế phong phú khác cho bài văn của mình!"
      )
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

    # Thao tác 4: Phản biện
    with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng", expanded=False):
      for c in cur_de_info.get("counter", []):
        st.markdown(f"- {c}")

  with c_right:
    st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
    with st.container(border=True):
      st.info(
          "💡 **Nguyên tắc:** Trợ lý Ngữ văn **không viết hộ / làm hộ bài văn**,"
          " chỉ đặt câu hỏi gợi mở để giúp các em tự tư duy."
      )

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

Hãy trả lời định hướng ngắn gọn (3–5 câu), bám sát đúng đề bài này và đặt câu hỏi gợi mở tư duy cho học sinh:
"""
      with st.spinner("Trợ lý Ngữ văn đang định hướng..."):
        reply = call_gemini_engine(prompt_chat)
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": reply}
        )
      st.rerun()

# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
  st.markdown(
      '<div class="section-title">✍️ Xưởng Viết Bài Độc Lập</div>',
      unsafe_allow_html=True,
  )
  st.info(
      "💡 *Dựa vào hệ thống gợi ý ở Bước 2, các em hãy tự tay viết bài văn hoàn"
      " chỉnh của mình vào đây nhé!*"
  )
  essay_in = st.text_area(
      "Nhập bài viết của em:",
      value=st.session_state.get("user_essay", ""),
      height=380,
      placeholder="Viết bài văn nghị luận hoàn chỉnh...",
  )
  st.session_state["user_essay"] = essay_in

# ------------------------------------------------------------------------------
# BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ RUBRIC
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
# HỒ SƠ BÀI LÀM
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
