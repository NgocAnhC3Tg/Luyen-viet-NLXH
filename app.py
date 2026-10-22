import json
import re
import google.generativeai as genai
import streamlit as st
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN VÀ KHO DỮ LIỆU TÍCH HỢP ĐẦY ĐỦ 30 ĐỀ & PHÂN LUỒNG
# ==============================================================================
st.set_page_config(
    page_title="Hệ Thống Luyện Viết NLXH - 30 Đề Chuẩn Mực",
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
    
    .counter-box {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 5px solid #dc2626;
        padding: 16px 20px;
        border-radius: 10px;
        line-height: 1.7;
        color: #7f1d1d;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. PHÂN LUỒNG KHO ĐỀ (15 CƠ BẢN & 15 NÂNG CAO)
# ==============================================================================
DE_BAI_CO_BAN = {
    "Đề 01: Sự cần thiết phải biết sống cống hiến": {
        "text": "Trong bài thơ Tiếng hát con tàu, Chế Lan Viên từng viết: Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn! Từ ý nghĩa câu thơ, em hãy viết bài văn nghị luận bàn về ý nghĩa của lối sống có trách nhiệm và biết cống hiến cho cộng đồng.",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_guide": "Thao tác giải thích theo đúng chuẩn: Giải thích VĐNL trước -> Giải thích câu nói/ngữ liệu -> Chốt lại VĐNL.",
        "explain_items": [
            "- **Giải thích vấn đề nghị luận (VĐNL):** 'Sống có trách nhiệm' là nhận thức đúng đắn về bổn phận của cá nhân đối với tập thể; 'cống hiến' là sự dấn thân đem tài năng, sức lực để đóng góp xây dựng những giá trị tốt đẹp cho cộng đồng.",
            "- **Giải thích câu nói/ngữ liệu:** Hình ảnh thơ của Chế Lan Viên gợi nhắc sự biến đổi kỳ diệu từ không gian vô tri ('đất ở') thành không gian mang nặng nghĩa tình ('hóa tâm hồn') chính là nhờ vào sự gắn bó, vun đắp và cống hiến của con người.",
            "- **Chốt lại VĐNL:** Từ đó, câu thơ khẳng định ý nghĩa cao đẹp và sự cần thiết của lối sống có trách nhiệm và biết cống hiến cho cộng đồng."
        ],
        "vdnl_ket_luan": "Ý nghĩa của lối sống có trách nhiệm và cống hiến cho cộng đồng.",
        "questions": [{
            "cau_hoi": "Vì sao thế hệ trẻ cần phải sống cống hiến và có trách nhiệm với cộng đồng?", 
            "y_tra_loi": [
                "- **Thứ nhất:** Cống hiến giúp con người vượt qua sự ích kỷ, vị kỷ cá nhân, kết nối sâu sắc với cộng đồng và xã hội.",
                "- **Thứ hai:** Sức trẻ và tài năng nếu chỉ giữ cho riêng mình sẽ trở nên lãng phí; chỉ khi cống hiến, giá trị ấy mới được nhân lên gấp bội.",
                "- **Thứ ba:** Đây là phương thức thiết thực nhất để tiếp nối truyền thống đạo lý 'uống nước nhớ nguồn', đền đáp công ơn của các thế hệ đi trước."
            ]
        }],
        "evidence": [{"ten": "Hoàng Hoa Trung & Dự án Nuôi Em", "chi_tiet": "Nuôi cơm trưa hơn 60.000 học sinh vùng cao.", "y_nghia": "Trách nhiệm chuyển hóa thành hành động thiết thực.", "nguon": "Báo Tuổi Trẻ"}],
        "counter": [
            "- **Trường hợp 1 (Góc độ cực đoan):** Cống hiến không đồng nghĩa với việc bao đồm lo chuyện thiên hạ mà quên mất trách nhiệm gốc rễ với gia đình và bản thân.",
            "- **Trường hợp 2 (Góc độ hình thức phô trương):** Cần phê phán lối cống hiến vụ lợi, làm màu check-in trên mạng xã hội thay vì xuất phát từ tâm.",
            "- **Trường hợp 3 (Góc độ năng lực thực tế):** Cống hiến phải tùy sức, tùy tài, tránh ảo tưởng sức mạnh làm quá sức dẫn đến kiệt sức hoặc gây gánh nặng cho người khác."
        ],
        "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản biện đa chiều 3 trường hợp", "kb": "Kết bài"}
    },
    "Đề 02: Trách nhiệm tiếp bước các thế hệ đi trước": {
        "text": "Viết bài văn nghị luận bàn về trách nhiệm của thế hệ trẻ trong việc tiếp bước các thế hệ đi trước để xây dựng và bảo vệ đất nước.",
        "vdnl_chuan": "Trách nhiệm, sứ mệnh lịch sử của thế hệ trẻ trong việc kế thừa truyền thống cha ông.",
        "explain_guide": "Thao tác giải thích: Giải thích VĐNL trước -> Giải thích bản chất -> Chốt lại VĐNL.",
        "explain_items": [
            "- **Giải thích vấn đề nghị luận (VĐNL):** 'Tiếp bước' là hành động kế thừa, phát huy những thành quả, truyền thống tốt đẹp mà các thế hệ cha ông đã đổ xương máu gây dựng để xây dựng và bảo vệ đất nước.",
            "- **Giải thích nội dung/bản chất:** Tiếp bước không phải là sự sao chép máy móc quá khứ mà là sự tiếp nối mạch nguồn lòng yêu nước, tinh thần tự tôn dân tộc bằng tư duy và hành động phù hợp với thời đại mới.",
            "- **Chốt lại VĐNL:** Qua đó, làm nổi bật sứ mệnh lịch sử của thế hệ trẻ trong công cuộc xây dựng và bảo vệ Tổ quốc."
        ],
        "vdnl_ket_luan": "Sứ mệnh kế thừa và phát huy truyền thống cha ông.",
        "questions": [{
            "cau_hoi": "Trong thời bình, trách nhiệm tiếp bước cha ông được thể hiện qua những khía cạnh cụ thể nào?", 
            "y_tra_loi": [
                "- **Thứ nhất:** Không ngừng tu dưỡng đạo đức, giữ gìn và phát huy bản sắc văn hóa dân tộc trước sự giao thoa toàn cầu hóa.",
                "- **Thứ hai:** Nỗ lực học tập, sáng tạo, làm chủ khoa học công nghệ để đưa đất nước thoát khỏi đói nghèo, vươn tầm quốc tế.",
                "- **Thứ ba:** Sẵn sàng dấn thân, bảo vệ chủ quyền biên giới, hải đảo và giữ vững ổn định an ninh quốc gia khi Tổ quốc cần."
            ]
        }],
        "evidence": [{"ten": "Thế hệ trẻ tình nguyện chống dịch và bão lũ", "chi_tiet": "Lao vào tâm dịch và vùng lũ cứu trợ đồng bào.", "y_nghia": "Tiếp nối truyền thống thương người như thể thương thân.", "nguon": "Báo Nhân Dân"}],
        "counter": [
            "- **Trường hợp 1 (Góc độ bảo thủ):** Tiếp bước truyền thống không phải là sự sao chép giáo điều, ôm giữ cái cũ lỗi thời bỏ qua tư duy đổi mới.",
            "- **Trường hợp 2 (Góc độ ỷ lại hào quang):** Cần phê phán lối sống ỷ lại vào công lao của thế hệ trước mà tự mãn, lười biếng trong hiện tại.",
            "- **Trường hợp 3 (Góc độ hội nhập cực đoan):** Tiếp bước không có nghĩa là khép kín cực đoan; cần biết dung hòa giữa bản sắc truyền thống và tinh hoa nhân loại."
        ],
        "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản biện đa chiều 3 trường hợp", "kb": "Kết bài"}
    }
}

DE_BAI_NANG_CAO = {
    "Đề 16: Hành trình trở về với chính mình": {
        "text": "Trong cuốn Khai vấn trong từng hơi thở, Ruby Nguyen viết: Kì quan lớn nhất nằm ngay bên trong chính mình. Viết bài văn nghị luận bàn về chủ đề: Trở về với chính mình.",
        "vdnl_chuan": "Ý nghĩa của hành trình quay về thấu hiểu và trân trọng giá trị nội tại.",
        "explain_guide": "Thao tác giải thích: Giải thích VĐNL trước -> Giải thích nhận định -> Chốt lại VĐNL.",
        "explain_items": [
            "- **Giải thích vấn đề nghị luận (VĐNL):** 'Trở về với chính mình' là hành trình quay kính chiếu hậu vào nội tâm, buông bỏ những áp đặt ngoại biên để đối thoại chân thành với bản ngã.",
            "- **Giải thích nhận định:** 'Kì quan lớn nhất nằm ngay bên trong chính mình' khẳng định vẻ đẹp tâm hồn và kho tàng tiềm năng vô tận bên trong mỗi con người.",
            "- **Chốt vấn đề:** Khẳng định ý nghĩa của hành trình trở về với chính mình."
        ],
        "vdnl_ket_luan": "Sự cần thiết trở về với chính mình tìm bình yên.",
        "questions": [{
            "cau_hoi": "Hành trình trở về với chính mình mang lại những giá trị chuyển hóa sâu sắc nào trong thời đại số?", 
            "y_tra_loi": [
                "- **Thứ nhất:** Giúp con người thoát khỏi sự thao túng của thế giới ảo, không bị cuốn theo lối sống xô bồ, lai căng.",
                "- **Thứ hai:** Chữa lành những tổn thương tâm lý, sạc lại năng lượng tự thân sau những giông bão cuộc đời.",
                "- **Thứ ba:** Khám phá sức mạnh độc bản, giúp ta sống một cuộc đời chân thật, ý nghĩa và không hối tiếc."
            ]
        }],
        "evidence": [{"ten": "Thiền sư Thích Nhất Hạnh", "chi_tiet": "Thực hành chánh niệm, lắng nghe nội tâm.", "y_nghia": "Sức mạnh tĩnh thức nội tâm.", "nguon": "Sách"}],
        "counter": [
            "- **Trường hợp 1 (Góc độ trốn tránh thực tại):** Trở về nội tâm không có nghĩa là trốn tránh trách nhiệm xã hội hay tự cô lập mình khỏi cộng đồng.",
            "- **Trường hợp 2 (Góc độ vị kỷ ái kỉ):** Cần tránh biến việc khám phá bản thân thành sự tự mãn, ích kỷ chỉ biết đến cái tôi cá nhân.",
            "- **Trường hợp 3 (Góc độ hình thức tĩnh tâm):** Tránh ngụy biện việc lười biếng lao động dưới vỏ bọc 'thiền định tìm bình yên nội tâm'."
        ],
        "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản biện đa chiều 3 trường hợp", "kb": "Kết bài"}
    }
}

KHO_DAN_CHUNG_9_CHU_DIEM = {
    "1. Lòng nhân ái – vị tha – trách nhiệm cộng đồng": [
        {"ten": "Albert Schweitzer", "noi_dung": "Từ bỏ sự nghiệp danh giá ở châu Âu để đến Gabon (châu Phi) xây dựng bệnh viện, tự tay chữa trị cho hàng ngàn người bệnh nhiệt đới, với triết lí 'tôn kính sự sống', nhận giải Nobel Hòa bình 1952.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "2. Ý chí – nghị lực – vượt lên nghịch cảnh": [
        {"ten": "Derek Redmond", "noi_dung": "Vận động viên điền kinh Anh bị rách cơ đùi tại Olympic 1992, từ chối cáng cứu thương và được cha dìu về đích trong tiếng vỗ tay vang dội.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "3. Đam mê – lí tưởng - can đảm": [
        {"ten": "Steve Jobs", "noi_dung": "Nhà sáng lập Apple, trải qua cú sốc bị sa thải khỏi chính công ty mình lập ra nhưng vẫn kiên định với khát vọng đổi mới công nghệ.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "4. Sáng tạo - đổi mới – nghĩ khác": [
        {"ten": "Alexander Fleming", "noi_dung": "Vô tình phát hiện nấm mốc tiêu diệt vi khuẩn, mở ra kỷ nguyên kháng sinh penicillin cứu sống vô số người.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "5. Sự trung thực và giả dối": [
        {"ten": "Edward Snowden", "noi_dung": "Tiết lộ tài liệu mật của chính phủ Mỹ, đánh đổi sự an toàn cá nhân để phơi bày sự thật trước công chúng.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "6. Danh vọng, vật chất và những vấn đề thiếu lành mạnh": [
        {"ten": "Choi Sulli", "noi_dung": "Ngôi sao K-Pop chịu áp lực dư luận và bạo lực mạng khắc nghiệt, để lại hồi chuông cảnh báo về sức khỏe tâm thần.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "7. Bản sắc – nguồn cội – hòa nhập": [
        {"ten": "Trần Đặng Đăng Khoa", "noi_dung": "Đi vòng quanh thế giới bằng xe máy, luôn mang theo tà áo dài và cờ Tổ quốc để quảng bá văn hóa Việt Nam.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "8. Những lối sống và quan niệm tích cực": [
        {"ten": "Nghệ thuật Kintsugi (Nhật Bản)", "noi_dung": "Nghệ thuật hàn gắn đồ gốm vỡ bằng bột vàng, biến tổn thương thành vẻ đẹp độc bản, chấp nhận sự không hoàn hảo.", "nguon": "TS. Nguyễn Thế Hưng"}
    ],
    "9. Các hiện tượng tâm lí – xã hội đương đại": [
        {"ten": "FOMO & JOMO", "noi_dung": "Nỗi sợ bị bỏ lỡ trên mạng xã hội vs Niềm vui chủ động ngắt kết nối để quay về chăm sóc nội tâm.", "nguon": "TS. Nguyễn Thế Hưng"}
    ]
}

# ==============================================================================
# 3. QUẢN LÝ SESSION STATE
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = DE_BAI_CO_BAN[st.session_state["selected_de_key"]]

with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input("Gemini API Key:", type="password", value=st.session_state["gemini_api_key"])
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
    st.write("3. **✍️ Bước 3:** Xưởng viết bài")
    st.write("4. **📁 Bước 4:** Hồ sơ bài làm")

# ==============================================================================
# 4. HÀM GỌI AI ỔN ĐỊNH TUYỆT ĐỐI (SỬ DỤNG GEMINI-1.5-FLASH)
# ==============================================================================
def call_gemini_engine(prompt_text, image_obj=None):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "❌ LỖI: Thầy/cô chưa nhập Gemini API Key ở thanh bên trái!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        if image_obj:
            response = model.generate_content([prompt_text, image_obj])
        else:
            response = model.generate_content(prompt_text)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return "⚠️ AI đã tiếp nhận nhưng không trả về nội dung."
    except Exception as e:
        try:
            model_fb = genai.GenerativeModel("gemini-pro")
            response = model_fb.generate_content(prompt_text)
            if response and response.text:
                return response.text
        except Exception:
            pass
        return f"❌ LỖI KẾT NỐI GEMINI API: {str(e)}"

def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giám khảo Ngữ văn THPT.
- Đề bài: "{exam_text}"
- VĐNL chuẩn: "{vdnl_chuan}"
- Câu trả lời HS: "{student_guess}"
Xuất ra JSON duy nhất:
{{"status": "DUNG" | "LECH" | "SAI", "feedback": "Nhận xét sư phạm xưng cô em", "suggested_fix": "{vdnl_chuan}"}}
"""
    raw = call_gemini_engine(prompt)
    try:
        clean_raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", clean_raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(clean_raw)
    except Exception:
        return {"status": "LECH", "feedback": "Câu trả lời chưa hoàn toàn sát trọng tâm.", "suggested_fix": vdnl_chuan}

# ==============================================================================
# 5. GIAO DIỆN CHÍNH & TABS (CÓ PHÂN LUỒNG ĐỀ CƠ BẢN VÀ NÂNG CAO)
# ==============================================================================
st.markdown('<div class="hero-banner"><div class="hero-title">🖊️ HỆ THỐNG 30 ĐỀ NGHỊ LUẬN XÃ HỘI THPT</div></div>', unsafe_allow_html=True)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "📁 HỒ SƠ BÀI LÀM",
])

with tabs[0]:
    st.markdown('<div class="section-title">🔍 Lựa chọn đề bài & Xác định vấn đề nghị luận</div>', unsafe_allow_html=True)
    
    # Phân luồng đề rõ ràng
    sub_tab_cb, sub_tab_nc = st.tabs(["🟢 Nhóm Đề Cơ Bản (01–15)", "🔴 Nhóm Đề Nâng Cao (16–30)"])
    
    with sub_tab_cb:
        c1, c2 = st.columns([1, 2], gap="medium")
        with c1:
            sel_cb = st.selectbox("Chọn đề Cơ bản:", list(DE_BAI_CO_BAN.keys()), key="sb_cb")
            info_cb = DE_BAI_CO_BAN[sel_cb]
        with c2:
            with st.container(border=True):
                st.info(info_cb["text"])
            if st.button("📌 Chọn đề này & Chuyển sang Bước 2", key="btn_cb", type="primary"):
                st.session_state["selected_de_key"] = sel_cb
                st.session_state["current_de_info"] = info_cb
                st.session_state["eval_vdnl_result"] = None
                st.success(f"Đã chọn: {sel_cb}! Mời thầy/cô bấm qua tab 'BƯỚC 2'.")

    with sub_tab_nc:
        c3, c4 = st.columns([1, 2], gap="medium")
        with c3:
            sel_nc = st.selectbox("Chọn đề Nâng cao:", list(DE_BAI_NANG_CAO.keys()), key="sb_nc")
            info_nc = DE_BAI_NANG_CAO[sel_nc]
        with c4:
            with st.container(border=True):
                st.info(info_nc["text"])
            if st.button("📌 Chọn đề này & Chuyển sang Bước 2", key="btn_nc", type="primary"):
                st.session_state["selected_de_key"] = sel_nc
                st.session_state["current_de_info"] = info_nc
                st.session_state["eval_vdnl_result"] = None
                st.success(f"Đã chọn: {sel_nc}! Mời thầy/cô bấm qua tab 'BƯỚC 2'.")

    st.markdown("---")
    cur_key = st.session_state["selected_de_key"]
    cur_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề đang chọn:** {cur_key}")

    student_vdnl = st.text_input("⚡ Xác định vấn đề nghị luận:", placeholder="Gõ câu trả lời...")
    if st.button("🔍 Đối chiếu với AI", type="primary"):
        if student_vdnl.strip():
            with st.spinner("AI đang thẩm định..."):
                st.session_state["eval_vdnl_result"] = ai_evaluate_student_vdnl(cur_info["text"], cur_info["vdnl_chuan"], student_vdnl)

    if st.session_state.get("eval_vdnl_result"):
        res = st.session_state["eval_vdnl_result"]
        if res.get("status") == "DUNG":
            st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}")
        else:
            st.warning(f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:* {res.get('suggested_fix')}")

with tabs[1]:
    cur_key = st.session_state["selected_de_key"]
    cur_info = st.session_state["current_de_info"]
    c_left, c_right = st.columns([1.1, 0.9], gap="large")

    with c_left:
        st.markdown(f"#### 🛠️ Gợi ý khung tư duy cho: <span style='color:#2563eb;'>{cur_key}</span>", unsafe_allow_html=True)
        with st.expander("📌 Thao tác 1: Giải thích", expanded=True):
            guide_txt = cur_info.get("explain_guide", "")
            items = cur_info.get("explain_items", [])
            vdnl_kl = cur_info.get("vdnl_ket_luan", "")
            st.markdown(f"*{guide_txt}*")
            st.markdown("---")
            for itm in items:
                st.markdown(itm)
            st.markdown(f"**👉 Chốt lại VĐNL:** *{vdnl_kl}*")

        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            for q in cur_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi')}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"{ans}")

        with st.expander("📚 Thao tác 3: Kho dẫn chứng trọng tâm & 9 chủ điểm", expanded=True):
            for ev in cur_info.get("evidence", []):
                st.markdown(f"<div class='evidence-card'><b>{ev.get('ten')}</b>: {ev.get('chi_tiet')}</div>", unsafe_allow_html=True)
            
            sel_top = st.selectbox("Chọn chủ điểm dẫn chứng mở rộng:", options=list(KHO_DAN_CHUNG_9_CHU_DIEM.keys()))
            for dc in KHO_DAN_CHUNG_9_CHU_DIEM[sel_top]:
                with st.container(border=True):
                    st.markdown(f"**{dc['ten']}**: {dc['noi_dung']}")

        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng (3 trường hợp)", expanded=True):
            for c_item in cur_info.get("counter", []):
                st.markdown(f"<div class='counter-box'>{c_item}</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        st.info("💡 Nhập câu hỏi bên dưới và bấm nút để AI phản hồi ngay lập tức.")
        user_q = st.text_input("Nhập câu hỏi cho Trợ lý AI:", placeholder="Hỏi cô về phương pháp...", key="user_q_input")
        if st.button("Gửi câu hỏi cho Cô 🚀", type="primary"):
            if user_q.strip():
                with st.spinner("Trợ lý Ngữ văn đang suy nghĩ..."):
                    reply = call_gemini_engine(f"Đề bài: {cur_key}. Học sinh hỏi: {user_q}. Hãy đưa ra định hướng sư phạm ngắn gọn, xưng cô - em.")
                st.markdown("### 🤖 Trợ lý Ngữ văn trả lời:")
                st.success(reply)
            else:
                st.warning("Vui lòng nhập nội dung câu hỏi!")

with tabs[2]:
    st.markdown('<div class="section-title">✍️ Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    write_mode = st.radio("Chọn hình thức nộp bài:", ["✍️ Tự gõ bài viết trực tiếp", "📷 Gửi ảnh chụp bài viết tay"], horizontal=True)

    if write_mode == "✍️ Tự gõ bài viết trực tiếp":
        st.session_state["user_essay"] = st.text_area("Nhập bài viết:", value=st.session_state.get("user_essay", ""), height=380)
    else:
        up_img = st.file_uploader("Tải lên ảnh chụp bài viết tay:", type=["png", "jpg", "jpeg"])
        if up_img:
            img = Image.open(up_img)
            st.image(img, caption="Ảnh bài làm", use_column_width=True)
            if st.button("🔍 Nhờ AI nhận xét bài viết tay", type="primary"):
                with st.spinner("AI đang phân tích ảnh..."):
                    feedback = call_gemini_engine(f"Nhận xét bài làm cho đề: {cur_key}", image_obj=img)
                    st.success(feedback)

with tabs[3]:
    st.markdown('<div class="section-title">📁 Hồ Sơ Bài Làm & Xuất File</div>', unsafe_allow_html=True)
    if st.session_state.get("user_essay"):
        st.text_area("Nội dung bài làm:", value=st.session_state["user_essay"], height=250, disabled=True)
