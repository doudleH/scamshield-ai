# 🛡️ ScamShield AI

[![ScamShield AI - CI Pipeline](https://github.com/doudleH/scamshield-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/doudleH/scamshield-ai/actions/workflows/ci.yml)

> **Hệ thống phát hiện và đánh giá rủi ro lừa đảo qua tin nhắn và đường link bằng AI**  
> *Đồ án tốt nghiệp môn AI (Capstone Project) — Chương trình Samsung Innovation Campus (SIC)*  
> **Hạn nộp & Báo cáo:** Thứ Sáu, ngày 30/10/2026  
> **Nền tảng mục tiêu:** Android Native (Kotlin) & Python Backend / Web Dashboard  

* 📋 **Tài liệu bàn giao nhiệm vụ nhóm:** [DANH_SACH_NHIEM_VU_DU_AN.md](DANH_SACH_NHIEM_VU_DU_AN.md)
* 📖 **Báo cáo tổng hợp kiến thức 11 chương:** [BAO_CAO_TONG_HOP_KIEN_THUC.md](BAO_CAO_TONG_HOP_KIEN_THUC.md)
* 📱 **Tài liệu kiến trúc Android & Bảo mật:** [mobile/README_MOBILE_ARCHITECTURE.md](mobile/README_MOBILE_ARCHITECTURE.md)

---

## 📌 1. Giới Thiệu Đề Tài

Lừa đảo trực tuyến qua tin nhắn mạo danh (SMS Brandname) và các đường link phishing (giả mạo ngân hàng, cơ quan công an, tuyển dụng việc làm ảo) đang là vấn đề nhức nhối tại Việt Nam.

**ScamShield AI** là giải pháp hỗ trợ người dùng phân tích độ rủi ro của tin nhắn và đường link trước khi tương tác. Hệ thống kết hợp:
1. **Mô hình NLP Tiếng Việt:** Phân tích ngữ nghĩa, phát hiện các thủ thuật thao túng tâm lý khẩn cấp (*TF-IDF N-gram + Random Forest, F1 = 0.8598*).
2. **Mô hình Phân tích Hình thái & Cấu trúc URL:** Phân tích 12 đặc trưng hình thái Hostname kết hợp cơ chế Whitelist tên miền uy tín (*StandardScaler + Logistic Regression Pipeline, F1 = 0.8609*).
3. **Ứng dụng Di động Android Native (Kotlin):** Tự động phát hiện tin nhắn SMS thời gian thực, động cơ On-Device Heuristic Engine nhận diện 4 thủ đoạn lách luật (CamelCase, tên miền trong ngoặc, ngụy trang GOOGLE.COM, giả mạo ngân hàng), bảo vệ tuyệt đối mã OTP cá nhân (Nghị định 13/2023/NĐ-CP).
4. **Bộ tổng hợp minh bạch (Risk Engine) & Backend API:** Tách bạch nguồn tín hiệu, giải thích rõ nguyên nhân rủi ro qua FastAPI và Streamlit Web App.

---

## 🧠 2. Đối Chiếu Giáo Trình 11 Chương Samsung Innovation Campus

| Chương SIC-AI | Nội dung áp dụng vào ScamShield AI |
| :--- | :--- |
| **Chương 1 (Intro to AI)** | Đạo đức AI, bảo vệ quyền riêng tư người dùng theo luật dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP), bảo vệ OTP. |
| **Chương 2 (Math for AI)** | Không gian vector đặc trưng, hàm kích hoạt Sigmoid ánh xạ xác suất rủi ro. |
| **Chương 3 (EDA)** | Tiền xử lý văn bản tiếng Việt, trích xuất đặc trưng hình thái URL, xử lý mất cân bằng dữ liệu (`class_weight='balanced'`). |
| **Chương 4 (Thống kê)** | Phân phối tần suất từ khóa khẩn cấp, Định lý Bayes trong phân loại văn bản (MultinomialNB baseline). |
| **Chương 5 (Machine Learning 1)** | Mô hình phân loại có giám sát: Logistic Regression, Decision Tree, Naive Bayes. Đánh giá đa chiều qua Confusion Matrix, Precision, Recall, F1. |
| **Chương 6 (Machine Learning 2)** | Thuật toán Ensemble **Random Forest** nâng cao độ chính xác phân loại SMS tiếng Việt (Recall 89.24%, F1 0.8598). |
| **Chương 7 (NLP & Text Mining)** | Chu trình NLP tiếng Việt: Chuẩn hóa Unicode NFC, Regex tokenization, N-grams (1, 2), trích xuất vector **TF-IDF**. |
| **Chương 10 (AI Integration & XAI)** | Trí tuệ Nhân tạo có thể giải thích (Explainable AI): Liệt kê minh bạch bằng chứng phát hiện, cảnh báo người dùng. |
| **Chương 11 (Starting AI Project)** | Vòng đời dự án chuẩn **CRISP-DM**, triển khai RESTful API (FastAPI) và ứng dụng di động Android Native. |

---

## 📂 3. Cấu Trúc Mã Nguồn

```text
scamshield-ai/
├── app.py                         # Ứng dụng Web giao diện Streamlit
├── api.py                         # Backend RESTful API (FastAPI + Swagger UI)
├── requirements.txt               # Danh sách thư viện phụ thuộc
├── README.md                      # Tài liệu tổng quan dự án
├── DANH_SACH_NHIEM_VU_DU_AN.md    # Bảng phân chia công việc & bàn giao nhóm
├── BAO_CAO_TONG_HOP_KIEN_THUC.md  # Báo cáo học thuật 11 chương SIC-AI
├── .gitignore                     # Cấu hình bỏ qua các file lớn/cache/Android build
├── mobile/                        # Ứng dụng di động Android Native
│   ├── README_MOBILE_ARCHITECTURE.md # Tài liệu kiến trúc Android & Privacy
│   └── android/                   # Dự án Android Studio (Mở thư mục này)
│       ├── app/src/main/java/com/samsung/sic/scamshield/
│       │   ├── MainActivity.kt        # Màn hình chính, quyền & Sandbox
│       │   ├── SmsReceiver.kt         # On-Device Heuristic & Fast-Bypass OTP
│       │   └── NotificationHelper.kt  # Heads-up Notification cảnh báo đỏ
│       └── app/src/main/res/          # Giao diện XML & Resources
├── src/                           # Thư mục mã nguồn xử lý chính
│   ├── text_preprocessing.py      # Tiền xử lý, chuẩn hóa NFC & Masking OTP
│   ├── url_features.py            # Trích xuất 12 đặc trưng URL (No-HTTP / An toàn)
│   ├── predict_sms.py             # Module dự đoán rủi ro tin nhắn
│   ├── predict_url.py             # Module dự đoán rủi ro đường link
│   ├── threat_lookup.py           # Module tùy chọn tra cứu Threat Intel ngoài
│   ├── risk_engine.py             # Bộ tổng hợp báo cáo và bằng chứng
│   └── explanations.py            # Module sinh lời khuyên an toàn theo luật
├── training/                      # Kịch bản huấn luyện mô hình
│   ├── train_sms.py               # Huấn luyện mô hình SMS
│   ├── train_url.py               # Huấn luyện mô hình URL
│   └── evaluate.py                # Đánh giá và xuất báo cáo so sánh
├── models/                        # Thư mục lưu trữ model đã train (.pkl)
├── reports/                       # Báo cáo so sánh mô hình và số liệu đánh giá
└── tests/                         # Kiểm thử tích hợp và hợp đồng dữ liệu
```

---

## 📊 4. Dữ Liệu Thực Nghiệm & Kết Quả Đánh Giá

### Nguồn dữ liệu sử dụng:
1. **SMS Tiếng Việt:** Tập dữ liệu SMS tiếng Việt từ Hugging Face (`trannguyenthaituan/vietnamese_sms_dataset`) gồm 2.394 mẫu huấn luyện và 597 mẫu kiểm thử độc lập.
2. **URL Phishing Việt Nam:** Bộ dữ liệu `PhishVN v3.1.0` từ Mendeley Data (53.112 URL thực tế tại Việt Nam) phân chia theo thời gian (36.905 Train / 8.941 Test).

### Kết quả mô hình tối ưu đã lưu trong `models/`:
- **Phát hiện SMS lừa đảo:** `RandomForest` — **F1-Score: 0.8598** (Recall: 89.24%, Precision: 82.94%).
- **Phát hiện URL Phishing:** `LogisticRegression (Pipeline)` — **F1-Score: 0.8609** (Precision: 95.18%, Recall: 78.59%).
*(Xem chi tiết tại [`reports/evaluation_summary.md`](reports/evaluation_summary.md))*

---

## 🚀 5. Hướng Dẫn Cài Đặt & Chạy Thử

### Bước 1: Môi trường & Cài đặt thư viện
```bash
cd scamshield-ai
pip install -r requirements.txt
```

### Bước 2: Chạy kiểm thử tự động (Unit Tests & Smoke Tests)
```bash
# Kiểm thử hợp đồng dữ liệu giữa các module
python tests/test_pipeline.py

# Kiểm thử kịch bản thực tế đầu-cuối (End-to-End Smoke Test)
python smoke_test.py
```

### Bước 3: Huấn luyện lại mô hình (Tùy chọn khi có dữ liệu mới)
```bash
# Huấn luyện mô hình SMS
python training/train_sms.py

# Huấn luyện mô hình URL
python training/train_url.py

# Xuất báo cáo tổng kết
python training/evaluate.py
```

### Bước 4: Khởi chạy ứng dụng Web Streamlit
```bash
streamlit run app.py
```

---

## 🔒 6. Tiêu Chuẩn Bảo Mật (OWASP Compliant)
- **Chống SSRF:** Hệ thống tuyệt đối KHÔNG thực hiện kết nối HTTP tới các URL do người dùng nhập.
- **Bảo vệ PII:** Khuyến cáo người dùng không nhập mật khẩu, mã OTP và thông tin định danh cá nhân.
- **Chống rò rỉ API Key:** Mọi cấu hình bên ngoài đều sử dụng biến môi trường hoặc Streamlit Secrets.
- **Kênh tiếp nhận chính thức tại Việt Nam:** Hotline 156 / 5656 và [tracuutenmien.gov.vn](https://tracuutenmien.gov.vn).

---

## 🔌 7. Module 2 — Backend & MLOps (nhánh `feature/backend-api`)

Mục tiêu: app Android kết nối được backend qua Internet thật và hình thành vòng lặp dữ liệu (Active Learning).

### 7.1 Endpoint

| Method | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `POST` | `/api/v1/scan` | Phân tích tổng hợp SMS + URL, trả điểm rủi ro và bằng chứng |
| `POST` | `/api/v1/report` | Nhận phản ánh lừa đảo, **che PII tự động** (SĐT / OTP / STK / email), ghi nối tiếp vào `data/reported_samples.jsonl` |
| `GET` | `/api/v1/rules/sync` | Trả bộ luật offline (domain + keyword) từ `config/scam_rules.json`, hỗ trợ `ETag` / `304 Not Modified` |
| `GET` | `/api/v1/health` | Healthcheck cho nền tảng cloud |

- Dữ liệu huấn luyện liên tục: `data/reported_samples.jsonl` (append-only JSONL, mỗi dòng 1 mẫu `pending_review`).
- Cập nhật luật nhận diện offline: chỉ cần sửa `config/scam_rules.json` + tăng `version`, app tự tải bản mới qua `If-None-Match`.

### 7.2 Triển khai cloud (Render / Railway / Hugging Face Spaces)

```bash
docker build -t scamshield-api .
docker run -p 8000:8000 -v ${PWD}/data:/app/data scamshield-api
```

- **Render:** tạo Blueprint từ `render.yaml` (repo đã có) → tự build Dockerfile, healthcheck `/api/v1/health`.
- **Railway / HF Spaces:** trỏ vào repo, nền tảng tự nhận `Dockerfile`; app đọc cổng từ biến môi trường `PORT`.
- **Lưu trữ bền vững:** thư mục `/app/data` nên mount volume (Render Disk) để phản ánh cộng đồng không mất khi redeploy; nếu không, dữ liệu chỉ nằm trong vòng đời container.

### 7.3 Kiểm thử

```bash
python tests/test_module2.py   # hợp đồng Module 2: masking PII, append JSONL, ETag 304, healthcheck
```
