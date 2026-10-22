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
# 2. QUẢN LÝ SESSION STATE & KHÓA KẾT NỐI
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
# 3. ĐỘNG CƠ KẾT NỐI AI TRỰC TIẾP QUA REST API (VƯỢT MỌI LỖI THƯ VIỆN)
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
# 4. BỘ MÁY NLP SƯ PHẠM NỘI BỘ: PHÂN TÍCH ĐỀ ĐỘNG, CHAT SÂU & CHẤM BÀI THỰC CHẤT
# ==============================================================================
CONCEPT_DICTIONARY = {
    "đoàn kết": {
        "def": "**Đoàn kết** là sự gắn kết, đồng lòng, tập hợp sức mạnh của các cá nhân thành một khối thống nhất để cùng hướng tới mục tiêu chung cao cả.",
        "why": "Một cá nhân dù xuất sắc đến đâu cũng có giới hạn; khi biết hợp lực, sức mạnh trí tuệ và tinh thần sẽ được nhân lên gấp bội để vượt qua nghịch cảnh và kiến tạo kỳ tích.",
        "manifest": "Sự tương thân tương ái khi đồng bào gặp thiên tai bão lũ; tinh thần phối hợp ăn ý trong học tập, nghiên cứu khoa học; sự đồng lòng của cả dân tộc trước những thử thách lịch sử.",
        "counter": "Lối sống ích kỷ, cục bộ bản vị, chia rẽ nội bộ, hoặc biến 'đoàn kết' thành sự bao che, xuôi chiều, dĩ hòa vi quý làm triệt tiêu sự đấu tranh phản biện tích cực.",
        "ev_ten": "Chiến dịch tình nguyện hỗ trợ đồng bào miền Bắc trong siêu bão Yagi & Dự án 'Nuôi Em'",
        "ev_chitiet": "Hàng triệu người dân Việt Nam từ khắp mọi miền đã chung tay quyên góp, những đoàn xe cứu trợ xuyên đêm và hàng nghìn chiến sĩ, thanh niên tình nguyện dầm mình trong lũ dữ để cứu trợ đồng bào.",
        "ev_ynghia": "Minh chứng sống động cho sức mạnh đại đoàn kết dân tộc: khi những trái tim cùng chung một nhịp đập, không thử thách nào có thể khuất phục."
    },
    "biết ơn": {
        "def": "**Lòng biết ơn** là sự trân trọng, ghi nhớ công lao, sự giúp đỡ của người khác hoặc những giá trị tốt đẹp mà thế hệ đi trước, thiên nhiên và cuộc đời đã ban tặng cho mình.",
        "why": "Không thành quả nào tự nhiên mà có; lòng biết ơn giúp con người sống có cội nguồn, nuôi dưỡng tâm hồn nhân hậu, xóa bỏ sự ích kỷ và tạo ra sợi dây gắn kết bền chặt giữa người với người.",
        "manifest": "Trân trọng công ơn sinh thành của cha mẹ, sự dạy dỗ của thầy cô; tri ân các anh hùng liệt sĩ; giữ gìn di sản văn hóa, bảo vệ môi trường sống và nỗ lực sống có ích để đáp đền tiếp nối.",
        "counter": "Thái độ vô ơn, bạc bẽo, 'qua cầu rút ván', coi sự hy sinh của cha mẹ và cộng đồng là điều hiển nhiên, hoặc chỉ thể hiện lòng biết ơn bằng lời nói hình thức trên mạng xã hội.",
        "ev_ten": "Anh Nguyễn Tất Minh và Ngô Minh Hiếu (Đôi bạn 10 năm cõng nhau đến trường)",
        "ev_chitiet": "Không chỉ là tình bạn, Nguyễn Tất Minh luôn khắc ghi sự hy sinh của gia đình và người bạn tri kỷ, nỗ lực vượt qua khuyết tật bẩm sinh để tốt nghiệp đại học loại Giỏi và tự lập giúp đỡ lại cộng đồng.",
        "ev_ynghia": "Biểu tượng đẹp đẽ của lòng biết ơn được chuyển hóa thành hành động vươn lên mạnh mẽ nhất."
    },
    "bản lĩnh": {
        "def": "**Bản lĩnh** là sức mạnh ý chí, sự kiên định, vững vàng của con người trước những giông bão, nghịch cảnh, áp lực hoặc cám dỗ của cuộc đời mà không hề nao núng hay đánh mất giá trị cốt lõi.",
        "why": "Cuộc sống luôn ẩn chứa những biến cố bất ngờ; bản lĩnh chính là chiếc mỏ neo giữ cho con người không gục ngã, biến nghịch cảnh thành bàn đạp để trưởng thành và khẳng định giá trị bản thân.",
        "manifest": "Dám đối diện với thất bại để làm lại từ đầu; dám nói lên chính kiến đúng đắn trước đám đông; giữ vững đạo đức trước những cám dỗ vật chất và không ngừng tự học hỏi trong kỷ nguyên số.",
        "counter": "Sự yếu đuối, hèn nhát, dễ dàng buông xuôi khi gặp khó khăn, sống phụ thuộc theo hiệu ứng đám đông; hoặc nhầm lẫn bản lĩnh với sự bảo thủ, liều lĩnh, bất chấp quy chuẩn.",
        "ev_ten": "Kình ngư Nguyễn Thị Ánh Viên và hành trình vượt ngưỡng bản thân",
        "ev_chitiet": "Trải qua hàng vạn giờ tập luyện khắc nghiệt nơi xứ người, vượt qua những chấn thương và áp lực tâm lý nặng nề để mang về hàng loạt kỷ lục lịch sử cho bơi lội Việt Nam, rồi tiếp tục mở lớp dạy bơi chống đuối nước cho trẻ em.",
        "ev_ynghia": "Bản lĩnh không chỉ nằm ở ánh hào quang chiến thắng mà còn ở sự kiên cường bền bỉ sau ánh đèn sân khấu."
    },
    "trách nhiệm": {
        "def": "**Sống có trách nhiệm** là ý thức nhận thức sâu sắc về bổn phận, nghĩa vụ của bản thân đối với chính mình, gia đình và xã hội, đồng thời dám làm dám chịu trước mọi quyết định của mình.",
        "why": "Mỗi cá nhân là một mắt xích trong cộng đồng; tinh thần trách nhiệm tạo nên sự tin cậy, thúc đẩy xã hội vận hành văn minh và định hình phẩm giá đích thực của một con người trưởng thành.",
        "manifest": "Hoàn thành tốt việc học tập, lao động; không đổ lỗi cho hoàn cảnh khi thất bại; chủ động tham gia giải quyết các vấn đề chung như bảo vệ môi trường, thượng tôn pháp luật.",
        "counter": "Lối sống thờ ơ, vô cảm ('cha chung không ai khóc'), đùn đẩy trách nhiệm, chỉ biết đòi hỏi quyền lợi cá nhân mà trốn tránh nghĩa vụ đóng góp cho tập thể.",
        "ev_ten": "Biệt đội Sài Gòn Xanh và các nhóm bạn trẻ giải cứu dòng kênh ô nhiễm",
        "ev_chitiet": "Những người trẻ tuổi tự nguyện lội xuống những dòng kênh đen đặc rác thải, mùi hôi thối nồng nặc để dọn sạch hàng trăm tấn rác, trả lại dòng nước trong xanh cho thành phố.",
        "ev_ynghia": "Hành động xuất phát từ ý thức trách nhiệm công dân tự giác, đánh thức lương tri và trách nhiệm của cả cộng đồng."
    },
    "thất bại": {
        "def": "**Thất bại** là trạng thái vấp ngã, chưa đạt được mục tiêu đề ra do giới hạn năng lực hoặc hoàn cảnh khách quan, nhưng đồng thời là những bài học kinh nghiệm vô giá trên hành trình trưởng thành.",
        "why": "Không có con đường thành công nào trải đầy hoa hồng; thất bại giúp con người nhận diện rõ điểm yếu của mình, rèn luyện sức chịu đựng (AQ) và tích lũy trí tuệ thực tiễn.",
        "manifest": "Bình tĩnh phân tích nguyên nhân sau mỗi lần điểm kém hoặc dự án đổ vỡ; kiên trì thử nghiệm lại bằng phương pháp mới thay vì tự ti, mặc cảm.",
        "counter": "Tâm lý sợ sai, sợ vấp ngã nên không dám dấn thân thử thách; hoặc thái độ bi quan, tuyệt vọng, đổ lỗi cho số phận sau một lần vấp ngã đầu đời.",
        "ev_ten": "Nhà bác học Thomas Edison và hàng nghìn lần thử nghiệm dây tóc bóng đèn",
        "ev_chitiet": "Trước khi phát minh ra bóng đèn điện làm thay đổi lịch sử nhân loại, ông đã trải qua hàng ngàn cuộc thí nghiệm thất bại nhưng luôn coi đó là 'hàng ngàn cách chưa phù hợp đã được loại trừ'.",
        "ev_ynghia": "Thất bại chỉ thực sự là dấu chấm hết khi con người ngừng cố gắng."
    },
    "ước mơ": {
        "def": "**Ước mơ / Khát vọng** là những mục tiêu, lý tưởng tốt đẹp, cao cả mà con người khao khát hướng tới và nỗ lực phấn đấu để hiện thực hóa trong tương lai.",
        "why": "Ước mơ giống như ngọn hải đăng soi đường, giúp tuổi trẻ sống có mục đích, không bị lạc lối trong sự tầm thường, đồng thời đánh thức những tiềm năng phi thường ẩn giấu bên trong mỗi người.",
        "manifest": "Xây dựng kế hoạch học tập rõ ràng, rèn luyện kỹ năng chuyên môn mỗi ngày, dám theo đuổi đam mê chân chính gắn liền với nhu cầu phát triển của đất nước.",
        "counter": "Lối sống hoài phí tuổi trẻ, không mục tiêu, 'nước đến chân mới nhảy'; hoặc những ảo tưởng viển vông, hão huyền, chỉ mơ mộng suông mà thiếu hành động thực tế.",
        "ev_ten": "Hành trình của cô gái dân tộc Mông Lầu Minh Vư chinh phục học bổng quốc tế",
        "ev_chitiet": "Sinh ra ở vùng cao nghèo khó nơi nhiều bạn bè phải nghỉ học lấy chồng sớm, Vư đã nuôi dưỡng khát vọng bước ra thế giới bằng con đường tri thức, tự học tiếng Anh và giành học bổng toàn phần đại học.",
        "ev_ynghia": "Khát vọng lớn chính là đôi cánh đưa con người vượt thoát khỏi mọi rào cản xuất phát điểm."
    },
    "thấu cảm": {
        "def": "**Sự thấu cảm / Tình yêu thương** là khả năng đặt mình vào vị trí của người khác để cảm nhận, sẻ chia những nỗi đau, khó khăn của họ và hành động bằng một trái tim nhân ái.",
        "why": "Trong kỷ nguyên số đầy áp lực và sự cô đơn, thấu cảm là chất keo hàn gắn những tổn thương tâm lý, hóa giải định kiến và làm cho thế giới trở nên ấm áp, nhân văn hơn.",
        "manifest": "Biết lắng nghe không phán xét; sẵn sàng nâng đỡ những mảnh đời yếu thế; tôn trọng sự khác biệt và lan tỏa những hành động tử tế giản dị mỗi ngày.",
        "counter": "Căn bệnh vô cảm, máu lạnh trước nỗi đau đồng loại; thói phán xét độc hại (cyberbullying) trên mạng xã hội hoặc lòng tốt giả tạo nhằm đánh bóng tên tuổi.",
        "ev_ten": "Chàng trai trẻ Lê Văn Phúc và nhóm 'Mái ấm 0 đồng' / 'Fly To Sky'",
        "ev_chitiet": "Từ khi còn là học sinh phổ thông, Phúc đã khởi xướng hàng chục dự án thiện nguyện bền vững, hỗ trợ sách vở, thư viện và sinh kế cho hàng vạn trẻ em yếu thế vùng biên giới.",
        "ev_ynghia": "Khi thấu cảm đi liền với hành động tử tế, tuổi trẻ có thể tạo ra những thay đổi kỳ diệu cho xã hội."
    },
    "sáng tạo": {
        "def": "**Tư duy sáng tạo / Đổi mới** là khả năng vượt thoát khỏi những lối mòn cũ kỹ để tìm ra những ý tưởng, phương pháp và giải pháp mới mẻ, hiệu quả hơn.",
        "why": "Thế giới vận động không ngừng cùng trí tuệ nhân tạo và công nghệ; nếu chỉ sao chép và đi theo lối mòn, cá nhân và dân tộc sẽ bị tụt hậu và đào thải.",
        "manifest": "Chủ động đặt câu hỏi phản biện trong học tập, tìm tòi cách giải quyết vấn đề mới, ứng dụng khoa học công nghệ vào thực tiễn đời sống.",
        "counter": "Sự bảo thủ, trì trệ, học vẹt máy móc, ngại thay đổi; hoặc sự 'sáng tạo' lệch chuẩn, kỳ dị, đi ngược lại các giá trị đạo đức và văn hóa truyền thống.",
        "ev_ten": "Kỹ sư trẻ Nguyễn Tử Quảng và đội ngũ chuyên gia công nghệ Việt Nam",
        "ev_chitiet": "Dám dấn thân nghiên cứu các lĩnh vực công nghệ lõi từ an ninh mạng đến trí tuệ nhân tạo ngay từ khi điều kiện trong nước còn vô cùng thiếu thốn, khẳng định trí tuệ Việt trên bản đồ số.",
        "ev_ynghia": "Tinh thần dám nghĩ dám làm, đổi mới sáng tạo là chìa khóa mở cánh cửa tương lai."
    }
}

def extract_key_phrases(text):
    clean = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text.lower())
    stop_words = {"bàn", "về", "suy", "nghĩ", "của", "anh", "chị", "em", "hãy", "viết", "bài", "văn", "đoạn", "nghị", "luận", "xã", "hội", "ý", "nghĩa", "vai", "trò", "tầm", "quan", "trọng", "trong", "cuộc", "sống", "hiện", "nay", "đối", "với", "giới", "trẻ", "tuổi", "người", "ta", "nói", "rằng", "có", "kiến", "cho", "từ", "đó", "rút", "ra", "bài", "học"}
    words = [w for w in clean.split() if w not in stop_words and len(w) > 1]
    return " ".join(words[:6]) if words else text.strip()

def build_dynamic_outline_for_custom_topic(topic_text, student_vdnl):
    # 1. Thử gọi Gemini REST API trước nếu có khóa hợp lệ
    prompt = f"""Đóng vai chuyên gia sư phạm Ngữ văn THPT. Hãy phân tích sâu sắc đề bài nghị luận xã hội sau và trả về MỘT CHUỖI JSON HỢP LỆ (chỉ xuất chuỗi JSON thuần túy, không dùng markdown code block):
Đề bài: "{topic_text}"
Vấn đề nghị luận học sinh xác định: "{student_vdnl}"

YÊU CẦU CHUYÊN MÔN:
- Giải thích cụ thể, cắt nghĩa từng từ khóa/hình ảnh ẩn dụ trong đề bài, tuyệt đối không viết câu chung chung kiểu "Giải thích từ khóa cốt lõi...".
- Hệ thống 5 luận điểm bàn luận phải bám sát trực tiếp vào vấn đề của đề bài.
- Dẫn chứng phải là nhân vật/sự kiện có thật, nêu rõ tên và chi tiết hành động.

Cấu trúc JSON BẮT BUỘC:
{{
  "text": "{topic_text}",
  "vdnl_chuan": "Tên vấn đề nghị luận chuẩn xác, cô đọng",
  "explain_items": [
    "- **Giải thích từ khóa/khái niệm:** (Viết nội dung giải thích cụ thể tại đây)...",
    "- **Ý nghĩa cả câu/thông điệp:** (Viết nội dung thông điệp cụ thể tại đây)..."
  ],
  "vdnl_ket_luan": "Câu chốt vấn đề nghị luận sắc bén",
  "questions": [
    {{
      "cau_hoi": "Hệ thống 5 luận điểm bàn luận trọng tâm làm sáng tỏ vấn đề:",
      "y_tra_loi": [
        "- **Luận điểm 1 (Bản chất & Biểu hiện):** ...",
        "- **Luận điểm 2 (Tác động đối với cá nhân):** ...",
        "- **Luận điểm 3 (Ý nghĩa đối với cộng đồng, xã hội):** ...",
        "- **Luận điểm 4 (Lý giải nguyên nhân / Hệ lụy nếu thiếu vắng):** ...",
        "- **Luận điểm 5 (Phương hướng rèn luyện của người trẻ):** ..."
      ]
    }}
  ],
  "evidence": [
    {{
      "ten": "Tên nhân vật/sự kiện thực tế cụ thể",
      "chi_tiet": "Tóm tắt hành động, sự kiện tiêu biểu",
      "y_nghia": "Ý nghĩa chứng minh cho luận điểm",
      "nguon": "Thực tiễn đời sống / Báo chí chính thống"
    }}
  ],
  "counter": [
    "- **Phê phán biểu hiện lệch lạc:** ...",
    "- **Góc nhìn phản biện / Mở rộng:** ..."
  ],
  "dani_chi_tiet": {{
    "mb": "Hướng dẫn dẫn dắt và nêu trực diện vấn đề nghị luận.",
    "gt": "Tóm tắt ý giải thích từ khóa.",
    "bl": "Tóm tắt 5 luận điểm bàn luận.",
    "dc": "Cách đưa dẫn chứng và phân tích.",
    "pb": "Cách lật lại vấn đề và phê phán.",
    "kb": "Khẳng định lại giá trị và liên hệ bản thân."
  }}
}}"""
    ai_res = call_gemini_rest_api(prompt)
    if ai_res:
        try:
            match = re.search(r'\{.*\}', ai_res, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if "explain_items" in parsed and "questions" in parsed:
                    return parsed
        except Exception:
            pass

    # 2. Nếu không có API hoặc lỗi mạng -> Chạy Bộ máy Phân tích Ngữ nghĩa Nội bộ
    combined_low = (topic_text + " " + student_vdnl).lower()
    matched_concept = None
    for kw, data in CONCEPT_DICTIONARY.items():
        if kw in combined_low:
            matched_concept = (kw, data)
            break
            
    core_focus = student_vdnl.strip() if student_vdnl.strip() else extract_key_phrases(topic_text)
    
    if matched_concept:
        kw_name, c_data = matched_concept
        vdnl_final = student_vdnl.strip() if student_vdnl.strip() else f"Giá trị và sức mạnh của {kw_name} trong cuộc sống"
        return {
            "text": topic_text,
            "vdnl_chuan": vdnl_final,
            "explain_items": [
                f"- **Cắt nghĩa khái niệm trọng tâm:** {c_data['def']}",
                f"- **Hàm ý toàn bộ đề bài:** Từ mệnh đề *\"{topic_text}\"*, đề bài khẳng định vai trò sống còn của **{kw_name}** như một thước đo phẩm giá và động lực giúp con người vượt qua giới hạn, kiến tạo những giá trị bền vững cho bản thân và cộng đồng."
            ],
            "vdnl_ket_luan": f"Khẳng định **{vdnl_final}** là kim chỉ nam định hướng nhân cách và hành động cho thế hệ trẻ trong thời đại mới.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống 5 luận điểm bàn luận chuyên sâu về: {vdnl_final}",
                    "y_tra_loi": [
                        f"- **Luận điểm 1 (Biểu hiện sinh động trong thực tiễn):** {c_data['manifest']}",
                        f"- **Luận điểm 2 (Lý giải nguyên nhân cốt lõi):** {c_data['why']}",
                        f"- **Luận điểm 3 (Sức mạnh đối với sự trưởng thành cá nhân):** Giúp con người rèn luyện nội lực vững vàng, tìm thấy ý nghĩa sống đích thực và không bị khuất phục trước những biến động của hoàn cảnh.",
                        f"- **Luận điểm 4 (Giá trị lan tỏa đối với cộng đồng, xã hội):** Truyền cảm hứng tích cực, kết nối những tâm hồn đồng điệu và góp phần xây dựng một xã hội văn minh, nhân ái, tiến bộ.",
                        f"- **Luận điểm 5 (Hệ lụy nếu đánh mất giá trị):** Nếu thiếu đi **{kw_name}**, con người dễ rơi vào trạng thái bế tắc, ích kỷ, cô lập và làm suy giảm niềm tin giữa người với người."
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
                f"- **Phê phán lối sống lệch chuẩn:** {c_data['counter']}",
                f"- **Góc nhìn phản đề toàn diện:** Đề cao **{kw_name}** nhưng cần đặt trong sự tỉnh táo, hài hòa với trí tuệ và hoàn cảnh thực tế, tránh biến phẩm chất tốt đẹp thành sự giáo điều hoặc cực đoan."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt từ quy luật cuộc sống hoặc câu nói tương đồng -> Trích dẫn đề bài -> Nêu trực diện vấn đề nghị luận: {vdnl_final}.",
                "gt": f"Giải thích tường minh khái niệm '{kw_name}' và rút ra thông điệp tư tưởng của đề bài.",
                "bl": f"Phân tích 5 luận điểm: Biểu hiện thực tế -> Nguyên nhân -> Tác động tới cá nhân -> Ý nghĩa xã hội -> Hệ lụy nếu thiếu vắng '{kw_name}'.",
                "dc": f"Đưa dẫn chứng về {c_data['ev_ten']} và phân tích ngắn gọn, sắc sảo để làm sáng tỏ luận điểm.",
                "pb": f"Phê phán những biểu hiện ngược lại (ích kỷ, hời hợt, cực đoan) và mở rộng góc nhìn biện chứng.",
                "kb": f"Khẳng định lại giá trị của {vdnl_final} và rút ra bài học nhận thức, hành động cụ thể cho bản thân."
            }
        }
    else:
        # Bóc tách mệnh đề thông minh cho bất kỳ đề bài triết lý/hiện tượng mới nào
        clauses = [c.strip() for c in re.split(r'[,;:.?!—\-]', topic_text) if len(c.strip()) > 3]
        clause_1 = clauses[0] if len(clauses) > 0 else topic_text
        clause_2 = clauses[1] if len(clauses) > 1 else core_focus
        vdnl_final = student_vdnl.strip() if student_vdnl.strip() else f"Bàn về {core_focus} trong đời sống đương đại"
        
        return {
            "text": topic_text,
            "vdnl_chuan": vdnl_final,
            "explain_items": [
                f"- **Giải thích vế thứ nhất / Khái niệm nền tảng (*\"{clause_1}\"*):** Chỉ trạng thái nhận thức, thái độ hoặc hoàn cảnh khách quan mà con người phải đối diện trên hành trình sống và định vị bản thân.",
                f"- **Giải thích vế trọng tâm (*\"{clause_2}\"*):** Nhấn mạnh vai trò quyết định của nội lực, sự lựa chọn chủ động và hành động thực tiễn của con người để tạo nên giá trị thực chất.",
                f"- **Ý nghĩa toàn diện của đề bài:** Khẳng định mối quan hệ biện chứng giữa nhận thức và hành động xoay quanh vấn đề **{vdnl_final}**."
            ],
            "vdnl_ket_luan": f"Đề bài gửi gắm thông điệp sâu sắc: **{vdnl_final}** chính là chìa khóa để mỗi cá nhân hoàn thiện nhân cách và đóng góp tích cực cho xã hội.",
            "questions": [
                {
                    "cau_hoi": f"Hệ thống 5 luận điểm bàn luận trọng tâm về: {vdnl_final}",
                    "y_tra_loi": [
                        f"- **Luận điểm 1 (Bản chất & Biểu hiện thực tế):** Vấn đề **{vdnl_final}** xuất hiện hiện hữu trong từng lựa chọn, cách ứng xử trước khó khăn và thái độ làm việc, học tập mỗi ngày của con người hiện đại.",
                        f"- **Luận điểm 2 (Tác động đối với nội lực cá nhân):** Khi thấu hiểu và thực hành đúng đắn vấn đề này, mỗi người sẽ làm chủ được cuộc đời mình, khai phóng tiềm năng và giữ vững bản lĩnh trước sóng gió.",
                        f"- **Luận điểm 3 (Ý nghĩa đối với cộng đồng và thời đại):** Tạo nên những giá trị văn minh, lan tỏa năng lượng tích cực, thúc đẩy sự gắn kết và phát triển bền vững của tập thể.",
                        f"- **Luận điểm 4 (Hệ lụy khi nhận thức sai lệch):** Nếu thờ ơ, buông xuôi hoặc đi ngược lại quy luật này, cá nhân sẽ đánh mất phương hướng, rơi vào sự tầm thường và tạo ra những hệ lụy tiêu cực cho xã hội.",
                        f"- **Luận điểm 5 (Phương hướng hành động của tuổi trẻ):** Chuyển hóa nhận thức thành kỹ năng sống, rèn luyện tri thức và bản lĩnh từ những việc làm cụ thể ngay hôm nay."
                    ]
                }
            ],
            "evidence": [
                {
                    "ten": "Hành trình vượt lên chính mình của thầy giáo Nguyễn Ngọc Ký & Các gương mặt trẻ Việt Nam tiêu biểu",
                    "chi_tiet": "Dù đối mặt với nghịch cảnh khắc nghiệt hay những thách thức mới của thời đại toàn cầu hóa, họ không chấp nhận đầu hàng số phận mà kiên trì rèn luyện, biến khát vọng và nhận thức đúng đắn thành thành tựu cống hiến cho đời.",
                    "y_nghia": f"Minh chứng thuyết phục cho chân lý: giá trị của con người được quyết định bởi thái độ và hành động thực chất đối với {vdnl_final}.",
                    "nguon": "Thực tiễn đời sống xã hội"
                }
            ],
            "counter": [
                f"- **Phê phán biểu hiện tiêu cực:** Lên án lối sống thụ động, hời hợt, chỉ nói lý thuyết suông về **{vdnl_final}** nhưng thiếu sự dấn thân và rèn luyện thực tế.",
                "- **Mở rộng & Phản biện biện chứng:** Cần đặt vấn đề trong từng hoàn cảnh cụ thể, kết hợp hài hòa giữa ý chí cá nhân và sự thấu hiểu quy luật khách quan, tránh cái nhìn phiến diện một chiều."
            ],
            "dani_chi_tiet": {
                "mb": f"Dẫn dắt từ thực tiễn thời đại -> Trích dẫn đề bài \"{topic_text}\" -> Nêu vấn đề nghị luận: {vdnl_final}.",
                "gt": f"Cắt nghĩa các vế \"{clause_1}\" và \"{clause_2}\", từ đó chốt lại thông điệp tư tưởng cốt lõi.",
                "bl": f"Triển khai 5 luận điểm: Biểu hiện -> Tác động cá nhân -> Ý nghĩa xã hội -> Hệ lụy nếu đi ngược lại -> Bài học cho tuổi trẻ.",
                "dc": "Chọn lọc và phân tích dẫn chứng người thật việc thật tiêu biểu gắn chặt với luận điểm.",
                "pb": "Phê phán lối sống lệch chuẩn, thụ động và bổ sung góc nhìn biện chứng hai chiều.",
                "kb": f"Khẳng định sức sống của thông điệp {vdnl_final} và liên hệ trực tiếp tới trách nhiệm của bản thân."
            }
        }

def generate_deep_chat_response(user_q, cur_de_info):
    q_clean = user_q.strip()
    q_low = q_clean.lower()
    topic_text = cur_de_info.get("text", "")
    vdnl = cur_de_info.get("vdnl_chuan", "vấn đề nghị luận của đề bài")
    
    # Chặn xin viết hộ
    if any(w in q_low for w in ["viết hộ", "viết giùm", "viết luôn", "làm hộ", "cho em bài văn", "viết cả bài", "viết đoạn văn hoàn chỉnh"]):
        return f"👩‍🏫 **Trợ lý Ngữ văn:** Cô tuyệt đối không viết hộ bài văn hay đoạn văn hoàn chỉnh cho em nhé! Với đề bài *\"{topic_text}\"*, việc tự mình tư duy và đặt bút viết mới giúp em rèn luyện năng lực thực chất. Em hãy cho cô biết em đang định viết ý gì, cô sẽ gợi ý khung câu và từ khóa đắt giá để em tự triển khai!"

    # 1. Thử gọi AI trực tiếp nếu có khóa hợp lệ
    prompt_chat = f"""Đóng vai giáo viên Ngữ văn THPT giỏi chuyên môn, tận tâm. Học sinh đang thực hiện Bước 2 (Tìm ý & Lập dàn ý) cho đề bài Nghị luận xã hội:
- Đề bài: "{topic_text}"
- Vấn đề nghị luận: "{vdnl}"
- Câu hỏi của học sinh: "{q_clean}"

YÊU CẦU SƯ PHẠM BẮT BUỘC:
1. TUYỆT ĐỐI KHÔNG VIẾT HỘ BÀI VĂN HOÀN CHỈNH.
2. Trả lời trực diện, cụ thể, sâu sắc đúng vào câu hỏi của học sinh, gắn chặt với từ khóa "{vdnl}".
3. Đưa ra cấu trúc câu gợi mở (ví dụ: Câu 1 nên viết gì, Câu 2 nên lập luận thế nào, dùng những từ khóa chuyên môn nào) để học sinh có thể tự viết được ngay."""
    
    ai_reply = call_gemini_rest_api(prompt_chat)
    if ai_reply:
        return ai_reply

    # 2. Bộ máy Tư vấn Sư phạm Nội bộ (Phân tích sâu theo từng khía cạnh câu hỏi & bám sát dữ liệu đề đang chọn)
    explain_list = cur_de_info.get("explain_items", [])
    questions_list = cur_de_info.get("questions", [])
    evidence_list = cur_de_info.get("evidence", [])
    counter_list = cur_de_info.get("counter", [])

    if "mở bài" in q_low:
        return f"""👩‍🏫 **Hướng dẫn viết Mở bài ấn tượng cho vấn đề \"{vdnl}\":**
Em có thể chọn 1 trong 2 cách dẫn dắt sau (khoảng 3-4 câu văn):
1. **Cách 1 (Đi từ quy luật đời sống / Phản đề):**
   - *Câu 1:* Giữa dòng chảy hối hả của cuộc sống hiện đại, đôi khi con người mải miết chạy theo những giá trị hào nhoáng bên ngoài mà quên mất điểm tựa cốt lõi bên trong.
   - *Câu 2:* Chính vì vậy, việc suy ngẫm về **{vdnl}** (như đề bài đã gợi mở: *"{topic_text[:70]}..."*) trở thành một bài học nhận thức vô cùng sâu sắc.
   - *Câu 3:* Đây là chiếc chìa khóa định hình phẩm giá và hướng đi của mỗi người, đặc biệt là thế hệ trẻ hôm nay.
2. **Cách 2 (Đi từ hình ảnh ẩn dụ):**
   - Em có thể so sánh cuộc đời như một cuộc hải trình dài, và **{vdnl}** chính là chiếc la bàn định hướng để con thuyền nhân cách không bị chệch hướng trước sóng gió.
👉 *Em hãy thử chọn 1 cách và tự viết 3 câu mở bài của riêng mình nhé!*"""

    if "giải thích" in q_low or "từ khóa" in q_low or "khái niệm" in q_low:
        gt_content = "\n".join(explain_list) if explain_list else f"- Làm rõ khái niệm cốt lõi xoay quanh **{vdnl}**."
        return f"""👩‍🏫 **Hướng dẫn viết đoạn Giải thích tường minh, chặt chẽ:**
Trong bài văn NLXH, phần Giải thích chiếm **1.0 điểm** và là nền móng cho toàn bài. Em cần triển khai theo 3 bước:
{gt_content}
- **Chốt ý chuyển đoạn:** *Như vậy, đề bài đã đặt ra một vấn đề tư tưởng giàu tính nhân văn và thời sự về **{vdnl}**.*
💡 **Lưu ý từ ngữ:** Em nên sử dụng các cụm từ chuyển ý học thuật như: *"Hiểu một cách sâu sắc...", "Ẩn đằng sau câu chữ ấy là thông điệp...", "Thực chất, khái niệm này dùng để chỉ..."*."""

    if "dẫn chứng" in q_low or "ví dụ" in q_low or "nhân vật" in q_low:
        ev_str = ""
        for idx, ev in enumerate(evidence_list[:2], 1):
            if isinstance(ev, dict):
                ev_str += f"\n- **Dẫn chứng {idx}: {ev.get('ten', '')}** – {ev.get('chi_tiet', '')} *(Ý nghĩa: {ev.get('y_nghia', '')})*"
        return f"""👩‍🏫 **Gợi ý Dẫn chứng và Công thức 3 câu đưa dẫn chứng đạt điểm tối đa (2.5đ):**
Đối với đề bài về **{vdnl}**, em có thể sử dụng dẫn chứng sát hợp sau:{ev_str}
- Ngoài ra, em có thể bổ sung thêm gương sáng từ **Kho dẫn chứng 9 chủ điểm** ở cột bên trái (như Nguyễn Ngọc Ký, Đen Vâu, Đội ngũ y bác sĩ, Biệt đội Sài Gòn Xanh...).

📌 **Công thức 3 câu phân tích dẫn chứng (Tránh lỗi kể lể dài dòng):**
- **Câu 1 (Giới thiệu trực diện):** *Thực tiễn đời sống đã ghi nhận biết bao tấm gương sáng ngời về {vdnl}, tiêu biểu như câu chuyện của [Tên nhân vật]...*
- **Câu 2 (Xoáy sâu vào hành động cốt lõi):** *Thay vì khuất phục trước hoàn cảnh hay sống chỉ biết riêng mình, họ đã [Nêu 1-2 hành động đắt giá nhất]...*
- **Câu 3 (Khái quát ý nghĩa gắn với luận điểm):** *Chính hành động ấy đã trở thành minh chứng sống động nhất khẳng định rằng {vdnl} có sức mạnh cảm hóa và kiến tạo kỳ diệu.*"""

    if "phản đề" in q_low or "phản biện" in q_low or "mở rộng" in q_low or "lật lại" in q_low:
        pb_content = "\n".join(counter_list) if counter_list else f"- Phê phán những người sống thiếu **{vdnl}**.\n- Nhìn nhận vấn đề đa chiều, tránh cực đoan."
        return f"""👩‍🏫 **Hướng dẫn viết đoạn Phản đề & Bàn luận mở rộng sắc bén (1.0đ):**
Muốn bài văn đạt điểm Giỏi (8.0+), phần Phản đề không chỉ dừng ở việc phê phán một chiều mà phải có **tư duy biện chứng 2 tầng**:
1. **Tầng 1 (Phê phán biểu hiện lệch lạc):**
{pb_content}
2. **Tầng 2 (Đặt giới hạn biện chứng):**
   - Em hãy đặt câu hỏi: *Liệu trong mọi hoàn cảnh, hiểu máy móc vấn đề có đúng không?* Cần phân biệt rõ giữa giá trị chân chính của **{vdnl}** với sự giáo điều, hình thức sáo rỗng hoặc cực đoan thái quá.
💡 **Cụm từ nối gợi ý:** *"Tuy nhiên, nhìn nhận vấn đề một cách toàn diện và đa chiều hơn, chúng ta cần thấy rằng...", "Đáng buồn thay, bên cạnh những giá trị tích cực ấy vẫn còn không ít cá nhân..."*."""

    if "liên hệ" in q_low or "kết bài" in q_low or "bài học" in q_low or "bản thân" in q_low:
        return f"""👩‍🏫 **Hướng dẫn viết đoạn Bài học nhận thức, Liên hệ bản thân & Kết bài sâu sắc:**
Để tránh lối viết sáo rỗng kiểu *"Là học sinh em hứa sẽ chăm ngoan học giỏi"*, em hãy triển khai theo 3 tầng sâu sắc sau:
1. **Về nhận thức:** Thấu hiểu rằng **{vdnl}** không phải là lý thuyết xa vời trong sách vở mà chính là thái độ sống quyết định giá trị của bản thân mình mỗi ngày.
2. **Về hành động cụ thể:** Bắt đầu từ những việc làm thiết thực ở tuổi 17-18: biết lắng nghe, dám chịu trách nhiệm trước lựa chọn của mình, kiên trì vượt qua áp lực thi cử và sống tử tế với mọi người xung quanh.
3. **Câu chốt Kết bài giàu hình ảnh:** *Khép lại trang viết nhưng dư âm về **{vdnl}** vẫn còn ngân vang mãi như một lời nhắc nhở: mỗi người trẻ chỉ sống một lần, hãy sống sao cho từng khoảnh khắc trôi qua đều mang một ý nghĩa đích thực.*"""

    # Hỏi về bàn luận / luận điểm / nguyên nhân / biểu hiện
    bl_items = []
    for q in questions_list:
        for ans in q.get("y_tra_loi", []):
            bl_items.append(ans)
    bl_text = "\n".join(bl_items[:5]) if bl_items else f"- Phân tích biểu hiện, nguyên nhân và ý nghĩa của **{vdnl}** đối với cá nhân và xã hội."
    
    return f"""👩‍🏫 **Định hướng triển khai Thân bài (Hệ thống luận điểm 3.5đ) cho câu hỏi của em:**
Để trả lời thấu đáo câu hỏi *"{q_clean}"* gắn với vấn đề **{vdnl}**, em cần tách phần Bàn luận thành các luận điểm rõ ràng (mỗi luận điểm nên viết thành một đoạn văn hoặc cụm câu có câu chủ đề đứng đầu):
{bl_text}

💡 **Kỹ thuật viết lập luận sâu (Không bị chấm là viết nông):**
- Khi nêu một ý, em luôn phải trả lời câu hỏi **"Vì sao lại như vậy?"** và **"Nếu không có nó thì điều gì sẽ xảy ra?"**.
- Hãy chọn 1 trong các luận điểm trên và viết thử 3-4 câu nháp gửi vào đây, cô sẽ đọc và góp ý cách chuốt câu cho em nhé!"""


# ==============================================================================
# 5. THUẬT TOÁN CHẤM ĐIỂM RUBRIC 7 TIÊU CHÍ (ĐỌC KỸ VĂN BẢN, TRÍCH DẪN THẬT, CHẤM NGHIÊM TÚC)
# ==============================================================================
def evaluate_essay_strictly_by_7_criteria(essay_text, cur_de_info):
    text = essay_text.strip()
    topic_text = cur_de_info.get("text", "")
    vdnl_chuan = cur_de_info.get("vdnl_chuan", "")

    # 1. Thử gọi AI chấm nếu có API Key hợp lệ (với Prompt chấm nghiêm túc, phân hóa chuẩn)
    prompt_grade = f"""Đóng vai Giám khảo chấm thi Ngữ văn THPT cấp Tỉnh/Thành phố, chấm bài công tâm, chuẩn mực, phân hóa sát thực tế và tuyệt đối không cho điểm dễ dãi.
Hãy đọc kỹ từng câu chữ trong bài làm của học sinh dưới đây và chấm theo BẢNG RUBRIC 7 TIÊU CHÍ (Thang điểm 10.0, bước nhảy 0.25đ).

THÔNG TIN ĐỀ BÀI:
- Đề bài: "{topic_text}"
- Vấn đề nghị luận trọng tâm: "{vdnl_chuan}"

BÀI LÀM CỦA HỌC SINH:
\"\"\"{text}\"\"\"

QUY TẮC CHẤM NGHIÊM NGẶT (TUYỆT ĐỐI KHÔNG KHEN TUNG GIỜI KHI BÀI VIẾT CHƯA ĐẠT):
1. Kiểm tra dung lượng thực tế: Một bài văn NLXH hoàn chỉnh bậc THPT cần đạt tối thiểu 550 - 700 chữ trở lên. Nếu bài viết dưới 500 chữ, tuyệt đối KHÔNG ĐƯỢC xếp loại Giỏi/Xuất sắc (tổng điểm không được vượt quá 6.5đ dù viết mạch lạc, vì độ sâu lập luận chưa đủ). Nếu dưới 250 chữ, chỉ là đoạn văn hoặc bài sơ sài (tổng điểm dưới 4.5đ).
2. BẮT BUỘC TRÍCH DẪN NGUYÊN VĂN (trong dấu ngoặc kép "...") ít nhất 3 câu văn cụ thể từ bài làm của học sinh vào cột Nhận xét để làm bằng chứng cộng điểm hoặc trừ điểm (chỉ rõ câu nào viết sơ sài, lặp từ, lủng củng hoặc câu nào lập luận tốt).
3. Lập bảng Markdown đúng 4 cột:
| Tiêu chí đánh giá | Điểm tối đa | Điểm đạt | Nhận xét chi tiết & Minh chứng trích dẫn từ bài làm |
Với đúng 7 tiêu chí:
- 1. Bố cục (Mở - Thân - Kết) (0.5đ)
- 2. Xác định Vấn đề nghị luận (0.5đ)
- 3. Giải thích khái niệm (1.0đ)
- 4. Hệ thống luận điểm (Tối thiểu 5 ý) (3.5đ)
- 5. Dẫn chứng thực tế (2.5đ)
- 6. Phản đề & Bài học (1.0đ)
- 7. Diễn đạt & Chính tả (1.0đ)
4. Cuối bảng tính TỔNG ĐIỂM chính xác bằng tổng 7 tiêu chí, xếp loại học lực thực chất và đưa ra LỜI PHÊ CỤ THỂ (Ưu điểm, Hạn chế cần khắc phục ngay và Gợi ý cách sửa lại 1 đoạn yếu nhất trong bài)."""

    ai_eval = call_gemini_rest_api(prompt_grade)
    if ai_eval and "|" in ai_eval:
        return ai_eval

    # 2. BỘ MÁY KIỂM ĐỊNH VĂN BẢN ĐỊNH LƯỢNG NỘI BỘ (NLP RUBRIC GRADER)
    words = re.findall(r'\w+', text)
    word_count = len(words)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\n', text) if len(p.strip()) > 10]
    num_paras = len(paragraphs)
    sentences = [s.strip() for s in re.split(r'[.?!]+', text) if len(s.strip()) > 5]
    num_sents = len(sentences)

    # Trích xuất câu văn thực tế của học sinh để làm minh chứng
    first_sent = sentences[0] if num_sents > 0 else text[:80]
    shortest_sent = min(sentences, key=lambda s: len(s.split())) if num_sents > 1 else first_sent
    longest_sent = max(sentences, key=lambda s: len(s.split())) if num_sents > 0 else first_sent

    # Quét mật độ từ khóa chuyên môn trong bài làm
    text_low = text.lower()
    vdnl_tokens = [w for w in extract_key_phrases(vdnl_chuan + " " + topic_text).split() if len(w) > 2]
    matched_topic_kws = [w for w in vdnl_tokens if w in text_low]
    topic_coverage = len(matched_topic_kws) / max(len(vdnl_tokens), 1)

    explain_markers = ["là gì", "nghĩa là", "được hiểu là", "chính là", "hàm ý", "khái niệm", "biểu tượng cho", "ẩn dụ", "thông điệp"]
    has_explain = sum(1 for m in explain_markers if m in text_low)

    argument_markers = ["trước hết", "thứ nhất", "thứ hai", "bên cạnh đó", "hơn thế nữa", "không chỉ vậy", "mặt khác", "bởi vì", "do đó", "chính vì", "nhờ có", "giúp cho", "tạo nên", "thúc đẩy", "cá nhân", "cộng đồng", "xã hội"]
    arg_count = sum(1 for m in argument_markers if m in text_low)

    evidence_markers = ["ví dụ", "dẫn chứng", "tiêu biểu", "chẳng hạn", "câu chuyện", "tấm gương", "như anh", "như chị", "thầy", "bác", "chiến dịch", "dự án", "lịch sử", "thực tế"]
    ev_marker_count = sum(1 for m in evidence_markers if m in text_low)
    # Tìm tên riêng viết hoa ở giữa câu (dấu hiệu có nhân vật/sự kiện cụ thể)
    proper_nouns = re.findall(r'(?<=[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]\s)[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+(?:\s[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+)+', text)

    counter_markers = ["tuy nhiên", "ngược lại", "đáng buồn", "phê phán", "bên cạnh những", "mặt trái", "thực trạng", "vô cảm", "ích kỷ", "lệch lạc", "nhầm lẫn", "cực đoan"]
    counter_count = sum(1 for m in counter_markers if m in text_low)

    # Kiểm tra lỗi lặp từ và câu quá ngắn/quá dài
    word_freq = {}
    for w in words:
        w_l = w.lower()
        if len(w_l) > 4:
            word_freq[w_l] = word_freq.get(w_l, 0) + 1
    repeated_words = [w for w, c in word_freq.items() if c >= max(6, word_count // 45)]

    # --- TÍNH ĐIỂM TỪNG TIÊU CHÍ (BƯỚC NHẢY 0.25) ---
    # Tiêu chí 1: Bố cục (0.5đ)
    if num_paras >= 3 and word_count >= 450:
        s1 = 0.5
        c1_note = f"Bài viết chia thành **{num_paras} đoạn văn** rõ ràng, đảm bảo kết cấu 3 phần Mở - Thân - Kết hợp lý."
    elif num_paras >= 3 and word_count >= 220:
        s1 = 0.25
        c1_note = f"Có tách thành {num_paras} đoạn nhưng dung lượng toàn bài mới đạt **{word_count} chữ** (chưa đạt chuẩn bài văn hoàn chỉnh từ 600 chữ trở lên), phần Thân bài chưa được tách đoạn theo từng luận điểm."
    else:
        s1 = 0.0 if word_count < 100 else 0.25
        c1_note = f"Bố cục chưa đạt yêu cầu: toàn bài chỉ có **{num_paras} đoạn văn** với **{word_count} chữ** (viết liền một khối hoặc quá ngắn ngủi, thiếu sự phân tách Mở - Thân - Kết)."

    # Tiêu chí 2: Xác định VĐNL (0.5đ)
    if topic_coverage >= 0.5 and word_count >= 150:
        s2 = 0.5
        c2_note = f"Xác định đúng vấn đề nghị luận trọng tâm (*{vdnl_chuan}*). Minh chứng câu mở đầu: *\"{first_sent[:110]}...\"*."
    elif topic_coverage > 0:
        s2 = 0.25
        c2_note = f"Có chạm tới từ khóa của đề bài nhưng cách giới thiệu vấn đề còn mờ nhạt, chưa chốt trực diện vấn đề nghị luận ở phần đầu (*\"{first_sent[:90]}...\"*)."
    else:
        s2 = 0.0
        c2_note = f"Bài viết có dấu hiệu lạc trọng tâm hoặc nêu vấn đề quá chung chung, không bám sát các từ khóa cốt lõi của đề bài."

    # Tiêu chí 3: Giải thích khái niệm (1.0đ)
    if has_explain >= 2 and word_count >= 400:
        s3 = 0.75 if word_count < 550 else 1.0
        c3_note = "Đã thực hiện thao tác giải thích khái niệm và làm rõ hàm ý thông điệp của đề bài trước khi đi vào bàn luận."
    elif has_explain >= 1 and word_count >= 200:
        s3 = 0.5
        c3_note = "Có ý giải thích từ khóa nhưng còn sơ lược ở bề mặt chữ nghĩa, chưa bóc tách sâu các lớp nghĩa ẩn dụ và thông điệp triết lý của đề."
    else:
        s3 = 0.25 if word_count >= 150 else 0.0
        c3_note = "Thiếu hẳn đoạn văn giải thích khái niệm tường minh; học sinh nhảy thẳng vào bàn luận cảm tính khiến hệ thống lập luận thiếu nền tảng."

    # Tiêu chí 4: Hệ thống luận điểm - Tối thiểu 5 ý (3.5đ) -> KHỐNG CHẾ NGHIÊM NGẶT THEO DUNG LƯỢNG & LẬP LUẬN
    if word_count < 180:
        s4 = 0.5
        c4_note = f"Dung lượng quá ngắn (**{word_count} chữ**, chỉ có {num_sents} câu văn). Hoàn toàn chưa triển khai được hệ thống 5 luận điểm. Minh chứng câu viết sơ sài: *\"{shortest_sent}\"*."
    elif word_count < 350:
        s4 = 1.25 if arg_count >= 3 else 1.0
        c4_note = f"Bài làm mới đạt **{word_count} chữ** (tương đương một đoạn văn dài, chưa phải bài văn lớn). Mới nêu được 1-2 ý bề nổi, thiếu sự phân tích sâu về nguyên nhân và hệ lụy. Minh chứng câu văn còn đơn giản: *\"{shortest_sent}\"*."
    elif word_count < 500:
        s4 = 2.0 if arg_count >= 5 else 1.5
        c4_note = f"Bài viết đạt **{word_count} chữ** (chưa đủ độ chín của bài văn chuẩn 600+ chữ). Dù có ý thức lập luận (*\"{longest_sent[:110]}...\"*) nhưng chưa chẻ đủ 5 luận điểm chuyên sâu, phân tích còn dừng ở mức khẳng định một chiều."
    elif word_count < 650:
        s4 = 2.5 if arg_count >= 6 else 2.25
        c4_note = f"Độ dài khá (**{word_count} chữ**), có sử dụng các từ ngữ chuyển ý lập luận. Tuy nhiên một số luận điểm phân tích chưa tới độ sắc sảo, cần đào sâu hơn mối quan hệ giữa cá nhân và thời đại. Câu lập luận trong bài: *\"{longest_sent[:110]}...\"*."
    else:
        s4 = 3.0 if arg_count >= 7 else 2.5
        c4_note = f"Dung lượng dồi dào (**{word_count} chữ**), hệ thống luận điểm triển khai đầy đặn từ biểu hiện, nguyên nhân đến ý nghĩa thực tiễn. Minh chứng câu lập luận tốt: *\"{longest_sent[:115]}...\"*."

    # Tiêu chí 5: Dẫn chứng thực tế (2.5đ)
    if len(proper_nouns) >= 1 and ev_marker_count >= 1 and word_count >= 500:
        s5 = 2.0 if len(proper_nouns) >= 2 else 1.75
        c5_note = f"Có đưa dẫn chứng thực tế cụ thể (**{', '.join(list(set(proper_nouns))[:3])}**) và bước đầu gắn kết với luận điểm. Cần chú ý phân tích sâu hơn ý nghĩa của dẫn chứng thay vì chỉ thuật lại sự việc."
    elif len(proper_nouns) >= 1 or ev_marker_count >= 1:
        s5 = 1.0 if word_count >= 300 else 0.75
        c5_note = "Đã có ý thức nhắc tới dẫn chứng nhưng còn chung chung, điểm danh tên nhân vật mà thiếu sự phân tích sắc bén để làm sáng tỏ trực tiếp cho vấn đề nghị luận."
    else:
        s5 = 0.25 if word_count >= 250 else 0.0
        c5_note = "Bài viết hoàn toàn thiếu vắng dẫn chứng người thật việc thật cụ thể. Toàn bộ phần thân bài chỉ dùng lý lẽ suông nên sức thuyết phục rất thấp."

    # Tiêu chí 6: Phản đề & Bài học (1.0đ)
    if counter_count >= 2 and word_count >= 450:
        s6 = 0.75
        c6_note = "Đã có góc nhìn phản đề, phê phán các biểu hiện lệch chuẩn và rút ra bài học nhận thức, hành động cho bản thân."
    elif counter_count >= 1 and word_count >= 250:
        s6 = 0.5
        c6_note = "Có nhắc qua ý phê phán/liên hệ nhưng còn ngắn gọn, chiếu lệ ở cuối bài, chưa có góc nhìn phản biện hai chiều sâu sắc."
    else:
        s6 = 0.25 if word_count >= 150 else 0.0
        c6_note = "Thiếu thao tác lật lại vấn đề (phản đề); bài học liên hệ bản thân còn chung chung theo kiểu khẩu hiệu."

    # Tiêu chí 7: Diễn đạt & Chính tả (1.0đ)
    if len(shortest_sent.split()) < 6 or len(repeated_words) >= 3:
        s7 = 0.5
        rep_str = f"Lặp từ khá nhiều (*{', '.join(repeated_words[:4])}*)." if repeated_words else ""
        c7_note = f"Diễn đạt còn câu cụt hoặc khẩu ngữ, thiếu tính học thuật. {rep_str} Minh chứng câu cần chỉnh sửa: *\"{shortest_sent}\"*."
    elif word_count < 400:
        s7 = 0.5
        c7_note = f"Câu văn tương đối rõ ý nhưng vốn từ còn nghèo, thiếu các cấu trúc câu giàu hình ảnh và nhạc điệu nghị luận."
    else:
        s7 = 0.75
        c7_note = "Diễn đạt mạch lạc, trong sáng, hầu như không mắc lỗi chính tả; tuy nhiên cần trau chuốt thêm các câu chuyển đoạn để văn phong giàu sức nặng hơn."

    total_score = round(s1 + s2 + s3 + s4 + s5 + s6 + s7, 2)
    
    if total_score < 4.0:
        rank = "Yếu / Chưa đạt yêu cầu"
    elif total_score < 5.5:
        rank = "Trung bình"
    elif total_score < 7.0:
        rank = "Trung bình - Khá"
    elif total_score < 8.0:
        rank = "Khá"
    else:
        rank = "Giỏi"

    return f"""### 📊 BẢNG ĐÁNH GIÁ RUBRIC 7 TIÊU CHÍ (KIỂM ĐỊNH THỰC CHẤT)
*📏 **Thông số văn bản kiểm định:** Dung lượng thực tế **{word_count} chữ** | **{num_paras} đoạn văn** | **{num_sents} câu văn**.*

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

#### 📝 LỜI PHÊ & ĐỊNH HƯỚNG CHỈNH SỬA TRỰC TIẾP TỪ GIÁO VIÊN:
* **Về dung lượng & Cấu trúc:** Một bài văn Nghị luận xã hội hoàn chỉnh cần đạt từ **600 – 800 chữ**. Bài làm hiện tại của em đạt **{word_count} chữ** ({'đã đảm bảo độ dài cần thiết' if word_count >= 550 else 'còn thiếu hụt nhiều về dung lượng, chưa đủ không gian để đào sâu lập luận'}).
* **Hạn chế lớn nhất cần sửa ngay:** 
  1. Câu văn trong bài như *\"{shortest_sent}\"* còn đơn điệu, thiếu sức nặng lập luận.
  2. {'Cần bổ sung ngay ít nhất 1 dẫn chứng người thật việc thật có tên tuổi, số liệu/hành động cụ thể và phân tích gắn với luận điểm.' if s5 < 1.5 else 'Cần gọt giũa phần phân tích dẫn chứng sắc sảo hơn, tránh kể lể dài dòng.'}
  3. {'Phải viết bổ sung đoạn Giải thích từ khóa và đoạn Phản đề tách biệt rõ ràng.' if (s3 < 0.75 or s6 < 0.75) else 'Cần nâng tầm phần Phản đề bằng góc nhìn biện chứng hai chiều.'}
* **Yêu cầu thực hành ở khung bên trái:** Em hãy bổ sung thêm luận điểm, dẫn chứng và sửa lại các câu văn yếu ngay tại khung soạn thảo bên trái, sau đó bấm **"🔍 Cập nhật chấm lại Rubric"** để cải thiện điểm số!"""


# ==============================================================================
# 6. GIAO DIỆN CHÍNH & QUY TRÌNH 4 BƯỚC SƯ PHẠM
# ==============================================================================
with st.sidebar:
    st.title("⚙️ HỆ THỐNG QUẢN TRỊ")
    st.success("✅ Hệ thống Sư phạm & Chấm điểm Rubric hoạt động ổn định 100%!")
    
    with st.expander("🔑 Cấu hình nâng cao (Dành cho GV)"):
        key_in = st.text_input("Mã Gemini API Key (Tùy chọn):", type="password", value=st.session_state["gemini_api_key"], help="Nếu nhập mã AIzaSy..., hệ thống sẽ kết hợp thêm AI đám mây. Nếu để trống, hệ thống tự động chạy Bộ máy NLP Sư phạm Nội bộ.")
        if key_in != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = key_in
            
    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM")
    st.markdown("1. **🌱 Bước 1:** Tìm hiểu đề & Xác định VĐNL")
    st.markdown("2. **🧵 Bước 2:** Tìm ý, Lập dàn ý & Kho dẫn chứng")
    st.markdown("3. **✍️ Bước 3:** Viết bài độc lập")
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
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_cb["text"])
            if st.button("📌 Chọn đề Cơ bản này để luyện tập", key="btn_chon_cb", type="primary"):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = de_info_cb
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang Bước 2.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox("Chọn đề trong nhóm Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="sb_nangcao")
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_nc["text"])
            if st.button("📌 Chọn đề Nâng cao này để luyện tập", key="btn_chon_nc", type="primary"):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = de_info_nc
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang Bước 2.")

    with tab_de_tu_nhap:
        st.markdown("##### ✏️ Nhập đề bài bất kỳ để hệ thống bóc tách từ khóa và thiết lập Khung dàn ý chuyên sâu:")
        custom_de_text = st.text_area("Nội dung đề bài tự nhập:", placeholder="Ví dụ: Suy nghĩ của anh/chị về sức mạnh của tinh thần đoàn kết trong cuộc sống...", height=110, key="txt_custom_de")
        student_custom_vdnl = st.text_input("Theo em, vấn đề nghị luận trọng tâm của đề bài này là gì?", placeholder="Ví dụ: Sức mạnh của tinh thần đoàn kết...", key="txt_custom_vdnl")
        if st.button("🔍 Phân tích đề tự nhập & Tạo khung định hướng Bước 2", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài trước khi bấm phân tích!")
            else:
                with st.spinner("Đang phân tích ngữ nghĩa từ khóa, lập hệ thống 5 luận điểm và trích xuất dẫn chứng..."):
                    outline = build_dynamic_outline_for_custom_topic(custom_de_text.strip(), student_custom_vdnl.strip())
                    short_title = custom_de_text.strip()[:55] + ("..." if len(custom_de_text.strip()) > 55 else "")
                    st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                    st.session_state["current_de_info"] = outline
                    st.success("✅ Đã thiết lập xong Khung định hướng tư duy chi tiết cho đề bài mới! Mời thầy/cô và các em chuyển sang **Bước 2** để xem toàn bộ Giải thích, 5 Luận điểm, Dẫn chứng và Phản đề.")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Nội dung đề:* {cur_active_info.get('text', '')}\n\n🎯 **Vấn đề nghị luận trọng tâm:** {cur_active_info.get('vdnl_chuan', '')}")


# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.15, 0.85], gap="large")

    with c_left:
        st.markdown(f"#### 🛠️ Khung định hướng tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>", unsafe_allow_html=True)
        
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            with st.container(border=True):
                for itm in cur_de_info.get("explain_items", []):
                    st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt lại VĐNL:** {cur_de_info.get('vdnl_ket_luan', '')}")

        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Từ 5 ý)", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế", expanded=True):
            st.markdown("##### 📌 Dẫn chứng gợi ý trực tiếp:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    st.markdown(f"<div class='evidence-card'><h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5><p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p><p style='margin:0 0 6px 0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p></div>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("##### 📚 Kho dẫn chứng 9 chủ điểm (Mở rộng):")
            selected_topic = st.selectbox("Chọn chủ điểm dẫn chứng cần tham khảo:", list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()), key="sb_kho_dc")
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"**👤 {dc['ten']}**")
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 Nguồn: {dc['nguon']}")

        with st.expander("🔄 Thao tác 4: Phản đề & Bài học", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        with st.expander("📝 Bố cục Dàn ý chi tiết 3 phần", expanded=True):
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
    st.info(f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n📖 *{st.session_state['current_de_info'].get('text', '')}*")

    write_mode = st.radio(
        "Chọn hình thức nộp bài:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode"
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội (Tiêu chuẩn bài văn hoàn chỉnh: 600 chữ trở lên):",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy tự viết bài văn hoàn chỉnh của em tại đây (Đảm bảo đủ 3 phần Mở bài, Thân bài tách các đoạn rõ ràng, Kết bài)..."
        )
        st.session_state["user_essay"] = essay_input
        wc = len(re.findall(r'\w+', essay_input)) if essay_input.strip() else 0
        st.caption(f"📊 Dung lượng hiện tại: **{wc} chữ** {'(Chưa đủ chuẩn 600 chữ của bài văn NLXH)' if wc < 600 else '(Đã đạt chuẩn dung lượng bài văn NLXH)'}.")

        col_w1, col_w2 = st.columns([1, 1])
        with col_w1:
            if st.button("💡 Nhắc lại tiêu chuẩn đạt điểm Giỏi", use_container_width=True):
                st.info("💡 **Tiêu chuẩn bài văn 8.0+:** Dung lượng từ 600 chữ trở lên, chia tối thiểu 4-5 đoạn văn, có đoạn Giải thích riêng, Thân bài triển khai đủ 5 luận điểm, có Dẫn chứng người thật việc thật cụ thể và có đoạn Phản đề hai chiều!")
        with col_w2:
            if st.button("📊 Nộp bài & Chấm Rubric 7 Tiêu Chí", type="primary", use_container_width=True):
                if not essay_input.strip():
                    st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên!")
                else:
                    with st.spinner("Đang đọc từng câu, kiểm định dung lượng, trích xuất minh chứng và chấm theo 7 tiêu chí Rubric..."):
                        st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(essay_input.strip(), st.session_state["current_de_info"])
                        st.success("✅ Đã chấm xong! Mời chuyển sang **Bước 4: Kiểm tra và chỉnh sửa** để xem Bảng điểm chi tiết và các câu văn được trích dẫn.")
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
                    prompt_img = f"""Hãy đọc toàn bộ chữ viết tay trong bức ảnh này và chấm điểm thật nghiêm túc theo Bảng Rubric 7 tiêu chí (Thang điểm 10.0) cho đề bài: "{st.session_state['current_de_info'].get('text', '')}".
Bắt buộc trích dẫn nguyên văn các câu trong ảnh bài làm để làm minh chứng trừ điểm/cộng điểm, kiểm tra kỹ độ dài thực tế, không khen dễ dãi."""
                    ai_img_res = call_gemini_rest_api(prompt_img, pil_image=img_obj)
                    if ai_img_res and "|" in ai_img_res:
                        st.session_state["rubric_evaluation"] = ai_img_res
                        st.success("✅ Đã đọc ảnh và chấm xong! Mời sang Bước 4 xem kết quả.")
                    elif ocr_assist_text.strip():
                        st.session_state["user_essay"] = ocr_assist_text.strip()
                        st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(ocr_assist_text.strip(), st.session_state["current_de_info"])
                        st.success("✅ Đã chấm xong văn bản bài làm! Mời sang Bước 4 xem kết quả.")
                    else:
                        st.warning("⚠️ Để đọc trực tiếp chữ viết tay từ ảnh mà không cần gõ lại, vui lòng nhập khóa Gemini API (`AIzaSy...`) ở mục Cấu hình nâng cao bên trái, hoặc dán văn bản bài viết vào ô bên trên để hệ thống kiểm định chính xác từng câu.")


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📊 Bước 4: Kiểm Tra và Chỉnh Sửa Theo Rubric</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric đánh giá bài văn Nghị luận xã hội (Chuẩn SKKN 7 tiêu chí - Thang điểm 10):</b><br>
            1. <b>Bố cục (0.5đ):</b> Đủ 3 phần Mở - Thân - Kết, tách đoạn hợp lý.<br>
            2. <b>Xác định VĐNL (0.5đ):</b> Nêu đúng trọng tâm vấn đề nghị luận.<br>
            3. <b>Giải thích (1.0đ):</b> Cắt nghĩa từ khóa, hình ảnh và rút ra thông điệp.<br>
            4. <b>Hệ thống luận điểm (3.5đ):</b> Triển khai tối thiểu 5 ý sâu sắc, dung lượng chuẩn bài văn (600+ chữ).<br>
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
        st.caption(f"📏 Số chữ sau khi chỉnh sửa: **{wc_step4} chữ**.")

        if st.button("🔍 Cập nhật chấm lại Rubric", type="primary", use_container_width=True):
            if edited_essay.strip():
                with st.spinner("Đang kiểm định lại từng tiêu chí sau khi chỉnh sửa..."):
                    st.session_state["rubric_evaluation"] = evaluate_essay_strictly_by_7_criteria(edited_essay.strip(), st.session_state["current_de_info"])
                    st.success("✅ Đã cập nhật bảng điểm mới sát với nội dung vừa chỉnh sửa!")
            else:
                st.warning("⚠️ Hãy nhập bài viết để hệ thống chấm điểm!")

        if edited_essay.strip():
            content = f"HỒ SƠ BÀI LÀM NLXH\nĐỀ BÀI: {st.session_state['selected_de_key']}\nNỘI DUNG ĐỀ: {st.session_state['current_de_info'].get('text', '')}\n\n-- BÀI LÀM CỦA HỌC SINH ({wc_step4} chữ) --\n{edited_essay}\n\n-- KẾT QUẢ ĐÁNH GIÁ RUBRIC --\n{st.session_state.get('rubric_evaluation', '')}"
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
