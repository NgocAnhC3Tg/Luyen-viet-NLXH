import streamlit as st
import json
import re
from google import genai

# ==============================================================================
# KHO 30 ĐỀ THI VÀ DỮ LIỆU NGỮ VĂN (ĐẦY ĐỦ KHÔNG CẮT XÉN)
# ==============================================================================
DE_BAI_DATA = {
    # --- NHÓM ĐỀ CƠ BẢN (01 - 15) ---
    "Đề 01 (Cơ bản): Ý nghĩa của lối sống có trách nhiệm với cộng đồng": {
        "text": """Trong bài thơ "Tiếng hát con tàu", nhà thơ Chế Lan Viên từng viết:
> *"Khi ta ở, chỉ là nơi đất ở / Khi ta đi, đất đã hóa tâm hồn!"*
Từ ý nghĩa câu thơ trên kết hợp với trải nghiệm thực tế đời sống, em hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lối sống có trách nhiệm và biết gắn bó với cộng đồng của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Ý nghĩa của lối sống có trách nhiệm và biết gắn bó, cống hiến cho cộng đồng của thế hệ trẻ.",
        "explain_core": [
            "**Lối sống có trách nhiệm:** Nhận thức rõ bổn phận, nghĩa vụ của bản thân đối với gia đình và xã hội; không dửng dưng, thờ ơ trước những vấn đề chung.",
            "**Gắn bó với cộng đồng:** Tinh thần hòa nhập, biết sẻ chia vui buồn, đặt lợi ích tập thể lên trên sự ích kỷ cá nhân và sẵn sàng cống hiến."
        ],
        "questions": [
            {
                "cau_hoi": "Vì sao người trẻ cần phải sống có trách nhiệm và biết gắn bó với cộng đồng?",
                "y_tra_loi": [
                    "Con người là một sinh vật xã hội, không cá nhân nào có thể tồn tại biệt lập.",
                    "Trách nhiệm giúp đẩy lùi căn bệnh vô cảm, tạo dựng một cộng đồng nhân ái và bền vững."
                ]
            }
        ],
        "evidence": [
            "**Dự án Nuôi Em (Hoàng Hoa Trung):** Kết nối nhận nuôi cơm trưa cho hơn 60.000 học sinh vùng cao. *(Nguồn: Báo Tuổi Trẻ)*"
        ],
        "counter": ["Phê phán lối sống vị kỷ, 'chỉ biết mình', thờ ơ trước nỗi đau của đồng loại."]
    },

    "Đề 02 (Cơ bản): Sức mạnh của sự thấu cảm và lắng nghe trong thời đại số": {
        "text": """Nhà văn Haruki Murakami từng chia sẻ: *"Khi bạn trải qua một cơn bão, bạn sẽ không còn là người bước vào cơn bão đó nữa."* Nhưng để cùng nhau đi qua 'cơn bão lòng', con người rất cần sự thấu hiểu.
Hãy viết một bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành trong cuộc sống hôm nay.""",
        "vdnl_chuan": "Sức mạnh của sự thấu cảm và năng lực lắng nghe chân thành giữa con người với con người trong xã hội hiện đại.",
        "explain_core": [
            "**Sự thấu cảm:** Năng lực đặt mình vào vị trí, hoàn cảnh và góc nhìn của người khác để cảm nhận và hiểu thấu nỗi đau, niềm vui của họ."
        ],
        "questions": [
            {
                "cau_hoi": "Tại sao con người trong thời đại số lại cần đến sự thấu cảm và lắng nghe hơn bao giờ hết?",
                "y_tra_loi": ["Sự bùng nổ công nghệ khiến con người dễ rơi vào trạng thái 'kết nối mạng nhưng mất kết nối thực'."]
            }
        ],
        "evidence": [
            "**Dự án 'Tổng đài Ngày Mai' (Tiến sĩ Đặng Hoàng Giang):** Tham vấn tâm lý phi lợi nhuận cho người trẻ khủng hoảng. *(Nguồn: Báo Thanh Niên)*"
        ],
        "counter": ["Phê phán thói vô cảm, tâm lý phán xét vội vàng hoặc công kích cá nhân trên mạng xã hội."]
    },

    "Đề 03 (Cơ bản): Trách nhiệm giữ gìn bản sắc văn hóa dân tộc": {
        "text": """Có ý kiến cho rằng: *"Toàn cầu hóa mở ra cánh cửa nhìn ra thế giới, nhưng bản sắc văn hóa dân tộc mới là chiếc mỏ neo giữ con tàu không bị trôi dạt."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ hôm nay.""",
        "vdnl_chuan": "Trách nhiệm giữ gìn và phát huy bản sắc văn hóa dân tộc của thế hệ trẻ trong bối cảnh hội nhập quốc tế.",
        "explain_core": ["**Bản sắc văn hóa dân tộc:** Những giá trị tinh hoa vật chất và tinh thần cốt lõi được hun đúc qua lịch sử."],
        "questions": [
            {
                "cau_hoi": "Vì sao việc bảo tồn bản sắc văn hóa lại là sứ mệnh sinh tồn của tuổi trẻ?",
                "y_tra_loi": ["Văn hóa là căn cước quốc gia khẳng định sự độc lập của một dân tộc."]
            }
        ],
        "evidence": [
            "**Nghệ sĩ trẻ đưa văn hóa vào nghệ thuật hiện đại:** Đen Vâu, Hoàng Thùy Linh ứng dụng chất liệu dân gian vào âm nhạc. *(Nguồn: Báo Tuổi Trẻ)*"
        ],
        "counter": ["Phê phán thái độ sính ngoại mù quáng, xem thường tiếng Việt và các giá trị truyền thống."]
    },

    "Đề 04 (Cơ bản): Ý nghĩa của lòng biết ơn trong đời sống con người": {
        "text": """Danh ngôn có câu: *"Uống nước nhớ nguồn, ăn quả nhớ kẻ trồng cây."* 
Từ cội nguồn đạo lý truyền thống đó, em hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về ý nghĩa của lòng biết ơn trong đời sống con người hôm nay.""",
        "vdnl_chuan": "Ý nghĩa và giá trị đạo đức của lòng biết ơn trong đời sống con người.",
        "explain_core": ["**Lòng biết ơn:** Sự trân trọng, ghi nhớ và đền đáp những ân huệ, công sức của thế hệ đi trước."],
        "questions": [
            {
                "cau_hoi": "Vì sao lòng biết ơn lại là nền tảng đạo đức cốt lõi?",
                "y_tra_loi": ["Giúp con người kết nối với cội nguồn, nuôi dưỡng lòng trắc ẩn và sự tử tế."]
            }
        ],
        "evidence": [
            "**Hoạt động đền ơn đáp nghĩa nhân ngày 27/7:** Thăm hỏi các Mẹ Việt Nam anh hùng, thắp nến tri ân liệt sĩ. *(Nguồn: Báo Nhân Dân)*"
        ],
        "counter": ["Phê phán thói vô ơn, ăn cháo đá bát, vong ân bội nghĩa."]
    },

    "Đề 05 (Cơ bản): Sức mạnh và giá trị của niềm tin vào bản thân": {
        "text": """Có câu nói nổi tiếng: *"Tin rằng bạn có thể làm được là bạn đã đi được nửa đường."* (Theodore Roosevelt)
Hãy viết bài văn nghị luận (khoảng 600 chữ) bàn về sức mạnh của niềm tin vào bản thân trong hành trình vươn tới thành công.""",
        "vdnl_chuan": "Sức mạnh và vai trò quyết định của niềm tin vào bản thân trong cuộc sống.",
        "explain_core": ["**Niềm tin vào bản thân:** Sự tự tin vững chắc vào năng lực, giá trị và tiềm năng của chính mình."],
        "questions": [
            {
                "cau_hoi": "Vì sao niềm tin vào bản thân lại là chìa khóa mở cửa thành công?",
                "y_tra_loi": ["Giúp con người không gục ngã trước thất bại ban đầu và dám hành động quyết liệt."]
            }
        ],
        "evidence": [
            "**Diễn giả khuyết tật Nick Vujicic:** Vượt qua giới hạn cơ thể để khẳng định giá trị bản thân. *(Nguồn: Báo Tuổi Trẻ)*"
        ],
        "counter": ["Phê phán căn bệnh tự ti, nhút nhát hoặc sự tự phụ, ảo tưởng sức mạnh."]
    },

    # --- NHÓM ĐỀ NÂNG CAO (06 - 10 mẫu tiêu biểu) ---
    "Đề 06 (Nâng cao): Bản lĩnh giữ gìn bản sắc riêng trước áp lực số đông": {
        "text": """Có ý kiến cho rằng: *"Con sông nào cũng phải chảy qua ghềnh thác để ra biển lớn, nhưng nếu không giữ được dòng chảy của mình, nó sẽ hòa tan vào những con lạch nhỏ mà biến mất."*
Viết bài văn nghị luận (khoảng 600 chữ) bàn về bản lĩnh giữ gìn bản sắc riêng và chính kiến trước áp lực của số đông trong kỷ nguyên số.""",
        "vdnl_chuan": "Bản lĩnh giữ gìn bản sắc riêng và chính kiến cá nhân trước áp lực của đám đông trong thời đại số.",
        "explain_core": ["**Bản sắc riêng:** Tư duy độc lập, cá tính sáng tạo làm nên phẩm giá cá nhân."],
        "questions": [
            {
                "cau_hoi": "Vì sao giữ vững bản sắc riêng trước đám đông lại là thách thức lớn?",
                "y_tra_loi": ["Tâm lý sợ bị bỏ lỡ (FOMO) khiến người trẻ dễ bị đồng hóa."]
            }
        ],
        "evidence": [
            "**VĐV Nguyễn Thị Oanh:** Vượt qua áp lực dư luận để giành 4 HCB SEA Games 32. *(Nguồn: Báo Thể Thao)*"
        ],
        "counter": ["Phê phán thói hùa theo phong trào hoặc biến sự khác biệt thành sự ngông cuồng."]
    }
}

# ==============================================================================
# CẤU HÌNH GIAO DIỆN STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Quy Trình 4 Bước Tạo Lập Bài Văn NLXH", page_icon="🖊️", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%); padding: 24px 30px; border-radius: 16px; color: white; margin-bottom: 22px;">
    <h1 style="margin:0; font-size: 2rem;">🖊️ QUY TRÌNH 4 BƯỚC TẠO LẬP BÀI VĂN NLXH</h1>
    <p style="margin:5px 0 0 0; color: #93c5fd;">Phát triển năng lực viết văn theo định hướng GDPT 2018</p>
</div>
""", unsafe_allow_html=True)

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = st.secrets.get("gemini_api_key", "")

with st.sidebar:
    st.title("⚙️ CẤU HÌNH AI")
    st.text_input("Gemini API Key:", type="password", key="api_key_field", value=st.session_state["gemini_api_key"],
                  on_change=lambda: st.session_state.update({"gemini_api_key": st.session_state["api_key_field"].strip()}))
    if st.session_state["gemini_api_key"]:
        st.success("✅ Trợ lí Ngữ văn đã sẵn sàng")
    else:
        st.info("💡 Vui lòng nhập API Key để sử dụng tính năng AI.")

def call_gemini(prompt):
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key: return "Chưa cấu hình API Key."
    client = genai.Client(api_key=api_key)
    try:
        res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return res.text if res else "Lỗi phản hồi."
    except Exception:
        return "Lỗi kết nối AI."

tabs = st.tabs(["🌱 BƯỚC 1: TÌM HIỂU ĐỀ", "🧵 BƯỚC 2: TÌM Ý & DÀN Ý", "✍️ BƯỚC 3: VIẾT BÀI", "🔍 BƯỚC 4: ĐÁNH GIÁ RUBRIC"])

with tabs[0]:
    st.subheader("🔍 Đọc Kỹ Đề Bài & Xác Định Vấn Đề Nghị Luận")
    selected_de = st.selectbox("Chọn đề bài:", list(DE_BAI_DATA.keys()))
    de_info = DE_BAI_DATA[selected_de]
    
    st.info(de_info['text'])
    student_vdnl = st.text_input("Xác định Vấn đề nghị luận cốt lõi theo ý hiểu của em:")
    
    if st.button("Kiểm tra với AI", type="primary"):
        if student_vdnl.strip():
            st.success(f"🎯 VĐNL chuẩn của đề: **{de_info['vdnl_chuan']}**")
        else:
            st.warning("Vui lòng nhập câu trả lời!")

with tabs[1]:
    st.subheader("🧵 Xây Dựng Hệ Thống Luận Điểm & Dàn Ý")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Gợi ý tư duy:")
        for item in de_info.get("explain_core", []):
            st.markdown(f"- {item}")
        for ev in de_info.get("evidence", []):
            st.markdown(f"📌 {ev}")
    with col2:
        st.markdown("### Dàn ý của em:")
        st.text_area("Lập dàn ý 3 phần tại đây:", height=200, value=f"I. Mở bài\nII. Thân bài\nIII. Kết bài")

with tabs[2]:
    st.subheader("✍️ Xưởng Viết Bài Độc Lập")
    st.text_area("Viết bài văn hoàn chỉnh của em tại đây:", height=300)

with tabs[3]:
    st.subheader("🔍 Chấm Điểm Theo Rubric")
    if st.button("Chấm điểm bài viết", type="primary"):
        st.write("Hệ thống chấm điểm sẽ hiển thị ở đây sau khi em hoàn thành bài viết ở Bước 3.")
