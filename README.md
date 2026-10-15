# 🛡️ ScamShield AI

> **Hệ thống phát hiện và đánh giá rủi ro lừa đảo qua tin nhắn và đường link bằng AI**  
> *Đồ án tốt nghiệp môn AI (Capstone Project) — Chương trình Samsung Innovation Campus (SIC)*  
> **Hạn nộp & Báo cáo:** Thứ Tư, ngày 21/10/2026

---

## 📌 1. Giới Thiệu Đề Tài

Lừa đảo trực tuyến qua tin nhắn mạo danh (SMS Brandname) và các đường link phishing (giả mạo ngân hàng, cơ quan công an, tuyển dụng việc làm ảo) đang là vấn đề nhức nhối tại Việt Nam.

**ScamShield AI** là giải pháp hỗ trợ người dùng phân tích độ rủi ro của tin nhắn và đường link trước khi tương tác. Hệ thống kết hợp:
1. **Mô hình NLP Tiếng Việt:** Phân tích ngữ nghĩa, phát hiện các thủ thuật thao túng tâm lý khẩn cấp (*TF-IDF + Classifier*).
2. **Mô hình Thị giác & Cấu trúc URL:** Phân tích 16 đặc trưng hình thái của đường link (*Random Forest*).
3. **Bộ tổng hợp minh bạch (Risk Engine):** Tách bạch nguồn tín hiệu, giải thích rõ nguyên nhân rủi ro và đưa ra khuyến nghị an toàn số.

---

## 🧠 2. Đối Chiếu Giáo Trình 11 Chương Samsung Innovation Campus

| Chương SIC-AI | Nội dung áp dụng vào ScamShield AI |
| :--- | :--- |
| **Chương 1 (Intro to AI)** | Đạo đức AI, bảo vệ quyền riêng tư người dùng theo luật dữ liệu cá nhân. |
| **Chương 2 (Math for AI)** | Không gian vector đặc trưng, hàm kích hoạt Sigmoid/Softmax. |
| **Chương 3 (EDA)** | Tiền xử lý văn bản tiếng Việt, trích xuất đặc trưng URL, xử lý mất cân bằng dữ liệu. |
| **Chương 4 (Thống kê)** | Phân phối tần suất từ khóa, Định lý Bayes trong phân loại văn bản. |
| **Chương 5 (Machine Learning 1)** | Mô hình phân loại có giám sát: MultinomialNB, Logistic Regression, Decision Tree, SVM. Đánh giá đa chiều qua Confusion Matrix, Precision, Recall, F1. |
| **Chương 6 (Machine Learning 2)** | Thuật toán Ensemble **Random Forest** nâng cao độ chính xác phân loại URL. |
| **Chương 7 (NLP & Text Mining)** | Chu trình NLP: Tách từ tiếng Việt, loại bỏ stopwords, N-grams, trích xuất vector **TF-IDF**. |
| **Chương 11 (Starting AI Project)** | Vòng đời dự án chuẩn **CRISP-DM**, đóng gói thành Web Demo tương tác bằng Streamlit. |

---

## 📂 3. Cấu Trúc Mã Nguồn

```text
scamshield-ai/
├── app.py                      # Ứng dụng Web giao diện Streamlit
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── README.md                   # Tài liệu hướng dẫn dự án
├── .gitignore                  # Cấu hình bỏ qua các file lớn/nhạy cảm
├── src/                        # Thư mục mã nguồn xử lý chính
│   ├── text_preprocessing.py   # Tiền xử lý và bóc tách tín hiệu văn bản
│   ├── url_features.py         # Trích xuất 16 đặc trưng URL (No-HTTP / An toàn)
│   ├── predict_sms.py          # Module dự đoán rủi ro tin nhắn
│   ├── predict_url.py          # Module dự đoán rủi ro đường link
│   ├── threat_lookup.py        # Module tùy chọn tra cứu Threat Intel ngoài
│   ├── risk_engine.py          # Bộ tổng hợp báo cáo và bằng chứng
│   └── explanations.py         # Module sinh lời khuyên an toàn theo luật
├── training/                   # Kịch bản huấn luyện mô hình
│   ├── train_sms.py            # Huấn luyện mô hình SMS
│   ├── train_url.py            # Huấn luyện mô hình URL
│   └── evaluate.py             # Đánh giá và xuất báo cáo so sánh
├── models/                     # Thư mục lưu trữ model đã train (.pkl)
├── reports/                    # Báo cáo so sánh mô hình và số liệu đánh giá
└── tests/                      # Kiểm thử tích hợp và hợp đồng dữ liệu
```

---

## 🚀 4. Hướng Dẫn Cài Đặt & Chạy Thử

### Bước 1: Môi trường & Cài đặt thư viện
```bash
cd d:\SIC_AI\scamshield-ai
pip install -r requirements.txt
```

### Bước 2: Chạy kiểm thử hệ thống
```bash
python tests/test_pipeline.py
```

### Bước 3: Huấn luyện mô hình
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

## 🔒 5. Tiêu Chuẩn Bảo Mật (OWASP Compliant)
- **Chống SSRF:** Hệ thống tuyệt đối KHÔNG thực hiện kết nối HTTP tới các URL do người dùng nhập.
- **Bảo vệ PII:** Khuyến cáo người dùng không nhập mật khẩu, mã OTP và thông tin định danh cá nhân.
- **Chống rò rỉ API Key:** Mọi cấu hình bên ngoài đều sử dụng biến môi trường hoặc Streamlit Secrets.
- **Kênh tiếp nhận chính thức tại Việt Nam:** Hotline 156 / 5656 và [tracuutenmien.gov.vn](https://tracuutenmien.gov.vn).
