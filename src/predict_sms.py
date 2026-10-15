"""
ScamShield AI - SMS Prediction Module
Dự đoán rủi ro tin nhắn SMS bằng mô hình học máy NLP (TF-IDF + Classifier).
Hỗ trợ cơ chế dự phòng Heuristic thông minh nếu mô hình chưa được huấn luyện xong.
"""

import os
from .text_preprocessing import clean_vietnamese_text, extract_sms_heuristic_signals

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
SMS_MODEL_PATH = os.path.join(MODEL_DIR, "sms_model.pkl")
SMS_VEC_PATH = os.path.join(MODEL_DIR, "sms_vectorizer.pkl")

def predict_sms(text: str, language: str = "vi") -> dict:
    """
    Phân tích và dự đoán độ rủi ro của tin nhắn SMS.
    
    Định dạng trả về:
    {
        "is_scam": bool,
        "scam_probability": float (0.0 - 1.0),
        "confidence_level": str ("Cao", "Trung bình", "Thấp"),
        "model_type": str ("ML_LogisticRegression" | "heuristic_fallback"),
        "detected_signals": dict
    }
    """
    if not text or not isinstance(text, str):
        return {
            "is_scam": False,
            "scam_probability": 0.0,
            "confidence_level": "Thấp",
            "model_type": "none",
            "detected_signals": {}
        }

    # Bóc tách các tín hiệu ngữ nghĩa
    cleaned = clean_vietnamese_text(text)
    signals = extract_sms_heuristic_signals(text)

    # Kiểm tra xem mô hình ML đã được lưu chưa
    if os.path.exists(SMS_MODEL_PATH) and os.path.exists(SMS_VEC_PATH):
        try:
            import joblib
            model = joblib.load(SMS_MODEL_PATH)
            vectorizer = joblib.load(SMS_VEC_PATH)
            
            vec = vectorizer.transform([cleaned])
            prob = float(model.predict_proba(vec)[0][1])  # Xác suất lớp 1 (Lừa đảo)

            # Hiệu chỉnh xác suất kết hợp tín hiệu ngữ cảnh (URL + từ khóa áp lực tâm lý)
            if 0.35 <= prob <= 0.65:
                if signals.get("has_url") and len(signals.get("found_keywords", [])) >= 2:
                    prob = min(0.95, prob + 0.15)
                elif signals.get("has_url") and len(signals.get("found_keywords", [])) >= 1:
                    prob = min(0.90, prob + 0.08)

            is_scam = prob >= 0.5
            conf = "Cao" if prob >= 0.8 or prob <= 0.2 else "Trung bình"

            return {
                "is_scam": is_scam,
                "scam_probability": round(prob, 4),
                "confidence_level": conf,
                "model_type": "ML_Trained_Model",
                "detected_signals": signals
            }
        except Exception as e:
            # Gặp lỗi khi load model, chuyển về fallback
            pass

    # Chế độ dự phòng Heuristic (Baseline) nếu chưa có file model
    prob = signals["urgency_score"]
    if signals["has_url"] and len(signals["found_keywords"]) > 0:
        prob = min(1.0, prob + 0.35)

    is_scam = prob >= 0.5
    conf = "Trung bình" if len(signals["found_keywords"]) > 0 else "Thấp"

    return {
        "is_scam": is_scam,
        "scam_probability": round(prob, 4),
        "confidence_level": conf,
        "model_type": "Heuristic_Baseline",
        "detected_signals": signals
    }
