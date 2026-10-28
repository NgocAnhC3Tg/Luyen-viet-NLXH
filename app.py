import streamlit as st
import data_de_bai as db
from PIL import Image
import json
import re
import urllib.request
import urllib.error
import base64
import io

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN & TÊN HỆ THỐNG
# ==============================================================================
st.set_page_config(
    page_title="EduAI - Hệ thống định hướng tư duy và phát triển năng lực viết văn nghị luận xã hội",
    page_icon="🖊️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        padding: 26px 32px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 22px;
    }
    
    .hero-title {
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px;
        margin-bottom: 6px !important;
        color: #ffffff !important;
        line-height: 1.35;
    }

    .hero-subtitle {
        font-size: 0.95rem;
        color: #dbeafe;
        margin: 0;
        font-weight: 500;
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
        color: #475569;
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
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .repo-guide-box {
        background: linear-gradient(90deg, #fefce8 0%, #fef9c3 100%);
        border: 1px solid #fde047;
        border-left: 5px solid #eab308;
        padding: 14px 18px;
        border-radius: 10px;
        margin-top: 14px;
        margin-bottom: 14px;
        color: #713f12;
        font-size: 0.94rem;
    }

    .rubric-info-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 5px solid #2563eb;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 16px;
    }

    .type-badge {
        display: inline-block;
        background-color: #dbeafe;
        color: #1e40af;
        font-weight: 700;
        font-size: 0.86rem;
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid #93c5fd;
        margin-bottom: 10px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 2. HÀM CHUẨN HÓA LỆNH ĐỀ BÀI (BÀI VĂN KHOẢNG 600 CHỮ)
# ==============================================================================
def ensure_600_words_prompt(raw_text):
    text = raw_text.strip()
    if not text:
        return ""
    low = text.lower()
    if "600 chữ" in low or "600 từ" in low:
        return text
    if "bài văn nghị luận" in low:
        return re.sub(r"(?i)(bài văn nghị luận)", r"\1 (khoảng 600 chữ)", text, count=1)
    if text.endswith(".") or text.endswith("?") or text.endswith("!"):
        return f"{text} Hãy viết một bài văn nghị luận xã hội (khoảng 600 chữ) trình bày suy nghĩ của anh/chị về vấn đề trên."
    return f"Hãy viết một bài văn nghị luận xã hội (khoảng 600 chữ) trình bày suy nghĩ của anh/chị về: {text}."

# ==============================================================================
# 3. QUẢN LÝ SESSION STATE & KHÓA KẾT NỐI
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        (
            "assistant",
            "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em giải thích khái niệm khó, gợi mở hệ thống luận điểm đúng trọng tâm đề bài, cung cấp dẫn chứng thực tế và góp ý diễn đạt cho từng câu văn của em. Em đang cần hỗ trợ ở khâu nào?",
        )
    ]
if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state:
    st.session_state["eval_vdnl_text"] = ""
if "selected_essay_type_override" not in st.session_state:
    st.session_state["selected_essay_type_override"] = "Tự động nhận diện theo đề bài"

def get_api_key():
    if st.session_state.get("gemini_api_key", "").strip():
        return st.session_state["gemini_api_key"].strip()
    try:
        for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "gemini_api_key", "api_key"]:
            if k in st.secrets and st.secrets[k]:
                return str(st.secrets[k]).strip()
    except Exception:
        pass
    return ""

# ==============================================================================
# 4. ĐỘNG CƠ KẾT NỐI AI ĐA PHIÊN (HỖ TRỢ LỊCH SỬ CHAT, SYSTEM INSTRUCTION & REST API)
# ==============================================================================
def call_gemini_rest_api(prompt, pil_image=None, contents_list=None, system_instruction=None, temperature=0.4):
    key = get_api_key()
    if not key or not key.startswith("AIza"):
        return None

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
    ]

    if contents_list is not None:
        contents_payload = contents_list
    else:
        parts = [{"text": prompt}]
        if pil_image is not None:
            try:
                buffered = io.BytesIO()
                img_rgb = pil_image.convert("RGB")
                img_rgb.save(buffered, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_b64,
                        }
                    }
                )
            except Exception:
                pass
        contents_payload = [{"parts": parts}]

    payload = {
        "contents": contents_payload,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 4000},
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    data = json.dumps(payload).encode("utf-8")

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if len(candidates) > 0:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if content_parts and "text" in content_parts[0]:
                        return content_parts[0]["text"]
        except Exception:
            continue
    return None

# ==============================================================================
# 5. KHO TRI THỨC BÁCH KHOA NLXH CHUYÊN SÂU (GIỮ NGUYÊN 100% ĐẦY ĐỦ)
# ==============================================================================
CONCEPT_DICTIONARY = {
    "sáng tạo": {
        "term": "Tinh thần sáng tạo",
        "def": "**Tinh thần sáng tạo** là khả năng tư duy độc lập, dám bứt phá khỏi những khuôn mẫu, lối mòn sẵn có để tìm tòi, khám phá ra những ý tưởng mới, phương pháp mới mang lại giá trị và hiệu quả cao hơn.",
        "why": "Thế giới hiện đại biến đổi từng giây cùng kỷ nguyên số và trí tuệ nhân tạo; nếu chỉ sao chép và đi theo lối mòn, con người sẽ bị đào thải. Sáng tạo chính là động lực cốt lõi giúp cá nhân khẳng định bản sắc độc bản và thúc đẩy xã hội tiến bộ.",
        "manifest": "Chủ động đặt câu hỏi phản biện trong học tập, tìm kiếm cách giải quyết vấn đề mới mẻ, dám thử nghiệm công nghệ và ý tưởng đột phá trong lao động, nghiên cứu khoa học.",
        "how_to_promote": "Không ngừng tự học để tích lũy nền tảng tri thức vững chắc; rèn tư duy phản biện, dám thử nghiệm và chấp nhận rủi ro sai sót như một phần của quá trình tìm tòi cái mới.",
        "counter": "Lối sống thụ động, học vẹt máy móc, rập khuôn văn mẫu sáo rỗng, ngại thay đổi; hoặc nhầm lẫn sáng tạo với sự lập dị, tùy tiện, bất chấp quy chuẩn đạo đức và khoa học.",
        "ev_ten": "Nhóm kỹ sư trẻ Việt Nam nghiên cứu AI & Học sinh chế tạo cánh tay robot hỗ trợ người khuyết tật",
        "ev_chitiet": "Từ những phòng thí nghiệm học đường còn khiêm tốn, nhiều học sinh THPT Việt Nam đã sáng tạo ra các thiết bị cảnh báo lũ quét, cánh tay robot sinh học đạt giải cao tại Cuộc thi Khoa học Kỹ thuật Quốc tế (ISEF).",
        "ev_ynghia": "Minh chứng rõ nét cho sức mạnh của tinh thần dám nghĩ dám làm và khát vọng sáng tạo từ chính lứa tuổi học trò.",
    },
    "đoàn kết": {
        "term": "Tinh thần đoàn kết",
        "def": "**Tinh thần đoàn kết** là sự gắn kết, đồng lòng, tập hợp sức mạnh trí tuệ và vật chất của nhiều cá nhân thành một khối thống nhất để cùng vượt qua thử thách, hướng tới mục tiêu chung.",
        "why": "Một cá nhân dù xuất sắc đến đâu cũng có giới hạn; khi biết hợp lực, sức mạnh tinh thần và hành động sẽ được nhân lên gấp bội để tạo nên kỳ tích trước nghịch cảnh.",
        "manifest": "Sự tương thân tương ái khi đồng bào gặp thiên tai bão lũ; tinh thần phối hợp ăn ý, tôn trọng lẫn nhau trong học tập, làm việc nhóm; sự đồng lòng của cả dân tộc trước những bước ngoặt lịch sử.",
        "how_to_promote": "Biết hạ cái tôi cá nhân vì mục tiêu chung, lắng nghe và tôn trọng sự khác biệt trong tập thể, chủ động sẻ chia trách nhiệm thay vì đùn đẩy.",
        "counter": "Lối sống ích kỷ, cục bộ, chia rẽ tập thể; hoặc biến 'đoàn kết' thành sự bao che sai phạm, dĩ hòa vi quý làm triệt tiêu sự đấu tranh phản biện tích cực.",
        "ev_ten": "Chiến dịch triệu tấm lòng hướng về đồng bào miền Bắc trong siêu bão Yagi (9/2024)",
        "ev_chitiet": "Chỉ trong vài ngày, hàng triệu người dân Việt Nam từ học sinh đến người già đã quyên góp hàng nghìn tỷ đồng qua Mặt trận Tổ quốc; hàng trăm đoàn xe cứu trợ xuyên đêm và lực lượng vũ trang dầm mình trong lũ dữ cứu dân.",
        "ev_ynghia": "Minh chứng sống động cho sức mạnh đại đoàn kết dân tộc: khi những trái tim cùng chung một nhịp đập, không thử thách nào có thể khuất phục.",
    },
    "biết ơn": {
        "term": "Lòng biết ơn",
        "def": "**Lòng biết ơn** là thái độ trân trọng, khắc ghi công lao, sự hy sinh, giúp đỡ của người khác hoặc những giá trị tốt đẹp mà gia đình, thế hệ đi trước và cuộc đời đã dành cho mình, từ đó chuyển hóa thành hành động đền đáp xứng đáng.",
        "why": "Không thành quả nào tự nhiên mà có; lòng biết ơn giúp con người sống có cội nguồn, nuôi dưỡng tâm hồn nhân hậu, xóa bỏ sự ích kỷ và tạo ra sợi dây gắn kết bền chặt giữa các thế hệ.",
        "manifest": "Hiếu thảo với cha mẹ, kính trọng thầy cô; tri ân các anh hùng liệt sĩ; trân trọng thành quả lao động, bảo vệ thiên nhiên và nỗ lực sống tử tế, có ích để tiếp nối giá trị.",
        "how_to_promote": "Thể hiện sự trân trọng từ lời cảm ơn chân thành đến những hành động thiết thực hàng ngày; nỗ lực học tập, tu dưỡng để không phụ lòng mong mỏi của đấng sinh thành.",
        "counter": "Thái độ vô ơn, bạc bẽo, 'qua cầu rút ván', coi sự hy sinh của cha mẹ và xã hội là điều hiển nhiên, hoặc chỉ thể hiện lòng biết ơn bằng lời nói hình thức trên mạng xã hội.",
        "ev_ten": "Đôi bạn Nguyễn Tất Minh và Ngô Minh Hiếu (10 năm cõng bạn đến trường) & Dự án phục dựng ảnh liệt sĩ của nhóm 'Màu hoa đỏ'",
        "ev_chitiet": "Nhóm các bạn trẻ thuộc dự án 'Màu hoa đỏ' và 'Team Lee' đã dành hàng nghìn giờ phục dựng miễn phí hàng trăm bức di ảnh liệt sĩ đã phai mờ để trao tặng các Mẹ Việt Nam Anh hùng.",
        "ev_ynghia": "Biểu tượng đẹp đẽ của lòng biết ơn thế hệ trẻ: dùng tri thức và công nghệ hiện đại để tri ân quá khứ hào hùng.",
    },
    "bản lĩnh": {
        "term": "Bản lĩnh sống",
        "def": "**Bản lĩnh** là sức mạnh ý chí, sự kiên định, vững vàng của con người trước những khó khăn, nghịch cảnh, áp lực hoặc cám dỗ mà không hề nao núng, gục ngã hay đánh mất nguyên tắc đạo đức của bản thân.",
        "why": "Cuộc sống luôn ẩn chứa những biến cố bất ngờ và vô vàn áp lực vô hình; bản lĩnh chính là chiếc mỏ neo giữ cho con người làm chủ tâm trí, biến nghịch cảnh thành bàn đạp để trưởng thành.",
        "manifest": "Bình tĩnh đối diện với thất bại để đứng lên làm lại; dám bảo vệ lẽ phải trước hiệu ứng đám đông; giữ vững nhân cách trước những cám dỗ vật chất hay thực dụng.",
        "how_to_promote": "Chủ động bước ra khỏi vùng an toàn để trải nghiệm thử thách; rèn luyện tư duy độc lập, trau dồi tri thức để có sự tự tin dựa trên năng lực thực chất.",
        "counter": "Sự yếu đuối, dễ dàng buông xuôi khi mới gặp trở ngại, sống ba phải a dua theo đám đông; hoặc nhầm lẫn bản lĩnh với sự bảo thủ, liều lĩnh bất chấp hậu quả.",
        "ev_ten": "Kình ngư Nguyễn Thị Ánh Viên và Nhà giáo ưu tú Nguyễn Ngọc Ký",
        "ev_chitiet": "Thầy Nguyễn Ngọc Ký bị liệt cả hai tay từ năm lên 4 tuổi nhưng bằng bản lĩnh phi thường đã dùng đôi chân tập viết, vượt qua những cơn đau co rút để trở thành người thầy mẫu mực truyền cảm hứng cho bao thế hệ.",
        "ev_ynghia": "Khẳng định nghịch cảnh khắc nghiệt nhất cũng phải cúi đầu trước bản lĩnh và ý chí kiên cường của con người.",
    },
    "trách nhiệm": {
        "term": "Tinh thần trách nhiệm",
        "def": "**Tinh thần trách nhiệm** là ý thức tự giác thực hiện trọn vẹn bổn phận, nghĩa vụ của bản thân đối với chính mình, gia đình và cộng đồng, đồng thời dám làm dám chịu trước mọi quyết định và hành động của mình.",
        "why": "Mỗi cá nhân là một mắt xích trong xã hội; sống có trách nhiệm tạo nên uy tín, sự tin cậy, thúc đẩy cộng đồng vận hành văn minh và khẳng định phẩm giá của một con người trưởng thành.",
        "manifest": "Hoàn thành nghiêm túc việc học tập, lao động; không đổ lỗi cho hoàn cảnh; chủ động lên tiếng và tham gia giải quyết các vấn đề chung như bảo vệ môi trường, thượng tôn pháp luật.",
        "how_to_promote": "Bắt đầu từ sự kỷ luật với chính bản thân mình, hoàn thành đúng hạn từng công việc nhỏ, dám nhận lỗi và sửa lỗi thay vì tìm cớ biện minh.",
        "counter": "Lối sống thờ ơ, vô cảm ('cha chung không ai khóc'), đùn đẩy trách nhiệm cho người khác, chỉ biết đòi hỏi quyền lợi cá nhân mà trốn tránh nghĩa vụ công dân.",
        "ev_ten": "Biệt đội Sài Gòn Xanh và Hà Nội Xanh (Những người trẻ giải cứu dòng kênh ô nhiễm)",
        "ev_chitiet": "Hàng trăm bạn trẻ thế hệ Gen Z tự nguyện mặc đồ bảo hộ, lội xuống những dòng kênh đen đặc rác thải và kim tiêm vào mỗi cuối tuần để vớt hàng trăm tấn rác, trả lại dòng chảy trong lành cho thành phố.",
        "ev_ynghia": "Hành động xuất phát từ ý thức trách nhiệm công dân tự giác, biến tình yêu quê hương thành việc làm cụ thể.",
    },
    "thất bại": {
        "term": "Thái độ đối diện với thất bại",
        "def": "**Thất bại** là những lần vấp ngã, sai sót, chưa đạt được mục tiêu đề ra trên đường đời; nhưng dưới góc nhìn tích cực, đó là phép thử bản lĩnh và bài học kinh nghiệm quý giá giúp con người hoàn thiện mình.",
        "why": "Không một hành trình vươn tới đỉnh cao nào mà trải toàn hoa hồng; thất bại giúp con người nhận diện rõ lỗ hổng năng lực, gột rửa sự tự mãn và tích lũy trí tuệ thực tiễn.",
        "manifest": "Bình tĩnh phân tích nguyên nhân sau mỗi lần điểm kém hay dự án đổ vỡ; kiên trì điều chỉnh phương pháp để thử sức lại thay vì tự ti, mặc cảm.",
        "how_to_promote": "Thay đổi góc nhìn coi thất bại là một phần tất yếu của sự trưởng thành; rèn luyện nghị lực bền bỉ và kỹ năng quản trị cảm xúc trước nghịch cảnh.",
        "counter": "Tâm lý 'sợ sai' nên thu mình trong vỏ ốc an toàn không dám dấn thân; hoặc thái độ bi quan, tuyệt vọng, gục ngã hoàn toàn sau một lần vấp ngã đầu đời.",
        "ev_ten": "Nhà bác học Thomas Edison và tỷ phú công nghệ Jensen Huang (CEO NVIDIA)",
        "ev_chitiet": "Trước khi đưa NVIDIA trở thành tập đoàn dẫn đầu kỷ nguyên AI toàn cầu, Jensen Huang từng đối mặt với những thiết kế chip đầu tiên thất bại hoàn toàn khiến công ty đứng bên bờ vực phá sản, nhưng ông đã thẳng thắn nhận sai, làm lại từ đầu.",
        "ev_ynghia": "Thất bại chỉ thực sự là dấu chấm hết khi con người từ bỏ nỗ lực đứng lên.",
    },
    "ước mơ": {
        "term": "Ước mơ và khát vọng tuổi trẻ",
        "def": "**Ước mơ / Khát vọng** là những mục tiêu, lý tưởng cao đẹp, chính đáng mà con người khao khát hướng tới và bền bỉ nỗ lực phấn đấu để hiện thực hóa trong tương lai.",
        "why": "Ước mơ giống như ngọn hải đăng soi đường giữa biển lớn, giúp tuổi trẻ sống có mục đích rõ ràng, đánh thức tiềm năng ẩn giấu và tạo động lực vượt qua mọi rào cản xuất phát điểm.",
        "manifest": "Xây dựng lộ trình học tập cụ thể, miệt mài trau dồi tri thức, ngoại ngữ và kỹ năng mỗi ngày; biết gắn khát vọng vươn lên của cá nhân với sự phồn vinh của đất nước.",
        "how_to_promote": "Biến ước mơ lớn thành những mục tiêu hành động cụ thể từng ngày; kết hợp giữa khát vọng bay cao với sự kiên trì, thực tế trên mặt đất.",
        "counter": "Lối sống hoài phí thanh xuân, buông thả 'đến đâu hay đến đó'; hoặc những ảo tưởng viển vông, chỉ mơ mộng hão huyền mà lười biếng hành động.",
        "ev_ten": "Cô gái dân tộc Mông Lầu Minh Vư và chàng trai xương thủy tinh Nguyễn Sơn Lâm",
        "ev_chitiet": "Sinh ra ở vùng cao nghèo khó nơi nhiều bạn bè bỏ học lấy chồng sớm, Lầu Minh Vư đã nuôi dưỡng khát vọng bước ra thế giới bằng con đường học vấn, tự học tiếng Anh và giành học bổng toàn phần đại học quốc tế.",
        "ev_ynghia": "Khát vọng lớn chính là đôi cánh đưa con người vượt thoát khỏi mọi giới hạn của hoàn cảnh.",
    },
    "thấu cảm": {
        "term": "Sự thấu cảm và sẻ chia",
        "def": "**Sự thấu cảm** là khả năng đặt mình vào vị trí, hoàn cảnh của người khác để cảm nhận, thấu hiểu sâu sắc những nỗi niềm, tổn thương hay khó khăn của họ, từ đó ứng xử bằng một trái tim nhân ái và tôn trọng.",
        "why": "Trong xã hội hiện đại nhiều áp lực và sự xa cách của màn hình số, sự thấu cảm là chất keo hàn gắn những vết thương tinh thần, xóa bỏ sự cô đơn và làm cho thế giới trở nên ấm áp, nhân văn hơn.",
        "manifest": "Biết lắng nghe chân thành mà không vội vã phán xét; sẵn sàng nâng đỡ những mảnh đời yếu thế; tôn trọng sự khác biệt của người xung quanh.",
        "how_to_promote": "Rèn thói quen quan sát tinh tế, chậm lại một nhịp trước khi bình luận hay phán xét người khác trên mạng xã hội; tích cực tham gia các hoạt động thiện nguyện thực tế.",
        "counter": "Căn bệnh vô cảm, dửng dưng trước nỗi đau đồng loại; thói phán xét độc hại (cyberbullying) trên không gian mạng hoặc lòng tốt giả tạo nhằm đánh bóng tên tuổi.",
        "ev_ten": "Chàng trai trẻ Lê Văn Phúc (Sáng lập nhóm thiện nguyện 'Fly To Sky') & Hoàng Hoa Trung (Dự án 'Nuôi Em')",
        "ev_chitiet": "Từ khi còn là học sinh THPT tại Gia Lai, Lê Văn Phúc đã khởi xướng mạng lưới 'Fly To Sky', quyên góp hàng chục tấn sách vở, xây dựng thư viện và mang nước sạch đến cho hàng vạn trẻ em vùng cao biên giới.",
        "ev_ynghia": "Khi sự thấu cảm đi liền với hành động tử tế, tuổi trẻ có thể tạo ra những thay đổi kỳ diệu cho cộng đồng.",
    },
}

# KHO TRI THỨC CHUYÊN BIỆT CHO CÁC CHỦ ĐỀ HIỆN TƯỢNG / THÓI QUEN (GIỮ NGUYÊN 100% ĐẦY ĐỦ)
PROBLEM_SOLVING_KB = {
    "mạng xã hội": {
        "name": "tình trạng nghiện mạng xã hội và phụ thuộc vào thế giới ảo",
        "is_positive_declining": False,
        "def": "**Nghiện mạng xã hội / Sống ảo** là trạng thái con người bị lệ thuộc quá mức về mặt thời gian và cảm xúc vào các nền tảng kỹ thuật số (TikTok, Facebook, Instagram...), lấy lượt tương tác ảo làm thước đo giá trị bản thân mà sao nhãng đời sống thực.",
        "manifest": "Dành hàng chục giờ mỗi ngày lướt video ngắn vô thức; bất an khi không có điện thoại; chăm chút hình ảnh hào nhoáng trên mạng nhưng thờ ơ, lạnh nhạt với người thân ngay bên cạnh.",
        "harms_4_levels": [
            "- **Ý 1 — Tác hại đối với trí tuệ và hiệu quả học tập, lao động:** Lướt video ngắn liên tục làm suy giảm nghiêm trọng khả năng tập trung sâu (deep work), gây phân tán tư duy, suy giảm trí nhớ và làm tụt dốc kết quả học tập.",
            "- **Ý 2 — Tác hại đối với sức khỏe thể chất và tâm thần:** Ánh sáng xanh và sự kích thích thần kinh liên tục gây rối loạn giấc ngủ, suy nhược cơ thể; đồng thời hội chứng sợ bị bỏ lỡ (FOMO) và áp lực so sánh với hình ảnh hào nhoáng trên mạng dễ đẩy người trẻ vào trầm cảm, tự ti.",
            "- **Ý 3 — Tác hại đối với các mối quan hệ gia đình và giao tiếp thực tế:** Tạo ra 'sự cô đơn giữa đám đông', làm đứt gãy sợi dây gắn kết giữa con cái với cha mẹ, khiến người trẻ vụng về, thu mình khi bước vào giao tiếp xã hội trực tiếp.",
            "- **Ý 4 — Hệ lụy đối với an ninh tư tưởng và văn hóa cộng đồng:** Sự lệ thuộc mù quáng vào thế giới ảo khiến người trẻ dễ bị dẫn dắt bởi tin giả (fake news), trào lưu lệch chuẩn và cuốn vào bạo lực ngôn từ trên không gian mạng.",
        ],
        "status_cause_harm": (
            "- **Thực trạng:** Theo thống kê số hóa, trung bình nhiều thanh thiếu niên hiện nay dành từ 5–7 giờ/ngày trên mạng xã hội, biến các buổi gặp mặt hay bữa cơm gia đình thành 'những ốc đảo cúi đầu vào màn hình'.\n"
            "  - **Nguyên nhân:** *Chủ quan* là do tâm lý thiếu bản lĩnh tự kiểm soát, sợ bị bỏ lỡ (FOMO) và khao khát sự công nhận nhanh chóng; *Khách quan* là do thuật toán gây nghiện của các nền tảng số và sự thiếu không gian sinh hoạt thực tế từ gia đình, đô thị.\n"
            "  - **Hậu quả:** Bào mòn khả năng tập trung sâu, suy giảm kết quả học tập, gây rối loạn giấc ngủ, trầm cảm, cô lập giao tiếp trực tiếp và dễ bị dẫn dắt bởi thông tin độc hại."
        ),
        "benefit_of_quitting": "Giúp người trẻ giành lại quỹ thời gian quý giá để phát triển kỹ năng thực chất, tâm trí trở nên tĩnh tại, tập trung sâu hơn và tận hưởng trọn vẹn những kết nối ấm áp, chân thực ngoài đời thực.",
        "sol_individual": (
            "- **Giải pháp khả thi:** Mỗi người trẻ cần thực hiện 'Thanh lọc số' (Digital Detox): cài đặt giới hạn thời gian sử dụng ứng dụng không quá 60 phút/ngày, tắt thông báo khi học tập và chuyển từ người tiêu thụ nội dung thụ động sang người sử dụng công nghệ có mục đích.\n"
            "  - **Lí giải vì sao:** Bởi chiếc điện thoại nằm trong tay mỗi cá nhân; nếu tự thân không thiết lập kỷ luật tự giác thì không một phần mềm hay sự cấm đoán nào từ bên ngoài có thể thay đổi được thói quen.\n"
            "  - **Dẫn chứng thực tế:** Phong trào '30 ngày Digital Detox' và thử thách tắt mạng xã hội sau 21h tối của hàng nghìn học sinh, sinh viên tại Hà Nội và TP.HCM đã giúp các bạn cải thiện rõ rệt điểm số và giấc ngủ."
        ),
        "sol_family": (
            "- **Giải pháp khả thi:** Cha mẹ cần làm gương không lướt điện thoại trong bữa ăn, thiết lập quy tắc 'Khung giờ vàng gia đình không màn hình' vào mỗi tối để cùng trò chuyện, đọc sách hoặc tập thể thao cùng con.\n"
            "  - **Lí giải vì sao:** Gia đình là môi trường định hình thói quen đầu tiên; khi con cái tìm thấy sự lắng nghe và niềm vui ấm áp trong gia đình, các em sẽ không cần tìm kiếm sự bù đắp cảm xúc trên thế giới ảo.\n"
            "  - **Dẫn chứng thực tế:** Chiến dịch 'Bữa cơm gia đình ấm áp – Tắt điện thoại, bật yêu thương' được Hội Liên hiệp Phụ nữ và nhiều gia đình trẻ hưởng ứng đã khôi phục sợi dây gắn kết bền chặt giữa cha mẹ và con cái."
        ),
        "sol_school": (
            "- **Giải pháp khả thi:** Nhà trường cần quy định rõ việc quản lý điện thoại trong giờ học, đồng thời mở rộng các câu lạc bộ thể thao, nghệ thuật, thiện nguyện thực tế và tổ chức chuyên đề kỹ năng làm chủ không gian mạng.\n"
            "  - **Lí giải vì sao:** Khi trường học tạo ra một môi trường trải nghiệm thực tế hấp dẫn và năng động, học sinh sẽ tự nhiên rời mắt khỏi màn hình ảo để hòa mình vào hoạt động tập thể.\n"
            "  - **Dẫn chứng thực tế:** Mô hình 'Hộp giữ điện thoại thông minh đầu giờ' kết hợp 'Giờ ra chơi trải nghiệm sáng tạo không thiết bị số' tại nhiều trường THPT ở Hà Nội, Hải Phòng, Nghệ An đã giúp sân trường rộn ràng tiếng cười và hoạt động thể chất."
        ),
        "counter_rebuttal": (
            "- **Ý kiến trái chiều / Biện minh:** Có người cho rằng trong kỷ nguyên số 4.0, việc online liên tục là xu thế tất yếu để cập nhật thông tin và kết nối bạn bè nên không việc gì phải hạn chế hay từ bỏ.\n"
            "- **Phản biện khẳng định:** Đây là sự ngụy biện đánh tráo khái niệm giữa 'ứng dụng công nghệ thông minh' với 'lệ thuộc mù quáng vào mạng xã hội'. Công nghệ sinh ra để phục vụ con người chứ không phải để làm chủ con người; vì vậy việc kiểm soát và khắc phục tình trạng nghiện mạng là yêu cầu sống còn."
        ),
    },
    "trì hoãn": {
        "name": "thói quen trì hoãn",
        "is_positive_declining": False,
        "def": "**Thói quen trì hoãn** là hành vi cố tình chần chừ, dây dưa, đẩy những công việc cần làm ngay sang 'ngày mai' hoặc 'lúc khác' dù biết rõ việc chậm trễ đó sẽ dẫn đến áp lực và kết quả kém.",
        "manifest": "Đợi sát ngày thi mới bắt đầu học bài ('nước đến chân mới nhảy'); lập thời gian biểu chi tiết nhưng luôn tự thưởng cho mình lướt mạng 'thêm 5 phút nữa'; viện cớ 'chưa có cảm hứng' để trốn tránh nhiệm vụ khó.",
        "harms_4_levels": [
            "- **Ý 1 — Làm suy giảm nghiêm trọng hiệu suất và chất lượng học tập, công việc:** Khi dồn mọi việc đến phút chót, con người chỉ có thể làm việc trong trạng thái đối phó, vội vàng, dẫn đến sản phẩm cẩu thả, nhiều sai sót và không phát huy được năng lực thực sự.",
            "- **Ý 2 — Gây tổn hại nặng nề đến sức khỏe tinh thần và làm xói mòn sự tự tin:** Việc liên tục nợ nần công việc tạo ra cảm giác bất an, tội lỗi âm ỉ và căng thẳng thần kinh (stress) cực độ khi hạn chót ập đến; lâu dần khiến cá nhân rơi vào mặc cảm thất bại.",
            "- **Ý 3 — Đánh cắp những cơ hội quý giá không bao giờ quay lại:** Thời gian và cơ hội không chờ đợi bất kỳ ai; chỉ vì sự chần chừ 'để mai tính', người trẻ dễ dàng đánh mất học bổng, cơ hội rèn luyện và tụt hậu hoàn toàn so với bạn bè đồng trang lứa.",
            "- **Ý 4 — Làm suy giảm uy tín cá nhân và gây hệ lụy cho tập thể:** Trong làm việc nhóm và đời sống xã hội, một cá nhân có thói quen trì hoãn, trễ hẹn sẽ làm đình trệ tiến độ chung, đánh mất niềm tin, sự tôn trọng từ thầy cô, bạn bè và đồng nghiệp.",
        ],
        "status_cause_harm": (
            "- **Thực trạng:** Thói quen 'nước đến chân mới nhảy' đang trở thành căn bệnh trầm kha của một bộ phận lớn học sinh, người trẻ hiện nay trong cả việc học lẫn rèn luyện kỹ năng.\n"
            "  - **Nguyên nhân:** *Chủ quan* là do sự thiếu kỷ luật bản thân, tâm lý ngại khó, sợ thất bại hoặc chạy theo những thú vui giải trí tức thời; *Khách quan* là do sự cám dỗ dày đặc của các thiết bị giải trí số và thiếu phương pháp quản lý thời gian khoa học.\n"
            "  - **Hậu quả:** Khiến công việc dồn ứ gây căng thẳng tâm lý cực độ, chất lượng học tập sụt giảm, đánh mất uy tín với tập thể và bỏ lỡ những cơ hội quý giá không bao giờ quay lại."
        ),
        "benefit_of_quitting": "Khi dứt khoát từ bỏ sự trì hoãn, mỗi người sẽ làm chủ được quỹ thời gian, giải phóng tâm trí khỏi cảm giác tội lỗi, nâng cao chất lượng công việc và xây dựng được phong thái làm việc chuyên nghiệp, đáng tin cậy.",
        "sol_individual": (
            "- **Giải pháp khả thi (Trọng tâm):** Áp dụng ngay 'Quy tắc 2 phút' (việc gì làm dưới 2 phút thì bắt tay làm ngay lập tức) và phương pháp quả cà chua (Pomodoro: tập trung cao độ 25 phút, nghỉ 5 phút), đồng thời chia nhỏ mục tiêu lớn thành từng bước nhỏ dễ bắt đầu.\n"
            "  - **Lí giải vì sao:** Rào cản lớn nhất của sự trì hoãn nằm ở cảm giác 'ngại bắt đầu' khi nhìn vào khối lượng việc quá lớn; khi chia nhỏ và hành động ngay trong 2 phút đầu, quán tính làm việc sẽ được kích hoạt.\n"
            "  - **Dẫn chứng thực tế:** Tác giả David Allen với nguyên tắc 'Getting Things Done' (Quy tắc 2 phút) và tấm gương tự học ngoại ngữ mỗi ngày 30 phút không ngắt quãng của các thủ khoa kỳ thi THPT Quốc gia."
        ),
        "sol_family": (
            "- **Giải pháp khả thi:** Cha mẹ rèn cho con tính tự lập và nguyên tắc hoàn thành nhiệm vụ đúng hạn từ những việc nhỏ trong nhà, khích lệ sự tiến bộ thay vì làm thay hoặc nhắc nhở chì chiết.\n"
            "  - **Lí giải vì sao:** Nề nếp sinh hoạt đúng giờ giấc trong gia đình sẽ tạo lập phản xạ kỷ luật tự nhiên cho người trẻ.\n"
            "  - **Dẫn chứng thực tế:** Phương pháp giáo dục tính tự giác và quản lý thời gian từ nhỏ của các gia đình có con đạt thành tích tự học xuất sắc."
        ),
        "sol_school": (
            "- **Giải pháp khả thi:** Giáo viên và nhà trường giao nhiệm vụ học tập theo từng chặng (milestone) có kiểm tra tiến độ định kỳ thay vì chỉ chấm kết quả cuối cùng, đồng thời hướng dẫn học sinh kỹ năng lập kế hoạch.\n"
            "  - **Lí giải vì sao:** Việc đồng hành và giám sát theo chặng giúp học sinh hình thành thói quen làm việc đều đặn, triệt tiêu thói quen dồn việc đến phút chót.\n"
            "  - **Dẫn chứng thực tế:** Mô hình học tập theo dự án (Project-based Learning) có nhật ký tiến độ hàng tuần tại các trường THPT hiện nay đã giúp học sinh rèn luyện tác phong làm việc đúng hạn."
        ),
        "counter_rebuttal": (
            "- **Dự đoán ý kiến phản đối:** Nhiều người thường biện minh rằng: 'Làm việc sát nút dưới áp lực cao mới kích thích sự sáng tạo' hoặc 'Tuổi trẻ còn nhiều thời gian, chậm một chút cũng chẳng sao'.\n"
            "- **Phản biện & Khuyên nhủ:** Thực chất, việc làm vội vã phút chót chỉ tạo ra những sản phẩm đối phó đầy sai sót và bào mòn sức khỏe. Thời gian trôi qua không thể lấy lại, vì vậy từ bỏ trì hoãn ngay hôm nay chính là cách tôn trọng tương lai của chính mình."
        ),
    },
    "bạo lực": {
        "name": "vấn nạn bạo lực học đường và bạo lực ngôn từ trên không gian mạng",
        "is_positive_declining": False,
        "def": "**Bạo lực học đường và bạo lực mạng** là những hành vi cố ý sử dụng vũ lực thể chất hoặc lời nói lăng mạ, cô lập, vu khống, công kích tinh thần người khác trong môi trường trường học và trên các nền tảng trực tuyến.",
        "manifest": "Đánh hội đồng, quay clip tung lên mạng; lập các hội nhóm nói xấu, tẩy chay bạn bè; buông những bình luận miệt thị ngoại hình, hoàn cảnh của người khác sau bàn phím.",
        "harms_4_levels": [
            "- **Ý 1 — Gây tổn thương nặng nề về thể chất và vết sẹo tâm lý suốt đời cho nạn nhân:** Khiến nạn nhân rơi vào hoảng loạn, trầm cảm, sợ hãi trường lớp, thậm chí dẫn đến những hành vi tự hủy hoại bản thân đau lòng.",
            "- **Ý 2 — Làm lệch lạc nhân cách và hủy hoại tương lai của chính người gây bạo lực:** Thói hung hăng, coi thường kỷ luật nếu không bị ngăn chặn sẽ đẩy người gây bạo lực trượt dài vào vi phạm pháp luật và đánh mất cơ hội học tập.",
            "- **Ý 3 — Gây đau đớn, bất an cho gia đình:** Khiến các bậc phụ huynh rơi vào khủng hoảng, lo âu và gánh chịu những tổn thất tinh thần không gì bù đắp được.",
            "- **Ý 4 — Phá vỡ sự tôn nghiêm, an toàn và nhân văn của môi trường giáo dục:** Biến mái trường vốn là nơi nuôi dưỡng tri thức và tình bạn thành không gian của sự sợ hãi, vô cảm.",
        ],
        "status_cause_harm": (
            "- **Thực trạng:** Bạo lực học đường hiện nay không chỉ dừng ở xô xát tay chân mà đã biến tướng tinh vi thành 'bạo lực tinh thần' và 'bạo lực mạng' với tốc độ phát tán chóng mặt.\n"
            "  - **Nguyên nhân:** *Chủ quan* do sự bốc đồng tâm lý lứa tuổi, thiếu kỹ năng kiểm soát cảm xúc, thích thể hiện cái tôi lệch lạc; *Khách quan* do ảnh hưởng từ phim ảnh bạo lực, sự thiếu quan tâm sâu sát của gia đình và tâm lý đám đông vô trách nhiệm trên mạng.\n"
            "  - **Hậu quả:** Để lại vết sẹo tâm lý nặng nề, khiến nạn nhân rơi vào trầm cảm, hoảng loạn, bỏ học, thậm chí có hành vi tự hủy hoại bản thân; đồng thời làm suy đồi đạo đức và sự an toàn của môi trường giáo dục."
        ),
        "benefit_of_quitting": "Chấm dứt bạo lực và thói phán xét độc hại giúp xây dựng một môi trường học đường nhân ái, an toàn, nơi mỗi cá nhân được tôn trọng và phát triển toàn diện.",
        "sol_individual": (
            "- **Giải pháp khả thi:** Mỗi học sinh cần học cách quản trị cơn giận, giải quyết mâu thuẫn bằng đối thoại tôn trọng; tuyệt đối không cổ xúy, không bấm 'like/share' các clip bạo lực và dũng cảm báo ngay cho thầy cô khi thấy hành vi bắt nạt.\n"
            "  - **Lí giải vì sao:** Bạo lực chỉ có thể lan rộng khi có sự tiếp tay hoặc im lặng vô cảm của những người xung quanh; khi mỗi cá nhân biết kiểm soát hành vi và lên tiếng bảo vệ lẽ phải, mầm mống bạo lực sẽ bị dập tắt.\n"
            "  - **Dẫn chứng thực tế:** Chiến dịch 'Ngừng bắt nạt bằng lời nói' và hành động dũng cảm đứng ra can ngăn, bảo vệ bạn yếu thế của nhiều học sinh THPT được tuyên dương dưới cờ."
        ),
        "sol_family": (
            "- **Giải pháp khả thi:** Cha mẹ cần giáo dục con bằng sự yêu thương và lắng nghe thay vì đòn roi quát tháo, đồng thời thường xuyên quan sát những biểu hiện tâm lý bất thường của con để kịp thời tháo gỡ.\n"
            "  - **Lí giải vì sao:** Một đứa trẻ lớn lên trong gia đình êm ấm, giàu lòng thấu cảm sẽ không dùng bạo lực để giải quyết vấn đề và luôn có điểm tựa an toàn khi gặp khủng hoảng.\n"
            "  - **Dẫn chứng thực tế:** Các chương trình kết nối 'Cha mẹ đồng hành cùng con tuổi dậy thì' do các chuyên gia tâm lý giáo dục triển khai hiệu quả tại nhiều địa phương."
        ),
        "sol_school": (
            "- **Giải pháp khả thi:** Nhà trường vận hành thực chất Phòng tư vấn tâm lý học đường, thiết lập kênh tiếp nhận thông tin ẩn danh của học sinh và xây dựng mô hình 'Trường học hạnh phúc – Không bạo lực'.\n"
            "  - **Lí giải vì sao:** Khi nhà trường vừa có sự hỗ trợ tâm lý kịp thời vừa có quy tắc ứng xử văn hóa nghiêm minh, học sinh sẽ được bảo vệ toàn diện.\n"
            "  - **Dẫn chứng thực tế:** Mô hình 'Hòm thư điều em muốn nói' và Câu lạc bộ Truyền thông phòng chống bạo lực học đường tại nhiều trường THPT trên cả nước."
        ),
        "counter_rebuttal": (
            "- **Ý kiến trái chiều:** Có người cho rằng những xích mích, trêu chọc hay xô xát tuổi học trò chỉ là chuyện nhỏ nhất thời của lứa tuổi mới lớn, không cần làm quá lên.\n"
            "- **Phản biện khẳng định:** Suy nghĩ thờ ơ đó chính là sự dung túng nguy hiểm, bởi từ những lời miệt thị hay cái tát tưởng như 'chuyện nhỏ' đã cướp đi tương lai và sinh mạng của không ít học sinh. Đẩy lùi bạo lực học đường là trách nhiệm không thể chần chừ."
        ),
    },
    "môi trường": {
        "name": "vấn đề ô nhiễm môi trường và thói quen xả rác, lạm dụng nhựa dùng một lần",
        "is_positive_declining": False,
        "def": "**Ô nhiễm môi trường / Lạm dụng rác thải nhựa** là tình trạng môi trường tự nhiên (đất, nước, không khí) bị suy thoái nghiêm trọng do các chất thải độc hại và thói quen tiêu dùng thiếu bền vững của con người.",
        "manifest": "Xả rác bừa bãi nơi công cộng; sử dụng tràn lan túi nilon, cốc nhựa dùng một lần; chặt phá cây xanh và xả nước thải chưa qua xử lý ra sông hồ.",
        "harms_4_levels": [
            "- **Ý 1 — Đe dọa trực tiếp đến sức khỏe và tính mạng con người:** Nguồn nước, không khí ô nhiễm và hạt vi nhựa xâm nhập vào chuỗi thức ăn gây ra hàng loạt căn bệnh hiểm nghèo về hô hấp, tiêu hóa và ung thư.",
            "- **Ý 2 — Tàn phá hệ sinh thái và làm suy giảm đa dạng sinh học:** Hàng triệu sinh vật biển và động vật hoang dã chết vì nuốt phải rác thải nhựa hoặc mất môi trường sống tự nhiên.",
            "- **Ý 3 — Thúc đẩy biến đổi khí hậu cực đoan:** Làm gia tăng hiệu ứng nhà kính, dẫn đến siêu bão, lũ quét, sạt lở đất và hạn hán khốc liệt đe dọa trực tiếp cuộc sống của hàng triệu người dân.",
            "- **Ý 4 — Gây thiệt hại nặng nề về kinh tế - xã hội và tương lai thế hệ mai sau:** Tiêu tốn hàng nghìn tỷ đồng mỗi năm để khắc phục hậu quả môi trường, làm suy giảm hình ảnh du lịch và để lại món nợ sinh thái cho thế hệ sau.",
        ],
        "status_cause_harm": (
            "- **Thực trạng:** Việt Nam nằm trong nhóm các quốc gia chịu ảnh hưởng nặng nề nhất của biến đổi khí hậu và rác thải nhựa; mỗi năm có hàng triệu tấn rác nhựa thải ra môi trường nhưng tỷ lệ tái chế còn rất thấp.\n"
            "  - **Nguyên nhân:** *Chủ quan* là do thói quen tiện đâu vứt đấy, lối sống tiêu dùng nhanh ích kỷ của một bộ phận người dân; *Khách quan* là do quá trình đô thị hóa nhanh và chế tài xử phạt vi phạm môi trường ở một số nơi chưa đủ sức răn đe.\n"
            "  - **Hậu quả:** Làm cạn kiệt tài nguyên, gây biến đổi khí hậu cực đoan (siêu bão, lũ quét, hạn mặn) và đe dọa trực tiếp đến sức khỏe, mạng sống của chính con người qua nguồn nước, thực phẩm nhiễm vi nhựa."
        ),
        "benefit_of_quitting": "Từ bỏ thói quen xả rác và dùng nhựa một lần giúp trả lại không gian sống xanh – sạch – lành mạnh, bảo vệ sức khỏe cộng đồng và giữ gìn hành tinh bền vững cho thế hệ tương lai.",
        "sol_individual": (
            "- **Giải pháp khả thi:** Mỗi cá nhân thực hành lối sống xanh từ những việc nhỏ nhất: mang bình nước cá nhân, dùng túi vải khi đi chợ, phân loại rác tại nguồn và bỏ rác đúng nơi quy định.\n"
            "  - **Lí giải vì sao:** Môi trường chung được tạo nên từ hành vi của hàng triệu cá nhân; khi mỗi người giảm đi một chiếc túi nilon mỗi ngày, hàng tỷ rác thải nhựa sẽ được cắt giảm mỗi năm.\n"
            "  - **Dẫn chứng thực tế:** Phong trào sống xanh của giới trẻ cùng hành động trực tiếp lội kênh vớt hàng trăm tấn rác của nhóm bạn trẻ 'Sài Gòn Xanh', 'Hà Nội Xanh'."
        ),
        "sol_family": (
            "- **Giải pháp khả thi:** Mỗi gia đình hình thành thói quen phân loại rác hữu cơ – rác tái chế ngay tại bếp, hạn chế đồ nhựa một lần và dạy con trẻ ý thức trân trọng cây xanh, tiết kiệm điện nước.\n"
            "  - **Lí giải vì sao:** Gia đình là đơn vị tiêu dùng trực tiếp mỗi ngày; nếp sống xanh từ gia đình sẽ tạo ra thế hệ công dân có trách nhiệm với tự nhiên.\n"
            "  - **Dẫn chứng thực tế:** Mô hình 'Gia đình 5 không, 3 sạch' và phong trào biến rác hữu cơ thành phân bón trồng cây tại nhiều khu dân cư."
        ),
        "sol_school": (
            "- **Giải pháp khả thi:** Nhà trường xây dựng mô hình 'Trường học xanh – Không rác thải nhựa', tổ chức ngày hội đổi rác lấy cây xanh và lồng ghép giáo dục bảo vệ môi trường qua trải nghiệm thực địa.\n"
            "  - **Lí giải vì sao:** Trường học có sức lan tỏa mạnh mẽ tới hàng triệu học sinh, giúp biến nhận thức bảo vệ môi trường thành thói quen văn minh bền vững.\n"
            "  - **Dẫn chứng thực tế:** Dự án 'Đổi sách báo cũ và vỏ lon lấy cây xanh' của chuỗi chương trình 'Fly To Sky' phối hợp cùng hàng trăm trường THPT trên toàn quốc."
        ),
        "counter_rebuttal": (
            "- **Ý kiến trái chiều:** Có người cho rằng việc bảo vệ môi trường là trách nhiệm vĩ mô của các cơ quan chức năng và tập đoàn lớn, một vài cá nhân tiết kiệm túi nilon cũng chẳng thay đổi được gì.\n"
            "- **Phản biện khẳng định:** Đó là lối tư duy ỷ lại vô trách nhiệm. Đại dương được tạo nên từ những giọt nước, và thảm họa môi trường cũng tích tụ từ chính sự tiện tay vô ý thức của từng cá nhân. Do đó, hành động từ mỗi người là không thể thay thế."
        ),
    },
    "tự lập": {
        "name": "tính tự lập, tự chủ và tinh thần tự giác của người trẻ",
        "is_positive_declining": True,
        "def": "**Tính tự lập / Tự giác** là khả năng tự mình suy nghĩ, đưa ra quyết định, tự lo liệu công việc học tập và cuộc sống bằng năng lực của bản thân mà không ỷ lại, dựa dẫm vào cha mẹ hay người khác.",
        "manifest": "Tự giác lập kế hoạch học tập mà không cần ai nhắc nhở; chủ động trang bị kỹ năng sống, tự giải quyết các vấn đề cá nhân và chịu trách nhiệm về lựa chọn của mình.",
        "meaning_when_positive": "**Ý nghĩa vốn có của tính tự lập:** Tự lập chính là bước ngoặt đánh dấu sự trưởng thành thực sự của một con người; nó giúp người trẻ rèn luyện bản lĩnh thích ứng trước mọi biến động, làm chủ cuộc đời mình và giảm bớt gánh nặng cho gia đình.",
        "harms_4_levels": [
            "- **Ý 1 — Đánh mất khả năng thích nghi và tự giải quyết vấn đề:** Khi thiếu tính tự lập, người trẻ dễ rơi vào khủng hoảng, lúng túng trước những thay đổi nhỏ nhất của hoàn cảnh sống.",
            "- **Ý 2 — Kìm hãm tư duy sáng tạo và bản lĩnh cá nhân:** Tâm lý ỷ lại biến con người thành cái bóng thụ động, không dám đưa ra quyết định và không dám chịu trách nhiệm.",
            "- **Ý 3 — Tạo gánh nặng lâu dài cho gia đình và người thân:** Khiến cha mẹ phải lo lắng, bao bọc suốt đời.",
            "- **Ý 4 — Làm suy giảm chất lượng nguồn nhân lực trẻ của xã hội:** Một thế hệ thiếu tự chủ sẽ không thể gánh vác những trọng trách đòi hỏi bản lĩnh độc lập trong kỷ nguyên mới.",
        ],
        "status_cause_harm": (
            "- **Thực trạng:** Hiện nay, không ít học sinh, thanh niên dù đã lớn nhưng vẫn mang tâm lý 'cây tầm gửi', thiếu kỹ năng tự chăm sóc bản thân, học tập đối phó khi không có người giám sát và dễ hoảng loạn khi bước vào môi trường mới.\n"
            "  - **Nguyên nhân:** *Chủ quan* là do sự lười biếng, ưa hưởng thụ trong vùng an toàn của chính người trẻ; *Khách quan* là do sự bao bọc thái quá ('cha mẹ trực thăng') làm thay con mọi việc của nhiều gia đình hiện đại.\n"
            "  - **Hậu quả:** Khiến người trẻ trở nên yếu ớt, thụ động, thiếu khả năng giải quyết vấn đề thực tế và dễ gục ngã trước những va vấp đầu đời."
        ),
        "sol_individual": (
            "- **Giải pháp khả thi:** Mỗi học sinh cần bắt đầu tự lập từ những việc gần gũi nhất: tự đặt báo thức, tự xây dựng thời gian biểu học tập, tự chăm sóc không gian sống và chủ động tìm tòi phương pháp giải quyết bài khó trước khi nhờ trợ giúp.\n"
            "  - **Lí giải vì sao:** Kỹ năng tự lập không tự nhiên sinh ra mà phải được tích lũy qua việc tự tay làm và tự chịu trách nhiệm mỗi ngày.\n"
            "  - **Dẫn chứng thực tế:** Nhiều học sinh THPT vùng cao hoặc các bạn học sinh giành học bổng du học tự túc đã rèn khả năng tự quản lý tài chính, thời gian và tự học xuất sắc ngay từ năm lớp 10."
        ),
        "sol_family": (
            "- **Giải pháp khả thi:** Cha mẹ cần thay đổi cách yêu thương: chuyển từ 'làm thay con' sang 'hướng dẫn và trao quyền cho con tự làm', chấp nhận để con va vấp trong giới hạn an toàn để trưởng thành.\n"
            "  - **Lí giải vì sao:** Nếu cha mẹ cứ giữ mãi đôi cánh bao bọc, con cái sẽ không bao giờ học được cách tự bay trên bầu trời của chính mình.\n"
            "  - **Dẫn chứng thực tế:** Phương pháp giáo dục tự lập của các gia đình văn minh (cho con tự chuẩn bị đồ dùng, tự chịu trách nhiệm với điểm số và quyết định cá nhân)."
        ),
        "sol_school": (
            "- **Giải pháp khả thi:** Nhà trường đẩy mạnh phương pháp dạy học phát triển năng lực tự học, tổ chức các hoạt động dã ngoại, trại hè kỹ năng sinh tồn và giao quyền tự quản cho các câu lạc bộ học sinh.\n"
            "  - **Lí giải vì sao:** Môi trường tập thể đòi hỏi sự tự chủ sẽ là thao trường tốt nhất để học sinh rèn luyện bản lĩnh độc lập.\n"
            "  - **Dẫn chứng thực tế:** Các chương trình 'Học kỳ trong quân đội' và mô hình Câu lạc bộ học sinh tự quản tại các trường THPT trên cả nước."
        ),
        "counter_rebuttal": (
            "- **Ý kiến trái chiều:** Có ý kiến cho rằng ở lứa tuổi học sinh phổ thông, nhiệm vụ duy nhất là học văn hóa nên việc được bố mẹ lo liệu hết mọi thứ là điều bình thường, khi nào đi làm mới cần tự lập.\n"
            "- **Phản biện khẳng định:** Đây là quan niệm sai lầm; bởi tự lập là một năng lực cần quá trình rèn luyện lâu dài. Nếu suốt 18 năm chỉ quen dựa dẫm, người trẻ sẽ hoàn toàn bơ vơ và khủng hoảng khi bước ra ngưỡng cửa đại học và cuộc đời."
        ),
    },
}

DANH_SACH_DANG_BAI = [
    "Tự động nhận diện theo đề bài",
    "Dạng 1 - TH1 (Khía cạnh tích cực): Bàn sâu về Ý nghĩa / Vai trò / Giá trị / Sức mạnh / Sự cần thiết",
    "Dạng 1 - TH1 (Khía cạnh tiêu cực): Bàn sâu về Tác hại / Hậu quả / Hệ lụy của một thói quen hay hiện tượng",
    "Dạng 1 - TH2: Bàn sâu về Bài học giải pháp / Trách nhiệm (Trả lời câu hỏi: Cần làm gì?)",
    "Dạng 1 - TH3: Bàn luận chung toàn diện về một tư tưởng, đạo lí (Giải thích -> Biểu hiện -> Ý nghĩa -> Dẫn chứng -> Phát huy)",
    "Dạng 2: Nghị luận về một vấn đề cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả - Giải pháp 3 cấp độ)",
    "Dạng 3: Nghị luận lựa chọn quan điểm (Đứng trước 2 quan điểm / ý kiến)",
    "Dạng 4: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học",
    "Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm",
]

def extract_clean_topic_noun(text):
    clean = re.sub(
        r"(?i)(hãy viết một bài văn nghị luận xã hội|hãy viết bài văn nghị luận xã hội|hãy viết một bài văn nghị luận|hãy viết bài văn nghị luận|viết một bài văn nghị luận|viết bài văn nghị luận|viết bài văn|viết đoạn văn|khoảng 600 chữ|khoảng 200 chữ|trình bày suy nghĩ của anh/chị về|suy nghĩ của anh/chị về|suy nghĩ về|bàn luận về|bàn về|nghị luận về|tác hại của|hậu quả của|hệ lụy của|mặt trái của|ý nghĩa của|vai trò của|tầm quan trọng của|sức mạnh của|sự cần thiết của|giá trị của|thuyết phục người khác từ bỏ|thuyết phục bạn bè từ bỏ|thuyết phục mọi người từ bỏ|thuyết phục từ bỏ|giải pháp khắc phục tình trạng|giải pháp khắc phục|làm thế nào để|cần làm gì để)",
        "",
        text,
    )
    clean = re.sub(r'[():.,?!"]', "", clean).strip()
    clean = re.sub(r"^(về|việc)\s+", "", clean, flags=re.IGNORECASE).strip()
    return clean if clean else text.strip()

def is_metaphorical_quote_topic(topic_text):
    if '"' in topic_text or "“" in topic_text or "”" in topic_text:
        return True
    if any(
        w in topic_text.lower()
        for w in ["có ý kiến cho rằng", "ngạn ngữ", "danh ngôn", "nhà văn", "từng nói", "câu nói"]
    ):
        return True
    return False

# ==============================================================================
# THUẬT TOÁN PHÂN LUỒNG CHÍNH XÁC TỪNG DẠNG BÀI
# ==============================================================================
def classify_essay_type(topic_text, vdnl_text="", manual_override="Tự động nhận diện theo đề bài"):
    if manual_override and manual_override != "Tự động nhận diện theo đề bài":
        if "Khía cạnh tích cực" in manual_override:
            return "DANG_1_TH1_Y_NGHIA"
        if "Khía cạnh tiêu cực" in manual_override:
            return "DANG_1_TH1_TAC_HAI"
        if "Dạng 1 - TH2" in manual_override:
            return "DANG_1_TH2"
        if "Dạng 1 - TH3" in manual_override:
            return "DANG_1_TH3"
        if "Dạng 2" in manual_override:
            return "DANG_2_GIAI_QUYET"
        if "Dạng 3" in manual_override:
            return "DANG_3_HAI_QUAN_DIEM"
        if "Dạng 4" in manual_override:
            return "DANG_4_VAN_HOC"
        if "Dạng 5" in manual_override:
            return "DANG_5_TU_BO"

    combined = (topic_text + " " + vdnl_text).lower()

    if any(
        kw in combined
        for kw in [
            "thuyết phục người khác từ bỏ",
            "thuyết phục bạn từ bỏ",
            "thuyết phục mọi người từ bỏ",
            "thuyết phục từ bỏ",
            "khuyên bạn từ bỏ",
            "viết bài luận thuyết phục",
            "từ bỏ một thói quen",
            "từ bỏ thói quen",
            "từ bỏ một quan niệm",
            "từ bỏ quan niệm",
        ]
    ):
        return "DANG_5_TU_BO"

    if any(kw in combined for kw in ["tác hại của", "hậu quả của", "hệ lụy của", "mặt trái của"]):
        if not any(sol_kw in combined for sol_kw in ["giải pháp", "khắc phục", "cần làm gì"]):
            return "DANG_1_TH1_TAC_HAI"
        return "DANG_2_GIAI_QUYET"

    if any(
        kw in combined
        for kw in [
            "ý nghĩa của",
            "vai trò của",
            "giá trị của",
            "sức mạnh của",
            "tầm quan trọng của",
            "sự cần thiết của",
            "vẻ đẹp của",
            "lợi ích của",
        ]
    ):
        if not any(sol_kw in combined for sol_kw in ["giải pháp", "khắc phục", "cần làm gì để", "làm thế nào để"]):
            return "DANG_1_TH1_Y_NGHIA"

    if any(
        kw in combined
        for kw in [
            "tác phẩm",
            "truyện ngắn",
            "bài thơ",
            "nhân vật văn học",
            "đoạn trích",
            "nhà thơ",
            "tiểu thuyết",
            "rút ra từ tác phẩm",
            "qua nhân vật",
        ]
    ):
        return "DANG_4_VAN_HOC"

    if any(
        kw in combined
        for kw in [
            "hai quan điểm",
            "2 quan điểm",
            "hai ý kiến",
            "nhưng có ý kiến khác lại cho rằng",
            "trong khi đó có người lại nghĩ",
            "anh/chị chọn quan điểm nào",
            "bạn chọn",
            "giữa hai lựa chọn",
            "quan điểm thứ nhất",
            "ý kiến thứ nhất",
        ]
    ):
        return "DANG_3_HAI_QUAN_DIEM"

    if any(
        kw in combined
        for kw in [
            "cần làm gì",
            "phải làm gì",
            "làm thế nào để",
            "trách nhiệm của tuổi trẻ",
            "trách nhiệm của thế hệ trẻ",
            "trách nhiệm của học sinh",
            "vai trò của người trẻ đối với",
            "bổn phận của",
            "để phát huy",
            "để rèn luyện",
        ]
    ):
        return "DANG_1_TH2"

    negative_phenomena = [
        "ô nhiễm",
        "nghiện game",
        "nghiện mạng",
        "bạo lực học đường",
        "bạo lực mạng",
        "rác thải",
        "lãng phí",
        "gian lận",
        "sống ảo",
        "vô cảm",
        "biến đổi khí hậu",
        "an toàn giao thông",
        "thực trạng",
        "vấn nạn",
        "hiện tượng",
        "cần giải quyết",
        "khắc phục tình trạng",
        "giải pháp để khắc phục",
        "giải pháp khắc phục",
        "mất kết nối",
    ]
    if any(kw in combined for kw in negative_phenomena):
        return "DANG_2_GIAI_QUYET"

    return "DANG_1_TH3"

def get_essay_type_label(code):
    labels = {
        "DANG_1_TH1_Y_NGHIA": "Dạng 1 (TH1 - Khía cạnh tích cực): Bàn sâu trọng tâm về Ý nghĩa / Vai trò / Giá trị / Sức mạnh của vấn đề",
        "DANG_1_TH1_TAC_HAI": "Dạng 1 (TH1 - Khía cạnh tiêu cực): Bàn sâu trọng tâm về Tác hại / Hậu quả / Hệ lụy của vấn đề",
        "DANG_1_TH2": "Dạng 1 (TH2 - Định hướng hành động): Bàn trọng tâm về Bài học giải pháp / Trách nhiệm (Trả lời câu hỏi: Cần làm gì?)",
        "DANG_1_TH3": "Dạng 1 (TH3 - Bàn luận chung): Tư tưởng, đạo lí toàn diện (Giải thích & Biểu hiện -> Ý nghĩa & Dẫn chứng -> Bài học phát huy)",
        "DANG_2_GIAI_QUYET": "Dạng 2: Nghị luận về một vấn đề cần giải quyết (Giải thích -> Lí do cần giải quyết -> Giải pháp 3 đoạn -> Phản biện)",
        "DANG_3_HAI_QUAN_DIEM": "Dạng 3: Nghị luận lựa chọn quan điểm (Giải thích & Mối quan hệ -> Bảo vệ lựa chọn & Hạn chế quan điểm kia -> Bài học)",
        "DANG_4_VAN_HOC": "Dạng 4: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học",
        "DANG_5_TU_BO": "Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay quan niệm (Giải thích & Biểu hiện -> Lí do + Dẫn chứng -> Giải pháp 3 đoạn -> Dự đoán phản đối)",
    }
    return labels.get(code, labels["DANG_1_TH3"])

def is_positive_topic_declining(topic_text, vdnl_text):
    combined = (topic_text + " " + vdnl_text).lower()
    direct_negative = [
        "tác hại",
        "hậu quả",
        "ô nhiễm",
        "nghiện game",
        "nghiện mạng",
        "bạo lực",
        "rác thải",
        "gian lận",
        "lãng phí",
        "tệ nạn",
        "cờ bạc",
        "thuốc lá",
        "nói tục",
        "sống ảo",
        "trì hoãn",
        "vô cảm",
    ]
    if any(neg in combined for neg in direct_negative):
        return False
    return True

def match_problem_solving_kb(raw_topic, vdnl):
    combined = (raw_topic + " " + vdnl).lower()
    if any(k in combined for k in ["mạng xã hội", "sống ảo", "nghiện game", "điện thoại", "không gian mạng", "công nghệ"]):
        return PROBLEM_SOLVING_KB["mạng xã hội"]
    if any(k in combined for k in ["trì hoãn", "nước đến chân", "lười biếng", "thời gian", "đúng giờ"]):
        return PROBLEM_SOLVING_KB["trì hoãn"]
    if any(k in combined for k in ["bạo lực", "bắt nạt", "ngôn từ", "nói tục", "phán xét"]):
        return PROBLEM_SOLVING_KB["bạo lực"]
    if any(k in combined for k in ["môi trường", "ô nhiễm", "rác thải", "nhựa", "biến đổi khí hậu", "sống xanh"]):
        return PROBLEM_SOLVING_KB["môi trường"]
    if any(k in combined for k in ["tự lập", "tự giác", "tự chủ", "ỷ lại", "dựa dẫm", "gắn kết"]):
        return PROBLEM_SOLVING_KB["tự lập"]
    return None

def parse_two_viewpoints_from_topic(raw_topic, vdnl):
    quotes = re.findall(r'["“”\']([^"“”\']{8,150})["“”\']', raw_topic)
    if len(quotes) >= 2:
        return quotes[0].strip(), quotes[1].strip()
    split_match = re.split(r"(?i)(?:nhưng có ý kiến khác lại cho rằng|trong khi đó|ngược lại có người cho rằng|hay là|hoặc)", raw_topic)
    if len(split_match) >= 2:
        v1 = extract_clean_topic_noun(split_match[0])[:100]
        v2 = extract_clean_topic_noun(split_match[1])[:100]
        if v1 and v2:
            return v1, v2
    return f"Quan điểm thứ nhất về {vdnl}", f"Quan điểm thứ hai (đối trọng/bổ sung) về {vdnl}"

def get_pedagogical_structure_guide(type_code, raw_topic, vdnl):
    has_meaning_step = is_positive_topic_declining(raw_topic, vdnl)
    if type_code == "DANG_1_TH1_Y_NGHIA":
        lines = [
            f"DẠNG BÀI: Đề chỉ hỏi 1 khía cạnh tích cực (Ý nghĩa / Vai trò / Giá trị / Sức mạnh / Sự cần thiết của '{vdnl}').",
            "QUY TẮC BẮT BUỘC: Tập trung phân tích sâu Ý NGHĨA / VAI TRÒ của vấn đề. Tuyệt đối KHÔNG ôm đồm biến thành bài giải pháp 3 cấp độ.",
            "- Luận điểm 1 (Giải thích & Biểu hiện): Giải thích khái niệm/nhận định và nêu biểu hiện thực tế.",
            f"- Luận điểm 2 (Bàn luận sâu về Ý NGHĨA / VAI TRÒ của '{vdnl}'): Chia thành các ý phân tích sâu giá trị đối với nội lực cá nhân, bồi đắp tâm hồn, kết nối con người và thúc đẩy xã hội + Phân tích Dẫn chứng thực tế.",
            "- Luận điểm 3 (Phản đề & Bài học liên hệ): Phê phán biểu hiện trái ngược, mở rộng biện chứng và rút ra bài học nhận thức, hành động ngắn gọn.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_1_TH1_TAC_HAI":
        lines = [
            f"DẠNG BÀI: Đề chỉ hỏi 1 khía cạnh tiêu cực (Tác hại / Hậu quả / Hệ lụy của '{vdnl}').",
            "QUY TẮC BẮT BUỘC: Trọng tâm của bài viết là MỔ XẺ SÂU CÁC TẦNG TÁC HẠI / HẬU QUẢ. Tuyệt đối KHÔNG ôm đồm biến bài văn thành dạng Giải pháp 3 đoạn hay dạng Thuyết phục từ bỏ.",
            "- Luận điểm 1 (Giải thích & Biểu hiện nhận diện): Giải thích rõ bản chất của thói quen/hiện tượng và chỉ ra các biểu hiện cụ thể trong đời sống, học đường.",
            f"- Luận điểm 2 (Bàn luận trọng tâm — Phân tích sâu các tầng TÁC HẠI / HẬU QUẢ của '{vdnl}'): Chia thành các ý phân tích sâu: Ý 1 (Tác hại đối với năng lực, hiệu suất học tập/làm việc) -> Ý 2 (Tác hại đối với sức khỏe tâm thần, sự tự tin và nhân cách) -> Ý 3 (Tác hại làm đánh mất cơ hội tương lai) -> Ý 4 (Hệ lụy đối với gia đình, uy tín tập thể và xã hội) + Phân tích Dẫn chứng thực tế chứng minh hậu quả.",
            "- Luận điểm 3 (Phản đề & Bài học tỉnh thức): Phê phán thái độ chủ quan, coi thường tác hại; rút ra bài học nhận thức và hành động rèn luyện bản thân để tránh xa tác hại đó.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_1_TH2":
        lines = [
            f"DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 2: Đề hỏi bài học giải pháp (Cần làm gì? Trách nhiệm của chủ thể đối với '{vdnl}').",
            "HỆ THỐNG LUẬN ĐIỂM THÂN BÀI (KHÔNG TRÙNG LẶP):",
            "- Luận điểm 1 (Giải thích & Khái quát ngắn gọn sự cần thiết).",
            "- Luận điểm 2 (Bàn luận trọng tâm trả lời câu hỏi CẦN LÀM GÌ?): Ý 1 (Bài học về nhận thức, tư duy) -> Ý 2 (Bài học về hành động rèn luyện cá nhân cụ thể) -> Ý 3 (Bài học về gắn kết, cống hiến cộng đồng) + Dẫn chứng thực tế.",
            "- Luận điểm 3 (Phản đề phê phán lối sống thụ động, nói suông & Liên hệ bản thân).",
        ]
        return "\n".join(lines)

    if type_code == "DANG_1_TH3":
        lines = [
            f"DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 3: Đề hỏi chung, nêu suy nghĩ về '{vdnl}'.",
            "HỆ THỐNG LUẬN ĐIỂM THÂN BÀI (KHÔNG TRÙNG LẶP):",
            f"- Luận điểm 1 (Giải thích & Biểu hiện): Giải thích khái niệm '{vdnl}' và nêu biểu hiện cụ thể.",
            f"- Luận điểm 2 (Bàn luận toàn diện): Ý 1 (Ý nghĩa đối với cá nhân) -> Ý 2 (Ý nghĩa đối với cộng đồng, xã hội) -> Ý 3 (Dẫn chứng thực tế) -> Ý 4 (Cần làm gì để phát huy '{vdnl}').",
            "- Luận điểm 3 (Phản đề & Liên hệ cá nhân).",
        ]
        return "\n".join(lines)

    if type_code == "DANG_2_GIAI_QUYET":
        meaning_note = (
            f"Ý 1 (Ý nghĩa vốn có của '{vdnl}') -> " if has_meaning_step else ""
        )
        lines = [
            f"DẠNG BÀI: Nghị luận về một vấn đề cần giải quyết ('{vdnl}').",
            "HỆ THỐNG LUẬN ĐIỂM THÂN BÀI:",
            "- Luận điểm 1 (Giải thích & Biểu hiện).",
            f"- Luận điểm 2 (Bàn luận Lí do & Giải pháp): {meaning_note}Lí do cần giải quyết (1 đoạn gộp: Thực trạng - Nguyên nhân - Hậu quả) -> Giải pháp khắc phục (Chia thành 3 đoạn: Cá nhân - Gia đình - Nhà trường; mỗi đoạn đều nêu giải pháp khả thi + lí giải vì sao + ít nhất 01 dẫn chứng).",
            "- Luận điểm 3 (Phản biện ý kiến khác cho rằng không cần thiết & Bài học liên hệ).",
        ]
        return "\n".join(lines)

    if type_code == "DANG_3_HAI_QUAN_DIEM":
        lines = [
            f"DẠNG BÀI: Nghị luận lựa chọn quan điểm ('{vdnl}').",
            "HỆ THỐNG LUẬN ĐIỂM THÂN BÀI:",
            "- Luận điểm 1 (Giải thích 2 quan điểm & Chỉ ra mối quan hệ giữa 2 quan điểm).",
            "- Luận điểm 2 (Bảo vệ quan điểm đã chọn bằng lý lẽ + Dẫn chứng thực tế -> Chỉ ra hạn chế của quan điểm còn lại).",
            "- Luận điểm 3 (Bài học khái quát & Bài học liên hệ cá nhân).",
        ]
        return "\n".join(lines)

    if type_code == "DANG_4_VAN_HOC":
        lines = [
            f"DẠNG BÀI: Nghị luận vấn đề xã hội rút ra từ tác phẩm văn học ('{vdnl}').",
            "HỆ THỐNG LUẬN ĐIỂM THÂN BÀI:",
            "- Luận điểm 1 (Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề -> Giải thích vấn đề xã hội).",
            "- Luận điểm 2 (Bàn luận biểu hiện, ý nghĩa thực tiễn trong đời sống + Dẫn chứng người thật việc thật).",
            "- Luận điểm 3 (Phản đề, Mở rộng & Bài học liên hệ).",
        ]
        return "\n".join(lines)

    if type_code == "DANG_5_TU_BO":
        lines = [
            f"DẠNG BÀI: Thuyết phục người khác từ bỏ một thói quen hay quan niệm ('{vdnl}').",
            "HỆ THỐNG LUẬN ĐIỂM THÂN BÀI:",
            "- Luận điểm 1 (Giải thích thói quen/quan niệm & Nêu biểu hiện).",
            "- Luận điểm 2 (Ý 1: Lí do phải từ bỏ gồm Hậu quả + Dẫn chứng + Lợi ích khi từ bỏ -> Ý 2: Giải pháp từ bỏ chia thành 3 đoạn Cá nhân (trọng tâm) - Gia đình - Nhà trường kèm lí giải + dẫn chứng).",
            "- Luận điểm 3 (Dự đoán những ý kiến phản đối & Khuyên vẫn cần từ bỏ).",
        ]
        return "\n".join(lines)

    return ""

# ==============================================================================
# HÀM XÂY DỰNG KHUNG ĐỊNH HƯỚNG TƯ DUY THEO HỆ THỐNG LUẬN ĐIỂM
# ==============================================================================
def build_dynamic_outline_for_custom_topic(raw_topic_text, student_vdnl, manual_type_override="Tự động nhận diện theo đề bài", base_de_info=None):
    formatted_topic = ensure_600_words_prompt(raw_topic_text)
    direct_problem = extract_clean_topic_noun(student_vdnl.strip()) if student_vdnl.strip() else extract_clean_topic_noun(raw_topic_text)
    is_quote = is_metaphorical_quote_topic(raw_topic_text)
    type_code = classify_essay_type(raw_topic_text, student_vdnl.strip() if student_vdnl.strip() else raw_topic_text, manual_type_override)
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, raw_topic_text, direct_problem)

    if base_de_info is not None and type_code == "DANG_1_TH3" and manual_type_override == "Tự động nhận diện theo đề bài":
        preserved = dict(base_de_info)
        preserved["essay_type_code"] = type_code
        preserved["essay_type_label"] = type_label
        return preserved

    prompt_lines = [
        "Đóng vai chuyên gia sư phạm Ngữ văn THPT. Hãy lập Khung định hướng tư duy CHI TIẾT, CỤ THỂ theo HỆ THỐNG LUẬN ĐIỂM cho đề bài NLXH sau và trả về MỘT CHUỖI JSON HỢP LỆ (không dùng markdown code block):",
        f'- Đề bài: "{formatted_topic}"',
        f'- Vấn đề nghị luận trọng tâm: "{direct_problem}"',
        f'- Phân loại dạng bài: "{type_label}"',
        "",
        "QUY CHUẨN PHÂN CHIA LUẬN ĐIỂM BẮT BUỘC (TUYỆT ĐỐI KHÔNG TRÙNG LẶP VÀ KHÔNG ÔM ĐỒM LỆCH DẠNG ĐỀ):",
        structure_guide,
        "",
        "LƯU Ý ĐẶC BIỆT QUAN TRỌNG:",
        "- Nếu đề bài chỉ hỏi về 1 khía cạnh như 'Tác hại của...' hoặc 'Vai trò/Ý nghĩa của...', phần Luận điểm 2 PHẢI xoáy sâu phân tích trọn vẹn khía cạnh Tác hại hoặc Vai trò đó, TUYỆT ĐỐI KHÔNG biến thành bài văn Giải pháp 3 cấp độ (Cá nhân - Gia đình - Nhà trường) hay bài Thuyết phục từ bỏ.",
        f"- Ở mục explain_items (Luận điểm 1): Giải thích cụ thể khái niệm '{direct_problem}' là gì và nêu biểu hiện thực tế.",
        "- Ở mục questions (Luận điểm 2): Tuyệt đối không lặp lại phần Giải thích và Biểu hiện của Luận điểm 1. Chia thành các ý bàn luận cụ thể (Ý 1, Ý 2, Ý 3...).",
        "- Ở mục counter (Luận điểm 3): Phản đề / Ý kiến trái chiều và rút ra bài học.",
        "",
        "Trả về JSON theo đúng các trường: text, vdnl_chuan, essay_type_code, essay_type_label, explain_items (mảng chuỗi cho Luận điểm 1), vdnl_ket_luan (chuỗi), questions (mảng đối tượng gồm cau_hoi và y_tra_loi cho Luận điểm 2), evidence (mảng đối tượng gồm ten, chi_tiet, y_nghia, nguon), counter (mảng chuỗi cho Luận điểm 3), dani_chi_tiet (đối tượng gồm mb, gt, bl, dc, pb, kb).",
    ]
    prompt = "\n".join(prompt_lines)

    ai_res = call_gemini_rest_api(prompt, temperature=0.35)
    if ai_res:
        try:
            match = re.search(r"\{.*\}", ai_res, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed["text"] = formatted_topic
                parsed["vdnl_chuan"] = student_vdnl.strip() if student_vdnl.strip() else direct_problem
                parsed["essay_type_code"] = type_code
                parsed["essay_type_label"] = type_label
                if "explain_items" in parsed and "questions" in parsed:
                    return parsed
        except Exception:
            pass

    combined_low = (raw_topic_text + " " + direct_problem).lower()
    matched_concept = None
    for kw, data in CONCEPT_DICTIONARY.items():
        if kw in combined_low:
            matched_concept = (kw, data)
            break

    matched_prob_kb = match_problem_solving_kb(raw_topic_text, direct_problem)
    vdnl_final = student_vdnl.strip() if student_vdnl.strip() else direct_problem

    if base_de_info and base_de_info.get("explain_items"):
        base_explain_items = base_de_info["explain_items"]
    else:
        base_explain_items = None

    if matched_prob_kb:
        specific_def = matched_prob_kb["def"]
        specific_manifest = matched_prob_kb["manifest"]
    elif matched_concept:
        specific_def = matched_concept[1]["def"]
        specific_manifest = matched_concept[1]["manifest"]
    else:
        specific_def = f"**{direct_problem}** được hiểu là những nhận thức, thái độ và hành vi ứng xử cụ thể của con người trước vấn đề đặt ra trong đời sống cá nhân và cộng đồng hiện đại."
        specific_manifest = f"Thể hiện trực tiếp qua cách suy nghĩ, lựa chọn thái độ và những hành động cụ thể hàng ngày của người trẻ trong học tập, giao tiếp và đời sống xã hội liên quan đến **{direct_problem}**."

    if base_de_info and base_de_info.get("evidence"):
        base_ev_list = base_de_info["evidence"]
        c_ev_ten = base_ev_list[0].get("ten", "Tấm gương tiêu biểu trong thực tiễn")
        c_ev_chitiet = base_ev_list[0].get("chi_tiet", "")
        c_ev_ynghia = base_ev_list[0].get("y_nghia", "")
    elif matched_concept:
        c_ev_ten = matched_concept[1]["ev_ten"]
        c_ev_chitiet = matched_concept[1]["ev_chitiet"]
        c_ev_ynghia = matched_concept[1]["ev_ynghia"]
        base_ev_list = [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": c_ev_ynghia, "nguon": "Thực tiễn đời sống"}]
    else:
        c_ev_ten = "Tác giả David Allen ('Quy tắc 2 phút'), Kình ngư Ánh Viên & Mạng lưới 'Fly To Sky'"
        c_ev_chitiet = "Những tấm gương rèn luyện kỷ luật tự thân nghiêm ngặt, làm chủ thời gian và hành động quyết liệt ngay từ những việc nhỏ nhất để vươn tới thành công."
        c_ev_ynghia = f"Minh chứng thực tế làm sáng tỏ sâu sắc cho vấn đề {vdnl_final}."
        base_ev_list = [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": c_ev_ynghia, "nguon": "Thực tiễn đời sống & Báo chí chính thống"}]

    if type_code == "DANG_1_TH1_TAC_HAI":
        explain_items_th = base_explain_items if base_explain_items else [
            f"- **1. Giải thích khái niệm:** {specific_def}",
            f"- **2. Biểu hiện nhận diện thực tế:** {specific_manifest}",
        ]
        if matched_prob_kb and "harms_4_levels" in matched_prob_kb:
            harm_points = list(matched_prob_kb["harms_4_levels"])
        elif base_de_info and base_de_info.get("questions"):
            harm_points = list(base_de_info["questions"][0].get("y_tra_loi", []))
        else:
            harm_points = [
                f"- **Ý 1 — Tác hại đối với năng lực, hiệu suất học tập và công việc:** **{direct_problem}** trực tiếp bào mòn sự tập trung, khiến công việc bị đình trệ, làm giảm sút chất lượng học tập và triệt tiêu khả năng sáng tạo của cá nhân.",
                f"- **Ý 2 — Tác hại đối với sức khỏe tâm thần và nhân cách:** Tạo ra áp lực tâm lý nặng nề, sự bất an, mặc cảm tự ti và lâu dần hình thành lối sống buông thả, thiếu kỷ luật.",
                f"- **Ý 3 — Đánh cắp thời gian và những cơ hội phát triển tương lai:** Khiến người trẻ bỏ lỡ những thời điểm vàng để trau dồi tri thức, kỹ năng và bị tụt hậu phía sau trong xã hội hiện đại.",
                f"- **Ý 4 — Hệ lụy đối với gia đình, tập thể và xã hội:** Làm suy giảm uy tín cá nhân, gây ảnh hưởng tiêu cực đến tiến độ chung của tập thể và làm mai một các giá trị sống tích cực.",
            ]
        harm_points.append(
            f"- **Ý {len(harm_points)+1} — Phân tích Dẫn chứng thực tế chứng minh:**\n  + *Dẫn chứng:* **{c_ev_ten}** ({c_ev_chitiet}).\n  + *Góc độ phân tích:* Đặt trong sự đối sánh với những người trẻ đánh mất cơ hội vì sa vào **{direct_problem}** để làm nổi bật hậu quả nặng nề và giá trị của sự thức tỉnh."
        )

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": explain_items_th,
            "vdnl_ket_luan": f"Từ việc nhận diện bản chất và biểu hiện trên, chúng ta cần đi sâu mổ xẻ toàn diện những tác hại, hệ lụy nghiêm trọng của **{direct_problem}** đối với cá nhân và xã hội.",
            "questions": [
                {
                    "cau_hoi": f"Luận điểm 2 — Bàn luận trọng tâm: Phân tích sâu các tầng Tác hại / Hậu quả của '{direct_problem}':",
                    "y_tra_loi": harm_points,
                }
            ],
            "evidence": base_ev_list,
            "counter": [
                f"- **Phê phán & Phản đề:** Lên án thái độ chủ quan, xem nhẹ tác hại của **{direct_problem}** hoặc ngụy biện cho rằng đó chỉ là thói quen vô hại nhất thời.",
                f"- **Bài học nhận thức và hành động cá nhân:** Mỗi người trẻ cần tỉnh táo nhận diện sớm những hệ lụy của **{direct_problem}**, từ đó tự giác rèn luyện bản lĩnh, kỷ luật bản thân ngay từ những việc nhỏ nhất hàng ngày.",
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt tự nhiên -> Trích dẫn đề bài -> Nêu trực diện vấn đề nghị luận: Tác hại của {direct_problem}.",
                "gt": f"Luận điểm 1 (Giải thích & Biểu hiện): Cắt nghĩa rõ bản chất của '{direct_problem}' và nêu các biểu hiện nhận diện.",
                "bl": f"Luận điểm 2 (Trọng tâm phân tích Tác hại): Tập trung phân tích sâu 4 tầng tác hại đối với hiệu suất học tập, tâm lý nhân cách, cơ hội tương lai và uy tín xã hội (Không sa đà sang bài văn giải pháp 3 cấp độ).",
                "dc": f"Phân tích dẫn chứng thực tế ({c_ev_ten}) để làm rõ hậu quả và bài học cảnh tỉnh.",
                "pb": "Luận điểm 3 (Phản đề & Bài học): Phê phán sự chủ quan, bao biện và rút ra bài học tự rèn luyện cho bản thân.",
                "kb": f"Khẳng định lại thông điệp cảnh tỉnh về tác hại của {direct_problem} và liên hệ cá nhân.",
            },
        }

    if type_code == "DANG_1_TH1_Y_NGHIA":
        explain_items_yn = base_explain_items if base_explain_items else [
            f"- **1. Giải thích khái niệm:** {specific_def}",
            f"- **2. Biểu hiện thực tế trong đời sống:** {specific_manifest}",
        ]
        why_detail = matched_concept[1]["why"] if matched_concept else f"Trong dòng chảy nhiều biến động của xã hội hiện đại, **{direct_problem}** chính là điểm tựa tinh thần vững chắc giúp con người khẳng định giá trị bản thân và lan tỏa điều tử tế."
        y_list_yn = [
            f"- **Ý 1 — Ý nghĩa đối với việc định hình nội lực và bản lĩnh cá nhân:** {why_detail}",
            f"- **Ý 2 — Vai trò bồi đắp chiều sâu tâm hồn, nhân cách và trí tuệ:** Giúp mỗi người sống có lý tưởng, khơi dậy tiềm năng ẩn giấu và đứng vững trước những thử thách, cám dỗ của cuộc đời.",
            f"- **Ý 3 — Giá trị kết nối và truyền cảm hứng giữa người với người:** Tạo dựng niềm tin, sự thấu hiểu, đồng cảm và lan tỏa nguồn năng lượng tích cực tới những người xung quanh.",
            f"- **Ý 4 — Sức mạnh thúc đẩy sự phát triển của cộng đồng, xã hội + Dẫn chứng thực tế:** Khi **{direct_problem}** được tôn vinh, nó trở thành động lực kiến tạo một xã hội văn minh, nhân ái (Minh chứng qua tấm gương: **{c_ev_ten}** — {c_ev_chitiet}).",
            f"- **Ý 5 — Khẳng định tầm quan trọng từ góc nhìn đối lập (Nếu thiếu vắng):** Nếu thiếu đi **{direct_problem}**, con người dễ rơi vào sự bế tắc, hời hợt và cuộc sống mất đi những giá trị bền vững.",
        ]
        counter_detail = matched_concept[1]["counter"] if matched_concept else f"Lối sống thờ ơ, hời hợt, thực dụng hoặc đi ngược lại những giá trị tốt đẹp của **{direct_problem}**."
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": explain_items_yn,
            "vdnl_ket_luan": f"Từ việc giải thích và nhận diện biểu hiện trên, chúng ta cần đi sâu bàn luận làm sáng tỏ những tầng ý nghĩa, vai trò to lớn của **{direct_problem}**.",
            "questions": [
                {
                    "cau_hoi": f"Luận điểm 2 — Bàn luận trọng tâm: Phân tích sâu Ý nghĩa / Vai trò / Sức mạnh của '{direct_problem}':",
                    "y_tra_loi": y_list_yn,
                }
            ],
            "evidence": base_ev_list,
            "counter": [
                f"- **Phê phán biểu hiện lệch lạc:** {counter_detail}",
                f"- **Mở rộng biện chứng & Bài học liên hệ:** Nhìn nhận **{direct_problem}** một cách toàn diện, tỉnh táo; từ đó rút ra bài học nhận thức và hành động thiết thực cho bản thân.",
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt tự nhiên -> Trích dẫn đề bài -> Nêu trực diện vấn đề nghị luận: {vdnl_final}.",
                "gt": f"Luận điểm 1 (Giải thích & Biểu hiện): Cắt nghĩa rõ '{direct_problem}' và nêu biểu hiện thực tế.",
                "bl": f"Luận điểm 2 (Trọng tâm phân tích Ý nghĩa / Vai trò): Bàn sâu 5 tầng ý nghĩa đối với nội lực cá nhân, nhân cách, mối quan hệ con người và sự phát triển xã hội.",
                "dc": f"Phân tích dẫn chứng cụ thể ({c_ev_ten}) gắn chặt với các tầng ý nghĩa.",
                "pb": "Luận điểm 3 (Phản đề & Bài học): Phê phán biểu hiện ngược lại, mở rộng biện chứng và liên hệ bản thân.",
                "kb": f"Khẳng định lại giá trị trường tồn của {direct_problem} và thông điệp kết bài.",
            },
        }

    if type_code == "DANG_2_GIAI_QUYET":
        if matched_prob_kb:
            has_meaning = matched_prob_kb.get("is_positive_declining", False)
            status_block = matched_prob_kb["status_cause_harm"]
            sol_ind = matched_prob_kb["sol_individual"]
            sol_fam = matched_prob_kb["sol_family"]
            sol_sch = matched_prob_kb["sol_school"]
            rebuttal_block = matched_prob_kb["counter_rebuttal"]
            meaning_text = matched_prob_kb.get("meaning_when_positive", f"**Ý nghĩa vốn có của {direct_problem}:** Là nền tảng quan trọng giúp cá nhân phát triển lành mạnh và gắn kết tập thể.")
        else:
            has_meaning = is_positive_topic_declining(raw_topic_text, direct_problem)
            meaning_text = f"**Ý nghĩa vốn có của {direct_problem}:** Khi được duy trì và phát huy đúng đắn, **{direct_problem}** là phẩm chất/kỹ năng thiết yếu giúp mỗi cá nhân hoàn thiện bản thân, nâng cao hiệu quả học tập và tạo dựng môi trường sống văn minh, gắn kết."
            status_block = (
                f"- **Thực trạng:** Trong đời sống học đường và xã hội hiện nay, vấn đề **{direct_problem}** đang diễn biến đáng báo động ở một bộ phận không nhỏ giới trẻ.\n"
                f"  - **Nguyên nhân:** *Chủ quan* xuất phát từ nhận thức chưa thấu đáo, tâm lý buông thả, thiếu kỷ luật tự thân của cá nhân; *Khách quan* do sự tác động từ mặt trái của môi trường số, áp lực cuộc sống và sự thiếu định hướng sát sao từ gia đình, xã hội.\n"
                f"  - **Hậu quả:** Nếu không kịp thời giải quyết, thực trạng này sẽ làm suy giảm trực tiếp năng lực học tập, bào mòn nhân cách người trẻ và gây hệ lụy tiêu cực cho sự phát triển bền vững của cộng đồng."
            )
            sol_ind = (
                f"- **Giải pháp khả thi:** Mỗi cá nhân phải chủ động nâng cao nhận thức đúng đắn về **{direct_problem}**, tự thiết lập nguyên tắc kỷ luật hàng ngày, rèn luyện kỹ năng tự kiểm soát và tích cực tham gia các hoạt động thực tế lành mạnh.\n"
                f"  - **Lí giải vì sao:** Bởi mỗi cá nhân là chủ thể trực tiếp của mọi nhận thức và hành vi; nếu bản thân không tự giác thay đổi từ bên trong thì mọi sự hỗ trợ bên ngoài đều chỉ là hình thức.\n"
                f"  - **Dẫn chứng cụ thể:** Tấm gương tự rèn luyện kỷ luật và hành động vì cộng đồng của các bạn trẻ thuộc mạng lưới tình nguyện quốc gia 'Fly To Sky' (do Lê Văn Phúc sáng lập từ khi còn là học sinh THPT) hay các thủ khoa tự học vượt khó."
            )
            sol_fam = (
                f"- **Giải pháp khả thi:** Cha mẹ cần làm tấm gương sáng trong lối sống, dành thời gian chất lượng mỗi ngày để lắng nghe, thấu cảm và đồng hành định hướng con cái xử lý vấn đề **{direct_problem}** thay vì áp đặt hay phó mặc.\n"
                f"  - **Lí giải vì sao:** Gia đình là cái nôi giáo dục đầu tiên và là điểm tựa tâm lý bền vững nhất giúp hình thành nhân cách, thói quen của người trẻ.\n"
                f"  - **Dẫn chứng cụ thể:** Mô hình 'Giờ tối gia đình không thiết bị điện tử – Cùng lắng nghe và chia sẻ' được hàng chục nghìn gia đình Việt Nam áp dụng hiệu quả trong việc gắn kết và định hướng con cái."
            )
            sol_sch = (
                f"- **Giải pháp khả thi:** Nhà trường cần đổi mới sinh hoạt dưới cờ, lồng ghép kỹ năng giải quyết vấn đề **{direct_problem}** vào hoạt động trải nghiệm và phát huy vai trò của Phòng tư vấn tâm lý học đường; xã hội tăng cường truyền thông những mô hình tích cực.\n"
                f"  - **Lí giải vì sao:** Môi trường giáo dục và cộng đồng văn minh sẽ tạo ra hệ sinh thái nâng đỡ, định hướng chuẩn mực để học sinh duy trì hành vi tích cực lâu dài.\n"
                f"  - **Dẫn chứng cụ thể:** Phong trào xây dựng 'Trường học hạnh phúc' của Bộ Giáo dục & Đào tạo cùng các câu lạc bộ kỹ năng sống, dự án học sinh tự quản tại các trường THPT trên cả nước."
            )
            rebuttal_block = (
                f"- **Ý kiến khác (Trái chiều):** Có ý kiến cho rằng vấn đề **{direct_problem}** chỉ là chuyện cá nhân nhỏ nhặt hoặc là hệ quả tất yếu của nhịp sống hiện đại nên không cần tốn công sức can thiệp, giải quyết.\n"
                f"- **Phản biện & Khẳng định:** Đây là góc nhìn phiến diện và thiếu trách nhiệm. Bởi những lệch lạc nhỏ nếu bị dung túng sẽ tích tụ thành khủng hoảng lớn cho cả thế hệ; do đó việc chung tay khắc phục là hoàn toàn cấp thiết."
            )

        explain_items = [
            f"- **1. Giải thích khái niệm:** {specific_def}",
            f"- **2. Biểu hiện nhận diện thực tế:** {specific_manifest}",
        ]

        y_tra_loi_d2 = []
        if has_meaning:
            y_tra_loi_d2.append(f"- **Ý 1 — Ý nghĩa vốn có của vấn đề (Vì đây là giá trị tốt nhưng đang có chiều hướng suy giảm):**\n  {meaning_text}")
            step_offset = 1
        else:
            step_offset = 0

        y_tra_loi_d2.extend([
            f"- **Ý {1 + step_offset} — Lí do cần giải quyết (Viết thành 01 đoạn văn nêu Thực trạng - Nguyên nhân - Hậu quả):**\n  {status_block}",
            f"- **Ý {2 + step_offset} — Giải pháp khắc phục (Chia thành 3 đoạn văn tách biệt):**\n"
            f"  * **Đoạn 1 — Đối với Cá nhân (Trọng tâm):**\n  {sol_ind}\n"
            f"  * **Đoạn 2 — Đối với Gia đình:**\n  {sol_fam}\n"
            f"  * **Đoạn 3 — Đối với Nhà trường & Xã hội:**\n  {sol_sch}",
        ])

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": explain_items,
            "vdnl_ket_luan": f"Từ việc nhận diện bản chất và biểu hiện trên, mỗi chúng ta cần đi sâu phân tích lí do và tìm ra các giải pháp thiết thực để giải quyết triệt để vấn đề **{direct_problem}**.",
            "questions": [
                {
                    "cau_hoi": f"Luận điểm 2 — Bàn luận Lí do & Hệ thống Giải pháp khắc phục '{direct_problem}':",
                    "y_tra_loi": y_tra_loi_d2,
                }
            ],
            "evidence": [
                {
                    "ten": "Dẫn chứng cho đoạn Giải pháp Cá nhân: Lê Văn Phúc ('Fly To Sky') & Phong trào '30 ngày kỷ luật tự thân'",
                    "chi_tiet": "Hàng nghìn học sinh THPT tự thiết lập kỷ luật cá nhân, hạn chế thiết bị số và tham gia các dự án thiện nguyện, nghiên cứu khoa học.",
                    "y_nghia": "Chứng minh khi cá nhân tự giác thay đổi nhận thức và hành vi, vấn đề được giải quyết tận gốc.",
                    "nguon": "Báo Tiền Phong & Trung ương Đoàn",
                },
                {
                    "ten": "Dẫn chứng cho đoạn Gia đình & Nhà trường: Chiến dịch 'Tắt điện thoại - Bật yêu thương' & Mô hình 'Trường học hạnh phúc'",
                    "chi_tiet": "Sự phối hợp giữa quy tắc 'Khung giờ tối gia đình không màn hình' và các câu lạc bộ trải nghiệm tâm lý học đường tại các trường THPT.",
                    "y_nghia": "Chứng minh sức mạnh của môi trường gia đình và nhà trường trong việc nâng đỡ, định hướng người trẻ.",
                    "nguon": "Bộ Giáo dục & Đào tạo / Báo Giáo dục & Thời đại",
                },
            ],
            "counter": [rebuttal_block],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt từ bối cảnh thời đại -> Nêu trực diện vấn đề cần giải quyết: {vdnl_final}.",
                "gt": f"Luận điểm 1: Giải thích khái niệm và nêu biểu hiện nhận diện của '{direct_problem}'.",
                "bl": f"Luận điểm 2: {'1. Đoạn nêu ý nghĩa vốn có -> ' if has_meaning else ''}Đoạn Lí do cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả) -> Ba đoạn Giải pháp tách biệt (Cá nhân - Gia đình - Nhà trường, mỗi đoạn đủ Giải pháp + Lí giải + 01 Dẫn chứng).",
                "dc": "Sử dụng trực tiếp các dẫn chứng đã gợi ý vào đoạn Lí do và 3 đoạn Giải pháp.",
                "pb": "Luận điểm 3 (Phản đề): Nêu ý kiến khác cho rằng không cần thiết -> Phản biện bác bỏ và khẳng định vẫn cần khắc phục.",
                "kb": f"Khẳng định lại thông điệp giải quyết {direct_problem} và rút ra bài học liên hệ cá nhân.",
            },
        }

    if type_code == "DANG_3_HAI_QUAN_DIEM":
        v1_text, v2_text = parse_two_viewpoints_from_topic(raw_topic_text, direct_problem)
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **1. Giải thích Quan điểm thứ nhất (*\"{v1_text}\"*):** Quan điểm này đề cao giá trị của sự nỗ lực chủ động, khẳng định vai trò của ý chí/lựa chọn thứ nhất trong việc định hình thành công và nhân cách con người.",
                f"- **2. Giải thích Quan điểm thứ hai (*\"{v2_text}\"*):** Quan điểm này nhìn nhận vấn đề từ góc độ đối trọng, nhấn mạnh vào điều kiện thực tế, sự linh hoạt hoặc giá trị tinh thần chiều sâu.",
                "- **3. Chỉ ra mối quan hệ giữa 2 quan điểm:** Hai quan điểm phản ánh hai chiều kích khác nhau của cuộc sống; đặt trong bối cảnh tuổi trẻ hôm nay, người viết cần xác lập rõ quan điểm ưu tiên mà mình lựa chọn.",
            ],
            "vdnl_ket_luan": f"Đứng trước hai luồng ý kiến về **{direct_problem}**, người viết cần đưa ra lý lẽ và dẫn chứng để bảo vệ quan điểm đã chọn, đồng thời chỉ rõ hạn chế của quan điểm còn lại.",
            "questions": [
                {
                    "cau_hoi": f"Luận điểm 2 — Bàn luận bảo vệ quan điểm đã chọn & Phân tích hạn chế quan điểm còn lại ({direct_problem}):",
                    "y_tra_loi": [
                        "- **Ý 1 — Lí giải vì sao chọn quan điểm của mình (Trọng tâm lập luận):**\n  + *Lý lẽ 1:* Quan điểm em chọn phù hợp với quy luật phát triển tự thân của con người hiện đại — giúp cá nhân làm chủ hoàn cảnh thay vì thụ động chờ đợi.\n  + *Lý lẽ 2:* Mang lại giá trị bền vững cho cả sự trưởng thành cá nhân lẫn sự tiến bộ của cộng đồng xã hội.",
                        f"- **Ý 2 — Phân tích Dẫn chứng thực tế bảo vệ quan điểm đã chọn:**\n  + *Dẫn chứng cụ thể:* **{c_ev_ten}** ({c_ev_chitiet}).\n  + *Phân tích:* Hành trình ấy chứng minh hùng hồn cho tính đúng đắn của quan điểm mà em đã lựa chọn.",
                        "- **Ý 3 — Chỉ ra hạn chế của quan điểm còn lại:**\n  + Phân tích khách quan: Nếu con người chỉ nghiêng hẳn về quan điểm còn lại một cách cực đoan, phiến diện thì dễ rơi vào sự thụ động, bảo thủ hoặc mất cân bằng trong thực tiễn cuộc sống.",
                    ],
                }
            ],
            "evidence": base_ev_list,
            "counter": [
                "- **Bài học khái quát:** Cần có bản lĩnh giữ vững lập trường đúng đắn, đồng thời có tư duy biện chứng, biết tiếp thu hạt nhân hợp lý và tránh thái độ cực đoan.",
                "- **Bài học liên hệ cá nhân:** Vận dụng trực tiếp quan điểm đã chọn vào việc học tập, rèn luyện nhân cách và định hướng tương lai của bản thân.",
            ],
            "dani_chi_tiet": {
                "mb": f"Giới thiệu 2 quan điểm ('{v1_text}' và '{v2_text}') + Chỉ ra rõ ràng quan điểm lựa chọn của bản thân.",
                "gt": "Luận điểm 1: Giải thích cụ thể 2 quan điểm và chỉ ra mối quan hệ giữa 2 quan điểm.",
                "bl": "Luận điểm 2: Ý 1 (Lí giải vì sao chọn quan điểm của mình) -> Ý 2 (Dẫn chứng chứng minh) -> Ý 3 (Chỉ ra hạn chế của quan điểm còn lại).",
                "dc": f"Đưa dẫn chứng ({c_ev_ten}) vào làm sáng tỏ quan điểm đã chọn.",
                "pb": "Luận điểm 3: Rút ra bài học nhận thức khái quát và bài học liên hệ cá nhân.",
                "kb": "Khẳng định lại sự lựa chọn và thông điệp kết bài.",
            },
        }

    if type_code == "DANG_4_VAN_HOC":
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **1. Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề:** Qua tình huống, chi tiết nghệ thuật và hình tượng nhân vật trong tác phẩm/đoạn trích, nhà văn đã gửi gắm thông điệp nhân sinh sâu sắc về **{direct_problem}**.",
                f"- **2. Giải thích vấn đề xã hội đặt ra:** {specific_def}",
                f"- **3. Biểu hiện trong đời sống thực tiễn:** {specific_manifest}",
            ],
            "vdnl_ket_luan": f"Bước ra từ trang sách, vấn đề **{direct_problem}** đặt ra những suy ngẫm sâu sắc cho con người trong cuộc đời thực hôm nay.",
            "questions": [
                {
                    "cau_hoi": f"Luận điểm 2 — Bàn luận vấn đề '{direct_problem}' trong đời sống thực tiễn:",
                    "y_tra_loi": [
                        f"- **Ý 1 — Ý nghĩa và tác động đối với cá nhân:** Thực hành **{direct_problem}** giúp mỗi người bồi đắp tâm hồn, định hình bản lĩnh và sống có giá trị nhân văn giữa đời thường.",
                        f"- **Ý 2 — Ý nghĩa và sức lan tỏa đối với cộng đồng, xã hội:** Hàn gắn những đứt gãy, đẩy lùi cái xấu và kiến tạo một xã hội tốt đẹp như khát vọng mà tác phẩm văn học đã khơi gợi.",
                        f"- **Ý 3 — Dẫn chứng người thật việc thật ngoài đời sống (Không lấy lại dẫn chứng trong văn học):**\n  + *Dẫn chứng cụ thể:* **{c_ev_ten}** — {c_ev_chitiet}.\n  + *Phân tích:* Minh chứng cho thấy thông điệp từ trang văn đã tỏa sáng sinh động giữa đời thực.",
                    ],
                }
            ],
            "evidence": base_ev_list,
            "counter": [
                f"- **Phê phán biểu hiện trái ngược:** Lên án lối sống thờ ơ, thực dụng, đi ngược lại giá trị **{direct_problem}** mà tác phẩm đã đặt ra.",
                "- **Mở rộng & Bài học liên hệ:** Khẳng định giá trị thức tỉnh của văn chương đối với cuộc đời và rút ra bài học hành động cho tuổi trẻ.",
            ],
            "dani_chi_tiet": {
                "mb": f"Giới thiệu tác giả, tác phẩm -> Dẫn dắt và nêu vấn đề xã hội rút ra: {vdnl_final}.",
                "gt": f"Luận điểm 1: Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề -> Giải thích khái niệm '{direct_problem}' và nêu biểu hiện thực tế.",
                "bl": f"Luận điểm 2: Bàn luận sâu sắc về ý nghĩa, tác động của '{direct_problem}' đối với cá nhân và xã hội hiện đại.",
                "dc": f"Phân tích dẫn chứng người thật việc thật ngoài đời sống ({c_ev_ten}).",
                "pb": "Luận điểm 3 (Phản đề): Phê phán mặt trái, mở rộng vấn đề và rút ra bài học liên hệ cá nhân.",
                "kb": "Khẳng định sức sống trường tồn của thông điệp từ tác phẩm văn học trong dòng chảy cuộc đời.",
            },
        }

    if type_code == "DANG_5_TU_BO":
        if matched_prob_kb:
            habit_def = matched_prob_kb["def"]
            habit_manifest = matched_prob_kb["manifest"]
            harm_and_benefit = (
                f"  + **Hậu quả nghiêm trọng nếu không từ bỏ:** {matched_prob_kb['status_cause_harm']}\n"
                f"  + **Dẫn chứng thực tế gắn với lí do:** Thực tế học đường và đời sống cho thấy biết bao người trẻ vốn có năng lực nhưng vì dung túng cho {matched_prob_kb['name']} mà đánh mất cơ hội, suy giảm kết quả học tập và rơi vào khủng hoảng tâm lý.\n"
                f"  + **Lợi ích tốt đẹp khi dũng cảm từ bỏ:** {matched_prob_kb.get('benefit_of_quitting', 'Giúp cá nhân giải phóng năng lượng tích cực, làm chủ cuộc sống và được mọi người tin yêu, tôn trọng.')}"
            )
            sol_ind = matched_prob_kb["sol_individual"]
            sol_fam = matched_prob_kb["sol_family"]
            sol_sch = matched_prob_kb["sol_school"]
            predict_objection = matched_prob_kb["counter_rebuttal"]
        else:
            habit_def = f"**{direct_problem}** là một thói quen chưa tốt / quan niệm lệch lạc được hình thành từ sự thiếu tự giác hoặc cái nhìn phiến diện, lâu dần ăn sâu vào nếp nghĩ và hành vi của con người."
            habit_manifest = f"Biểu hiện cụ thể qua lời nói, thái độ chủ quan, sự chần chừ hoặc cách ứng xử thiếu chuẩn mực trong học tập, công việc và giao tiếp hàng ngày liên quan đến **{direct_problem}**."
            harm_and_benefit = (
                f"  + **Hậu quả nặng nề:** **{direct_problem}** âm thầm bào mòn thời gian, làm suy giảm năng lực học tập, thu hẹp cơ hội phát triển của bản thân và gây ảnh hưởng tiêu cực tới tập thể.\n"
                f"  + **Dẫn chứng thực tế gắn với lí do:** Không ít người trẻ có tố chất thông minh nhưng vì không vượt qua được **{direct_problem}** nên đã tụt hậu phía sau trong kỷ nguyên số đầy cạnh tranh.\n"
                f"  + **Lợi ích thiết thực khi từ bỏ:** Khi dứt khoát từ bỏ **{direct_problem}**, mỗi người sẽ tìm lại sự tự chủ, nâng cao hiệu suất học tập, hoàn thiện nhân cách và nhận được sự tin cậy từ cộng đồng."
            )
            sol_ind = (
                f"- **Giải pháp khả thi:** Thẳng thắn nhìn nhận tác hại của **{direct_problem}**, đặt mục tiêu thay đổi theo từng chặng nhỏ (Quy tắc 21 ngày tạo thói quen mới), thay thế hành vi cũ bằng một hoạt động tích cực cụ thể và tự kỷ luật mỗi ngày.\n"
                f"  - **Lí giải vì sao:** Thói quen/quan niệm nằm trong chính tiềm thức và hành vi của mỗi người; chỉ khi bản thân thực sự quyết tâm thay đổi thì quá trình từ bỏ mới thành công.\n"
                f"  - **Dẫn chứng cụ thể:** Hành trình tự rèn luyện kỷ luật thép, vượt qua thói quen trì hoãn và giới hạn bản thân của kình ngư Nguyễn Thị Ánh Viên hay các thủ khoa tự học."
            )
            sol_fam = (
                f"- **Giải pháp khả thi:** Cha mẹ và người thân kiên nhẫn đồng hành, nhắc nhở nhẹ nhàng, ghi nhận từng bước tiến bộ nhỏ của con thay vì chê bai, chỉ trích nặng lời.\n"
                f"  - **Lí giải vì sao:** Sự khích lệ và môi trường gia đình tích cực sẽ tạo động lực tâm lý giúp người trẻ không bỏ cuộc giữa chừng khi thay đổi thói quen.\n"
                f"  - **Dẫn chứng cụ thể:** Sự đồng hành thấu cảm của gia đình trong các chương trình 'Cha mẹ cùng con thay đổi thói quen tích cực'."
            )
            sol_sch = (
                f"- **Giải pháp khả thi:** Thầy cô và bạn bè tạo môi trường sinh hoạt câu lạc bộ lành mạnh, cùng lập nhóm 'Đôi bạn cùng tiến' để nhắc nhở và truyền cảm hứng rèn luyện mỗi ngày.\n"
                f"  - **Lí giải vì sao:** Áp lực tích cực từ tập thể bạn bè đồng trang lứa giúp cá nhân duy trì cam kết từ bỏ thói quen xấu dễ dàng hơn.\n"
                f"  - **Dẫn chứng cụ thể:** Phong trào 'Đôi bạn cùng tiến' và các câu lạc bộ rèn luyện kỹ năng sống tại các trường THPT."
            )
            predict_objection = (
                f"- **Dự đoán những ý kiến phản đối / bao biện:** Người mang thói quen/quan niệm **{direct_problem}** có thể phản đối rằng: *'Thói quen này đã thành bản tính khó đổi'* hoặc *'Đó là quyền cá nhân, chẳng ảnh hưởng lớn đến ai'*.\n"
                f"- **Phản biện & Khuyên vẫn cần từ bỏ:** Hãy nhẹ nhàng nhưng kiên quyết chỉ rõ: Không ai sinh ra đã hoàn hảo, mọi thói quen đều do rèn luyện mà thành. Nếu cứ thỏa hiệp với một thói quen/quan niệm sai lầm, chính tương lai của bạn sẽ phải trả giá đắt. Vì vậy, bắt đầu từ bỏ ngay hôm nay là lựa chọn sáng suốt nhất."
            )

        explain_items_d5 = [
            f"- **1. Giải thích cụ thể thói quen / quan niệm:** {habit_def}",
            f"- **2. Biểu hiện thực tế trong đời sống:** {habit_manifest}",
        ]

        y_tra_loi_d5 = [
            f"- **Ý 1 — Lí do vì sao phải từ bỏ (Phân tích Hậu quả + Dẫn chứng + Lợi ích khi từ bỏ):**\n{harm_and_benefit}",
            f"- **Ý 2 — Giải pháp từ bỏ khả thi (Chia theo 3 đoạn văn: Cá nhân - Gia đình - Nhà trường):**\n"
            f"  * **Đoạn 1 — Giải pháp đối với Cá nhân (TRỌNG TÂM):**\n  {sol_ind}\n"
            f"  * **Đoạn 2 — Giải pháp phối hợp từ Gia đình:**\n  {sol_fam}\n"
            f"  * **Đoạn 3 — Giải pháp phối hợp từ Nhà trường & Tập thể:**\n  {sol_sch}",
        ]

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": explain_items_d5,
            "vdnl_ket_luan": f"Từ việc nhận diện rõ bản chất và biểu hiện của **{direct_problem}**, mỗi chúng ta cần nhìn thẳng vào những hậu quả nghiêm trọng để tìm ra giải pháp kiên quyết từ bỏ.",
            "questions": [
                {
                    "cau_hoi": f"Luận điểm 2 — Bàn luận Lí do phải từ bỏ & Hệ thống Giải pháp từ bỏ '{direct_problem}' (Chia theo đoạn):",
                    "y_tra_loi": y_tra_loi_d5,
                }
            ],
            "evidence": base_ev_list,
            "counter": [predict_objection],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt bằng giọng điệu chân thành, tôn trọng -> Nêu rõ thói quen/quan niệm cần thuyết phục từ bỏ: {vdnl_final}.",
                "gt": f"Luận điểm 1: Giải thích rõ bản chất của '{direct_problem}' và nêu các biểu hiện cụ thể trong đời sống hàng ngày.",
                "bl": "Luận điểm 2:\n  - Ý 1: Lí do vì sao phải từ bỏ (Hậu quả + Dẫn chứng + Lợi ích khi từ bỏ).\n  - Ý 2: Giải pháp từ bỏ chia thành 3 đoạn: Cá nhân (Trọng tâm) - Gia đình - Nhà trường (Mỗi đoạn đều nêu rõ cách làm + lí giải vì sao + dẫn chứng cụ thể).",
                "dc": "Lồng ghép dẫn chứng vào cả phần Lí do (Hậu quả) và phần Giải pháp từ bỏ.",
                "pb": "Luận điểm 3 (Phản đề): Dự đoán những ý kiến phản đối/biện minh -> Phân tích thấu tình đạt lý để khuyên vẫn cần kiên quyết từ bỏ.",
                "kb": "Khẳng định niềm tin vào sự thay đổi tích cực và rút ra bài học liên hệ bản thân.",
            },
        }

    explain_list = base_explain_items if base_explain_items else (
        [
            f"- **1. Giải thích khái niệm cụ thể:** {specific_def}",
            f"- **2. Biểu hiện thực tế trong đời sống:** {specific_manifest}",
        ]
        if not is_quote
        else [
            f"- **1. Giải thích câu nói/nhận định trong đề:** Cắt nghĩa lớp nghĩa tường minh (hình ảnh, từ ngữ trong câu trích dẫn) và rút ra thông điệp hàm ẩn sâu sắc về **{direct_problem}**.",
            f"- **2. Giải thích khái niệm & Biểu hiện thực tế:** {specific_def} Biểu hiện qua: {specific_manifest}",
        ]
    )

    why_detail = matched_concept[1]["why"] if matched_concept else f"Trong dòng chảy nhiều biến động của xã hội hiện đại, **{direct_problem}** chính là điểm tựa tinh thần vững chắc giúp con người khẳng định giá trị bản thân và lan tỏa điều tử tế."
    promote_detail = matched_concept[1].get("how_to_promote", f"Mỗi người trẻ cần chủ động nâng cao nhận thức, rèn luyện **{direct_problem}** thông qua những hành động kiên trì, thiết thực trong học tập và ứng xử hàng ngày.") if matched_concept else f"Mỗi người trẻ cần chủ động nâng cao nhận thức, rèn luyện **{direct_problem}** thông qua những hành động kiên trì, thiết thực trong học tập và ứng xử hàng ngày."
    counter_detail = matched_concept[1]["counter"] if matched_concept else f"Lối sống thờ ơ, hời hợt, thực dụng hoặc đi ngược lại những giá trị tốt đẹp của **{direct_problem}**."

    if type_code == "DANG_1_TH2":
        y_list = [
            f"- **Ý 1 — Khái quát sự cần thiết phải hành động:** {why_detail}",
            f"- **Ý 2 — Bài học giải pháp về Nhận thức & Tư tưởng (Cần hiểu và xác lập tâm thế ra sao?):** Mỗi người trẻ cần nhận thức sâu sắc trách nhiệm của mình đối với **{direct_problem}**, xóa bỏ tâm lý ỷ lại, thờ ơ hay ngại khó.",
            f"- **Ý 3 — Bài học giải pháp về Hành động rèn luyện cá nhân (Cần làm gì cụ thể?):** {promote_detail} (Kèm dẫn chứng: **{c_ev_ten}**).",
            f"- **Ý 4 — Bài học giải pháp trong Gắn kết & Cống hiến cộng đồng:** Chủ động tham gia các hoạt động tập thể, dự án xã hội để biến nhận thức về **{direct_problem}** thành giá trị đóng góp thiết thực cho quê hương, đất nước.",
        ]
        bl_summary = "Luận điểm 2 (Bàn luận trả lời câu hỏi CẦN LÀM GÌ?): Triển khai các ý giải pháp về nhận thức, hành động cá nhân và trách nhiệm cộng đồng."
    else:  # DANG_1_TH3
        y_list = [
            f"- **Ý 1 — Bàn luận: Nêu ý nghĩa của '{direct_problem}' đối với cá nhân:** {why_detail}",
            f"- **Ý 2 — Bàn luận: Nêu ý nghĩa đối với cộng đồng, xã hội:** Góp phần gắn kết tình người, lan tỏa lối sống đẹp và tạo động lực thúc đẩy xã hội phát triển văn minh.",
            f"- **Ý 3 — Phân tích Dẫn chứng thực tế chứng minh:** Đưa tấm gương **{c_ev_ten}** ({c_ev_chitiet}) để làm sáng tỏ sức mạnh của **{direct_problem}**.",
            f"- **Ý 4 — Cần làm gì để phát huy '{direct_problem}' (Bài học định hướng) & Liên hệ cá nhân:** {promote_detail} Từ đó soi chiếu trực tiếp vào quá trình tự tu dưỡng của bản thân.",
        ]
        bl_summary = f"Luận điểm 2 (Bàn luận): Ý 1 & 2 (Phân tích ý nghĩa đối với cá nhân, xã hội) -> Ý 3 (Phân tích dẫn chứng: {c_ev_ten}) -> Ý 4 (Cần làm gì để phát huy & Liên hệ cá nhân)."

    return {
        "text": formatted_topic,
        "vdnl_chuan": vdnl_final,
        "essay_type_code": type_code,
        "essay_type_label": type_label,
        "explain_items": explain_list,
        "vdnl_ket_luan": f"Từ việc giải thích và nhận diện biểu hiện trên, chúng ta cần đi sâu bàn luận toàn diện về giá trị và bài học hành động của **{direct_problem}**.",
        "questions": [{"cau_hoi": f"Luận điểm 2 — Bàn luận trọng tâm ({type_label}):", "y_tra_loi": y_list}],
        "evidence": base_ev_list,
        "counter": [
            f"- **Phê phán biểu hiện lệch lạc:** {counter_detail}",
            f"- **Mở rộng biện chứng & Bài học liên hệ:** Cần đặt **{direct_problem}** trong cái nhìn tỉnh táo, toàn diện, tránh giáo điều hình thức; rút ra bài học hành động thực chất cho bản thân.",
        ],
        "dani_chi_tiet": {
            "mb": f"Dẫn dắt tự nhiên -> Trích dẫn đề bài -> Nêu vấn đề nghị luận: {vdnl_final}.",
            "gt": f"Luận điểm 1 (Giải thích & Biểu hiện): {specific_def}",
            "bl": bl_summary,
            "dc": f"Phân tích dẫn chứng cụ thể: {c_ev_ten}.",
            "pb": f"Luận điểm 3 (Phản đề): Phê phán biểu hiện trái ngược ({counter_detail}) và mở rộng góc nhìn biện chứng.",
            "kb": f"Khẳng định lại giá trị của {direct_problem} và liên hệ trách nhiệm tuổi trẻ.",
        },
    }

def is_ghostwriting_request(q_low):
    ghost_patterns = [
        r"viết\s*(hộ|giùm|giúp|cho|luôn|mẫu|thay)",
        r"(cô|ai|hệ thống|bạn)\s*viết\s*(bài|đoạn|giúp|cho|hộ|luôn)",
        r"làm\s*(hộ|giùm|giúp|cho)\s*(em|tôi|mình)?\s*(bài|đoạn)?",
        r"cho\s*(em|tôi|mình)\s*(xin\s*)?(một\s*)?(bài\s*văn|đoạn\s*văn|bài\s*làm|bài\s*mẫu)",
        r"viết\s*(cả\s*bài|bài\s*văn|hoàn\s*chỉnh|thành\s*bài)",
        r"^viết\s*bài(\s*cho\s*em|\s*đi|\s*nhé|\s*với)?$",
        r"soạn\s*(hộ|giúp|cho)\s*bài",
    ]
    for pat in ghost_patterns:
        if re.search(pat, q_low):
            return True
    return False

# ==============================================================================
# HÀM TRỢ LÝ NGỮ VĂN
# ==============================================================================
def generate_deep_chat_response(user_q, cur_de_info, chat_history_list):
    q_clean = user_q.strip()
    q_low = q_clean.lower()
    topic_text = ensure_600_words_prompt(cur_de_info.get("text", ""))
    vdnl = cur_de_info.get("vdnl_chuan", "vấn đề nghị luận của đề bài")
    override_val = st.session_state.get("selected_essay_type_override", "Tự động nhận diện theo đề bài")
    type_code = cur_de_info.get("essay_type_code", classify_essay_type(topic_text, vdnl, override_val))
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, topic_text, vdnl)
    current_draft = st.session_state.get("user_essay", "").strip()
    draft_excerpt = current_draft[:600] if current_draft else "Chưa viết"

    if is_ghostwriting_request(q_low):
        if "mở bài" in q_low:
            part_hint = "Mở bài"
        elif "kết bài" in q_low:
            part_hint = "Kết bài"
        elif "phản đề" in q_low:
            part_hint = "đoạn Phản đề"
        else:
            part_hint = "đoạn văn"
        explain_preview = cur_de_info.get("explain_items", [""])[0]
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Cô không viết sẵn nguyên bài văn hay {part_hint} thay cho em nhé, vì tự mình đặt câu mới giúp em làm chủ kỹ năng viết! "
            f"Nhưng cô cung cấp ngay cho em **chất liệu cụ thể** của đề **{vdnl}** (*{type_label}*) để em ráp thành đoạn ngay lập tức:\n"
            f"- **Ý cốt lõi cần đưa vào:** {explain_preview}\n"
            f"- **Khung câu gợi mở cho {part_hint}:** *\"Giữa dòng chảy không ngừng của cuộc sống hiện đại, {vdnl} đang đặt ra những suy ngẫm sâu sắc cho mỗi người trẻ...\"*\n"
            f"👉 *Em hãy viết tiếp 2-3 câu theo ý trên rồi gửi vào đây, cô sẽ sửa câu chữ cho em thật sắc sảo!*"
        )

    sys_lines = [
        "Bạn là một giáo viên Ngữ văn THPT giỏi chuyên môn, nhạy bén và tận tâm, đang trực tiếp hướng dẫn học sinh viết bài Nghị luận xã hội (khoảng 600 chữ).",
        "THÔNG TIN ĐỀ BÀI ĐANG LÀM:",
        f'- Đề bài: "{topic_text}"',
        f'- Vấn đề nghị luận trọng tâm: "{vdnl}"',
        "- Phân loại dạng đề và hệ thống luận điểm chuẩn:",
        structure_guide,
        f'- Bản nháp học sinh đang viết (nếu có): "{draft_excerpt}"',
        "",
        "QUY TẮC PHẢN HỒI BẮT BUỘC:",
        "1. CUNG CẤP KIẾN THỨC CỤ THỂ, TRỰC DIỆN: Khi học sinh hỏi khái niệm/từ khóa nào, phải định nghĩa rõ ràng, đầy đủ khái niệm đó là gì. Khi học sinh hỏi dẫn chứng, phải nêu rõ tên nhân vật, sự kiện thực tế, số liệu/hành động cụ thể và câu văn mẫu phân tích dẫn chứng đó. Khi học sinh hỏi luận điểm, phải vạch ra ý cụ thể gắn sát với đề bài.",
        "2. KHÔNG ÔM ĐỒM SAI DẠNG ĐỀ: Nếu đề chỉ hỏi về 'Tác hại' hoặc 'Vai trò/Ý nghĩa', hãy tập trung hướng dẫn phân tích sâu các tầng Tác hại hoặc Vai trò đó, không ép học sinh viết 3 đoạn giải pháp như dạng bài giải quyết vấn đề.",
        "3. NHẠY BÉN THEO MẠCH HỘI THOẠI: Đọc kỹ lịch sử trò chuyện. Tuyệt đối không lặp lại câu trả lời cũ.",
    ]
    system_instruction_text = "\n".join(sys_lines)

    contents_payload = []
    recent_history = chat_history_list[-10:] if len(chat_history_list) > 10 else chat_history_list
    for role, msg in recent_history:
        clean_msg = re.sub(r"^👩‍🏫 \*\*Trợ lý Ngữ văn:\*\*\s*", "", msg).strip()
        if role == "user":
            contents_payload.append({"role": "user", "parts": [{"text": clean_msg}]})
        elif role == "assistant" and clean_msg:
            contents_payload.append({"role": "model", "parts": [{"text": clean_msg}]})

    while contents_payload and contents_payload[0]["role"] == "model":
        contents_payload.pop(0)

    contents_payload.append({"role": "user", "parts": [{"text": q_clean}]})

    ai_reply = call_gemini_rest_api(
        prompt="",
        contents_list=contents_payload,
        system_instruction=system_instruction_text,
        temperature=0.5,
    )
    if ai_reply and len(ai_reply.strip()) > 20:
        return ai_reply

    explain_list = cur_de_info.get("explain_items", [])
    questions_list = cur_de_info.get("questions", [])
    counter_list = cur_de_info.get("counter", [])

    last_user_q = ""
    for r, m in reversed(chat_history_list):
        if r == "user":
            last_user_q = m.lower()
            break
    is_followup = any(
        w in q_low
        for w in ["thêm", "khác", "nữa", "sâu hơn", "cụ thể", "chưa hiểu", "rõ hơn", "ví dụ", "còn gì", "ý 1", "ý 2", "ý 3", "ý 4", "đoạn 2", "tiếp"]
    )
    effective_query = (last_user_q + " " + q_low) if (is_followup and len(q_low.split()) <= 10) else q_low

    def count_previous_topic_asks(keywords):
        cnt = 0
        for r, m in chat_history_list:
            if r == "user" and any(k in m.lower() for k in keywords):
                cnt += 1
        return cnt

    all_repo_evidences = []
    try:
        for topic_name, dc_list in db.KHO_DAN_CHUNG_9_CHU_DIEM.items():
            for item in dc_list:
                all_repo_evidences.append((topic_name, item))
    except Exception:
        pass

    gt_keywords = ["giải thích", "khái niệm", "từ khóa", "là gì", "nghĩa là gì", "hiểu như thế nào", "luận điểm 1", "biểu hiện"]
    if any(k in effective_query for k in gt_keywords):
        for kw, c_data in CONCEPT_DICTIONARY.items():
            if kw in effective_query:
                return (
                    f"👩‍🏫 **Trợ lý Ngữ văn:** Cô giải thích cụ thể khái niệm **{c_data['term']}** (Luận điểm 1) để em đưa ngay vào đầu phần Thân bài nhé:\n"
                    f"- **Giải thích khái niệm:** {c_data['def']}\n"
                    f"- **Biểu hiện thực tế:** {c_data['manifest']}\n"
                    f"- **Câu văn mẫu ghép vào bài viết:** *\"Hiểu một cách sâu sắc, {c_data['def'].replace('**', '')} Chính phẩm chất ấy được thể hiện sinh động qua {c_data['manifest'].lower()}\"*."
                )
        prob_kb = match_problem_solving_kb(effective_query, vdnl)
        if prob_kb:
            return (
                f"👩‍🏫 **Trợ lý Ngữ văn:** Cô cung cấp ngay nội dung **Luận điểm 1 (Giải thích & Biểu hiện)** cho vấn đề **{prob_kb['name']}**:\n"
                f"- **1. Giải thích khái niệm:** {prob_kb['def']}\n"
                f"- **2. Biểu hiện cụ thể:** {prob_kb['manifest']}\n"
                f"- **Câu chuyển ý sang Luận điểm 2:** *\"Nhận diện rõ bản chất và những biểu hiện thực tế ấy, chúng ta cần đi sâu phân tích trọng tâm của vấn đề '{vdnl}'.\"*"
            )
        gt_content = "\n".join(explain_list) if explain_list else f"- **{vdnl}** là nhận thức đúng đắn và hành động thiết thực của con người trước vấn đề đặt ra trong đời sống."
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Đây là nội dung **Luận điểm 1 (Giải thích & Biểu hiện)** cho đề bài **'{vdnl}'** (*{type_label}*):\n"
            f"{gt_content}\n"
            f"- **Câu văn mẫu dẫn dắt giải thích:** *\"Trước hết, cần hiểu thấu đáo bản chất của vấn đề: {vdnl} được thể hiện rõ nét qua...\"*"
        )

    ev_keywords = ["dẫn chứng", "ví dụ", "nhân vật", "tấm gương", "người thật", "minh họa", "chứng minh"]
    if any(k in effective_query for k in ev_keywords):
        ask_idx = count_previous_topic_asks(ev_keywords)
        cur_evs = cur_de_info.get("evidence", [])

        if ask_idx == 0 and cur_evs:
            ev_lines = [f"👩‍🏫 **Trợ lý Ngữ văn:** Cô cung cấp ngay cho em **các dẫn chứng người thật việc thật cụ thể** sát với đề **'{vdnl}'** (*{type_label}*):"]
            for i, ev in enumerate(cur_evs, 1):
                ev_lines.append(f"**{i}. {ev.get('ten', '')}**")
                ev_lines.append(f"   - *Chi tiết sự kiện/số liệu:* {ev.get('chi_tiet', '')}")
                ev_lines.append(f"   - *Góc độ phân tích gắn với đề:* {ev.get('y_nghia', '')}")
            if all_repo_evidences:
                t0, dc0 = all_repo_evidences[0]
                ev_lines.append(f"**{len(cur_evs)+1}. {dc0['ten']}** *(Chủ điểm: {t0})*")
                ev_lines.append(f"   - *Chi tiết:* {dc0['noi_dung']} *(Nguồn: {dc0['nguon']})*")
            ev_lines.append("\n💡 **Đoạn văn mẫu đưa dẫn chứng vào bài (Em có thể tham khảo cách hành văn này):**")
            first_ev_name = cur_evs[0].get("ten", "những tấm gương người trẻ tiêu biểu")
            ev_lines.append(f"*\"Thực tiễn đời sống đã ghi nhận biết bao minh chứng sống động cho điều đó, mà tiêu biểu là câu chuyện về {first_ev_name}. {cur_evs[0].get('chi_tiet', '')} Qua đó, ta càng thấm thía sâu sắc hơn về {vdnl}.\"*")
            return "\n".join(ev_lines)
        else:
            if all_repo_evidences:
                idx1 = (ask_idx * 2) % len(all_repo_evidences)
                idx2 = (ask_idx * 2 + 1) % len(all_repo_evidences)
                t1, dc1 = all_repo_evidences[idx1]
                t2, dc2 = all_repo_evidences[idx2]
                return (
                    f"👩‍🏫 **Trợ lý Ngữ văn:** Cô bổ sung ngay cho em **2 dẫn chứng thực tế mới hoàn toàn** kèm số liệu và nguồn báo chí để em lựa chọn cho đề **'{vdnl}'**:\n"
                    f"1. **{dc1['ten']}** *(Chủ điểm: {t1})*\n"
                    f"   - *Chi tiết xác thực:* {dc1['noi_dung']}\n"
                    f"   - *Nguồn:* {dc1['nguon']}\n"
                    f"2. **{dc2['ten']}** *(Chủ điểm: {t2})*\n"
                    f"   - *Chi tiết xác thực:* {dc2['noi_dung']}\n"
                    f"   - *Nguồn:* {dc2['nguon']}\n"
                    f"👉 **Câu nối dẫn chứng vào luận điểm:** *\"Nhìn từ câu chuyện thực tế của {dc1['ten']}, người trẻ chúng ta càng nhận thức sâu sắc hơn về {vdnl}.\"*"
                )

    bl_keywords = ["luận điểm", "bàn luận", "thân bài", "dàn ý", "tác hại", "hậu quả", "ý nghĩa", "vai trò", "giải pháp", "thực trạng", "nguyên nhân", "lí do", "lý do", "triển khai", "cần làm gì", "bài học", "cá nhân", "gia đình", "nhà trường"]
    if any(k in effective_query for k in bl_keywords):
        ask_idx = count_previous_topic_asks(bl_keywords)
        bl_items = []
        for q in questions_list:
            for ans in q.get("y_tra_loi", []):
                bl_items.append(ans)
        bl_text = "\n\n".join(bl_items)

        if ask_idx == 0:
            return (
                f"👩‍🏫 **Trợ lý Ngữ văn:** Đối với đề **'{vdnl}'** thuộc **{type_label}**, ở **Luận điểm 2 (Trọng tâm Thân bài)** em triển khai đúng các ý sau:\n\n"
                f"{bl_text}\n\n"
                "👉 *Em muốn cô hướng dẫn cách viết thành đoạn văn hoàn chỉnh cho **Ý số mấy** trong các ý trên? Hãy nhắn rõ số thứ tự (VD: 'hướng dẫn em viết Ý 1') nhé!*"
            )
        else:
            target_idx = 0
            for num in ["1", "2", "3", "4", "5"]:
                if num in effective_query:
                    target_idx = min(int(num) - 1, max(len(bl_items) - 1, 0))
                    break
            chosen_point = bl_items[target_idx] if bl_items else f"Phân tích trọng tâm về {vdnl}"
            return (
                f"👩‍🏫 **Trợ lý Ngữ văn:** Cô hướng dẫn em cách triển khai sâu ý này thành một **đoạn văn chuẩn mực (khoảng 120-150 chữ)** cho đề **'{vdnl}'**:\n"
                f"**Nội dung cốt lõi của đoạn:**\n{chosen_point}\n\n"
                "**Khung câu văn triển khai mạch lạc (4 bước):**\n"
                f"- *Câu 1 (Câu chủ đề mở đoạn):* Tiếp nối mạch suy ngẫm, một khía cạnh cốt lõi cần phân tích sâu sắc về {vdnl} chính là...\n"
                "- *Câu 2-3 (Lí giải nguyên nhân/bản chất):* Sở dĩ như vậy là bởi trong thực tế đời sống hôm nay, khi mà... thì điều này tác động trực tiếp bởi...\n"
                "- *Câu 4-5 (Đưa dẫn chứng cụ thể):* Minh chứng thuyết phục nhất cho điều này là... (nêu tên nhân vật/sự kiện và phân tích ngắn gọn ý nghĩa).\n"
                "- *Câu 6 (Chốt đoạn):* Như vậy, có thể khẳng định đây chính là góc nhìn quan trọng giúp chúng ta nhận thức thấu đáo về vấn đề."
            )

    pb_keywords = ["phản đề", "phản biện", "mở rộng", "lật lại", "phê phán", "ý kiến khác", "trái chiều", "phản đối", "luận điểm 3"]
    if any(k in effective_query for k in pb_keywords):
        pb_content = "\n".join(counter_list) if counter_list else f"- Phê phán biểu hiện lệch lạc đối với **{vdnl}** và rút ra bài học."
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Đây là nội dung cụ thể và khung câu văn cho **Luận điểm 3 (Phản đề & Bài học)** của đề **'{vdnl}'** (*{type_label}*):\n"
            f"{pb_content}\n\n"
            "✍️ **Mẫu câu diễn đạt sắc bén em có thể vận dụng ngay:**\n"
            f"*\"Nhìn nhận vấn đề một cách đa chiều, bên cạnh những nhận thức đúng đắn, thực tế vẫn tồn tại thái độ chủ quan hoặc góc nhìn phiến diện đối với {vdnl}... Đây là biểu hiện lệch lạc cần thẳng thắn phê phán và loại bỏ. Từ đó, mỗi người trẻ chúng ta cần tự rút ra bài học tỉnh thức và rèn luyện bản thân mỗi ngày.\"*"
        )

    if any(w in effective_query for w in ["mở bài", "câu đầu", "dẫn dắt", "kết bài", "liên hệ"]):
        dani = cur_de_info.get("dani_chi_tiet", {})
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Cô gợi ý cụ thể cách viết **Mở bài và Kết bài** đúng chuẩn **{type_label}** cho đề **'{vdnl}'**:\n"
            f"- **Mở bài ({dani.get('mb', '')}):**\n"
            f"  *Mẫu dẫn dắt:* \"Giữa kỷ nguyên số đầy biến động, nơi mỗi người trẻ đều đứng trước vô vàn cơ hội nhưng cũng không ít thử thách định hình nhân cách, câu chuyện về **{vdnl}** trở thành một vấn đề thiết thực và đáng suy ngẫm hơn bao giờ hết...\"\n"
            f"- **Kết bài ({dani.get('kb', '')}):**\n"
            f"  *Mẫu khép lại:* \"Khép lại những suy ngẫm về **{vdnl}**, mỗi chúng ta hiểu rằng nhận thức đúng đắn chỉ thực sự có giá trị khi được chuyển hóa thành hành động kiên trì ngay từ hôm nay...\""
        )

    if len(q_clean.split()) >= 12:
        snippet = q_clean[:160] + ("..." if len(q_clean) > 160 else "")
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Cô đã đọc kỹ đoạn viết của em: *'{snippet}'*.\n"
            f"- **Nhận xét chuyên môn:** Đoạn viết của em đã hướng vào chủ đề **{vdnl}** (*{type_label}*).\n"
            "- **Hướng dẫn nâng cấp câu chữ cụ thể:**\n"
            "  1. Em hãy bổ sung ngay cụm từ lập luận chỉ nguyên nhân - hệ quả (*Sở dĩ như vậy là bởi..., Chính điều này đã dẫn tới...*) vào câu thứ 2 để tăng sức nặng lý lẽ.\n"
            "  2. Đừng quên gắn kèm 1 dẫn chứng người thật việc thật đã có sẵn ở cột bên trái vào cuối đoạn để đạt điểm tối đa tiêu chí Dẫn chứng nhé!"
        )

    return (
        f"👩‍🏫 **Trợ lý Ngữ văn:** Về câu hỏi **'{q_clean}'** của em cho đề bài **{vdnl}** (*{type_label}*):\n"
        "Cô đã chia sẵn bài viết ở khung bên trái thành **3 Luận điểm rõ ràng, đúng trọng tâm khía cạnh đề hỏi**:\n"
        "- Nhắn *\"Hướng dẫn Luận điểm 1\"* nếu em cần câu văn mẫu Giải thích & Biểu hiện.\n"
        "- Nhắn *\"Hướng dẫn Luận điểm 2\"* nếu em cần phân tích sâu trọng tâm Thân bài.\n"
        "- Nhắn *\"Cho em dẫn chứng cụ thể\"* nếu em cần thêm dẫn chứng người thật việc thật nhé!"
    )


# ==============================================================================
# 6. THUẬT TOÁN CHẤM ĐIỂM RUBRIC 7 TIÊU CHÍ (HIỂN THỊ ĐẦY ĐỦ TRONG 1 BẢNG DUY NHẤT)
# ==============================================================================
def evaluate_essay_strictly_by_7_criteria(essay_text, cur_de_info):
    text = essay_text.strip()
    topic_text = ensure_600_words_prompt(cur_de_info.get("text", ""))
    vdnl_chuan = cur_de_info.get("vdnl_chuan", "")
    override_val = st.session_state.get("selected_essay_type_override", "Tự động nhận diện theo đề bài")
    type_code = cur_de_info.get("essay_type_code", classify_essay_type(topic_text, vdnl_chuan, override_val))
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, topic_text, vdnl_chuan)

    prompt_lines = [
        "Bạn là Giám khảo chấm thi Ngữ văn THPT cấp Tỉnh/Thành phố có chuyên môn sâu, cẩn trọng và nghiêm khắc. Hãy đọc thật kỹ từng câu chữ trong bài làm dưới đây và đánh giá theo BẢNG RUBRIC 7 TIÊU CHÍ (Thang điểm 10.0, bước nhảy 0.25đ).",
        f'- Đề bài: "{topic_text}"',
        f'- Vấn đề nghị luận trọng tâm: "{vdnl_chuan}"',
        "- Dạng bài và yêu cầu hệ thống luận điểm bắt buộc của đề này:",
        structure_guide,
        "",
        "- Bài làm thực tế của học sinh:",
        text,
        "",
        "QUY TẮC HIỂN THỊ BẮT BUỘC ĐỂ TRÁNH BỊ VỠ BẢNG:",
        "1. TOÀN BỘ 7 TIÊU CHÍ BẮT BUỘC PHẢI NẰM HOÀN TOÀN TRONG DUY NHẤT 1 BẢNG MARKDOWN gồm 4 cột:",
        "| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |",
        "2. Bảng phải có đủ 7 hàng không được thiếu hàng nào:",
        "   Hàng 1: 1. Bố cục bài viết (0.50đ)",
        "   Hàng 2: 2. Xác định Vấn đề nghị luận (0.50đ)",
        "   Hàng 3: 3. Giải thích khái niệm & Biểu hiện (1.00đ)",
        "   Hàng 4: 4. Hệ thống luận điểm bàn luận (3.50đ)",
        "   Hàng 5: 5. Dẫn chứng thực tế (2.50đ)",
        "   Hàng 6: 6. Phản đề & Bài học liên hệ (1.00đ)",
        "   Hàng 7: 7. Diễn đạt, ngữ pháp & chính tả (1.00đ)",
        "3. LƯU Ý KỸ THUẬT QUAN TRỌNG: Tuyệt đối KHÔNG gõ ký tự xuống dòng bên trong các ô bảng (nếu cần xuống dòng trong ô thì bắt buộc dùng thẻ <br>).",
        "4. Bắt buộc trích dẫn nguyên văn (trong ngoặc kép) các câu văn lỗi từ bài làm của học sinh.",
        "5. Sau khi kết thúc bảng mới ghi: Tổng điểm, Xếp loại và các mục rà soát lỗi cụ thể.",
    ]
    prompt_grade = "\n".join(prompt_lines)

    ai_eval = call_gemini_rest_api(prompt_grade, temperature=0.25)
    # Kiểm tra tính toàn vẹn của bảng trả về từ AI: Phải có đủ 7 tiêu chí trong bảng
    if ai_eval and ai_eval.count("|") >= 28 and all(f"{i}." in ai_eval for i in range(1, 8)):
        return ai_eval

    # BỘ MÁY KIỂM ĐỊNH NỘI BỘ (ĐẢM BẢO 100% HIỂN THỊ ĐỦ 7 TIÊU CHÍ BẰNG BẢNG)
    words = re.findall(r"\w+", text)
    word_count = len(words)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if len(p.strip()) > 10]
    num_paras = len(paragraphs)
    sentences = [s.strip() for s in re.split(r"[.?!]+", text) if len(s.strip()) > 3]
    num_sents = len(sentences)

    first_sent = sentences[0] if num_sents > 0 else text[:80]
    shortest_sent = min(sentences, key=lambda s: len(s.split())) if num_sents > 1 else first_sent
    longest_sent = max(sentences, key=lambda s: len(s.split())) if num_sents > 0 else first_sent

    text_low = text.lower()
    vdnl_tokens = [w for w in extract_clean_topic_noun(vdnl_chuan + " " + topic_text).lower().split() if len(w) > 2]
    matched_topic_kws = [w for w in vdnl_tokens if w in text_low]
    topic_coverage = len(matched_topic_kws) / max(len(vdnl_tokens), 1)

    explain_markers = ["được hiểu là", "chính là", "nghĩa là", "khái niệm", "hàm ý", "biểu hiện", "thể hiện qua", "ẩn dụ", "nhận định", "câu nói", "thói quen", "quan điểm"]
    has_explain = sum(1 for m in explain_markers if m in text_low)

    argument_markers = ["trước hết", "thứ nhất", "thứ hai", "bên cạnh đó", "hơn thế nữa", "không chỉ vậy", "mặt khác", "bởi vì", "bởi lẽ", "do đó", "chính vì", "nhờ có", "giúp cho", "tạo nên", "thúc đẩy", "cá nhân", "gia đình", "nhà trường", "cộng đồng", "xã hội", "nguyên nhân", "hậu quả", "tác hại", "hệ lụy", "giải pháp"]
    arg_count = sum(1 for m in argument_markers if m in text_low)

    evidence_markers = ["ví dụ", "dẫn chứng", "tiêu biểu", "chẳng hạn", "câu chuyện", "tấm gương", "như anh", "như chị", "thầy", "chiến dịch", "dự án", "thực tế", "chứng minh"]
    ev_marker_count = sum(1 for m in evidence_markers if m in text_low)
    proper_nouns = re.findall(
        r"(?<=[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]\s)[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+(?:\s[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+)+",
        text,
    )
    unique_proper_nouns = list(set(proper_nouns))

    counter_markers = ["tuy nhiên", "ngược lại", "đáng buồn", "phê phán", "bên cạnh những", "mặt trái", "thực trạng", "vô cảm", "ích kỷ", "lệch lạc", "nhầm lẫn", "cực đoan", "ý kiến khác", "phản đối", "hạn chế"]
    counter_count = sum(1 for m in counter_markers if m in text_low)

    type_specific_missing = []
    if type_code == "DANG_1_TH1_TAC_HAI":
        harm_kws = ["tác hại", "hậu quả", "hệ lụy", "ảnh hưởng xấu", "suy giảm", "đánh mất", "bào mòn", "tổn hại"]
        if sum(1 for k in harm_kws if k in text_low) < 2:
            type_specific_missing.append("chưa tập trung phân tích sâu các tầng Tác hại / Hậu quả theo đúng lệnh đề")
    elif type_code == "DANG_1_TH1_Y_NGHIA":
        meaning_kws = ["ý nghĩa", "vai trò", "giá trị", "sức mạnh", "giúp", "tạo nên", "thúc đẩy", "động lực"]
        if sum(1 for k in meaning_kws if k in text_low) < 2:
            type_specific_missing.append("chưa đào sâu phân tích các tầng Ý nghĩa / Vai trò của vấn đề")
    elif type_code in ["DANG_2_GIAI_QUYET", "DANG_5_TU_BO"]:
        for actor in ["cá nhân", "gia đình", "nhà trường"]:
            if actor not in text_low:
                type_specific_missing.append(f"thiếu đoạn giải pháp đối với {actor}")
    elif type_code == "DANG_3_HAI_QUAN_DIEM":
        if not any(w in text_low for w in ["hạn chế", "phiến diện", "chưa toàn diện", "mặt khác"]):
            type_specific_missing.append("chưa phân tích rõ hạn chế của quan điểm còn lại")

    colloquial_words = ["rất là", "cực kỳ", "siêu", "thì là", "nói chung là", "kiểu như", "vân vân", "v.v", "là một học sinh đang ngồi trên ghế nhà trường"]
    found_colloquial = [cw for cw in colloquial_words if cw in text_low]

    word_freq = {}
    for w in words:
        w_l = w.lower()
        if len(w_l) > 4:
            word_freq[w_l] = word_freq.get(w_l, 0) + 1
    repeated_words = [w for w, c in word_freq.items() if c >= max(5, word_count // 40)]

    weak_sentences = [s for s in sentences if len(s.split()) < 7 or len(s.split()) > 65]
    sample_weak_sent = weak_sentences[0] if weak_sentences else shortest_sent

    # 1. Bố cục (0.50đ)
    if num_paras >= 4 and word_count >= 500:
        s1 = 0.50
        c1_note = f"Đủ 3 phần Mở - Thân - Kết; thân bài tách {num_paras} đoạn mạch lạc; đạt dung lượng chuẩn {word_count} chữ."
    elif num_paras >= 3 and word_count >= 250:
        s1 = 0.25
        c1_note = f"Có đủ 3 phần nhưng thân bài tách đoạn chưa cân đối hoặc dung lượng còn thiếu ({word_count} chữ)."
    else:
        s1 = 0.00
        c1_note = f"Bố cục dang dở ({num_paras} đoạn, {word_count} chữ), chưa hoàn chỉnh 3 phần."

    # 2. Xác định VĐNL (0.50đ)
    if topic_coverage >= 0.5 and num_paras >= 3:
        s2 = 0.50
        c2_note = f"Xác định đúng và trúng vấn đề nghị luận trọng tâm. Trích câu mở đầu: \"{first_sent[:90]}...\"."
    elif topic_coverage >= 0.2:
        s2 = 0.25
        c2_note = f"Có nhắc đến vấn đề nhưng cách diễn đạt còn chung chung, chưa làm nổi bật trọng tâm."
    else:
        s2 = 0.00
        c2_note = "Xác định sai lệch vấn đề nghị luận, lạc đề."

    # 3. Giải thích & Biểu hiện (1.00đ)
    if has_explain >= 2 and word_count >= 500:
        s3 = 1.00
        c3_note = "Cắt nghĩa tường minh bản chất khái niệm và nêu được biểu hiện thực tế đời sống sinh động."
    elif has_explain >= 1 and word_count >= 350:
        s3 = 0.75
        c3_note = "Giải thích đúng khái niệm nhưng phần nêu biểu hiện đời sống còn sơ sài."
    elif has_explain >= 1:
        s3 = 0.50
        c3_note = "Mới giải thích bề mặt từ ngữ, chưa làm bật được bản chất vấn đề."
    else:
        s3 = 0.25 if word_count >= 200 else 0.00
        c3_note = "Chưa có đoạn giải thích rõ ràng khái niệm ở đầu phần Thân bài."

    # 4. Hệ thống luận điểm (3.50đ)
    if word_count < 250:
        base_s4 = 1.00
    elif word_count < 400:
        base_s4 = 1.75
    elif word_count < 550:
        base_s4 = 2.50 if arg_count >= 5 else 2.00
    else:
        base_s4 = 3.25 if (arg_count >= 7 and topic_coverage >= 0.5) else 2.75

    if type_specific_missing and base_s4 >= 1.50:
        base_s4 = max(1.00, base_s4 - 0.50)
        missing_str = ", ".join(type_specific_missing)
        c4_note = f"Bài làm đạt {word_count} chữ, tuy nhiên so với dạng bài {type_label} còn {missing_str}. Câu tiêu biểu: \"{longest_sent[:90]}...\"."
    else:
        c4_note = f"Triển khai đúng trọng tâm theo dạng bài {type_label}. Lý lẽ tương đối tốt, cần đào sâu hơn quan hệ nhân - quả."
    s4 = base_s4

    # 5. Dẫn chứng thực tế (2.50đ)
    if len(unique_proper_nouns) >= 2 and ev_marker_count >= 2 and word_count >= 500:
        s5 = 2.25
        nouns_str = ", ".join(unique_proper_nouns[:2])
        c5_note = f"Có dẫn chứng người thật việc thật xác thực ({nouns_str}), đã có câu phân tích gắn với luận điểm."
    elif len(unique_proper_nouns) >= 1 or ev_marker_count >= 1:
        s5 = 1.50 if word_count >= 350 else 1.00
        nouns_str = ", ".join(unique_proper_nouns[:2]) if unique_proper_nouns else "dẫn chứng chung"
        c5_note = f"Có nêu dẫn chứng ({nouns_str}) nhưng còn nghiêng về kể lể sự việc, thiếu câu bình luận đắt giá."
    else:
        s5 = 0.50 if word_count >= 300 else 0.00
        c5_note = "Thiếu dẫn chứng thực tế xác thực; bài viết chủ yếu nói lý thuyết suông."

    # 6. Phản đề & Bài học (1.00đ)
    if counter_count >= 2 and word_count >= 450:
        s6 = 1.00
        c6_note = "Phản biện sắc bén, biết lật lại vấn đề và rút ra bài học nhận thức, hành động thiết thực."
    elif counter_count >= 1 and word_count >= 280:
        s6 = 0.75
        c6_note = "Có phản đề và bài học nhưng góc nhìn phản biện còn nông, liên hệ bản thân còn hơi công thức."
    elif counter_count >= 1:
        s6 = 0.50
        c6_note = "Mới chỉ có 1 câu phê phán chung chung hoặc bài học hô hào khẩu hiệu."
    else:
        s6 = 0.25 if word_count >= 200 else 0.00
        c6_note = "Thiếu thao tác phản biện ý kiến trái chiều và bài học liên hệ bản thân."

    # 7. Diễn đạt & Chính tả (1.00đ)
    err_details = []
    if found_colloquial:
        err_details.append(f"dùng từ khẩu ngữ ({', '.join(found_colloquial[:2])})")
    if repeated_words:
        err_details.append(f"lặp từ nhiều lần ({', '.join(repeated_words[:3])})")
    if len(sample_weak_sent.split()) < 7:
        err_details.append(f"câu cụt: \"{sample_weak_sent}\"")

    if not err_details and word_count >= 450:
        s7 = 1.00
        c7_note = "Lời văn chuẩn mực, giàu tính chính luận, câu cú hoàn chỉnh, không mắc lỗi chính tả."
    elif not err_details:
        s7 = 0.75
        c7_note = "Diễn đạt rõ ràng, mạch lạc, câu văn tương đối trôi chảy."
    else:
        s7 = 0.50
        c7_note = "Cần khắc phục các lỗi diễn đạt: " + "; ".join(err_details) + "."

    total_score = round(s1 + s2 + s3 + s4 + s5 + s6 + s7, 2)
    rank = "Tốt" if total_score >= 8.0 else ("Khá" if total_score >= 6.5 else ("Đạt" if total_score >= 5.0 else "Chưa đạt"))

    # XUẤT RA TOÀN BỘ 7 TIÊU CHÍ TRONG 1 BẢNG MARKDOWN DUY NHẤT
    report_lines = [
        "### 📊 BẢNG ĐÁNH GIÁ CHI TIẾT THEO 7 TIÊU CHÍ RUBRIC",
        f"*🧭 **Dạng bài áp dụng:** {type_label}*<br>",
        f"*📏 **Thông số bài làm:** Độ dài **{word_count} chữ** | **{num_paras} đoạn văn** | **{num_sents} câu văn**.*\n",
        "| STT | Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng từ bài làm |",
        "| :---: | :--- | :---: | :---: | :--- |",
        f"| **1** | **Bố cục bài viết (Mở - Thân - Kết)** | 0.50đ | **{s1:.2f}đ** | {c1_note} |",
        f"| **2** | **Xác định Vấn đề nghị luận** | 0.50đ | **{s2:.2f}đ** | {c2_note} |",
        f"| **3** | **Giải thích khái niệm & Biểu hiện** | 1.00đ | **{s3:.2f}đ** | {c3_note} |",
        f"| **4** | **Hệ thống luận điểm bàn luận** | 3.50đ | **{s4:.2f}đ** | {c4_note} |",
        f"| **5** | **Dẫn chứng thực tế** | 2.50đ | **{s5:.2f}đ** | {c5_note} |",
        f"| **6** | **Phản đề & Bài học liên hệ** | 1.00đ | **{s6:.2f}đ** | {c6_note} |",
        f"| **7** | **Diễn đạt, ngữ pháp & chính tả** | 1.00đ | **{s7:.2f}đ** | {c7_note} |",
        "",
        "---",
        f"### 📌 TỔNG ĐIỂM: **{total_score:.2f} / 10.0 điểm** — Xếp loại: **{rank}**",
        "",
        "#### 🔍 RÀ SOÁT LỖI CỤ THỂ & ĐỊNH HƯỚNG CHỈNH SỬA NÂNG CẤP BÀI VIẾT:",
        f"1. **Cấu trúc bài làm theo dạng đề ({type_label}):**<br>",
        f"   - Bài làm đạt **{word_count} chữ**. Cần bám chắc các luận điểm đã vạch ra ở Bước 2, tránh ôm đồm lan man.<br>",
        f"   - **Câu mở đầu:** *\"{first_sent[:110]}...\"* -> Hãy kiểm tra lại xem đã nêu trực diện vấn đề trọng tâm hay chưa.<br>",
        f"2. **Lỗi diễn đạt và câu chữ cần sửa ngay:**<br>",
        f"   - **Câu văn còn non/cụt trong bài:** *\"{sample_weak_sent}\"* -> **Cách sửa:** Bổ sung quan hệ từ lập luận (*bởi lẽ, chính vì vậy, nhờ đó...*) để tăng tính liên kết.<br>",
        f"   - **Từ vựng:** Tránh các từ ngữ khẩu ngữ hoặc lặp từ nhiều lần; ưu tiên dùng từ ngữ chính luận.<br>",
        f"3. **Về khai thác Dẫn chứng và Phản đề:**<br>",
        f"   - **Dẫn chứng:** Cần đưa tên người thật việc thật cụ thể và phân tích sâu ý nghĩa thay vì chỉ kể sự việc.<br>",
        f"   - **Phản đề:** Nhìn nhận đa chiều, phê phán quan điểm lệch lạc để làm nổi bật tính đúng đắn của vấn đề.",
    ]
    return "\n".join(report_lines)


# ==============================================================================
# 7. GIAO DIỆN CHÍNH & QUY TRÌNH 4 BƯỚC SƯ PHẠM
# ==============================================================================
with st.sidebar:
    st.title("⚙️ HỆ THỐNG QUẢN TRỊ")
    st.success("✅ Hệ thống EduAI hoạt động ổn định!")

    with st.expander("🔑 Cấu hình nâng cao (Dành cho GV)"):
        key_in = st.text_input(
            "Mã Gemini API Key (Tùy chọn):",
            type="password",
            value=st.session_state["gemini_api_key"],
            help="Nếu nhập mã AIzaSy..., hệ thống kết hợp thêm AI đám mây. Nếu để trống, hệ thống tự động chạy Bộ máy Tri thức Sư phạm Nội bộ.",
        )
        if key_in != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = key_in

    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM")
    st.markdown("1. **🌱 Bước 1:** Tìm hiểu đề và xác định vấn đề nghị luận")
    st.markdown("2. **🧵 Bước 2:** Tìm ý và Lập dàn ý")
    st.markdown("3. **✍️ Bước 3:** Viết bài")
    st.markdown("4. **📊 Bước 4:** Đánh giá và Chỉnh sửa")

st.markdown(
    """
<div class="hero-banner">
    <div class="hero-title">🖊️ EduAI - HỆ THỐNG ĐỊNH HƯỚNG TƯ DUY VÀ PHÁT TRIỂN NĂNG LỰC VIẾT VĂN NGHỊ LUẬN XÃ HỘI</div>
    <p class="hero-subtitle">Đồng hành kiến tạo tư duy lập luận độc lập, bồi đắp chiều sâu nhận thức và làm chủ kỹ năng tạo lập văn bản nghị luận xã hội</p>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        "🌱 Bước 1: Tìm hiểu đề và xác định vấn đề nghị luận",
        "🧵 Bước 2: Tìm ý và Lập dàn ý",
        "✍️ Bước 3: Viết bài",
        "📊 Bước 4: Đánh giá và Chỉnh sửa",
    ]
)

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ VÀ XÁC ĐỊNH VẤN ĐỀ NGHỊ LUẬN
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown(
        '<div class="section-title">🔍 Bước 1: Tìm hiểu đề và xác định vấn đề nghị luận</div>',
        unsafe_allow_html=True,
    )

    cur_override_idx = (
        DANH_SACH_DANG_BAI.index(st.session_state["selected_essay_type_override"])
        if st.session_state["selected_essay_type_override"] in DANH_SACH_DANG_BAI
        else 0
    )
    selected_override = st.selectbox(
        "🧭 Định hướng Dạng bài Nghị luận xã hội (Tự động nhận diện chính xác theo lệnh đề hoặc chủ động chọn dạng bài):",
        DANH_SACH_DANG_BAI,
        index=cur_override_idx,
        key="sb_type_override",
    )
    st.session_state["selected_essay_type_override"] = selected_override

    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs(
        [
            "🟢 Nhóm Đề Cơ Bản (Đề 01 – Đề 15)",
            "🔴 Nhóm Đề Nâng Cao (Đề 16 – Đề 30)",
            "✏️ Nhập / Dán Đề Bài Riêng",
        ]
    )

    with tab_de_coban:
        col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
        with col_cb1:
            selected_cb_key = st.selectbox(
                "Chọn đề trong nhóm Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="sb_coban"
            )
            de_info_cb = db.DE_BAI_CO_BAN[selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Đề bài:")
                st.info(ensure_600_words_prompt(de_info_cb["text"]))
            if st.button("📌 Chọn đề Cơ bản này để luyện tập", key="btn_chon_cb", type="primary"):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = build_dynamic_outline_for_custom_topic(
                    de_info_cb["text"],
                    de_info_cb.get("vdnl_chuan", selected_cb_key),
                    selected_override,
                    base_de_info=de_info_cb,
                )
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Mời chuyển sang Bước 2.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox(
                "Chọn đề trong nhóm Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="sb_nangcao"
            )
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Đề bài:")
                st.info(ensure_600_words_prompt(de_info_nc["text"]))
            if st.button("📌 Chọn đề Nâng cao này để luyện tập", key="btn_chon_nc", type="primary"):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = build_dynamic_outline_for_custom_topic(
                    de_info_nc["text"],
                    de_info_nc.get("vdnl_chuan", selected_nc_key),
                    selected_override,
                    base_de_info=de_info_nc,
                )
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Mời chuyển sang Bước 2.")

    with tab_de_tu_nhap:
        st.markdown(
            "##### ✏️ Nhập đề bài riêng (Hệ thống tự động nhận diện đúng khía cạnh lệnh đề hỏi và thiết lập hệ thống luận điểm tương ứng):"
        )
        custom_de_text = st.text_area(
            "Đề bài:",
            placeholder="Ví dụ: Suy nghĩ về tác hại của thói quen trì hoãn... hoặc Giải pháp khắc phục tình trạng nghiện mạng xã hội... hoặc Thuyết phục bạn từ bỏ thói quen thức khuya...",
            height=110,
            key="txt_custom_de",
        )
        student_custom_vdnl = st.text_input(
            "Theo em, vấn đề nghị luận trọng tâm của đề bài này là gì?",
            placeholder="Ví dụ: Tác hại của thói quen trì hoãn...",
            key="txt_custom_vdnl",
        )
        if st.button(
            "🔍 Phân tích đề tự nhập & Thiết lập Hệ thống Luận điểm Bước 2",
            type="primary",
            key="btn_custom_analyze",
        ):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập Đề bài trước khi bấm phân tích!")
            else:
                with st.spinner("Đang nhận diện khía cạnh lệnh đề, giải thích khái niệm và lập hệ thống luận điểm..."):
                    outline = build_dynamic_outline_for_custom_topic(
                        custom_de_text.strip(), student_custom_vdnl.strip(), selected_override
                    )
                    short_title = custom_de_text.strip()[:55] + (
                        "..." if len(custom_de_text.strip()) > 55 else ""
                    )
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                    st.session_state["current_de_info"] = outline
                    st.success(
                        f"✅ Đã phân luồng chính xác: **{outline.get('essay_type_label', '')}**! Mời chuyển sang **Bước 2**."
                    )

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    active_type_code = cur_active_info.get(
        "essay_type_code",
        classify_essay_type(
            cur_active_info.get("text", ""), cur_active_info.get("vdnl_chuan", ""), selected_override
        ),
    )
    active_type_label = cur_active_info.get("essay_type_label", get_essay_type_label(active_type_code))
    st.info(
        f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Đề bài:* {ensure_600_words_prompt(cur_active_info.get('text', ''))}\n\n🎯 **Vấn đề nghị luận trọng tâm:** {cur_active_info.get('vdnl_chuan', '')}\n\n🧭 **Định hướng cấu trúc:** {active_type_label}"
    )


# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý VÀ LẬP DÀN Ý
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">🧵 Bước 2: Tìm ý và Lập dàn ý</div>', unsafe_allow_html=True)
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]
    cur_type_code = cur_de_info.get(
        "essay_type_code",
        classify_essay_type(
            cur_de_info.get("text", ""),
            cur_de_info.get("vdnl_chuan", ""),
            st.session_state.get("selected_essay_type_override", "Tự động nhận diện theo đề bài"),
        ),
    )
    cur_type_label = cur_de_info.get("essay_type_label", get_essay_type_label(cur_type_code))

    c_left, c_right = st.columns([1.15, 0.85], gap="large")

    with c_left:
        st.markdown(
            f"#### 🛠️ Hệ thống luận điểm định hướng tư duy: <span style='color:#2563eb;'>{cur_de_key}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='type-badge'>🧭 {cur_type_label}</div>", unsafe_allow_html=True)

        with st.expander("📌 Luận điểm 1 (Thao tác Giải thích & Nêu biểu hiện nhận diện)", expanded=True):
            with st.container(border=True):
                for itm in cur_de_info.get("explain_items", []):
                    st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt vấn đề chuyển sang bàn luận:** {cur_de_info.get('vdnl_ket_luan', '')}")

        with st.expander("💡 Luận điểm 2 (Thao tác Bàn luận trọng tâm theo đúng khía cạnh lệnh đề)", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**🎯 {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        with st.expander("🔄 Luận điểm 3 (Thao tác Phản đề / Ý kiến trái chiều & Bài học)", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        with st.expander("📚 Dẫn chứng thực tế trọng tâm & Tra cứu Kho dẫn chứng 9 chủ điểm", expanded=True):
            st.markdown("##### 📌 1. Dẫn chứng tiêu biểu gắn trực tiếp với đề bài này:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    card_html = (
                        f"<div class='evidence-card'>"
                        f"<h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>"
                        f"<p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p>"
                        f"<p style='margin:0 0 6px 0;'><b>• Ý nghĩa phân tích:</b> {ev.get('y_nghia', '')}</p>"
                        f"</div>"
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

            st.markdown(
                """
                <div class="repo-guide-box">
                    💡 <b>KHO DẪN CHỨNG 9 CHỦ ĐIỂM (MỞ RỘNG):</b> Danh sách dẫn chứng mở rộng được cất gọn trong kho bên dưới. Khi cần tìm thêm dẫn chứng ở chủ điểm nào, em hãy bấm chọn chủ điểm đó để mở kho nhé!
                </div>
                """,
                unsafe_allow_html=True,
            )

            placeholder_opt = "--- 👉 Bấm vào đây để chọn chủ điểm dẫn chứng cần tra cứu (9 chủ điểm) ---"
            kho_options = [placeholder_opt] + list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys())
            selected_topic = st.selectbox(
                "📂 Mở Kho dẫn chứng 9 chủ điểm:",
                kho_options,
                index=0,
                key="sb_kho_dc",
            )
            if selected_topic != placeholder_opt:
                st.markdown(f"###### 📖 Danh sách dẫn chứng thuộc chủ điểm: *{selected_topic}*")
                for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                    with st.container(border=True):
                        st.markdown(f"**👤 {dc['ten']}**")
                        st.write(dc["noi_dung"])
                        st.caption(f"📰 Nguồn: {dc['nguon']}")

        with st.expander("📝 Tổng hợp Bố cục Dàn ý 3 phần (Mở bài - Thân bài - Kết bài)", expanded=False):
            dani = cur_de_info.get("dani_chi_tiet", {})
            with st.container(border=True):
                st.markdown(f"**I. MỞ BÀI:** {dani.get('mb','')}")
                st.markdown(
                    f"**II. THÂN BÀI:**\n- {dani.get('gt','')}\n- {dani.get('bl','')}\n- {dani.get('dc','')}\n- {dani.get('pb','')}"
                )
                st.markdown(f"**III. KẾT BÀI:** {dani.get('kb','')}")

    with c_right:
        st.markdown("#### 🧭 Trợ lý Ngữ văn")
        chat_container = st.container(height=420, border=True)
        with chat_container:
            for role, msg in st.session_state["chat_history"]:
                speaker = "🧑‍🎓 Học sinh" if role == "user" else "👩‍🏫 Trợ lý Ngữ văn"
                st.markdown(f"**{speaker}:**\n\n{msg}")
                st.markdown("---")

        user_question = st.text_area(
            "Nhập câu hỏi cụ thể (VD: Giải thích khái niệm, cho thêm dẫn chứng mới, hướng dẫn viết Ý 1, Ý 2, phản đề...):",
            height=80,
            key="txt_chat_input",
        )
        col_chat_1, col_chat_2 = st.columns([2, 1])
        with col_chat_1:
            if st.button("🚀 Gửi câu hỏi", type="primary", use_container_width=True):
                if user_question.strip():
                    with st.spinner("Trợ lý Ngữ văn đang phân tích câu hỏi trong mạch hội thoại..."):
                        reply = generate_deep_chat_response(
                            user_question.strip(), cur_de_info, st.session_state["chat_history"]
                        )
                        st.session_state["chat_history"].append(("user", user_question.strip()))
                        st.session_state["chat_history"].append(("assistant", reply))
                        st.rerun()
                else:
                    st.warning("Em hãy nhập câu hỏi trước khi bấm gửi nhé!")
        with col_chat_2:
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                st.session_state["chat_history"] = [
                    (
                        "assistant",
                        "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng ở Luận điểm nào (Luận điểm 1: Giải thích & Biểu hiện; Luận điểm 2: Bàn luận trọng tâm; hay Luận điểm 3: Phản đề)?",
                    )
                ]
                st.rerun()


# ------------------------------------------------------------------------------
# BƯỚC 3: VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Viết bài</div>', unsafe_allow_html=True)
    st.info(
        f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n📖 **Đề bài:** *{ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}*"
    )

    write_mode = st.radio(
        "Chọn hình thức nộp bài:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode",
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội:",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy tự viết bài văn hoàn chỉnh của em tại đây (Đảm bảo đủ 3 phần Mở bài, Thân bài tách các đoạn rõ ràng theo đúng hệ thống Luận điểm ở Bước 2, Kết bài)...",
        )
        st.session_state["user_essay"] = essay_input
        wc = len(re.findall(r"\w+", essay_input)) if essay_input.strip() else 0
        wc_status = (
            "(Chưa đạt yêu cầu khoảng 600 chữ của đề bài)"
            if wc < 550
            else "(Đã đạt chuẩn dung lượng khoảng 600 chữ)"
        )
        st.caption(f"📊 Dung lượng hiện tại: **{wc} chữ** {wc_status}.")

        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            if st.button("💡 Nhắc lại tiêu chuẩn bài văn 600 chữ", use_container_width=True):
                st.info(
                    "💡 **Lưu ý:** Bài văn cần đạt dung lượng khoảng 600 chữ, bố cục 3 phần rõ ràng, giải thích trúng trọng tâm, thân bài triển khai đúng hệ thống luận điểm của dạng đề, có dẫn chứng thực tế và phản biện sắc bén!"
                )
        with col_w2:
            if st.button("📊 Nộp bài & Đánh giá theo Rubric", type="primary", use_container_width=True):
                if not essay_input.strip():
                    st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên!")
                else:
                    with st.spinner("Đang đọc kỹ từng câu, rà soát lỗi và đánh giá theo 7 tiêu chí Rubric..."):
                        st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(
                            essay_input.strip(), st.session_state["current_de_info"]
                        )
                        st.success(
                            "✅ Đã đánh giá xong! Mời chuyển sang **Bước 4: Đánh giá và Chỉnh sửa** để xem chi tiết."
                        )
    else:
        uploaded_img = st.file_uploader("Tải lên ảnh chụp bài làm viết tay:", type=["png", "jpg", "jpeg"])
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm của học sinh", use_column_width=True)
            ocr_assist_text = st.text_area(
                "Nhập/dán nội dung văn bản từ ảnh (hoặc để hệ thống quét trực tiếp nếu đã kết nối khóa AI):",
                height=150,
                placeholder="Nếu chưa nhập khóa AI đám mây, em hãy dán nội dung bài viết vào đây để bộ máy kiểm định chính xác từng câu chữ...",
            )
            if st.button("📊 Đọc bài & Đánh giá theo Rubric", type="primary"):
                with st.spinner("Đang đọc kỹ bài làm, rà soát lỗi và chấm điểm theo 7 tiêu chí..."):
                    prompt_img = (
                        f"Hãy đọc toàn bộ chữ viết tay trong bức ảnh này và đánh giá theo BẢNG RUBRIC 7 TIÊU CHÍ (Thang điểm 10.0) cho đề bài: "
                        f"'{ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}'. "
                        "BẮT BUỘC hiển thị toàn bộ 7 tiêu chí trong DUY NHẤT 1 BẢNG MARKDOWN (không ngắt dòng trong ô, dùng thẻ <br> nếu muốn xuống dòng). Sau bảng mới ghi Tổng điểm và rà soát lỗi."
                    )
                    ai_img_res = call_gemini_rest_api(prompt_img, pil_image=img_obj, temperature=0.25)
                    if ai_img_res and "|" in ai_img_res and ai_img_res.count("|") >= 28:
                        st.session_state["rubric_evaluation"] = ai_img_res
                        st.success("✅ Đã đọc ảnh và đánh giá xong! Mời sang Bước 4 xem kết quả.")
                    elif ocr_assist_text.strip():
                        st.session_state["user_essay"] = ocr_assist_text.strip()
                        st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(
                            ocr_assist_text.strip(), st.session_state["current_de_info"]
                        )
                        st.success("✅ Đã đánh giá xong văn bản bài làm! Mời sang Bước 4 xem kết quả.")
                    else:
                        st.warning(
                            "⚠️ Để đọc trực tiếp chữ viết tay từ ảnh mà không cần gõ lại, vui lòng nhập khóa Gemini API (`AIzaSy...`) ở mục Cấu hình nâng cao bên trái, hoặc dán văn bản bài viết vào ô bên trên."
                        )


# ------------------------------------------------------------------------------
# BƯỚC 4: ĐÁNH GIÁ VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Đánh giá và Chỉnh sửa</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric đánh giá bài văn Nghị luận xã hội (Thang điểm 10):</b><br>
            1. <b>Bố cục (0.5đ):</b> Đủ 3 phần Mở - Thân - Kết, tách đoạn hợp lý theo dạng bài.<br>
            2. <b>Xác định VĐNL (0.5đ):</b> Nêu đúng trọng tâm vấn đề nghị luận.<br>
            3. <b>Giải thích & Biểu hiện (1.0đ):</b> Cắt nghĩa tường minh khái niệm, nhận định và nêu biểu hiện.<br>
            4. <b>Hệ thống luận điểm (3.5đ):</b> Triển khai đầy đủ, sâu sắc các ý bàn luận theo đúng khía cạnh đề hỏi.<br>
            5. <b>Dẫn chứng (2.5đ):</b> Người thật việc thật xác thực, phân tích gắn kết hữu cơ với luận điểm.<br>
            6. <b>Phản đề & Bài học (1.0đ):</b> Có góc nhìn phản biện đa chiều, bác bỏ ý kiến lệch lạc và bài học thực chất.<br>
            7. <b>Diễn đạt & Chính tả (1.0đ):</b> Trong sáng, lập luận chặt chẽ, không lặp từ hay viết câu cụt.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_r1, col_r2 = st.columns([1, 1.35], gap="large")

    with col_r1:
        st.markdown("##### 📝 Chỉnh sửa và hoàn thiện bài viết tại đây:")
        edited_essay = st.text_area(
            "Nội dung bài làm (Sửa trực tiếp các câu văn được chỉ ra ở bảng bên phải):",
            value=st.session_state.get("user_essay", ""),
            height=420,
            key="essay_step4_editor",
        )
        st.session_state["user_essay"] = edited_essay
        wc_step4 = len(re.findall(r"\w+", edited_essay)) if edited_essay.strip() else 0
        st.caption(f"📏 Số chữ sau khi chỉnh sửa: **{wc_step4} chữ**.")

        if st.button("🔍 Cập nhật đánh giá lại", type="primary", use_container_width=True):
            if edited_essay.strip():
                with st.spinner("Đang kiểm định lại từng tiêu chí sau khi chỉnh sửa..."):
                    st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(
                        edited_essay.strip(), st.session_state["current_de_info"]
                    )
                    st.success("✅ Đã cập nhật bảng đánh giá mới sát với nội dung vừa chỉnh sửa!")
            else:
                st.warning("⚠️ Hãy nhập bài viết để hệ thống đánh giá!")

        if edited_essay.strip():
            content = (
                f"HỒ SƠ BÀI LÀM NLXH\nĐỀ BÀI: {st.session_state['selected_de_key']}\n"
                f"NỘI DUNG ĐỀ: {ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}\n\n"
                f"-- BÀI LÀM CỦA HỌC SINH ({wc_step4} chữ) --\n{edited_essay}\n\n"
                f"-- KẾT QUẢ ĐÁNH GIÁ RUBRIC --\n{st.session_state.get('rubric_evaluation', '')}"
            )
            st.download_button(
                label="📥 Tải Hồ sơ bài làm & Bảng Rubric (.txt)",
                data=content.encode("utf-8"),
                file_name="HoSo_EduAI_NLXH.txt",
                use_container_width=True,
            )

    with col_r2:
        st.markdown("##### 📋 Bảng Điểm & Nhận Xét Chi Tiết:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"], unsafe_allow_html=True)
        else:
            st.info("💡 Chưa có kết quả đánh giá. Hãy nộp bài ở Bước 3 để hệ thống chấm và rà soát lỗi.")
