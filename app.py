"""
ScamShield AI - Mobile-First Cybersecurity Web Application
Hệ thống phát hiện và đánh giá rủi ro lừa đảo qua tin nhắn tiếng Việt và URL bằng Trí tuệ Nhân tạo.
Thiết kế tối ưu hóa trải nghiệm Mobile-First, PWA và giao diện An ninh Mạng cao cấp.
Phục vụ Đồ án Capstone Samsung Innovation Campus (SIC-AI).
"""

import streamlit as st
import re
import os
from src.predict_sms import predict_sms
from src.predict_url import predict_url
from src.threat_lookup import lookup_url
from src.risk_engine import build_report

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="ScamShield AI - Lá Chắn Bảo Vệ Di Động",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Hệ thống CSS Tối ưu Mobile-First, Giao diện An ninh Mạng & Ẩn hoàn toàn Watermark
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
    /* Áp dụng font chữ hiện đại cho toàn bộ ứng dụng */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1, h2, h3, h4, .brand-title {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Ẩn footer, header phụ và toàn bộ watermark Streamlit Cloud */
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    #MainMenu {visibility: hidden !important; display: none !important;}
    header[data-testid="stHeader"] {background: transparent !important;}
    
    /* Ẩn huy hiệu Streamlit Cloud, vương miện đỏ, avatar và nút Manage */
    .viewerBadge_container__1QSob, [class*="viewerBadge"], [class*="ViewerBadge"] {display: none !important; visibility: hidden !important;}
    div[class*="viewerBadge"], a[class*="viewerBadge"] {display: none !important; visibility: hidden !important;}
    [class*="profileContainer"], [class*="ProfileContainer"] {display: none !important; visibility: hidden !important;}
    [data-testid="manage-app-button"], #manage-app-button {display: none !important; visibility: hidden !important;}
    button[title*="Manage app"], button[aria-label*="Manage app"] {display: none !important;}
    img[src*="githubusercontent.com"], img[src*="avatar"] {display: none !important;}
    a[href*="streamlit.io"], a[href*="share.streamlit.io"] {display: none !important;}
    div:has(> a[href*="streamlit.io"]) {display: none !important;}
    div:has(> img[src*="githubusercontent.com"]) {display: none !important;}

    /* Tối ưu hóa layout container */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1000px !important;
    }

    /* Thẻ Hero Header phong cách Cybersecurity Glassmorphism */
    .hero-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        text-align: center;
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 14px;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 9999px;
        color: #60a5fa;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 8px;
        margin-bottom: 0;
    }

    /* Nút bấm mẫu nhanh kiểu Chips / Pills tối ưu cảm ứng */
    .quick-chips-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    /* Thẻ cảnh báo kết quả lớn (Hero Result Card) */
    .result-banner {
        border-radius: 18px;
        padding: 22px;
        margin: 18px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        animation: fadeIn 0.4s ease-in-out;
    }

    .result-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(153, 27, 27, 0.25) 100%);
        border: 1px solid rgba(239, 68, 68, 0.45);
        color: #fca5a5;
    }

    .result-caution {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(180, 83, 9, 0.25) 100%);
        border: 1px solid rgba(245, 158, 11, 0.45);
        color: #fde68a;
    }

    .result-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 95, 70, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.45);
        color: #a7f3d0;
    }

    /* Thẻ chỉ số module AI con */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }

    .metric-title {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 1.65rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        margin: 4px 0;
    }

    .metric-badge {
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        font-weight: 600;
    }

    /* Thanh tiến trình thanh lịch */
    .risk-bar-container {
        width: 100%;
        height: 12px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 9999px;
        overflow: hidden;
        margin: 12px 0 6px 0;
    }

    .risk-bar-fill-danger {
        height: 100%;
        background: linear-gradient(90deg, #f59e0b, #ef4444);
        border-radius: 9999px;
    }

    .risk-bar-fill-caution {
        height: 100%;
        background: linear-gradient(90deg, #10b981, #f59e0b);
        border-radius: 9999px;
    }

    .risk-bar-fill-safe {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #10b981);
        border-radius: 9999px;
    }

    /* Bằng chứng vi phạm dạng Tag Badge */
    .evidence-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.28);
        color: #fca5a5;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin: 4px 4px 4px 0;
        font-weight: 500;
    }

    .safe-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: #86efac;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin: 4px 4px 4px 0;
        font-weight: 500;
    }

    /* Nút gọi khẩn cấp 1-chạm */
    .emergency-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 8px;
        margin-top: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.15s ease;
    }
    .emergency-btn:hover {
        transform: scale(1.02);
    }

    /* Tối ưu hóa đặc biệt trên màn hình điện thoại (Mobile) */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        .hero-title {
            font-size: 1.55rem !important;
        }
        .hero-card {
            padding: 18px 14px !important;
        }
        .metric-value {
            font-size: 1.4rem !important;
        }
        .stButton > button {
            min-height: 48px !important;
            font-size: 1.05rem !important;
            border-radius: 12px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header chính (Hero Banner)
st.markdown("""
    <div class="hero-card">
        <span class="hero-badge">SIC-AI Capstone • Mobile-First Edition</span>
        <h1 class="hero-title">🛡️ ScamShield AI</h1>
        <p class="hero-subtitle">
            Hệ thống phát hiện & đánh giá rủi ro lừa đảo qua tin nhắn tiếng Việt và đường link bằng Trí tuệ Nhân tạo
        </p>
    </div>
""", unsafe_allow_html=True)

# 4. Sidebar: Thông tin hệ thống và tra cứu nhanh
with st.sidebar:
    st.markdown("### 🛡️ ScamShield AI System")
    st.markdown("**Phiên bản:** `v1.2.0 (Mobile Ready)`")
    st.markdown("**Kiến trúc:**")
    st.markdown("- **Frontend:** Streamlit Mobile-First PWA")
    st.markdown("- **Backend:** FastAPI REST API (`api.py`)")
    st.markdown("- **SMS NLP:** Random Forest (F1: `85.98%`)")
    st.markdown("- **URL Engine:** Logistic Regression (F1: `86.09%`)")
    st.markdown("- **Whitelist:** 50+ tên miền ngân hàng & .gov.vn")
    
    st.markdown("---")
    st.markdown("🚨 **Tổng đài phản ánh khẩn cấp:**")
    st.markdown("- **156** hoặc **5656** (Cục ATTT)")
    st.markdown("- Tra cứu tên miền: [tracuutenmien.gov.vn](https://tracuutenmien.gov.vn)")
    
    st.markdown("---")
    st.markdown("📱 **Quét mã QR trên điện thoại:**")
    if os.path.exists("reports/qr_code_scamshield.png"):
        st.image("reports/qr_code_scamshield.png", caption="Mở ngay trên Smartphone", use_container_width=True)

# 5. Hệ thống Tab chính: Quét rủi ro, Cài đặt Mobile PWA, Cẩm nang an toàn
tab_scan, tab_pwa, tab_edu = st.tabs([
    "🔍 Quét Rủi Ro (Mobile Scanner)",
    "📱 Cài Đặt Mobile App (PWA & QR)",
    "📖 Cẩm Nang An Toàn & Tra Cứu"
])

with tab_scan:
    # Các nút nạp nhanh mẫu thử nghiệm (Quick-tap Chips) ngay đầu trang
    st.markdown('<div class="quick-chips-title">⚡ Chọn nhanh mẫu thử nghiệm (Dành cho Mobile & Trình chiếu):</div>', unsafe_allow_html=True)
    
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    
    sample_vcb = "Thong bao: Tai khoan VCB Digibank cua quy khach bi khoa do dang nhap bat thuong tren thiet bi la. Vui long truy cap http://vcb-digibank-login.xyz/verify de xac minh trong 24h."
    sample_gift = "Chuc mung ban da trung thuong 1 iPhone 16 Pro Max tri gia 34.000.000d tu chuong trinh tri an khach hang. Nhan thuong ngay tai: http://qua-tang-tri-an.top/nhanthuong"
    sample_fine = "Cuc Canh Sat Giao Thong thong bao: Phuong tien cua ban co bien ban vi pham phat nguoi 5.000.000d. Vui long nop phat truc tuyen qua cong: http://csgt-nop-phat-nguoi.site/tra-cuu"
    sample_safe = "Cam on quy khach da thanh toan thanh cong hoa don tien dien thang 10 so tien 450.000d qua Viettel Money. Ma GD: VT123456789. Chi tiet tai https://viettelmoney.vn"

    with c_m1:
        if st.button("🚨 Mạo danh VCB Digibank", use_container_width=True):
            st.session_state["sms_input"] = sample_vcb
            st.session_state["url_input"] = "http://vcb-digibank-login.xyz/verify"
    with c_m2:
        if st.button("🎁 Trúng thưởng iPhone", use_container_width=True):
            st.session_state["sms_input"] = sample_gift
            st.session_state["url_input"] = "http://qua-tang-tri-an.top/nhanthuong"
    with c_m3:
        if st.button("⚡ Phạt nguội Bộ CA", use_container_width=True):
            st.session_state["sms_input"] = sample_fine
            st.session_state["url_input"] = "http://csgt-nop-phat-nguoi.site/tra-cuu"
    with c_m4:
        if st.button("✅ Tin nhắn an toàn mẫu", use_container_width=True):
            st.session_state["sms_input"] = sample_safe
            st.session_state["url_input"] = "https://viettelmoney.vn"

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Ô nhập liệu
    col_input1, col_input2 = st.columns([1, 1])
    
    with col_input1:
        sms_text = st.text_area(
            "1. Nội dung tin nhắn nghi ngờ (SMS / Zalo / Telegram):",
            value=st.session_state.get("sms_input", ""),
            height=130,
            placeholder="Dán toàn bộ nội dung tin nhắn bạn nhận được tại đây...",
            help="Hệ thống tự động phát hiện các từ khóa đe dọa, tạo áp lực tâm lý và bóc tách liên kết."
        )

    with col_input2:
        url_text = st.text_input(
            "2. Đường link / URL cần phân tích (Tùy chọn):",
            value=st.session_state.get("url_input", ""),
            placeholder="Ví dụ: http://vcb-digibank-login.xyz hoặc tên miền lạ...",
            help="Phân tích tĩnh hình thái URL không truy cập mạng, an toàn tuyệt đối chống mã độc."
        )

    # Tự động trích xuất URL nếu dán vào SMS
    if sms_text and not url_text:
        urls_found = re.findall(r"https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?", sms_text)
        if urls_found:
            url_text = urls_found[0]
            st.caption(f"ℹ️ Đã tự động nhận diện liên kết: `{url_text}`")

    # Nút bấm hành động chính (Mobile-First Tap Target lớn)
    btn_scan = st.button("🛡️ PHÂN TÍCH RỦI RO NGAY", type="primary", use_container_width=True)

    if btn_scan:
        if not sms_text.strip() and not url_text.strip():
            st.warning("⚠️ Vui lòng nhập ít nhất một nội dung tin nhắn hoặc một đường link để phân tích!")
        else:
            with st.spinner("Đang chạy mô hình NLP & Phân tích cấu trúc hình thái URL..."):
                sms_res = predict_sms(sms_text) if sms_text.strip() else None
                url_res = predict_url(url_text) if url_text.strip() else None
                lookup_res = lookup_url(url_text) if url_text.strip() else None
                report = build_report(sms_res, url_res, lookup_res)

            alert_level = report["alert_level"]
            sms_prob = report.get("sms_probability", 0.0)
            url_prob = report.get("url_probability", 0.0)
            overall_score = max(sms_prob, url_prob)
            overall_pct = overall_score * 100

            # 1. Hero Result Card
            if alert_level == "DANGEROUS":
                card_class = "result-danger"
                bar_class = "risk-bar-fill-danger"
                icon_tag = "🚨 NGUY CƠ CAO (LỪA ĐẢO / PHISHING)"
                score_color = "#f87171"
            elif alert_level == "CAUTION":
                card_class = "result-caution"
                bar_class = "risk-bar-fill-caution"
                icon_tag = "⚠️ CẦN THẬN TRỌNG (DẤU HIỆU ĐÁNG NGỜ)"
                score_color = "#fbbf24"
            else:
                card_class = "result-safe"
                bar_class = "risk-bar-fill-safe"
                icon_tag = "✅ AN TOÀN (TIN CẬY / XÁC THỰC)"
                score_color = "#34d399"

            st.markdown(f"""
                <div class="result-banner {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <span style="font-size: 1.15rem; font-weight: 800; text-transform: uppercase;">{icon_tag}</span>
                        <span style="font-size: 1.6rem; font-weight: 800; font-family: 'Outfit'; color: {score_color};">{overall_pct:.1f}% RỦI RO</span>
                    </div>
                    <div class="risk-bar-container">
                        <div class="{bar_class}" style="width: {min(max(overall_pct, 6.0), 100.0):.1f}%;"></div>
                    </div>
                    <div style="font-size: 0.92rem; margin-top: 6px;">
                        <strong>Đánh giá:</strong> {report['status_label']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 2. Chi tiết 3 nhánh phòng thủ AI
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">💬 Tin nhắn SMS (NLP AI)</div>
                        <div class="metric-value" style="color: {'#ef4444' if sms_prob >= 0.7 else ('#f59e0b' if sms_prob >= 0.35 else '#10b981')};">
                            {sms_prob * 100:.1f}%
                        </div>
                        <div class="metric-badge" style="background: rgba(255,255,255,0.1); color: #cbd5e1;">
                            {sms_res.get('confidence_level', 'Độ tin cậy cao') if sms_res else 'Chưa nhập SMS'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">🔗 Hình thái URL & Tên miền</div>
                        <div class="metric-value" style="color: {'#ef4444' if url_prob >= 0.7 else ('#f59e0b' if url_prob >= 0.35 else '#10b981')};">
                            {url_prob * 100:.1f}%
                        </div>
                        <div class="metric-badge" style="background: rgba(255,255,255,0.1); color: #cbd5e1;">
                            {url_res.get('confidence_level', 'Độ tin cậy cao') if url_res else 'Chưa có URL'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with c3:
                is_threat = lookup_res.get("is_threat", False) if lookup_res else False
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">🌐 Tình báo đe dọa (Intel)</div>
                        <div class="metric-value" style="color: {'#ef4444' if is_threat else '#10b981'}; font-size: 1.3rem; line-height: 2.2rem;">
                            {'Đe dọa đã biết' if is_threat else 'An toàn / Sạch'}
                        </div>
                        <div class="metric-badge" style="background: rgba(255,255,255,0.1); color: #cbd5e1;">
                            {lookup_res.get('status', 'AI Engine Cục bộ') if lookup_res else 'Nguồn Whitelist'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # 3. Danh sách bằng chứng vi phạm cụ thể (XAI)
            st.markdown("#### 🔍 Bằng chứng & Dấu hiệu phát hiện (Explainable AI):")
            if report.get("reasons"):
                badges_html = "".join([f'<span class="evidence-badge">⚠️ {r}</span>' for r in report["reasons"]])
                st.markdown(badges_html, unsafe_allow_html=True)
            else:
                st.markdown('<span class="safe-badge">✅ Không phát hiện bất kỳ dấu hiệu thao túng tâm lý hay tên miền giả mạo nào.</span>', unsafe_allow_html=True)

            # 4. Khuyến nghị an toàn số & Nút gọi khẩn cấp
            st.markdown("#### 🛡️ Khuyến nghị an toàn tức thời:")
            for adv in report.get("advice", []):
                st.markdown(f"- {adv}")

            # Nút gọi phản ánh khẩn cấp 1-chạm
            st.markdown("""
                <div style="margin-top: 14px; margin-bottom: 10px;">
                    <a href="tel:156" class="emergency-btn">📞 Gọi Tổng đài 156 (Miễn phí)</a>
                    <a href="tel:5656" class="emergency-btn" style="background: linear-gradient(135deg, #b91c1c, #7f1d1d);">📞 Phản ánh qua 5656</a>
                    <a href="https://tracuutenmien.gov.vn" target="_blank" class="emergency-btn" style="background: linear-gradient(135deg, #1e40af, #1e3a8a);">🌐 Tra cứu tên miền Bộ TT&TT</a>
                </div>
            """, unsafe_allow_html=True)

            # 5. Minh bạch giới hạn hệ thống
            with st.expander("ℹ️ Giới hạn kỹ thuật và tuyên bố miễn trừ trách nhiệm"):
                for lim in report.get("limitations", []):
                    st.caption(f"• {lim}")

with tab_pwa:
    st.subheader("📱 Cài đặt Ứng dụng Di động (PWA) & Trải nghiệm Trên Smartphone")
    st.markdown("""
        Hệ thống được thiết kế theo tiêu chuẩn **Progressive Web App (PWA)**, cho phép bạn cài đặt trực tiếp về màn hình chính điện thoại như một ứng dụng Native mà **không cần qua App Store hay Google Play**.
    """)

    col_qr, col_guide = st.columns([1, 1])

    with col_qr:
        if os.path.exists("reports/qr_code_scamshield.png"):
            st.image("reports/qr_code_scamshield.png", caption="Mở camera điện thoại quét để vào ứng dụng ngay", use_container_width=True)
        else:
            st.info("Mã QR đang sẵn sàng tại địa chỉ web trực tuyến.")

    with col_guide:
        st.markdown("""
            #### 📲 Hướng dẫn 2 bước cài đặt về màn hình chính:
            
            **1. Đối với iPhone (Trình duyệt Safari):**
            - Mở đường link ứng dụng trên Safari.
            - Bấm vào nút **Chia sẻ** (biểu tượng hình vuông có mũi tên trỏ lên ở thanh dưới cùng).
            - Chọn **"Thêm vào Màn hình chính" (Add to Home Screen)**.
            - Biểu tượng lá chắn ScamShield AI sẽ xuất hiện trên màn hình điện thoại của bạn!

            **2. Đối với Android (Trình duyệt Google Chrome):**
            - Mở link trên Chrome.
            - Bấm vào dấu **3 chấm** ở góc trên bên phải.
            - Chọn **"Cài đặt ứng dụng"** hoặc **"Thêm vào màn hình chính"**.
            - Xác nhận cài đặt để sử dụng toàn màn hình.

            ---
            #### 🚀 Kiến trúc Backend REST API cho Mobile App:
            - **RESTful API Backend:** Chúng em đã xây dựng sẵn file `api.py` sử dụng **FastAPI**.
            - **Swagger Docs:** Cung cấp tài liệu API tự động tại endpoint `/docs`.
            - **Khả năng mở rộng:** Dễ dàng kết nối với ứng dụng Android Native (Kotlin) để lắng nghe sự kiện `RECEIVE_SMS` và quét tự động trong tương lai.
        """)

with tab_edu:
    st.subheader("📖 Cẩm nang phòng chống lừa đảo trực tuyến tại Việt Nam")
    st.markdown("""
    Theo thống kê từ Cục An toàn thông tin (Bộ TT&TT), 90% các vụ lừa đảo tài chính qua mạng xuất phát từ 4 chiêu trò kinh điển sau:

    - **1. Giả mạo SMS Brandname ngân hàng:** Kẻ gian dùng trạm phát sóng BTS giả mạo chèn tin nhắn vào luồng SMS của ngân hàng (Vietcombank, MB, Techcombank) báo tài khoản bị khóa và gửi kèm link độc hại.
    - **2. Bẫy tâm lý khẩn cấp (Urgency Manipulation):** Ép nạn nhân hành động trong vòng 24 giờ hoặc đe dọa khởi tố để nạn nhân hoảng loạn không kịp xác minh với người thân.
    - **3. Tên miền tương tự (Typosquatting & Look-alike Domains):** Thay đổi ký tự hoặc thêm đuôi bất thường như `.top`, `.xyz`, `.site`, `.vip` (ví dụ: `vietcombank-login.xyz`).
    - **4. Yêu cầu mật khẩu và mã OTP:** Cơ quan công an, viện kiểm sát và ngân hàng **TUYỆT ĐỐI KHÔNG BAO GIỜ** yêu cầu người dân đọc mã OTP hoặc nhập mật khẩu ngân hàng qua các trang web lạ.
    """)
    
    st.info("💡 **Ghi nhớ thần chú:** 'Không hoảng sợ - Không bấm link lạ - Gọi ngay tổng đài 156 hoặc chi nhánh ngân hàng gần nhất để kiểm chứng!'")
