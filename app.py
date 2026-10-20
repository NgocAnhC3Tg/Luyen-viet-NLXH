import streamlit as st
import json
import re
from google import genai
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH THIẾT KẾ GIAO DIỆN CAO CẤP (ADVANCED CSS & COLORFUL STATIONS)
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
        padding: 30px 35px;
        border-radius: 18px;
        color: white;
        box-shadow: 0 12px 24px -5px rgba(15, 23, 42, 0.2);
        margin-bottom: 25px;
    }
    
    .hero-title {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 6px !important;
        color: #ffffff !important;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #93c5fd;
        margin: 0;
    }

    /* 4 Thanh Màu Nổi Bật Cho 4 Bước Học Tập */
    .step-header-1 {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 12px 22px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
        display: flex;
        align-items: center;
    }

    .step-header-2 {
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 12px 22px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }

    .step-header-3 {
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 12px 22px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
    }

    .step-header-4 {
        background: linear-gradient(90deg, #8b5cf6 0%, #6d28d9 100%);
        color: white;
        padding: 12px 22px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.25);
    }

    .step-header-5 {
        background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
        color: white;
        padding: 12px 22px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
    }

    /* Tối ưu hóa Tabs chính nổi bật */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 8px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #cbd5e1;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        color: #475569;
        padding: 0 18px;
    }

    .stTabs [aria-selected="true"] {
        background: #1e3a8a !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3) !important;
    }

    /* Card thông tin */
    .custom-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. NGÂN HÀNG ĐỀ THI VÀ DỮ LIỆU
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

KHO_DAN_CHUNG = {
    "1. Lòng nhân ái – Trách nhiệm cộng đồng": [
        {"nv": "Trưởng thôn Ma Seo Chứ (Lào Cai)", "nd": "Trong cơn bão số 3 (Yagi) năm 2024, bằng linh cảm nhạy bén và tinh thần trách nhiệm, anh đã di dời 115 người dân thôn Kho Vàng lên núi dựng lán trú ẩn an toàn trước khi sạt lở san phẳng làng xóm.", "nguon": "Báo Dân Trí, VTV (09/2024)"},
        {"nv": "Bé Nguyễn Hải An (7 tuổi)", "nd": "Trước khi qua đời vì bệnh hiểm nghèo, bé và mẹ đã tình nguyện hiến tặng giác mạc mang lại ánh sáng cho 2 người khác, lan tỏa làn sóng đăng ký hiến tạng rộng khắp.", "nguon": "Báo VnExpress (2018)"}
    ],
    "2. Ý chí – Nghị lực – Vượt nghịch cảnh": [
        {"nv": "Vận động viên Derek Redmond", "nd": "Bị rách gân khoeo gục ngã trên đường chạy bán kết 400m Olympic 1992, anh kiên quyết đứng dậy bước từng bước khập khiễng về đích trong sự nể phục của cả khán đài.", "nguon": "Olympic Channel"}
    ]
}

# ==============================================================================
# 3. KẾT NỐI GEMINI AI & SESSION STATE
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "last_selected_de" not in st.session_state:
    st.session_state["last_selected_de"] = ""

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
        st.info("💡 Hệ thống đang dùng Key ẩn (Secrets) hoặc chờ bạn dán Key.")

    st.markdown("---")
    st.markdown("### 📌 LỘ TRÌNH 4 BƯỚC")
    st.write("1. **🌱 Bước 1:** Phân tích đề")
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
Bạn là Giám khảo Ngữ văn THPT GDPT 2018. Đề bài: {exam_text}. Đáp án VĐNL: {vdnl_chuan}. Học sinh trả lời: "{student_guess}".
Trả về JSON:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét ngắn gọn xưng cô-em",
  "suggested_fix": "{vdnl_chuan}"
}}
"""
    raw = call_gemini_engine(prompt)
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw)
    except Exception:
        return {"status": "LECH", "feedback": "Em hãy kiểm tra lại từ khóa chính trong đề.", "suggested_fix": vdnl_chuan}

# ==============================================================================
# 4. GIAO DIỆN CHÍNH (HERO BANNER & TABS NỔI BẬT)
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
    st.markdown('<div class="step-header-1">🌱 BƯỚC 1: ĐỌC KỸ ĐỀ BÀI & XÁC ĐỊNH VẤN ĐỀ NGHỊ LUẬN CỐT LÕI</div>', unsafe_allow_html=True)
    
    col_de1, col_de2 = st.columns([1, 2], gap="medium")
    with col_de1:
        muc_do_de = st.radio("Dạng đề thi:", ["Đề cơ bản", "Đề nâng cao"], index=0)
        filtered_de_keys = [k for k in DE_BAI_DATA.keys() if ("(Nâng cao)" if muc_do_de == "Đề nâng cao" else "(Cơ bản)") in k]
        selected_de_key = st.selectbox("Chọn đề bài:", filtered_de_keys)
        kiem_tra_va_reset_khi_doi_de(selected_de_key)
        de_info = DE_BAI_DATA[selected_de_key]
        
    with col_de2:
        with st.container(border=True):
            st.markdown("##### 📖 Đề bài đã chọn:")
            st.info(de_info['text'].replace("**", ""))
            
    st.markdown("---")
    student_vdnl = st.text_input("⚡ Thao tác học sinh: Xác định Vấn đề nghị luận cốt lõi của đề trên:", placeholder="Gõ câu trả lời của em ở đây...")
    
    if st.button("🔍 Kiểm tra Vấn đề Nghị luận với AI", type="primary"):
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
    st.session_state["current_de_key"] = selected_de_key

# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý & LẬP DÀN Ý
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="step-header-2">🧵 BƯỚC 2: XÂY DỰNG HỆ THỐNG LUẬN ĐIỂM & TỰ HOÀN THIỆN DÀN Ý</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="step-header-3">✍️ BƯỚC 3: XƯỞNG VIẾT ĐỘC LẬP (DUNG LƯỢNG 600 - 1000 CHỮ)</div>', unsafe_allow_html=True)
    c_v1, c_v2 = st.columns([1.3, 0.7], gap="medium")
    with c_v1:
        essay_in = st.text_area("✍️ Nhập bài văn hoàn chỉnh của em:", value=st.session_state.get("user_essay", ""), height=400)
        st.session_state["user_essay"] = essay_in
        w_cnt = len(essay_in.strip().split()) if essay_in.strip() else 0
        st.metric("Số từ đã viết", f"{w_cnt} chữ", delta="Đạt chuẩn" if 600 <= w_cnt <= 1000 else "Cần 600-1000 chữ")

    with c_v2:
        st.markdown("##### 💡 Dàn ý đối chiếu:")
        st.info(st.session_state.get("user_outline", "Chưa có dàn ý."))

# ------------------------------------------------------------------------------
# BƯỚC 4: CHỈNH SỬA & ĐÁNH GIÁ
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="step-header-4">🔍 BƯỚC 4: GIÁM KHẢO AI CHẤM ĐIỂM THEO BẢNG RUBRIC 10 ĐIỂM</div>', unsafe_allow_html=True)
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
# HỒ SƠ BÀI LÀM (SỬA HOÀN TOÀN LỖI HIỂN THỊ JSON)
# ------------------------------------------------------------------------------
with tabs[4]:
    st.markdown('<div class="step-header-5">📁 HỒ SƠ BÀI LÀM & TỔNG KẾT TIẾN TRÌNH HỌC TẬP</div>', unsafe_allow_html=True)
    
    student_name = st.text_input("Họ và tên học sinh:", placeholder="Ví dụ: Nguyễn Văn An - Lớp 12A1")
    
    current_de = st.session_state.get("current_de_key", "Chưa chọn đề bài")
    user_outline = st.session_state.get("user_outline", "Chưa lập dàn ý")
    user_essay = st.session_state.get("user_essay", "Chưa viết bài")
    grading_result = st.session_state.get("grading_result", "Chưa thực hiện chấm điểm ở Bước 4")
    
    # Tạo văn bản báo cáo chuẩn sư phạm
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
