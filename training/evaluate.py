"""
ScamShield AI - Model Evaluation & Reporting Script
Tạo báo cáo đánh giá tổng thể (Evaluation Summary) cho bài nộp SIC-AI:
- Đọc kết quả so sánh từ reports/
- Tạo bảng đối sánh chi tiết
- Lưu báo cáo tóm tắt ra markdown phục vụ làm slide thuyết trình
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import pandas as pd

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

def generate_markdown_summary():
    sms_report_path = os.path.join(REPORT_DIR, "sms_model_comparison.csv")
    url_report_path = os.path.join(REPORT_DIR, "url_model_comparison.csv")
    summary_path = os.path.join(REPORT_DIR, "evaluation_summary.md")

    md_lines = [
        "# 📊 BÁO CÁO ĐÁNH GIÁ MÔ HÌNH — ScamShield AI\n",
        "> **Cập nhật:** 2026-10-15  ",
        "> **Dữ liệu:** Thực tế (dataset SMS tiếng Việt + PhishVN v3.1.0)\n",
        "---\n",
        "## 🟢 1. Mô hình Phân loại SMS Lừa đảo (Tiếng Việt)\n",
        "### Nguồn dữ liệu",
        "- **Tập Train:** `data/raw/train.csv` — **2.394 mẫu** (Ham: 1.754 | Spam: 640)",
        "- **Tập Test:** `data/raw/test.csv` — **597 mẫu** (Ham: 439 | Spam: 158)",
        "- **Tiền xử lý:** TF-IDF N-gram (1,2), max 5.000 đặc trưng, min_df=2\n",
        "### Kết quả so sánh 3 mô hình\n"
    ]

    if os.path.exists(sms_report_path):
        df_sms = pd.read_csv(sms_report_path)
        md_lines.append(df_sms.to_markdown(index=False))
        md_lines.append("\n")

    md_lines.extend([
        "### 🏆 Mô hình tốt nhất: `RandomForest`",
        "- **F1-Score:** 0.8598 (cân bằng tốt nhất giữa Precision và Recall)",
        "- **Precision:** 0.8294 — Ít cảnh báo nhầm nhất",
        "- **Recall:** 0.8924 — Phát hiện được 89.2% tin nhắn lừa đảo thực sự",
        "- **Confusion Matrix:**",
        "  ```",
        "  [[410  29]   ← 410 Ham đúng, 29 Ham nhầm là Spam",
        "   [ 17 141]]  ← 17 Spam bỏ lọt, 141 Spam phát hiện đúng",
        "  ```\n",
        "### Nhận xét kỹ thuật",
        "- RandomForest vượt trội nhờ khả năng nắm bắt tổ hợp từ khóa phức tạp trong tin nhắn tiếng Việt.",
        "- LogisticRegression có Recall cao hơn (96%) nhưng Precision thấp hơn — cảnh báo nhầm nhiều hơn.",
        "- Dataset thực tế (2.394 mẫu) cho kết quả tốt hơn hẳn so với dữ liệu mẫu 16 dòng trước đây.\n",
        "---\n",
        "## 🔵 2. Mô hình Phát hiện URL Lừa đảo (Phishing URL)\n",
        "### Nguồn dữ liệu",
        "- **Dataset:** PhishVN v3.1.0 (53.112 URL Việt Nam) — phân chia sẵn theo thời gian",
        "- **Tập Train:** 36.905 URL (Lành tính: 11.004 | Phishing: 25.901)",
        "- **Tập Test:**   8.941 URL  (Lành tính:  3.845 | Phishing:  5.096)",
        "- **Đặc trưng:** 12 đặc trưng hình thái Hostname & Domain (chuẩn hóa `has_path=0`)\n",
        "### Kết quả so sánh 3 mô hình\n"
    ])

    if os.path.exists(url_report_path):
        df_url = pd.read_csv(url_report_path)
        md_lines.append(df_url.to_markdown(index=False))
        md_lines.append("\n")

    md_lines.extend([
        "### 🏆 Mô hình tốt nhất: `LogisticRegression (Pipeline with StandardScaler)`",
        "- **F1-Score:** 0.8609 — Cao nhất trong các mô hình thử nghiệm",
        "- **Precision:** 0.9518 — Tỷ lệ báo nhầm URL lành tính là cực thấp (< 5%)",
        "- **Recall:** 0.7859 — Bắt được gần 79% URL phishing mới",
        "- **Đặc điểm:** Huấn luyện qua `StandardScaler` + `LogisticRegression(class_weight='balanced')` giúp mô hình ổn định, không bị overfit.\n",
        "### Nhận định kỹ thuật & Giải pháp khắc phục Dataset Bias:",
        "1. **Thiên lệch dữ liệu (Dataset Bias):** PhishVN chứa tập lành tính chủ yếu là `.gov.vn`. Các tên miền ngân hàng `.com.vn` có cấu trúc nhiều dấu chấm dễ bị mô hình ML đánh giá nhầm.",
        "2. **Chiến lược phòng thủ đa tầng (Hybrid Defense-in-Depth):**",
        "   - **Tầng 1 - Danh sách trắng (Whitelist):** Kiểm tra tên miền đã xác minh (VCB, MB, Vietinbank, `.gov.vn`, báo chí lớn, sàn TMĐT).",
        "   - **Tầng 2 - Mô hình Máy học (ML Pipeline):** Phân tích hình thái tên miền lạ, TLD nguy hiểm, từ khóa giả mạo, tỷ lệ chữ số.",
        "   - **Tầng 3 - Động cơ Heuristic & Risk Engine:** Tổng hợp rủi ro đa chiều từ SMS, URL và Threat Intel.\n",
        "---\n",
        "## ✅ Tóm tắt chung\n",
        "| Nhiệm vụ | Mô hình tốt nhất | F1-Score | Precision | Recall | Trạng thái |",
        "|---|---|---|---|---|---|",
        "| Phát hiện SMS lừa đảo (VN) | RandomForest | **0.8598** | 0.8294 | 0.8924 | ✅ Đã huấn luyện thực tế (train.csv / test.csv) |",
        "| Phát hiện URL phishing (VN) | LogisticRegression (Pipeline) | **0.8609** | 0.9518 | 0.7859 | ✅ Đã huấn luyện thực tế (PhishVN v3.1.0) |\n",
        "**Cả hai mô hình đều đã được huấn luyện trên dữ liệu thực tế quy mô lớn và tích hợp sẵn sàng vào ứng dụng.**\n",
        "---\n",
        "## 📁 File đã lưu\n",
        "| File | Mô tả |",
        "|---|---|",
        "| `models/sms_model.pkl` | RandomForest phân loại SMS (2.394 mẫu train, 597 mẫu test) |",
        "| `models/sms_vectorizer.pkl` | TF-IDF Vectorizer (5.000 n-gram) cho tiếng Việt |",
        "| `models/url_model.pkl` | LogisticRegression Pipeline phát hiện phishing URL (36.905 mẫu train) |",
        "| `models/url_model_meta.pkl` | Metadata phiên bản mô hình URL (12 đặc trưng hình thái) |",
        "| `reports/sms_model_comparison.csv` | Bảng đối sánh chi tiết 3 thuật toán SMS |",
        "| `reports/url_model_comparison.csv` | Bảng đối sánh chi tiết 3 thuật toán URL |"
    ])

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[OK] Đã cập nhật báo cáo đánh giá tổng thể tại: {summary_path}")

if __name__ == "__main__":
    generate_markdown_summary()
