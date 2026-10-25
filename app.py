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
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 22px;
    }
    
    .hero-title {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px !important;
        color: #ffffff !important;
    }

    .hero-subtitle {
        font-size: 0.92rem;
        color: #dbeafe;
        margin: 0;
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
        return re.sub(r'(?i)(bài văn nghị luận)', r'\1 (khoảng 600 chữ)', text, count=1)
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
            "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em giải thích khái niệm khó, gợi mở luận điểm sâu sắc theo đúng dạng đề, cung cấp dẫn chứng người thật việc thật và sửa từng câu văn cho em. Em đang cần cô hỗ trợ khâu nào?",
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
# 5. KHO TRI THỨC BÁCH KHOA NLXH CHUYÊN SÂU (KHÁI NIỆM, LÝ LẼ, GIẢI PHÁP 3 CẤP ĐỘ & DẪN CHỨNG CỤ THỂ)
# Đảm bảo học sinh có ngay khái niệm chuẩn và dẫn chứng cụ thể mà không cần tra Google/ChatGPT
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

# KHO TRI THỨC CHUYÊN BIỆT CHO DẠNG 2 (VẤN ĐỀ CẦN GIẢI QUYẾT) VÀ DẠNG 5 (THUYẾT PHỤC TỪ BỎ THÓI QUEN/QUAN NIỆM)
PROBLEM_SOLVING_KB = {
    "mạng xã hội": {
        "name": "Tình trạng nghiện mạng xã hội và phụ thuộc vào thế giới ảo của giới trẻ",
        "is_positive_declining": False,
        "def": "**Nghiện mạng xã hội / Sống ảo** là trạng thái con người bị lệ thuộc quá mức về mặt thời gian và cảm xúc vào các nền tảng kỹ thuật số (TikTok, Facebook, Instagram...), lấy lượt tương tác ảo làm thước đo giá trị bản thân mà sao nhãng đời sống thực.",
        "manifest": "Dành hàng chục giờ mỗi ngày lướt video ngắn vô thức; bất an khi không có điện thoại; chăm chút hình ảnh hào nhoáng trên mạng nhưng thờ ơ, lạnh nhạt với người thân ngay bên cạnh.",
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
        "name": "Thói quen trì hoãn ('Nước đến chân mới nhảy') trong học tập và cuộc sống",
        "is_positive_declining": False,
        "def": "**Thói quen trì hoãn** là hành vi cố tình chần chừ, dây dưa, đẩy những công việc cần làm ngay sang 'ngày mai' hoặc 'lúc khác' dù biết rõ việc chậm trễ đó sẽ dẫn đến áp lực và kết quả kém.",
        "manifest": "Đợi sát ngày thi mới bắt đầu học bài; lập thời gian biểu chi tiết nhưng luôn tự thưởng cho mình lướt mạng 'thêm 5 phút nữa'; viện cớ 'chưa có cảm hứng' để trốn tránh nhiệm vụ khó.",
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
        "name": "Vấn nạn bạo lực học đường và bạo lực ngôn từ trên không gian mạng",
        "is_positive_declining": False,
        "def": "**Bạo lực học đường và bạo lực mạng** là những hành vi cố ý sử dụng vũ lực thể chất hoặc lời nói lăng mạ, cô lập, vu khống, công kích tinh thần người khác trong môi trường trường học và trên các nền tảng trực tuyến.",
        "manifest": "Đánh hội đồng, quay clip tung lên mạng; lập các hội nhóm nói xấu, tẩy chay bạn bè; buông những bình luận miệt thị ngoại hình, hoàn cảnh của người khác sau bàn phím.",
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
        "name": "Vấn đề ô nhiễm môi trường và thói quen xả rác, lạm dụng đồ nhựa dùng một lần",
        "is_positive_declining": False,
        "def": "**Ô nhiễm môi trường / Lạm dụng rác thải nhựa** là tình trạng môi trường tự nhiên (đất, nước, không khí) bị suy thoái nghiêm trọng do các chất thải độc hại và thói quen tiêu dùng thiếu bền vững của con người.",
        "manifest": "Xả rác bừa bãi nơi công cộng; sử dụng tràn lan túi nilon, cốc nhựa dùng một lần; chặt phá cây xanh và xả nước thải chưa qua xử lý ra sông hồ.",
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
        "name": "Rèn luyện tính tự lập, tự chủ và tinh thần tự giác của người trẻ",
        "is_positive_declining": True,
        "def": "**Tính tự lập / Tự giác** là khả năng tự mình suy nghĩ, đưa ra quyết định, tự lo liệu công việc học tập và cuộc sống bằng năng lực của bản thân mà không ỷ lại, dựa dẫm vào cha mẹ hay người khác.",
        "manifest": "Tự giác lập kế hoạch học tập mà không cần ai nhắc nhở; chủ động trang bị kỹ năng sống, tự giải quyết các vấn đề cá nhân và chịu trách nhiệm về lựa chọn của mình.",
        "meaning_when_positive": "**Ý nghĩa cốt lõi của tính tự lập:** Tự lập chính là bước ngoặt đánh dấu sự trưởng thành thực sự của một con người; nó giúp người trẻ rèn luyện bản lĩnh thích ứng trước mọi biến động, làm chủ cuộc đời mình và giảm bớt gánh nặng cho gia đình.",
        "status_cause_harm": (
            "- **Thực trạng cần giải quyết:** Hiện nay, không ít học sinh, thanh niên dù đã lớn nhưng vẫn mang tâm lý 'cây tầm gửi', thiếu kỹ năng tự chăm sóc bản thân, học tập đối phó khi không có người giám sát và dễ hoảng loạn khi bước vào môi trường mới.\n"
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
    "Dạng 1 - TH1: Tư tưởng, đạo lí (Bàn sâu về Ý nghĩa / Giá trị / Vai trò / Sức mạnh)",
    "Dạng 1 - TH2: Tư tưởng, đạo lí (Bàn về Bài học giải pháp / Trách nhiệm cần làm gì)",
    "Dạng 1 - TH3: Tư tưởng, đạo lí (Suy nghĩ chung toàn diện về một tư tưởng/phẩm chất)",
    "Dạng 2: Nghị luận về một vấn đề cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả - Giải pháp)",
    "Dạng 3: Nghị luận lựa chọn quan điểm (Đứng trước 2 quan điểm / ý kiến)",
    "Dạng 4: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học",
    "Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm",
]

def extract_clean_topic_noun(text):
    clean = re.sub(
        r"(?i)(hãy viết một bài văn nghị luận xã hội|hãy viết bài văn nghị luận|viết bài văn nghị luận|khoảng 600 chữ|trình bày suy nghĩ của anh/chị về|suy nghĩ của anh/chị về|suy nghĩ về|bàn về|ý nghĩa của|vai trò của|tầm quan trọng của|sức mạnh của|sự cần thiết của|giá trị của|thuyết phục người khác từ bỏ|giải pháp khắc phục|làm thế nào để|cần làm gì để)",
        "",
        text,
    )
    clean = re.sub(r'[():.,?!"]', "", clean).strip()
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

def classify_essay_type(topic_text, vdnl_text="", manual_override="Tự động nhận diện theo đề bài"):
    if manual_override and manual_override != "Tự động nhận diện theo đề bài":
        if "Dạng 1 - TH1" in manual_override:
            return "DANG_1_TH1"
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
            "thuyết phục",
            "từ bỏ một thói quen",
            "từ bỏ thói quen",
            "từ bỏ một quan niệm",
            "từ bỏ quan niệm",
            "từ bỏ lối sống",
            "khuyên bạn từ bỏ",
            "viết bài luận thuyết phục",
        ]
    ):
        return "DANG_5_TU_BO"

    if any(
        kw in combined
        for kw in [
            "tác phẩm",
            "truyện ngắn",
            "bài thơ",
            "nhân vật văn học",
            "đoạn trích",
            "văn bản",
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
        "thờ ơ",
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
        ]
    ):
        return "DANG_1_TH2"

    if any(
        kw in combined
        for kw in [
            "ý nghĩa của",
            "sự cần thiết của",
            "giá trị của",
            "vai trò của",
            "sức mạnh của",
            "tầm quan trọng của",
            "vẻ đẹp của",
            "lợi ích của",
        ]
    ):
        return "DANG_1_TH1"

    return "DANG_1_TH3"

def get_essay_type_label(code):
    labels = {
        "DANG_1_TH1": "Dạng 1 (TH1): Nghị luận Tư tưởng, đạo lí — Bàn sâu về Ý nghĩa / Giá trị / Vai trò / Sức mạnh",
        "DANG_1_TH2": "Dạng 1 (TH2): Nghị luận Tư tưởng, đạo lí — Bàn về Bài học giải pháp (Trả lời câu hỏi: Cần làm gì?)",
        "DANG_1_TH3": "Dạng 1 (TH3): Nghị luận Tư tưởng, đạo lí — Bàn luận toàn diện (Giải thích -> Biểu hiện -> Ý nghĩa -> Dẫn chứng -> Phát huy)",
        "DANG_2_GIAI_QUYET": "Dạng 2: Nghị luận về một vấn đề cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả - Giải pháp 3 cấp độ)",
        "DANG_3_HAI_QUAN_DIEM": "Dạng 3: Nghị luận lựa chọn quan điểm (Phân tích mối quan hệ 2 quan điểm, bảo vệ lựa chọn & chỉ hạn chế quan điểm kia)",
        "DANG_4_VAN_HOC": "Dạng 4: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học",
        "DANG_5_TU_BO": "Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm",
    }
    return labels.get(code, labels["DANG_1_TH3"])

def is_positive_topic_declining(topic_text, vdnl_text):
    combined = (topic_text + " " + vdnl_text).lower()
    direct_negative = [
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
    # Tự động trích xuất 2 câu trích dẫn hoặc 2 vế quan điểm từ đề bài
    quotes = re.findall(r'["“”\']([^"“”\']{8,150})["“”\']', raw_topic)
    if len(quotes) >= 2:
        return quotes[0].strip(), quotes[1].strip()
    split_match = re.split(r"(?i)(?:nhưng có ý kiến khác lại cho rằng|trong khi đó|ngược lại có người cho rằng|hay là|hoặc)", raw_topic)
    if len(split_match) >= 2:
        v1 = extract_clean_topic_noun(split_match[0])[:100]
        v2 = extract_clean_topic_noun(split_match[1])[:100]
        if v1 and v2:
            return v1, v2
    return f"Góc nhìn đề cao khía cạnh thứ nhất của {vdnl}", f"Góc nhìn nhấn mạnh khía cạnh đối trọng/bổ sung của {vdnl}"

def get_pedagogical_structure_guide(type_code, raw_topic, vdnl):
    has_meaning_step = is_positive_topic_declining(raw_topic, vdnl)
    if type_code == "DANG_1_TH1":
        lines = [
            f"DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 1: Đề hỏi trực tiếp khía cạnh mặt tích cực (ý nghĩa/sự cần thiết/giá trị/vai trò/sức mạnh/tầm quan trọng của '{vdnl}').",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            f"- Mở bài: Dẫn dắt và nêu trực diện vấn đề nghị luận (nhấn mạnh tầm quan trọng/ý nghĩa của {vdnl}).",
            "- Thao tác 1 (Giải thích): Giải thích tường minh từ khóa/khái niệm/ý kiến và chốt vấn đề.",
            f"- Thao tác 2 (Bàn luận trọng tâm - Bàn sâu về Ý NGHĨA của VĐNL): Tập trung phân tích sâu sắc các tầng ý nghĩa, giá trị, sức mạnh của {vdnl} đối với cá nhân, mối quan hệ con người và xã hội; lý giải vì sao {vdnl} lại cần thiết.",
            "- Thao tác 3 (Dẫn chứng): Đưa dẫn chứng người thật việc thật cụ thể chứng minh cho sức mạnh/ý nghĩa đó.",
            "- Thao tác 4 (Phản đề & Bài học): Phê phán biểu hiện đi ngược lại, mở rộng biện chứng và rút ra bài học nhận thức, hành động.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_1_TH2":
        lines = [
            f"DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 2: Đề hỏi các bài học mang tính giải pháp (trả lời câu hỏi: Cần làm gì? Vai trò/trách nhiệm của chủ thể đối với '{vdnl}').",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            "- Mở bài: Dẫn dắt và nêu vấn đề nghị luận gắn với trách nhiệm/hành động cần thực hiện.",
            "- Thao tác 1 (Giải thích & Khái quát sự cần thiết): Giải thích khái niệm cụ thể và khẳng định ngắn gọn tầm quan trọng của vấn đề để làm tiền đề cho hành động.",
            "- Thao tác 2 (Bàn luận trọng tâm - Trả lời câu hỏi CẦN LÀM GÌ?): Triển khai hệ thống các bài học/giải pháp cụ thể, sâu sắc về nhận thức, hành động rèn luyện cá nhân và cống hiến cộng đồng.",
            "- Thao tác 3 (Dẫn chứng): Dẫn chứng người thật việc thật đã hành động quyết liệt, hiệu quả.",
            "- Thao tác 4 (Phản đề & Liên hệ): Phê phán thái độ thụ động, nói suông không làm; liên hệ bản thân và Kết bài.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_1_TH3":
        lines = [
            f"DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 3: Đề hỏi chung, nêu suy nghĩ về '{vdnl}'.",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            f"- Mở bài: Giới thiệu và dẫn vào vấn đề nghị luận '{vdnl}'.",
            f"- Thao tác 1 (Giải thích): Giải thích rõ ràng khái niệm/nhận định '{vdnl}'.",
            "- Thao tác 2 (Bàn luận toàn diện): Nêu biểu hiện cụ thể -> Phân tích ý nghĩa đối với cá nhân và xã hội -> Dẫn chứng thực tế -> Chỉ ra cần làm gì để phát huy (bài học) -> Liên hệ cá nhân.",
            "- Thao tác 3 (Phản đề & Mở rộng): Phê phán biểu hiện lệch lạc/trái ngược.",
            "- Kết bài: Khẳng định lại vấn đề và liên hệ cá nhân sâu sắc.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_2_GIAI_QUYET":
        if has_meaning_step:
            meaning_note = f"- Bước 2 (Ý nghĩa của vấn đề): Vì đề cập đến một giá trị tích cực đang có chiều hướng mai một ({vdnl}), cần viết 1 đoạn ngắn khẳng định ý nghĩa vốn có của nó trước khi nêu thực trạng."
        else:
            meaning_note = f"- Lưu ý: Vì đề hỏi trực tiếp về một hiện tượng tiêu cực ({vdnl}), đi thẳng từ Giải thích sang Lí do cần giải quyết (không cần đoạn ca ngợi ý nghĩa)."
        lines = [
            f"DẠNG BÀI: Nghị luận về một vấn đề cần giải quyết ('{vdnl}').",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            "- Mở bài: Dẫn dắt và nêu trực diện vấn đề cần giải quyết.",
            "- Bước 1 (Giải thích): Cắt nghĩa rõ bản chất khái niệm của vấn đề cần giải quyết.",
            meaning_note,
            "- Bước 3 (Lí do cần giải quyết): Viết thành 01 đoạn văn thống nhất nêu cụ thể: Thực trạng -> Nguyên nhân -> Hậu quả.",
            "- Bước 4 (Đưa ra Giải pháp - Trình bày thành 3 đoạn văn: Đối với Cá nhân - Gia đình - Nhà trường; mỗi đoạn bắt buộc nêu rõ giải pháp khả thi cụ thể + lí giải vì sao chọn như vậy + ít nhất 01 dẫn chứng thực tế cụ thể).",
            "- Bước 5 (Ý kiến khác & Phản biện): Nêu ý kiến trái chiều cho rằng không cần thiết -> Phản biện khẳng định vẫn cần khắc phục.",
            "- Kết bài: Khẳng định thông điệp và bài học liên hệ.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_3_HAI_QUAN_DIEM":
        lines = [
            f"DẠNG BÀI: Nghị luận lựa chọn quan điểm ('{vdnl}').",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            "- Mở bài: Giới thiệu cả 2 quan điểm và chỉ ra rõ quan điểm của mình.",
            "- Bước 1 (Giải thích & Mối quan hệ): Giải thích cụ thể từng quan điểm và chỉ ra mối quan hệ giữa 2 quan điểm.",
            "- Bước 2 (Lí giải vì sao chọn quan điểm của mình + Dẫn chứng thực tế cụ thể).",
            "- Bước 3 (Chỉ ra hạn chế của quan điểm còn lại).",
            "- Bước 4 (Bài học khái quát & Bài học liên hệ) -> Kết bài.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_4_VAN_HOC":
        lines = [
            f"DẠNG BÀI: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học ('{vdnl}').",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            "- Mở bài: Giới thiệu tác giả, tác phẩm và vấn đề xã hội rút ra.",
            "- Bước 1 (Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề).",
            "- Bước 2 (Giải thích cụ thể khái niệm vấn đề xã hội đó).",
            "- Bước 3 (Bàn luận ý nghĩa/tác động trong đời sống thực tế + Dẫn chứng người thật việc thật ngoài đời sống).",
            "- Bước 4 (Mở rộng, Phản đề & Bài học liên hệ) -> Kết bài.",
        ]
        return "\n".join(lines)

    if type_code == "DANG_5_TU_BO":
        lines = [
            f"DẠNG BÀI: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm ('{vdnl}').",
            "CẤU TRÚC TƯ DUY BẮT BUỘC:",
            "- Mở bài: Nêu rõ thói quen/quan niệm cần thuyết phục từ bỏ.",
            "- Bước 1 (Giải thích cụ thể thói quen/quan niệm & Chỉ ra biểu hiện cụ thể).",
            "- Bước 2 (Lí do vì sao phải từ bỏ: Phân tích hậu quả + dẫn chứng thực tế + lợi ích khi từ bỏ).",
            "- Bước 3 (Giải pháp từ bỏ: Cá nhân (trọng tâm) - Gia đình - Nhà trường; mỗi phần đều nêu cách làm cụ thể + lí giải vì sao làm vậy + dẫn chứng cụ thể).",
            "- Bước 4 (Dự đoán những ý kiến phản đối - Khuyên vẫn cần từ bỏ) -> Kết bài, bài học liên hệ.",
        ]
        return "\n".join(lines)

    return ""

# ==============================================================================
# HÀM XÂY DỰNG KHUNG ĐỊNH HƯỚNG TƯ DUY CỤ THỂ, CHI TIẾT SÁT TỪNG ĐỀ BÀI
# (Giải thích sẵn khái niệm, cung cấp sẵn lý lẽ & dẫn chứng người thật việc thật vào từng bước)
# ==============================================================================
def build_dynamic_outline_for_custom_topic(raw_topic_text, student_vdnl, manual_type_override="Tự động nhận diện theo đề bài"):
    formatted_topic = ensure_600_words_prompt(raw_topic_text)
    direct_problem = student_vdnl.strip() if student_vdnl.strip() else extract_clean_topic_noun(raw_topic_text)
    is_quote = is_metaphorical_quote_topic(raw_topic_text)
    type_code = classify_essay_type(raw_topic_text, direct_problem, manual_type_override)
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, raw_topic_text, direct_problem)

    # 1. GỌI GEMINI API VỚI YÊU CẦU BẮT BUỘC CUNG CẤP TRI THỨC CỤ THỂ (KHÔNG NÓI CHUNG CHUNG)
    prompt_lines = [
        "Đóng vai chuyên gia sư phạm Ngữ văn THPT. Hãy lập Khung định hướng tư duy CHI TIẾT, CỤ THỂ cho đề bài NLXH sau theo ĐÚNG DẠNG BÀI ĐÃ PHÂN LOẠI và trả về MỘT CHUỖI JSON HỢP LỆ (không dùng markdown code block):",
        f'- Đề bài: "{formatted_topic}"',
        f'- Vấn đề nghị luận trọng tâm: "{direct_problem}"',
        f'- Phân loại dạng bài: "{type_label}"',
        "",
        "CẤU TRÚC SƯ PHẠM BẮT BUỘC CỦA DẠNG BÀI NÀY:",
        structure_guide,
        "",
        "YÊU CẦU TỐI QUAN TRỌNG (TUYỆT ĐỐI KHÔNG VIẾT CHUNG CHUNG):",
        f"1. Ở mục explain_items: Phải viết rõ định nghĩa/giải thích cụ thể từ khóa '{direct_problem}' là gì (nếu có câu nói/2 quan điểm/tác phẩm văn học thì phải cắt nghĩa cụ thể từng vế ngay tại đây để học sinh nắm được khái niệm mà không cần tra Google).",
        "2. Ở mục questions (y_tra_loi): Không được ghi chung chung kiểu 'Hãy nêu thực trạng, hãy nêu giải pháp...'. Phải viết rõ nội dung thực trạng là gì, nguyên nhân là gì, hậu quả là gì; ở mỗi giải pháp (Cá nhân - Gia đình - Nhà trường) phải ghi rõ hành động cụ thể + lí giải vì sao + ghi rõ tên dẫn chứng người thật việc thật ngay trong từng đoạn.",
        "3. Ở mục evidence: Cung cấp ít nhất 2 dẫn chứng thực tế có tên nhân vật, sự kiện, số liệu xác thực gắn chặt với đề bài.",
        "",
        "Trả về JSON theo đúng các trường: text, vdnl_chuan, essay_type_code, essay_type_label, explain_items (mảng chuỗi), vdnl_ket_luan (chuỗi), questions (mảng đối tượng gồm cau_hoi và y_tra_loi), evidence (mảng đối tượng gồm ten, chi_tiet, y_nghia, nguon), counter (mảng chuỗi), dani_chi_tiet (đối tượng gồm mb, gt, bl, dc, pb, kb).",
    ]
    prompt = "\n".join(prompt_lines)

    ai_res = call_gemini_rest_api(prompt, temperature=0.35)
    if ai_res:
        try:
            match = re.search(r"\{.*\}", ai_res, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed["text"] = formatted_topic
                parsed["essay_type_code"] = type_code
                parsed["essay_type_label"] = type_label
                if "explain_items" in parsed and "questions" in parsed:
                    return parsed
        except Exception:
            pass

    # ==========================================================================
    # 2. BỘ MÁY TRI THỨC SƯ PHẠM NỘI BỘ CHUYÊN SÂU (KHI CHƯA NHẬP API KEY)
    # Tự động tra cứu Kho tri thức và cung cấp sẵn Khái niệm + Lý lẽ + Giải pháp + Dẫn chứng cụ thể!
    # ==========================================================================
    combined_low = (raw_topic_text + " " + student_vdnl).lower()
    matched_concept = None
    for kw, data in CONCEPT_DICTIONARY.items():
        if kw in combined_low:
            matched_concept = (kw, data)
            break

    matched_prob_kb = match_problem_solving_kb(raw_topic_text, direct_problem)
    vdnl_final = direct_problem

    # Xác định định nghĩa cụ thể & dẫn chứng cụ thể cho chủ đề
    if matched_prob_kb:
        specific_def = matched_prob_kb["def"]
        specific_manifest = matched_prob_kb["manifest"]
    elif matched_concept:
        specific_def = matched_concept[1]["def"]
        specific_manifest = matched_concept[1]["manifest"]
    else:
        specific_def = f"**{vdnl_final}** được hiểu là những nhận thức, chuẩn mực thái độ và hành vi ứng xử cụ thể của con người trước vấn đề đặt ra trong đời sống cá nhân và cộng đồng hiện đại."
        specific_manifest = f"Thể hiện trực tiếp qua cách suy nghĩ, lựa chọn thái độ và những hành động cụ thể hàng ngày của người trẻ trong học tập, giao tiếp và trách nhiệm xã hội liên quan đến **{vdnl_final}**."

    if matched_concept:
        c_ev_ten = matched_concept[1]["ev_ten"]
        c_ev_chitiet = matched_concept[1]["ev_chitiet"]
        c_ev_ynghia = matched_concept[1]["ev_ynghia"]
    else:
        c_ev_ten = "Lê Văn Phúc (Sáng lập mạng lưới 'Fly To Sky') & Biệt đội Sài Gòn Xanh"
        c_ev_chitiet = "Những người trẻ tuổi khởi xướng hàng chục dự án cộng đồng từ khi còn ngồi trên ghế nhà trường THPT, biến nhận thức thành hành động thực tế lan tỏa khắp cả nước."
        c_ev_ynghia = f"Minh chứng sống động, thuyết phục cho việc giải quyết và thực hành {vdnl_final} trong thực tiễn."

    # --------------------------------------------------------------------------
    # CHI TIẾT DẠNG 2: VẤN ĐỀ CẦN GIẢI QUYẾT
    # --------------------------------------------------------------------------
    if type_code == "DANG_2_GIAI_QUYET":
        if matched_prob_kb:
            has_meaning = matched_prob_kb.get("is_positive_declining", False)
            status_block = matched_prob_kb["status_cause_harm"]
            sol_ind = matched_prob_kb["sol_individual"]
            sol_fam = matched_prob_kb["sol_family"]
            sol_sch = matched_prob_kb["sol_school"]
            rebuttal_block = matched_prob_kb["counter_rebuttal"]
            meaning_text = matched_prob_kb.get("meaning_when_positive", f"**Ý nghĩa vốn có của {vdnl_final}:** Là nền tảng quan trọng giúp cá nhân phát triển lành mạnh và gắn kết tập thể.")
        else:
            has_meaning = is_positive_topic_declining(raw_topic_text, vdnl_final)
            meaning_text = f"**Ý nghĩa của {vdnl_final}:** Khi được duy trì và phát huy đúng đắn, **{vdnl_final}** là phẩm chất/kỹ năng thiết yếu giúp mỗi cá nhân hoàn thiện bản thân, nâng cao hiệu quả học tập và tạo dựng môi trường sống văn minh, gắn kết."
            status_block = (
                f"- **Thực trạng:** Trong đời sống học đường và xã hội hiện nay, vấn đề **{vdnl_final}** đang diễn biến đáng báo động ở một bộ phận không nhỏ giới trẻ ({specific_manifest}).\n"
                f"  - **Nguyên nhân:** *Chủ quan* xuất phát từ nhận thức chưa thấu đáo, tâm lý buông thả, thiếu kỷ luật tự thân của cá nhân; *Khách quan* do sự tác động từ mặt trái của môi trường số, áp lực cuộc sống và sự thiếu định hướng sát sao từ gia đình, xã hội.\n"
                f"  - **Hậu quả:** Nếu không kịp thời giải quyết, thực trạng này sẽ làm suy giảm trực tiếp năng lực học tập, bào mòn nhân cách người trẻ và gây hệ lụy tiêu cực cho sự phát triển bền vững của cộng đồng."
            )
            sol_ind = (
                f"- **Giải pháp khả thi:** Mỗi cá nhân phải chủ động nâng cao nhận thức đúng đắn về **{vdnl_final}**, tự thiết lập nguyên tắc kỷ luật hàng ngày, rèn luyện kỹ năng tự kiểm soát và tích cực tham gia các hoạt động thực tế lành mạnh.\n"
                f"  - **Lí giải vì sao:** Bởi mỗi cá nhân là chủ thể trực tiếp của mọi nhận thức và hành vi; nếu bản thân không tự giác thay đổi từ bên trong thì mọi sự hỗ trợ bên ngoài đều chỉ là hình thức.\n"
                f"  - **Dẫn chứng cụ thể:** Tấm gương tự rèn luyện kỷ luật và hành động vì cộng đồng của các bạn trẻ thuộc mạng lưới tình nguyện quốc gia 'Fly To Sky' (do Lê Văn Phúc sáng lập từ khi còn là học sinh THPT) hay các thủ khoa tự học vượt khó."
            )
            sol_fam = (
                f"- **Giải pháp khả thi:** Cha mẹ cần làm tấm gương sáng trong lối sống, dành thời gian chất lượng mỗi ngày để lắng nghe, thấu cảm và đồng hành định hướng con cái xử lý vấn đề **{vdnl_final}** thay vì áp đặt hay phó mặc.\n"
                f"  - **Lí giải vì sao:** Gia đình là cái nôi giáo dục đầu tiên và là điểm tựa tâm lý bền vững nhất giúp hình thành nhân cách, thói quen của người trẻ.\n"
                f"  - **Dẫn chứng cụ thể:** Mô hình 'Giờ tối gia đình không thiết bị điện tử – Cùng lắng nghe và chia sẻ' được hàng chục nghìn gia đình Việt Nam áp dụng hiệu quả trong việc gắn kết và định hướng con cái."
            )
            sol_sch = (
                f"- **Giải pháp khả thi:** Nhà trường cần đổi mới sinh hoạt dưới cờ, lồng ghép kỹ năng giải quyết vấn đề **{vdnl_final}** vào hoạt động trải nghiệm và phát huy vai trò của Phòng tư vấn tâm lý học đường; xã hội tăng cường truyền thông những mô hình tích cực.\n"
                f"  - **Lí giải vì sao:** Môi trường giáo dục và cộng đồng văn minh sẽ tạo ra hệ sinh thái nâng đỡ, định hướng chuẩn mực để học sinh duy trì hành vi tích cực lâu dài.\n"
                f"  - **Dẫn chứng cụ thể:** Phong trào xây dựng 'Trường học hạnh phúc' của Bộ Giáo dục & Đào tạo cùng các câu lạc bộ kỹ năng sống, dự án học sinh tự quản tại các trường THPT trên cả nước."
            )
            rebuttal_block = (
                f"- **Ý kiến khác (Trái chiều):** Có ý kiến cho rằng vấn đề **{vdnl_final}** chỉ là chuyện cá nhân nhỏ nhặt hoặc là hệ quả tất yếu của nhịp sống hiện đại nên không cần tốn công sức can thiệp, giải quyết.\n"
                f"- **Phản biện & Khẳng định:** Đây là góc nhìn phiến diện và thiếu trách nhiệm. Bởi những lệch lạc nhỏ nếu bị dung túng sẽ tích tụ thành khủng hoảng lớn cho cả thế hệ; do đó việc chung tay khắc phục là hoàn toàn cấp thiết."
            )

        explain_items = [
            f"- **Giải thích khái niệm cụ thể:** {specific_def}",
            f"- **Biểu hiện nhận diện:** {specific_manifest}",
        ]
        if has_meaning:
            explain_items.append(f"- {meaning_text}")
            step_offset = 1
        else:
            explain_items.append(
                f"- **Lưu ý triển khai:** Vì **{vdnl_final}** là vấn đề/hiện tượng tiêu cực trực tiếp, sau đoạn Giải thích, bài viết đi thẳng vào đoạn **Lí do cần giải quyết** (không viết đoạn ca ngợi ý nghĩa)."
            )
            step_offset = 0

        y_tra_loi_d2 = []
        if has_meaning:
            y_tra_loi_d2.append(f"- **Đoạn 1 — Ý nghĩa của vấn đề (Vì vấn đề tốt nhưng đang có chiều hướng chưa tốt):**\n  {meaning_text}")

        y_tra_loi_d2.extend([
            f"- **Đoạn {1 + step_offset} — Lí do cần giải quyết (Tích hợp chặt chẽ Thực trạng - Nguyên nhân - Hậu quả trong 1 đoạn):**\n  {status_block}",
            f"- **Đoạn {2 + step_offset} — Giải pháp đối với Cá nhân (Giải pháp khả thi + Lí giải + Dẫn chứng cụ thể):**\n  {sol_ind}",
            f"- **Đoạn {3 + step_offset} — Giải pháp đối với Gia đình (Giải pháp khả thi + Lí giải + Dẫn chứng cụ thể):**\n  {sol_fam}",
            f"- **Đoạn {4 + step_offset} — Giải pháp đối với Nhà trường & Xã hội (Giải pháp khả thi + Lí giải + Dẫn chứng cụ thể):**\n  {sol_sch}",
        ])

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": explain_items,
            "vdnl_ket_luan": f"Từ thực trạng và những hệ lụy trên, việc tìm kiếm các giải pháp đồng bộ để giải quyết vấn đề **{vdnl_final}** là yêu cầu bức thiết đặt ra cho mỗi cá nhân, gia đình và nhà trường.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống luận điểm chi tiết giải quyết vấn đề '{vdnl_final}' (Đã kèm lý lẽ & dẫn chứng cụ thể cho từng đoạn):",
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
                "gt": f"Giải thích khái niệm cụ thể của '{vdnl_final}' {'+ Đoạn nêu ý nghĩa vốn có của vấn đề' if has_meaning else '(Chuyển thẳng sang Lí do cần giải quyết)'}.",
                "bl": "1. Đoạn Lí do cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả).\n2. Ba đoạn Giải pháp (Cá nhân - Gia đình - Nhà trường): mỗi đoạn đều triển khai đủ Giải pháp khả thi + Lí giải vì sao + Dẫn chứng cụ thể như khung bên trên.",
                "dc": "Sử dụng trực tiếp các dẫn chứng đã gợi ý vào từng đoạn Giải pháp Cá nhân, Gia đình, Nhà trường.",
                "pb": "Nêu ý kiến khác cho rằng không cần thiết -> Phản biện bác bỏ và khẳng định vẫn cần khắc phục.",
                "kb": f"Khẳng định lại thông điệp giải quyết {vdnl_final} và rút ra bài học liên hệ cá nhân.",
            },
        }

    # --------------------------------------------------------------------------
    # CHI TIẾT DẠNG 3: LỰA CHỌN QUAN ĐIỂM (ĐỨNG TRƯỚC 2 QUAN ĐIỂM)
    # --------------------------------------------------------------------------
    if type_code == "DANG_3_HAI_QUAN_DIEM":
        v1_text, v2_text = parse_two_viewpoints_from_topic(raw_topic_text, vdnl_final)
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **Giải thích Quan điểm 1 (*\"{v1_text}\"*):** Quan điểm này đề cao giá trị của sự nỗ lực chủ động, khẳng định vai trò của ý chí/lựa chọn thứ nhất trong việc định hình thành công và nhân cách con người.",
                f"- **Giải thích Quan điểm 2 (*\"{v2_text}\"*):** Quan điểm này nhìn nhận vấn đề từ góc độ đối trọng, nhấn mạnh vào điều kiện thực tế, sự linh hoạt hoặc giá trị tinh thần chiều sâu.",
                "- **Chỉ ra mối quan hệ giữa 2 quan điểm:** Hai quan điểm tưởng chừng đối lập nhưng thực chất phản ánh hai chiều kích khác nhau của cuộc sống; tuy nhiên, đặt trong bối cảnh của tuổi trẻ hôm nay, người viết cần xác lập rõ quan điểm ưu tiên mà mình lựa chọn (hoặc lựa chọn quan điểm tích hợp có trọng tâm).",
            ],
            "vdnl_ket_luan": f"Đứng trước hai luồng ý kiến về **{vdnl_final}**, em lựa chọn bảo vệ quan điểm mang tính chủ động, kiến tạo giá trị thực chất, đồng thời nhìn nhận thấu đáo hạn chế nếu tuyệt đối hóa quan điểm còn lại.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống luận điểm chi tiết cho dạng Lựa chọn quan điểm ({vdnl_final}):",
                    "y_tra_loi": [
                        f"- **1. Giải thích 2 quan điểm & Mối quan hệ:**\n  + Cắt nghĩa rõ nội hàm của **\"{v1_text}\"** và **\"{v2_text}**\".\n  + Chỉ ra mối quan hệ: Hai góc nhìn xuất phát từ những hệ quy chiếu khác nhau trước vấn đề **{vdnl_final}**.",
                        "- **2. Lí giải vì sao chọn quan điểm của mình (Trọng tâm lập luận):**\n  + *Lý lẽ 1:* Quan điểm em chọn phù hợp với quy luật phát triển tự thân của con người hiện đại — giúp cá nhân làm chủ hoàn cảnh thay vì thụ động chờ đợi.\n  + *Lý lẽ 2:* Mang lại giá trị bền vững cho cả sự trưởng thành cá nhân lẫn sự tiến bộ của cộng đồng xã hội.",
                        f"- **3. Phân tích Dẫn chứng thực tế bảo vệ quan điểm đã chọn:**\n  + *Dẫn chứng cụ thể:* **{c_ev_ten}** ({c_ev_chitiet}).\n  + *Phân tích:* Hành trình ấy chứng minh hùng hồn cho tính đúng đắn của quan điểm mà em đã lựa chọn.",
                        "- **4. Chỉ ra hạn chế của quan điểm còn lại:**\n  + Nếu con người chỉ nghiêng hẳn về quan điểm còn lại một cách cực đoan, phiến diện thì dễ rơi vào sự thụ động, bảo thủ hoặc mất cân bằng trong thực tiễn cuộc sống.",
                        "- **5. Bài học khái quát & Bài học liên hệ cá nhân:**\n  + *Bài học khái quát:* Cần có bản lĩnh giữ vững lập trường đúng đắn, đồng thời có tư duy biện chứng, không cực đoan.\n  + *Bài học liên hệ:* Áp dụng trực tiếp quan điểm đã chọn vào việc học tập, rèn luyện nhân cách và định hướng tương lai của bản thân.",
                    ],
                }
            ],
            "evidence": [
                {
                    "ten": c_ev_ten,
                    "chi_tiet": c_ev_chitiet,
                    "y_nghia": "Dẫn chứng thực tế sắc bén dùng để bảo vệ quan điểm lựa chọn của học sinh ở Bước 2.",
                    "nguon": "Thực tiễn đời sống & Báo chí chính thống",
                }
            ],
            "counter": [
                "- **Chỉ ra hạn chế của quan điểm còn lại:** Phân tích rõ những điểm bất cập, thiếu khả thi nếu tuyệt đối hóa quan điểm không được chọn.",
                "- **Bài học khái quát & Liên hệ:** Rút ra chân lý nhận thức toàn diện và bài học hành động cụ thể cho tuổi trẻ.",
            ],
            "dani_chi_tiet": {
                "mb": f"Giới thiệu 2 quan điểm ('{v1_text}' và '{v2_text}') + Khẳng định rõ quan điểm lựa chọn của bản thân.",
                "gt": "Giải thích cụ thể từng quan điểm và chỉ ra mối quan hệ giữa 2 quan điểm.",
                "bl": "1. Lí giải sâu sắc vì sao chọn quan điểm của mình (kèm dẫn chứng thực tế).\n2. Chỉ ra những hạn chế của quan điểm còn lại.",
                "dc": f"Đưa dẫn chứng ({c_ev_ten}) vào ngay sau phần lí giải bảo vệ quan điểm của mình.",
                "pb": "Nêu bài học khái quát về cách nhìn nhận vấn đề đa chiều -> Bài học liên hệ cá nhân.",
                "kb": "Khẳng định lại sự lựa chọn và thông điệp kết bài.",
            },
        }

    # --------------------------------------------------------------------------
    # CHI TIẾT DẠNG 4: VẤN ĐỀ XÃ HỘI RÚT RA TỪ TÁC PHẨM VĂN HỌC
    # --------------------------------------------------------------------------
    if type_code == "DANG_4_VAN_HOC":
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **Bước 1 — Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề:** Qua tình huống, chi tiết nghệ thuật và hình tượng nhân vật trong văn bản/tác phẩm, tác giả đã gửi gắm một bức thông điệp nhân sinh sâu sắc về **{vdnl_final}**.",
                f"- **Bước 2 — Giải thích vấn đề xã hội đặt ra:** {specific_def}",
            ],
            "vdnl_ket_luan": f"Khép lại trang văn, vấn đề **{vdnl_final}** bước ra giữa đời thực như một câu hỏi lớn đánh thức nhận thức và lương tri của mỗi con người hôm nay.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống luận điểm chi tiết cho dạng Vấn đề xã hội rút ra từ tác phẩm văn học ({vdnl_final}):",
                    "y_tra_loi": [
                        f"- **1. Phân tích khái quát ngữ liệu văn học (Khoảng 1 đoạn ngắn):**\n  + Chỉ ra vẻ đẹp/bi kịch của nhân vật hoặc ý nghĩa của chi tiết trong tác phẩm.\n  + Chốt lại vấn đề xã hội cốt lõi được rút ra: **{vdnl_final}**.",
                        f"- **2. Giải thích vấn đề xã hội trong đời sống thực tiễn:**\n  + {specific_def}\n  + Biểu hiện trong đời thực: {specific_manifest}",
                        f"- **3. Bàn luận ý nghĩa, tác động của '{vdnl_final}' giữa cuộc đời thực:**\n  + *Đối với cá nhân:* Giúp con người bồi đắp tâm hồn, định hình bản lĩnh và sống có giá trị nhân văn.\n  + *Đối với cộng đồng, xã hội:* Hàn gắn những đứt gãy, đẩy lùi cái xấu và kiến tạo một xã hội tốt đẹp như khát vọng mà nhà văn gửi gắm.",
                        f"- **4. Dẫn chứng thực tế ngoài đời sống (Lưu ý: Lấy người thật việc thật, không lấy lại nhân vật văn học):**\n  + *Dẫn chứng cụ thể:* **{c_ev_ten}** — {c_ev_chitiet}.\n  + *Phân tích:* Minh chứng cho thấy thông điệp từ trang sách đã và đang tỏa sáng sinh động giữa cuộc đời.",
                        "- **5. Phản đề, Mở rộng & Bài học liên hệ:**\n  + Phê phán những người sống thờ ơ, thực dụng, đi ngược lại giá trị nhân văn của tác phẩm.\n  + Rút ra bài học nhận thức và hành động cụ thể cho bản thân người trẻ hôm nay.",
                    ],
                }
            ],
            "evidence": [
                {
                    "ten": c_ev_ten,
                    "chi_tiet": c_ev_chitiet,
                    "y_nghia": "Dẫn chứng người thật việc thật ngoài đời thực để chứng minh sức sống của vấn đề rút ra từ tác phẩm.",
                    "nguon": "Thực tiễn đời sống xã hội",
                }
            ],
            "counter": [
                f"- **Phê phán biểu hiện trái ngược:** Lên án lối sống vô cảm, ích kỷ hoặc đi ngược lại giá trị **{vdnl_final}** mà tác phẩm đã đặt ra.",
                "- **Khẳng định mối quan hệ Văn học - Cuộc đời & Bài học:** Văn chương chân chính luôn bắt nguồn từ cuộc đời và quay trở lại thanh lọc, nâng đỡ con người.",
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt từ sứ mệnh của văn chương hoặc giới thiệu tác giả, tác phẩm -> Nêu vấn đề xã hội rút ra: {vdnl_final}.",
                "gt": f"1. Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề.\n2. Giải thích khái niệm '{vdnl_final}' trong đời sống xã hội.",
                "bl": f"Bàn luận sâu sắc về biểu hiện, ý nghĩa và sức mạnh của '{vdnl_final}' đối với cá nhân và xã hội hiện đại.",
                "dc": f"Phân tích dẫn chứng người thật việc thật ngoài đời sống ({c_ev_ten}).",
                "pb": "Phản đề phê phán mặt trái, mở rộng vấn đề và rút ra bài học liên hệ cá nhân.",
                "kb": "Khẳng định giá trị trường tồn của thông điệp từ tác phẩm văn học trong dòng chảy cuộc đời.",
            },
        }

    # --------------------------------------------------------------------------
    # CHI TIẾT DẠNG 5: THUYẾT PHỤC NGƯỜI KHÁC TỪ BỎ MỘT THÓI QUEN HAY MỘT QUAN NIỆM
    # --------------------------------------------------------------------------
    if type_code == "DANG_5_TU_BO":
        if matched_prob_kb:
            habit_def = matched_prob_kb["def"]
            habit_manifest = matched_prob_kb["manifest"]
            harm_and_benefit = (
                f"  + **Hậu quả nghiêm trọng nếu giữ thói quen/quan niệm này:** {matched_prob_kb['status_cause_harm']}\n"
                f"  + **Dẫn chứng thực tế về hậu quả:** Thực tế đã có biết bao bạn trẻ đánh mất cơ hội học tập, rơi vào khủng hoảng tâm lý và rạn nứt các mối quan hệ tốt đẹp chỉ vì dung túng cho thói quen này.\n"
                f"  + **Lợi ích to lớn khi dũng cảm từ bỏ:** {matched_prob_kb.get('benefit_of_quitting', 'Giúp cá nhân giải phóng năng lượng tích cực, làm chủ cuộc sống và được mọi người tin yêu, tôn trọng.')}"
            )
            sol_ind = matched_prob_kb["sol_individual"]
            sol_fam = matched_prob_kb["sol_family"]
            sol_sch = matched_prob_kb["sol_school"]
            predict_objection = matched_prob_kb["counter_rebuttal"]
        else:
            habit_def = f"**{vdnl_final}** là một thói quen chưa tốt / quan niệm lệch lạc được hình thành từ sự thiếu tự giác hoặc cái nhìn phiến diện, lâu dần ăn sâu vào nếp nghĩ và hành vi của con người."
            habit_manifest = f"Biểu hiện cụ thể qua lời nói, thái độ chủ quan, sự chần chừ hoặc cách ứng xử thiếu chuẩn mực trong học tập, công việc và giao tiếp hàng ngày liên quan đến **{vdnl_final}**."
            harm_and_benefit = (
                f"  + **Hậu quả nặng nề:** Thói quen/quan niệm **{vdnl_final}** âm thầm bào mòn thời gian, làm suy giảm năng lực học tập, thu hẹp cơ hội phát triển của bản thân và gây ảnh hưởng tiêu cực tới tập thể.\n"
                f"  + **Dẫn chứng thực tế:** Không ít người trẻ có tố chất thông minh nhưng vì không vượt qua được **{vdnl_final}** nên đã tụt hậu phía sau trong kỷ nguyên số đầy cạnh tranh.\n"
                f"  + **Lợi ích thiết thực khi từ bỏ:** Khi dứt khoát từ bỏ **{vdnl_final}**, mỗi người sẽ tìm lại sự tự chủ, nâng cao hiệu suất học tập, hoàn thiện nhân cách và nhận được sự tin cậy từ cộng đồng."
            )
            sol_ind = (
                f"- **Giải pháp đối với Cá nhân (TRỌNG TÂM):**\n"
                f"  + *Cách làm khả thi:* Thẳng thắn nhìn nhận tác hại của **{vdnl_final}**, đặt mục tiêu thay đổi theo từng chặng nhỏ (Quy tắc 21 ngày tạo thói quen mới), thay thế hành vi cũ bằng một hoạt động tích cực cụ thể và tự kỷ luật mỗi ngày.\n"
                f"  + *Lí giải vì sao:* Thói quen/quan niệm nằm trong chính tiềm thức và hành vi của mỗi người; chỉ khi bản thân thực sự quyết tâm thay đổi thì quá trình từ bỏ mới thành công.\n"
                f"  + *Dẫn chứng cụ thể:* Hành trình tự rèn luyện kỷ luật thép, vượt qua thói quen trì hoãn và giới hạn bản thân của kình ngư Nguyễn Thị Ánh Viên hay các thủ khoa tự học."
            )
            sol_fam = (
                f"- **Giải pháp đối với Gia đình:**\n"
                f"  + *Cách làm khả thi:* Cha mẹ và người thân kiên nhẫn đồng hành, nhắc nhở nhẹ nhàng, ghi nhận từng bước tiến bộ nhỏ của con thay vì chê bai, chỉ trích nặng lời.\n"
                f"  + *Lí giải vì sao:* Sự khích lệ và môi trường gia đình tích cực sẽ tạo động lực tâm lý giúp người trẻ không bỏ cuộc giữa chừng khi thay đổi thói quen.\n"
                f"  + *Dẫn chứng cụ thể:* Sự đồng hành thấu cảm của gia đình trong các chương trình 'Cha mẹ cùng con thay đổi thói quen tích cực'."
            )
            sol_sch = (
                f"- **Giải pháp đối với Nhà trường & Tập thể:**\n"
                f"  + *Cách làm khả thi:* Thầy cô và bạn bè tạo môi trường sinh hoạt câu lạc bộ lành mạnh, cùng lập nhóm 'Đôi bạn cùng tiến' để nhắc nhở và truyền cảm hứng rèn luyện mỗi ngày.\n"
                f"  + *Lí giải vì sao:* Áp lực tích cực từ tập thể bạn bè đồng trang lứa giúp cá nhân duy trì cam kết từ bỏ thói quen xấu dễ dàng hơn.\n"
                f"  + *Dẫn chứng cụ thể:* Phong trào 'Đôi bạn cùng tiến' và các câu lạc bộ rèn luyện kỹ năng sống tại các trường THPT."
            )
            predict_objection = (
                f"- **Dự đoán những ý kiến phản đối / bao biện:** Người mang thói quen/quan niệm **{vdnl_final}** có thể phản đối rằng: *'Thói quen này đã thành bản tính khó đổi'* hoặc *'Đó là quyền cá nhân, chẳng ảnh hưởng lớn đến ai'*.\n"
                f"- **Khuyên nhủ & Khẳng định vẫn cần từ bỏ:** Hãy nhẹ nhàng nhưng kiên quyết chỉ rõ: Không ai sinh ra đã hoàn hảo, mọi thói quen đều do rèn luyện mà thành. Nếu cứ thỏa hiệp với một thói quen/quan niệm sai lầm, chính tương lai của bạn sẽ phải trả giá đắt. Vì vậy, bắt đầu từ bỏ ngay hôm nay là lựa chọn sáng suốt nhất."
            )

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **1. Giải thích cụ thể thói quen / quan niệm:** {habit_def}",
                f"- **2. Biểu hiện thực tế trong đời sống:** {habit_manifest}",
            ],
            "vdnl_ket_luan": f"Nhận thức rõ những tác hại ấy, việc thuyết phục và đồng hành để mỗi người kiên quyết từ bỏ **{vdnl_final}** là điều vô cùng ý nghĩa.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống luận điểm chi tiết Thuyết phục từ bỏ '{vdnl_final}' (Đã kèm lý lẽ, giải pháp 3 cấp độ & dẫn chứng cụ thể):",
                    "y_tra_loi": [
                        f"- **Bước 1 — Giải thích & Biểu hiện:**\n  + {habit_def}\n  + *Biểu hiện:* {habit_manifest}",
                        f"- **Bước 2 — Lí do vì sao phải từ bỏ (Phân tích Hậu quả + Dẫn chứng + Lợi ích khi từ bỏ):**\n{harm_and_benefit}",
                        f"- **Bước 3a — Giải pháp từ bỏ đối với Cá nhân (TRỌNG TÂM - Nêu cách làm + Lí giải + Dẫn chứng):**\n  {sol_ind}",
                        f"- **Bước 3b — Giải pháp phối hợp từ Gia đình (Cách làm + Lí giải + Dẫn chứng):**\n  {sol_fam}",
                        f"- **Bước 3c — Giải pháp phối hợp từ Nhà trường (Cách làm + Lí giải + Dẫn chứng):**\n  {sol_sch}",
                        f"- **Bước 4 — Dự đoán ý kiến phản đối & Khuyên nhủ thuyết phục:**\n  {predict_objection}",
                    ],
                }
            ],
            "evidence": [
                {
                    "ten": "Dẫn chứng vượt qua thói quen/giới hạn bản thân: Nguyễn Thị Ánh Viên & Thử thách '21 ngày thay đổi bản thân'",
                    "chi_tiet": "Rèn luyện kỷ luật nghiêm ngặt từng ngày để vượt qua sự trì hoãn và sức ỳ tâm lý, biến mục tiêu thành hành động thực tế.",
                    "y_nghia": "Chứng minh không có thói quen xấu hay định kiến nào là không thể từ bỏ nếu có phương pháp đúng và ý chí kiên định.",
                    "nguon": "Thực tiễn đời sống & Báo chí chính thống",
                }
            ],
            "counter": [predict_objection],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt bằng giọng điệu chân thành, tôn trọng -> Nêu rõ thói quen/quan niệm cần thuyết phục từ bỏ: {vdnl_final}.",
                "gt": f"Giải thích rõ bản chất của '{vdnl_final}' -> Nêu các biểu hiện cụ thể trong đời sống hàng ngày.",
                "bl": "1. Lí do phải từ bỏ (Hậu quả + Dẫn chứng + Lợi ích khi từ bỏ).\n2. Giải pháp từ bỏ ở 3 cấp độ: Cá nhân (Trọng tâm) - Gia đình - Nhà trường (Mỗi cấp độ đều nêu rõ cách làm + lí giải vì sao + dẫn chứng cụ thể).",
                "dc": "Lồng ghép dẫn chứng vào cả phần Hậu quả và phần Giải pháp từ bỏ.",
                "pb": "Dự đoán những ý kiến phản đối/biện minh -> Phân tích thấu tình đạt lý để khuyên vẫn cần kiên quyết từ bỏ.",
                "kb": "Khẳng định niềm tin vào sự thay đổi tích cực và rút ra bài học liên hệ bản thân.",
            },
        }

    # --------------------------------------------------------------------------
    # CHI TIẾT DẠNG 1: TƯ TƯỞNG, ĐẠO LÍ (CHIA 3 TRƯỜNG HỢP CỤ THỂ)
    # --------------------------------------------------------------------------
    if not is_quote:
        explain_list = [
            f"- **Giải thích khái niệm cụ thể:** {specific_def}",
            f"- **Biểu hiện cốt lõi:** {specific_manifest}",
        ]
    else:
        explain_list = [
            f"- **Giải thích câu nói/nhận định trong đề:** Cắt nghĩa lớp nghĩa tường minh (hình ảnh, từ ngữ trong câu trích dẫn) và rút ra thông điệp hàm ẩn sâu sắc về **{vdnl_final}**.",
            f"- **Giải thích khái niệm cốt lõi:** {specific_def}",
        ]

    why_detail = matched_concept[1]["why"] if matched_concept else f"Trong dòng chảy nhiều biến động của xã hội hiện đại, **{vdnl_final}** chính là điểm tựa tinh thần vững chắc giúp con người khẳng định giá trị bản thân và lan tỏa điều tử tế."
    promote_detail = matched_concept[1].get("how_to_promote", f"Mỗi người trẻ cần chủ động nâng cao nhận thức, rèn luyện **{vdnl_final}** thông qua những hành động kiên trì, thiết thực trong học tập và ứng xử hàng ngày.") if matched_concept else f"Mỗi người trẻ cần chủ động nâng cao nhận thức, rèn luyện **{vdnl_final}** thông qua những hành động kiên trì, thiết thực trong học tập và ứng xử hàng ngày."
    counter_detail = matched_concept[1]["counter"] if matched_concept else f"Lối sống thờ ơ, hời hợt, thực dụng hoặc đi ngược lại những giá trị tốt đẹp của **{vdnl_final}**."

    if type_code == "DANG_1_TH1":
        y_list = [
            f"- **Luận điểm 1 — Ý nghĩa đối với việc định hình nội lực và bản lĩnh cá nhân:** {why_detail}",
            f"- **Luận điểm 2 — Giá trị bồi đắp chiều sâu tâm hồn và nhân cách:** Thực hành **{vdnl_final}** giúp con người sống có lý tưởng, tìm thấy hạnh phúc thực chất và không bị đánh mất mình trước những cám dỗ.",
            f"- **Luận điểm 3 — Vai trò kết nối và truyền cảm hứng giữa người với người:** Tạo dựng niềm tin, sự thấu hiểu, đồng cảm và lan tỏa nguồn năng lượng tích cực tới những người xung quanh.",
            f"- **Luận điểm 4 — Sức mạnh thúc đẩy sự phát triển của cộng đồng, xã hội:** Khi **{vdnl_final}** trở thành chuẩn mực chung, nó sẽ kiến tạo một xã hội văn minh, nhân ái và giàu nội lực phát triển.",
            f"- **Luận điểm 5 — Khẳng định tầm quan trọng qua góc nhìn đối lập (Nếu thiếu vắng):** Nếu thiếu đi giá trị này, cá nhân dễ rơi vào khủng hoảng phương hướng và xã hội trở nên lạnh lùng, trì trệ.",
        ]
        bl_summary = f"Xoáy sâu toàn diện vào 5 tầng Ý NGHĨA, GIÁ TRỊ, VAI TRÒ, SỨC MẠNH của '{vdnl_final}' đối với cá nhân, mối quan hệ con người và xã hội."
    elif type_code == "DANG_1_TH2":
        y_list = [
            f"- **Luận điểm 1 — Khái quát sự cần thiết phải hành động:** {why_detail}",
            f"- **Luận điểm 2 — Bài học giải pháp về Nhận thức & Thái độ (Cần hiểu và xác lập tâm thế ra sao?):** Mỗi người trẻ cần nhận thức sâu sắc trách nhiệm của mình đối với **{vdnl_final}**, xóa bỏ tâm lý ỷ lại, thờ ơ hay ngại khó.",
            f"- **Luận điểm 3 — Bài học giải pháp về Hành động rèn luyện cá nhân (Cần làm gì cụ thể?):** {promote_detail}",
            f"- **Luận điểm 4 — Bài học giải pháp trong Gắn kết & Cống hiến cộng đồng:** Chủ động tham gia các hoạt động tập thể, dự án xã hội để biến nhận thức về **{vdnl_final}** thành giá trị đóng góp thiết thực cho quê hương, đất nước.",
            f"- **Luận điểm 5 — Bản lĩnh kiên trì thực hiện đến cùng:** Kiên định vượt qua những rào cản, cám dỗ để duy trì hành động bền bỉ chứ không làm theo phong trào nhất thời.",
        ]
        bl_summary = f"Trọng tâm trả lời câu hỏi CẦN LÀM GÌ? (Triển khai hệ thống các bài học giải pháp cụ thể về nhận thức, hành động cá nhân và trách nhiệm cộng đồng đối với '{vdnl_final}')."
    else:  # DANG_1_TH3
        y_list = [
            f"- **Bước 1 — Biểu hiện cụ thể của '{vdnl_final}' trong đời sống:** {specific_manifest}",
            f"- **Bước 2 — Bàn luận: Nêu ý nghĩa đối với cá nhân:** {why_detail}",
            f"- **Bước 3 — Bàn luận: Nêu ý nghĩa đối với cộng đồng, xã hội:** Góp phần gắn kết tình người, lan tỏa lối sống đẹp và tạo động lực thúc đẩy xã hội phát triển văn minh.",
            f"- **Bước 4 — Phân tích Dẫn chứng thực tế:** Đưa tấm gương **{c_ev_ten}** ({c_ev_chitiet}) để chứng minh sinh động.",
            f"- **Bước 5 — Cần làm gì để phát huy '{vdnl_final}' (Bài học định hướng) & Liên hệ cá nhân:** {promote_detail} Từ đó soi chiếu trực tiếp vào quá trình tự tu dưỡng của bản thân.",
        ]
        bl_summary = f"Triển khai đúng mạch toàn diện: Giải thích '{vdnl_final}' -> Biểu hiện -> Bàn luận nêu ý nghĩa -> Dẫn chứng ({c_ev_ten}) -> Cần làm gì để phát huy (bài học) -> Liên hệ cá nhân."

    return {
        "text": formatted_topic,
        "vdnl_chuan": vdnl_final,
        "essay_type_code": type_code,
        "essay_type_label": type_label,
        "explain_items": explain_list,
        "vdnl_ket_luan": f"Từ đó, đề bài đặt ra vấn đề nghị luận sâu sắc và giàu tính thời sự: **{vdnl_final}**.",
        "questions": [{"cau_hoi": f"Hệ thống luận điểm chi tiết ({type_label}):", "y_tra_loi": y_list}],
        "evidence": [
            {
                "ten": c_ev_ten,
                "chi_tiet": c_ev_chitiet,
                "y_nghia": c_ev_ynghia,
                "nguon": "Thực tiễn đời sống xã hội & Báo chí chính thống",
            }
        ],
        "counter": [
            f"- **Phê phán biểu hiện lệch lạc:** {counter_detail}",
            f"- **Mở rộng biện chứng & Bài học liên hệ:** Cần đặt **{vdnl_final}** trong cái nhìn tỉnh táo, toàn diện, tránh giáo điều hình thức; rút ra bài học hành động thực chất cho bản thân.",
        ],
        "dani_chi_tiet": {
            "mb": f"Dẫn dắt tự nhiên -> Trích dẫn đề bài -> Nêu vấn đề nghị luận: {vdnl_final}.",
            "gt": f"Giải thích cụ thể khái niệm '{vdnl_final}': {specific_def}",
            "bl": bl_summary,
            "dc": f"Phân tích dẫn chứng cụ thể: {c_ev_ten}.",
            "pb": f"Phê phán biểu hiện trái ngược ({counter_detail}) và mở rộng góc nhìn biện chứng.",
            "kb": f"Khẳng định lại giá trị của {vdnl_final} và liên hệ trách nhiệm tuổi trẻ.",
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
# HÀM TRỢ LÝ TƯ VẤN SƯ PHẠM ĐA LƯỢT - GIẢI ĐÁP CỤ THỂ KHÁI NIỆM, DẪN CHỨNG, LẬP LUẬN
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

    # 1. Nếu học sinh nhờ viết hộ cả bài văn: từ chối khéo nhưng đưa ngay khung ý + từ khóa cụ thể của đề
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
            f"- **Khung câu gợi mở cho {part_hint}:** *\"Giữa dòng chảy không ngừng của cuộc sống hiện đại, {vdnl} không chỉ là một khái niệm nhận thức mà còn là thước đo bản lĩnh và trách nhiệm của mỗi người trẻ...\"*\n"
            "👉 *Em hãy viết tiếp 2-3 câu theo ý trên rồi gửi vào đây, cô sẽ sửa câu chữ cho em thật sắc sảo!*"
        )

    # 2. GỌI GEMINI API VỚI YÊU CẦU CUNG CẤP KIẾN THỨC CỤ THỂ (KHÁI NIỆM, DẪN CHỨNG, LÝ LẼ RÕ RÀNG)
    sys_lines = [
        "Bạn là một giáo viên Ngữ văn THPT giỏi chuyên môn, nhạy bén và tận tâm, đang trực tiếp hướng dẫn học sinh viết bài Nghị luận xã hội (khoảng 600 chữ).",
        "THÔNG TIN ĐỀ BÀI ĐANG LÀM:",
        f'- Đề bài: "{topic_text}"',
        f'- Vấn đề nghị luận trọng tâm: "{vdnl}"',
        "- Phân loại dạng đề và cấu trúc chuẩn:",
        structure_guide,
        f'- Bản nháp học sinh đang viết (nếu có): "{draft_excerpt}"',
        "",
        "QUY TẮC PHẢN HỒI BẮT BUỘC (ĐỂ HỌC SINH KHÔNG PHẢI TRA GOOGLE HAY CHATGPT):",
        "1. CUNG CẤP KIẾN THỨC CỤ THỂ, TRỰC DIỆN: Khi học sinh hỏi khái niệm/từ khóa nào, phải định nghĩa rõ ràng, đầy đủ khái niệm đó là gì. Khi học sinh hỏi dẫn chứng, phải nêu rõ tên nhân vật, sự kiện thực tế, số liệu/hành động cụ thể và câu văn mẫu phân tích dẫn chứng đó. Khi học sinh hỏi giải pháp hay luận điểm, phải vạch ra ý cụ thể gắn sát với đề bài chứ tuyệt đối không chỉ nói lý thuyết chung chung.",
        "2. NHẠY BÉN THEO MẠCH HỘI THOẠI: Đọc kỹ lịch sử trò chuyện. Tuyệt đối không lặp lại câu trả lời cũ. Nếu học sinh hỏi tiếp ('còn dẫn chứng nào khác không', 'giải thích rõ hơn ý 2', 'làm sao nối đoạn...'), phải cung cấp dẫn chứng mới và góc nhìn sâu hơn.",
        f"3. BÁM SÁT ĐÚNG DẠNG BÀI: Hướng dẫn đúng theo cấu trúc của '{type_label}'. Không viết hộ nguyên bài văn 600 chữ hoàn chỉnh.",
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

    # ==========================================================================
    # 3. BỘ MÁY PHẢN HỒI SƯ PHẠM NỘI BỘ CỤ THỂ, SÂU SẮC (KHI CHƯA NHẬP API KEY)
    # ==========================================================================
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
        for w in ["thêm", "khác", "nữa", "sâu hơn", "cụ thể", "chưa hiểu", "rõ hơn", "ví dụ", "còn gì", "ý 2", "ý 3", "đoạn 2", "tiếp"]
    )
    effective_query = (last_user_q + " " + q_low) if (is_followup and len(q_low.split()) <= 10) else q_low

    def count_previous_topic_asks(keywords):
        cnt = 0
        for r, m in chat_history_list:
            if r == "user" and any(k in m.lower() for k in keywords):
                cnt += 1
        return cnt

    # Lấy toàn bộ dẫn chứng từ Kho 9 chủ điểm
    all_repo_evidences = []
    try:
        for topic_name, dc_list in db.KHO_DAN_CHUNG_9_CHU_DIEM.items():
            for item in dc_list:
                all_repo_evidences.append((topic_name, item))
    except Exception:
        pass

    # --- NHÁNH A: HỎI KHÁI NIỆM / GIẢI THÍCH TỪ KHÓA ("A là gì", "giải thích", "khái niệm") ---
    gt_keywords = ["giải thích", "khái niệm", "từ khóa", "là gì", "nghĩa là gì", "hiểu như thế nào"]
    if any(k in effective_query for k in gt_keywords):
        # Kiểm tra xem học sinh có hỏi đích danh một khái niệm trong từ điển không
        for kw, c_data in CONCEPT_DICTIONARY.items():
            if kw in effective_query:
                return (
                    f"👩‍🏫 **Trợ lý Ngữ văn:** Cô giải thích cụ thể khái niệm **{c_data['term']}** để em đưa ngay vào đầu phần Thân bài nhé:\n"
                    f"- **Định nghĩa chuẩn xác:** {c_data['def']}\n"
                    f"- **Biểu hiện thực tế:** {c_data['manifest']}\n"
                    f"- **Câu văn mẫu ghép vào bài viết:** *\"Hiểu một cách sâu sắc, {c_data['def'].replace('**', '')} Chính phẩm chất ấy được thể hiện sinh động qua {c_data['manifest'].lower()}\"*."
                )
        prob_kb = match_problem_solving_kb(effective_query, vdnl)
        if prob_kb:
            return (
                f"👩‍🏫 **Trợ lý Ngữ văn:** Cô cung cấp ngay phần **Giải thích khái niệm & Biểu hiện cụ thể** cho vấn đề **{prob_kb['name']}**:\n"
                f"- **Khái niệm:** {prob_kb['def']}\n"
                f"- **Biểu hiện cụ thể:** {prob_kb['manifest']}\n"
                "- **Câu chuyển ý sang đoạn tiếp theo:** *\"Nhận diện rõ bản chất và những biểu hiện đáng lo ngại ấy, chúng ta càng thấy rõ tính cấp thiết của việc tìm hiểu nguyên nhân và giải pháp khắc phục triệt để vấn đề này.\"*"
            )
        gt_content = "\n".join(explain_list) if explain_list else f"- **{vdnl}** là nhận thức đúng đắn và hành động thiết thực của con người trước vấn đề đặt ra trong đời sống."
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Đây là phần **Giải thích cụ thể** cho đề bài **'{vdnl}'** (*{type_label}*) để em viết đoạn đầu Thân bài:\n"
            f"{gt_content}\n"
            f"- **Câu văn mẫu dẫn dắt giải thích:** *\"Trước hết, cần hiểu thấu đáo bản chất của vấn đề: {vdnl} không phải là những lý thuyết xa vời mà chính là...\"*"
        )

    # --- NHÁNH B: HỎI VỀ DẪN CHỨNG (Đưa dẫn chứng cụ thể tên người, sự việc, nguồn báo chí & câu văn mẫu) ---
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
            ev_lines.append("\n💡 **oạn văn mẫu đưa dẫn chứng vào bài (Em có thể tham khảo cách hành văn này):**")
            first_ev_name = cur_evs[0].get("ten", "những tấm gương người trẻ tiêu biểu")
            ev_lines.append(f"*\"Thực tiễn đời sống đã ghi nhận biết bao minh chứng sống động cho điều đó, mà tiêu biểu là câu chuyện về {first_ev_name}. {cur_evs[0].get('chi_tiet', '')} Chính hành động thiết thực ấy đã khẳng định đầy thuyết phục giá trị của {vdnl}.\"*")
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
                    f"👉 **Câu nối dẫn chứng vào luận điểm:** *\"Nhìn vào hành trình của {dc1['ten']}, người trẻ chúng ta càng thấm thía rằng {vdnl} được khẳng định bằng chính những hành động bền bỉ, dám dấn thân giữa đời thực.\"*"
                )

    # --- NHÁNH C: HỎI VỀ LUẬN ĐIỂM / GIẢI PHÁP / THỰC TRẠNG (Trả lời cụ thể từng ý + lý lẽ + dẫn chứng) ---
    bl_keywords = ["luận điểm", "bàn luận", "thân bài", "dàn ý", "ý nghĩa", "vai trò", "giải pháp", "thực trạng", "nguyên nhân", "hậu quả", "lí do", "lý do", "triển khai", "cần làm gì", "bài học", "cá nhân", "gia đình", "nhà trường"]
    if any(k in effective_query for k in bl_keywords):
        ask_idx = count_previous_topic_asks(bl_keywords)
        bl_items = []
        for q in questions_list:
            for ans in q.get("y_tra_loi", []):
                bl_items.append(ans)
        bl_text = "\n\n".join(bl_items)

        if ask_idx == 0:
            return (
                f"👩‍🏫 **Trợ lý Ngữ văn:** Đối với đề **'{vdnl}'** thuộc **{type_label}**, cô vạch sẵn cho em **nội dung lý lẽ và dẫn chứng cụ thể cho từng đoạn Thân bài** như sau (em không cần phải tìm ở đâu khác):\n\n"
                f"{bl_text}\n\n"
                "👉 *Em đang bắt đầu viết đoạn số mấy trong các đoạn trên? Hãy nhắn số đoạn (VD: 'hướng dẫn em viết thành đoạn văn hoàn chỉnh cho ý số 2') để cô cung cấp khung câu nối chi tiết cho đoạn đó nhé!*"
            )
        else:
            # Lượt hỏi tiếp theo về luận điểm: cung cấp mẫu câu triển khai sâu từng đoạn
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
                f"- *Câu 1 (Mở đoạn trực diện):* Trước hết, xét trên bình diện thực tiễn, một khía cạnh trọng tâm cần bàn luận sâu sắc về {vdnl} chính là...\n"
                "- *Câu 2-3 (Lí giải sâu nguyên nhân/bản chất):* Bởi lẽ, trong bối cảnh xã hội hiện đại hôm nay, khi mà... thì điều này đóng vai trò quyết định bởi...\n"
                "- *Câu 4-5 (Đưa dẫn chứng cụ thể):* Minh chứng rõ nét nhất cho điều này là... (nêu tên nhân vật/sự kiện và phân tích ngắn gọn ý nghĩa).\n"
                "- *Câu 6 (Chốt đoạn):* Như vậy, có thể khẳng định đây chính là mắt xích quan trọng không thể tách rời khi nhìn nhận về vấn đề."
            )

    # --- NHÁNH D: HỎI VỀ PHẢN ĐỀ / Ý KIẾN TRÁI CHIỀU / DỰ ĐOÁN PHẢN ĐỐI ---
    pb_keywords = ["phản đề", "phản biện", "mở rộng", "lật lại", "phê phán", "ý kiến khác", "trái chiều", "phản đối"]
    if any(k in effective_query for k in pb_keywords):
        pb_content = "\n".join(counter_list) if counter_list else f"- Phê phán biểu hiện thiếu **{vdnl}** và mở rộng góc nhìn biện chứng."
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Đây là nội dung cụ thể và khung câu văn cho đoạn **Phản đề / Ý kiến trái chiều** của đề **'{vdnl}'** (*{type_label}*):\n"
            f"{pb_content}\n\n"
            "✍️ **Mẫu câu diễn đạt sắc bén em có thể vận dụng ngay:**\n"
            f"*\"Nhìn nhận vấn đề một cách đa chiều, bên cạnh những giá trị tích cực, thực tế vẫn tồn tại một bộ phận người trẻ có suy nghĩ và hành vi lệch lạc đối với {vdnl}... Tuy nhiên, có ý kiến lại bao biện cho rằng điều đó là bình thường và không cần thay đổi. Đây là một cái nhìn phiến diện cần được bác bỏ, bởi nếu dung túng cho sự lệch lạc ấy, chính cá nhân và cộng đồng sẽ phải gánh chịu hệ lụy lâu dài.\"*"
        )

    # --- NHÁNH E: HỎI MỞ BÀI / KẾT BÀI ---
    if any(w in effective_query for w in ["mở bài", "câu đầu", "dẫn dắt", "kết bài", "liên hệ"]):
        dani = cur_de_info.get("dani_chi_tiet", {})
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Cô gợi ý cụ thể cách viết **Mở bài và Kết bài** đúng chuẩn **{type_label}** cho đề **'{vdnl}'**:\n"
            f"- **Mở bài ({dani.get('mb', '')}):**\n"
            f"  *Mẫu dẫn dắt:* \"Giữa kỷ nguyên số đầy biến động, nơi mỗi người trẻ đều đứng trước vô vàn cơ hội nhưng cũng không ít thử thách định hình nhân cách, câu chuyện về **{vdnl}** trở thành một vấn đề thiết실 và đáng suy ngẫm hơn bao giờ hết...\"\n"
            f"- **Kết bài ({dani.get('kb', '')}):**\n"
            f"  *Mẫu khép lại:* \"Khép lại những suy ngẫm về **{vdnl}**, mỗi chúng ta hiểu rằng nhận thức đúng đắn chỉ thực sự có giá trị khi được chuyển hóa thành hành động kiên trì ngay từ hôm nay...\""
        )

    # --- NHÁNH F: HỌC SINH GỬI ĐOẠN VĂN NHỜ SỬA HOẶC HỎI CÂU BẤT KỲ ---
    if len(q_clean.split()) >= 12:
        snippet = q_clean[:160] + ("..." if len(q_clean) > 160 else "")
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Cô đã đọc kỹ đoạn viết của em: *'{snippet}'*.\n"
            f"- **Nhận xét chuyên môn:** Đoạn viết của em đã hướng vào chủ đề **{vdnl}** (*{type_label}*).\n"
            "- **Hướng dẫn nâng cấp câu chữ cụ thể:**\n"
            "  1. Em hãy bổ sung ngay cụm từ lập luận chỉ nguyên nhân (*Sở dĩ như vậy là bởi..., Thực tế đã chứng minh rằng...*) vào câu thứ 2 để tăng sức nặng lý lẽ.\n"
            "  2. Đừng quên gắn kèm 1 dẫn chứng người thật việc thật đã có sẵn ở cột bên trái vào cuối đoạn để đạt điểm tối đa tiêu chí Dẫn chứng nhé!"
        )

    return (
        f"👩‍🏫 **Trợ lý Ngữ văn:** Về câu hỏi **'{q_clean}'** của em cho đề bài **{vdnl}** (*{type_label}*):\n"
        "Cô đã thiết lập sẵn đầy đủ **Khái niệm giải thích tường minh, Hệ thống luận điểm/giải pháp 3 cấp độ và Dẫn chứng cụ thể** ở ngay khung bên trái.\n"
        "- Nếu em muốn lấy **đoạn văn mẫu giải thích khái niệm**, hãy nhắn: *\"Giải thích khái niệm\"*.\n"
        "- Nếu em muốn lấy **dẫn chứng mới kèm cách phân tích**, hãy nhắn: *\"Cho em dẫn chứng cụ thể\"*.\n"
        "- Nếu em muốn hướng dẫn chi tiết **Giải pháp Cá nhân - Gia đình - Nhà trường**, hãy nhắn: *\"Hướng dẫn phần giải pháp\"* nhé!"
    )


# ==============================================================================
# 6. THUẬT TOÁN CHẤM ĐIỂM RUBRIC 7 TIÊU CHÍ (ĐỌC KỸ, RÀ SOÁT LỖI, SÁT TỪNG DẠNG BÀI)
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
        "- Dạng bài và yêu cầu cấu trúc bắt buộc của đề này:",
        structure_guide,
        "",
        "- Bài làm thực tế của học sinh:",
        text,
        "",
        "Thực hiện đánh giá trực tiếp vào bảng điểm và lời phê theo các nguyên tắc chuyên môn sau (tuyệt đối không nhắc lại các nguyên tắc này trong kết quả trả về):",
        f"- Chấm nghiêm ngặt, công tâm dựa trên chất lượng thực tế và ĐÚNG DẠNG ĐỀ ({type_label}). Không chấm dễ dãi theo kiểu 'cứ có ý là cho điểm tối đa'. Nếu học sinh có nhắc đến ý nhưng phân tích hời hợt, lập luận lỏng lẻo, thiếu lí giải, hoặc làm sai cấu trúc của dạng bài thì PHẢI trừ điểm tương ứng và chỉ rõ.",
        "- Nếu bài viết ngắn dưới 450 chữ, tổng điểm không vượt quá 6.0 điểm; dưới 250 chữ, tổng điểm dưới 4.0 điểm.",
        "- Đọc kỹ từng câu để rà soát lỗi: Bắt buộc trích dẫn nguyên văn (trong dấu ngoặc kép) ít nhất 3-4 câu hoặc cụm từ thực tế từ bài làm của học sinh để chỉ rõ lỗi lập luận nông/lặp ý, lỗi diễn đạt, lỗi dùng từ, ngữ pháp hoặc chính tả.",
        "- Lập bảng Markdown đúng 4 cột: Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm (với 7 tiêu chí: 1. Bố cục 0.5đ; 2. Xác định Vấn đề nghị luận 0.5đ; 3. Giải thích / Khởi điểm vấn đề 1.0đ; 4. Hệ thống luận điểm theo đúng dạng bài 3.5đ; 5. Dẫn chứng thực tế 2.5đ; 6. Phản đề / Ý kiến trái chiều & Bài học 1.0đ; 7. Diễn đạt & Chính tả 1.0đ).",
        "- Sau bảng điểm, trình bày phần Rà soát lỗi cụ thể & Hướng dẫn chỉnh sửa nâng cấp từng câu/đoạn bị lỗi.",
    ]
    prompt_grade = "\n".join(prompt_lines)

    ai_eval = call_gemini_rest_api(prompt_grade, temperature=0.25)
    if ai_eval and "|" in ai_eval:
        return ai_eval

    # Bộ máy kiểm định nội bộ nghiêm ngặt theo sát từng dạng đề
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

    explain_markers = ["được hiểu là", "chính là", "nghĩa là", "khái niệm", "hàm ý", "thể hiện qua", "ẩn dụ", "nhận định", "câu nói", "thói quen", "quan điểm"]
    has_explain = sum(1 for m in explain_markers if m in text_low)

    argument_markers = ["trước hết", "thứ nhất", "thứ hai", "bên cạnh đó", "hơn thế nữa", "không chỉ vậy", "mặt khác", "bởi vì", "bởi lẽ", "do đó", "chính vì", "nhờ có", "giúp cho", "tạo nên", "thúc đẩy", "cá nhân", "gia đình", "nhà trường", "cộng đồng", "xã hội", "nguyên nhân", "hậu quả", "giải pháp"]
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
    if type_code in ["DANG_2_GIAI_QUYET", "DANG_5_TU_BO"]:
        for actor in ["cá nhân", "gia đình", "nhà trường"]:
            if actor not in text_low:
                type_specific_missing.append(f"thiếu giải pháp đối với **{actor}**")
        if not any(w in text_low for w in ["thực trạng", "nguyên nhân", "hậu quả", "tác hại"]):
            type_specific_missing.append("thiếu phân tích rõ Thực trạng - Nguyên nhân - Hậu quả")
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

    # 1. Bố cục (0.5đ)
    if num_paras >= 4 and word_count >= 500:
        s1 = 0.5
        c1_note = f"Bài viết chia thành **{num_paras} đoạn văn**, đảm bảo kết cấu 3 phần Mở - Thân - Kết và phân đoạn hợp lý theo dạng đề."
    elif num_paras >= 3 and word_count >= 250:
        s1 = 0.25
        c1_note = f"Có chia thành {num_paras} đoạn nhưng việc tách các đoạn luận điểm trong Thân bài chưa rõ hoặc dung lượng còn thiếu (**{word_count} chữ**)."
    else:
        s1 = 0.0
        c1_note = f"Bố cục chưa đạt yêu cầu: bài viết chỉ có **{num_paras} đoạn** (**{word_count} chữ**), thiếu sự phân tách Mở - Thân - Kết."

    # 2. Xác định VĐNL (0.5đ)
    if topic_coverage >= 0.6 and num_paras >= 3 and len(paragraphs[0].split()) >= 25:
        s2 = 0.5
        c2_note = f"Dẫn dắt và xác định trúng vấn đề nghị luận trọng tâm (*{vdnl_chuan}*). Minh chứng mở đầu: *'{first_sent[:110]}...'*."
    elif topic_coverage >= 0.25:
        s2 = 0.25
        c2_note = f"Có chạm tới từ khóa của đề nhưng giới thiệu vấn đề còn gượng gạo, chưa làm nổi bật trọng tâm (*'{first_sent[:95]}...'*)."
    else:
        s2 = 0.0
        c2_note = f"Chưa xác định đúng trọng tâm vấn đề nghị luận (*{vdnl_chuan}*)."

    # 3. Giải thích khái niệm (1.0đ)
    if has_explain >= 2 and word_count >= 500 and topic_coverage >= 0.5:
        s3 = 0.75
        c3_note = "Đã thực hiện thao tác giải thích khái niệm/vấn đề, tuy nhiên cách cắt nghĩa các tầng nghĩa cần cô đọng và sắc sảo hơn."
    elif has_explain >= 1 and word_count >= 250:
        s3 = 0.5
        c3_note = "Mới dừng lại ở việc giải thích bề mặt từ ngữ, chưa làm bật lên bản chất cốt lõi của vấn đề."
    else:
        s3 = 0.25 if (word_count >= 180 and topic_coverage > 0) else 0.0
        c3_note = "Thiếu đoạn giải thích tường minh khái niệm/nhận định ở đầu phần Thân bài."

    # 4. Hệ thống luận điểm (3.5đ)
    if word_count < 200:
        base_s4 = 0.5
    elif word_count < 380:
        base_s4 = 1.0 if arg_count >= 3 else 0.75
    elif word_count < 520:
        base_s4 = 1.75 if arg_count >= 5 else 1.5
    elif word_count < 600:
        base_s4 = 2.25 if arg_count >= 7 else 2.0
    else:
        base_s4 = 2.75 if (arg_count >= 9 and topic_coverage >= 0.6) else 2.25

    if type_specific_missing and base_s4 >= 1.5:
        base_s4 = max(1.0, base_s4 - 0.5)
        missing_str = ", ".join(type_specific_missing)
        c4_note = f"Dung lượng đạt **{word_count} chữ**, nhưng so với yêu cầu của **{type_label}**, bài làm còn {missing_str}. Minh chứng câu văn: *'{longest_sent[:100]}...'*."
    else:
        c4_note = f"Dung lượng đạt **{word_count} chữ**. Đã triển khai các ý bàn luận (*'{longest_sent[:105]}...'*), song chiều sâu lý lẽ và sự sắc bén trong phân tích vẫn cần nâng cao hơn để đạt điểm tối đa."
    s4 = base_s4

    # 5. Dẫn chứng thực tế (2.5đ)
    if len(unique_proper_nouns) >= 2 and ev_marker_count >= 2 and word_count >= 500:
        s5 = 1.75
        nouns_str = ", ".join(unique_proper_nouns[:3])
        c5_note = f"Có đưa dẫn chứng thực tế (**{nouns_str}**), nhưng cần phân tích sâu hơn sự kết nối giữa dẫn chứng với luận điểm/giải pháp thay vì chỉ thuật lại."
    elif len(unique_proper_nouns) >= 1 or ev_marker_count >= 1:
        s5 = 1.0 if word_count >= 350 else 0.75
        nouns_str = ", ".join(unique_proper_nouns[:2]) if unique_proper_nouns else "ví dụ chung"
        c5_note = f"Có nhắc tới dẫn chứng ({nouns_str}), nhưng chủ yếu mới dừng ở mức điểm tên, thiếu câu bình luận đắt giá."
    else:
        s5 = 0.25 if word_count >= 300 else 0.0
        c5_note = "Bài viết thiếu dẫn chứng thực tế xác thực; lập luận chỉ dựa vào lý lẽ suông nên sức thuyết phục thấp."

    # 6. Phản đề & Bài học (1.0đ)
    if counter_count >= 3 and word_count >= 500:
        s6 = 0.75
        c6_note = "Đã có đoạn phản đề / phản biện ý kiến trái chiều và rút ra bài học, nhưng góc nhìn phản biện cần sắc bén hơn."
    elif counter_count >= 1 and word_count >= 280:
        s6 = 0.5
        c6_note = "Có nhắc qua ý phê phán và liên hệ bản thân nhưng viết còn sơ lược, mang tính công thức."
    else:
        s6 = 0.25 if word_count >= 200 else 0.0
        c6_note = "Thiếu thao tác phản đề / phản biện ý kiến trái chiều; phần liên hệ bản thân còn chung chung."

    # 7. Diễn đạt & Chính tả (1.0đ)
    err_details = []
    if found_colloquial:
        col_str = ", ".join(found_colloquial[:3])
        err_details.append(f"dùng từ khẩu ngữ/sáo mòn (*{col_str}*)")
    if repeated_words:
        rep_str = ", ".join(repeated_words[:4])
        err_details.append(f"lặp từ nhiều lần (*{rep_str}*)")
    if len(sample_weak_sent.split()) < 7:
        err_details.append(f"câu văn cụt/sơ sài (*'{sample_weak_sent}'*)")
    elif len(sample_weak_sent.split()) > 65:
        err_details.append(f"câu văn quá dài, thiếu ngắt câu (*'{sample_weak_sent[:90]}...'*)")

    if err_details:
        s7 = 0.5 if word_count >= 350 else 0.25
        c7_note = "Cần khắc phục các lỗi diễn đạt: " + "; ".join(err_details) + "."
    elif word_count < 450:
        s7 = 0.5
        c7_note = f"Diễn đạt tương đối rõ ý nhưng thiếu các cấu trúc câu liên kết chuyển đoạn. Câu cần trau chuốt thêm: *'{shortest_sent}'*."
    else:
        s7 = 0.75
        c7_note = f"Diễn đạt khá mạch lạc, tuy nhiên một số câu văn vẫn cần gọt giũa từ ngữ cho giàu sức nặng lập luận hơn (ví dụ: *'{shortest_sent}'*)."

    total_score = round(s1 + s2 + s3 + s4 + s5 + s6 + s7, 2)

    if total_score < 4.0:
        rank = "Yếu / Chưa đạt"
    elif total_score < 5.5:
        rank = "Trung bình"
    elif total_score < 7.0:
        rank = "Trung bình - Khá"
    elif total_score < 8.0:
        rank = "Khá"
    else:
        rank = "Giỏi"

    if type_specific_missing:
        struct_advice = "Lưu ý khắc phục ngay về mặt cấu trúc: **" + ", ".join(type_specific_missing) + "**."
    else:
        struct_advice = "Cần chú ý đào sâu lý lẽ ở từng đoạn thân bài, tránh chỉ nêu nhận định bề mặt mà thiếu câu phân tích nguyên nhân - ý nghĩa."

    if repeated_words:
        vocab_advice = "Bài viết đang lặp lại nhiều lần các từ: **" + ", ".join(repeated_words[:4]) + "**. Hãy thay thế bằng từ đồng nghĩa."
    else:
        vocab_advice = "Cần tránh các từ ngữ khẩu ngữ hoặc sáo mòn, ưu tiên sử dụng từ vựng chính luận giàu sức biểu đạt."

    if s5 < 1.75:
        ev_advice = "Em mới chỉ điểm tên hoặc kể lại sự việc mà thiếu câu bình luận chốt ý gắn với luận điểm."
    else:
        ev_advice = "Cần trau chuốt thêm câu văn bình luận dẫn chứng cho thật sắc bén."

    if s6 < 0.75:
        pb_advice = "Cần bổ sung đoạn văn phản biện góc nhìn ngược lại theo đúng yêu cầu của dạng đề."
    else:
        pb_advice = "Phần liên hệ bản thân cần gắn với hành động thực chất hơn."

    report_lines = [
        "### 📊 BẢNG ĐÁNH GIÁ CHI TIẾT THEO 7 TIÊU CHÍ RUBRIC",
        f"*🧭 **Dạng bài áp dụng chấm:** {type_label}*  ",
        f"*📏 **Thông số kiểm định bài làm:** Độ dài **{word_count} chữ** | **{num_paras} đoạn văn** | **{num_sents} câu văn**.*",
        "",
        "| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |",
        "| :--- | :---: | :---: | :--- |",
        f"| **1. Bố cục (Mở - Thân - Kết)** | 0.50đ | **{s1:.2f}đ** | {c1_note} |",
        f"| **2. Xác định Vấn đề nghị luận** | 0.50đ | **{s2:.2f}đ** | {c2_note} |",
        f"| **3. Giải thích khái niệm** | 1.00đ | **{s3:.2f}đ** | {c3_note} |",
        f"| **4. Hệ thống luận điểm (Theo dạng đề)** | 3.50đ | **{s4:.2f}đ** | {c4_note} |",
        f"| **5. Dẫn chứng thực tế** | 2.50đ | **{s5:.2f}đ** | {c5_note} |",
        f"| **6. Phản đề & Bài học** | 1.00đ | **{s6:.2f}đ** | {c6_note} |",
        f"| **7. Diễn đạt & Chính tả** | 1.00đ | **{s7:.2f}đ** | {c7_note} |",
        "",
        "---",
        f"### 📌 TỔNG ĐIỂM ĐẠT ĐƯỢC: **{total_score:.2f} / 10.0 điểm** — Xếp loại: **{rank}**",
        "",
        "#### 🔍 RÀ SOÁT LỖI CỤ THỂ & ĐỊNH HƯỚNG CHỈNH SỬA NÂNG CẤP BÀI VIẾT:",
        f"1. **Rà soát cấu trúc theo đúng dạng bài ({type_label}):**",
        f"   * Bài làm đạt **{word_count} chữ**. {struct_advice}",
        f"   * **Câu mở đầu cần chú ý:** *'{first_sent[:120]}'* — Kiểm tra lại độ tự nhiên và tính chuẩn xác khi giới thiệu vấn đề **{vdnl_chuan}**.",
        "",
        "2. **Các lỗi diễn đạt, dùng từ và câu văn cần sửa ngay:**",
        f"   * **Câu văn còn non / vụng về trong bài:** *'{sample_weak_sent}'* -> **Hướng sửa:** Tránh viết câu cụt hoặc liệt kê khô khan; hãy bổ sung quan hệ từ lập luận (*bởi lẽ, chính vì vậy, nhờ đó...*) để câu văn chặt chẽ hơn.",
        f"   * **Về từ vựng:** {vocab_advice}",
        "",
        "3. **Về khai thác Dẫn chứng và Phản đề / Phản biện:**",
        f"   * **Dẫn chứng:** {ev_advice}",
        f"   * **Phản đề / Ý kiến trái chiều:** {pb_advice}",
    ]
    return "\n".join(report_lines)


# ==============================================================================
# 7. GIAO DIỆN CHÍNH & QUY TRÌNH 4 BƯỚC SƯ PHẠM
# ==============================================================================
with st.sidebar:
    st.title("⚙️ HỆ THỐNG QUẢN TRỊ")
    st.success("✅ Hệ thống Sư phạm 5 Dạng Bài & Chấm điểm Rubric hoạt động ổn định 100%!")

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
    <div class="hero-title">🖊️ EduAI - Hệ thống định hướng tư duy và phát triển năng lực viết văn nghị luận xã hội</div>
    <p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT theo định hướng phát triển năng lực</p>
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
        "🧭 Định hướng Dạng bài Nghị luận xã hội (Hệ thống tự động nhận diện theo lệnh đề hoặc Học sinh/GV chủ động chọn dạng bài cần luyện):",
        DANH_SACH_DANG_BAI,
        index=cur_override_idx,
        key="sb_type_override",
    )
    st.session_state["selected_essay_type_override"] = selected_override

    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs(
        [
            "🟢 Nhóm Đề Cơ Bản (Đề 01 – Đề 15)",
            "🔴 Nhóm Đề Nâng Cao (Đề 16 – Đề 30)",
            "✏️ Nhập / Dán Đề Bài Riêng (Đủ 5 Dạng Bài)",
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
                if selected_override != "Tự động nhận diện theo đề bài":
                    st.session_state["current_de_info"] = build_dynamic_outline_for_custom_topic(
                        de_info_cb["text"], de_info_cb.get("vdnl_chuan", ""), selected_override
                    )
                else:
                    auto_code = classify_essay_type(de_info_cb["text"], de_info_cb.get("vdnl_chuan", ""))
                    if auto_code != "DANG_1_TH3":
                        st.session_state["current_de_info"] = build_dynamic_outline_for_custom_topic(
                            de_info_cb["text"], de_info_cb.get("vdnl_chuan", ""), selected_override
                        )
                    else:
                        de_copy = dict(de_info_cb)
                        de_copy["essay_type_code"] = auto_code
                        de_copy["essay_type_label"] = get_essay_type_label(auto_code)
                        st.session_state["current_de_info"] = de_copy
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
                if selected_override != "Tự động nhận diện theo đề bài":
                    st.session_state["current_de_info"] = build_dynamic_outline_for_custom_topic(
                        de_info_nc["text"], de_info_nc.get("vdnl_chuan", ""), selected_override
                    )
                else:
                    auto_code = classify_essay_type(de_info_nc["text"], de_info_nc.get("vdnl_chuan", ""))
                    if auto_code != "DANG_1_TH3":
                        st.session_state["current_de_info"] = build_dynamic_outline_for_custom_topic(
                            de_info_nc["text"], de_info_nc.get("vdnl_chuan", ""), selected_override
                        )
                    else:
                        de_copy = dict(de_info_nc)
                        de_copy["essay_type_code"] = auto_code
                        de_copy["essay_type_label"] = get_essay_type_label(auto_code)
                        st.session_state["current_de_info"] = de_copy
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Mời chuyển sang Bước 2.")

    with tab_de_tu_nhap:
        st.markdown(
            "##### ✏️ Nhập đề bài riêng (Hệ thống tự động giải thích khái niệm, lập luận điểm & cung cấp dẫn chứng cụ thể sát từng dạng đề):"
        )
        custom_de_text = st.text_area(
            "Đề bài:",
            placeholder="Ví dụ: Hãy viết bài văn nghị luận bàn về giải pháp khắc phục tình trạng nghiện mạng xã hội... hoặc Thuyết phục người khác từ bỏ thói quen trì hoãn...",
            height=110,
            key="txt_custom_de",
        )
        student_custom_vdnl = st.text_input(
            "Theo em, vấn đề nghị luận trọng tâm của đề bài này là gì?",
            placeholder="Ví dụ: Giải pháp khắc phục tình trạng nghiện mạng xã hội...",
            key="txt_custom_vdnl",
        )
        if st.button(
            "🔍 Phân tích đề tự nhập & Thiết lập Khung định hướng chi tiết Bước 2",
            type="primary",
            key="btn_custom_analyze",
        ):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập Đề bài trước khi bấm phân tích!")
            else:
                with st.spinner("Đang giải thích khái niệm, thiết lập hệ thống luận điểm và trích xuất dẫn chứng cụ thể..."):
                    outline = build_dynamic_outline_for_custom_topic(
                        custom_de_text.strip(), student_custom_vdnl.strip(), selected_override
                    )
                    short_title = custom_de_text.strip()[:55] + (
                        "..." if len(custom_de_text.strip()) > 55 else ""
                    )
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                    st.session_state["current_de_info"] = outline
                    st.success(
                        f"✅ Đã nhận diện: **{outline.get('essay_type_label', '')}** và cung cấp đầy đủ khái niệm, luận điểm, dẫn chứng ở **Bước 2**!"
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
        f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Đề bài:* {ensure_600_words_prompt(cur_active_info.get('text', ''))}\n\n🎯 **Vấn đề nghị luận trọng tâm:** {cur_active_info.get('vdnl_chuan', '')}\n\n🧭 **Cấu trúc dạng bài áp dụng:** {active_type_label}"
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
            f"#### 🛠️ Khung định hướng tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='type-badge'>🧭 {cur_type_label}</div>", unsafe_allow_html=True)

        with st.expander("📌 Thao tác 1: Giải thích khái niệm & Khởi điểm vấn đề (Cụ thể, tường minh)", expanded=True):
            with st.container(border=True):
                for itm in cur_de_info.get("explain_items", []):
                    st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt lại VĐNL:** {cur_de_info.get('vdnl_ket_luan', '')}")

        with st.expander("💡 Thao tác 2: Hệ thống luận điểm & Giải pháp chi tiết (Kèm lý lẽ và dẫn chứng cụ thể)", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế & Kho dẫn chứng 9 chủ điểm", expanded=True):
            st.markdown("##### 📌 1. Dẫn chứng gợi ý trực tiếp cho đề bài này:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    card_html = (
                        f"<div class='evidence-card'>"
                        f"<h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>"
                        f"<p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p>"
                        f"<p style='margin:0 0 6px 0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p>"
                        f"</div>"
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

            st.markdown(
                """
                <div class="repo-guide-box">
                    💡 <b>MÁCH NHỎ CHO HỌC SINH:</b> Ngoài dẫn chứng gợi ý trên, hệ thống đã trang bị sẵn <b>Kho dẫn chứng 9 chủ điểm mở rộng</b> ngay bên dưới. Em hãy bấm vào khung chọn chủ điểm để tìm thêm những tấm gương người thật việc thật đắt giá nhất đưa vào bài viết của mình nhé!
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("##### 📚 2. Khai thác Kho dẫn chứng 9 chủ điểm (Mở rộng):")
            selected_topic = st.selectbox(
                "👉 Bấm vào đây để chọn chủ điểm dẫn chứng cần tham khảo:",
                list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()),
                key="sb_kho_dc",
            )
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"**👤 {dc['ten']}**")
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 Nguồn: {dc['nguon']}")

        with st.expander("🔄 Thao tác 4: Phản đề / Ý kiến trái chiều / Dự đoán phản đối & Bài học", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        with st.expander("📝 Bố cục Dàn ý chi tiết 3 phần", expanded=True):
            dani = cur_de_info.get("dani_chi_tiet", {})
            with st.container(border=True):
                st.markdown(f"**I. MỞ BÀI:** {dani.get('mb','')}")
                st.markdown(
                    f"**II. THÂN BÀI:**\n1. {dani.get('gt','')}\n2. {dani.get('bl','')}\n3. {dani.get('dc','')}\n4. {dani.get('pb','')}"
                )
                st.markdown(f"**III. KẾT BÀI:** {dani.get('kb','')}")

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn Tư Vấn (Chat Đa Lượt Linh Hoạt)")
        chat_container = st.container(height=420, border=True)
        with chat_container:
            for role, msg in st.session_state["chat_history"]:
                speaker = "🧑‍🎓 Học sinh" if role == "user" else "👩‍🏫 Trợ lý Ngữ văn"
                st.markdown(f"**{speaker}:**\n\n{msg}")
                st.markdown("---")

        user_question = st.text_area(
            "Nhập câu hỏi cụ thể (VD: Giải thích khái niệm, cho thêm dẫn chứng mới, hướng dẫn viết đoạn giải pháp, phản đề...):",
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
                        "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng ở khâu nào (Mở bài, Giải thích khái niệm, Luận điểm, Giải pháp, Dẫn chứng hay Phản đề)?",
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
            placeholder="Hãy tự viết bài văn hoàn chỉnh của em tại đây (Đảm bảo đủ 3 phần Mở bài, Thân bài tách các đoạn rõ ràng theo đúng dạng đề, Kết bài)...",
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
                    "💡 **Lưu ý:** Bài văn cần đạt dung lượng khoảng 600 chữ, bố cục 3 phần rõ ràng, giải thích trúng trọng tâm, thân bài triển khai đúng cấu trúc dạng đề, có dẫn chứng thực tế và phản biện sắc bén!"
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
                        f"Hãy đọc toàn bộ chữ viết tay trong bức ảnh này và đánh giá nghiêm khắc, thực chất theo BẢNG RUBRIC 7 TIÊU CHÍ (Thang điểm 10.0) cho đề bài: "
                        f"'{ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}'. "
                        "Trích dẫn nguyên văn các câu trong ảnh bài làm để chỉ rõ lỗi diễn đạt, lỗi lập luận, lỗi chính tả và hướng dẫn cách sửa chi tiết."
                    )
                    ai_img_res = call_gemini_rest_api(prompt_img, pil_image=img_obj, temperature=0.25)
                    if ai_img_res and "|" in ai_img_res:
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
            3. <b>Giải thích (1.0đ):</b> Cắt nghĩa tường minh khái niệm, nhận định hoặc ngữ liệu mở đầu.<br>
            4. <b>Hệ thống luận điểm (3.5đ):</b> Triển khai đầy đủ, sâu sắc các bước lập luận theo đúng dạng đề.<br>
            5. <b>Dẫn chứng (2.5đ):</b> Người thật việc thật xác thực, phân tích gắn kết hữu cơ với luận điểm/giải pháp.<br>
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
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info("💡 Chưa có kết quả đánh giá. Hãy nộp bài ở Bước 3 để hệ thống chấm và rà soát lỗi.")
