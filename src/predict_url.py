"""
ScamShield AI - URL Prediction Module
Dự đoán mức độ độc hại / lừa đảo của URL bằng mô hình Machine Learning
dựa trên 12 đặc trưng hình thái hostname (nhất quán với quá trình huấn luyện PhishVN).

Lưu ý bảo mật: KHÔNG thực hiện HTTP request tới URL (chống SSRF).
"""

import os
import re
from urllib.parse import urlparse

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
URL_MODEL_PATH = os.path.join(MODEL_DIR, "url_model.pkl")

# Danh sách TLD đáng ngờ (thường bị lạm dụng để phishing miễn phí/rẻ)
SUSPICIOUS_TLDS = {
    "xyz", "top", "club", "tk", "ml", "ga", "cf", "gq", "work", "date",
    "racing", "men", "party", "click", "site", "online", "live", "vip", "cc",
    "pw", "ru", "ws", "info", "biz", "mobi"
}

# Từ khóa giả mạo thường thấy trong URL phishing Việt Nam
# Chỉ dùng từ khóa đặc thù, tránh từ thông dụng như 'nhan', 'xac', 'phat'
SUSPICIOUS_KEYWORDS = [
    "login", "signin", "verify", "secure", "account", "banking", "ebank", "digibank",
    "otp-verify", "xac-minh", "cap-nhat", "truy-cap",
    "reward", "voucher", "nhan-thuong", "qua-tang", "khuyenmai",
    "phat-nguoi", "kiem-tien", "nhanthuong"
]

# Dịch vụ rút gọn link phổ biến
SHORTENER_DOMAINS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd", "buff.ly", "ow.ly"}

# Whitelist tên miền hợp lệ đã xác minh (tránh false positive do dataset bias)
# Dataset PhishVN benign chủ yếu là .gov.vn, nên model kém với .com.vn thương mại
TRUSTED_DOMAIN_SUFFIXES = {
    # Ngân hàng Việt Nam chính thống
    "vietcombank.com.vn", "vietinbank.vn", "bidv.com.vn", "bidv.vn",
    "agribank.com.vn", "techcombank.com.vn", "techcombank.com",
    "mbbank.com.vn", "acb.com.vn", "sacombank.com.vn", "sacombank.com",
    "vpbank.com.vn", "tpbank.vn", "tpbank.com.vn", "ocb.com.vn",
    "hdbank.com.vn", "vib.com.vn", "vib.vn", "shb.com.vn",
    "seabank.com.vn", "msb.com.vn", "shinhanbank.com.vn", "shinhan.com.vn",
    # Ví điện tử & Fintech
    "momo.vn", "zalopay.vn", "vnpay.vn", "viettelmoney.vn",
    # Chính phủ và dịch vụ công
    "chinhphu.vn", "dichvucong.gov.vn", "ncsc.vn", "mof.gov.vn",
    "most.gov.vn", "bca.gov.vn", "bocongan.gov.vn", "mic.gov.vn",
    # Tin tức lớn
    "vnexpress.net", "dantri.com.vn", "tuoitre.vn", "thanhnien.vn",
    "vietnamnet.vn", "vtv.vn", "vov.vn", "laodong.vn", "plo.vn",
    # Thương mại điện tử lớn
    "shopee.vn", "lazada.vn", "tiki.vn", "sendo.vn",
    # Mạng xã hội / Công nghệ
    "google.com", "google.com.vn", "facebook.com", "fb.com", "youtube.com",
    "zalo.me", "github.com", "microsoft.com", "apple.com",
    # Viễn thông
    "viettel.vn", "vietteltelecom.vn", "viettelstore.vn",
    "vinaphone.vn", "mobifone.vn", "vnpt.com.vn",
}


def extract_url_features_v2(url_str: str) -> dict:
    """
    Trích xuất 12 đặc trưng hình thái URL theo chuẩn PhishVN training data.
    Tập trung vào đặc trưng domain/hostname thay vì toàn bộ URL path.
    """
    if not url_str or not isinstance(url_str, str):
        url_str = ""
    url_str = url_str.strip()

    # Parse URL
    url_for_parse = url_str if re.match(r"^[a-zA-Z]+://", url_str) else "http://" + url_str
    try:
        parsed = urlparse(url_for_parse)
        hostname = parsed.hostname or ""
        path = parsed.path or ""
    except Exception:
        hostname = ""
        path = ""

    # 1. Độ dài URL (domain-only nếu không có path, full nếu có)
    url_len = len(url_str)

    # 2. Đếm dấu chấm trong URL
    num_dots = url_str.count(".")

    # 3. Số lượng subdomain (phần hostname ngoài domain chính)
    parts = [p for p in hostname.split(".") if p]
    num_subdomains = max(0, len(parts) - 2) if len(parts) > 2 else 0

    # 4. Kiểm tra IP address
    has_ip = 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname) else 0

    # 5. Kiểm tra ký tự @ (có thể dùng để lừa đảo)
    has_at = 1 if "@" in url_str else 0

    # 6. TLD đáng ngờ
    tld = parts[-1].lower() if parts else ""
    suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0

    # 7. Số dấu gạch ngang trong hostname (không tính path)
    num_hyphens = hostname.count("-")

    # 8. Độ dài hostname
    hostname_len = len(hostname)

    # 9. Tỷ lệ chữ số trong hostname
    digits_in_hostname = sum(c.isdigit() for c in hostname)
    digits_ratio = digits_in_hostname / max(1, hostname_len)

    # 10. Từ khóa đáng ngờ trong URL — dùng whole-word hoặc hyphen-separated để tránh match sai
    low_url = url_str.lower()
    suspicious_keyword_count = 0
    for kw in SUSPICIOUS_KEYWORDS:
        # Tránh match từ khóa nằm bên trong từ dài hơn (ví dụ: 'vcb' trong 'vietcombank')
        # Chỉ match nếu kw là toàn bộ path segment hoặc domain label
        if kw in low_url:
            # Kiểm tra xem kw có là substring của từ dài hơn không
            idx = low_url.find(kw)
            before = low_url[idx-1] if idx > 0 else '-'
            after = low_url[idx + len(kw)] if idx + len(kw) < len(low_url) else '-'
            # Chỉ đếm nếu bao quanh bởi ký tự phân cách (không phải chữ cái/số)
            if not before.isalnum() and not after.isalnum():
                suspicious_keyword_count += 1

    # 11. Dịch vụ rút gọn link
    is_shortened = 1 if hostname.lower() in SHORTENER_DOMAINS else 0

    # 12. Có path component không — đây KHÔNG phải tín hiệu phishing
    # (URL hợp lệ thường có path, nhưng dataset PhishVN chứa domain-only)
    # Để tránh false positive, ta dùng path = 0 cho cả hai trường hợp
    has_path = 0  # Không dùng feature này trong prediction (neutralized)

    return {
        "url_len": url_len,
        "num_dots": num_dots,
        "num_subdomains": num_subdomains,
        "has_ip": has_ip,
        "has_at": has_at,
        "suspicious_tld": suspicious_tld,
        "num_hyphens": num_hyphens,
        "hostname_len": hostname_len,
        "digits_ratio": round(digits_ratio, 4),
        "suspicious_keyword_count": suspicious_keyword_count,
        "is_shortened": is_shortened,
        "has_path": has_path,
        # Thông tin bổ sung cho UI (không dùng trong model)
        "_hostname": hostname,
        "_tld": tld,
    }


def get_feature_vector_v2(features: dict) -> list:
    """Chuyển đặc trưng thành vector 12 chiều cho mô hình."""
    keys = [
        "url_len", "num_dots", "num_subdomains", "has_ip", "has_at",
        "suspicious_tld", "num_hyphens", "hostname_len", "digits_ratio",
        "suspicious_keyword_count", "is_shortened", "has_path"
    ]
    return [float(features.get(k, 0)) for k in keys]


def predict_url(url: str) -> dict:
    """
    Phân tích và dự đoán độ rủi ro của URL.

    Định dạng trả về:
    {
        "is_phishing": bool,
        "phishing_probability": float (0.0 - 1.0),
        "confidence_level": str ("Cao", "Trung bình", "Thấp"),
        "model_type": str,
        "features": dict,
        "suspicious_factors": list
    }
    """
    if not url or not isinstance(url, str):
        return {
            "is_phishing": False,
            "phishing_probability": 0.0,
            "confidence_level": "Thấp",
            "model_type": "none",
            "features": {},
            "suspicious_factors": []
        }

    features = extract_url_features_v2(url)
    hostname = (features.get("_hostname") or "").lower().strip()

    # 1. Kiểm tra Whitelist tên miền uy tín đã xác minh trước
    # Tránh triệt để False Positive với ngân hàng, báo chí, CQNN do bias dữ liệu huấn luyện
    is_trusted = False
    if hostname:
        # Tên miền chính phủ Việt Nam (.gov.vn) được cấp phép chặt chẽ bởi VNNIC
        if hostname == "gov.vn" or hostname.endswith(".gov.vn"):
            is_trusted = True
        else:
            for trusted in TRUSTED_DOMAIN_SUFFIXES:
                trusted_clean = trusted.lower().strip()
                if hostname == trusted_clean or hostname.endswith("." + trusted_clean):
                    is_trusted = True
                    break

    if is_trusted:
        return {
            "is_phishing": False,
            "phishing_probability": 0.01,
            "confidence_level": "Cao",
            "model_type": "Whitelist_Verified",
            "features": {k: v for k, v in features.items() if not k.startswith("_")},
            "suspicious_factors": []
        }

    # Liệt kê các yếu tố đáng ngờ cho UI
    suspicious_factors = []
    if features.get("has_ip") == 1:
        suspicious_factors.append("Sử dụng địa chỉ IP trực tiếp thay vì tên miền hợp lệ")
    if features.get("suspicious_tld") == 1:
        suspicious_factors.append("Đuôi tên miền (TLD) có độ tin cậy thấp, thường bị lạm dụng")
    if features.get("is_shortened") == 1:
        suspicious_factors.append("Sử dụng dịch vụ rút gọn link để che giấu đích đến thực tế")
    if features.get("suspicious_keyword_count", 0) > 0:
        suspicious_factors.append(f"Chứa {features['suspicious_keyword_count']} từ khóa giả mạo ngân hàng / xác minh")
    if features.get("num_dots", 0) >= 4:
        suspicious_factors.append("Chứa quá nhiều subdomain (≥ 4 dấu chấm)")
    if features.get("has_at") == 1:
        suspicious_factors.append("Chứa ký tự @ bất thường trong URL")
    if features.get("num_hyphens", 0) >= 3:
        suspicious_factors.append("Tên miền chứa nhiều dấu gạch ngang (≥ 3)")

    # Kiểm tra mô hình ML đã lưu
    if os.path.exists(URL_MODEL_PATH):
        try:
            import joblib
            model = joblib.load(URL_MODEL_PATH)
            feat_vec = [get_feature_vector_v2(features)]
            prob = float(model.predict_proba(feat_vec)[0][1])
            is_phishing = prob >= 0.5
            conf = "Cao" if prob >= 0.8 or prob <= 0.2 else "Trung bình"

            return {
                "is_phishing": is_phishing,
                "phishing_probability": round(prob, 4),
                "confidence_level": conf,
                "model_type": "ML_Trained_Model",
                "features": {k: v for k, v in features.items() if not k.startswith("_")},
                "suspicious_factors": suspicious_factors
            }
        except Exception:
            pass

    # Chế độ dự phòng Heuristic
    risk_score = 0.0
    risk_score += len(suspicious_factors) * 0.2
    if features.get("has_ip"):
        risk_score += 0.3
    if features.get("suspicious_tld"):
        risk_score += 0.25
    risk_score = min(1.0, risk_score)
    is_phishing = risk_score >= 0.5
    conf = "Trung bình" if suspicious_factors else "Thấp"

    return {
        "is_phishing": is_phishing,
        "phishing_probability": round(risk_score, 4),
        "confidence_level": conf,
        "model_type": "Heuristic_Baseline",
        "features": {k: v for k, v in features.items() if not k.startswith("_")},
        "suspicious_factors": suspicious_factors
    }
