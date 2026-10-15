"""
ScamShield AI - Explanations & Advice Module
Cung cấp giải thích nguyên nhân rủi ro dễ hiểu và khuyến nghị an toàn số theo hướng dẫn chính thức.
"""

def generate_safety_advice(risk_level: str) -> list:
    """
    Tạo danh sách các khuyến nghị an toàn cho người dùng theo mức cảnh báo.
    """
    if risk_level == "DANGEROUS":
        return [
            "🚨 TUYỆT ĐỐI KHÔNG nhấp vào bất kỳ đường link nào trong tin nhắn.",
            "🔒 KHÔNG cung cấp mật khẩu ngân hàng, mã OTP, mã PIN hay số thẻ tín dụng cho bất kỳ ai.",
            "📞 Gọi trực tiếp đến hotline tổng đài chính thức của ngân hàng/đơn vị để xác thực lại thông tin.",
            "📢 Chuyển tiếp tin nhắn lừa đảo tới đầu số 156 hoặc 5656 (Tổng đài tiếp nhận phản ánh tin nhắn rác, lừa đảo của Bộ TT&TT - Miễn phí).",
            "🔍 Tra cứu chủ thể tên miền tại website chính thức của Trung tâm Internet Việt Nam: https://tracuutenmien.gov.vn"
        ]
    elif risk_level == "CAUTION":
        return [
            "⚠️ Hãy cẩn trọng kiểm tra kỹ thông tin người gửi trước khi tương tác.",
            "🔍 Không vội vàng làm theo các yêu cầu khẩn cấp (như chuyển tiền, xác minh tài khoản trong thời gian ngắn).",
            "🌐 Nếu tin nhắn chứa link, hãy tự mở trình duyệt và gõ địa chỉ trang chủ chính thức thay vì click trực tiếp."
        ]
    else:
        return [
            "✅ Không phát hiện dấu hiệu lừa đảo rõ ràng theo các tiêu chí đã kiểm tra.",
            "🛡️ Lưu ý: Không có công cụ nào phát hiện được 100% mối đe dọa. Vẫn luôn giữ cảnh giác khi giao dịch trực tuyến."
        ]
