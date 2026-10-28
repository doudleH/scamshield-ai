"""
ScamShield AI - PII Masking Module
Che giau thong tin ca nhan (Nghi dinh 13/2023/ND-CP) truoc khi luu tru / gui may chu.
"""

import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_OTP = re.compile(r"(?i)((?:mã|ma|otp|code|mã xác thực)[^\d\n]{0,15})(\d{4,8})(?!\d)")
_PHONE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[ .-]?\d){9,10}(?!\d)")
_CARD = re.compile(r"(?<!\d)\d{10,19}(?!\d)")


def mask_pii(text: str) -> str:
    """Thay email / OTP / so dien thoai / so tai khoan bang token an toan."""
    if not isinstance(text, str):
        return ""
    out = _EMAIL.sub("[EMAIL]", text)
    out = _OTP.sub(r"\1[OTP]", out)
    out = _PHONE.sub("[SĐT]", out)
    out = _CARD.sub("[SỐ_TÀI_KHOẢN]", out)
    return out


def mask_sender(sender: str) -> str:
    """Che so dien thoai nguoi gui, giu brandname nguyen ven."""
    raw = (sender or "Unknown").strip()
    digits = re.sub(r"\D", "", raw)
    if len(digits) >= 9:
        return f"{digits[:3]}****{digits[-3:]}"
    return raw[:64]
