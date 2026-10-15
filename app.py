"""
ScamShield AI - Streamlit Web Application
Hệ thống phát hiện và đánh giá rủi ro lừa đảo qua tin nhắn và URL bằng AI.
Phục vụ đánh giá Đồ án Capstone Samsung Innovation Campus (SIC-AI).
"""

import streamlit as st
import re
from src.predict_sms import predict_sms
from src.predict_url import predict_url
from src.threat_lookup import lookup_url
from src.risk_engine import build_report

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="ScamShield AI - Phát Hiện Lừa Đảo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header chính
st.title("🛡️ ScamShield AI")
st.markdown(
    "**Hệ thống phát hiện và đánh giá rủi ro tin nhắn & đường link lừa đảo trực tuyến bằng Trí tuệ Nhân tạo**"
)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("💡 Hướng dẫn nhanh")
    st.markdown(
        "Dán tin nhắn hoặc đường link bạn nghi ngờ vào khung kiểm tra để hệ thống phân tích mức độ an toàn bằng AI."
    )
    
    st.subheader("📋 Mẫu thử nghiệm nhanh:")
    sample_scam_sms = "Thong bao: Tai khoan VCB Digibank cua quy khach bi khoa do dang nhap bat thuong. Vui long truy cap http://vcb-digibank-login.xyz/verify de xac minh trong 24h hoac lien he 0912345678."
    sample_safe_sms = "Cam on quy khach da thanh toan tien dien thang 10 so tien 450.000d qua Viettel Money. Ma giao dich: VT123456789."
    
    if st.button("📋 Nạp tin nhắn lừa đảo mẫu", use_container_width=True):
        st.session_state["sms_input"] = sample_scam_sms
        st.session_state["url_input"] = "http://vcb-digibank-login.xyz/verify"
        
    if st.button("✅ Nạp tin nhắn an toàn mẫu", use_container_width=True):
        st.session_state["sms_input"] = sample_safe_sms
        st.session_state["url_input"] = ""

    st.markdown("---")
    st.markdown("🚨 **Tổng đài phản ánh lừa đảo:**")
    st.markdown("- **156** hoặc **5656** (Cục ATTT - Bộ TT&TT)")
    st.markdown("- Tra cứu tên miền: [tracuutenmien.gov.vn](https://tracuutenmien.gov.vn)")

# Tạo các tab chính
tab_check, tab_edu = st.tabs(["🔍 Kiểm tra rủi ro", "📖 Cẩm nang an toàn số"])

with tab_check:
    st.subheader("Nhập dữ liệu cần phân tích:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sms_text = st.text_area(
            "1. Nội dung tin nhắn (SMS / Zalo / Telegram / Email):",
            value=st.session_state.get("sms_input", ""),
            height=140,
            placeholder="Dán toàn bộ nội dung tin nhắn bạn nhận được tại đây...",
            help="Giới hạn tối đa 1000 ký tự. Vui lòng không dán mã OTP hoặc mật khẩu cá nhân."
        )
    
    with col2:
        url_text = st.text_input(
            "2. Đường link / URL nghi ngờ (tùy chọn hoặc tự bóc tách từ tin nhắn):",
            value=st.session_state.get("url_input", ""),
            placeholder="Ví dụ: http://vcb-digibank-login.xyz hoặc link lạ...",
            help="Hệ thống chỉ phân tích cấu trúc tên miền, KHÔNG tự động truy cập để đảm bảo an toàn."
        )

    # Tự động trích xuất URL từ nội dung tin nhắn nếu người dùng chưa điền URL riêng
    if sms_text and not url_text:
        urls_found = re.findall(r"https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?", sms_text)
        if urls_found:
            url_text = urls_found[0]
            st.caption(f"ℹ️ Đã tự động nhận diện URL trong tin nhắn: `{url_text}`")

    # Nút bấm kích hoạt kiểm tra
    if st.button("🚀 Phân Tích Rủi Ro Ngay", type="primary", use_container_width=True):
        if not sms_text.strip() and not url_text.strip():
            st.warning("⚠️ Vui lòng nhập ít nhất một nội dung tin nhắn hoặc một đường link để phân tích!")
        else:
            with st.spinner("Đang phân tích các đặc trưng ngữ nghĩa và cấu trúc URL..."):
                # 1. Gọi module SMS
                sms_res = predict_sms(sms_text) if sms_text.strip() else None
                
                # 2. Gọi module URL
                url_res = predict_url(url_text) if url_text.strip() else None
                
                # 3. Gọi module Threat Lookup
                lookup_res = lookup_url(url_text) if url_text.strip() else None
                
                # 4. Tổng hợp báo cáo qua Risk Engine
                report = build_report(sms_res, url_res, lookup_res)

            st.markdown("---")
            st.subheader("📊 Kết quả Đánh giá Rủi ro:")

            # Hiển thị Banner kết quả
            alert_level = report["alert_level"]
            if alert_level == "DANGEROUS":
                st.error(f"### 🚨 {report['status_label']}")
            elif alert_level == "CAUTION":
                st.warning(f"### ⚠️ {report['status_label']}")
            else:
                st.success(f"### ✅ {report['status_label']}")

            # Thước đo chi tiết
            c_sms, c_url, c_ext = st.columns(3)
            with c_sms:
                if sms_res:
                    st.metric(
                        label="Xác suất Lừa đảo (SMS NLP)",
                        value=f"{report['sms_probability'] * 100:.1f}%",
                        delta=f"Độ tin cậy: {sms_res.get('confidence_level', 'Cao')}"
                    )
                else:
                    st.info("Chưa nhập văn bản tin nhắn")

            with c_url:
                if url_res:
                    st.metric(
                        label="Xác suất Phishing (URL)",
                        value=f"{report['url_probability'] * 100:.1f}%",
                        delta=f"Độ tin cậy: {url_res.get('confidence_level', 'Cao')}"
                    )
                else:
                    st.info("Chưa có liên kết URL")

            with c_ext:
                if lookup_res:
                    st.metric(
                        label="Dữ liệu Threat Intel ngoài",
                        value="Chưa phát hiện" if not lookup_res.get("is_threat") else "Nguy hại đã biết",
                        delta=lookup_res.get("status")
                    )
                else:
                    st.info("Không có dữ liệu tra cứu")

            # Bằng chứng phát hiện
            st.markdown("#### 🔍 Các bằng chứng & Dấu hiệu phát hiện:")
            if report["reasons"]:
                for r in report["reasons"]:
                    st.markdown(f"- ⚠️ **{r}**")
            else:
                st.markdown("- Không phát hiện từ khóa kích động tâm lý hay bất thường cấu trúc tên miền.")

            # Hướng dẫn hành động an toàn
            st.markdown("#### 🛡️ Khuyến nghị an toàn:")
            for adv in report["advice"]:
                st.markdown(f"- {adv}")

            # Minh bạch về giới hạn hệ thống
            with st.expander("ℹ️ Giới hạn kỹ thuật và tuyên bố miễn trừ trách nhiệm"):
                for lim in report["limitations"]:
                    st.caption(f"• {lim}")

with tab_edu:
    st.subheader("Cẩm nang phòng chống lừa đảo trực tuyến tại Việt Nam")
    st.markdown("""
    **Các dấu hiệu nhận biết lừa đảo phổ biến:**
    1. **Tạo cảm giác khẩn cấp:** Đe dọa khóa tài khoản trong 24 giờ, phạt nguội hoặc yêu cầu nộp phạt ngay.
    2. **Đường link mạo danh (Look-alike domain):** Thay chữ cái bằng số hoặc thêm từ khóa (`vietcombank-security.xyz`, `mbbank-online.top`).
    3. **Yêu cầu mã OTP:** Ngân hàng và cơ quan công an KHÔNG BAO GIỜ yêu cầu người dân cung cấp mã OTP hay mật khẩu qua điện thoại/tin nhắn.
    4. **Chiêu trò tuyển dụng:** Làm nhiệm vụ xem video, chốt đơn hàng ảo trên Telegram với hứa hẹn hoa hồng cao.
    """)
