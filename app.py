import base64
import io
import json
import re
import urllib.error
import urllib.request
import google.generativeai as genai
import streamlit as st
import data_de_bai as db
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP & CHUẨN SƯ PHẠM
# ==============================================================================
st.set_page_config(
    page_title="Hệ Thống Luyện Viết NLXH THPT",
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
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px !important;
        color: #ffffff !important;
    }

    .hero-subtitle {
        font-size: 0.95rem;
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
# 2. QUẢN LÝ SESSION STATE
# ==============================================================================
def get_default_api_key():
    try:
        for k in ["gemini_api_key", "GEMINI_API_KEY", "GOOGLE_API_KEY"]:
            if k in st.secrets and st.secrets[k]:
                return str(st.secrets[k]).strip()
    except Exception:
        pass
    return ""

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = get_default_api_key()

if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[st.session_state["selected_de_key"]]

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em có thắc mắc gì về cách giải thích, tìm ý bàn luận hay chọn dẫn chứng cho đề bài này thì cứ hỏi cô nhé!")
    ]

if "user_essay" not in st.session_state:
    st.session_state["user_essay"] = ""

if "rubric_evaluation" not in st.session_state:
    st.session_state["rubric_evaluation"] = ""

if "eval_vdnl_text" not in st.session_state:
    st.session_state["eval_vdnl_text"] = ""


# ==============================================================================
# 3. ĐỘNG CƠ GỌI AI QUA GIAO THỨC HTTPS REST (CHỐNG TREO 100% TRÊN STREAMLIT CLOUD)
# ==============================================================================
def call_gemini_engine(prompt_text, image_obj=None):
    """
    Gọi trực tiếp Gemini REST API qua HTTPS chuẩn với timeout=25s.
    Giải quyết triệt để lỗi treo gRPC (vòng quay vô tận) trên Streamlit Cloud.
    """
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        api_key = get_default_api_key()
        if api_key:
            st.session_state["gemini_api_key"] = api_key

    if not api_key:
        return "❌ LỖI: Chưa có Gemini API Key. Vui lòng nhập API Key ở thanh cấu hình bên trái!"

    # Chuẩn bị nội dung gửi đi (Text hoặc Text + Ảnh bài làm)
    parts = [{"text": prompt_text}]
    if image_obj is not None:
        try:
            buffered = io.BytesIO()
            img_rgb = image_obj.convert("RGB")
            img_rgb.save(buffered, format="JPEG", quality=85)
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_b64
                }
            })
        except Exception as e:
            return f"❌ Lỗi xử lý ảnh tải lên: {str(e)}"

    payload = {
        "contents": [{"parts": parts}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
        }
    }
    data_bytes = json.dumps(payload).encode("utf-8")

    # Danh sách các model Gemini qua cổng HTTPS REST (tự động chuyển đổi nếu model đầu bận)
    rest_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
    ]

    last_error = ""
    for model_name in rest_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                resp_body = resp.read().decode("utf-8")
                result_json = json.loads(resp_body)
                candidates = result_json.get("candidates", [])
                if candidates:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    texts = [p.get("text", "") for p in content_parts if "text" in p]
                    final_text = "".join(texts).strip()
                    if final_text:
                        return final_text
        except urllib.error.HTTPError as http_err:
            try:
                err_detail = http_err.read().decode("utf-8")
                err_json = json.loads(err_detail)
                err_msg = err_json.get("error", {}).get("message", str(http_err))
            except Exception:
                err_msg = str(http_err)
            last_error = f"HTTP {http_err.code} ({model_name}): {err_msg}"
            # Nếu lỗi do API Key sai hoàn toàn thì dừng ngay để báo cho người dùng
            if "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg:
                return "❌ LỖI: Gemini API Key không hợp lệ hoặc bị sai ký tự. Thầy/cô vui lòng kiểm tra lại mã Key ở thanh bên trái!"
            continue
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            continue

    # Phương án dự phòng cuối cùng qua SDK với transport="rest" (tắt hẳn gRPC)
    try:
        genai.configure(api_key=api_key, transport="rest")
        model = genai.GenerativeModel("gemini-1.5-flash")
        content = [prompt_text, image_obj] if image_obj is not None else prompt_text
        resp = model.generate_content(content)
        if resp and hasattr(resp, "text") and resp.text:
            return resp.text.strip()
    except Exception as e:
        last_error = str(e)

    return f"❌ Không thể kết nối với AI ({last_error}). Vui lòng kiểm tra lại Gemini API Key ở thanh bên trái!"


def extract_section(text, tag_name):
    pattern = rf"\[{tag_name}\](.*?)\[/{tag_name}\]"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def ai_evaluate_student_vdnl(exam_text, vdnl_chuan, student_guess):
    prompt = f"""
Bạn là Giáo viên Ngữ văn THPT giàu kinh nghiệm (xưng cô, gọi học sinh là em).
- Đề bài: "{exam_text}"
- Vấn đề nghị luận chuẩn của đề: "{vdnl_chuan}"
- Câu trả lời xác định vấn đề nghị luận của học sinh: "{student_guess}"

Hãy nhận xét ngắn gọn (3-4 câu):
1. Đánh giá câu trả lời của em đã ĐÚNG TRỌNG TÂM, CÒN THIẾU SÓT hay CHƯA CHÍNH XÁC.
2. Chỉ ra điểm em làm tốt hoặc điểm cần bổ sung.
3. Chốt lại Vấn đề nghị luận chuẩn xác cho em: "{vdnl_chuan}".
"""
    return call_gemini_engine(prompt)


def ai_analyze_custom_exam(exam_text, student_guess):
    prompt = f"""
Bạn là Giáo viên Ngữ văn THPT chuyên luyện thi Nghị luận xã hội (xưng cô - em).
Hãy phân tích đề bài tự nhập sau đây:
\"\"\"{exam_text}\"\"\"
Học sinh tự xác định vấn đề nghị luận là: "{student_guess if student_guess else 'Chưa nhập'}"

YÊU CẦU BẮT BUỘC: Trả lời ngắn gọn, súc tích theo ĐÚNG các thẻ đánh dấu dưới đây (giữ nguyên tên thẻ trong ngoặc vuông):

[NHAN_XET_VDNL]
Nhận xét câu trả lời xác định VĐNL của học sinh (Đúng/Chưa đầy đủ/Lệch hướng) và khích lệ sư phạm.
[/NHAN_XET_VDNL]

[VDNL_CHUAN]
Nêu 1 câu ngắn gọn, chuẩn xác nhất về vấn đề nghị luận của đề bài trên.
[/VDNL_CHUAN]

[GIAI_THICH]
- **Giải thích vấn đề nghị luận:** (Giải thích các từ khóa, khái niệm chính của VĐNL)
- **Giải thích câu nói/ngữ liệu:** (Giải thích ý nghĩa nhận định hoặc ngữ liệu trong đề bài; nếu đề không có trích dẫn thì làm rõ biểu hiện thực tế của vấn đề)
- **Chốt lại vấn đề nghị luận:** (Khái quát tổng kết bản chất vấn đề cần bàn luận)
[/GIAI_THICH]

[CAU_HOI_BAN_LUAN]
Nêu 1 câu hỏi trọng tâm nhất cho phần Bàn luận.
[/CAU_HOI_BAN_LUAN]

[Y_BAN_LUAN]
- (Luận điểm bàn luận sâu sắc thứ 1)
- (Luận điểm bàn luận sâu sắc thứ 2)
- (Luận điểm bàn luận sâu sắc thứ 3)
- (Luận điểm bàn luận sâu sắc thứ 4)
[/Y_BAN_LUAN]

[DAN_CHUNG]
Tên nhân vật/sự kiện tiêu biểu | Chi tiết cụ thể của dẫn chứng | Ý nghĩa làm sáng tỏ vấn đề | Nguồn dẫn chứng
[/DAN_CHUNG]

[PHAN_BIEN]
- **Trường hợp 1 (Phê phán mặt trái):** (Phê phán những biểu hiện trái ngược, tiêu cực trong xã hội)
- **Trường hợp 2 (Phân biệt tránh cực đoan):** (Phân biệt vấn đề với những nhận thức lệch lạc, cực đoan hoặc hình thức)
- **Trường hợp 3 (Đặt trong điều kiện thực tế):** (Mở rộng điều kiện để vấn đề phát huy giá trị tốt nhất trong thực tiễn)
[/PHAN_BIEN]

[DAN_Y]
MB: (Hướng dẫn dẫn dắt và nêu VĐNL ở Mở bài)
GT: (Hướng dẫn triển khai bước Giải thích: VĐNL -> Câu nói -> Chốt VĐNL)
BL: (Hướng dẫn triển khai các luận điểm Bàn luận trọng tâm)
DC: (Hướng dẫn đưa và phân tích Dẫn chứng thực tế)
PB: (Hướng dẫn triển khai 3 trường hợp Phản biện mở rộng)
KB: (Hướng dẫn khẳng định lại vấn đề và rút ra bài học nhận thức, hành động ở Kết bài)
[/DAN_Y]
"""
    raw = call_gemini_engine(prompt)
    if raw.startswith("❌"):
        return None, raw

    vdnl_chuan = extract_section(raw, "VDNL_CHUAN") or (student_guess if student_guess else "Vấn đề nghị luận trọng tâm của đề bài.")
    nhan_xet = extract_section(raw, "NHAN_XET_VDNL") or "Cô đã tiếp nhận câu trả lời của em. Em hãy đối chiếu với khung định hướng chuẩn bên dưới nhé."
    
    gt_raw = extract_section(raw, "GIAI_THICH")
    explain_items = [line.strip() for line in gt_raw.split("\n") if line.strip()]
    if not explain_items:
        explain_items = [
            "- **Giải thích vấn đề nghị luận:** Làm rõ nghĩa của từ khóa trọng tâm trong đề bài.",
            "- **Giải thích câu nói/ngữ liệu:** Phân tích ý nghĩa thông điệp của nhận định/ngữ liệu.",
            "- **Chốt lại vấn đề nghị luận:** Khái quát nội dung cốt lõi cần bàn luận."
        ]

    cau_hoi_bl = extract_section(raw, "CAU_HOI_BAN_LUAN") or "Vì sao vấn đề này lại có ý nghĩa quan trọng đối với mỗi cá nhân và xã hội?"
    y_bl_raw = extract_section(raw, "Y_BAN_LUAN")
    y_tra_loi = [line.strip() for line in y_bl_raw.split("\n") if line.strip()]
    if len(y_tra_loi) < 3:
        y_tra_loi = [
            "- Giúp mỗi cá nhân nâng cao nhận thức, hoàn thiện nhân cách và định hướng hành động đúng đắn.",
            "- Tạo động lực vượt qua khó khăn, phát huy tối đa giá trị bản thân trong cuộc sống hiện đại.",
            "- Góp phần lan tỏa những giá trị tích cực, xây dựng cộng đồng văn minh và giàu tính nhân văn."
        ]

    dc_raw = extract_section(raw, "DAN_CHUNG")
    dc_parts = [p.strip() for p in dc_raw.split("|")]
    if len(dc_parts) >= 3:
        ev_item = {
            "ten": dc_parts[0],
            "chi_tiet": dc_parts[1],
            "y_nghia": dc_parts[2],
            "nguon": dc_parts[3] if len(dc_parts) > 3 else "Thực tế đời sống & Báo chí"
        }
    else:
        ev_item = {
            "ten": "Dẫn chứng thực tế tiêu biểu",
            "chi_tiet": dc_raw if dc_raw else "Lựa chọn tấm gương tiêu biểu trong Kho dẫn chứng 9 chủ điểm bên dưới.",
            "y_nghia": "Làm sáng tỏ và tăng sức thuyết phục cho các luận điểm bàn luận.",
            "nguon": "Kho dẫn chứng NLXH"
        }

    pb_raw = extract_section(raw, "PHAN_BIEN")
    counter_items = [line.strip() for line in pb_raw.split("\n") if line.strip()]
    if len(counter_items) < 3:
        counter_items = [
            "- **Trường hợp 1 (Phê phán mặt trái):** Phê phán những người có nhận thức và hành động đi ngược lại giá trị tích cực của vấn đề.",
            "- **Trường hợp 2 (Phân biệt tránh cực đoan):** Cần tránh việc hiểu hoặc áp dụng vấn đề một cách máy móc, cực đoan hay phô trương hình thức.",
            "- **Trường hợp 3 (Đặt trong điều kiện thực tế):** Cần kết hợp hài hòa giữa nhận thức và hành động thực tiễn phù hợp với hoàn cảnh."
        ]

    dany_raw = extract_section(raw, "DAN_Y")
    dani_dict = {
        "mb": "Dẫn dắt và giới thiệu chính xác vấn đề nghị luận.",
        "gt": "Giải thích vấn đề nghị luận trước, giải thích câu nói/ngữ liệu, sau đó chốt lại VĐNL.",
        "bl": "Triển khai hệ thống các luận điểm bàn luận sâu sắc, đa chiều.",
        "dc": "Đưa dẫn chứng thực tế xác thực và phân tích gắn liền với luận điểm.",
        "pb": "Mở rộng, lật lại vấn đề theo 3 trường hợp phản biện để bài viết chặt chẽ.",
        "kb": "Khẳng định lại giá trị của vấn đề và rút ra bài học nhận thức, hành động cho bản thân."
    }
    for line in dany_raw.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            k_clean = k.strip().upper().replace("-", "").replace("*", "").strip()
            if k_clean in ["MB", "GT", "BL", "DC", "PB", "KB"] and v.strip():
                dani_dict[k_clean.lower()] = v.strip()

    info_custom = {
        "text": exam_text,
        "vdnl_chuan": vdnl_chuan,
        "explain_guide": "Giải thích vấn đề nghị luận trước, sau đó giải thích câu nói/ngữ liệu và chốt lại vấn đề.",
        "explain_items": explain_items,
        "vdnl_ket_luan": vdnl_chuan,
        "questions": [{"cau_hoi": cau_hoi_bl, "y_tra_loi": y_tra_loi}],
        "evidence": [ev_item],
        "counter": counter_items,
        "dani_chi_tiet": dani_dict,
    }
    return info_custom, f"**🎯 Nhận xét của Cô:** {nhan_xet}\n\n**👉 Vấn đề nghị luận chuẩn xác:** {vdnl_chuan}"


def ai_evaluate_essay_rubric(de_key, de_info, essay_text=None, image_obj=None):
    rubric_prompt = f"""
Bạn là Giám khảo và Giáo viên Ngữ văn THPT giàu kinh nghiệm, tận tâm (xưng cô - gọi học sinh là em).
Hãy kiểm tra, đánh giá và hướng dẫn học sinh chỉnh sửa bài văn Nghị luận xã hội sau đây theo THANG RUBRIC CHUẨN.

- Đề bài: "{de_info.get('text', de_key)}"
- Vấn đề nghị luận trọng tâm: "{de_info.get('vdnl_chuan', '')}"
"""
    if essay_text:
        rubric_prompt += f"\n- Bài làm của học sinh:\n\"\"\"{essay_text}\"\"\"\n"
    else:
        rubric_prompt += "\n- Bài làm của học sinh được chụp trong hình ảnh đính kèm. Trước hết hãy đọc kỹ toàn bộ chữ viết tay trong ảnh.\n"

    rubric_prompt += """
YÊU CẦU ĐẦU RA BẮT BUỘC:
Hãy trình bày kết quả đánh giá đầy đủ, rõ ràng gồm 3 phần sau:

### 📊 1. BẢNG ĐÁNH GIÁ THEO TIÊU CHÍ RUBRIC NGHỊ LUẬN XÃ HỘI
Hãy kẻ bảng Markdown gồm 4 cột: **Tiêu chí đánh giá | Mức độ đạt được (Tốt / Đạt / Cần cố gắng) | Điểm ước lượng | Nhận xét chi tiết từ bài làm của em** cho 6 tiêu chí sau:
1. **Đảm bảo cấu trúc bài văn nghị luận (0.5 điểm):** Đủ 3 phần Mở bài, Thân bài, Kết bài; chia đoạn hợp lý, có sự liên kết mạch lạc.
2. **Xác định & Giải thích đúng vấn đề nghị luận (1.0 điểm):** Mở bài nêu đúng VĐNL; Thân bài giải thích đúng trình tự (Giải thích VĐNL -> Giải thích câu nói/ngữ liệu -> Chốt VĐNL).
3. **Hệ thống luận điểm bàn luận trọng tâm (2.0 điểm):** Có từ 3 luận điểm bàn luận sâu sắc trở lên, lập luận chặt chẽ, thuyết phục.
4. **Dẫn chứng thực tế (0.5 điểm):** Dẫn chứng tiêu biểu, xác thực, cập nhật và có phân tích gắn với luận điểm (không kể lể lan man).
5. **Tư duy phản biện, mở rộng & Bài học (0.5 điểm):** Có lật lại vấn đề đa chiều (phê phán mặt trái, tránh cực đoan, điều kiện thực tế) và rút ra bài học nhận thức, hành động chân thành.
6. **Chính tả, dùng từ, ngữ pháp & Sáng tạo (0.5 điểm):** Diễn đạt trong sáng, giàu hình ảnh/cảm xúc, không mắc lỗi chính tả hay ngữ pháp.
*(Cuối bảng có dòng **TỔNG ĐIỂM ĐÁNH GIÁ** trên thang điểm 5.0 hoặc quy đổi thang 10.0)*

### 🌟 2. NHỮNG ĐIỂM SÁNG ĐÁNG KHEN TRONG BÀI VIẾT CỦA EM
- Chỉ ra cụ thể những câu văn, ý tưởng hoặc cách lập luận tốt mà học sinh đã viết được.

### ✍️ 3. HƯỚNG DẪN KIỂM TRA VÀ CHỈNH SỬA CỤ THỂ (CẦM TAY CHỈ VIỆC)
- Chỉ rõ từng đoạn/câu còn yếu hoặc thiếu sót trong bài của học sinh.
- Gợi ý cách viết lại hoặc bổ sung ý (theo đúng tinh thần sư phạm: định hướng và làm mẫu 1-2 câu nâng cấp diễn đạt để học sinh tự hoàn thiện bài viết).
"""
    return call_gemini_engine(rubric_prompt, image_obj=image_obj)


# ==============================================================================
# 4. THANH BÊN (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH HỆ THỐNG")
    api_key_input = st.text_input(
        "Nhập Gemini API Key:",
        type="password",
        value=st.session_state["gemini_api_key"],
        help="Nhập khóa API từ Google AI Studio để kích hoạt toàn bộ tính năng AI.",
    )
    if api_key_input.strip() != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = api_key_input.strip()

    if st.session_state["gemini_api_key"]:
        st.success("✅ Trợ lý Ngữ văn AI đã sẵn sàng!")
        if st.button("🔌 Kiểm tra kết nối AI ngay"):
            with st.spinner("Đang kiểm tra kết nối qua cổng HTTPS REST..."):
                test_res = call_gemini_engine("Hãy trả lời ngắn gọn đúng 1 câu: Kết nối thành công!")
                if test_res.startswith("❌"):
                    st.error(test_res)
                else:
                    st.info(f"🎯 Phản hồi từ AI: {test_res}")
    else:
        st.warning("⚠️ Vui lòng nhập Gemini API Key để kích hoạt AI.")

    st.markdown("---")
    st.markdown("### 📌 QUY TRÌNH 4 BƯỚC SƯ PHẠM")
    st.markdown("1. **🌱 Bước 1:** Tìm hiểu đề & Xác định VĐNL")
    st.markdown("2. **🧵 Bước 2:** Tìm ý, Lập dàn ý & Kho dẫn chứng")
    st.markdown("3. **✍️ Bước 3:** Xưởng viết bài độc lập")
    st.markdown("4. **📊 Bước 4:** Kiểm tra & Chỉnh sửa (Rubric)")


# ==============================================================================
# 5. GIAO DIỆN CHÍNH & 4 BƯỚC SƯ PHẠM
# ==============================================================================
st.markdown(
    """
<div class="hero-banner">
    <div class="hero-title">🖊️ HỆ THỐNG LUYỆN VIẾT NGHỊ LUẬN XÃ HỘI THPT</div>
    <p class="hero-subtitle">Đồng hành phát triển tư duy phản biện và kỹ năng viết văn nghị luận chuẩn mực theo quy trình 4 bước sư phạm</p>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "📊 BƯỚC 4: KIỂM TRA & CHỈNH SỬA (RUBRIC)",
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ (PHÂN LUỒNG 15 CƠ BẢN - 15 NÂNG CAO - ĐỀ TỰ NHẬP)
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown(
        '<div class="section-title">🔍 Bước 1: Lựa chọn đề bài & Xác định vấn đề nghị luận</div>',
        unsafe_allow_html=True,
    )

    tab_de_coban, tab_de_nangcao, tab_de_tu_nhap = st.tabs([
        "🟢 Nhóm Đề Cơ Bản (Đề 01 – Đề 15)",
        "🔴 Nhóm Đề Nâng Cao (Đề 16 – Đề 30)",
        "✏️ Nhập / Dán Đề Bài Riêng",
    ])

    with tab_de_coban:
        col_cb1, col_cb2 = st.columns([1, 2], gap="medium")
        with col_cb1:
            selected_cb_key = st.selectbox(
                "Chọn đề trong nhóm Cơ bản (15 đề):",
                list(db.DE_BAI_CO_BAN.keys()),
                key="sb_coban",
            )
            de_info_cb = db.DE_BAI_CO_BAN[selected_cb_key]
        with col_cb2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_cb["text"])

            if st.button(
                "📌 Chọn đề Cơ bản này để luyện tập",
                key="btn_chon_cb",
                type="primary",
            ):
                st.session_state["selected_de_key"] = selected_cb_key
                st.session_state["current_de_info"] = de_info_cb
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_cb_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang **BƯỚC 2**.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox(
                "Chọn đề trong nhóm Nâng cao (15 đề):",
                list(db.DE_BAI_NANG_CAO.keys()),
                key="sb_nangcao",
            )
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
        with col_nc2:
            with st.container(border=True):
                st.markdown("##### 📖 Nội dung đề bài:")
                st.info(de_info_nc["text"])

            if st.button(
                "📌 Chọn đề Nâng cao này để luyện tập",
                key="btn_chon_nc",
                type="primary",
            ):
                st.session_state["selected_de_key"] = selected_nc_key
                st.session_state["current_de_info"] = de_info_nc
                st.session_state["eval_vdnl_text"] = ""
                st.success(f"✅ Đã chọn: **{selected_nc_key}**! Hãy xác định VĐNL bên dưới rồi chuyển sang **BƯỚC 2**.")

    with tab_de_tu_nhap:
        st.markdown("##### ✏️ Nhập đề bài bất kỳ của thầy/cô hoặc học sinh để AI thiết lập khung định hướng:")
        custom_de_text = st.text_area(
            "Nội dung đề bài tự nhập:",
            placeholder="Ví dụ: Cuộc sống tốt đẹp hay tồi tệ chính là do cách bạn nhìn nhận về nó. Viết bài văn nghị luận (khoảng 600 chữ) bày tỏ suy nghĩ của anh/chị...",
            height=110,
            key="txt_custom_de",
        )
        student_custom_vdnl = st.text_input(
            "Theo em, vấn đề nghị luận của đề bài này là gì?",
            placeholder="Nhập câu trả lời dự đoán của em trước khi AI phân tích...",
            key="txt_custom_vdnl",
        )
        if st.button("🔍 Phân tích đề tự nhập & Tạo khung định hướng Bước 2", type="primary", key="btn_custom_analyze"):
            if not custom_de_text.strip():
                st.warning("⚠️ Vui lòng nhập nội dung đề bài trước khi bấm phân tích!")
            else:
                with st.spinner("🤖 Cô giáo AI đang phân tích đề bài (chỉ mất khoảng 3-5 giây)..."):
                    info_custom, feedback_msg = ai_analyze_custom_exam(custom_de_text.strip(), student_custom_vdnl.strip())
                    if info_custom is None:
                        st.error(feedback_msg)
                    else:
                        short_title = custom_de_text.strip()[:55] + ("..." if len(custom_de_text.strip()) > 55 else "")
                        st.session_state["selected_de_key"] = f"Đề tự nhập: {short_title}"
                        st.session_state["current_de_info"] = info_custom
                        st.session_state["eval_vdnl_text"] = feedback_msg
                        st.success("✅ Đã phân tích xong! Em hãy xem nhận xét VĐNL ngay bên dưới và bấm sang tab **BƯỚC 2** để xem toàn bộ khung định hướng chi tiết.")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài đang làm việc:** {cur_active_key}\n\n*Nội dung đề:* {cur_active_info.get('text', '')}")

    if not cur_active_key.startswith("Đề tự nhập:"):
        student_vdnl = st.text_input(
            "⚡ Thao tác học sinh: Hãy xác định vấn đề nghị luận của đề bài đang chọn:",
            placeholder="Gõ câu trả lời của em vào đây để đối chiếu với AI...",
            key="input_vdnl_b1",
        )
        col_b1_a, col_b1_b = st.columns([1, 1])
        with col_b1_a:
            if st.button("🤖 Đối chiếu câu trả lời với Trợ lý AI", type="primary"):
                if student_vdnl.strip():
                    with st.spinner("Cô giáo AI đang nhận xét câu trả lời của em..."):
                        res_text = ai_evaluate_student_vdnl(
                            cur_active_info["text"],
                            cur_active_info["vdnl_chuan"],
                            student_vdnl.strip(),
                        )
                        st.session_state["eval_vdnl_text"] = res_text
                else:
                    st.warning("⚠️ Em hãy nhập câu trả lời trước khi bấm đối chiếu nhé!")
        with col_b1_b:
            if st.button("👁️ Xem ngay Vấn đề nghị luận chuẩn của đề"):
                st.session_state["eval_vdnl_text"] = f"🎯 **Vấn đề nghị luận chuẩn xác của đề bài là:**\n\n{cur_active_info['vdnl_chuan']}"

    if st.session_state.get("eval_vdnl_text"):
        with st.container(border=True):
            st.markdown(st.session_state["eval_vdnl_text"])


# ------------------------------------------------------------------------------
# BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG + TRỢ LÝ AI TƯ VẤN
# ------------------------------------------------------------------------------
with tabs[1]:
    cur_de_key = st.session_state["selected_de_key"]
    cur_de_info = st.session_state["current_de_info"]

    c_left, c_right = st.columns([1.15, 0.85], gap="large")

    with c_left:
        st.markdown(
            f"#### 🛠️ Khung định hướng tư duy cho: <span style='color:#2563eb;'>{cur_de_key}</span>",
            unsafe_allow_html=True,
        )

        # Thao tác 1: Giải thích (VĐNL -> Câu nói -> Chốt lại VĐNL)
        with st.expander("📌 Thao tác 1: Giải thích (Vấn đề nghị luận ➔ Câu nói/Ngữ liệu ➔ Chốt vấn đề)", expanded=True):
            with st.container(border=True):
                for itm in cur_de_info.get("explain_items", []):
                    st.markdown(itm)
                st.markdown("---")
                st.markdown(f"**👉 Chốt lại vấn đề nghị luận:** {cur_de_info.get('vdnl_ket_luan', '')}")

        # Thao tác 2: Bàn luận trọng tâm
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            with st.container(border=True):
                for q in cur_de_info.get("questions", []):
                    st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                    for ans in q.get("y_tra_loi", []):
                        st.markdown(ans)

        # Thao tác 3: Kho dẫn chứng
        with st.expander("📚 Thao tác 3: Dẫn chứng thực tế & Kho dẫn chứng 9 chủ điểm", expanded=True):
            st.markdown("##### 📌 Dẫn chứng gợi ý trực tiếp cho đề bài:")
            for ev in cur_de_info.get("evidence", []):
                if isinstance(ev, dict):
                    st.markdown(
                        f"""
                        <div class='evidence-card'>
                            <h5 style='margin:0 0 6px 0; color:#15803d;'>👤 {ev.get('ten', '')}</h5>
                            <p style='margin:0 0 6px 0;'><b>• Chi tiết:</b> {ev.get('chi_tiet', '')}</p>
                            <p style='margin:0 0 6px 0;'><b>• Ý nghĩa:</b> {ev.get('y_nghia', '')}</p>
                            <p style='margin:0; font-size:0.85rem; color:#64748b;'>📰 <i>Nguồn: {ev.get('nguon', '')}</i></p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("---")
            st.markdown("##### 📚 Tra cứu Kho dẫn chứng mở rộng (9 nhóm chủ điểm):")
            selected_topic = st.selectbox(
                "Chọn chủ điểm dẫn chứng cần tham khảo:",
                options=list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()),
                key="sb_kho_dc",
            )
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"**👤 {dc['ten']}**")
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 Nguồn: {dc['nguon']}")

        # Thao tác 4: Phản biện & Mở rộng (3 trường hợp)
        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng vấn đề (3 trường hợp đa chiều)", expanded=True):
            with st.container(border=True):
                for c_item in cur_de_info.get("counter", []):
                    st.markdown(c_item)

        # Định hướng dàn ý 3 phần
        with st.expander("📝 Định hướng bố cục Dàn ý chi tiết 3 phần (Mở bài - Thân bài - Kết bài)", expanded=True):
            dani_data = cur_de_info.get("dani_chi_tiet", {})
            with st.container(border=True):
                st.markdown("##### 🌟 I. MỞ BÀI")
                st.markdown(f"- {dani_data.get('mb', 'Dẫn dắt và nêu chính xác vấn đề nghị luận.')}")
                st.markdown("##### 🌟 II. THÂN BÀI")
                st.markdown(f"- **1. Giải thích:** {dani_data.get('gt', '')}")
                st.markdown(f"- **2. Bàn luận trọng tâm:** {dani_data.get('bl', '')}")
                st.markdown(f"- **3. Chứng minh (Dẫn chứng):** {dani_data.get('dc', '')}")
                st.markdown(f"- **4. Phản biện & Mở rộng:** {dani_data.get('pb', '')}")
                st.markdown("##### 🌟 III. KẾT BÀI")
                st.markdown(f"- {dani_data.get('kb', 'Khẳng định lại vấn đề và liên hệ bài học bản thân.')}")

    # CỘT PHẢI: TRỢ LÝ NGỮ VĂN AI TƯ VẤN (HIỂN THỊ TRỰC TIẾP KHÔNG DÙNG RERUN GÂY KẸT)
    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        st.caption("Cô giáo AI luôn sẵn sàng giải đáp thắc mắc, gợi mở ý tưởng và hướng dẫn cách lập luận cho em.")

        user_question = st.text_area(
            "Nhập câu hỏi của em dành cho Cô:",
            placeholder="Ví dụ: Cô ơi gợi ý giúp em thêm dẫn chứng hoặc cách viết mở bài cho đề này ạ...",
            height=90,
            key="txt_chat_input",
        )

        col_chat_1, col_chat_2 = st.columns([2, 1])
        with col_chat_1:
            send_clicked = st.button("🚀 Gửi câu hỏi cho Cô", type="primary", use_container_width=True)
        with col_chat_2:
            clear_clicked = st.button("🗑️ Xóa lịch sử", use_container_width=True)

        if clear_clicked:
            st.session_state["chat_history"] = [
                ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em có thắc mắc gì về đề bài này cứ hỏi cô nhé!")
            ]

        if send_clicked:
            if not user_question.strip():
                st.warning("⚠️ Em hãy nhập câu hỏi trước khi bấm gửi nhé!")
            else:
                q_clean = user_question.strip()
                st.session_state["chat_history"].append(("user", q_clean))
                prompt_advisor = f"""
Bạn là Giáo viên Ngữ văn THPT giàu kinh nghiệm, tâm lý (xưng cô - gọi học sinh là em).
Nguyên tắc sư phạm: Định hướng tư duy, gợi mở phương pháp, gợi ý dẫn chứng hoặc làm mẫu câu ngắn gọn chứ không viết hộ toàn bộ bài văn.
- Đề bài học sinh đang làm: "{cur_de_info.get('text', cur_de_key)}"
- Vấn đề nghị luận: "{cur_de_info.get('vdnl_chuan', '')}"
- Câu hỏi của học sinh: "{q_clean}"

Hãy trả lời rõ ràng, sâu sắc, dễ hiểu để hỗ trợ học sinh:
"""
                with st.spinner("👩‍🏫 Cô đang suy nghĩ và trả lời em..."):
                    ai_reply = call_gemini_engine(prompt_advisor)
                st.session_state["chat_history"].append(("assistant", ai_reply))

        chat_display = st.container(height=420, border=True)
        with chat_display:
            for role, msg in reversed(st.session_state["chat_history"]):
                if role == "user":
                    st.markdown(f"🧑‍🎓 **Học sinh:** {msg}")
                else:
                    st.markdown(f"👩‍🏫 **Trợ lý Ngữ văn:**\n\n{msg}")
                st.markdown("---")


# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Bước 3: Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info(
        f"📌 **Đề bài đang thực hành:** {st.session_state['selected_de_key']}\n\n"
        f"📖 *{st.session_state['current_de_info'].get('text', '')}*"
    )

    write_mode = st.radio(
        "Chọn hình thức làm bài của em:",
        ["✍️ Gõ bài viết trực tiếp trên hệ thống", "📷 Tải lên ảnh chụp bài viết tay"],
        horizontal=True,
        key="radio_write_mode",
    )

    if write_mode == "✍️ Gõ bài viết trực tiếp trên hệ thống":
        essay_input = st.text_area(
            "Khung soạn thảo bài văn Nghị luận xã hội (Khoảng 600 chữ):",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Hãy vận dụng dàn ý và dẫn chứng ở Bước 2 để viết bài văn hoàn chỉnh tại đây...",
        )
        st.session_state["user_essay"] = essay_input
        word_count = len(essay_input.strip().split()) if essay_input.strip() else 0
        st.caption(f"📊 Số từ hiện tại: **{word_count} từ** (Dung lượng chuẩn khuyến nghị: khoảng 500 – 700 từ).")

        if st.button("📊 Chuyển bài viết sang Bước 4 để Chấm & Nhận xét theo Rubric", type="primary"):
            if not essay_input.strip():
                st.warning("⚠️ Em chưa nhập nội dung bài viết!")
            else:
                with st.spinner("👩‍🏫 Cô giáo AI đang chấm và đối chiếu bài viết của em với thang đo Rubric..."):
                    eval_res = ai_evaluate_essay_rubric(
                        st.session_state["selected_de_key"],
                        st.session_state["current_de_info"],
                        essay_text=essay_input.strip(),
                    )
                    st.session_state["rubric_evaluation"] = eval_res
                st.success("✅ Đã đánh giá xong! Mời em bấm sang tab **'📊 BƯỚC 4: KIỂM TRA & CHỈNH SỬA (RUBRIC)'** (hoặc xem ngay kết quả bên dưới).")
                with st.container(border=True):
                    st.markdown(st.session_state["rubric_evaluation"])
    else:
        uploaded_img = st.file_uploader(
            "Tải lên ảnh chụp rõ nét bài làm viết tay của em (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="uploader_handwriting",
        )
        if uploaded_img is not None:
            img_obj = Image.open(uploaded_img)
            st.image(img_obj, caption="Ảnh bài làm viết tay của học sinh", use_container_width=True)
            if st.button("📊 Nhờ AI đọc bài viết tay & Chấm theo Rubric (Bước 4)", type="primary"):
                with st.spinner("👩‍🏫 Cô giáo AI đang đọc chữ viết tay và lập bảng đánh giá Rubric..."):
                    eval_res = ai_evaluate_essay_rubric(
                        st.session_state["selected_de_key"],
                        st.session_state["current_de_info"],
                        image_obj=img_obj,
                    )
                    st.session_state["rubric_evaluation"] = eval_res
                st.success("✅ Đã đánh giá xong! Mời em xem kết quả bên dưới hoặc mở tab **BƯỚC 4**.")
                with st.container(border=True):
                    st.markdown(st.session_state["rubric_evaluation"])


# ------------------------------------------------------------------------------
# BƯỚC 4: KIỂM TRA VÀ CHỈNH SỬA THEO THANG RUBRIC (ĐẦU RA BẢNG NHẬN XÉT TIÊU CHÍ)
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown(
        '<div class="section-title">📊 Bước 4: Kiểm Tra Và Chỉnh Sửa Theo Thang Đo Rubric</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="rubric-info-box">
            <b>📌 Hệ thống tiêu chí Rubric chuẩn đánh giá bài văn Nghị luận xã hội THPT:</b><br>
            1. <b>Đảm bảo cấu trúc bài nghị luận (0.5đ):</b> Mở bài, Thân bài, Kết bài rõ ràng; chia đoạn hợp lý.<br>
            2. <b>Xác định & Giải thích đúng VĐNL (1.0đ):</b> Giải thích VĐNL ➔ Giải thích câu nói/ngữ liệu ➔ Chốt VĐNL.<br>
            3. <b>Hệ thống luận điểm bàn luận (2.0đ):</b> Triển khai từ 3 ý bàn luận sâu sắc, lập luận chặt chẽ, thuyết phục.<br>
            4. <b>Dẫn chứng thực tế (0.5đ):</b> Xác thực, tiêu biểu, phân tích gắn chặt với luận điểm.<br>
            5. <b>Tư duy phản biện & Bài học (0.5đ):</b> Phản biện đa chiều (3 trường hợp) và rút ra bài học nhận thức, hành động.<br>
            6. <b>Chính tả, diễn đạt & Sáng tạo (0.5đ):</b> Không sai chính tả/ngữ pháp, văn phong giàu sức biểu cảm.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_r1, col_r2 = st.columns([1, 1.35], gap="large")

    with col_r1:
        st.markdown("##### 📝 Bài viết hiện tại của học sinh (Có thể chỉnh sửa trực tiếp tại đây):")
        edited_essay = st.text_area(
            "Nội dung bài làm để kiểm tra & chỉnh sửa:",
            value=st.session_state.get("user_essay", ""),
            height=420,
            placeholder="Nếu em chưa nhập bài ở Bước 3, em có thể dán trực tiếp bài viết vào đây để kiểm tra theo Rubric...",
            key="essay_step4_editor",
        )
        st.session_state["user_essay"] = edited_essay

        if st.button("🔍 Chấm & Xuất Bảng Nhận Xét Theo Tiêu Chí Rubric", type="primary", use_container_width=True):
            if not edited_essay.strip():
                st.warning("⚠️ Vui lòng nhập bài viết của học sinh vào ô bên trên để hệ thống đánh giá!")
            else:
                with st.spinner("👩‍🏫 Đang phân tích bài làm và lập Bảng nhận xét theo 6 tiêu chí Rubric..."):
                    eval_res = ai_evaluate_essay_rubric(
                        st.session_state["selected_de_key"],
                        st.session_state["current_de_info"],
                        essay_text=edited_essay.strip(),
                    )
                    st.session_state["rubric_evaluation"] = eval_res

        if edited_essay.strip():
            export_content = (
                f"HỒ SƠ BÀI LÀM NGHỊ LUẬN XÃ HỘI THPT\n"
                f"==================================================\n"
                f"ĐỀ BÀI: {st.session_state['selected_de_key']}\n"
                f"NỘI DUNG ĐỀ: {st.session_state['current_de_info'].get('text', '')}\n\n"
                f"--- BÀI LÀM CỦA HỌC SINH ---\n{edited_essay}\n\n"
                f"--- KẾT QUẢ ĐÁNH GIÁ THEO RUBRIC ---\n{st.session_state.get('rubric_evaluation', 'Chưa có đánh giá.')}\n"
            )
            st.download_button(
                label="📥 Tải xuống Hồ sơ bài làm & Bảng đánh giá Rubric (.txt)",
                data=export_content.encode("utf-8"),
                file_name="Ho_so_bai_lam_NLXH_Rubric.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with col_r2:
        st.markdown("##### 📋 Kết quả đầu ra: Bảng Nhận Xét Theo Tiêu Chí Rubric & Hướng Dẫn Sửa Bài:")
        if st.session_state.get("rubric_evaluation"):
            with st.container(border=True):
                st.markdown(st.session_state["rubric_evaluation"])
        else:
            st.info(
                "💡 Chưa có bảng nhận xét. Học sinh hãy nhập bài làm ở cột bên trái (hoặc từ Bước 3) và bấm nút **'🔍 Chấm & Xuất Bảng Nhận Xét Theo Tiêu Chí Rubric'** để nhận kết quả đánh giá chi tiết."
            )
