import streamlit as st
import json
import re
from google import genai
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH TRANG WEB VÀ GIAO DIỆN SỰ PHẠM (CSS NGUYÊN BẢN)
# ==============================================================================
st.set_page_config(
    page_title="Quy Trình 4 Bước Tạo Lập Bài Văn NLXH",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .station-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .step-badge {
        background-color: #e8f0fe;
        color: #1a73e8;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.95em;
        display: inline-block;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1557b0;
        box-shadow: 0 4px 12px rgba(26,115,232,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. KHỞI TẠO TÀI NGUYÊN ĐỀ BÀI VÀ SESSION STATE
# ==============================================================================
DE_BAI_DB = {
    "Đề 1: Ý thức tự học trong kỷ nguyên số": {
        "linh_vuc": "Tự phát triển bản thân",
        "van_de": "Ý thức tự học và khả năng tự định hướng tri thức của học sinh trong thời đại công nghệ số",
        "goi_y": "Tập trung vào tính chủ động, kỹ năng lọc thông tin và sự kiên trì."
    },
    "Đề 2: Trách nhiệm của tuổi trẻ với cộng đồng": {
        "linh_vuc": "Trách nhiệm xã hội",
        "van_de": "Thái độ sống cống hiến và tinh thần sẻ chia của thế hệ trẻ đối với cộng đồng",
        "goi_y": "Nhấn mạnh những hành động thiết thực, từ chối lối sống vô cảm."
    },
    "Đề 3: Bản lĩnh vượt qua áp lực đồng lứa (Peer Pressure)": {
        "linh_vuc": "Tâm lý lứa tuổi",
        "van_de": "Xây dựng bản lĩnh cá nhân để giữ vững giá trị riêng trước áp lực đồng lứa",
        "goi_y": "Phân tích nguyên nhân áp lực, định hình bản sắc cá nhân và sự tự tin."
    }
}

if 'student_name' not in st.session_state:
    st.session_state['student_name'] = ""
if 'user_outline' not in st.session_state:
    st.session_state['user_outline'] = ""
if 'user_essay' not in st.session_state:
    st.session_state['user_essay'] = ""

# ==============================================================================
# 3. SIDEBAR ĐIỀU HƯỚNG VÀ CẤU HÌNH AI
# ==============================================================================
with st.sidebar:
    st.title("📌 CẤU HÌNH HỌC TẬP")
    student_name = st.text_input("Họ và tên học sinh:", value=st.session_state['student_name'])
    st.session_state['student_name'] = student_name
    
    muc_tieu = st.selectbox(
        "Mức độ rèn luyện mục tiêu:",
        ["Cơ bản (Đạt chuẩn)", "Khá (Nâng cao kỹ năng)", "Giỏi (Sâu sắc, sáng tạo)"]
    )
    st.session_state['muc_tieu_hoc_tap'] = muc_tieu

    st.markdown("---")
    st.markdown("### 🤖 CẤU HÌNH AI ASSISTANT")
    api_key_input = st.text_input("Nhập Gemini API Key (để bật AI):", type="password")
    
    st.markdown("---")
    st.markdown("### 🛠 TRẠM HỌC TẬP")
    st.markdown("📍 **Trạm 1:** Phân tích đề bài")
    st.markdown("📍 **Trạm 2:** Lập dàn ý 3 phần")
    st.markdown("📍 **Trạm 3:** Viết bài hoàn chỉnh")
    st.markdown("📍 **Trạm 4:** AI Chấm điểm & Báo cáo")

# ==============================================================================
# 4. GIAO DIỆN CHÍNH: MÔ HÌNH 4 TRẠM TƯƠNG TÁC
# ==============================================================================
st.markdown('<div class="main-header"><h1>🖊️ HỆ THỐNG RÈN LUYỆN VIẾT VĂN NGHỊ LUẬN XÃ HỘI</h1><p>Mô hình 4 trạm tư duy sáng tạo - Tích hợp Trợ lý AI Chấm điểm & Phản hồi cá nhân hóa</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TRẠM 1: PHÂN TÍCH ĐỀ BÀI
# ------------------------------------------------------------------------------
st.markdown('<div class="station-card">', unsafe_allow_html=True)
st.markdown('<span class="step-badge">TRẠM 1</span>', unsafe_allow_html=True)
st.subheader("🎯 Bắt Đầu: Chọn & Phân Tích Đề Bài")

selected_de_key = st.selectbox("Chọn đề bài luyện viết:", list(DE_BAI_DB.keys()))
st.session_state['current_de_key'] = selected_de_key
st.session_state['current_de_info'] = DE_BAI_DB[selected_de_key]

de_info = DE_BAI_DB[selected_de_key]
st.info(f"**Lĩnh vực:** {de_info['linh_vuc']}\n\n**Vấn đề nghị luận cốt lõi:** {de_info['van_de']}\n\n**Gợi ý định hướng:** {de_info['goi_y']}")
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TRẠM 2: LẬP DÀN Ý 3 PHẦN
# ------------------------------------------------------------------------------
st.markdown('<div class="station-card">', unsafe_allow_html=True)
st.markdown('<span class="step-badge">TRẠM 2</span>', unsafe_allow_html=True)
st.subheader("🧩 Xây Dựng Dàn Ý 3 Phần")

user_outline = st.text_area(
    "Nhập dàn ý chi tiết của bạn (Mở bài - Thân bài - Kết bài):",
    value=st.session_state['user_outline'],
    height=220,
    placeholder="1. Mở bài: Dẫn dắt và nêu vấn đề...\n2. Thân bài:\n - Giải thích khái niệm...\n - Phân tích biểu hiện và ý nghĩa...\n - Bàn luận mở rộng & Dẫn chứng...\n3. Kết bài: Bài học nhận thức và hành động..."
)
st.session_state['user_outline'] = user_outline

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("💡 AI Gợi Ý Dàn Ý"):
        if not api_key_input:
            st.error("Vui lòng nhập Gemini API Key ở thanh bên trái!")
        else:
            try:
                client = genai.Client(api_key=api_key_input)
                prompt = f"Hãy lập một dàn ý 3 phần chi tiết, sâu sắc cho bài văn nghị luận xã hội về đề tài: {de_info['van_de']}. Yêu cầu đưa ra dàn ý chuẩn mực sư phạm cho học sinh THPT."
                with st.spinner("AI đang xây dựng dàn ý tham khảo..."):
                    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.markdown("#### 📝 Dàn ý tham khảo từ AI:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Lỗi kết nối AI: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TRẠM 3: THỰC HÀNH VIẾT BÀI
# ------------------------------------------------------------------------------
st.markdown('<div class="station-card">', unsafe_allow_html=True)
st.markdown('<span class="step-badge">TRẠM 3</span>', unsafe_allow_html=True)
st.subheader("✍️ Thực Hành Viết Bài Văn Hoàn Chỉnh")

user_essay = st.text_area(
    "Nhập bài văn nghị luận hoàn chỉnh:",
    value=st.session_state['user_essay'],
    height=320,
    placeholder="Viết hoàn chỉnh bài văn nghị luận từ dàn ý đã xây dựng ở Trạm 2..."
)
st.session_state['user_essay'] = user_essay
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TRẠM 4: AI CHẤM ĐIỂM & BÁO CÁO HỌC TẬP
# ------------------------------------------------------------------------------
st.markdown('<div class="station-card">', unsafe_allow_html=True)
st.markdown('<span class="step-badge">TRẠM 4</span>', unsafe_allow_html=True)
st.subheader("📊 AI Đánh Giá, Chấm Điểm & Xuất Báo Cáo")

if st.button("🤖 AI Chấm Điểm & Khởi Tạo Báo Cáo"):
    if not student_name:
        st.warning("Vui lòng nhập Họ và tên học sinh ở thanh bên trái trước!")
    elif not user_essay.strip():
        st.warning("Vui lòng nhập bài văn hoàn chỉnh ở Trạm 3 để AI chấm điểm!")
    elif not api_key_input:
        st.error("Vui lòng nhập Gemini API Key ở thanh bên trái để bật tính năng AI chấm điểm!")
    else:
        try:
            client = genai.Client(api_key=api_key_input)
            prompt_cham = f"""Bạn là một giáo viên Ngữ văn giàu kinh nghiệm. Hãy chấm bài văn nghị luận xã hội của học sinh theo các tiêu chí chuẩn:
- Đề bài: {selected_de_key}
- Mức độ rèn luyện học sinh hướng tới: {muc_tieu}
- Dàn ý học sinh lập: {user_outline}
- Bài văn của học sinh: {user_essay}

Hãy nhận xét chi tiết ưu điểm, hạn chế, chấm điểm trên thang 10 và đưa ra lời khuyên cụ thể để học sinh sửa bài.
"""
            with st.spinner("AI đang đọc bài, phân tích và chấm điểm chi tiết..."):
                response_cham = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_cham)
                ai_feedback = response_cham.text

            # ĐOẠN REPORT TEXT ĐÃ ĐƯỢC CHỈNH SỬA CHUẨN XÁC CÚ PHÁP
            report_text = f"""BẢN BÁO CÁO HỌC TẬP & ĐÁNH GIÁ TỰ ĐỘNG BẰNG AI
Học sinh: {student_name}
Mức độ rèn luyện: {muc_tieu}
Đề bài thực hiện: {selected_de_key}
Vấn đề nghị luận cốt lõi: {de_info['van_de']}
======================================================================
1. DÀN Ý 3 PHẦN ĐÃ LẬP (TRẠM 2):
{user_outline}

======================================================================
2. BÀI VĂN NGHỊ LUẬN HOÀN CHỈNH (TRẠM 3):
{user_essay}

======================================================================
3. KẾT QUẢ ĐÁNH GIÁ & CHẤM ĐIỂM TỰ ĐỘNG TỪ TRỢ LÝ AI (TRẠM 4):
{ai_feedback}
"""
            st.success("AI đã hoàn thành đánh giá và chấm điểm!")
            st.markdown("### 🏆 Kết Quả Đánh Giá Từ Trợ Lý AI:")
            st.write(ai_feedback)
            
            st.download_button(
                label="📥 Tải Báo Cáo Đánh Giá Học Tập (.txt)",
                data=report_text,
                file_name=f"Bao_Cao_AI_Cham_Diem_{student_name}.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Lỗi trong quá trình AI chấm điểm: {e}")

st.markdown('</div>', unsafe_allow_html=True)
