import json
import re
import google.generativeai as genai
import streamlit as st
import data_de_bai as db
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP & CHUẨN SƯ PHẠM
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
# 2. QUẢN LÝ SESSION STATE
# ==============================================================================
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

if "selected_de_key" not in st.session_state:
    st.session_state["selected_de_key"] = list(db.DE_BAI_CO_BAN.keys())[0]

if "current_de_info" not in st.session_state:
    st.session_state["current_de_info"] = db.DE_BAI_CO_BAN[
        st.session_state["selected_de_key"]
    ]

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
    st.write("3. **✍️ Bước 3:** Xưởng viết bài")
    st.write("4. **📁 Bước 4:** Hồ sơ bài làm")


# ==============================================================================
# 3. HÀM GỌI AI AN TOÀN, CHỐNG TREO MÁY
# ==============================================================================
def call_gemini_engine(prompt_text, image_obj=None):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        return "❌ LỖI: Bạn chưa nhập Gemini API Key ở thanh bên trái!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        if image_obj:
            response = model.generate_content([prompt_text, image_obj])
        else:
            response = model.generate_content(prompt_text)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return "⚠️ AI đã tiếp nhận nhưng không trả về nội dung."
    except Exception as e:
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


def ai_analyze_custom_exam(exam_text, student_guess):
    prompt = f"""
Bạn là chuyên gia khảo thí Ngữ văn THPT. Phân tích đề bài tự dán: \"\"\"{exam_text}\"\"\"
Học sinh đoán VĐNL: \"\"\"{student_guess}\"\"\"

Yêu cầu xuất ra JSON duy nhất gồm đúng cấu trúc:
{{
  "status": "DUNG" | "LECH" | "SAI",
  "feedback": "Nhận xét sư phạm (xưng cô - em)",
  "vdnl_chuan": "VĐNL cốt lõi chuẩn",
  "explain_guide": "Thao tác giải thích: Giải thích VĐNL trước -> Giải thích ngữ liệu/nhận định -> Chốt lại VĐNL.",
  "explain_items": [
    "- **Giải thích vấn đề nghị luận (VĐNL):** Cắt nghĩa các từ khóa chính.",
    "- **Giải thích ngữ liệu/câu nói:** Làm rõ ý nghĩa câu nói hoặc ngữ liệu của đề.",
    "- **Chốt lại VĐNL:** Khái quát lại vấn đề nghị luận."
  ],
  "vdnl_ket_luan": "Chốt vấn đề nghị luận.",
  "questions": [
    {{"cau_hoi": "Ý 1 bàn luận?", "y_tra_loi": ["- **Thứ nhất:** ...", "- **Thứ hai:** ...", "- **Thứ ba:** ..."]}}
  ],
  "evidence": [{{"ten": "Tên dẫn chứng", "chi_tiet": "Chi tiết", "y_nghia": "Ý nghĩa", "nguon": "Nguồn"}}],
  "counter": [
    "- **Trường hợp 1 (Góc độ cực đoan):** ...",
    "- **Trường hợp 2 (Góc độ hoàn cảnh khách quan):** ...",
    "- **Trường hợp 3 (Góc độ lạm dụng hình thức):** ..."
  ],
  "dani_chi_tiet": {
    "mb": "Dẫn dắt và giới thiệu VĐNL.",
    "gt": "Giải thích VĐNL trước, sau đó giải thích ngữ liệu và chốt VĐNL.",
    "bl": "Triển khai hệ thống ý bàn luận sâu sắc.",
    "dc": "Lựa chọn dẫn chứng thực tế tiêu biểu.",
    "pb": "Phản biện đa chiều với 3 trường hợp cụ thể.",
    "kb": "Tổng kết vấn đề và rút ra bài học."
  }
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
            "feedback": "Cô nhận thấy em đã cố gắng nhưng cần điều chỉnh để diễn đạt chuẩn xác hơn.",
            "vdnl_chuan": student_guess if student_guess else "Vấn đề nghị luận từ đề bài",
            "explain_guide": "Thao tác giải thích: Giải thích VĐNL trước -> Giải thích ngữ liệu -> Chốt lại VĐNL.",
            "explain_items": [
                "- **Giải thích vấn đề nghị luận (VĐNL):** Cắt nghĩa các từ khóa chính.",
                "- **Giải thích ngữ liệu:** Làm rõ ý nghĩa câu nói hoặc ngữ liệu của đề.",
                "- **Chốt lại VĐNL:** Khái quát lại vấn đề nghị luận."
            ],
            "vdnl_ket_luan": student_guess if student_guess else "Vấn đề nghị luận trọng tâm.",
            "questions": [{
                "cau_hoi": "Vì sao vấn đề này quan trọng đối với tuổi trẻ?",
                "y_tra_loi": [
                    "- **Thứ nhất:** Giúp bồi dưỡng nhận thức và tư duy tích cực.",
                    "- **Thứ hai:** Định hình nhân cách và hành động đúng đắn.",
                    "- **Thứ ba:** Tạo ra giá trị thiết thực cho cộng đồng."
                ]
            }],
            "evidence": [{"ten": "Hoàng Hoa Trung - Dự án Nuôi Em", "chi_tiet": "Nuôi cơm trưa cho trẻ em vùng cao.", "y_nghia": "Tinh thần cống hiến.", "nguon": "Báo Tuổi Trẻ"}],
            "counter": [
                "- **Trường hợp 1 (Góc độ cực đoan):** Vấn đề không nên được tuyệt đối hóa thành chân lý cứng nhắc trong mọi hoàn cảnh.",
                "- **Trường hợp 2 (Góc độ hoàn cảnh khách quan):** Cần xem xét điều kiện thực tế, tránh áp đặt chủ quan.",
                "- **Trường hợp 3 (Góc độ lạm dụng hình thức):** Tránh biến giá trị tốt đẹp thành vỏ bọc hình thức để phô trương."
            ],
            "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản biện", "kb": "Kết bài"}
        }


# ==============================================================================
# 4. GIAO DIỆN CHÍNH & TABS
# ==============================================================================
st.markdown(
    """
<div class="hero-banner">
    <div class="hero-title">🖊️ HỆ THỐNG 30 ĐỀ NGHỊ LUẬN XÃ HỘI THPT</div>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "🌱 BƯỚC 1: TÌM HIỂU ĐỀ",
    "🧵 BƯỚC 2: TÌM Ý, LẬP DÀN Ý & THAM KHẢO DẪN CHỨNG",
    "✍️ BƯỚC 3: XƯỞNG VIẾT BÀI",
    "📁 HỒ SƠ BÀI LÀM",
])

# ------------------------------------------------------------------------------
# BƯỚC 1: TÌM HIỂU ĐỀ
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown(
        '<div class="section-title">🔍 Lựa chọn đề bài & Xác định vấn đề nghị luận</div>',
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
                "Chọn đề Cơ bản:", list(db.DE_BAI_CO_BAN.keys()), key="sb_coban"
            )
            de_info_cb = db.DE_BAI_CO_BAN[selected_cb_key]
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
                st.success(f"Đã chọn: {selected_cb_key}! Mời các em bấm qua tab 'BƯỚC 2'.")

    with tab_de_nangcao:
        col_nc1, col_nc2 = st.columns([1, 2], gap="medium")
        with col_nc1:
            selected_nc_key = st.selectbox(
                "Chọn đề Nâng cao:", list(db.DE_BAI_NANG_CAO.keys()), key="sb_nangcao"
            )
            de_info_nc = db.DE_BAI_NANG_CAO[selected_nc_key]
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
                st.success(f"Đã chọn: {selected_nc_key}! Mời các em bấm qua tab 'BƯỚC 2'.")

    with tab_de_tu_nhap:
        custom_de_text = st.text_area(
            "Nội dung đề bài tự chọn:",
            placeholder="Ví dụ: Viết bài văn nghị luận bàn về...",
            height=100,
        )
        student_custom_vdnl = st.text_input(
            "Vấn đề nghị luận em tự đoán cho đề này:",
            placeholder="Gõ VĐNL theo suy nghĩ của em...",
        )
        if st.button("🔍 Tạo khung định hướng cho đề tự nhập", type="primary"):
            if custom_de_text.strip():
                with st.spinner("AI đang phân tích ngữ liệu và tạo khung định hướng..."):
                    res_custom = ai_analyze_custom_exam(custom_de_text, student_custom_vdnl)
                    ten_de_custom = "Đề tự nhập: " + (custom_de_text[:30] + "..." if len(custom_de_text) > 30 else custom_de_text)
                    info_custom = {
                        "text": custom_de_text,
                        "vdnl_chuan": res_custom.get("vdnl_chuan", student_custom_vdnl),
                        "explain_guide": res_custom.get("explain_guide", ""),
                        "explain_items": res_custom.get("explain_items", []),
                        "vdnl_ket_luan": res_custom.get("vdnl_ket_luan", student_custom_vdnl),
                        "questions": res_custom.get("questions", []),
                        "evidence": res_custom.get("evidence", []),
                        "counter": res_custom.get("counter", []),
                        "dani_chi_tiet": res_custom.get("dani_chi_tiet", {
                            "mb": "Dẫn dắt và giới thiệu VĐNL.",
                            "gt": "Giải thích VĐNL trước, sau đó giải thích ngữ liệu và chốt VĐNL.",
                            "bl": "Triển khai hệ thống ý bàn luận sâu sắc.",
                            "dc": "Lựa chọn dẫn chứng thực tế tiêu biểu.",
                            "pb": "Phản biện đa chiều với 3 trường hợp cụ thể.",
                            "kb": "Tổng kết vấn đề và rút ra bài học."
                        })
                    }
                    st.session_state["selected_de_key"] = ten_de_custom
                    st.session_state["current_de_info"] = info_custom
                    st.session_state["eval_vdnl_result"] = {
                        "status": res_custom.get("status", "LECH"),
                        "feedback": res_custom.get("feedback", ""),
                        "suggested_fix": res_custom.get("vdnl_chuan", "")
                    }
                    st.success("✅ Đã tạo xong khung định hướng cho đề tự nhập!")

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
        if res.get("status") == "DUNG":
            st.success(f"🎯 **CHÍNH XÁC!** {res.get('feedback')}")
        else:
            st.warning(
                f"⚠️ **CẦN ĐIỀU CHỈNH:** {res.get('feedback')}\n\n👉 *Đáp án chuẩn:*"
                f" {res.get('suggested_fix')}"
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

        # Thao tác 1: Giải thích (Chuẩn trật tự: Giải thích VĐNL -> Câu nói -> Chốt lại VĐNL)
        with st.expander("📌 Thao tác 1: Giải thích bản chất khái niệm / nhận định", expanded=True):
            guide_txt = cur_de_info.get("explain_guide", "")
            items = cur_de_info.get("explain_items", [])
            vdnl_kl = cur_de_info.get("vdnl_ket_luan", "")

            st.markdown(f"*{guide_txt}*")
            st.markdown("---")
            for itm in items:
                st.markdown(itm)
            st.markdown(f"**👉 Chốt lại VĐNL:** *{vdnl_kl}*")

        # Thao tác 2: Bàn luận trọng tâm
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"{ans}")

        # Thao tác 3: Dẫn chứng
        with st.expander("📚 Thao tác 3: Kho dẫn chứng trọng tâm & Dẫn chứng mở rộng", expanded=True):
            st.markdown("##### 📌 Dẫn chứng thực tế tường minh cho đề bài:")
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
                else:
                    st.markdown(f"<div class='evidence-card'>{ev}</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📚 Tra cứu Kho dẫn chứng mở rộng (9 nhóm chủ điểm):")
            selected_topic = st.selectbox(
                "Chọn chủ điểm dẫn chứng cần tra cứu:",
                options=list(db.KHO_DAN_CHUNG_9_CHU_DIEM.keys()),
                key="sb_kho_dc",
            )
            for dc in db.KHO_DAN_CHUNG_9_CHU_DIEM[selected_topic]:
                with st.container(border=True):
                    st.markdown(f"#### 👤 <span style='color:#1d4ed8;'>{dc['ten']}</span>", unsafe_allow_html=True)
                    st.write(dc["noi_dung"])
                    st.caption(f"📰 *Nguồn: {dc['nguon']}*")

        # Thao tác 4: Phản biện (Đã có đủ 3 trường hợp/hướng)
        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng (3 trường hợp lật lại vấn đề)", expanded=True):
            st.markdown("*Lưu ý học sinh: Khi làm bài, cần tránh nhìn nhận vấn đề một chiều, tuyệt đối hóa mà phải biết phản biện đa chiều qua các trường hợp sau:*")
            st.markdown("---")
            for c_item in cur_de_info.get("counter", []):
                st.markdown(f"<div class='counter-box'>{c_item}</div>", unsafe_allow_html=True)

        # ĐỊNH HƯỚNG DÀN Ý 3 PHẦN
        st.markdown("---")
        st.markdown("#### 📝 Định Hướng Bố Cục Dàn Ý Chi Tiết Chuẩn 3 Phần")
        dani_data = cur_de_info.get(
            "dani_chi_tiet",
            {
                "mb": "Dẫn dắt từ ngữ liệu và giới thiệu vấn đề nghị luận.",
                "gt": "Giải thích VĐNL trước, sau đó giải thích ngữ liệu và chốt VĐNL.",
                "bl": "Triển khai hệ thống ý bàn luận sâu sắc.",
                "dc": "Lựa chọn dẫn chứng thực tế tiêu biểu.",
                "pb": "Phản biện đa chiều với 3 trường hợp cụ thể.",
                "kb": "Tổng kết vấn đề và rút ra bài học.",
            },
        )

        st.markdown(
            f"""
### 🌟 I. PHẦN MỞ BÀI
- **Dẫn dắt & Giới thiệu VĐNL:** {dani_data.get('mb', '')}

### 🌟 II. PHẦN THÂN BÀI
- **1. Mục Giải thích:** {dani_data.get('gt', '')}
- **2. Mục Bàn luận trọng tâm:** {dani_data.get('bl', '')}
- **3. Mục Dẫn chứng thực tế:** {dani_data.get('dc', '')}
- **4. Mục Phản biện đa chiều (3 trường hợp):** {dani_data.get('pb', '')}

### 🌟 III. PHẦN KẾT BÀI
- **Tổng kết & Bài học hành động:** {dani_data.get('kb', '')}
"""
        )

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        st.info("💡 Học sinh gõ câu hỏi bên dưới, bấm nút gửi để nhận định hướng sư phạm từ Cô giáo AI.")

        user_question = st.text_input("Nhập câu hỏi của em:", placeholder="Ví dụ: Gợi ý thêm cho em ý bàn luận...", key="input_ai_b2")
        
        if st.button("Gửi câu hỏi cho Cô 🚀", type="primary", key="btn_send_ai"):
            if user_question.strip():
                with st.spinner("Trợ lý Ngữ văn đang suy nghĩ..."):
                    prompt_chat = f"Bạn là Giáo viên Ngữ văn THPT tâm lý, tuân thủ nguyên tắc SƯ PHẠM (TUYỆT ĐỐI KHÔNG VIẾT HỘ, chỉ đặt câu hỏi gợi mở, xưng cô - em). Đề bài: {cur_de_key}. Học sinh hỏi: {user_question}. Hãy trả lời ngắn gọn định hướng tư duy:"
                    reply = call_gemini_engine(prompt_chat)
                st.markdown("### 🤖 Trợ lý Ngữ văn trả lời:")
                st.success(reply)
            else:
                st.warning("Em chưa nhập câu hỏi!")

# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
# HỒ SƠ BÀI LÀM
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📁 Hồ Sơ Bài Làm & Xuất File</div>', unsafe_allow_html=True)
    if st.session_state.get("user_essay"):
        st.text_area("Nội dung bài làm:", value=st.session_state["user_essay"], height=250, disabled=True)
