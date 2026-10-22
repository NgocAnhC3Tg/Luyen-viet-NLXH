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
    page_title="HỆ THỐNG LUYỆN VIẾT NLXH",
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
        font-size: 1.8rem !important;
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
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. HÀM CHUẨN HÓA LỆNH ĐỀ BÀI (ĐẢM BẢO YÊU CẦU BÀI VĂN KHOẢNG 600 CHỮ)
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
if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp lập ý, cung cấp dẫn chứng thực tế và gợi ý cách hành văn, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state: st.session_state["eval_vdnl_text"] = ""

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
# 4. ĐỘNG CƠ KẾT NỐI AI TRỰC TIẾP QUA REST API
# ==============================================================================
def call_gemini_rest_api(prompt, pil_image=None):
    key = get_api_key()
    if not key or not key.startswith("AIza"):
        return None
    
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest"
    ]
    
    parts = [{"text": prompt}]
    if pil_image is not None:
        try:
            buffered = io.BytesIO()
            img_rgb = pil_image.convert("RGB")
            img_rgb.save(buffered, format="JPEG", quality=85)
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_b64
                }
            })
        except Exception:
            pass

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 3000}
    }
    data = json.dumps(payload).encode("utf-8")

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if content_parts and "text" in content_parts[0]:
                        return content_parts[0]["text"]
        except Exception:
            continue
    return None

# ==============================================================================
# 5. BỘ MÁY NLP SƯ PHẠM NỘI BỘ: GIẢI THÍCH TINH GỌN, ĐÚNG DẠNG ĐỀ
# ==============================================================================
CONCEPT_DICTIONARY = {
    "sáng tạo": {
        "term": "Tinh thần sáng tạo",
        "def": "**Tinh thần sáng tạo** là khả năng tư duy độc lập, dám bứt phá khỏi những khuôn mẫu, lối mòn sẵn có để tìm tòi, khám phá ra những ý tưởng mới, cách làm mới mang lại giá trị và hiệu quả cao hơn.",
        "why": "Thế giới hiện đại biến đổi từng giây cùng kỷ nguyên số; nếu chỉ sao chép và đi theo lối mòn, con người sẽ bị tụt hậu. Sáng tạo chính là động lực cốt lõi giúp cá nhân khẳng định bản sắc và thúc đẩy xã hội tiến bộ.",
        "manifest": "Chủ động đặt câu hỏi phản biện trong học tập, tìm kiếm phương pháp giải quyết vấn đề mới mẻ, dám thử nghiệm công nghệ và ý tưởng đột phá trong lao động, nghiên cứu.",
        "counter": "Lối sống thụ động, học vẹt máy móc, rập khuôn sáo rỗng, ngại thay đổi; hoặc nhầm lẫn sáng tạo với sự lập dị, tùy tiện, bất chấp các quy chuẩn đạo đức và khoa học.",
        "ev_ten": "Kỹ sư trẻ Nguyễn Tử Quảng và các nhóm nghiên cứu công nghệ lõi Việt Nam",
        "ev_chitiet": "Dám dấn thân nghiên cứu các lĩnh vực công nghệ cao từ an ninh mạng đến trí tuệ nhân tạo ngay từ khi điều kiện trong nước còn thiếu thốn, góp phần khẳng định trí tuệ Việt trên bản đồ công nghệ.",
        "ev_ynghia": "Minh chứng rõ nét cho sức mạnh của tinh thần dám nghĩ dám làm và khát vọng sáng tạo không ngừng."
    },
    "đoàn kết": {
        "term": "Tinh thần đoàn kết",
        "def": "**Tinh thần đoàn kết** là sự gắn kết, đồng lòng, tập hợp sức mạnh của nhiều cá nhân thành một khối thống nhất để cùng hướng tới mục tiêu chung.",
        "why": "Một cá nhân dù xuất sắc đến đâu cũng có giới hạn; khi biết hợp lực, sức mạnh trí tuệ và tinh thần sẽ được nhân lên gấp bội để vượt qua nghịch cảnh.",
        "manifest": "Sự tương thân tương ái khi đồng bào gặp thiên tai bão lũ; tinh thần phối hợp ăn ý trong học tập, làm việc nhóm; sự đồng lòng của cả dân tộc trước những thử thách lịch sử.",
        "counter": "Lối sống ích kỷ, cục bộ, chia rẽ tập thể; hoặc biến 'đoàn kết' thành sự bao che, dĩ hòa vi quý làm triệt tiêu sự đấu tranh phản biện tích cực.",
        "ev_ten": "Chiến dịch chung tay hỗ trợ đồng bào miền Bắc trong siêu bão Yagi & Dự án 'Nuôi Em'",
        "ev_chitiet": "Hàng triệu người dân Việt Nam từ khắp mọi miền đã chung tay quyên góp, những đoàn xe cứu trợ xuyên đêm và hàng nghìn chiến sĩ, thanh niên tình nguyện dầm mình trong lũ dữ để cứu giúp đồng bào.",
        "ev_ynghia": "Minh chứng sống động cho sức mạnh đại đoàn kết: khi những trái tim cùng chung một nhịp đập, không thử thách nào có thể khuất phục."
    },
    "biết ơn": {
        "term": "Lòng biết ơn",
        "def": "**Lòng biết ơn** là thái độ trân trọng, khắc ghi công lao, sự giúp đỡ của người khác hoặc những giá trị tốt đẹp mà gia đình, thế hệ đi trước và cuộc đời đã dành cho mình.",
        "why": "Không thành quả nào tự nhiên mà có; lòng biết ơn giúp con người sống có cội nguồn, nuôi dưỡng tâm hồn nhân hậu và tạo ra sợi dây gắn kết bền chặt giữa người với người.",
        "manifest": "Hiếu thảo với cha mẹ, kính trọng thầy cô; tri ân các anh hùng liệt sĩ; trân trọng thành quả lao động, bảo vệ thiên nhiên và nỗ lực sống có ích để đáp đền tiếp nối.",
        "counter": "Thái độ vô ơn, bạc bẽo, 'qua cầu rút ván', coi sự hy sinh của người khác là điều hiển nhiên, hoặc chỉ thể hiện lòng biết ơn bằng lời nói hình thức.",
        "ev_ten": "Đôi bạn Nguyễn Tất Minh và Ngô Minh Hiếu (10 năm cõng bạn đến trường)",
        "ev_chitiet": "Nguyễn Tất Minh luôn khắc ghi sự hy sinh của gia đình và người bạn tri kỷ Ngô Minh Hiếu, nỗ lực vượt qua khuyết tật bẩm sinh để tốt nghiệp đại học loại Giỏi và tự lập giúp đỡ lại cộng đồng.",
        "ev_ynghia": "Biểu tượng đẹp đẽ của lòng biết ơn được chuyển hóa thành hành động vươn lên mạnh mẽ."
    },
    "bản lĩnh": {
        "term": "Bản lĩnh sống",
        "def": "**Bản lĩnh** là sức mạnh ý chí, sự kiên định, vững vàng của con người trước những khó khăn, nghịch cảnh, áp lực hoặc cám dỗ mà không hề nao núng hay đánh mất giá trị bản thân.",
        "why": "Cuộc sống luôn ẩn chứa những biến cố bất ngờ; bản lĩnh chính là chiếc mỏ neo giữ cho con người không gục ngã, biến nghịch cảnh thành bàn đạp để trưởng thành.",
        "manifest": "Dám đối diện với thất bại để đứng lên làm lại; dám bảo vệ lẽ phải trước đám đông; giữ vững đạo đức trước những cám dỗ vật chất.",
        "counter": "Sự yếu đuối, dễ dàng buông xuôi khi gặp khó khăn, sống ba phải theo hiệu ứng đám đông; hoặc nhầm lẫn bản lĩnh với sự bảo thủ, liều lĩnh bất chấp.",
        "ev_ten": "Kình ngư Nguyễn Thị Ánh Viên và hành trình vượt ngưỡng bản thân",
        "ev_chitiet": "Trải qua hàng vạn giờ tập luyện khắc nghiệt, vượt qua chấn thương và áp lực tâm lý nặng nề để mang về hàng loạt kỷ lục lịch sử cho thể thao Việt Nam, rồi tiếp tục truyền cảm hứng dạy bơi chống đuối nước cho trẻ em.",
        "ev_ynghia": "Bản lĩnh được tôi luyện qua sự kiên cường bền bỉ trước mọi áp lực."
    },
    "trách nhiệm": {
        "term": "Tinh thần trách nhiệm",
        "def": "**Tinh thần trách nhiệm** là ý thức thực hiện trọn vẹn bổn phận, nghĩa vụ của bản thân đối với chính mình, gia đình và xã hội, đồng thời dám làm dám chịu trước mọi hành động của mình.",
        "why": "Mỗi cá nhân là một mắt xích trong cộng đồng; sống có trách nhiệm tạo nên sự tin cậy, thúc đẩy xã hội vận hành văn minh và khẳng định phẩm giá của người trưởng thành.",
        "manifest": "Hoàn thành tốt việc học tập, lao động; không đổ lỗi cho hoàn cảnh; chủ động tham gia giải quyết các vấn đề chung như bảo vệ môi trường, thượng tôn pháp luật.",
        "counter": "Lối sống thờ ơ, vô cảm ('cha chung không ai khóc'), đùn đẩy lỗi lầm cho người khác, chỉ biết đòi hỏi quyền lợi mà trốn tránh nghĩa vụ.",
        "ev_ten": "Biệt đội Sài Gòn Xanh và các nhóm bạn trẻ giải cứu dòng kênh ô nhiễm",
        "ev_chitiet": "Những người trẻ tuổi tự nguyện lội xuống những dòng kênh đen đặc rác thải để dọn sạch hàng trăm tấn rác, trả lại dòng nước trong xanh và lan tỏa ý thức bảo vệ môi trường.",
        "ev_ynghia": "Hành động xuất phát từ ý thức trách nhiệm công dân tự giác vì cộng đồng."
    },
    "thất bại": {
        "term": "Cách đối diện với thất bại",
        "def": "**Thất bại** là những lần vấp ngã, chưa đạt được mục tiêu đề ra trên đường đời, nhưng đồng thời là phép thử bản lĩnh và bài học kinh nghiệm quý giá giúp con người hoàn thiện mình.",
        "why": "Không ai thành công mà chưa từng vấp ngã; thất bại giúp con người nhận diện rõ thiếu sót, rèn luyện nghị lực và tích lũy trí tuệ thực tiễn.",
        "manifest": "Bình tĩnh nhìn nhận nguyên nhân sau mỗi lần vấp ngã; kiên trì điều chỉnh phương pháp để thử sức lại thay vì tự ti, mặc cảm.",
        "counter": "Tâm lý sợ sai nên không dám dấn thân thử thách; hoặc thái độ bi quan, tuyệt vọng, buông xuôi sau một lần vấp ngã đầu đời.",
        "ev_ten": "Nhà bác học Thomas Edison và hàng nghìn lần thử nghiệm dây tóc bóng đèn",
        "ev_chitiet": "Trước khi phát minh ra bóng đèn điện làm thay đổi nhân loại, ông đã trải qua hàng ngàn cuộc thí nghiệm thất bại nhưng luôn coi đó là bước đệm cần thiết để tìm ra chân lý.",
        "ev_ynghia": "Thất bại chỉ thực sự là dấu chấm hết khi con người ngừng cố gắng."
    },
    "ước mơ": {
        "term": "Ước mơ và khát vọng",
        "def": "**Ước mơ / Khát vọng** là những mục tiêu, lý tưởng tốt đẹp mà con người khao khát hướng tới và nỗ lực phấn đấu để hiện thực hóa trong tương lai.",
        "why": "Ước mơ giống như ngọn hải đăng soi đường, giúp tuổi trẻ sống có mục đích, đánh thức tiềm năng và tạo động lực vượt qua mọi rào cản.",
        "manifest": "Xây dựng mục tiêu học tập rõ ràng, bền bỉ trau dồi tri thức và kỹ năng mỗi ngày, gắn ước mơ cá nhân với sự phát triển của cộng đồng.",
        "counter": "Lối sống hoài phí tuổi trẻ, không mục tiêu, buông thả; hoặc những ảo tưởng viển vông, chỉ mơ mộng suông mà không bắt tay vào hành động.",
        "ev_ten": "Cô gái dân tộc Mông Lầu Minh Vư chinh phục học bổng đại học quốc tế",
        "ev_chitiet": "Sinh ra ở vùng cao nghèo khó nơi nhiều bạn bè nghỉ học sớm, Vư đã nuôi dưỡng khát vọng bước ra thế giới bằng con đường tri thức, tự học ngoại ngữ và giành học bổng toàn phần.",
        "ev_ynghia": "Khát vọng lớn chính là đôi cánh đưa con người vượt thoát khỏi mọi giới hạn xuất phát điểm."
    },
    "thấu cảm": {
        "term": "Sự thấu cảm và sẻ chia",
        "def": "**Sự thấu cảm** là khả năng đặt mình vào vị trí của người khác để thấu hiểu, sẻ chia những nỗi niềm, khó khăn của họ và hành động bằng một trái tim nhân ái.",
        "why": "Trong xã hội hiện đại nhiều áp lực, sự thấu cảm là chất keo hàn gắn những tổn thương, xóa bỏ sự cô đơn và làm cho cuộc sống trở nên ấm áp, nhân văn hơn.",
        "manifest": "Biết lắng nghe không phán xét; sẵn sàng nâng đỡ những mảnh đời yếu thế; tôn trọng sự khác biệt của người xung quanh.",
        "counter": "Căn bệnh vô cảm, dửng dưng trước nỗi đau đồng loại; thói phán xét độc hại trên mạng xã hội hoặc lòng tốt giả tạo nhằm đánh bóng tên tuổi.",
        "ev_ten": "Chàng trai trẻ Lê Văn Phúc và dự án thiện nguyện 'Fly To Sky'",
        "ev_chitiet": "Từ khi còn là học sinh phổ thông, Phúc đã khởi xướng hàng chục dự án hỗ trợ sách vở, thư viện và nước sạch cho hàng vạn trẻ em vùng cao biên giới.",
        "ev_ynghia": "Khi sự thấu cảm đi liền với hành động tử tế, tuổi trẻ có thể tạo ra những thay đổi kỳ diệu."
    }
}

def extract_clean_topic_noun(text):
    clean = re.sub(r'(?i)(hãy viết một bài văn nghị luận xã hội|hãy viết bài văn nghị luận|khoảng 600 chữ|trình bày suy nghĩ của anh/chị về|suy nghĩ của anh/chị về|suy nghĩ về|bàn về|ý nghĩa của|vai trò của|tầm quan trọng của)', '', text)
    clean = re.sub(r'[():.,?!"]', '', clean).strip()
    return clean if clean else text.strip()

def is_metaphorical_quote_topic(topic_text):
    # Kiểm tra xem đề bài là câu nói ẩn dụ/danh ngôn hay là đề nêu trực tiếp vấn đề
    if '"' in topic_text or '“' in topic_text or '”' in topic_text:
        return True
    if any(w in topic_text.lower() for w in ["có ý kiến cho rằng", "ngạn ngữ", "danh ngôn", "nhà văn", "từng nói"]):
        return True
    return False

def build_dynamic_outline_for_custom_topic(raw_topic_text, student_vdnl):
    formatted_topic = ensure_600_words_prompt(raw_topic_text)
    direct_problem = student_vdnl.strip() if student_vdnl.strip() else extract_clean_topic_noun(raw_topic_text)
    is_quote = is_metaphorical_quote_topic(raw_topic_text)

    # 1. Thử gọi Gemini REST API nếu có khóa hợp lệ
    explain_instruction = (
        "Vì đây là đề bài nêu trực tiếp vấn đề nghị luận, ở phần Giải thích CHỈ CẦN 1 Ý DUY NHẤT định nghĩa ngắn gọn, trực diện khái niệm cốt lõi là gì (tuyệt đối không chẻ thành 2-3 lớp nghĩa cồng kềnh)."
        if not is_quote else
        "Vì đây là đề bài dạng câu nói/ý kiến có hình ảnh ẩn dụ, hãy giải thích ngắn gọn từ khóa/hình ảnh ẩn dụ rồi rút ra ý nghĩa cả câu."
    )
    prompt = f"""Đóng vai chuyên gia sư phạm Ngữ văn THPT. Hãy lập Khung định hướng tư duy cho đề bài NLXH (khoảng 600 chữ) sau và trả về MỘT CHUỖI JSON HỢP LỆ (không dùng markdown code block):
Đề bài: "{formatted_topic}"
Vấn đề nghị luận: "{direct_problem}"

YÊU CẦU SƯ PHẠM QUAN TRỌNG:
- {explain_instruction}
- Hệ thống 5 luận điểm bàn luận rõ ràng, sâu sắc, đúng trọng tâm.
- Dẫn chứng người thật việc thật cụ thể.

Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{formatted_topic}",
  "vdnl_chuan": "{direct_problem}",
  "explain_items": [
    "- **Giải thích khái niệm:** (Viết ngắn gọn, trực diện, đúng trọng tâm tại đây)..."
  ],
  "vdnl_ket_luan": "Câu chốt ngắn gọn dẫn vào phần bàn luận",
  "questions": [
    {{
      "cau_hoi": "Hệ thống 5 luận điểm bàn luận trọng tâm:",
      "y_tra_loi": [
        "- **1. Biểu hiện thực tế:** ...",
        "- **2. Ý nghĩa đối với cá nhân:** ...",
        "- **3. Ý nghĩa đối với cộng đồng, xã hội:** ...",
        "- **4. Lý giải nguyên nhân / Hệ lụy nếu thiếu vắng:** ...",
        "- **5. Bài học nhận thức và hành động của tuổi trẻ:** ..."
      ]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên nhân vật/sự kiện thực tế cụ thể",
      "chi_tiet": "Tóm tắt hành động tiêu biểu",
      "y_nghia": "Ý nghĩa chứng minh cho luận điểm",
      "nguon": "Thực tiễn đời sống"
    }}
  ],
  "counter": [
    "- **Phê phán biểu hiện lệch lạc:** ...",
    "- **Góc nhìn phản biện / Mở rộng:** ..."
  ],
  "dani_chi_tiet": {{
    "mb": "Dẫn dắt và nêu trực diện vấn đề nghị luận.",
    "gt": "Giải thích ngắn gọn, súc tích khái niệm trọng tâm.",
    "bl": "Triển khai 5 luận điểm bàn luận.",
    "dc": "Đưa dẫn chứng thực tế và phân tích.",
    "pb": "Phê phán biểu hiện ngược lại và mở rộng vấn đề.",
    "kb": "Khẳng định lại giá trị của vấn đề và liên hệ bản thân."
  }}
}}"""
    ai_res = call_gemini_rest_api(prompt)
    if ai_res:
        try:
            match = re.search(r'\{.*\}', ai_res, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed["text"] = formatted_topic
                if "explain_items" in parsed and "questions" in parsed:
                    return parsed
        except Exception:
            pass

    # 2. Xử lý bằng Bộ máy NLP Sư phạm Nội bộ (Tinh gọn Giải thích theo đúng dạng đề)
    combined_low = (raw_topic_text + " " + student_vdnl).lower()
    matched_concept = None
    for kw, data in CONCEPT_DICTIONARY.items():
        if kw in combined_low:
            matched_concept = (kw, data)
            break

    if matched_concept:
        kw_name, c_data = matched_concept
        vdnl_final = student_vdnl.strip() if student_vdnl.strip() else direct_problem
        # Chỉ giải thích 1 ý trực diện nếu đề nêu trực tiếp vấn đề
        if not is_quote:
            explain_list = [f"- **Giải thích khái niệm:** {c_data['def']}"]
        else:
            explain_list = [
                f"- **Giải thích khái niệm trọng tâm:** {c_data['def']}",
                f"- **Ý nghĩa câu nói:** Nhấn mạnh vai trò và giá trị to lớn của **{kw_name}** đối với sự trưởng thành của mỗi cá nhân và sự phát triển của xã hội."
            ]

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "explain_items": explain_list,
            "vdnl_ket_luan": f"Qua đó, đề bài đặt ra vấn đề cần bàn luận sâu sắc là: **{vdnl_final}**.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống 5 luận điểm bàn luận trọng tâm về: {vdnl_final}",
                    "y_tra_loi": [
                        f"- **Luận điểm 1 (Biểu hiện trong đời sống):** {c_data['manifest']}",
                        f"- **Luận điểm 2 (Vì sao cần có {kw_name}?):** {c_data['why']}",
                        f"- **Luận điểm 3 (Giá trị đối với sự phát triển cá nhân):** Giúp mỗi người phát huy tối đa nội lực, vượt qua giới hạn của bản thân và tạo dựng những thành quả có giá trị thực chất.",
                        f"- **Luận điểm 4 (Ý nghĩa đối với cộng đồng, xã hội):** Tạo ra sức mạnh cộng hưởng, lan tỏa tinh thần tích cực và thúc đẩy xã hội phát triển văn minh, hiện đại.",
                        f"- **Luận điểm 5 (Hệ lụy nếu thiếu vắng {kw_name}):** Con người dễ rơi vào sự trì trệ, bế tắc, tụt hậu và đánh mất cơ hội khẳng định mình."
                    ]
                }
            ],
            "evidence": [
                {
                    "ten": c_data["ev_ten"],
                    "chi_tiet": c_data["ev_chitiet"],
                    "y_nghia": c_data["ev_ynghia"],
                    "nguon": "Thực tiễn đời sống xã hội & Báo chí chính thống"
                }
            ],
            "counter": [
                f"- **Phê phán biểu hiện lệch lạc:** {c_data['counter']}",
                f"- **Mở rộng & Bài học nhận thức:** Phát huy **{kw_name}** cần đi đôi với nền tảng đạo đức, tri thức vững vàng và sự kiên trì rèn luyện mỗi ngày."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt ngắn gọn và nêu trực diện vấn đề nghị luận: {vdnl_final}.",
                "gt": f"Giải thích ngắn gọn khái niệm '{c_data['term']}' là gì.",
                "bl": f"Phân tích 5 luận điểm: Biểu hiện -> Lý do cốt lõi -> Sức mạnh với cá nhân -> Ý nghĩa với xã hội -> Hệ lụy nếu thiếu vắng '{kw_name}'.",
                "dc": f"Đưa dẫn chứng thực tế ({c_data['ev_ten']}) và phân tích gắn với luận điểm.",
                "pb": f"Phê phán lối sống ngược lại và rút ra cái nhìn toàn diện.",
                "kb": f"Khẳng định lại tầm quan trọng của {vdnl_final} và liên hệ hành động của bản thân."
            }
        }
    else:
        # Đề tự nhập bất kỳ khác: Giải thích trực diện, ngắn gọn 1 lớp nếu là đề trực tiếp
        vdnl_final = student_vdnl.strip() if student_vdnl.strip() else direct_problem
        if not is_quote:
            explain_list = [
                f"- **Giải thích khái niệm:** **{vdnl_final}** được hiểu là phẩm chất, thái độ sống hoặc năng lực nhận thức và hành động tích cực của con người nhằm hướng tới những giá trị tốt đẹp, tiến bộ trong đời sống cá nhân và cộng đồng."
            ]
        else:
            explain_list = [
                f"- **Giải thích từ ngữ/hình ảnh trong câu nói:** Làm rõ nghĩa đen và nghĩa bóng của các từ khóa trọng tâm trong nhận định.",
                f"- **Ý nghĩa cả câu:** Khẳng định tầm quan trọng của **{vdnl_final}** đối với nhân cách và sự trưởng thành của con người."
            ]

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "explain_items": explain_list,
            "vdnl_ket_luan": f"Trọng tâm bài viết cần tập trung làm sáng tỏ giá trị và ý nghĩa của **{vdnl_final}**.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống 5 luận điểm bàn luận trọng tâm về: {vdnl_final}",
                    "y_tra_loi": [
                        f"- **Luận điểm 1 (Biểu hiện cụ thể):** **{vdnl_final}** được thể hiện trực tiếp qua nhận thức, thái độ ứng xử và hành động nỗ lực mỗi ngày của con người trước công việc và cuộc sống.",
                        f"- **Luận điểm 2 (Tác động đối với cá nhân):** Giúp con người hoàn thiện nhân cách, phát huy tiềm năng nội tại và vững vàng vượt qua những thử thách.",
                        f"- **Luận điểm 3 (Ý nghĩa đối với xã hội):** Góp phần lan tỏa những giá trị tốt đẹp, thúc đẩy cộng đồng phát triển văn minh và bền vững.",
                        f"- **Luận điểm 4 (Hệ lụy nếu thiếu vắng):** Nếu thờ ơ hoặc đi ngược lại giá trị này, cá nhân dễ rơi vào sự trì trệ, mất phương hướng và giảm sút giá trị bản thân.",
                        f"- **Luận điểm 5 (Phương hướng rèn luyện của người trẻ):** Chủ động trau dồi nhận thức và biến thành hành động thiết thực ngay từ khi còn ngồi trên ghế nhà trường."
                    ]
                }
            ],
            "evidence": [
                {
                    "ten": "Tấm gương thầy giáo Nguyễn Ngọc Ký và những người trẻ Việt Nam giàu nghị lực, cống hiến",
                    "chi_tiet": "Không khuất phục trước hoàn cảnh hay giới hạn bản thân, họ luôn kiên trì rèn luyện, dấn thân sáng tạo và đóng góp những giá trị thiết thực cho xã hội.",
                    "y_nghia": f"Minh chứng thuyết phục cho sức mạnh và giá trị của {vdnl_final} trong thực tiễn.",
                    "nguon": "Thực tiễn đời sống xã hội"
                }
            ],
            "counter": [
                f"- **Phê phán biểu hiện tiêu cực:** Lên án lối sống thụ động, hời hợt, thiếu ý thức rèn luyện hoặc chỉ nói lý thuyết suông về **{vdnl_final}**.",
                "- **Mở rộng vấn đề:** Cần thực hành một cách tỉnh táo, phù hợp với hoàn cảnh thực tế và chuẩn mực đạo đức xã hội."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt và giới thiệu trực tiếp vấn đề nghị luận: {vdnl_final}.",
                "gt": f"Giải thích ngắn gọn, trực diện khái niệm {vdnl_final} là gì.",
                "bl": f"Triển khai 5 luận điểm: Biểu hiện -> Tác động cá nhân -> Ý nghĩa xã hội -> Hệ lụy -> Bài học hành động.",
                "dc": "Chọn lọc dẫn chứng thực tế tiêu biểu và phân tích ngắn gọn.",
                "pb": "Phê phán biểu hiện lệch lạc và mở rộng góc nhìn.",
                "kb": f"Khẳng định lại giá trị của {vdnl_final} và liên hệ bản thân."
            }
        }

def generate_deep_chat_response(user_q, cur_de_info):
    q_clean = user_q.strip()
    q_low = q_clean.lower()
    topic_text = ensure_600_words_prompt(cur_de_info.get("text", ""))
    vdnl = cur_de_info.get("vdnl_chuan", "vấn đề nghị luận của đề bài")
    
    if any(w in q_low for w in ["viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho em bài văn", "viết cả bài", "viết đoạn văn hoàn chỉnh"]):
        return f"👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết hộ bài văn hay đoạn văn hoàn chỉnh cho em nhé! Với yêu cầu viết bài văn khoảng 600 chữ về **{vdnl}**, em hãy tự nháp ý của mình trước, cô sẽ hướng dẫn cách triển khai câu chữ!"

    prompt_chat = f"""Đóng vai giáo viên Ngữ văn THPT giỏi chuyên môn. Học sinh đang thực hiện Bước 2 (Tìm ý & Lập dàn ý) cho bài văn Nghị luận xã hội (khoảng 600 chữ):
- Đề bài: "{topic_text}"
- Vấn đề nghị luận: "{vdnl}"
- Câu hỏi của học sinh: "{q_clean}"

YÊU CẦU:
1. Không viết hộ bài văn hoàn chỉnh.
2. Nếu học sinh hỏi về giải thích: hướng dẫn giải thích ngắn gọn, trực diện đúng khái niệm trọng tâm, không rườm rà nhiều lớp nếu đề bài đã nêu trực tiếp vấn đề.
3. Trả lời cụ thể, sát với vấn đề "{vdnl}"."""
    
    ai_reply = call_gemini_rest_api(prompt_chat)
    if ai_reply:
        return ai_reply

    explain_list = cur_de_info.get("explain_items", [])
    questions_list = cur_de_info.get("questions", [])
    evidence_list = cur_de_info.get("evidence", [])
    counter_list = cur_de_info.get("counter", [])

    if "mở bài" in q_low:
        return f"""👩‍🏫 **Hướng dẫn viết Mở bài cho bài văn (khoảng 600 chữ) về \"{vdnl}\":**
- **Câu 1 (Dẫn dắt):** Đi từ thực tiễn cuộc sống hoặc một hình ảnh tương đồng gắn với tuổi trẻ hôm nay.
- **Câu 2 (Nêu trực diện vấn đề):** Dẫn vào trọng tâm đề bài cần bàn luận là **{vdnl}**.
- **Câu 3 (Định hướng):** Khẳng định đây là yếu tố quan trọng góp phần làm nên giá trị bản thân và sự tiến bộ của xã hội."""

    if "giải thích" in q_low or "từ khóa" in q_low or "khái niệm" in q_low:
        gt_content = explain_list[0] if explain_list else f"- Làm rõ khái niệm **{vdnl}** là gì."
        return f"""👩‍🏫 **Hướng dẫn viết đoạn Giải thích ngắn gọn, súc tích (Tránh dài dòng, máy móc):**
- Với đề bài nêu trực tiếp vấn đề như thế này, em **không cần** chia thành nhiều lớp rườm rà mà chỉ cần giải thích trực diện trong **2 - 3 câu văn**:
{gt_content}
- Sau đó dùng 1 câu chuyển ý để bước ngay vào phần trọng tâm nhất của bài là **Bàn luận (3.5đ)**."""

    if "dẫn chứng" in q_low or "ví dụ" in q_low or "nhân vật" in q_low:
        ev_str = ""
        for idx, ev in enumerate(evidence_list[:2], 1):
            if isinstance(ev, dict):
                ev_str += f"\n- **{ev.get('ten', '')}:** {ev.get('chi_tiet', '')}"
        return f"""👩‍🏫 **Gợi ý Dẫn chứng và cách khai thác Kho dẫn chứng:**
1. **Dẫn chứng sát hợp ngay cho đề:**{ev_str}
2. **Mẹo tìm thêm dẫn chứng:** Em hãy nhìn sang cột bên trái, mở mục **📚 Thao tác 3: Dẫn chứng thực tế**, ở ngay phía dưới có **Kho dẫn chứng 9 chủ điểm (Mở rộng)** với hàng chục nhân vật thực tế có nguồn báo chí rõ ràng để em lựa chọn!"""

    if "phản đề" in q_low or "phản biện" in q_low or "mở rộng" in q_low:
        pb_content = "\n".join(counter_list) if counter_list else f"- Phê phán biểu hiện thiếu **{vdnl}** và nhìn nhận vấn đề toàn diện."
        return f"""👩‍🏫 **Hướng dẫn viết đoạn Phản đề & Mở rộng (1.0đ):**
Em triển khai gọn trong 1 đoạn văn khoảng 4-5 câu:
{pb_content}"""

    if "liên hệ" in q_low or "kết bài" in q_low or "bài học" in q_low:
        return f"""👩‍🏫 **Hướng dẫn viết Bài học liên hệ & Kết bài:**
- Khẳng định lại giá trị của **{vdnl}** đối với mỗi người.
- Liên hệ thực chất tới những việc làm cụ thể của bản thân trong học tập và rèn luyện hàng ngày."""

    bl_items = []
    for q in questions_list:
        for ans in q.get("y_tra_loi", []):
            bl_items.append(ans)
    bl_text = "\n".join(bl_items[:5]) if bl_items else f"- Phân tích biểu hiện, nguyên nhân và ý nghĩa của **{vdnl}**."
    
    return f"""👩‍🏫 **Định hướng triển khai hệ thống luận điểm Thân bài cho \"{vdnl}\":**
Để bài văn đạt dung lượng khoảng **600 chữ** và có chiều sâu, phần Bàn luận em nên triển khai theo các ý sau:
{bl_text}"""


# ==============================================================================
# 6. THUẬT TOÁN CHẤM ĐIỂM RUBRIC 7 TIÊU CHÍ (CHUẨN BÀI VĂN KHOẢNG 600 CHỮ)
# ==============================================================================
def evaluate_essay_strictly_by_7_criteria(essay_text, cur_de_info):
    text = essay_text.strip()
    topic_text = ensure_600_words_prompt(cur_de_info.get("text", ""))
    vdnl_chuan = cur_de_info.get("vdnl_chuan", "")

    prompt_grade = f"""Đóng vai Giám khảo chấm thi Ngữ văn THPT công tâm, chuẩn mực. Hãy đọc kỹ từng câu trong bài làm dưới đây và chấm theo BẢNG RUBRIC 7 TIÊU CHÍ (Thang điểm 10.0, bước nhảy 0.25đ).
- Đề bài (Yêu cầu bài văn khoảng 600 chữ): "{topic_text}"
- Vấn đề nghị luận: "{vdnl_chuan}"
- Bài làm của học sinh:
\"\"\"{text}\"\"\"

QUY TẮC CHẤM NGHIÊM NGẶT:
1. Chuẩn dung lượng đề bài là bài văn khoảng 600 chữ. Nếu bài viết dưới 450 chữ, tuyệt đối KHÔNG ĐƯỢC xếp loại Giỏi/Xuất sắc (tổng điểm không quá 6.5đ vì chưa triển khai đủ độ sâu của một bài văn 600 chữ). Nếu dưới 250 chữ, tổng điểm dưới 4.5đ.
2. Ở tiêu chí Giải thích: nếu đề nêu trực tiếp vấn đề, chỉ cần học sinh giải thích ngắn gọn, rõ khái niệm trọng tâm là đạt điểm tối đa (không đòi hỏi giải thích rườm rà nhiều lớp).
3. BẮT BUỘC TRÍCH DẪN NGUYÊN VĂN (trong dấu ngoặc kép "...") ít nhất 3 câu văn cụ thể từ bài làm của học sinh vào cột Nhận xét để làm bằng chứng.
4. Lập bảng Markdown đúng 4 cột: Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm."""

    ai_eval = call_gemini_rest_api(prompt_grade)
    if ai_eval and "|" in ai_eval:
        return ai_eval

    words = re.findall(r'\w+', text)
    word_count = len(words)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\n', text) if len(p.strip()) > 10]
    num_paras = len(paragraphs)
    sentences = [s.strip() for s in re.split(r'[.?!]+', text) if len(s.strip()) > 5]
    num_sents = len(sentences)

    first_sent = sentences[0] if num_sents > 0 else text[:80]
    shortest_sent = min(sentences, key=lambda s: len(s.split())) if num_sents > 1 else first_sent
    longest_sent = max(sentences, key=lambda s: len(s.split())) if num_sents > 0 else first_sent

    text_low = text.lower()
    vdnl_tokens = [w for w in extract_clean_topic_noun(vdnl_chuan + " " + topic_text).lower().split() if len(w) > 2]
    matched_topic_kws = [w for w in vdnl_tokens if w in text_low]
    topic_coverage = len(matched_topic_kws) / max(len(vdnl_tokens), 1)

    explain_markers = ["là", "được hiểu là", "chính là", "nghĩa là", "khái niệm", "biểu hiện của", "thể hiện qua", "sức mạnh của", "tinh thần"]
    has_explain = sum(1 for m in explain_markers if m in text_low)

    argument_markers = ["trước hết", "thứ nhất", "thứ hai", "bên cạnh đó", "hơn thế nữa", "không chỉ vậy", "mặt khác", "bởi vì", "do đó", "chính vì", "nhờ có", "giúp cho", "tạo nên", "thúc đẩy", "cá nhân", "cộng đồng", "xã hội"]
    arg_count = sum(1 for m in argument_markers if m in text_low)

    evidence_markers = ["ví dụ", "dẫn chứng", "tiêu biểu", "chẳng hạn", "câu chuyện", "tấm gương", "như anh", "như chị", "thầy", "bác", "chiến dịch", "dự án", "thực tế"]
    ev_marker_count = sum(1 for m in evidence_markers if m in text_low)
    proper_nouns = re.findall(r'(?<=[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]\s)[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+(?:\s[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+)+', text)

    counter_markers = ["tuy nhiên", "ngược lại", "đáng buồn", "phê phán", "bên cạnh những", "mặt trái", "thực trạng", "vô cảm", "ích kỷ", "lệch lạc", "nhầm lẫn", "cực đoan"]
    counter_count = sum(1 for m in counter_markers if m in text_low)

    word_freq = {}
    for w in words:
        w_l = w.lower()
        if len(w_l) > 4:
            word_freq[w_l] = word_freq.get(w_l, 0) + 1
    repeated_words = [w for w, c in word_freq.items() if c >= max(6, word_count // 45)]

    # 1. Bố cục (0.5đ)
    if num_paras >= 3 and word_count >= 450:
        s1 = 0.5
        c1_note = f"Bài viết chia thành **{num_paras} đoạn văn**, đảm bảo kết cấu 3 phần Mở - Thân - Kết của bài văn nghị luận (khoảng 600 chữ)."
    elif num_paras >= 3 and word_count >= 220:
        s1 = 0.25
        c1_note = f"Có chia thành {num_paras} đoạn nhưng dung lượng mới đạt **{word_count} chữ** (chưa đạt yêu cầu đề bài là khoảng 600 chữ)."
    else:
        s1 = 0.0 if word_count < 100 else 0.25
        c1_note = f"Bố cục chưa đảm bảo: bài viết chỉ có **{num_paras} đoạn** với **{word_count} chữ**, thiếu sự phân tách rõ ràng Mở - Thân - Kết."

    # 2. Xác định VĐNL (0.5đ)
    if topic_coverage >= 0.4 and word_count >= 150:
        s2 = 0.5
        c2_note = f"Xác định đúng vấn đề nghị luận trọng tâm (*{vdnl_chuan}*). Minh chứng câu mở đầu: *\"{first_sent[:110]}...\"*."
    elif topic_coverage > 0:
        s2 = 0.25
        c2_note = f"Có nhắc tới từ khóa của đề nhưng giới thiệu còn vòng vo (*\"{first_sent[:90]}...\"*)."
    else:
        s2 = 0.0
        c2_note = "Chưa nêu được vấn đề nghị luận trọng tâm của đề bài."

    # 3. Giải thích khái niệm (1.0đ) -> Chấm linh hoạt, chỉ cần giải thích gọn rõ khái niệm chính
    if has_explain >= 1 and word_count >= 380:
        s3 = 0.75 if word_count < 500 else 1.0
        c3_note = "Đã giải thích trực diện, rõ ràng khái niệm trọng tâm của đề bài trước khi đi vào bàn luận."
    elif has_explain >= 1 and word_count >= 180:
        s3 = 0.5
        c3_note = "Có bước đầu cắt nghĩa khái niệm nhưng diễn đạt còn sơ lược, cần chốt rõ bản chất của vấn đề hơn."
    else:
        s3 = 0.25 if word_count >= 120 else 0.0
        c3_note = "Thiếu thao tác giải thích khái niệm cốt lõi ở đầu phần Thân bài."

    # 4. Hệ thống luận điểm (3.5đ) -> Đối chiếu sát với yêu cầu bài văn khoảng 600 chữ
    if word_count < 180:
        s4 = 0.5
        c4_note = f"Dung lượng quá ngắn (**{word_count} chữ / ~600 chữ** theo yêu cầu đề bài). Hoàn toàn chưa triển khai được các luận điểm bàn luận. Câu viết sơ sài: *\"{shortest_sent}\"*."
    elif word_count < 350:
        s4 = 1.25 if arg_count >= 3 else 1.0
        c4_note = f"Bài làm mới đạt **{word_count} chữ** (chỉ bằng một nửa so với yêu cầu khoảng 600 chữ). Mới nêu được vài ý bề nổi, thiếu phân tích sâu. Minh chứng câu đơn giản: *\"{shortest_sent}\"*."
    elif word_count < 500:
        s4 = 2.0 if arg_count >= 5 else 1.5
        c4_note = f"Dung lượng đạt **{word_count} chữ** (vẫn thiếu hụt so với chuẩn bài văn khoảng 600 chữ). Đã có lập luận (*\"{longest_sent[:110]}...\"*) nhưng chưa triển khai đủ 5 luận điểm sâu sắc."
    elif word_count < 600:
        s4 = 2.5 if arg_count >= 6 else 2.25
        c4_note = f"Dung lượng tiệm cận mức yêu cầu (**{word_count} chữ**). Có các ý bàn luận cơ bản (*\"{longest_sent[:110]}...\"*) nhưng cần đào sâu hơn ý nghĩa đối với cộng đồng và thời đại."
    else:
        s4 = 3.0 if arg_count >= 7 else 2.5
        c4_note = f"Đạt chuẩn dung lượng bài văn (**{word_count} chữ**), hệ thống luận điểm triển khai đầy đặn, chặt chẽ. Minh chứng câu lập luận tốt: *\"{longest_sent[:115]}...\"*."

    # 5. Dẫn chứng thực tế (2.5đ)
    if len(proper_nouns) >= 1 and ev_marker_count >= 1 and word_count >= 480:
        s5 = 2.0 if len(proper_nouns) >= 2 else 1.75
        c5_note = f"Có đưa dẫn chứng thực tế cụ thể (**{', '.join(list(set(proper_nouns))[:3])}**) và phân tích gắn với vấn đề nghị luận."
    elif len(proper_nouns) >= 1 or ev_marker_count >= 1:
        s5 = 1.0 if word_count >= 300 else 0.75
        c5_note = "Có nhắc tới dẫn chứng nhưng mới chỉ nêu tên/liệt kê sự việc mà thiếu câu văn phân tích sâu ý nghĩa của dẫn chứng đó."
    else:
        s5 = 0.25 if word_count >= 250 else 0.0
        c5_note = "Thiếu dẫn chứng người thật việc thật cụ thể; bài viết mới chỉ dùng lý lẽ thuần túy nên sức thuyết phục chưa cao."

    # 6. Phản đề & Bài học (1.0đ)
    if counter_count >= 2 and word_count >= 450:
        s6 = 0.75
        c6_note = "Đã có góc nhìn phản đề phê phán biểu hiện trái ngược và rút ra bài học nhận thức, hành động."
    elif counter_count >= 1 and word_count >= 250:
        s6 = 0.5
        c6_note = "Có ý phê phán/liên hệ nhưng còn ngắn gọn, chưa mở rộng được góc nhìn hai chiều."
    else:
        s6 = 0.25 if word_count >= 150 else 0.0
        c6_note = "Thiếu đoạn phản đề lật lại vấn đề; phần liên hệ bản thân còn chung chung."

    # 7. Diễn đạt & Chính tả (1.0đ)
    if len(shortest_sent.split()) < 6 or len(repeated_words) >= 3:
        s7 = 0.5
        rep_str = f"Lặp từ (*{', '.join(repeated_words[:4])}*)." if repeated_words else ""
        c7_note = f"Diễn đạt còn câu cụt hoặc khẩu ngữ. {rep_str} Câu cần sửa lại: *\"{shortest_sent}\"*."
    elif word_count < 400:
        s7 = 0.5
        c7_note = "Câu văn rõ ý nhưng lập luận còn mỏng, thiếu các từ ngữ liên kết chuyển đoạn."
    else:
        s7 = 0.75
        c7_note = "Diễn đạt mạch lạc, trong sáng, từ ngữ sử dụng chuẩn mực."

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

    return f"""### 📊 BẢNG ĐÁNH GIÁ RUBRIC 7 TIÊU CHÍ (CHUẨN BÀI VĂN KHOẢNG 600 CHỮ)
*📏 **Kiểm định thực tế:** Dung lượng **{word_count} chữ** (Yêu cầu đề bài: khoảng 600 chữ) | **{num_paras} đoạn văn** | **{num_sents} câu văn**.*

| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |
| :--- | :---: | :---: | :--- |
| **1. Bố cục (Mở - Thân - Kết)** | 0.50đ | **{s1:.2f}đ** | {c1_note} |
| **2. Xác định Vấn đề nghị luận** | 0.50đ | **{s2:.2f}đ** | {c2_note} |
| **3. Giải thích khái niệm** | 1.00đ | **{s3:.2f}đ** | {c3_note} |
| **4. Hệ thống luận điểm (5 ý)** | 3.50đ | **{s4:.2f}đ** | {c4_note} |
| **5. Dẫn chứng thực tế** | 2.50đ | **{s5:.2f}đ** | {c5_note} |
| **6. Phản đề & Bài học** | 1.00đ | **{s6:.2f}đ** | {c6_note} |
| **7. Diễn đạt & Chính tả** | 1.00đ | **{s7:.2f}đ** | {c7_note} |

---
### 📌 TỔNG ĐIỂM ĐẠT ĐƯỢC: **{total_score:.2f} / 10.0 điểm** — Xếp loại: **{rank}**

#### 📝 NHẬN XÉT & HƯỚNG DẪN CHỈNH SỬA CỤ THỂ:
* **Về yêu cầu dung lượng (khoảng 600 chữ):** Bài làm hiện tại đạt **{word_count} chữ** ({'đã đáp ứng tốt yêu cầu độ dài của đề bài' if word_count >= 550 else 'chưa đạt chuẩn dung lượng khoảng 600 chữ của đề bài, cần mở rộng thêm lập luận ở phần Thân bài'}).
* **Các điểm cần hoàn thiện ngay:** 
  1. Chỉnh sửa lại câu văn còn đơn giản/ngắn cụt trong bài: *\"{shortest_sent}\"*.
  2. {'Em hãy quay lại Bước 2 (Thao tác 3 - Kho dẫn chứng 9 chủ điểm) để chọn lấy 1-2 nhân vật thực tế đưa vào bài viết.' if s5 < 1.5 else 'Tiếp tục trau chuốt câu văn phân tích dẫn chứng để tăng sức thuyết phục.'}
  3. {'Bổ sung đoạn Phản đề phê phán các biểu hiện tiêu cực để bài viết toàn diện hơn.' if s6 < 0.75 else 'Giữ vững tư duy phản biện hai chiều sắc bén.'}"""


# ==============================================================================
# 7. GIAO DIỆN CHÍNH & QUY TRÌNH 4 BƯỚC SƯ PHẠM
# ==============================================================================
with st.sidebar:
    st.title("⚙️ HỆ THỐNG QUẢN TRỊ")
    st.success("✅ Hệ thống Sư phạm & Chấm điểm Rubric hoạt động ổn định 100%!")
    
    with st.expander("🔑 Cấu hình nâng cao (Dành cho GV)"):
        key_in = st.text_input("Mã Gemini API Key (Tùy chọn):", type="password", value=st.session_state["gemini_api_key"], help="Nếu nhập mã AIzaSy..., hệ thống kết hợp thêm AI đám mây. Nếu để trống, hệ thống tự động chạy Bộ máy NLP Sư phạm Nội bộ.")
        if key_in != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = key_in
            
    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM")
    st.markdown("1. **🌱 Bước 1:** Tìm hiểu đề & Xác định VĐNL")
    st.markdown("2. **🧵 Bước 2:** Tìm ý, Lập dàn ý & Kho dẫn chứng")
    st.markdown("3. **✍️ Bước 3:** Viết bài")
    st.markdown("4. **📊 Bước 4:** Kiểm tra và chỉnh sửa")

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NLXH</div>
    <p class="hero-subtitle">Ứng dụng trí tuệ nhân tạo trong dạy học viết nghị luận xã hội THPT theo định hướng phát triển năng lực</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & DẪN CHỨNG",
    "✍️ BƯỚC 3: VIẾT BÀI",
    "📊 BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA",
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🔍 Bước 1: Lựa chọn đề bài & Xác định vấn đề nghị luận</div>', unsafe_allow_html=True)
    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
        "🟢 Nhóm Đề Cơ Bản (Đề 01 – Đề 15)",
        "🔴 Nhóm Đề Nâng Cao (Đề 16 – Đề 30)",
        "✏️ Nhập / Dán Đề Bài Riêng",
    ])

    with tab_de_coban:
        col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
        with col_cb1:
            selected_cb_key = st.selectbox("Chọn đề trong nhóm Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="sb_coban")
            de_info_cb = db.DE_BAI_CO_BAN[selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài (Chuẩn bài văn khoảng 600 chữ):")
                st.info(ensure_600_words_prompt(de_info_cb["text"]))
            if st.button("📌 Chọn đề Cơ bản này để luyện tập", key="btn_chon_cb", type="primary"):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = de_info_cb
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Mời chuyển sang Bước 2.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox("Chọn đề trong nhóm Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="sb_nangcao")
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài (Chuẩn bài văn khoảng 600 chữ):")
                st.info(ensure_600_words_prompt(de_info_nc["text"]))
            if st.button("📌 Chọn đề Nâng cao này để luyện tập", key="btn_chon_nc", type="primary"):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = de_info_nc
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Mời chuyển sang Bước 2.")

    with tab_de_tu_nhap:
        st.markdown("##### ✏️ Nhập đề bài riêng (Hệ thống tự động chuẩn hóa lệnh đề bài văn khoảng 600 chữ và lập dàn ý sát dạng đề):")
        custom_de_text = st.text_area("Nội dung đề bài tự nhập:", placeholder="Ví dụ: Hãy viết một bài văn nghị luận (khoảng 600 chữ) trình bày suy nghĩ của anh/chị về sức mạnh của tinh thần sáng tạo...", height=110, key="txt_custom_de")
        student_custom_vdnl = st.text_input("Theo em, vấn đề nghị luận trọng tâm của đề bài này là gì?", placeholder="Ví dụ: Sức mạnh của tinh thần sáng tạo...", key="txt_custom_vdnl")
        if st.button("🔍 Phân tích đề tự nhập & Tạo khung định hướng Bước 2", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài trước khi bấm phân tích!")
            else:
                with st.spinner("Đang phân tích đề bài và thiết lập Khung định hướng Bước 2..."):
                    outline = build_dynamic_outline_for_custom_topic(custom_de_text.strip(), student_custom_vdnl.strip())
                    short_title = custom_de_text.strip()[:55] + ("..." if len(custom_de_text.strip()) > 55 else "")
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                    st.session_state["current_de_info"] = outline
                    st.success("✅ Đã thiết lập xong Khung định hướng tư duy tinh gọn, đúng trọng tâm! Mời chuyển sang **Bước 2**.")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Nội dung đề:* {ensure_600_words_prompt(cur_active_info.get('text', ''))}\n\n🎯 **Vấn đề nghị luận trọng tâm:** {cur_active_info.get('vdnl_chuan', '')}")


# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.15, 0.85], gap="large")

    with c_left:
        st.markdown(f"#### 🛠️ Khung định hướng tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>", unsafe_allow_html=True)
        
        with st.expander("📌 Thao tác 1: Giải thích (Ngắn gọn, đúng trọng tâm)", expanded=True):
            with st.container(border=True):
                raw_explains = cur_de_info.get("explain_items", [])
                # Nếu đề bài nêu trực tiếp vấn đề (không phải câu nói ẩn dụ trong ngoặc kép), chỉ hiển thị tinh gọn 1 ý giải thích khái niệm chính
                if not is_metaphorical_quote_topic(cur_de_info.get("text", "")) and len(raw_explains) > 1:
                    st.markdown(raw_explains[0])
                else:
                    for itm in raw_explains:
                        st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt lại VĐNL:** {cur_de_info.get('vdnl_ket_luan', '')}")

        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Từ 5 ý)", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế & Kho dẫn chứng 9 chủ điểm", expanded=True):
            st.markdown("##### 📌 1. Dẫn chứng gợi ý trực tiếp cho đề bài này:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    st.markdown(f"<div class='evidence-card'><h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5><p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p><p style='margin:0 0 6px 0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p></div>", unsafe_allow_html=True)
            
            # Hộp chỉ dẫn nổi bật nhắc học sinh khai thác Kho dẫn chứng 9 chủ điểm
            st.markdown(
                """
                <div class="repo-guide-box">
                    💡 <b>MÁCH NHỎ CHO HỌC SINH:</b> Ngoài dẫn chứng gợi ý trên, hệ thống đã trang bị sẵn <b>Kho dẫn chứng 9 chủ điểm mở rộng</b> ngay bên dưới. Em hãy bấm vào khung chọn chủ điểm để tìm thêm những tấm gương người thật việc thật đắt giá nhất đưa vào bài viết của mình nhé!
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("##### 📚 2. Khai thác Kho dẫn chứng 9 chủ điểm (Mở rộng):")
            selected_topic = st.selectbox("👉 Bấm vào đây để chọn chủ điểm dẫn chứng cần tham khảo:", list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()), key="sb_kho_dc")
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"**👤 {dc['ten']}**")
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 Nguồn: {dc['nguon']}")

        with st.expander("🔄 Thao tác 4: Phản đề & Bài học", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        with st.expander("📝 Bố cục Dàn ý chi tiết 3 phần (Chuẩn bài văn khoảng 600 chữ)", expanded=True):
            dani = cur_de_info.get("dani_chi_tiet", {})
            with st.container(border=True):
                st.markdown(f"**I. MỞ BÀI:** {dani.get('mb','')}")
                st.markdown(f"**II. THÂN BÀI:**\n1. {dani.get('gt','')}\n2. {dani.get('bl','')}\n3. {dani.get('dc','')}\n4. {dani.get('pb','')}")
                st.markdown(f"**III. KẾT BÀI:** {dani.get('kb','')}")

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn Tư Vấn (Chat)")
        chat_container = st.container(height=420, border=True)
        with chat_container:
            for role, msg in st.session_state["chat_history"]:
                st.markdown(f"**{'🧑‍🎓 Học sinh' if role == 'user' else '👩‍🏫 Trợ lý Ngữ văn'}:**\n\n{msg}")
                st.markdown("---")

        user_question = st.text_area("Nhập câu hỏi cụ thể (VD: Cách viết mở bài, giải thích, đưa dẫn chứng, phản đề, liên hệ...):", height=80, key="txt_chat_input")
        col_chat_1, col_chat_2 = st.columns([2, 1])
        with col_chat_1:
            if st.button("🚀 Gửi câu hỏi", type="primary", use_container_width=True):
                if user_question.strip():
                    with st.spinner("Trợ lý Ngữ văn đang phân tích câu hỏi..."):
                        reply = generate_deep_chat_response(user_question.strip(), cur_de_info)
                        st.session_state["chat_history"].append(("user", user_question.strip()))
                        st.session_state["chat_history"].append(("assistant", reply))
                        st.rerun()
                else:
                    st.warning("Em hãy nhập câu hỏi trước khi bấm gửi nhé!")
        with col_chat_2:
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                st.session_state["chat_history"] = [
                    ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em đang vướng ở khâu nào (Mở bài, Giải thích, Luận điểm, Dẫn chứng hay Phản đề)?")
                ]
                st.rerun()


# ------------------------------------------------------------------------------
# BƯỚC 3: VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info(f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n📖 *{ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}*")

    write_mode = st.radio(
        "Chọn hình thức nộp bài:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode"
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội (Yêu cầu: Bài văn hoàn chỉnh khoảng 600 chữ):",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy tự viết bài văn hoàn chỉnh của em tại đây (Đảm bảo đủ 3 phần Mở bài, Thân bài tách các đoạn rõ ràng, Kết bài)..."
        )
        st.session_state["user_essay"] = essay_input
        wc = len(re.findall(r'\w+', essay_input)) if essay_input.strip() else 0
        st.caption(f"📊 Dung lượng hiện tại: **{wc} chữ** {'(Chưa đạt yêu cầu khoảng 600 chữ của đề bài)' if wc < 550 else '(Đã đạt chuẩn dung lượng khoảng 600 chữ)'}.")

        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            if st.button("💡 Nhắc lại tiêu chuẩn bài văn 600 chữ", use_container_width=True):
                st.info("💡 **Lưu ý:** Bài văn cần đạt dung lượng khoảng 600 chữ, bố cục 3 phần rõ ràng, giải thích ngắn gọn trúng trọng tâm, thân bài đủ 5 luận điểm, có dẫn chứng thực tế và phản đề sắc bén!")
        with col_w2:
            if st.button("📊 Nộp bài & Chấm Rubric 7 Tiêu Chí", type="primary", use_container_width=True):
                if not essay_input.strip():
                    st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên!")
                else:
                    with st.spinner("Đang đọc từng câu, kiểm định dung lượng và chấm theo 7 tiêu chí Rubric..."):
                        st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(essay_input.strip(), st.session_state["current_de_info"])
                        st.success("✅ Đã chấm xong! Mời chuyển sang **Bước 4: Kiểm tra và chỉnh sửa** để xem Bảng điểm chi tiết.")
    else:
        uploaded_img = st.file_uploader("Tải lên ảnh chụp bài làm viết tay:", type=["png", "jpg", "jpeg"])
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm của học sinh", use_column_width=True)
            ocr_assist_text = st.text_area(
                "Nhập/dán nội dung văn bản từ ảnh (hoặc để hệ thống quét trực tiếp nếu đã kết nối khóa AI):",
                height=150,
                placeholder="Nếu chưa nhập khóa AI đám mây, em hãy dán nội dung bài viết vào đây để bộ máy kiểm định chính xác từng câu chữ..."
            )
            if st.button("📊 Đọc bài & Chấm Rubric 7 Tiêu Chí", type="primary"):
                with st.spinner("Đang xử lý bài làm và chấm điểm theo 7 tiêu chí..."):
                    prompt_img = f"""Hãy đọc toàn bộ chữ viết tay trong bức ảnh này và chấm điểm theo Bảng Rubric 7 tiêu chí (Thang điểm 10.0) cho đề bài (khoảng 600 chữ): "{ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}".
Bắt buộc trích dẫn nguyên văn các câu trong ảnh bài làm để làm minh chứng trừ điểm/cộng điểm, kiểm tra kỹ độ dài thực tế."""
                    ai_img_res = call_gemini_rest_api(prompt_img, pil_image=img_obj)
                    if ai_img_res and "|" in ai_img_res:
                        st.session_state["rubric_evaluation"] = ai_img_res
                        st.success("✅ Đã đọc ảnh và chấm xong! Mời sang Bước 4 xem kết quả.")
                    elif ocr_assist_text.strip():
                        st.session_state["user_essay"] = ocr_assist_text.strip()
                        st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(ocr_assist_text.strip(), st.session_state["current_de_info"])
                        st.success("✅ Đã chấm xong văn bản bài làm! Mời sang Bước 4 xem kết quả.")
                    else:
                        st.warning("⚠️ Để đọc trực tiếp chữ viết tay từ ảnh mà không cần gõ lại, vui lòng nhập khóa Gemini API (`AIzaSy...`) ở mục Cấu hình nâng cao bên trái, hoặc dán văn bản bài viết vào ô bên trên.")


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra và Chỉnh Sửa Theo Rubric</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric đánh giá bài văn Nghị luận xã hội (Chuẩn bài văn khoảng 600 chữ - Thang điểm 10):</b><br>
            1. <b>Bố cục (0.5đ):</b> Đủ 3 phần Mở - Thân - Kết, tách đoạn hợp lý.<br>
            2. <b>Xác định VĐNL (0.5đ):</b> Nêu đúng trọng tâm vấn đề nghị luận.<br>
            3. <b>Giải thích (1.0đ):</b> Giải thích ngắn gọn, đúng trọng tâm khái niệm/hình ảnh của đề.<br>
            4. <b>Hệ thống luận điểm (3.5đ):</b> Triển khai tối thiểu 5 ý sâu sắc, đáp ứng dung lượng bài văn khoảng 600 chữ.<br>
            5. <b>Dẫn chứng (2.5đ):</b> Người thật việc thật xác thực, phân tích gắn với luận điểm.<br>
            6. <b>Phản đề & Bài học (1.0đ):</b> Có góc nhìn lật lại vấn đề hai chiều và bài học thực chất.<br>
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
            key="essay_step4_editor"
        )
        st.session_state["user_essay"] = edited_essay
        wc_step4 = len(re.findall(r'\w+', edited_essay)) if edited_essay.strip() else 0
        st.caption(f"📏 Số chữ sau khi chỉnh sửa: **{wc_step4} chữ** (Chuẩn đề bài: khoảng 600 chữ).")

        if st.button("🔍 Cập nhật chấm lại Rubric", type="primary", use_container_width=True):
            if edited_essay.strip():
                with st.spinner("Đang kiểm định lại từng tiêu chí sau khi chỉnh sửa..."):
                    st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(edited_essay.strip(), st.session_state["current_de_info"])
                    st.success("✅ Đã cập nhật bảng điểm mới sát với nội dung vừa chỉnh sửa!")
            else:
                st.warning("⚠️ Hãy nhập bài viết để hệ thống chấm điểm!")

        if edited_essay.strip():
            content = f"HỒ SƠ BÀI LÀM NLXH\nĐỀ BÀI: {st.session_state['selected_de_key']}\nNỘI DUNG ĐỀ: {ensure_600_words_prompt(st.session_state['current_de_info'].get('text', ''))}\n\n-- BÀI LÀM CỦA HỌC SINH ({wc_step4} chữ) --\n{edited_essay}\n\n-- KẾT QUẢ ĐÁNH GIÁ RUBRIC --\n{st.session_state.get('rubric_evaluation', '')}"
            st.download_button(
                label="📥 Tải Hồ sơ bài làm & Bảng Rubric (.txt)",
                data=content.encode("utf-8"),
                file_name="HoSo_LuyenViet_NLXH.txt",
                use_container_width=True
            )

    with col_r2:
        st.markdown("##### 📋 Bảng Điểm & Nhận Xét Chi Tiết:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info("💡 Chưa có bảng điểm. Hãy nộp bài ở Bước 3 và bấm Chấm điểm.")
