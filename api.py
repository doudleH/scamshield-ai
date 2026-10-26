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
import os
import json
from datetime import datetime

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

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    sms_text: Optional[str] = Field(None, description="Nội dung văn bản tin nhắn tiếng Việt cần kiểm tra", example="Thong bao: Tai khoan cua ban bi khoa, truy cap lien ket de xac minh.")
    url_text: Optional[str] = Field(None, description="Đường dẫn URL cần phân tích tĩnh hình thái", example="http://verify-account.xyz/login")

class ScanResponse(BaseModel):
    alert_level: str = Field(..., description="Cấp độ cảnh báo: DANGEROUS | CAUTION | SAFE")
    status_label: str = Field(..., description="Nhãn trạng thái hiển thị người dùng")
    overall_risk_score: float = Field(..., description="Điểm rủi ro tổng hợp từ 0.0 đến 1.0")
    sms_probability: float = Field(..., description="Xác suất rủi ro từ nhánh tin nhắn")
    url_probability: float = Field(..., description="Xác suất rủi ro từ nhánh đường dẫn")
    reasons: List[str] = Field(..., description="Danh sách các bằng chứng và dấu hiệu nghi ngờ phát hiện được")
    advice: List[str] = Field(..., description="Các khuyến nghị an toàn phù hợp")
    raw_details: Dict[str, Any] = Field(..., description="Chi tiết kết quả các thành phần phân tích")

@app.get("/", tags=["Hệ thống"])
def root_info():
    return {
        "service": "ScamShield Mobile Backend",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "supported_features": ["Vietnamese SMS NLP", "URL Lexical Analysis", "Trusted Whitelist"]
    }

@app.get("/api/v1/health", tags=["Hệ thống"])
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/api/v1/scan", response_model=ScanResponse, tags=["Phân tích An ninh"])
def scan_content(request: ScanRequest):
    """
    Điểm cuối tiếp nhận văn bản tin nhắn hoặc đường dẫn URL,
    thực thi phân tích đa tầng và trả về báo cáo đánh giá rủi ro cho Mobile App.
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

class ReportRequest(BaseModel):
    sender: Optional[str] = Field("Unknown", description="Số điện thoại hoặc brandname người gửi")
    message: str = Field(..., description="Nội dung tin nhắn lừa đảo phản ánh")
    risk_percent: Optional[int] = Field(0, description="Điểm phần trăm rủi ro đánh giá trên thiết bị")
    reason: Optional[str] = Field("", description="Lý do hoặc dấu hiệu phát hiện")

@app.post("/api/v1/report", tags=["Phản ánh Cộng đồng"])
def report_scam(report_data: ReportRequest):
    """
    Tiếp nhận phản ánh tin nhắn từ người dùng di động (Android Client),
    thực hiện ẩn danh hóa thông tin cá nhân (PII Masking) và lưu trữ.
    """
    os.makedirs("data", exist_ok=True)
    report_file = os.path.join("data", "reported_samples.json")

    raw_sender = (report_data.sender or "Unknown").strip()
    digits_only = re.sub(r"\D", "", raw_sender)
    if len(digits_only) >= 9:
        masked_sender = digits_only[:3] + "****" + digits_only[-3:]
    else:
        masked_sender = raw_sender

    entry = {
        "timestamp": datetime.now().isoformat(),
        "masked_sender": masked_sender,
        "message": report_data.message,
        "risk_percent": report_data.risk_percent,
        "reason": report_data.reason,
        "status": "pending_review"
    }

    samples = []
    if os.path.exists(report_file):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                samples = json.load(f)
        except Exception:
            samples = []

    samples.append(entry)
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    return {
        "status": "success",
        "message": "Đã tiếp nhận phản ánh thành công. Cảm ơn bạn đã đóng góp bảo vệ cộng đồng!",
        "reported_id": len(samples)
    }

@app.get("/api/v1/rules/sync", tags=["Đồng bộ Cảnh báo"])
def sync_rules():
    """
    Cung cấp danh sách tên miền độc hại mới nổi và các mẫu từ khóa lừa đảo
    để ứng dụng di động cập nhật ngoại tuyến.
    """
    return {
        "version": "2026.10.26",
        "new_emerging_malicious_domains": [
            "bidvzj.com", "bidvzf.com", "vcb-verify.xyz", "vietcombank-sms.top",
            "mbbank-online.club", "techcombank-chotdon.site", "cuc-thue-hoanthue.cc"
        ],
        "new_scam_keywords": [
            "traophucloi", "dangkinhan", "nhan88k", "nohu", "gamebai", "phatnguoi"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
