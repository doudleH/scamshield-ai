# BỘ MẪU TIN NHẮN KIỂM THỬ THỰC TẾ VÀ KỊCH BẢN DEMO
**Dự án:** ScamShield AI – Hệ thống Giám sát & Phát hiện Tin nhắn, Đường dẫn Lừa đảo Đa tầng
**Chương trình:** Samsung Innovation Campus (SIC-AI) Capstone Project
**Thời điểm biên soạn:** 30/10/2026
**Tài liệu phục vụ:** Kiểm thử tích hợp hệ thống, thực nghiệm độ chính xác và kịch bản trình diễn trực tiếp trước Hội đồng chấm thi.

---

## I. MỤC TIÊU VÀ QUY CÁCH SỬ DỤNG BỘ KIỂM THỬ

Tài liệu này cung cấp tập hợp các mẫu dữ liệu thực nghiệm tiêu biểu phản ánh đúng bối cảnh tấn công lừa đảo trực tuyến tại Việt Nam trong năm 2026. Bộ dữ liệu được thiết kế nhằm phục vụ 3 mục đích chính:

* Thử nghiệm trực tiếp trong Hộp cát kiểm thử nội bộ (In-app Test Sandbox) trên ứng dụng di động Android Native.
* Kiểm thử tính năng phân tích và trực quan hóa giải trình (XAI) trên Bảng điều khiển Web Streamlit (`app.py`).
* Kiểm thử khả năng tiếp nhận yêu cầu và phản hồi qua giao diện lập trình ứng dụng RESTful API (`POST /api/v1/scan` tại `http://localhost:8000/docs`).

---

## II. NHÓM 1: CÁC MẪU TIN NHẮN LỪA ĐẢO CÓ ĐƯỜNG DẪN (PHISHING URL)

Nhóm này kiểm tra sự phối hợp đồng bộ giữa Mô hình Xử lý Ngôn ngữ Tự nhiên (TF-IDF + Random Forest) và Mô hình Phân tích Hình thái Tên miền Hostname (Logistic Regression kết hợp 12 đặc trưng tĩnh, tuyệt đối chống lỗ hổng SSRF).

### 1. Mạo danh Ngân hàng thương mại đe dọa khóa tài khoản (Brand Typosquatting)
* **Kịch bản tấn công:** Kẻ gian tạo tên miền gần giống ngân hàng thật (ví dụ: `vcb-digibank-login.xyz`), đánh vào tâm lý hoang mang sợ bị gián đoạn giao dịch tài chính để lừa người dùng đăng nhập chiếm đoạt mã xác thực.
* **Cơ chế nhận diện:** Hệ thống phát hiện từ khóa đe dọa khẩn cấp ("bị khóa", "trong 24h") và tên miền có đuôi TLD nguy cơ cao `.xyz` không nằm trong Danh sách tin cậy (Whitelist).
* **Nội dung kiểm thử:**
```text
Thong bao: Tai khoan VCB Digibank cua quy khach bi khoa do dang nhap bat thuong tren thiet bi la. Vui long truy cap http://vcb-digibank-login.xyz/verify de xac minh trong 24h.
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 85%, Kích hoạt rung và chuông báo động đỏ trên Android.

### 2. Lừa đảo Cờ bạc lách bộ lọc viễn thông (CamelCase Evasion & Tên miền trong ngoặc)
* **Kịch bản tấn công:** Thủ đoạn mới nhất năm 2026 nhằm vượt qua tường lửa SMS của các nhà mạng viễn thông: viết hoa dính liền từ ngữ không dấu cách, bao bọc tên miền cờ bạc trong ngoặc đơn và gắn kèm đuôi `GOOGLE.COM` làm mồi nhử.
* **Cơ chế nhận diện:** Động cơ Heuristic ngoại tuyến trên Android (`SmsReceiver.kt`) bóc tách chuỗi CamelCase `kFDangKiNhanPhanThuong`, trích xuất tên miền trong ngoặc `sqlpy.bidvzj.com` và nhận diện thủ đoạn ngụy trang mồi nhử.
* **Nội dung kiểm thử:**
```text
kFDangKiNhanPhanThuong201Ngin tai (sqlpy.bidvzj.com) GOOGLE.COM
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro 100%, Động cơ On-Device bắt trúng tức thì dưới 10 mili-giây.

### 3. Giả mạo Cục Cảnh sát Giao thông thông báo "Phạt nguội"
* **Kịch bản tấn công:** Mạo danh cơ quan thực thi pháp luật thông báo phương tiện vi phạm giao thông và yêu cầu nộp phạt trực tuyến gấp để tránh bị tạm giữ giấy tờ/phương tiện.
* **Cơ chế nhận diện:** Phát hiện cấu trúc đe dọa nộp tiền, số tiền phạt lớn và tên miền mạo danh sử dụng TLD giá rẻ `.site`.
* **Nội dung kiểm thử:**
```text
Cuc Canh Sat Giao Thong thong bao: Phuong tien cua ban co bien ban vi pham phat nguoi 5.000.000d. Vui long nop phat truc tuyen tranh bi tam giu phuong tien tai: http://csgt-nop-phat-nguoi.site/tra-cuu
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 80%.

### 4. Lừa đảo Trúng thưởng Tri ân Sàn Thương mại Điện tử
* **Kịch bản tấn công:** Đánh vào lòng tham của nạn nhân bằng cách mạo danh các sàn thương mại điện tử lớn (Shopee, Lazada, TikTok Shop) thông báo trúng thưởng thiết bị công nghệ đắt tiền.
* **Cơ chế nhận diện:** Mô hình NLP nhận diện mẫu câu chúc mừng trúng thưởng ảo kết hợp tên miền phishing đuôi `.top`.
* **Nội dung kiểm thử:**
```text
Chuc mung ban da trung thuong 1 iPhone 16 Pro Max tri gia 34.000.000d tu chuong trinh tri an khach hang Shopee. Nhan thuong ngay tai: http://qua-tang-tri-an.top/nhanthuong
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 85%.

### 5. Giả mạo Cơ quan Thuế hoàn tiền thuế điện tử
* **Kịch bản tấn công:** Lợi dụng mùa quyết toán thuế, gửi tin nhắn mạo danh Tổng cục Thuế thông báo hoàn tiền thuế thu nhập cá nhân để dẫn dụ người dùng tải mã độc hoặc đăng nhập tài khoản ngân hàng.
* **Cơ chế nhận diện:** Tên miền giả mạo sử dụng đuôi `.cc`, đường dẫn không phải cổng dịch vụ công nhà nước `.gov.vn`.
* **Nội dung kiểm thử:**
```text
Tong Cuc Thue thong bao: Quy khach duoc hoan 2.450.000d tien thue thu nhap ca nhan nam 2026. Truy cap cong dich vu truc tuyen de nhan tien ve tai khoan: http://cuc-thue-hoanthue.cc/login
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 90%.

---

## III. NHÓM 2: CÁC MẪU TIN NHẮN LỪA ĐẢO KHÔNG CÓ ĐƯỜNG DẪN (THAO TÚNG TÂM LÝ)

Nhóm này kiểm tra năng lực chuyên sâu của Mô hình Xử lý Ngôn ngữ Tự nhiên (NLP & Text Mining) theo Chương 7 giáo trình SIC-AI. Kẻ gian không gửi link mà dẫn dụ nạn nhân gọi lại số lạ, kết bạn Zalo/Telegram hoặc chuyển khoản tiền gấp.

### 1. Lừa đảo Tuyển dụng việc làm ảo / Việc nhẹ lương cao
* **Kịch bản tấn công:** Tuyển dụng cộng tác viên xử lý đơn hàng online tại nhà với mức thù lao vô lý (300.000đ - 800.000đ/ngày), yêu cầu liên hệ Zalo hoặc số điện thoại cá nhân.
* **Cơ chế nhận diện:** Mô hình NLP nhận diện cấu trúc chào mời việc làm tại nhà, không cần kinh nghiệm, trả lương theo ngày và điều hướng sang kênh liên lạc cá nhân.
* **Nội dung kiểm thử:**
```text
Tuyen dung: Cong ty TNHH Shopee tuyen nhan vien online lam tai nha, xu ly don hang 300k - 800k/ngay, khong can kinh nghiem, tra luong trong ngay. Lien he Zalo: 0987123456 gap chi Lan.
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo CẦN TRỌNG hoặc NGUY HIỂM (CAUTION / DANGEROUS), Điểm rủi ro trên 70%.

### 2. Mạo danh Cơ quan Cảnh sát điều tra đe dọa bắt giữ
* **Kịch bản tấn công:** Kẻ lừa đảo xưng danh Bộ Công an thông báo số CCCD của nạn nhân liên quan đến đường dây tội phạm xuyên quốc gia, yêu cầu gọi lại số điện thoại giả mạo để thao túng tâm lý chiếm đoạt tài sản.
* **Cơ chế nhận diện:** Phát hiện các thực thể đe dọa đặc trưng ("Bo Cong An", "buon ma tuy", "rua tien", "hop tac giai trinh").
* **Nội dung kiểm thử:**
```text
Bo Cong An thong bao: So CCCD cua ban co lien quan den du an buon ma tuy va rua tien xuyen quoc gia. Yeu cau co mat tai co quan dieu tra trong 24 gio hoac goi ngay toi so 0899123888 de hop tac giai trinh.
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 85%.

### 3. Mạo danh Người thân / Bạn bè vay tiền cấp cứu tai nạn
* **Kịch bản tấn công:** Nhắn tin xưng con hoặc người nhà thông báo bị tai nạn nguy kịch đang nằm viện, giục chuyển tiền gấp vào số tài khoản ngân hàng lạ để kịp thời phẫu thuật.
* **Cơ chế nhận diện:** Nhận diện cấu trúc cảm xúc khẩn cấp ("tai nan", "cap cuu", "vien phi", "gap", "chuyen ngay").
* **Nội dung kiểm thử:**
```text
Con bi tai nan giao thong dang cap cuu tai benh vien Cho Ray, can dong vien phi gap 20 trieu de mo. Me chuyen ngay vao so tai khoan MBBank 09123456789 chu tai khoan NGUYEN VAN A giup con voi!
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 75%.

### 4. Lừa đảo Tăng tương tác TikTok / Nhiệm vụ xem video kiếm tiền
* **Kịch bản tấn công:** Dụ dỗ người dùng tham gia các nhóm kín Telegram để làm nhiệm vụ xem video, thả tim nhận tiền hoa hồng, từ đó dẫn dắt nạp tiền làm nhiệm vụ lớn rồi chiếm đoạt.
* **Cơ chế nhận diện:** Bắt các từ khóa cày tương tác mạng xã hội ("thu dong", "tha tim", "Telegram", "nhiem vu").
* **Nội dung kiểm thử:**
```text
Kiem tien thu dong cung TikTok: Chi can xem video va tha tim nhan 50k/luot, moi ngay kiem 1 trieu de dang. Tham gia nhom Telegram @kiemtienonline2026 de nhan nhiem vu dau tien.
```
* **Kỳ vọng đầu ra:** Mức độ cảnh báo NGUY HIỂM (DANGEROUS), Điểm rủi ro trên 80%.

---

## IV. NHÓM 3: CÁC MẪU HỢP PHÁP ĐỐI CHỨNG (BENIGN BASELINE)

Nhóm mẫu này dùng để chứng minh hệ thống hoạt động thông minh, **không báo động nhầm (giảm thiểu False Positive)** và tuân thủ nguyên lý Privacy by Design (Nghị định 13/2023/NĐ-CP).

### 1. Tin nhắn Mã xác thực giao dịch OTP Ngân hàng (Fast-Bypass)
* **Kịch bản:** Người dùng thực hiện chuyển khoản hợp pháp và nhận được tin nhắn OTP từ ngân hàng thương mại.
* **Cơ chế xử lý:** Cơ chế Fast-Bypass của `SmsReceiver.kt` nhận diện Brandname ngân hàng và cấu trúc OTP chuẩn -> Tự động cho qua, tuyệt đối không gửi lên mạng, không lưu trữ mã OTP nhằm bảo vệ an toàn tài khoản.
* **Nội dung kiểm thử:**
```text
Vietcombank: Ma OTP xac thuc giao dich chuyen khoan 5,000,000 VND la 849201. Ma co hieu luc trong 3 phut. Tuyet doi khong chia se ma nay cho bat ky ai.
```
* **Kỳ vọng đầu ra:** Mức độ AN TOÀN (SAFE), Điểm rủi ro 0%, Không có cảnh báo chuông/rung.

### 2. Tin nhắn Thông báo Cước Viễn thông / Ví điện tử Hợp pháp (Có link Whitelist)
* **Kịch bản:** Tin nhắn thông báo xác nhận thanh toán tiền điện từ ví điện tử Viettel Money có đính kèm đường link chính thống.
* **Cơ chế xử lý:** Tên miền `viettelmoney.vn` nằm trong Whitelist hơn 50 thương hiệu đã xác minh -> Bỏ qua phân tích nghi ngờ.
* **Nội dung kiểm thử:**
```text
Cam on quy khach da thanh toan thanh cong hoa don tien dien thang 10 so tien 450.000d qua Viettel Money. Ma GD: VT123456789. Chi tiet tai https://viettelmoney.vn
```
* **Kỳ vọng đầu ra:** Mức độ AN TOÀN (SAFE), Điểm rủi ro dưới 15%.

---

## V. KỊCH BẢN THUYẾT MINH VÀ TRÌNH DIỄN TRỰC TIẾP (LIVE DEMO PROTOCOL)

Khi trình diễn trước Hội đồng Ban giám khảo, nhóm nên thực hiện theo trình tự 4 bước sau để tạo hiệu ứng thuyết phục cao nhất:

* **Bước 1 (Trình diễn Cơ chế Fast-Bypass & Quyền riêng tư):** Dán mẫu tin nhắn OTP Vietcombank thật vào app -> Nhấn mạnh với Thầy: *"Hệ thống tự động bỏ qua để đảm bảo không vi phạm Nghị định 13/2023/NĐ-CP và không rò rỉ mã bảo mật tài chính của người dùng."*
* **Bước 2 (Trình diễn Bắt bài Chiêu trò lách luật viễn thông):** Dán mẫu cờ bạc `kFDangKiNhanPhanThuong201Ngin tai (sqlpy.bidvzj.com)` -> App kích hoạt chuông báo động đỏ lập tức -> Nhấn mạnh: *"Đây là thủ đoạn lách bộ lọc mới nhất năm 2026 mà các app thông thường bị lọt lưới, nhưng động cơ On-Device của nhóm bắt trúng 100%."*
* **Bước 3 (Trình diễn Quét toàn bộ hộp thư SMS Inbox):** Bấm nút "Quét toàn bộ hộp thư" -> Hệ thống duyệt qua tin nhắn trong điện thoại và bóc tách danh sách cảnh báo các mối đe dọa cũ còn tồn đọng.
* **Bước 4 (Trình diễn Vòng lặp phản hồi Active Learning):** Bấm nút "Báo cáo tin nhắn này" -> Dữ liệu được che số điện thoại PII tự động truyền về máy chủ FastAPI (`POST /api/v1/report`) sẵn sàng cho việc tái huấn luyện mô hình.
