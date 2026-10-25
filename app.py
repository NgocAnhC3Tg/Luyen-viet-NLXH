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
""",
    unsafe_allow_html=True,
)

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
if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
if "selected_de_key" not in st.session_state: st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]
if "current_de_info" not in st.session_state: st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]
if "chat_history" not in st.session_state: st.session_state["chat_history"] = [("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Cô sẵn sàng hỗ trợ em định hướng phương pháp lập ý theo đúng dạng đề, cung cấp dẫn chứng thực tế và gợi ý cách hành văn, nhưng em phải tự viết bài nhé. Em đang vướng ở phần nào?")]
if "user_essay" not in st.session_state: st.session_state["user_essay"] = ""
if "rubric_evaluation" not in st.session_state: st.session_state["rubric_evaluation"] = ""
if "eval_vdnl_text" not in st.session_state: st.session_state["eval_vdnl_text"] = ""
if "selected_essay_type_override" not in st.session_state: st.session_state["selected_essay_type_override"] = "Tự động nhận diện theo đề bài"

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
def call_gemini_rest_api(prompt, pil_image=None, contents_list=None, system_instruction=None, temperature=0.45):
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
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }
                })
            except Exception:
                pass
        contents_payload = [{"parts": parts}]

    payload = {
        "contents": contents_payload,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 3800}
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    data = json.dumps(payload).encode("utf-8")

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=24) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                ifCandidates = len(candidates) > 0
                if ifCandidates:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if content_parts and "text" in content_parts[0]:
                        return content_parts[0]["text"]
        except Exception:
            continue
    return None

# ==============================================================================
# 5. HỆ THỐNG TỪ ĐIỂN SƯ PHẠM & NHẬN DIỆN 5 DẠNG BÀI + 3 TRƯỜNG HỢP TƯ TƯỞNG ĐẠO LÝ
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

DANH_SACH_DANG_BAI = [
    "Tự động nhận diện theo đề bài",
    "Dạng 1 - TH1: Tư tưởng, đạo lí (Bàn sâu về Ý nghĩa / Giá trị / Vai trò / Sức mạnh)",
    "Dạng 1 - TH2: Tư tưởng, đạo lí (Bàn về Bài học giải pháp / Trách nhiệm cần làm gì)",
    "Dạng 1 - TH3: Tư tưởng, đạo lí (Suy nghĩ chung toàn diện về một tư tưởng/phẩm chất)",
    "Dạng 2: Nghị luận về một vấn đề cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả - Giải pháp)",
    "Dạng 3: Nghị luận lựa chọn quan điểm (Đứng trước 2 quan điểm / ý kiến)",
    "Dạng 4: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học",
    "Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm"
]

def extract_clean_topic_noun(text):
    clean = re.sub(r'(?i)(hãy viết một bài văn nghị luận xã hội|hãy viết bài văn nghị luận|khoảng 600 chữ|trình bày suy nghĩ của anh/chị về|suy nghĩ của anh/chị về|suy nghĩ về|bàn về|ý nghĩa của|vai trò của|tầm quan trọng của|sức mạnh của|sự cần thiết của|giá trị của|thuyết phục người khác từ bỏ|giải pháp khắc phục|làm thế nào để)', '', text)
    clean = re.sub(r'[():.,?!"]', '', clean).strip()
    return clean if clean else text.strip()

def is_metaphorical_quote_topic(topic_text):
    if '"' in topic_text or '“' in topic_text or '”' in topic_text:
        return True
    if any(w in topic_text.lower() for w in ["có ý kiến cho rằng", "ngạn ngữ", "danh ngôn", "nhà văn", "từng nói", "câu nói"]):
        return True
    return False

def classify_essay_type(topic_text, vdnl_text="", manual_override="Tự động nhận diện theo đề bài"):
    if manual_override and manual_override != "Tự động nhận diện theo đề bài":
        if "Dạng 1 - TH1" in manual_override: return "DANG_1_TH1"
        if "Dạng 1 - TH2" in manual_override: return "DANG_1_TH2"
        if "Dạng 1 - TH3" in manual_override: return "DANG_1_TH3"
        if "Dạng 2" in manual_override: return "DANG_2_GIAI_QUYET"
        if "Dạng 3" in manual_override: return "DANG_3_HAI_QUAN_DIEM"
        if "Dạng 4" in manual_override: return "DANG_4_VAN_HOC"
        if "Dạng 5" in manual_override: return "DANG_5_TU_BO"

    combined = (topic_text + " " + vdnl_text).lower()

    # Nhận diện Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm
    if any(kw in combined for kw in ["thuyết phục", "từ bỏ một thói quen", "từ bỏ thói quen", "từ bỏ một quan niệm", "từ bỏ quan niệm", "từ bỏ lối sống", "khuyên bạn từ bỏ", "viết bài luận thuyết phục"]):
        return "DANG_5_TU_BO"

    # Nhận diện Dạng 4: Vấn đề xã hội rút ra từ tác phẩm văn học
    if any(kw in combined for kw in ["tác phẩm", "truyện ngắn", "bài thơ", "nhân vật văn học", "đoạn trích", "văn bản", "nhà thơ", "tiểu thuyết", "rút ra từ tác phẩm", "qua nhân vật"]):
        return "DANG_4_VAN_HOC"

    # Nhận diện Dạng 3: Lựa chọn quan điểm (2 luồng ý kiến)
    if any(kw in combined for kw in ["hai quan điểm", "2 quan điểm", "hai ý kiến", "nhưng có ý kiến khác lại cho rằng", "trong khi đó có người lại nghĩ", "anh/chị chọn quan điểm nào", "bạn chọn", "giữa hai lựa chọn", "hay là"]):
        if "quan điểm" in combined or "ý kiến" in combined or "lựa chọn" in combined or "chọn" in combined:
            return "DANG_3_HAI_QUAN_DIEM"

    # Nhận diện Dạng 2: Vấn đề cần giải quyết (hiện tượng đời sống hoặc vấn đề tốt đang mai một cần giải pháp)
    negative_phenomena = ["ô nhiễm", "nghiện game", "bạo lực học đường", "bạo lực mạng", "rác thải", "lãng phí", "gian lận", "sống ảo", "thờ ơ", "vô cảm", "biến đổi khí hậu", "an toàn giao thông", "thực trạng", "vấn nạn", "hiện tượng", "cần giải quyết", "khắc phục tình trạng", "giải pháp để khắc phục", "mất kết nối"]
    if any(kw in combined for kw in negative_phenomena):
        return "DANG_2_GIAI_QUYET"

    # Nhận diện Dạng 1 - TH2: Bài học mang tính giải pháp (cần làm gì / trách nhiệm của A với B)
    if any(kw in combined for kw in ["cần làm gì", "phải làm gì", "làm thế nào để", "trách nhiệm của tuổi trẻ", "trách nhiệm của thế hệ trẻ", "trách nhiệm của học sinh", "vai trò của người trẻ đối với", "bổn phận của"]):
        return "DANG_1_TH2"

    # Nhận diện Dạng 1 - TH1: Hỏi trực tiếp mặt tích cực (ý nghĩa / sự cần thiết / giá trị / vai trò / sức mạnh / tầm quan trọng)
    if any(kw in combined for kw in ["ý nghĩa của", "sự cần thiết của", "giá trị của", "vai trò của", "sức mạnh của", "tầm quan trọng của", "vẻ đẹp của", "lợi ích của"]):
        return "DANG_1_TH1"

    # Mặc định là Dạng 1 - TH3: Hỏi chung, nêu suy nghĩ về A
    return "DANG_1_TH3"

def get_essay_type_label(code):
    labels = {
        "DANG_1_TH1": "Dạng 1 (TH1): Nghị luận Tư tưởng, đạo lí — Bàn sâu về Ý nghĩa / Giá trị / Vai trò / Sức mạnh",
        "DANG_1_TH2": "Dạng 1 (TH2): Nghị luận Tư tưởng, đạo lí — Bàn về Bài học giải pháp (Trả lời câu hỏi: Cần làm gì?)",
        "DANG_1_TH3": "Dạng 1 (TH3): Nghị luận Tư tưởng, đạo lí — Bàn luận toàn diện (Giải thích -> Biểu hiện -> Ý nghĩa -> Dẫn chứng -> Phát huy)",
        "DANG_2_GIAI_QUYET": "Dạng 2: Nghị luận về một vấn đề cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả - Giải pháp 3 cấp độ)",
        "DANG_3_HAI_QUAN_DIEM": "Dạng 3: Nghị luận lựa chọn quan điểm (Phân tích mối quan hệ 2 quan điểm, bảo vệ lựa chọn & chỉ hạn chế quan điểm kia)",
        "DANG_4_VAN_HOC": "Dạng 4: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học",
        "DANG_5_TU_BO": "Dạng 5: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm"
    }
    return labels.get(code, labels["DANG_1_TH3"])

def is_positive_topic_declining(topic_text, vdnl_text):
    combined = (topic_text + " " + vdnl_text).lower()
    direct_negative = ["ô nhiễm", "nghiện game", "bạo lực", "rác thải", "gian lận", "lãng phí", "tệ nạn", "cờ bạc", "thuốc lá", "nói tục"]
    if any(neg in combined for neg in direct_negative):
        return False
    return True

def get_pedagogical_structure_guide(type_code, raw_topic, vdnl):
    has_meaning_step = is_positive_topic_declining(raw_topic, vdnl)
    if type_code == "DANG_1_TH1":
        return f"""DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 1: Đề hỏi trực tiếp khía cạnh mặt tích cực (ý nghĩa/sự cần thiết/giá trị/vai trò/sức mạnh/tầm quan trọng của "{vdnl}").
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Dẫn dắt và nêu trực diện vấn đề nghị luận (nhấn mạnh tầm quan trọng/ý nghĩa của {vdnl}).
- Thao tác 1 (Giải thích): Giải thích từ khóa/khái niệm/ý kiến và chốt vấn đề.
- Thao tác 2 (Bàn luận trọng tâm - Bàn sâu về Ý NGHĨA của VĐNL): Tập trung phân tích sâu sắc các tầng ý nghĩa, giá trị, sức mạnh của {vdnl} đối với sự trưởng thành của cá nhân, đối với mối quan hệ giữa người với người và đối với sự phát triển của cộng đồng, xã hội; lý giải vì sao {vdnl} lại cần thiết trong thời đại hôm nay.
- Thao tác 3 (Dẫn chứng): Đưa dẫn chứng thực tế xác thực chứng minh cho sức mạnh/ý nghĩa đó.
- Thao tác 4 (Phản đề & Bài học): Phê phán biểu hiện đi ngược lại, mở rộng biện chứng và rút ra bài học nhận thức, hành động."""
    
    if type_code == "DANG_1_TH2":
        return f"""DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 2: Đề hỏi các bài học mang tính giải pháp (trả lời câu hỏi: Cần làm gì? Vai trò/trách nhiệm của chủ thể đối với "{vdnl}").
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Dẫn dắt và nêu vấn đề nghị luận gắn với trách nhiệm/hành động cần thực hiện.
- Thao tác 1 (Giải thích & Khái quát sự cần thiết): Giải thích khái niệm và khẳng định ngắn gọn tầm quan trọng của vấn đề để làm tiền đề cho hành động.
- Thao tác 2 (Bàn luận trọng tâm - Trả lời câu hỏi CẦN LÀM GÌ?): Triển khai hệ thống các bài học/giải pháp cụ thể, sâu sắc:
  + Về nhận thức, tư tưởng: Thay đổi tư duy, xác lập thái độ đúng đắn như thế nào?
  + Về hành động, rèn luyện thực tế: Cần trau dồi kỹ năng gì, hành động cụ thể ra sao trong học tập, lao động và cống hiến?
  + Về sự lan tỏa và kết nối cộng đồng: Làm gì để cùng cộng đồng thúc đẩy giá trị tốt đẹp đó?
- Thao tác 3 (Dẫn chứng): Dẫn chứng người thật việc thật đã hành động quyết liệt, hiệu quả.
- Thao tác 4 (Phản đề & Liên hệ): Phê phán thái độ thụ động, nói suông không làm; liên hệ bản thân và Kết bài."""

    if type_code == "DANG_1_TH3":
        return f"""DẠNG BÀI: Nghị luận tư tưởng, đạo lí - Trường hợp 3: Đề hỏi chung, nêu suy nghĩ về "{vdnl}".
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Giới thiệu và dẫn vào vấn đề nghị luận "{vdnl}".
- Thao tác 1 (Giải thích): Giải thích rõ ràng khái niệm/nhận định "{vdnl}".
- Thao tác 2 (Bàn luận toàn diện):
  + Nêu biểu hiện cụ thể của "{vdnl}" trong đời sống.
  + Phân tích ý nghĩa, giá trị của "{vdnl}" đối với cá nhân và xã hội (kết hợp dẫn chứng thực tế).
  + Chỉ ra cần làm gì để phát huy "{vdnl}" trong cuộc sống hôm nay (bài học giải pháp phát huy).
- Thao tác 3 (Phản đề & Mở rộng): Phê phán biểu hiện lệch lạc/trái ngược.
- Kết bài: Khẳng định lại vấn đề và liên hệ cá nhân sâu sắc."""

    if type_code == "DANG_2_GIAI_QUYET":
        meaning_note = (
            f"- Bước 2 (Ý nghĩa của vấn đề): Vì đề cập đến một giá trị tích cực đang có chiều hướng mai một/chưa tốt ({vdnl}), cần viết 1 đoạn ngắn khẳng định ý nghĩa vốn có của nó trước khi nêu thực trạng."
            if has_meaning_step else
            f"- Lưu ý: Vì đề hỏi trực tiếp về một hiện tượng tiêu cực ({vdnl}), đi thẳng từ Giải thích sang Lí do cần giải quyết (không cần đoạn ca ngợi ý nghĩa)."
        )
        return f"""DẠNG BÀI: Nghị luận về một vấn đề cần giải quyết ("{vdnl}").
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Dẫn dắt và nêu trực diện vấn đề cần giải quyết.
- Bước 1 (Giải thích): Cắt nghĩa rõ bản chất vấn đề cần giải quyết.
{meaning_note}
- Bước 3 (Lí do cần giải quyết): Viết gọn thành 01 đoạn văn chặt chẽ tích hợp đủ 3 ý: Thực trạng đang diễn ra như thế nào -> Nguyên nhân (chủ quan, khách quan) -> Hậu quả/Hệ lụy nghiêm trọng nếu không giải quyết.
- Bước 4 (Đưa ra Giải pháp - Trọng tâm, trình bày thành 3 đoạn văn rõ ràng):
  + Đoạn 1 - Giải pháp đối với Cá nhân: Nêu giải pháp khả thi -> Lí giải vì sao chọn giải pháp đó -> Kèm ít nhất 01 dẫn chứng thực tế.
  + Đoạn 2 - Giải pháp đối với Gia đình: Nêu giải pháp khả thi -> Lí giải vì sao -> Kèm ít nhất 01 dẫn chứng thực tế.
  + Đoạn 3 - Giải pháp đối với Nhà trường / Xã hội: Nêu giải pháp khả thi -> Lí giải vì sao -> Kèm ít nhất 01 dẫn chứng thực tế.
- Bước 5 (Ý kiến khác & Phản biện): Nêu ý kiến trái chiều (thường cho rằng việc giải quyết là không cần thiết hoặc bất khả thi) -> Phản biện sắc bén để khẳng định dứt khoát vẫn cần phải khắc phục.
- Kết bài: Khẳng định lại thông điệp và rút ra bài học liên hệ bản thân."""

    if type_code == "DANG_3_HAI_QUAN_DIEM":
        return f"""DẠNG BÀI: Nghị luận lựa chọn quan điểm ("{vdnl}").
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Giới thiệu cả 2 quan điểm được nêu trong đề bài VÀ chỉ ra rõ ràng quan điểm lựa chọn của bản thân.
- Bước 1 (Giải thích & Mối quan hệ): Giải thích tường minh quan điểm 1, giải thích quan điểm 2, và chỉ ra mối quan hệ giữa 2 quan điểm (đối lập hay bổ sung ở những khía cạnh nào).
- Bước 2 (Lí giải vì sao chọn quan điểm của mình + Dẫn chứng): Đưa ra hệ thống lý lẽ sắc bén để bảo vệ quan điểm đã chọn, kết hợp phân tích dẫn chứng thực tế thuyết phục.
- Bước 3 (Chỉ ra hạn chế của quan điểm còn lại): Phân tích khách quan những điểm chưa toàn diện, bất cập hoặc hệ lụy nếu tuyệt đối hóa quan điểm còn lại.
- Bước 4 (Bài học khái quát & Bài học liên hệ): Rút ra bài học nhận thức khái quát và liên hệ trực tiếp tới bản thân.
- Kết bài: Khẳng định lại lập trường và thông điệp kết thúc."""

    if type_code == "DANG_4_VAN_HOC":
        return f"""DẠNG BÀI: Nghị luận về một vấn đề xã hội rút ra từ tác phẩm văn học ("{vdnl}").
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Giới thiệu tác giả, tác phẩm/nhân vật và dẫn dắt vào vấn đề xã hội cần nghị luận.
- Bước 1 (Phân tích ngắn gọn ngữ liệu văn học để rút ra vấn đề): Khái quát ngắn gọn tình huống, hình tượng hoặc chi tiết trong tác phẩm, từ đó chốt lại vấn đề tư tưởng/xã hội mà nhà văn gửi gắm.
- Bước 2 (Giải thích vấn đề xã hội): Giải thích khái niệm, bản chất của vấn đề xã hội đó khi đặt trong đời sống thực tiễn.
- Bước 3 (Bàn luận vấn đề trong đời sống thực tế + Dẫn chứng): Phân tích biểu hiện, ý nghĩa/tác động của vấn đề đối với con người và xã hội hôm nay; đưa dẫn chứng người thật việc thật ngoài đời sống để chứng minh.
- Bước 4 (Mở rộng, Phản đề & Bài học): Phê phán các biểu hiện lệch lạc, khẳng định sức sống của thông điệp từ trang sách ra đời thực và rút ra bài học nhận thức, hành động cho bản thân.
- Kết bài: Khẳng định giá trị nhân sinh của tác phẩm và thông điệp xã hội."""

    if type_code == "DANG_5_TU_BO":
        return f"""DẠNG BÀI: Thuyết phục người khác từ bỏ một thói quen hay một quan niệm ("{vdnl}").
CẤU TRÚC TƯ DUY BẮT BUỘC:
- Mở bài: Dẫn dắt gần gũi, nêu rõ thói quen/quan niệm cần từ bỏ và bày tỏ thiện chí thuyết phục.
- Bước 1 (Giải thích & Biểu hiện): Giải thích thói quen/quan niệm đó là gì và chỉ ra những biểu hiện phổ biến của nó trong đời sống hàng ngày.
- Bước 2 (Lí do vì sao phải từ bỏ): Phân tích sâu sắc những hậu quả, tác hại đối với cá nhân và tập thể (kèm dẫn chứng thực tế); đồng thời chỉ ra lợi ích tốt đẹp sẽ nhận được khi dũng cảm từ bỏ.
- Bước 3 (Giải pháp từ bỏ khả thi - Chia 3 cấp độ, mỗi phần đều phải lí giải vì sao làm vậy + có dẫn chứng):
  + Đối với Cá nhân (TRỌNG TÂM): Giải pháp tự nhận thức, thay đổi hành vi từng bước + lí giải vì sao + dẫn chứng.
  + Đối với Gia đình: Sự đồng hành, khích lệ, tạo môi trường + lí giải + dẫn chứng.
  + Đối với Nhà trường / Cộng đồng: Hoạt động định hướng, hỗ trợ + lí giải + dẫn chứng.
- Bước 4 (Dự đoán những ý kiến phản đối & Khuyên nhủ): Dự đoán lý lẽ bao biện của người mang thói quen/quan niệm đó (ví dụ: cho rằng thói quen vô hại hoặc quá khó bỏ) -> Phản biện nhẹ nhàng nhưng sắc bén và khẳng định vẫn cần kiên quyết từ bỏ.
- Kết bài: Khẳng định lại thông điệp tích cực và rút ra bài học liên hệ."""

    return ""

# ==============================================================================
# HÀM XÂY DỰNG KHUNG ĐỊNH HƯỚNG TƯ DUY ĐỘNG THEO ĐÚNG DẠNG BÀI
# ==============================================================================
def build_dynamic_outline_for_custom_topic(raw_topic_text, student_vdnl, manual_type_override="Tự động nhận diện theo đề bài"):
    formatted_topic = ensure_600_words_prompt(raw_topic_text)
    direct_problem = student_vdnl.strip() if student_vdnl.strip() else extract_clean_topic_noun(raw_topic_text)
    is_quote = is_metaphorical_quote_topic(raw_topic_text)
    type_code = classify_essay_type(raw_topic_text, direct_problem, manual_type_override)
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, raw_topic_text, direct_problem)

    explain_instruction = (
        "Vì đề bài nêu trực tiếp vấn đề, phần Giải thích cần cắt nghĩa tường minh khái niệm cốt lõi là gì."
        if not is_quote else
        "Vì đề bài có trích dẫn câu nói/nhận định/tác phẩm, phần Giải thích phải cắt nghĩa cả lớp nghĩa đen/hình ảnh ẩn dụ/ngữ liệu rồi rút ra nghĩa hàm ẩn."
    )

    prompt = f"""Đóng vai chuyên gia sư phạm Ngữ văn THPT. Hãy lập Khung định hướng tư duy chuẩn mực cho đề bài NLXH sau theo ĐÚNG DẠNG BÀI ĐÃ PHÂN LOẠI và trả về MỘT CHUỖI JSON HỢP LỆ (không dùng markdown code block):
- Đề bài: "{formatted_topic}"
- Vấn đề nghị luận trọng tâm: "{direct_problem}"
- Phân loại dạng bài: "{type_label}"

QUY CHUẨN CẤU TRÚC SƯ PHẠM BẮT BUỘC CỦA DẠNG BÀI NÀY:
{structure_guide}
- {explain_instruction}

Trả về JSON theo đúng các trường sau (nội dung bên trong phải tuân thủ tuyệt đối cấu trúc của dạng bài "{type_label}"):
{{
  "text": "{formatted_topic}",
  "vdnl_chuan": "{direct_problem}",
  "essay_type_code": "{type_code}",
  "essay_type_label": "{type_label}",
  "explain_items": [
    "- **Giải thích / Khởi điểm vấn đề:** (Viết chi tiết, chuẩn xác theo đúng dạng đề)..."
  ],
  "vdnl_ket_luan": "Câu chốt vấn đề nghị luận sắc bén",
  "questions": [
    {{
      "cau_hoi": "Hệ thống luận điểm triển khai Thân bài theo đúng cấu trúc '{type_label}':",
      "y_tra_loi": [
        "- **Bước / Luận điểm 1:** ...",
        "- **Bước / Luận điểm 2:** ...",
        "- **Bước / Luận điểm 3:** ...",
        "- **Bước / Luận điểm 4:** ...",
        "- **Bước / Luận điểm 5:** ..."
      ]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên nhân vật/sự kiện thực tế cụ thể",
      "chi_tiet": "Tóm tắt hành động tiêu biểu",
      "y_nghia": "Ý nghĩa chứng minh cho luận điểm/giải pháp",
      "nguon": "Thực tiễn đời sống"
    }}
  ],
  "counter": [
    "- **Phản đề / Ý kiến trái chiều / Dự đoán phản đối:** ...",
    "- **Phản biện khẳng định & Bài học liên hệ:** ..."
  ],
  "dani_chi_tiet": {{
    "mb": "Hướng dẫn Mở bài chuẩn theo dạng đề.",
    "gt": "Hướng dẫn phần Giải thích / Phân tích ngữ liệu.",
    "bl": "Hướng dẫn triển khai trọng tâm Thân bài (Bàn luận / Lí do & Giải pháp 3 cấp độ / Bảo vệ & Bác bỏ quan điểm).",
    "dc": "Hướng dẫn lồng ghép và phân tích dẫn chứng thực tế.",
    "pb": "Hướng dẫn phần Phản đề / Ý kiến khác / Dự đoán phản đối.",
    "kb": "Hướng dẫn Kết bài và rút ra bài học liên hệ."
  }}
}}"""

    ai_res = call_gemini_rest_api(prompt, temperature=0.35)
    if ai_res:
        try:
            match = re.search(r'\{.*\}', ai_res, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                parsed["text"] = formatted_topic
                parsed["essay_type_code"] = type_code
                parsed["essay_type_label"] = type_label
                if "explain_items" in parsed and "questions" in parsed:
                    return parsed
        except Exception:
            pass

    # BỘ MÁY SƯ PHẠM NỘI BỘ: TỰ ĐỘNG SINH DÀN Ý CHUẨN XÁC CHO TỪNG DẠNG TRONG 5 DẠNG + 3 TRƯỜNG HỢP
    combined_low = (raw_topic_text + " " + student_vdnl).lower()
    matched_concept = None
    for kw, data in CONCEPT_DICTIONARY.items():
        if kw in combined_low:
            matched_concept = (kw, data)
            break

    vdnl_final = direct_problem
    c_def = matched_concept[1]["def"] if matched_concept else f"**{vdnl_final}** là khái niệm/vấn đề phản ánh nhận thức, thái độ và cách ứng xử của con người trước những yêu cầu của đời sống cá nhân và cộng đồng."
    c_ev_ten = matched_concept[1]["ev_ten"] if matched_concept else "Biệt đội Sài Gòn Xanh, Dự án 'Nuôi Em' và những tấm gương người trẻ sống cống hiến, bản lĩnh"
    c_ev_chitiet = matched_concept[1]["ev_chitiet"] if matched_concept else "Những con người trẻ tuổi dám hành động thực chất, vượt qua khó khăn và định kiến để tạo ra giá trị tích cực, truyền cảm hứng mạnh mẽ cho xã hội."
    c_ev_ynghia = matched_concept[1]["ev_ynghia"] if matched_concept else f"Minh chứng thuyết phục cho giá trị thực tiễn và sức lan tỏa của {vdnl_final}."

    # --- DẠNG 2: VẤN ĐỀ CẦN GIẢI QUYẾT ---
    if type_code == "DANG_2_GIAI_QUYET":
        has_meaning = is_positive_topic_declining(raw_topic_text, vdnl_final)
        explain_items = [
            f"- **Giải thích vấn đề:** Làm rõ bản chất của **{vdnl_final}** là gì và biểu hiện nhận diện trong đời sống hiện nay.",
        ]
        if has_meaning:
            explain_items.append(f"- **Ý nghĩa vốn có của vấn đề (Vì đây là giá trị tốt đang có chiều hướng suy giảm):** Khẳng định vai trò quan trọng của **{vdnl_final}** đối với sự phát triển nhân cách và gắn kết cộng đồng trước khi chỉ ra thực trạng đáng lo ngại.")
        else:
            explain_items.append(f"- **Lưu ý cấu trúc:** Vì **{vdnl_final}** là vấn đề/hiện tượng tiêu cực trực tiếp, sau khi giải thích khái niệm, bài viết chuyển thẳng sang phân tích Lí do cần giải quyết (bỏ qua bước nêu ý nghĩa tích cực).")

        y_tra_loi_d2 = []
        if has_meaning:
            y_tra_loi_d2.append(f"- **1. Ý nghĩa của vấn đề:** Khẳng định giá trị tốt đẹp của **{vdnl_final}** khi được thực hiện đúng đắn, giúp cá nhân trưởng thành và tập thể gắn kết.")
        y_tra_loi_d2.extend([
            f"- **{'2' if has_meaning else '1'}. Lí do cần giải quyết (Viết thành 01 đoạn văn thống nhất gồm 3 ý):**\n  + *Thực trạng:* Chỉ ra mức độ phổ biến và những biểu hiện đáng báo động của vấn đề **{vdnl_final}** hiện nay.\n  + *Nguyên nhân:* Do nhận thức chủ quan của cá nhân (thiếu tự giác, chạy theo thói quen dễ dãi) và tác động khách quan từ môi trường gia đình, xã hội, mặt trái công nghệ.\n  + *Hậu quả:* Gây hệ lụy trực tiếp đến sức khỏe tinh thần, tương lai của cá nhân và làm suy giảm các giá trị bền vững của xã hội.",
            f"- **{'3' if has_meaning else '2'}. Giải pháp 1 — Đối với Cá nhân (Viết 01 đoạn văn):**\n  + *Giải pháp khả thi:* Chủ động nâng cao nhận thức, thiết lập kỷ luật bản thân và rèn luyện kỹ năng thực tế để làm chủ hành vi trước **{vdnl_final}**.\n  + *Lí giải vì sao:* Cá nhân là chủ thể trực tiếp quyết định mọi hành động; nếu tự thân không thay đổi thì mọi tác động bên ngoài đều vô nghĩa.\n  + *Dẫn chứng (ít nhất 01 dẫn chứng):* Các bạn trẻ tự lập kế hoạch học tập, chủ động cai nghiện mạng xã hội hoặc tham gia các dự án rèn luyện bản lĩnh thực tế.",
            f"- **{'4' if has_meaning else '3'}. Giải pháp 2 — Đối với Gia đình (Viết 01 đoạn văn):**\n  + *Giải pháp khả thi:* Cha mẹ làm gương, dành thời gian lắng nghe, đồng hành và định hướng con cái bằng sự thấu cảm thay vì áp đặt hay phó mặc.\n  + *Lí giải vì sao:* Gia đình là cái nôi đầu tiên hình thành thói quen và điểm tựa tâm lý vững chắc nhất của mỗi người.\n  + *Dẫn chứng (ít nhất 01 dẫn chứng):* Mô hình 'Giờ tối không thiết bị điện tử' và cùng đọc sách, trò chuyện của nhiều gia đình hiện đại.",
            f"- **{'5' if has_meaning else '4'}. Giải pháp 3 — Đối với Nhà trường & Xã hội (Viết 01 đoạn văn):**\n  + *Giải pháp khả thi:* Nhà trường đổi mới hoạt động trải nghiệm, tư vấn tâm lý học đường; xã hội và truyền thông lan tỏa các chiến dịch tích cực, hoàn thiện chế tài quản lý.\n  + *Lí giải vì sao:* Môi trường giáo dục và cộng đồng lành mạnh sẽ tạo hành lang hỗ trợ bền vững để cá nhân duy trì thói quen tốt.\n  + *Dẫn chứng (ít nhất 01 dẫn chứng):* Các chương trình 'Trường học hạnh phúc', chiến dịch 'Sài Gòn Xanh' hay các câu lạc bộ kỹ năng sống tại trường THPT."
        ])

        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": explain_items,
            "vdnl_ket_luan": f"Từ thực tiễn đó, việc nhận diện thấu đáo và tìm ra giải pháp khắc phục triệt để cho vấn đề **{vdnl_final}** là yêu cầu cấp thiết.",
            "questions": [{"cau_hoi": f"Khung triển khai Thân bài dạng Vấn đề cần giải quyết ({vdnl_final}):", "y_tra_loi": y_tra_loi_d2}],
            "evidence": [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": "Đưa vào các đoạn Giải pháp (Cá nhân / Gia đình / Nhà trường) để chứng minh tính khả thi.", "nguon": "Thực tiễn đời sống xã hội"}],
            "counter": [
                f"- **Ý kiến khác (Trái chiều):** Có ý kiến cho rằng vấn đề **{vdnl_final}** chỉ là chuyện nhỏ của cá nhân hoặc là xu thế tất yếu của thời đại nên không cần tốn công sức giải quyết.",
                f"- **Phản biện & Khẳng định:** Bác bỏ suy nghĩ chủ quan, buông xuôi đó; khẳng định nếu không kiên quyết khắc phục ngay từ hôm nay thì hệ lụy tích tụ sẽ hủy hoại tương lai người trẻ."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt từ bối cảnh thời đại -> Nêu trực diện vấn đề cần giải quyết: {vdnl_final}.",
                "gt": f"Giải thích rõ khái niệm/vấn đề {'+ Nêu ý nghĩa vốn có của vấn đề' if has_meaning else '(Bỏ qua bước ý nghĩa vì là hiện tượng tiêu cực trực tiếp)'}.",
                "bl": "1. Đoạn Lí do cần giải quyết (Thực trạng - Nguyên nhân - Hậu quả).\n2. Ba đoạn Giải pháp tách biệt: Cá nhân - Gia đình - Nhà trường (Mỗi đoạn đủ: Giải pháp khả thi + Lí giải vì sao + 01 Dẫn chứng).",
                "dc": "Lồng ghép trực tiếp ít nhất 01 dẫn chứng thực tế vào mỗi đoạn giải pháp.",
                "pb": "Nêu ý kiến khác cho rằng không cần thiết -> Phản biện lại và khẳng định vẫn cần phải khắc phục.",
                "kb": f"Khẳng định lại tầm quan trọng của việc giải quyết {vdnl_final} và liên hệ hành động bản thân."
            }
        }

    # --- DẠNG 3: LỰA CHỌN QUAN ĐIỂM ---
    if type_code == "DANG_3_HAI_QUAN_DIEM":
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **Giải thích Quan điểm 1:** Làm rõ nội hàm, cơ sở hình thành và thông điệp của quan điểm thứ nhất trong đề bài.",
                f"- **Giải thích Quan điểm 2:** Làm rõ nội hàm, góc nhìn và thông điệp của quan điểm thứ hai.",
                f"- **Chỉ ra mối quan hệ giữa 2 quan điểm:** Phân tích xem 2 quan điểm đối lập nhau hoàn toàn hay là hai lát cắt bổ sung cho nhau trong những hoàn cảnh khác nhau."
            ],
            "vdnl_ket_luan": f"Đứng trước hai góc nhìn trên về **{vdnl_final}**, người viết cần xác lập rõ quan điểm lựa chọn của mình và bảo vệ bằng lý lẽ thuyết phục.",
            "questions": [{
                "cau_hoi": f"Khung triển khai Thân bài dạng Lựa chọn quan điểm ({vdnl_final}):",
                "y_tra_loi": [
                    "- **1. Giải thích 2 quan điểm & Mối quan hệ:** Cắt nghĩa từng quan điểm và chỉ rõ điểm giao thoa hoặc khác biệt giữa chúng.",
                    "- **2. Lí giải vì sao chọn quan điểm của mình (Trọng tâm):** Đưa ra các luận cứ sắc bén chứng minh tính đúng đắn, phù hợp và giá trị tích cực của quan điểm mình lựa chọn đối với sự phát triển của cá nhân và xã hội.",
                    "- **3. Phân tích Dẫn chứng chứng minh:** Đưa dẫn chứng người thật việc thật tiêu biểu để bảo vệ vững chắc cho quan điểm đã chọn.",
                    "- **4. Chỉ ra hạn chế của quan điểm còn lại:** Phân tích khách quan những điểm phiến diện, bất cập hoặc rủi ro nếu con người tuyệt đối hóa quan điểm còn lại.",
                    "- **5. Bài học khái quát & Bài học liên hệ:** Rút ra quy luật ứng xử linh hoạt trong cuộc sống và bài học hành động cho bản thân."
                ]
            }],
            "evidence": [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": "Chứng minh sức thuyết phục cho quan điểm mà học sinh đã lựa chọn.", "nguon": "Thực tiễn đời sống"}],
            "counter": [
                "- **Chỉ ra hạn chế của quan điểm không chọn:** Phân tích vì sao quan điểm kia chưa tối ưu hoặc dễ dẫn đến sự cực đoan trong thực tế.",
                "- **Bài học nhận thức khái quát:** Biết giữ vững lập trường đúng đắn nhưng đồng thời có cái nhìn biện chứng, tôn trọng sự đa dạng của tư duy."
            ],
            "dani_chi_tiet": {
                "mb": "Giới thiệu 2 quan điểm trong đề bài + Chỉ ra rõ ràng quan điểm lựa chọn của bản thân.",
                "gt": "Giải thích lần lượt 2 quan điểm và chỉ ra mối quan hệ giữa chúng.",
                "bl": "Lí giải sâu sắc vì sao chọn quan điểm của mình + Chỉ ra những hạn chế của quan điểm còn lại.",
                "dc": "Phân tích dẫn chứng thực tế để bảo vệ quan điểm đã chọn.",
                "pb": "Rút ra bài học khái quát từ sự đối sánh hai quan điểm.",
                "kb": "Khẳng định lại sự lựa chọn và nêu bài học liên hệ cá nhân."
            }
        }

    # --- DẠNG 4: VẤN ĐỀ XÃ HỘI RÚT RA TỪ TÁC PHẨM VĂN HỌC ---
    if type_code == "DANG_4_VAN_HOC":
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **Bước 1 — Phân tích ngắn gọn ngữ liệu văn học:** Khái quát nội dung, tình huống hoặc hình tượng nhân vật trong tác phẩm/đoạn trích để rút ra thông điệp, vấn đề xã hội: **{vdnl_final}**.",
                f"- **Bước 2 — Giải thích vấn đề xã hội:** Cắt nghĩa khái niệm, bản chất của **{vdnl_final}** khi bước ra khỏi trang sách để đi vào đời sống xã hội."
            ],
            "vdnl_ket_luan": f"Từ hình tượng nghệ thuật trong tác phẩm, một vấn đề nhân sinh và xã hội sâu sắc được đặt ra là: **{vdnl_final}**.",
            "questions": [{
                "cau_hoi": f"Khung triển khai Thân bài dạng Vấn đề xã hội rút ra từ tác phẩm văn học ({vdnl_final}):",
                "y_tra_loi": [
                    "- **1. Chuyển giao từ Văn học sang Đời sống:** Phân tích ngắn gọn (khoảng 1 đoạn) ý nghĩa ngữ liệu văn học để gọi tên chính xác vấn đề xã hội.",
                    f"- **2. Giải thích vấn đề xã hội:** Làm rõ bản chất của **{vdnl_final}** trong thực tiễn cuộc sống.",
                    f"- **3. Bàn luận biểu hiện & Ý nghĩa thực tiễn:** Phân tích các biểu hiện sinh động và vai trò, tác động của **{vdnl_final}** đối với con người và xã hội đương đại.",
                    "- **4. Dẫn chứng thực tế đời sống:** Lấy dẫn chứng người thật, việc thật ngoài xã hội (không lấy lại dẫn chứng trong văn học) để làm sáng tỏ vấn đề.",
                    "- **5. Phản đề, Mở rộng & Bài học liên hệ:** Phê phán các biểu hiện trái ngược, khẳng định giá trị thức tỉnh của văn chương đối với cuộc đời và rút ra bài học cho tuổi trẻ."
                ]
            }],
            "evidence": [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": "Dẫn chứng thực tế đời sống làm sáng tỏ thông điệp xã hội rút ra từ tác phẩm.", "nguon": "Thực tiễn đời sống"}],
            "counter": [
                f"- **Phê phán & Mở rộng:** Lên án những biểu hiện đi ngược lại giá trị nhân văn mà tác phẩm đã cảnh báo/khơi gợi.",
                "- **Bài học nhận thức và hành động:** Biết soi chiếu bản thân qua trang sách để sống nhân ái, bản lĩnh và trách nhiệm hơn."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt từ tác giả, tác phẩm -> Nêu vấn đề xã hội rút ra từ tác phẩm: {vdnl_final}.",
                "gt": "Phân tích ngắn gọn khía cạnh văn học để rút ra vấn đề -> Giải thích khái niệm vấn đề xã hội đó.",
                "bl": f"Bàn luận sâu sắc về biểu hiện, ý nghĩa và tác động của {vdnl_final} trong đời sống xã hội hôm nay.",
                "dc": "Phân tích dẫn chứng thực tế ngoài đời sống xã hội.",
                "pb": "Phản đề, mở rộng góc nhìn và nêu bài học nhận thức, hành động.",
                "kb": "Khẳng định sức sống lâu bền của thông điệp từ tác phẩm văn học trong cuộc sống và liên hệ bản thân."
            }
        }

    # --- DẠNG 5: THUYẾT PHỤC NGƯỜI KHÁC TỪ BỎ MỘT THÓI QUEN HAY QUAN NIỆM ---
    if type_code == "DANG_5_TU_BO":
        return {
            "text": formatted_topic,
            "vdnl_chuan": vdnl_final,
            "essay_type_code": type_code,
            "essay_type_label": type_label,
            "explain_items": [
                f"- **Giải thích thói quen / quan niệm:** Làm rõ bản chất của thói quen/quan niệm (**{vdnl_final}**) là gì.",
                f"- **Biểu hiện thực tế:** Chỉ ra những biểu hiện cụ thể, phổ biến của thói quen/quan niệm này trong suy nghĩ, lời nói và hành động hàng ngày của một bộ phận giới trẻ/con người hiện nay."
            ],
            "vdnl_ket_luan": f"Nhận diện rõ những hệ lụy âm thầm nhưng nặng nề ấy, mỗi chúng ta cần dũng cảm từ bỏ **{vdnl_final}** để hướng tới lối sống tích cực hơn.",
            "questions": [{
                "cau_hoi": f"Khung triển khai Thân bài dạng Thuyết phục từ bỏ thói quen/quan niệm ({vdnl_final}):",
                "y_tra_loi": [
                    f"- **1. Giải thích & Biểu hiện:** Gọi tên rõ bản chất và các biểu hiện thường gặp của **{vdnl_final}**.",
                    f"- **2. Lí do vì sao phải từ bỏ (Hậu quả + Dẫn chứng + Lợi ích khi từ bỏ):**\n  + *Hậu quả:* Phân tích tác hại trực tiếp đến sức khỏe, thời gian, nhân cách, cơ hội phát triển của cá nhân và ảnh hưởng xấu đến người xung quanh (kèm dẫn chứng thực tế).\n  + *Lợi ích khi từ bỏ:* Chỉ ra sự thay đổi tích cực, tự do và trưởng thành khi thoát khỏi thói quen/quan niệm sai lầm đó.",
                    "- **3. Giải pháp từ bỏ — Đối với Cá nhân (TRỌNG TÂM):** Đưa ra các bước hành động cụ thể để tự thay đổi (nhận diện nguyên nhân, chia nhỏ mục tiêu, thay thế bằng thói quen tích cực) + Lí giải vì sao phải làm vậy + Dẫn chứng thực tế.",
                    "- **4. Giải pháp phối hợp — Đối với Gia đình & Nhà trường:**\n  + *Gia đình:* Thấu hiểu, khích lệ và đồng hành thay vì chỉ trích nặng lời + Lí giải vì sao + Dẫn chứng.\n  + *Nhà trường/Tập thể:* Tạo môi trường hoạt động lành mạnh, truyền cảm hứng tích cực + Lí giải vì sao + Dẫn chứng.",
                    "- **5. Dự đoán những ý kiến phản đối & Khuyên nhủ thuyết phục:** Dự đoán lời biện minh của người mang thói quen/quan niệm đó (cho rằng 'ai cũng vậy' hoặc 'không ảnh hưởng đến ai') -> Phân tích thấu tình đạt lý để khuyên họ kiên quyết từ bỏ."
                ]
            }],
            "evidence": [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": "Sử dụng làm minh chứng cho phần Hậu quả và phần Giải pháp vượt qua thói quen/định kiến.", "nguon": "Thực tiễn đời sống"}],
            "counter": [
                "- **Dự đoán ý kiến phản đối:** Có người có thể phản đối rằng thói quen/quan niệm này đã ăn sâu vào tính cách hoặc chỉ là sở thích cá nhân vô hại.",
                "- **Phản biện & Khuyên nhủ:** Dùng lý lẽ chân thành chỉ rõ nếu cứ dung túng cho những điều lệch lạc nhỏ sẽ dẫn đến sự tụt hậu lớn; từ đó khẳng định việc từ bỏ là hoàn toàn cần thiết và khả thi."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt chân thành -> Nêu rõ thói quen/quan niệm cần thuyết phục từ bỏ: {vdnl_final}.",
                "gt": "Giải thích thói quen/quan niệm -> Nêu các biểu hiện cụ thể trong đời sống.",
                "bl": "1. Lí do phải từ bỏ (Phân tích hậu quả + Dẫn chứng + Lợi ích khi từ bỏ).\n2. Giải pháp từ bỏ khả thi ở 3 cấp độ: Cá nhân (Trọng tâm) - Gia đình - Nhà trường (Đều có lí giải vì sao + dẫn chứng).",
                "dc": "Đưa dẫn chứng thực tế vào cả phần Hậu quả và phần Giải pháp.",
                "pb": "Dự đoán những ý kiến phản đối/biện minh -> Phản biện và khuyên vẫn cần kiên quyết từ bỏ.",
                "kb": "Khẳng định lại thông điệp khích lệ thay đổi và rút ra bài học liên hệ bản thân."
            }
        }

    # --- DẠNG 1 (TƯ TƯỞNG, ĐẠO LÍ) CHIA 3 TRƯỜNG HỢP: TH1, TH2, TH3 ---
    explain_list = (
        [f"- **Giải thích khái niệm:** {c_def}", f"- **Chốt trọng tâm đề bài:** Định hướng suy ngẫm trực diện vào **{vdnl_final}**."]
        if not is_quote else
        [f"- **Giải thích câu nói/nhận định:** Cắt nghĩa lớp nghĩa tường minh (từ ngữ, hình ảnh ẩn dụ) và rút ra nghĩa hàm ẩn của nhận định.", f"- **Bản chất tư tưởng:** {c_def}"]
    )

    if type_code == "DANG_1_TH1":
        y_list = [
            f"- **Luận điểm 1 (Bàn sâu ý nghĩa đối với nhận thức & nội lực cá nhân):** **{vdnl_final}** chính là nguồn sức mạnh nội sinh giúp con người định hình bản lĩnh, vượt qua giới hạn và vững vàng trước nghịch cảnh.",
            f"- **Luận điểm 2 (Giá trị bồi đắp nhân cách & tâm hồn):** Nuôi dưỡng chiều sâu tâm hồn, giúp mỗi người sống có lý tưởng, có giá trị thực chất và không bị cuốn theo những điều phù phiếm.",
            f"- **Luận điểm 3 (Vai trò kết nối giữa người với người):** Tạo dựng niềm tin, sự thấu hiểu và truyền cảm hứng tích cực tới những người xung quanh.",
            f"- **Luận điểm 4 (Sức mạnh thúc đẩy cộng đồng, xã hội):** Khi giá trị này được lan tỏa rộng rãi, nó trở thành động lực kiến tạo một xã hội văn minh, nhân ái và tiến bộ.",
            f"- **Luận điểm 5 (Lý giải bằng góc nhìn ngược lại - Hệ lụy nếu thiếu vắng):** Nếu đánh mất giá trị này, cá nhân dễ rơi vào bế tắc, phương hướng sống mờ nhạt và xã hội thiếu đi điểm tựa phát triển."
        ]
        bl_summary = "Tập trung bàn thật sâu các tầng Ý NGHĨA, VAI TRÒ, SỨC MẠNH của vấn đề đối với cá nhân, mối quan hệ con người và xã hội."
    elif type_code == "DANG_1_TH2":
        y_list = [
            f"- **Luận điểm 1 (Khái quát sự cần thiết phải hành động):** Khẳng định ngắn gọn tầm quan trọng của vấn đề để làm rõ vì sao chủ thể cần nhận thức rõ trách nhiệm của mình.",
            f"- **Luận điểm 2 (Bài học giải pháp về Nhận thức & Tư duy - Cần hiểu thế nào?):** Chủ động nâng cao nhận thức, xác lập mục tiêu sống đúng đắn, vượt qua sự thờ ơ hay tâm lý ỷ lại.",
            f"- **Luận điểm 3 (Bài học giải pháp về Hành động rèn luyện cá nhân - Cần làm gì?):** Không ngừng trau dồi tri thức, kỹ năng và hiện thực hóa bằng những việc làm kiên trì, thiết thực mỗi ngày.",
            f"- **Luận điểm 4 (Bài học giải pháp trong Gắn kết & Cống hiến cộng đồng):** Đặt trách nhiệm của bản thân trong sự phát triển chung của gia đình, nhà trường và đất nước; lan tỏa năng lượng tích cực.",
            f"- **Luận điểm 5 (Rèn luyện bản lĩnh vượt rào cản khi thực hiện):** Kiên định trước khó khăn, cám dỗ để biến nhận thức thành kết quả thực chất chứ không dừng ở khẩu hiệu."
        ]
        bl_summary = "Trọng tâm trả lời câu hỏi CẦN LÀM GÌ? (Hệ thống các bài học giải pháp về nhận thức, hành động cá nhân và trách nhiệm cộng đồng)."
    else: # DANG_1_TH3
        y_list = [
            f"- **1. Biểu hiện của vấn đề:** Chỉ ra những biểu hiện sinh động, cụ thể của **{vdnl_final}** trong suy nghĩ, thái độ và hành động thực tế giữa đời sống.",
            f"- **2. Bàn luận — Nêu ý nghĩa đối với cá nhân:** Giúp con người hoàn thiện nhân cách, khơi dậy tiềm năng và tạo điểm tựa vượt qua thử thách.",
            f"- **3. Bàn luận — Nêu ý nghĩa đối với cộng đồng, xã hội:** Góp phần lan tỏa những giá trị tốt đẹp, gắn kết con người và thúc đẩy xã hội phát triển.",
            f"- **4. Cần làm gì để phát huy (Bài học định hướng):** Xác định rõ những việc cần làm về cả nhận thức lẫn hành động thực tế để nuôi dưỡng và phát huy **{vdnl_final}**.",
            f"- **5. Liên hệ cá nhân sâu sắc:** Soi chiếu vào trải nghiệm và hành trình rèn luyện của chính bản thân người viết."
        ]
        bl_summary = "Triển khai tuần tự: Biểu hiện -> Bàn luận nêu ý nghĩa -> Dẫn chứng -> Cần làm gì để phát huy (bài học) -> Liên hệ cá nhân."

    return {
        "text": formatted_topic,
        "vdnl_chuan": vdnl_final,
        "essay_type_code": type_code,
        "essay_type_label": type_label,
        "explain_items": explain_list,
        "vdnl_ket_luan": f"Qua đó, đề bài định hướng chúng ta bàn luận sâu sắc về: **{vdnl_final}**.",
        "questions": [{"cau_hoi": f"Hệ thống luận điểm Thân bài ({type_label}):", "y_tra_loi": y_list}],
        "evidence": [{"ten": c_ev_ten, "chi_tiet": c_ev_chitiet, "y_nghia": c_ev_ynghia, "nguon": "Thực tiễn đời sống xã hội"}],
        "counter": [
            f"- **Phê phán biểu hiện lệch lạc:** Lên án những biểu hiện sống hời hợt, ích kỷ, đi ngược lại giá trị của **{vdnl_final}**.",
            f"- **Mở rộng biện chứng & Liên hệ:** Nhìn nhận vấn đề toàn diện, tránh cực đoan hoặc giáo điều hình thức; rút ra bài học thiết thực cho bản thân."
        ],
        "dani_chi_tiet": {
            "mb": f"Dẫn dắt tự nhiên -> Trích dẫn đề bài -> Nêu vấn đề nghị luận: {vdnl_final}.",
            "gt": "Giải thích khái niệm hoặc thông điệp câu nói.",
            "bl": bl_summary,
            "dc": "Đưa dẫn chứng người thật việc thật và phân tích gắn kết với luận điểm.",
            "pb": "Phản đề (phê phán biểu hiện ngược lại, mở rộng góc nhìn) và liên hệ cá nhân.",
            "kb": f"Khẳng định lại giá trị của {vdnl_final} và thông điệp kết bài."
        }
    }

def is_ghostwriting_request(q_low):
    ghost_patterns = [
        r"viết\s*(hộ|giùm|giúp|cho|luôn|mẫu|thay)",
        r"(cô|ai|hệ thống|bạn)\s*viết\s*(bài|đoạn|giúp|cho|hộ|luôn)",
        r"làm\s*(hộ|giùm|giúp|cho)\s*(em|tôi|mình)?\s*(bài|đoạn)?",
        r"cho\s*(em|tôi|mình)\s*(xin\s*)?(một\s*)?(bài\s*văn|đoạn\s*văn|bài\s*làm|bài\s*mẫu)",
        r"viết\s*(cả\s*bài|bài\s*văn|hoàn\s*chỉnh|thành\s*bài)",
        r"^viết\s*bài(\s*cho\s*em|\s*đi|\s*nhé|\s*với)?$",
        r"soạn\s*(hộ|giúp|cho)\s*bài"
    ]
    for pat in ghost_patterns:
        if re.search(pat, q_low):
            return True
    return False

# ==============================================================================
# HÀM TRỢ LÝ TƯ VẤN SƯ PHẠM ĐA LƯỢT - NHẠY BÉN, LINH HOẠT, KHÔNG BAO GIỜ LẶP LẠI 1 CÂU
# ==============================================================================
def generate_deep_chat_response(user_q, cur_de_info, chat_history_list):
    q_clean = user_q.strip()
    q_low = q_clean.lower()
    topic_text = ensure_600_words_prompt(cur_de_info.get("text", ""))
    vdnl = cur_de_info.get("vdnl_chuan", "vấn đề nghị luận của đề bài")
    type_code = cur_de_info.get("essay_type_code", classify_essay_type(topic_text, vdnl, st.session_state.get("selected_essay_type_override", "Tự động nhận diện theo đề bài")))
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, topic_text, vdnl)
    current_draft = st.session_state.get("user_essay", "").strip()

    # 1. Nhận diện nhạy bén nếu học sinh yêu cầu viết hộ nhưng gợi mở theo đúng phần học sinh đang cần
    if is_ghostwriting_request(q_low):
        part_hint = "Mở bài" if "mở bài" in q_low else ("Kết bài" if "kết bài" in q_low else ("đoạn Phản đề" if "phản đề" in q_low else "đoạn văn"))
        return (
            f"👩‍🏫 **Trợ lý Ngữ văn:** Cô không viết sẵn bài văn hay {part_hint} hoàn chỉnh thay cho em nhé, vì tự tay diễn đạt mới giúp em làm chủ tư duy! "
            f"Tuy nhiên, để em viết {part_hint} cho đề **{vdnl}** (*{type_label}*) thật nhanh và trúng ý, cô gợi ý ngay công thức nối câu cho em:\n"
            f"- **Câu mở đoạn:** Nêu trực diện luận điểm chính gắn với từ khóa *{vdnl}*.\n"
            f"- **Câu triển khai:** Dùng các cụm từ lập luận (*Bởi lẽ..., Thực tế cho thấy..., Chính điều này đã...*) để làm rõ lý do/biểu hiện.\n"
            f"👉 *Em hãy viết thử 1-2 câu nháp theo ý của em vào đây, cô sẽ đọc và chuốt lại câu chữ cho em ngay lập tức!*"
        )

    # 2. GỌI GEMINI API VỚI LỊCH SỬ ĐA LƯỢT + SYSTEM INSTRUCTION CHUYÊN SÂU THEO ĐÚNG DẠNG BÀI
    system_instruction_text = f"""Bạn là một giáo viên Ngữ văn THPT giỏi chuyên môn, nhạy bén và tận tâm, đang trực tiếp hướng dẫn học sinh viết bài Nghị luận xã hội (khoảng 600 chữ).
THÔNG TIN ĐỀ BÀI ĐANG LÀM:
- Đề bài: "{topic_text}"
- Vấn đề nghị luận trọng tâm: "{vdnl}"
- Phân loại dạng đề và cấu trúc chuẩn:
{structure_guide}
- Bản nháp học sinh đang viết (nếu có): "{current_draft[:600] if current_draft else 'Chưa viết'}"

QUY TẮC PHẢN HỒI BẮT BUỘC:
1. LINH HOẠT, NHẠY BÉN, TRẢ LỜI ĐÚNG TRỌNG TÂM: Đọc kỹ câu hỏi mới nhất của học sinh và toàn bộ lịch sử trò chuyện trước đó. Học sinh hỏi khía cạnh nào (mở bài, giải thích, thêm dẫn chứng khác, cách phân tích dẫn chứng, cách viết giải pháp cá nhân/gia đình/nhà trường, cách phản đề, cách dùng từ, hay hỏi tiếp "còn gì nữa không", "em chưa hiểu ý số 2"...), hãy giải đáp xoáy sâu vào ĐÚNG khía cạnh đó.
2. TUYỆT ĐỐI KHÔNG LẶP LẠI CÂU TRẢ LỜI CŨ: Nếu ở lượt trước đã gợi ý một ý/dẫn chứng mà học sinh hỏi thêm, phải cung cấp góc nhìn mới, dẫn chứng mới, mẫu câu diễn đạt mới hoặc phân tích sâu hơn. Không bao giờ trả lời máy móc bằng cách chép lại dàn ý chung.
3. BÁM SÁT ĐÚNG DẠNG BÀI: Mọi hướng dẫn về luận điểm, dẫn chứng, phản đề phải khớp với cấu trúc của dạng bài "{type_label}" ở trên.
4. Không viết hộ toàn bộ bài văn hoàn chỉnh, nhưng được phép đưa ra các cụm từ đắt giá, mẫu câu chuyển đoạn hoặc sửa trực tiếp câu văn nháp của học sinh."""

    contents_payload = []
    recent_history = chat_history_list[-10:] if len(chat_history_list) > 10 else chat_history_list
    for role, msg in recent_history:
        clean_msg = re.sub(r'^👩‍🏫 \*\*Trợ lý Ngữ văn:\*\*\s*', '', msg).strip()
        if role == "user":
            contents_payload.append({"role": "user", "parts": [{"text": clean_msg}]})
        elif role == "assistant" and clean_msg:
            contents_payload.append({"role": "model", "parts": [{"text": clean_msg}]})

    # Đảm bảo lượt đầu tiên trong contents là "user" theo chuẩn Gemini REST API
    while contents_payload and contents_payload[0]["role"] == "model":
        contents_payload.pop(0)

    contents_payload.append({"role": "user", "parts": [{"text": q_clean}]})

    ai_reply = call_gemini_rest_api(
        prompt="",
        contents_list=contents_payload,
        system_instruction=system_instruction_text,
        temperature=0.55
    )
    if ai_reply and len(ai_reply.strip()) > 20:
        return ai_reply

    # ==========================================================================
    # 3. BỘ MÁY PHẢN HỒI SƯ PHẠM NỘI BỘ ĐA TẦNG (KHI CHƯA NHẬP API KEY HOẶC LỖI MẠNG)
    # Tự động theo dõi ngữ cảnh từng lượt hỏi để mỗi lần hỏi đều có câu trả lời mới, sâu sắc!
    # ==========================================================================
    explain_list = cur_de_info.get("explain_items", [])
    questions_list = cur_de_info.get("questions", [])
    counter_list = cur_de_info.get("counter", [])

    # Xác định chủ đề của câu hỏi trước đó (nếu học sinh hỏi nối tiếp: "còn gì nữa không", "cho thêm đi", "sâu hơn", "cách khác")
    last_user_q = ""
    for r, m in reversed(chat_history_list):
        if r == "user":
            last_user_q = m.lower()
            break
    is_followup = any(w in q_low for w in ["thêm", "khác", "nữa", "sâu hơn", "cụ thể hơn", "chưa hiểu", "rõ hơn", "ví dụ", "còn gì", "ý 2", "ý 3", "đoạn 2", "tiếp"])
    effective_query = (last_user_q + " " + q_low) if (is_followup and len(q_low.split()) <= 10) else q_low

    # Đếm số lần học sinh đã hỏi về cùng một khía cạnh để xoay vòng góc độ tư vấn (tránh trả lời 1 câu duy nhất)
    def count_previous_topic_asks(keywords):
        cnt = 0
        for r, m in chat_history_list:
            if r == "user" and any(k in m.lower() for k in keywords):
                cnt += 1
        return cnt

    # Trích xuất toàn bộ dẫn chứng từ Kho 9 chủ điểm để làm nguồn dẫn chứng vô tận
    all_repo_evidences = []
    try:
        for topic_name, dc_list in db.KHO_DAN_CHUNG_9_CHU_DIEM.items():
            for item in dc_list:
                all_repo_evidences.append((topic_name, item))
    except Exception:
        pass

    # --- NHÁNH A: HỎI VỀ DẪN CHỨNG (Mỗi lần hỏi đưa ra các dẫn chứng mới + cách phân tích mới) ---
    ev_keywords = ["dẫn chứng", "ví dụ", "nhân vật", "tấm gương", "người thật", "minh họa", "chứng minh"]
    if any(k in effective_query for k in ev_keywords):
        ask_idx = count_previous_topic_asks(ev_keywords)
        cur_evs = cur_de_info.get("evidence", [])
        
        if ask_idx == 0 and cur_evs:
            ev0 = cur_evs[0]
            extra_ev = all_repo_evidences[0][1] if all_repo_evidences else {"ten": "Dự án Nuôi Em & Biệt đội Sài Gòn Xanh", "noi_dung": "Những người trẻ hành động thiết thực vì cộng đồng.", "nguon": "Báo chí chính thống"}
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Đối với đề bài về **\"{vdnl}\"** (*{type_label}*), cô gợi ý cho em 2 dẫn chứng tiêu biểu kèm cách đưa vào bài:
1. **Dẫn chứng trọng tâm: {ev0.get('ten', '')}**
   - *Sự việc cốt lõi:* {ev0.get('chi_tiet', '')}
   - *Cách phân tích gắn với luận điểm:* {ev0.get('y_nghia', '')}
2. **Dẫn chứng mở rộng: {extra_ev.get('ten', '')}**
   - *Chi tiết:* {extra_ev.get('noi_dung', '')}
💡 **Công thức viết đoạn dẫn chứng (3 câu - không sa vào kể lể):**
- *Câu 1 (Dẫn dắt):* Thực tiễn cuộc sống đã ghi nhận biết bao câu chuyện lay động về {vdnl}, mà tiêu biểu là...
- *Câu 2 (Khái quát hành động):* Nêu ngắn gọn hành động/sự kiện đắt giá nhất của nhân vật.
- *Câu 3 (Bình luận chốt ý):* Chính hành trình ấy là minh chứng sống động nhất khẳng định rằng...
*(Nếu em muốn lấy dẫn chứng ở lĩnh vực khác như khoa học, thể thao, lịch sử hay đời sống giới trẻ, em cứ nhắn "cho em thêm dẫn chứng khác" nhé!)*"""
        else:
            # Lượt hỏi thứ 2, 3, 4... về dẫn chứng: xoay vòng từ kho 9 chủ điểm
            if all_repo_evidences:
                idx1 = (ask_idx * 2) % len(all_repo_evidences)
                idx2 = (ask_idx * 2 + 1) % len(all_repo_evidences)
                t1, dc1 = all_repo_evidences[idx1]
                t2, dc2 = all_repo_evidences[idx2]
                return f"""👩‍🏫 **Trợ lý Ngữ văn:** Cô cung cấp thêm cho em **2 dẫn chứng mới** ở góc nhìn khác để bài viết về **\"{vdnl}\"** tránh lối mòn nhé:
1. **{dc1['ten']}** *(Chủ điểm: {t1})*
   - *Nội dung:* {dc1['noi_dung']}
   - *Cách lồng ghép vào đề \"{vdnl}\":* Em có thể dùng câu dẫn: *"Nhìn từ câu chuyện của {dc1['ten']}, ta càng thấm thía cách mà {vdnl} được chuyển hóa thành hành động thực tế..."*
2. **{dc2['ten']}** *(Chủ điểm: {t2})*
   - *Nội dung:* {dc2['noi_dung']}
   - *Nguồn dẫn:* {dc2['nguon']}
👉 *Trong trường hợp bài viết của em thuộc dạng Giải pháp (Cá nhân - Gia đình - Nhà trường), em hãy chia mỗi dẫn chứng ngắn gọn (1-2 câu) đặt ngay sau phần lí giải của từng giải pháp để đạt điểm tối đa nhé!*"""
            else:
                return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để làm mới dẫn chứng cho đề **\"{vdnl}\"**, ngoài các nhân vật nổi tiếng, em có thể kết hợp **Dẫn chứng diện (số liệu/thực trạng chung)** và **Dẫn chứng điểm (1 cá nhân tiêu biểu)**:
- *Câu nêu diện:* Từ những chiến dịch tình nguyện mùa hè xanh của sinh viên cho đến những nhóm nghiên cứu khoa học trẻ trên khắp cả nước...
- *Câu nêu điểm:* Đặc biệt, hình ảnh... đã cho thấy sức mạnh thực chất của {vdnl}."""

    # --- NHÁNH B: HỎI VỀ PHẢN ĐỀ / Ý KIẾN TRÁI CHIỀU / DỰ ĐOÁN PHẢN ĐỐI ---
    pb_keywords = ["phản đề", "phản biện", "mở rộng", "lật lại", "phê phán", "ý kiến khác", "trái chiều", "phản đối"]
    if any(k in effective_query for k in pb_keywords):
        ask_idx = count_previous_topic_asks(pb_keywords)
        pb_content = "\n".join(counter_list) if counter_list else f"- Phê phán biểu hiện thiếu **{vdnl}** và mở rộng góc nhìn biện chứng."
        
        if ask_idx == 0:
            if type_code == "DANG_2_GIAI_QUYET":
                return f"""👩‍🏫 **Trợ lý Ngữ văn:** Với **Dạng bài Vấn đề cần giải quyết** (*{vdnl}*), phần cuối Thân bài không chỉ phê phán thông thường mà cần thực hiện thao tác **Nêu ý kiến khác & Phản biện**:
1. **Nêu ý kiến khác:** Em giả định một luồng suy nghĩ cho rằng: *"Có người cho rằng {vdnl} chỉ là chuyện cá nhân hoặc là xu thế tất yếu không thể thay đổi, nên việc tìm giải pháp là không cần thiết."*
2. **Phản biện lại:** Em dùng lý lẽ bác bỏ: *"Đây là cái nhìn phiến diện và buông xuôi. Bởi nếu mỗi cá nhân, gia đình và nhà trường đều thờ ơ, hệ lụy của nó sẽ trực tiếp kìm hãm sự phát triển chung. Do đó, việc kiên trì khắc phục là hoàn toàn cấp thiết."*"""
            elif type_code == "DANG_5_TU_BO":
                return f"""👩‍🏫 **Trợ lý Ngữ văn:** Với **Dạng bài Thuyết phục từ bỏ thói quen/quan niệm** (*{vdnl}*), phần này là **Dự đoán ý kiến phản đối và Khuyên nhủ**:
1. **Dự đoán lý lẽ bao biện:** *"Có thể bạn sẽ nghĩ rằng thói quen/quan niệm này chẳng gây hại cho ai, hoặc đã quen rồi nên rất khó thay đổi..."*
2. **Thuyết phục ngược lại:** *"Thế nhưng, chính sự thỏa hiệp từng chút một ấy lại đang âm thầm lấy đi thời gian, cơ hội và giá trị tốt đẹp của chính bạn. Thay đổi chưa bao giờ là muộn nếu chúng ta bắt đầu ngay hôm nay."*"""
            elif type_code == "DANG_3_HAI_QUAN_DIEM":
                return f"""👩‍🏫 **Trợ lý Ngữ văn:** Với **Dạng bài Lựa chọn quan điểm**, phần phản biện chính là **Chỉ ra hạn chế của quan điểm còn lại**:
- Em hãy phân tích khách quan: Nếu tuyệt đối hóa quan điểm kia mà bỏ qua thực tế thì con người sẽ dễ rơi vào sự cực đoan, phiến diện hoặc thiếu tính khả thi như thế nào.
- Từ đó khẳng định sự lựa chọn của em là có cơ sở vững chắc."""
            else:
                return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để viết đoạn **Phản đề & Mở rộng** cho đề **\"{vdnl}\"** đạt điểm tối đa (1.0đ), em triển khai theo 2 tầng tư duy:
{pb_content}
- **Tầng 1 (Phê phán mặt trái):** Chỉ ra và lên án bộ phận sống thiếu **{vdnl}** hoặc đi ngược lại giá trị này.
- **Tầng 2 (Mở rộng biện chứng - Rất ăn điểm):** Đặt vấn đề trong giới hạn hợp lý — phân biệt rõ giá trị đích thực của **{vdnl}** với những biểu hiện cực đoan, máy móc hoặc sáo rỗng hình thức."""
        else:
            # Khi học sinh hỏi thêm lần 2, 3 về phản đề: Cung cấp khung câu chữ và cách lập luận nâng cao
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để đoạn **Phản đề / Phản biện** về **\"{vdnl}\"** của em sắc sảo hơn nữa (không bị giống văn mẫu), em hãy áp dụng **Kỹ thuật "Nhượng bộ - Phản bác"** chỉ trong 3-4 câu văn:
- **Câu 1 (Mở góc nhìn đối lập):** *Nhìn từ chiều ngược lại, không thể phủ nhận trong thực tế vẫn tồn tại những biểu hiện đi ngược lại {vdnl}, hoặc những cái nhìn lệch lạc khi...*
- **Câu 2 (Chỉ ra ranh giới biện chứng):** *Hơn nữa, đề cao {vdnl} hoàn toàn không đồng nghĩa với sự cực đoan, giáo điều hay bất chấp quy luật khách quan.*
- **Câu 3 (Chốt giá trị):** *Chỉ khi đặt {vdnl} trên nền tảng của nhận thức tỉnh táo và sự chân thành, giá trị ấy mới thực sự tỏa sáng bền vững.*
👉 *Em thử ráp ý của đề bài vào 3 câu này xem, đoạn văn sẽ cực kỳ chặt chẽ!*"""

    # --- NHÁNH C: HỎI VỀ LUẬN ĐIỂM BÀN LUẬN / GIẢI PHÁP / THÂN BÀI ---
    bl_keywords = ["luận điểm", "bàn luận", "thân bài", "dàn ý", "ý nghĩa", "vai trò", "giải pháp", "thực trạng", "nguyên nhân", "hậu quả", "lí do", "lý do", "triển khai", "cần làm gì", "bài học"]
    if any(k in effective_query for k in bl_keywords):
        ask_idx = count_previous_topic_asks(bl_keywords)
        bl_items = []
        for q in questions_list:
            for ans in q.get("y_tra_loi", []):
                bl_items.append(ans)
        bl_text = "\n".join(bl_items)

        # Kiểm tra xem học sinh có hỏi đích danh phần Giải pháp Cá nhân / Gia đình / Nhà trường không
        if "giải pháp" in effective_query or "cá nhân" in effective_query or "gia đình" in effective_query or "nhà trường" in effective_query:
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Khi viết phần **Giải pháp** cho vấn đề **\"{vdnl}\"**, em nhớ quy tắc vàng: **Tách thành 3 đoạn văn (Cá nhân - Gia đình - Nhà trường)**, và mỗi đoạn bắt buộc đủ 3 mạch câu: **[Nêu giải pháp khả thi] $\rightarrow$ [Lí giải vì sao chọn giải pháp đó] $\rightarrow$ [Ít nhất 01 dẫn chứng]**:
1. **Đoạn Giải pháp từ Cá nhân (Trọng tâm):**
   - *Cách làm:* Tự nhận thức, thay đổi thói quen từ những hành động nhỏ, rèn kỹ năng tự kiểm soát.
   - *Lí giải:* Bởi mỗi cá nhân là chủ thể trực tiếp của nhận thức và hành động; sự thay đổi tự thân luôn mang tính quyết định.
   - *Dẫn chứng:* Nêu tấm gương người trẻ tự rèn luyện vượt qua hoàn cảnh.
2. **Đoạn Giải pháp từ Gia đình:**
   - *Cách làm:* Cha mẹ lắng nghe, thấu cảm, làm gương và tạo không gian gắn kết.
   - *Lí giải:* Gia đình là môi trường giáo dục đầu tiên, định hình cảm xúc và thói quen bền vững nhất.
   - *Dẫn chứng:* Những gia đình duy trì thói quen sinh hoạt chung, đồng hành cùng con.
3. **Đoạn Giải pháp từ Nhà trường & Xã hội:**
   - *Cách làm:* Tăng cường hoạt động trải nghiệm thực tế, tư vấn tâm lý và truyền thông tích cực.
   - *Lí giải:* Tạo hệ sinh thái lành mạnh nâng đỡ và định hướng cá nhân phát triển đúng hướng.
   - *Dẫn chứng:* Các dự án học đường, phong trào thanh niên tình nguyện, câu lạc bộ kỹ năng."""

        if ask_idx == 0:
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Hệ thống đã nhận diện đề bài của em thuộc **{type_label}**. Do đó, phần Thân bài em tuyệt đối không viết chung chung mà triển khai theo đúng cấu trúc đặc thù sau:
{bl_text}
💡 *Em muốn cô hướng dẫn cách viết chi tiết (cách lập lý lẽ, cách đặt câu chủ đề) cho **Luận điểm số mấy** trong các mục trên? Em hãy nhắn rõ số thứ tự hoặc tên mục đó nhé!*"""
        else:
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để đào sâu từng **Luận điểm bàn luận** về **\"{vdnl}\"** sao cho dày dặn (đạt chuẩn bài văn khoảng 600 chữ) mà không bị cụt ý, ở mỗi đoạn văn thân bài em hãy triển khai theo **Mô hình 4 câu hỏi (PEEL)**:
1. **Câu chủ đề (Point):** Khẳng định trực tiếp luận điểm ở ngay câu đầu đoạn (Ví dụ: *Trước hết, {vdnl} chính là động lực...*).
2. **Lí giải nguyên nhân (Explanation):** Trả lời câu hỏi *Vì sao lại như vậy? Nếu nhìn vào quy luật tâm lý và thực tế đời sống thì điều đó diễn ra thế nào?*
3. **Minh chứng thực tế (Evidence):** Đưa dẫn chứng cụ thể và phân tích ngắn gọn.
4. **Câu tiểu kết (Link):** Khẳng định lại giá trị của luận điểm và mở đường sang đoạn tiếp theo.
👉 *Em đang viết tới luận điểm nào rồi? Hãy gõ thử ý em định viết vào đây để cô giúp em mở rộng lý lẽ nhé!*"""

    # --- NHÁNH D: HỎI VỀ MỞ BÀI / KẾT BÀI / GIẢI THÍCH / CHUYỂN Ý ---
    if "mở bài" in effective_query or "câu đầu" in effective_query or "dẫn dắt" in effective_query:
        ask_idx = count_previous_topic_asks(["mở bài", "câu đầu", "dẫn dắt"])
        if ask_idx == 0:
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Với đề bài về **\"{vdnl}\"** (*{type_label}*), cô gợi ý 2 cách **Mở bài** phù hợp nhất:
- **Cách 1 (Mở bài trực tiếp - Ngắn gọn, sáng rõ):** Đi từ yêu cầu bức thiết của cuộc sống hiện đại $\rightarrow$ Nêu trực diện vấn đề **{vdnl}** (Nếu là dạng 2 quan điểm thì giới thiệu 2 quan điểm và chốt lựa chọn của em; nếu là dạng tác phẩm văn học thì giới thiệu tác giả, tác phẩm rồi rút ra vấn đề).
- **Cách 2 (Mở bài gián tiếp - Giàu hình ảnh, cảm xúc):** Dẫn dắt từ một nghịch lý của thời đại số hoặc một hình ảnh ẩn dụ tương đồng, sau đó kết nối tự nhiên vào **{vdnl}**.
👉 *Em thích phong cách mở bài nào hơn? Hãy viết thử 2 câu mở đầu của em vào đây cô xem nhé!*"""
        else:
            return f"""👩‍🏫 **Trợ lý Ngữ văn:** Cô gợi ý thêm cho em **khung câu Mở bài nâng cao** dành cho đề **\"{vdnl}\"**:
*"Cuộc sống không chỉ được đo bằng chiều dài của năm tháng, mà được định giá bằng những giá trị thực chất mà con người kiến tạo và theo đuổi. Giữa dòng chảy nhiều biến động của thời đại hôm nay, câu chuyện về **{vdnl}** lại càng trở thành một vấn đề đáng suy ngẫm sâu sắc..."* (Sau đó em trích dẫn đề bài/quan điểm của mình).
Em hãy biến tấu lại bằng từ ngữ của riêng em để mở bài thật tự nhiên nhé!"""

    if "giải thích" in effective_query or "khái niệm" in effective_query or "từ khóa" in effective_query:
        gt_content = "\n".join(explain_list) if explain_list else f"- Cắt nghĩa tường minh bản chất của **{vdnl}**."
        return f"""👩‍🏫 **Trợ lý Ngữ văn:** Ở đoạn **Giải thích** cho đề **\"{vdnl}\"** (*{type_label}*), em cần thực hiện gọn gàng trong khoảng 4-5 câu văn đầu Thân bài:
{gt_content}
- **Lưu ý quan trọng:** Giải thích xong phải có 1 câu chốt để bắc cầu sang phần trọng tâm tiếp theo của dạng bài này."""

    if "kết bài" in effective_query or "kết thúc" in effective_query or "liên hệ" in effective_query:
        return f"""👩‍🏫 **Trợ lý Ngữ văn:** Để viết **Kết bài & Liên hệ bản thân** cho đề **\"{vdnl}\"** thật ấn tượng:
1. **Khẳng định lại thông điệp cốt lõi:** Tóm lược lại giá trị/bài học quan trọng nhất của **{vdnl}** bằng một câu văn cô đọng.
2. **Liên hệ cá nhân thực chất:** Tránh câu sáo mòn *"Là học sinh ngồi trên ghế nhà trường..."*; hãy nói rõ sự thay đổi trong góc nhìn của riêng em và một hành động cụ thể em chọn thực hiện ngay từ hôm nay."""

    # --- NHÁNH E: HỌC SINH GỬI ĐOẠN NHÁP HOẶC CÂU HỎI TỰ DO ---
    if len(q_clean.split()) >= 14:
        return f"""👩‍🏫 **Trợ lý Ngữ văn:** Cô đã đọc kỹ đoạn/ý em vừa viết: *\"{q_clean[:140]}{'...' if len(q_clean) > 140 else ''}\"*.
- **Điểm tốt:** Em đã bám vào chủ đề **{vdnl}** và có ý thức triển khai câu văn nghị luận.
- **Điểm cần nâng cấp:**
  1. Em hãy kiểm tra xem đoạn này đã đặt đúng vị trí trong cấu trúc **{type_label}** chưa.
  2. Hãy bổ sung thêm các từ ngữ lập luận chỉ nguyên nhân - hệ quả (*bởi lẽ, chính điều đó đã khẳng định, từ thực tế ấy...*) và kèm theo 1 minh chứng thực tế cụ thể để đoạn văn có sức nặng thuyết phục hơn nhé!"""

    return f"""👩‍🏫 **Trợ lý Ngữ văn:** Về câu hỏi **\"{q_clean}\"** của em cho đề bài **{vdnl}** (*{type_label}*):
Để triển khai tốt ý này, em hãy bám sát vào yêu cầu đặc thù của dạng đề:
{structure_guide}
Em muốn cô gợi mở sâu hơn về **Cách giải thích, Hệ thống luận điểm/giải pháp, Dẫn chứng mới hay Cách viết phản biện**? Em cứ nhắn cụ thể nhé!"""


# ==============================================================================
# 6. THUẬT TOÁN CHẤM ĐIỂM RUBRIC 7 TIÊU CHÍ (ĐỌC KỸ, RÀ SOÁT LỖI, SÁT TỪNG DẠNG BÀI)
# ==============================================================================
def evaluate_essay_strictly_by_7_criteria(essay_text, cur_de_info):
    text = essay_text.strip()
    topic_text = ensure_600_words_prompt(cur_de_info.get("text", ""))
    vdnl_chuan = cur_de_info.get("vdnl_chuan", "")
    type_code = cur_de_info.get("essay_type_code", classify_essay_type(topic_text, vdnl_chuan, st.session_state.get("selected_essay_type_override", "Tự động nhận diện theo đề bài")))
    type_label = get_essay_type_label(type_code)
    structure_guide = get_pedagogical_structure_guide(type_code, topic_text, vdnl_chuan)

    prompt_grade = f"""Bạn là Giám khảo chấm thi Ngữ văn THPT cấp Tỉnh/Thành phố có chuyên môn sâu, cẩn trọng và nghiêm khắc. Hãy đọc thật kỹ từng câu chữ trong bài làm dưới đây và đánh giá theo BẢNG RUBRIC 7 TIÊU CHÍ (Thang điểm 10.0, bước nhảy 0.25đ).
- Đề bài: "{topic_text}"
- Vấn đề nghị luận trọng tâm: "{vdnl_chuan}"
- Dạng bài và yêu cầu cấu trúc bắt buộc của đề này:
{structure_guide}

- Bài làm thực tế của học sinh:
\"\"\"{text}\"\"\"

Thực hiện đánh giá trực tiếp vào bảng điểm và lời phê theo các nguyên tắc chuyên môn sau (tuyệt đối không nhắc lại các nguyên tắc này trong kết quả trả về):
- Chấm nghiêm ngặt, công tâm dựa trên chất lượng thực tế và ĐÚNG DẠNG ĐỀ ({type_label}). Không chấm dễ dãi theo kiểu "cứ có ý là cho điểm tối đa". Nếu học sinh có nhắc đến ý nhưng phân tích hời hợt, lập luận lỏng lẻo, thiếu lí giải, hoặc làm sai cấu trúc của dạng bài (ví dụ: dạng Vấn đề cần giải quyết mà thiếu tách 3 đoạn giải pháp Cá nhân - Gia đình - Nhà trường kèm dẫn chứng; dạng Lựa chọn quan điểm mà không chỉ ra hạn chế của quan điểm kia; dạng Thuyết phục từ bỏ mà thiếu dự đoán ý kiến phản đối...) thì PHẢI trừ điểm tương ứng và chỉ rõ.
- Nếu bài viết ngắn dưới 450 chữ, tổng điểm không vượt quá 6.0 điểm; dưới 250 chữ, tổng điểm dưới 4.0 điểm.
- Đọc kỹ từng câu để rà soát lỗi: Bắt buộc trích dẫn nguyên văn (trong dấu ngoặc kép "...") ít nhất 3-4 câu hoặc cụm từ thực tế từ bài làm của học sinh để chỉ rõ lỗi lập luận nông/lặp ý, lỗi diễn đạt, lỗi dùng từ, ngữ pháp hoặc chính tả.
- Lập bảng Markdown đúng 4 cột: Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm (với 7 tiêu chí: 1. Bố cục 0.5đ; 2. Xác định Vấn đề nghị luận 0.5đ; 3. Giải thích / Khởi điểm vấn đề 1.0đ; 4. Hệ thống luận điểm theo đúng dạng bài 3.5đ; 5. Dẫn chứng thực tế 2.5đ; 6. Phản đề / Ý kiến trái chiều & Bài học 1.0đ; 7. Diễn đạt & Chính tả 1.0đ).
- Sau bảng điểm, trình bày phần Rà soát lỗi cụ thể & Hướng dẫn chỉnh sửa nâng cấp từng câu/đoạn bị lỗi."""

    ai_eval = call_gemini_rest_api(prompt_grade, temperature=0.25)
    if ai_eval and "|" in ai_eval:
        return ai_eval

    # Bộ máy kiểm định nội bộ nghiêm ngặt theo sát từng dạng đề (Khi không dùng hoặc lỗi API)
    words = re.findall(r'\w+', text)
    word_count = len(words)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\n', text) if len(p.strip()) > 10]
    num_paras = len(paragraphs)
    sentences = [s.strip() for s in re.split(r'[.?!]+', text) if len(s.strip()) > 3]
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
    proper_nouns = re.findall(r'(?<=[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]\s)[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+(?:\s[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+)+', text)
    unique_proper_nouns = list(set(proper_nouns))

    counter_markers = ["tuy nhiên", "ngược lại", "đáng buồn", "phê phán", "bên cạnh những", "mặt trái", "thực trạng", "vô cảm", "ích kỷ", "lệch lạc", "nhầm lẫn", "cực đoan", "ý kiến khác", "phản đối", "hạn chế"]
    counter_count = sum(1 for m in counter_markers if m in text_low)

    # Kiểm tra đặc thù theo dạng bài
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
    if topic_coverage >= 0.6 and len(paragraphs[0].split()) >= 25 and num_paras >= 3:
        s2 = 0.5
        c2_note = f"Dẫn dắt và xác định trúng vấn đề nghị luận trọng tâm (*{vdnl_chuan}*). Minh chứng mở đầu: *\"{first_sent[:110]}...\"*."
    elif topic_coverage >= 0.25:
        s2 = 0.25
        c2_note = f"Có chạm tới từ khóa của đề nhưng giới thiệu vấn đề còn gượng gạo, chưa làm nổi bật trọng tâm (*\"{first_sent[:95]}...\"*)."
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
        s3 = 0.25 if word_count >= 180 and topic_coverage > 0 else 0.0
        c3_note = "Thiếu đoạn giải thích tường minh khái niệm/nhận định ở đầu phần Thân bài."

    # 4. Hệ thống luận điểm (3.5đ) - Trừ điểm nếu thiếu cấu trúc đặc thù của dạng đề
    base_s4 = 0.5
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
        c4_note = f"Dung lượng đạt **{word_count} chữ**, nhưng so với yêu cầu của **{type_label}**, bài làm còn {', '.join(type_specific_missing)}. Minh chứng câu văn: *\"{longest_sent[:100]}...\"*."
    else:
        c4_note = f"Dung lượng đạt **{word_count} chữ**. Đã triển khai các ý bàn luận (*\"{longest_sent[:105]}...\"*), song chiều sâu lý lẽ và sự sắc bén trong phân tích vẫn cần nâng cao hơn để đạt điểm tối đa."
    s4 = base_s4

    # 5. Dẫn chứng thực tế (2.5đ)
    if len(unique_proper_nouns) >= 2 and ev_marker_count >= 2 and word_count >= 500:
        s5 = 1.75
        c5_note = f"Có đưa dẫn chứng thực tế (**{', '.join(unique_proper_nouns[:3])}**), nhưng cần phân tích sâu hơn sự kết nối giữa dẫn chứng với luận điểm/giải pháp thay vì chỉ thuật lại."
    elif len(unique_proper_nouns) >= 1 or ev_marker_count >= 1:
        s5 = 1.0 if word_count >= 350 else 0.75
        c5_note = f"Có nhắc tới dẫn chứng ({', '.join(unique_proper_nouns[:2]) if unique_proper_nouns else 'ví dụ chung'}), nhưng chủ yếu mới dừng ở mức điểm tên, thiếu câu bình luận đắt giá."
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
        err_details.append(f"dùng từ khẩu ngữ/sáo mòn (*{', '.join(found_colloquial[:3])}*)")
    if repeated_words:
        err_details.append(f"lặp từ nhiều lần (*{', '.join(repeated_words[:4])}*)")
    if len(sample_weak_sent.split()) < 7:
        err_details.append(f"câu văn cụt/sơ sài (*\"{sample_weak_sent}\"*)")
    elif len(sample_weak_sent.split()) > 65:
        err_details.append(f"câu văn quá dài, thiếu ngắt câu (*\"{sample_weak_sent[:90]}...\"*)")

    if err_details:
        s7 = 0.5 if word_count >= 350 else 0.25
        c7_note = f"Cần khắc phục các lỗi diễn đạt: {'; '.join(err_details)}."
    elif word_count < 450:
        s7 = 0.5
        c7_note = f"Diễn đạt tương đối rõ ý nhưng thiếu các cấu trúc câu liên kết chuyển đoạn. Câu cần trau chuốt thêm: *\"{shortest_sent}\"*."
    else:
        s7 = 0.75
        c7_note = f"Diễn đạt khá mạch lạc, tuy nhiên một số câu văn vẫn cần gọt giũa từ ngữ cho giàu sức nặng lập luận hơn (ví dụ: *\"{shortest_sent}\"*)."

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

    return f"""### 📊 BẢNG ĐÁNH GIÁ CHI TIẾT THEO 7 TIÊU CHÍ RUBRIC
*🧭 **Dạng bài áp dụng chấm:** {type_label}*  
*📏 **Thông số kiểm định bài làm:** Độ dài **{word_count} chữ** | **{num_paras} đoạn văn** | **{num_sents} câu văn**.*

| Tiêu chí đánh giá | Điểm
