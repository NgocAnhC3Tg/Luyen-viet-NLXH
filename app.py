import json
import re
import google.generativeai as genai
import streamlit as st
import data_de_bai as db
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN CAO CẤP
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

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        ("assistant", "Chào em! Cô là Trợ lý Ngữ văn. Em có thắc mắc gì về phương pháp lập dàn ý, chọn dẫn chứng hay cách triển khai ý cứ hỏi cô nhé!")
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
        return "❌ Bạn chưa nhập Gemini API Key ở thanh bên trái nên Trợ lý AI chưa thể hoạt động!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        if image_obj:
            response = model.generate_content([prompt_text, image_obj])
        else:
            response = model.generate_content(prompt_text)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return "⚠️ AI đã tiếp nhận nhưng không trả về nội dung. Em hãy thử gửi lại nhé!"
    except Exception as e:
        return f"❌ Lỗi kết nối AI: {str(e)}"


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
        if st.button("🔍 Tạo giàn giáo cơ bản cho đề tự nhập", type="primary"):
            if custom_de_text.strip():
                st.session_state["selected_de_key"] = "Đề tự nhập"
                st.session_state["current_de_info"] = {
                    "text": custom_de_text,
                    "vdnl_chuan": "Vấn đề nghị luận trọng tâm từ đề bài",
                    "explain_guide": "Giải thích từ khóa trọng tâm.",
                    "explain_items": ["1. Cắt nghĩa bản chất khái niệm."],
                    "vdnl_ket_luan": "Chốt vấn đề nghị luận.",
                    "questions": [{
                        "cau_hoi": "Vì sao vấn đề này quan trọng đối với tuổi trẻ?",
                        "y_tra_loi": [
                            "• Giúp bồi dưỡng nhận thức và tư duy tích cực.",
                            "• Định hình nhân cách và hành động đúng đắn.",
                            "• Tạo ra giá trị thiết thực cho cộng đồng."
                        ]
                    }],
                    "evidence": [{"ten": "Dẫn chứng thực tế", "chi_tiet": "Sự kiện tiêu biểu", "y_nghia": "Ý nghĩa", "nguon": "Báo chí"}],
                    "counter": ["<b>Phản biện:</b> Tránh cực đoan hóa vấn đề."],
                    "dani_chi_tiet": {"mb": "Mở bài", "gt": "Giải thích", "bl": "Bàn luận", "dc": "Dẫn chứng", "pb": "Phản biện", "kb": "Kết bài"}
                }
                st.success("Đã tạo xong giàn giáo cho đề tự nhập!")

    st.markdown("---")
    cur_active_key = st.session_state["selected_de_key"]
    cur_active_info = st.session_state["current_de_info"]
    st.info(f"📌 **Đề bài hiện tại đang chọn:** {cur_active_key}")

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

        # Thao tác 1: Giải thích
        with st.expander("📌 Thao tác 1: Giải thích bản chất khái niệm / nhận định", expanded=True):
            guide_txt = cur_de_info.get("explain_guide", "")
            items = cur_de_info.get("explain_items", [])
            vdnl_kl = cur_de_info.get("vdnl_ket_luan", "")

            items_html = "".join([f"<p style='margin-bottom: 8px;'>• {it}</p>" for it in items])
            st.markdown(
                f"""
                <div class='explain-box-clean'>
                    <p style='margin:0 0 8px 0; font-style:italic; color:#475569;'><i>{guide_txt}</i></p>
                    <div style='margin:0 0 10px 0;'>{items_html}</div>
                    <p style='margin:0; font-weight:700; color:#166534;'>
                        👉 Chốt lại VĐNL: <span style='font-weight:normal; font-style:italic;'>{vdnl_kl}</span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Thao tác 2: Bàn luận trọng tâm (Đảm bảo >= 3 ý)
        with st.expander("💡 Thao tác 2: Bàn luận trọng tâm (Hệ thống ý sâu sắc, đa chiều)", expanded=True):
            for q in cur_de_info.get("questions", []):
                st.markdown(f"**❓ {q.get('cau_hoi', '')}**")
                for ans in q.get("y_tra_loi", []):
                    st.markdown(f"  {ans}")

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

        # Thao tác 4: Phản biện
        with st.expander("🔄 Thao tác 4: Phản biện & Mở rộng (Lật lại vấn đề)", expanded=True):
            for c_item in cur_de_info.get("counter", []):
                st.markdown(f"<div class='counter-box'>{c_item}</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("#### 🧭 Trợ Lý Ngữ Văn AI Tư Vấn")
        
        # Hiển thị lịch sử chat
        chat_box = st.container(height=320)
        with chat_box:
            for role, text in st.session_state["chat_history"]:
                if role == "user":
                    st.markdown(f"**👤 Học sinh:** {text}")
                else:
                    st.markdown(f"🤖 **Trợ lý Ngữ văn:** {text}")
                st.markdown("---")

        # Khung form gửi câu hỏi cực kỳ ổn định, chống treo
        with st.form(key="chat_form", clear_on_submit=True):
            user_q = st.text_input("Hỏi cô về phương pháp, dẫn chứng...", placeholder="Ví dụ: Gợi ý thêm cho em ý bàn luận...")
            submit_clicked = st.form_submit_button("Gửi câu hỏi cho Cô 🚀", type="primary")
            
            if submit_clicked and user_q.strip():
                st.session_state["chat_history"].append(("user", user_q))
                prompt_chat = f"Bạn là Giáo viên Ngữ văn THPT tâm lý, tuân thủ nguyên tắc SƯ PHẠM (TUYỆT ĐỐI KHÔNG VIẾT HỘ, chỉ đặt câu hỏi gợi mở, xưng cô - em). Đề bài: {cur_de_key}. Học sinh hỏi: {user_q}. Hãy trả lời ngắn gọn định hướng tư duy:"
                with st.spinner("Trợ lý Ngữ văn đang định hướng..."):
                    reply = call_gemini_engine(prompt_chat)
                st.session_state["chat_history"].append(("assistant", reply))
                st.rerun()

# ------------------------------------------------------------------------------
# BƯỚC 3: XƯỞNG VIẾT BÀI
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">✍️ Xưởng Viết Bài Độc Lập</div>', unsafe_allow_html=True)
    st.info("💡 *Dựa vào hệ thống gợi ý ở Bước 2, các em có thể tự gõ bài làm trực tiếp hoặc chụp ảnh bài viết tay gửi lên để AI nhận xét!*")

    write_mode = st.radio(
        "Chọn hình thức nộp bài:",
        ["✍️ Tự gõ bài viết trực tiếp", "📷 Gửi ảnh chụp bài viết tay"],
        horizontal=True,
    )

    if write_mode == "✍️ Tự gõ bài viết trực tiếp":
        essay_in = st.text_area(
            "Nhập bài viết của em:",
            value=st.session_state.get("user_essay", ""),
            height=380,
            placeholder="Viết bài văn nghị luận hoàn chỉnh...",
        )
        st.session_state["user_essay"] = essay_in
    else:
        uploaded_img = st.file_uploader(
            "Tải lên ảnh chụp bài viết tay của em (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
        )
        if uploaded_img is not None:
            img = Image.open(uploaded_img)
            st.image(img, caption="Ảnh bài làm viết tay của học sinh", use_column_width=True)
            if st.button("🔍 Nhờ AI nhận xét bài viết tay", type="primary"):
                with st.spinner("AI đang đọc và phân tích chữ viết..."):
                    eval_prompt = f"Bạn là Giám khảo Ngữ văn THPT. Hãy đọc ảnh bài làm viết tay cho đề bài '{cur_de_key}' và nhận xét chi tiết ưu điểm, điểm cần bổ sung (xưng cô - em)."
                    feedback = call_gemini_engine(eval_prompt, image_obj=img)
                    st.success(feedback)

# ------------------------------------------------------------------------------
# HỒ SƠ BÀI LÀM
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">📁 Hồ Sơ Bài Làm & Xuất File</div>', unsafe_allow_html=True)
    if st.session_state.get("user_essay"):
        st.text_area("Nội dung bài làm đã lưu:", value=st.session_state["user_essay"], height=250, disabled=True)
