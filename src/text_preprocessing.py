"""
ScamShield AI - Text Preprocessing Module
Xử lý dữ liệu văn bản tin nhắn tiếng Việt phục vụ trích xuất đặc trưng và mô hình NLP.
"""

import re
import unicodedata

# Từ khóa tạo áp lực tâm lý / lừa đảo thường gặp trong SMS tiếng Việt
URGENCY_KEYWORDS = [
    "khóa thẻ", "khoa the", "tài khoản bị khóa", "tai khoan bi khoa",
    "xác minh", "xac minh", "trong 24h", "trong 24 giờ", "khẩn cấp", "khan cap",
    "otp", "mã otp", "ma otp", "trúng thưởng", "trung thuong",
    "quà tặng", "qua tang", "tri ân", "tri an", "vay vốn", "vay von",
    "giải ngân", "giai ngan", "phạt nguội", "phat nguoi", "bộ công an", "bo cong an",
    "thu hồi nợ", "thu hoi no", "hoàn tiền", "hoan tien", "việc làm tại nhà", "viec lam tai nha"
]

def clean_vietnamese_text(text: str) -> str:
    """
    Chuẩn hóa văn bản tiếng Việt:
    - Chuẩn hóa Unicode (NFC)
    - Chuyển chữ thường
    - Thay thế link/URL bằng token <URL>
    - Thay thế số điện thoại bằng token <PHONE>
    - Loại bỏ ký tự đặc biệt thừa thãi
    """
    if not isinstance(text, str):
        return ""

    # Chuẩn hóa Unicode NFC
    text = unicodedata.normalize("NFC", text)
    
    # Chuyển về chữ thường
    text = text.lower()

    # Thay thế URL
    url_pattern = r"https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?"
    text = re.sub(url_pattern, " <URL> ", text)

    # Thay thế số điện thoại (10-11 số)
    phone_pattern = r"(?:\+?84|0)(?:\d{9}|\d{10})\b"
    text = re.sub(phone_pattern, " <PHONE> ", text)

    # Thay thế mã OTP xác thực thành token an toàn <OTP>
    otp_pattern = r"(?:mã\s*(?:otp|xác\s*thực)?|otp\s*(?:code|is|là)?\s*[:\s]*)([0-9]{4,8})\b"
    text = re.sub(otp_pattern, " <OTP> ", text)

    # Thay thế chuỗi số tài khoản / thẻ ngân hàng (10-19 chữ số) thành <CARD_NUMBER>
    card_pattern = r"\b\d{10,19}\b"
    text = re.sub(card_pattern, " <CARD_NUMBER> ", text)

    # Loại bỏ ký tự lạ, giữ lại chữ cái, số và dấu câu cơ bản
    text = re.sub(r"[^\w\s<>]", " ", text)

    # Loại bỏ khoảng trắng thừa
    text = re.sub(r"\s+", " ", text).strip()

    return text

def extract_sms_heuristic_signals(text: str) -> dict:
    """
    Trích xuất các tín hiệu dấu hiệu nghi vấn dựa trên heuristic:
    - Có chứa URL
    - Có chứa số điện thoại
    - Có chứa từ khóa khẩn cấp / đe dọa / dụ dỗ
    - Tỷ lệ chữ hoa bất thường
    """
    signals = {
        "has_url": bool(re.search(r"https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text, re.IGNORECASE)),
        "has_phone": bool(re.search(r"(?:\+?84|0)(?:\d{9}|\d{10})\b", text)),
        "found_keywords": [],
        "urgency_score": 0.0
    }

    lower_text = text.lower()
    for kw in URGENCY_KEYWORDS:
        if kw in lower_text:
            signals["found_keywords"].append(kw)

    # Tính điểm khẩn cấp sơ bộ
    if signals["found_keywords"]:
        signals["urgency_score"] = min(1.0, len(signals["found_keywords"]) * 0.25)

    return signals
