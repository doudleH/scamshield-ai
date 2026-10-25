# BẢNG TỔNG KẾT DỰ ÁN & HẠNG MỤC CÔNG VIỆC PHÁT TRIỂN
**Dự án:** ScamShield AI – Hệ thống Giám sát & Phát hiện Tin nhắn, Đường dẫn Lừa đảo Đa tầng
**Chương trình:** Samsung Innovation Campus (SIC-AI) Capstone Project
**Thời hạn báo cáo:** 30/10/2026
**Nền tảng mục tiêu:** Android Native (Kotlin) & Python Backend / Dashboard (Theo chỉ đạo: Hủy bỏ hoàn toàn iOS, tập trung 100% Android)

---

## I. TỔNG QUAN HIỆN TRẠNG DỰ ÁN (NHỮNG GÌ ĐÃ HOÀN THIỆN)

Dự án hiện đã hoàn thành khung kiến trúc cốt lõi từ Mô hình Trí tuệ Nhân tạo, Backend API, Web Dashboard đến Ứng dụng di động Android Native. Cụ thể:

### 1. Phân hệ Mô hình Trí tuệ Nhân tạo & Xử lý Dữ liệu (AI / ML Engine)
* **Mô hình Phân loại SMS (`models/sms_model.pkl`):**
  * Thuật toán: Random Forest Classifier (100 cây quyết định).
  * Trích xuất đặc trưng: TF-IDF (1,2)-grams với 5.000 đặc trưng từ khóa tiếng Việt.
  * Hiệu năng: Đạt F1-Score 0.8598, Recall 89.24% (đảm bảo hạn chế tối đa việc bỏ sót tin nhắn độc hại).
* **Mô hình Nhận diện URL Độc hại (`models/url_model.pkl`):**
  * Thuật toán: Logistic Regression kết hợp chuẩn hóa dữ liệu StandardScaler.
  * Dữ liệu huấn luyện: Hơn 53.000 URL từ bộ dữ liệu PhishVN v3.1.0.
  * Đặc trưng: 12 đặc trưng hình thái Hostname (chiều dài, số dấu chấm, dấu gạch ngang, tỷ lệ số/chữ, TLD rủi ro cao, entropy chuỗi ký tự...).
  * Hiệu năng: Đạt F1-Score 0.8609, Precision 95.18% (hạn chế tối đa cảnh báo nhầm đối với website an toàn).
* **Bộ lọc Danh sách Tin cậy (Trusted Whitelist):**
  * Tích hợp hơn 50 tên miền ngân hàng thương mại Việt Nam (Vietcombank, BIDV, Agribank, Techcombank, MBBank, ACB, TPBank...), các ví điện tử (MoMo, ZaloPay, VNPay, Viettel Money) và toàn bộ cổng dịch vụ công Chính phủ (`.gov.vn`).
* **Bảo vệ Quyền riêng tư Thiết bị (Privacy by Design - Nghị định 13/2023/NĐ-CP):**
  * Module tiền xử lý `src/text_preprocessing.py` thực hiện che giấu (redaction / masking) các thông tin nhạy cảm: mã OTP, mật khẩu dùng một lần, số thẻ ngân hàng, số CMND/CCCD ngay trên thiết bị trước khi xử lý, cam kết không lưu trữ hoặc gửi thông tin cá nhân lên máy chủ.

### 2. Phân hệ Máy chủ Dịch vụ (Backend RESTful API - `api.py`)
* Xây dựng trên nền tảng **FastAPI** tốc độ cao, hỗ trợ bất đồng bộ (Asynchronous).
* Đã cấu hình đầy đủ CORS Middleware phục vụ việc gọi API từ ứng dụng Android hoặc Web Client.
* Tự động sinh tài liệu kiểm thử tương tác Swagger UI tại địa chỉ `/docs`.
* **Endpoint chính:**
  * `POST /api/v1/scan`: Nhận diện phối hợp nội dung tin nhắn và đường dẫn (URL) trích xuất, trả về điểm số rủi ro tổng hợp (0 - 100), cấp độ cảnh báo (`SAFE`, `SUSPICIOUS`, `DANGEROUS`) và danh sách giải trình nguyên nhân.
  * `GET /api/v1/health`: Kiểm tra sức khỏe hệ thống và tình trạng nạp các mô hình AI.

### 3. Phân hệ Bảng điều khiển Trực quan (Web Dashboard - `app.py`)
* Xây dựng bằng **Streamlit**, phục vụ việc demo trực tiếp cho ban giám khảo và phân tích thử nghiệm:
  * Cho phép nhập tự do SMS hoặc URL để kiểm tra rủi ro tức thì.
  * Biểu đồ phân tích độ đóng góp của các từ khóa (Feature Importance / LIME giải thích quyết định của AI).
  * Chế độ kiểm tra hàng loạt và bảng điều khiển thống kê trực quan.

### 4. Ứng dụng Di động Android Native (`mobile/android/`)
* Cấu trúc chuẩn dự án Android Studio Gradle (Kotlin 1.9, Android Gradle Plugin 8.2, minSdk 24 - hỗ trợ từ Android 7.0 trở lên, compileSdk / targetSdk 34).
* **Động cơ Phân tích Ngoại tuyến trên Thiết bị (On-Device Heuristic Engine - `SmsReceiver.kt`):**
  * Khả năng hoạt động 100% độc lập, không cần kết nối Internet hoặc Server backend.
  * **Giải quyết 4 thủ đoạn lách bộ lọc viễn thông mới nhất:**
    * Nhận diện chuỗi viết hoa không dấu cách (CamelCase: `kFDangKiNhanPhanThuong`, `LannapThuong`, `100phantram`).
    * Trích xuất tên miền đặt trong dấu ngoặc đơn hoặc không có tiền tố http/https (ví dụ: `(sqlpy.bidvzj.com)`).
    * Bóc tách và cảnh báo thủ đoạn lừa đảo gắn đuôi tên miền uy tín làm mồi nhử (Decoy Evasion: `GOOGLE.COM` đi kèm link cờ bạc).
    * Nhận diện giả mạo thương hiệu ngân hàng (Brand Typosquatting: tên miền chứa từ khóa `bidv` nhưng không thuộc Whitelist ngân hàng chính thống).
* **Cơ chế Bỏ qua Tin cậy Tức thì (Fast-Bypass):**
  * Tự động nhận diện tin nhắn mã OTP từ đầu số Brandname chính thống để chuyển tiếp bình thường cho người dùng, tuyệt đối không chặn nhầm và không rò rỉ mã bảo mật.
* **Hệ thống Quản trị Quyền & Trải nghiệm Người dùng (`MainActivity.kt`):**
  * Quản lý quyền thời gian thực (`RECEIVE_SMS`, `READ_SMS`, `POST_NOTIFICATIONS`).
  * Công tắc Bật / Tắt chế độ bảo vệ một chạm (lưu cấu hình vào `SharedPreferences`).
  * Nút chuyển nhanh vào Cài đặt ứng dụng hệ thống để người dùng toàn quyền thu hồi hoặc cấp quyền.
  * Hộp cát kiểm thử nội bộ (In-app Test Sandbox): Cho phép dán bất kỳ tin nhắn SMS nào vào app để thử nghiệm phát hiện ngay trên máy thật mà không cần phát sinh chi phí gửi SMS qua nhà mạng.
* **Hệ thống Thông báo Khẩn cấp (`NotificationHelper.kt`):**
  * Đẩy thông báo khẩn cấp (Heads-up Notification) với âm thanh cảnh báo, độ rung và biểu tượng cảnh báo màu đỏ ngay khi phát hiện tin nhắn nguy hiểm.

### 5. Hồ sơ & Báo cáo Học thuật Đã có
* `BAO_CAO_TONG_HOP_KIEN_THUC.md`: Báo cáo 11 chương chi tiết, chuẩn mực theo toàn bộ giáo trình SIC-AI (từ Xử lý Dữ liệu, Mô hình Học máy, Tinh chỉnh Tham số, API Backend đến Đạo đức AI & Tuân thủ Luật pháp).
* `mobile/README_MOBILE_ARCHITECTURE.md`: Tài liệu kiến trúc chuyên sâu ứng dụng di động Android.

---

## II. DANH MỤC CÁC HẠNG MỤC CẦN PHÁT TRIỂN THÊM (CHIA THEO MODULE CÔNG VIỆC)

Các hạng mục dưới đây được chia theo từng Module độc lập, rõ ràng để các thành viên trong nhóm dễ dàng nhận việc, phối hợp triển khai và hoàn thành trước thời hạn 30/10/2026.

---

### MODULE 1: NÂNG CẤP TÍNH NĂNG ỨNG DỤNG ANDROID (ANDROID CLIENT)
* **Nhánh Git phụ trách:** `feature/android-app`
* *Mục tiêu: Hoàn thiện tính năng trải nghiệm người dùng, quét toàn diện thiết bị và chuẩn bị file APK đóng gói cuối cùng.*

* **Nhiệm vụ 1.1: Xây dựng tính năng "Quét Hộp thư Đến" (Scan SMS Inbox)**
  * Mô tả: Khi người dùng bấm nút "Quét hộp thư", ứng dụng sử dụng `contentResolver.query(Telephony.Sms.Inbox.CONTENT_URI, ...)` để quét toàn bộ các tin nhắn đã có sẵn trong điện thoại.
  * Kết quả hiển thị: Một hộp thoại (Dialog) hoặc màn hình danh sách liệt kê các tin nhắn trong quá khứ có chứa nội dung lừa đảo kèm lý do phát hiện.
* **Nhiệm vụ 1.2: Xây dựng màn hình "Lịch sử Cảnh báo" (Alert History / Threat Log)**
  * Mô tả: Mỗi khi `SmsReceiver` hoặc công cụ Quét phát hiện một tin nhắn lừa đảo, lưu bản ghi vào bộ nhớ cục bộ (sử dụng Room Database hoặc SharedPreferences) gồm: Số người gửi, Thời gian nhận, Nội dung vắn tắt, Mức độ rủi ro.
  * Giao diện: Hiển thị danh sách các cảnh báo gần nhất để người dùng xem lại bất cứ lúc nào.
* **Nhiệm vụ 1.3: Nút "Báo cáo Tin nhắn Nghi ngờ" (Community Report Button)**
  * Mô tả: Cho phép người dùng bấm nút gửi nội dung tin nhắn nghi ngờ lên hệ thống máy chủ để đội ngũ quản trị kiểm duyệt và cập nhật mô hình.
* **Nhiệm vụ 1.4: Tối ưu Giao diện UI/UX & Đóng gói File Cài đặt APK**
  * Mô tả: Áp dụng Material 3, tinh chỉnh tông màu nhận diện hiện đại, bổ sung biểu tượng ứng dụng (App Icon) chuyên nghiệp.
  * Đóng gói: Tiến hành chạy `Build` -> `Build APK(s)` trong Android Studio để tạo ra file `ScamShield-AI-v1.0.apk` sẵn sàng cài trực tiếp lên điện thoại của ban giám khảo.

---

### MODULE 2: MỞ RỘNG MÁY CHỦ BACKEND & DỊCH VỤ ĐÁM MÂY (BACKEND & MLOPS)
* **Nhánh Git phụ trách:** `feature/backend-api`
* *Mục tiêu: Đảm bảo ứng dụng di động có thể kết nối Internet thực tế và xây dựng vòng lặp phản hồi dữ liệu (Active Learning).*

* **Nhiệm vụ 2.1: Bổ sung Endpoint Tiếp nhận Phản ánh `/api/v1/report`**
  * Mô tả: Tiếp nhận dữ liệu tin nhắn lừa đảo do người dùng báo cáo từ app Android hoặc Web Streamlit.
  * Xử lý: Tự động che số điện thoại cá nhân (PII Masking), lưu trữ mẫu mới vào hàng đợi dữ liệu (`data/reported_samples.json` hoặc cơ sở dữ liệu) phục vụ việc tái huấn luyện mô hình (Continuous Training).
* **Nhiệm vụ 2.2: Bổ sung Endpoint Đồng bộ Danh sách Đen Động `/api/v1/rules/sync`**
  * Mô tả: Trả về danh sách các tên miền lừa đảo mới nổi và từ khóa độc hại cập nhật trong ngày.
  * Ý nghĩa: Ứng dụng Android có thể tải danh sách này về để nâng cấp khả năng nhận diện offline mà không cần người dùng phải cài lại app mới.
* **Nhiệm vụ 2.3: Triển khai Backend lên Máy chủ Trực tuyến (Cloud Deployment)**
  * Mô tả: Đưa file `api.py` chạy trên một nền tảng trực tuyến công khai (ví dụ: Render, Railway, Hugging Face Spaces hoặc VPS có hỗ trợ SSL/HTTPS).
  * Ý nghĩa: Giúp điện thoại Android thật khi dùng mạng 4G/5G ngoài hội trường chấm thi vẫn có thể gọi được API backend thông qua Internet.

---

### MODULE 3: KIỂM THỬ THỰC THỰC NGHIỆM & ĐÁNH GIÁ MÔ HÌNH (DATA & BENCHMARKING)
* **Nhánh Git phụ trách:** `feature/ai-benchmark`
* *Mục tiêu: Thu thập số liệu khoa học, biểu đồ thực nghiệm phục vụ việc chứng minh hiệu quả dự án trước hội đồng SIC.*

* **Nhiệm vụ 3.1: Mở rộng Bộ dữ liệu Kiểm thử Thực tế (Real-world Test Suite)**
  * Mô tả: Thu thập thêm 30 - 50 mẫu tin nhắn lừa đảo thực tế xuất hiện tại Việt Nam cuối năm 2026 (lừa đảo tuyển dụng, mạo danh cục thuế hoàn thuế, phạt nguội giao thông, tặng quà tri ân sàn thương mại điện tử, cờ bạc lách luật).
  * Đo lường: Đưa các mẫu này qua cả 2 bộ máy (On-Device Heuristics và Server ML) để tính toán tỷ lệ phát hiện chính xác (Accuracy, True Positive Rate).
* **Nhiệm vụ 3.2: Đánh giá Hiệu năng Hệ thống (Performance Benchmarking)**
  * Đo lường thời gian suy luận (Inference Latency): So sánh tốc độ xử lý On-Device (tính bằng mili-giây) so với thời gian gọi API qua mạng.
  * Đo lường mức tiêu thụ tài nguyên trên Android: Kiểm tra mức tiêu hao RAM và độ ảnh hưởng đến thời lượng pin khi app chạy nền.
* **Nhiệm vụ 3.3: Vẽ Biểu đồ Trực quan hóa Khoa học**
  * Tạo các hình ảnh biểu đồ: Ma trận nhầm lẫn (Confusion Matrix), Biểu đồ Precision-Recall, Biểu đồ so sánh thời gian phản hồi giữa các kiến trúc để chèn vào báo cáo và slide thuyết trình.

---

### MODULE 4: HỒ SƠ BÁO CÁO, SLIDE THUYẾT TRÌNH & KỊCH BẢN DEMO (DEFENSE DELIVERABLES)
* **Quy cách làm việc:** Làm việc trực tiếp cùng Nhóm trưởng hoàn thiện hồ sơ nộp thầy (không cần tạo nhánh riêng).
* *Mục tiêu: Đóng gói toàn bộ sản phẩm trí tuệ thành bài thuyết trình thuyết phục và ấn tượng trước ban giám khảo.*

* **Nhiệm vụ 4.1: Thiết kế Slide Báo cáo Khóa luận (12 - 15 Slide Chuẩn mực)**
  * Slide 1: Trang tiêu đề dự án, mã nhóm, logo Samsung Innovation Campus.
  * Slide 2: Đặt vấn đề & Thực trạng lừa đảo viễn thông bùng nổ tại Việt Nam.
  * Slide 3: Mục tiêu dự án & Quyết định tập trung chuyên sâu nền tảng Android.
  * Slide 4: Kiến trúc giải pháp đa tầng (On-Device + Cloud AI).
  * Slide 5 - 6: Mô hình AI xử lý SMS (TF-IDF + Random Forest) & URL (Lexical + Logistic Regression).
  * Slide 7: Cơ chế On-Device Heuristic Engine (Giải quyết 4 thủ đoạn lách luật).
  * Slide 8: Thiết kế Tuân thủ Quyền riêng tư (Nghị định 13/2023/NĐ-CP & Bảo vệ OTP).
  * Slide 9: Giao diện ứng dụng Android & Tính năng Quét hộp thư.
  * Slide 10: Kết quả thử nghiệm thực tế & Đo lường hiệu năng.
  * Slide 11: Định hướng phát triển mở rộng trong tương lai.
  * Slide 12: Lời cảm ơn ban giám khảo & Ban điều hành SIC.
* **Nhiệm vụ 4.2: Xây dựng Kịch bản Thuyết trình & Trình diễn Trực tiếp (Live Demo Script)**
  * Soạn tài liệu từng bước hướng dẫn người thuyết trình thao tác khi đứng trên sân khấu:
    * Bước 1: Mở app Android, bật chế độ bảo vệ.
    * Bước 2: Giả lập gửi tin nhắn OTP ngân hàng -> App cho qua an toàn, không có chuông báo.
    * Bước 3: Dán tin nhắn lừa đảo cờ bạc có tên miền `(sqlpy.bidvzj.com)` -> App kích hoạt chuông báo động đỏ tức thì.
    * Bước 4: Chạy tính năng "Quét hộp thư" tìm ra các mối đe dọa tiềm ẩn trong máy.
* **Nhiệm vụ 4.3: Biên tập & Hoàn thiện Báo cáo Toàn văn (Final Report Document)**
  * Rà soát tài liệu `BAO_CAO_TONG_HOP_KIEN_THUC.md`, bổ sung bìa báo cáo, danh mục thuật ngữ viết tắt, danh mục hình ảnh và xuất bản ra định dạng PDF chính thức.

---

## III. HƯỚNG DẪN CÀI ĐẶT & BẮT ĐẦU DÀNH CHO THÀNH VIÊN KHI CLONE DỰ ÁN

Khi thành viên nhận link GitHub và clone dự án về máy tính cá nhân, làm theo các bước sau để thiết lập môi trường:

### 1. Lệnh Clone Mã nguồn
```bash
git clone https://github.com/doudleH/scamshield-ai.git
cd scamshield-ai
```

### 2. Thiết lập Môi trường Python (Dành cho Module 2 & Module 3)
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường (trên Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Khởi động Backend API (truy cập tài liệu tại: http://127.0.0.1:8000/docs)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Khởi động Web Dashboard Streamlit
streamlit run app.py
```

### 3. Thiết lập Môi trường Android Studio (Dành cho Module 1)
* **Khởi động Android Studio:** Chọn `File` -> `Open...` và trỏ đường dẫn chính xác vào thư mục:
  `scamshield-ai/mobile/android` *(Lưu ý quan trọng: Phải mở đúng thư mục `mobile/android`, không mở thư mục cha `mobile/`)*.
* Chờ Android Studio tự động tải Gradle và đồng bộ các gói thư viện (Sync Project with Gradle Files).
* Cắm cáp kết nối điện thoại Android thật (đã bật chế độ `Gỡ lỗi USB / USB Debugging`) hoặc bật máy ảo Android Emulator.
* Bấm nút **Run 'app'** (tam giác xanh) để nạp ứng dụng lên thiết bị.

---

## IV. LỘ TRÌNH TRIỂN KHAI THEO MỐC THỜI GIAN (DEADLINE: 30/10/2026)

* **Giai đoạn 1 (Ngày 25/10 - 27/10):**
  * Triển khai code Module 1 (Tính năng Quét hộp thư & Lịch sử cảnh báo trên Android).
  * Triển khai code Module 2 (Endpoint Report & Đồng bộ rules trên Backend).
  * Thu thập dữ liệu thực tế cho Module 3.
* **Giai đoạn 2 (Ngày 28/10):**
  * Tích hợp toàn diện các thành phần (End-to-End Testing).
  * Build file `app-release.apk` hoặc `app-debug.apk` hoàn chỉnh.
  * Quay video demo dự phòng (tránh rủi ro trục trặc kỹ thuật trong ngày báo cáo).
* **Giai đoạn 3 (Ngày 29/10):**
  * Hoàn thành Slide thuyết trình và in ấn báo cáo PDF.
  * Nhóm tiến hành tập dượt thuyết trình (Rehearsal) và căn thời gian theo quy định của ban tổ chức.
* **Ngày 30/10/2026:**
  * Báo cáo chính thức và bảo vệ dự án Capstone SIC-AI.
