"""
ScamShield AI - Risk Engine Module
Tổng hợp kết quả từ các nguồn tín hiệu:
- Dự đoán mô hình SMS
- Dự đoán mô hình URL
- Tra cứu dịch vụ Threat Intelligence bên ngoài
Nguyên tắc: Giữ nguyên tính minh bạch của từng nguồn tín hiệu, không tính trung bình giả tạo.
"""

from .explanations import generate_safety_advice

def build_report(sms_result: dict, url_result: dict, lookup_result: dict) -> dict:
    """
    Tổng hợp báo cáo đánh giá rủi ro từ các nguồn dữ liệu độc lập.
    
    Quy tắc phân loại mức cảnh báo:
    - DANGEROUS (Đỏ): Khi SMS hoặc URL bị mô hình AI đánh giá xác suất lừa đảo >= 0.7 
      HOẶC nguồn tra cứu bên ngoài xác nhận là mối đe dọa đã biết.
    - CAUTION (Vàng): Khi xác suất lừa đảo nằm trong khoảng [0.35, 0.7) 
      HOẶC có các tín hiệu nghi vấn (từ khóa đe dọa, đuôi tên miền rác).
    - SAFE (Xanh): Không phát hiện dấu hiệu bất thường nào.
    """
    reasons = []
    
    sms_prob = sms_result.get("scam_probability", 0.0) if sms_result else 0.0
    url_prob = url_result.get("phishing_probability", 0.0) if url_result else 0.0
    is_external_threat = lookup_result.get("is_threat") if lookup_result else None

    # Thu thập bằng chứng từ SMS
    if sms_result and sms_result.get("detected_signals"):
        found_kw = sms_result["detected_signals"].get("found_keywords", [])
        if found_kw:
            reasons.append(f"Văn bản chứa {len(found_kw)} cụm từ thường dùng để thao túng tâm lý: {', '.join(found_kw)}")
        if sms_result["detected_signals"].get("has_url"):
            reasons.append("Tin nhắn đính kèm liên kết ngoài (đặc điểm thường thấy của chiến dịch Phishing)")

    # Thu thập bằng chứng từ URL
    if url_result and url_result.get("suspicious_factors"):
        for factor in url_result["suspicious_factors"]:
            reasons.append(f"Đặc trưng URL: {factor}")

    # Thu thập bằng chứng từ Threat Lookup
    if lookup_result:
        status = lookup_result.get("status")
        if status == "success" and is_external_threat is True:
            reasons.append(f"Cơ sở dữ liệu {lookup_result.get('source')} xác nhận đây là liên kết độc hại đã được ghi nhận!")
        elif status == "not_configured":
            # Ghi nhận trạng thái rõ ràng, không giấu diếm
            pass

    # Quyết định mức cảnh báo tổng thể
    if is_external_threat is True or sms_prob >= 0.7 or url_prob >= 0.7:
        alert_level = "DANGEROUS"
        status_label = "CẢNH BÁO NGUY HIỂM / LỪA ĐẢO"
        color_badge = "red"
    elif sms_prob >= 0.35 or url_prob >= 0.35 or len(reasons) > 0:
        alert_level = "CAUTION"
        status_label = "CẦN CẨN TRỌNG / CÓ DẤU HIỆU NGHI VẤN"
        color_badge = "orange"
    else:
        alert_level = "SAFE"
        status_label = "AN TOÀN THEO CÁC TIÊU CHÍ ĐÃ KIỂM TRA"
        color_badge = "green"

    advice = generate_safety_advice(alert_level)

    # Giới hạn kỹ thuật cần thông báo cho người dùng
    limitations = [
        "Mô hình học máy dự đoán dựa trên các đặc trưng cấu trúc và ngữ nghĩa thống kê, có thể có tỷ lệ báo sai (False Positive) hoặc bỏ sót (False Negative).",
        "Trạng thái 'An toàn' chỉ có nghĩa là chưa phát hiện dấu hiệu bất thường, không đồng nghĩa với cam kết an toàn tuyệt đối.",
        "Hệ thống không tự truy cập vào website đích để bảo vệ an toàn cho máy chủ và người dùng."
    ]

    report = {
        "alert_level": alert_level,
        "status_label": status_label,
        "color_badge": color_badge,
        "sms_probability": sms_prob,
        "url_probability": url_prob,
        "external_threat": is_external_threat,
        "reasons": reasons,
        "advice": advice,
        "limitations": limitations
    }

    return report
