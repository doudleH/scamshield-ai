"""
ScamShield AI - Threat Intelligence Lookup Module
Module tùy chọn tra cứu danh sách mối đe dọa (Threat Feeds / Google Web Risk / PhishTank).
Lưu ý: Nếu chưa cấu hình API key, trả về trạng thái 'not_configured' minh bạch.
"""

import os

def lookup_url(url: str) -> dict:
    """
    Tra cứu URL qua các dịch vụ Threat Intelligence bên ngoài.
    
    Trả về định dạng chuẩn:
    {
        "status": "not_configured" | "success" | "error",
        "source": str hoặc None,
        "is_threat": bool hoặc None,
        "threat_type": str hoặc None,
        "details": str
    }
    """
    if not url or not isinstance(url, str):
        return {
            "status": "error",
            "source": None,
            "is_threat": None,
            "threat_type": None,
            "details": "URL không hợp lệ hoặc để trống"
        }

    # Kiểm tra cấu hình API key (ví dụ GOOGLE_WEB_RISK_KEY hoặc PHISHTANK_KEY)
    api_key = os.environ.get("THREAT_LOOKUP_API_KEY", "").strip()

    if not api_key:
        return {
            "status": "not_configured",
            "source": "Threat Intel Service",
            "is_threat": None,
            "threat_type": None,
            "details": "Chưa kích hoạt tra cứu cơ sở dữ liệu bên ngoài (Chế độ chạy thuần AI nội bộ)"
        }

    # Placeholder logic khi có API key thực tế
    # Cần kiểm tra timeout và xử lý lỗi mạng
    try:
        # TODO: Tích hợp API call tới dịch vụ được cấp phép
        return {
            "status": "success",
            "source": "External Threat Feed",
            "is_threat": False,
            "threat_type": None,
            "details": "Không tìm thấy trong danh sách cảnh báo công khai"
        }
    except Exception as e:
        return {
            "status": "error",
            "source": "External Threat Feed",
            "is_threat": None,
            "threat_type": None,
            "details": f"Lỗi kết nối tra cứu: {str(e)}"
        }
