"""
ScamShield AI - URL Feature Extraction Module
Trích xuất đặc trưng hình thái (lexical & structural) của URL phục vụ mô hình Machine Learning.
Lưu ý bảo mật: KHÔNG thực hiện request HTTP tới URL để phòng tránh SSRF và mã độc.
"""

import re
from urllib.parse import urlparse

# Danh sách TLD thường bị kẻ xấu lạm dụng cho phishing miễn phí / giá rẻ
SUSPICIOUS_TLDS = {
    "xyz", "top", "club", "tk", "ml", "ga", "cf", "gq", "work", "date",
    "racing", "men", "party", "click", "site", "online", "live", "vip", "cc"
}

# Các từ khóa nhạy cảm thường thấy trong đường link phishing mạo danh tại VN
SUSPICIOUS_URL_KEYWORDS = [
    "login", "signin", "verify", "secure", "account", "banking", "ebank", "digibank",
    "vcb", "bidv", "vietinbank", "mbbank", "techcombank", "acb", "sacombank",
    "otp", "update", "service", "reward", "qua-tang", "khuyenmai", "voucher",
    "phat-nguoi", "canhsat", "kiem-tien", "nhanthuong"
]

def extract_url_features(url_str: str) -> dict:
    """
    Trích xuất từ điển các đặc trưng số học từ chuỗi URL.
    """
    if not url_str or not isinstance(url_str, str):
        url_str = ""

    url_str = url_str.strip()

    # Thêm scheme giả định nếu thiếu để urlparse phân tích đúng netloc
    parsed_url = url_str
    if not re.match(r"^[a-zA-Z]+://", url_str):
        parsed_url = "http://" + url_str

    try:
        parsed = urlparse(parsed_url)
        hostname = parsed.hostname or ""
        path = parsed.path or ""
        query = parsed.query or ""
    except Exception:
        hostname = ""
        path = ""
        query = ""

    # 1. Các độ dài cơ bản
    url_length = len(url_str)
    hostname_length = len(hostname)
    path_length = len(path)

    # 2. Đếm ký tự đặc biệt
    count_dots = url_str.count(".")
    count_hyphens = url_str.count("-")
    count_underscores = url_str.count("_")
    count_slashes = url_str.count("/")
    count_question = url_str.count("?")
    count_equals = url_str.count("=")
    count_at = url_str.count("@")
    count_ampersand = url_str.count("&")

    # 3. Kiểm tra hostname là địa chỉ IP (IPv4)
    has_ip = 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) else 0

    # 4. Tỷ lệ chữ số trên toàn URL
    digits_count = sum(c.isdigit() for c in url_str)
    digits_ratio = digits_count / max(1, url_length)

    # 5. Phân tích TLD (đuôi tên miền)
    tld = hostname.split(".")[-1].lower() if "." in hostname else ""
    is_suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0

    # 6. Đếm từ khóa nhạy cảm trong URL
    lower_url = url_str.lower()
    suspicious_keyword_count = sum(1 for kw in SUSPICIOUS_URL_KEYWORDS if kw in lower_url)

    # 7. Kiểm tra có cổng (port) bất thường không
    has_custom_port = 1 if parsed.port and parsed.port not in [80, 443] else 0

    # 8. Kiểm tra URL rút gọn (shortened URL)
    shortener_domains = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd", "buff.ly", "ow.ly"}
    is_shortened = 1 if hostname.lower() in shortener_domains else 0

    features = {
        "url_length": url_length,
        "hostname_length": hostname_length,
        "path_length": path_length,
        "count_dots": count_dots,
        "count_hyphens": count_hyphens,
        "count_underscores": count_underscores,
        "count_slashes": count_slashes,
        "count_question": count_question,
        "count_equals": count_equals,
        "count_at": count_at,
        "has_ip": has_ip,
        "digits_ratio": round(digits_ratio, 4),
        "is_suspicious_tld": is_suspicious_tld,
        "suspicious_keyword_count": suspicious_keyword_count,
        "has_custom_port": has_custom_port,
        "is_shortened": is_shortened
    }

    return features

def get_feature_vector(features: dict) -> list:
    """
    Chuyển dictionary đặc trưng thành vector danh sách theo đúng thứ tự huấn luyện.
    """
    feature_keys = [
        "url_length", "hostname_length", "path_length",
        "count_dots", "count_hyphens", "count_underscores", "count_slashes",
        "count_question", "count_equals", "count_at",
        "has_ip", "digits_ratio", "is_suspicious_tld",
        "suspicious_keyword_count", "has_custom_port", "is_shortened"
    ]
    return [features.get(k, 0) for k in feature_keys]
