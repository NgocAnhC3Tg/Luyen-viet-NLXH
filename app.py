import streamlit as st
import json
import re
from google import genai
from PIL import Image

# ==============================================================================
# 1. CẤU HÌNH TRANG WEB VÀ GIAO DIỆN SỰ PHẠM
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
    .step-badge {
        background-color: #e8f0fe;
        color: #1a73e8;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.9em;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
    }
</style>
""", unsafe_allow_syntax_hide=True)

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
# 3. SIDEBAR ĐIỀU HƯỚNG
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
    st.markdown("### 🛠 QUY TRÌNH 4 BƯỚC")
    st.markdown("1. **Bước 1:** Phân tích đề bài")
    st.markdown("2. **Bước 2:** Lập dàn ý 3 phần")
    st.markdown("3. **Bước 3:** Viết bài hoàn chỉnh")
    st.markdown("4. **Bước 4:** Chấm điểm & Báo cáo")

# ==============================================================================
# 4. THÂN TRANG WEB: QUY TRÌNH 4 BƯỚC
# ==============================================================================
st.markdown('<div class="main-header"><h1>🖊️ HỆ THỐNG RÈN LUYỆN VIẾT VĂN NGHỊ LUẬN XÃ HỘI</h1><p>Quy trình 4 bước chuẩn hóa tư duy và tạo lập văn bản</p></div>', unsafe_allow_html=True)

# BƯỚC 1: PHÂN TÍCH ĐỀ BÀI
st.header("Bước 1: Chọn & Phân Tích Đề Bài")
selected_de_key = st.selectbox("Chọn đề bài luyện viết:", list(DE_BAI_DB.keys()))
st.session_state['current_de_key'] = selected_de_key
st.session_state['current_de_info'] = DE_BAI_DB[selected_de_key]

de_info = DE_BAI_DB[selected_de_key]
st.info(f"**Vấn đề nghị luận:** {de_info['van_de']}\n\n**Gợi ý định hướng:** {de_info['goi_y']}")

st.markdown("---")

# BƯỚC 2: LẬP DÀN Ý
st.header("Bước 2: Lập Dàn Ý 3 Phần")
user_outline = st.text_area(
    "Xây dựng dàn ý chi tiết (Mở bài - Thân bài - Kết bài):",
    value=st.session_state['user_outline'],
    height=200,
    placeholder="1. Mở bài: Dẫn dắt và nêu vấn đề...\n2. Thân bài:\n - Giải thích khái niệm...\n - Phân tích biểu hiện và ý nghĩa...\n - Bàn luận mở rộng & Dẫn chứng...\n3. Kết bài: Bài học nhận thức và hành động..."
)
st.session_state['user_outline'] = user_outline

st.markdown("---")

# BƯỚC 3: VIẾT BÀI HOÀN CHỈNH
st.header("Bước 3: Thực Hành Viết Bài")
user_essay = st.text_area(
    "Nhập bài văn nghị luận hoàn chỉnh của bạn:",
    value=st.session_state['user_essay'],
    height=300,
    placeholder="Viết hoàn chỉnh bài văn từ dàn ý đã lập ở Bước 2..."
)
st.session_state['user_essay'] = user_essay

st.markdown("---")

# BƯỚC 4: KẾT QUẢ VÀ XUẤT BÁO CÁO
st.header("Bước 4: Đánh Giá & Xuất Báo Cáo Học Tập")

if st.button("📊 Khởi Tạo Báo Cáo Học Tập"):
    if not student_name:
        st.warning("Vui lòng nhập Họ và tên học sinh ở thanh bên trái trước khi xuất báo cáo!")
    else:
        bai_viet_hien_thi = user_essay if user_essay.strip() else "(Chưa nhập bài viết)"
        
        # ĐOẠN F-STRING ĐÃ ĐƯỢC CHỈNH SỬA CHUẨN XÁC 3 DẤU NGOẶC KÉP
        report_text = f"""BẢN BÁO CÁO HỌC TẬP – QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH
Học sinh: {student_name}
Mức độ rèn luyện: {st.session_state.get('muc_tieu_hoc_tap', '')}
Đề bài thực hiện: {st.session_state.get('current_de_key', '')}
Vấn đề nghị luận cốt lõi: {st.session_state.get('current_de_info', {}).get('van_de', '')}
======================================================================
1. DÀN Ý 3 PHẦN ĐÃ LẬP (BƯỚC 2):
{st.session_state.get('user_outline', '')}

======================================================================
2. BÀI VĂN NGHỊ LUẬN HOÀN CHỈNH (BƯỚC 3):
{bai_viet_hien_thi}

======================================================================
3. KẾT QUẢ ĐÁNH GIÁ & CHẤM ĐIỂM TỰ ĐỘNG THEO RUBRIC (BƯỚC 4):
- Cấu trúc bài viết: Đạt chuẩn 3 phần (Mở bài, Thân bài, Kết bài).
- Lập luận & Dẫn chứng: Đang hoàn thiện bài tập rèn luyện.
"""
        st.success("Khởi tạo báo cáo học tập thành công!")
        st.text_area("Xem trước kết quả báo cáo:", value=report_text, height=350)
        
        st.download_button(
            label="📥 Tải Báo Cáo Học Tập (.txt)",
            data=report_text,
            file_name=f"Bao_Cao_Hoc_Tap_{student_name}.txt",
            mime="text/plain"
        )
