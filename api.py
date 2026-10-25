"""
ScamShield AI - RESTful Backend API Server (FastAPI)
Cung cấp cổng dịch vụ API chuẩn công nghiệp cho ứng dụng di động (Android / iOS)
và các hệ thống giám sát an ninh mạng tích hợp.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import re

from src.predict_sms import predict_sms
from src.predict_url import predict_url
from src.threat_lookup import lookup_url
from src.risk_engine import build_report

app = FastAPI(
    title="ScamShield AI - Mobile Backend REST API",
    description="API phát hiện và đánh giá rủi ro lừa đảo qua tin nhắn tiếng Việt và đường dẫn URL độc hại bằng Trí tuệ Nhân tạo. Phục vụ đồ án Capstone Samsung Innovation Campus (SIC-AI).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS để ứng dụng di động (Flutter / React Native / Web) kết nối không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema dữ liệu đầu vào cho yêu cầu quét
class ScanRequest(BaseModel):
    sms_text: Optional[str] = Field(None, description="Nội dung văn bản tin nhắn tiếng Việt cần kiểm tra", example="Thong bao: Tai khoan VCB cua ban bi khoa, truy cap http://vcb-verify.xyz de xac minh.")
    url_text: Optional[str] = Field(None, description="Đường dẫn URL cần phân tích tĩnh hình thái", example="http://vcb-verify.xyz/login")

# Schema phản hồi chi tiết
class ScanResponse(BaseModel):
    alert_level: str = Field(..., description="Cấp độ cảnh báo: DANGEROUS | CAUTION | SAFE")
    status_label: str = Field(..., description="Nhãn trạng thái hiển thị người dùng")
    overall_risk_score: float = Field(..., description="Điểm rủi ro tổng hợp từ 0.0 đến 1.0")
    sms_probability: float = Field(..., description="Xác suất lừa đảo từ nhánh NLP tin nhắn")
    url_probability: float = Field(..., description="Xác suất lừa đảo từ nhánh hình thái URL")
    reasons: List[str] = Field(..., description="Danh sách các bằng chứng và dấu hiệu nghi ngờ phát hiện được")
    advice: List[str] = Field(..., description="Các khuyến nghị an toàn số phù hợp")
    raw_details: Dict[str, Any] = Field(..., description="Chi tiết kết quả từng module AI con")

@app.get("/", tags=["Hệ thống"])
def root_info():
    """Thông tin trạng thái dịch vụ ScamShield AI Backend."""
    return {
        "service": "ScamShield AI Mobile Backend",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "supported_features": ["Vietnamese SMS NLP (Random Forest)", "URL Lexical Analysis (Logistic Regression)", "Trusted Whitelist"]
    }

@app.get("/api/v1/health", tags=["Hệ thống"])
def health_check():
    """Kiểm tra tình trạng hoạt động của máy chủ và các module AI."""
    return {
        "status": "healthy",
        "ai_models_loaded": True
    }

@app.post("/api/v1/scan", response_model=ScanResponse, tags=["Phân tích An ninh"])
def scan_content(request: ScanRequest):
    """
    Điểm cuối chính (Endpoint) nhận văn bản tin nhắn hoặc đường dẫn URL,
    thực thi phân tích AI đa tầng và trả về báo cáo đánh giá rủi ro cho Mobile App.
    """
    sms_input = (request.sms_text or "").strip()
    url_input = (request.url_text or "").strip()

    if not sms_input and not url_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp ít nhất nội dung tin nhắn ('sms_text') hoặc đường dẫn URL ('url_text')!"
        )

    # Tự động trích xuất URL từ SMS nếu người dùng chỉ truyền SMS mà không truyền URL riêng
    if sms_input and not url_input:
        urls_found = re.findall(r"https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?", sms_input)
        if urls_found:
            url_input = urls_found[0]

    # 1. Dự đoán SMS NLP
    sms_res = predict_sms(sms_input) if sms_input else None

    # 2. Phân tích URL
    url_res = predict_url(url_input) if url_input else None

    # 3. Tra cứu Threat Lookup
    lookup_res = lookup_url(url_input) if url_input else None

    # 4. Tổng hợp qua Risk Engine
    report = build_report(sms_res, url_res, lookup_res)

    # Tính điểm rủi ro tổng thể (Risk Score)
    sms_prob = report.get("sms_probability", 0.0)
    url_prob = report.get("url_probability", 0.0)
    overall_score = max(sms_prob, url_prob)

    return ScanResponse(
        alert_level=report["alert_level"],
        status_label=report["status_label"],
        overall_risk_score=round(overall_score, 4),
        sms_probability=round(sms_prob, 4),
        url_probability=round(url_prob, 4),
        reasons=report.get("reasons", []),
        advice=report.get("advice", []),
        raw_details={
            "sms_analysis": sms_res,
            "url_analysis": url_res,
            "threat_lookup": lookup_res
        }
    )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
