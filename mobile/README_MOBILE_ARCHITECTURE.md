# KIẾN TRÚC VÀ HƯỚNG DẪN TRIỂN KHAI ỨNG DỤNG DI ĐỘNG (MOBILE APP)
## HỆ THỐNG PHÁT HIỆN LỪA ĐẢO TỰ ĐỘNG THỜI GIAN THỰC SCAMSHIELD AI

---

### 1. BẢN CHẤT KỸ THUẬT VÀ PHÂN ĐỊNH NỀN TẢNG (WEB VS NATIVE APP)

#### Vì sao Web / PWA không thể tự động đọc SMS?
- Theo tiêu chuẩn bảo mật của các trình duyệt hiện đại (W3C, Google Chrome, Apple Safari), một trang Web thông thường **BỊ CẤM TUYỆT ĐỐI** việc tự động truy cập vào hộp thư tin nhắn SMS của điện thoại nhằm ngăn chặn việc lộ mã OTP ngân hàng và tin nhắn riêng tư.
- Do đó, trang Web (PC / Mobile Web) phục vụ mục đích **tra cứu chủ động (Manual Check)**: Người dùng copy nội dung tin nhắn hoặc đường link nghi ngờ và dán vào web để AI kiểm tra.

#### Giải pháp trên Ứng dụng Di động Native (Android & iOS):
- Để khi vừa mở app, ứng dụng **yêu cầu cấp quyền đọc tin nhắn SMS** và **tự động đẩy thông báo cảnh báo (Push Notification)** khi có tin nhắn lừa đảo gửi đến mà người dùng không cần mở app, chúng ta **BẮT BUỘC PHẢI DÙNG ỨNG DỤNG DI ĐỘNG NATIVE (Android Kotlin / Java hoặc Flutter / React Native)**.

---

### 2. LUỒNG HOẠT ĐỘNG THỜI GIAN THỰC TRÊN ANDROID

```text
[Tin nhắn SMS mới gửi đến điện thoại]
                     │
                     ▼
[Hệ điều hành Android kích hoạt broadcast SMS_RECEIVED]
                     │
                     ▼
[SmsReceiver.kt (BroadcastReceiver chạy ngầm)]
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
[Trích xuất nội dung SMS]    [Trích xuất đường link URL]
     │                               │
     └───────────────┬───────────────┘
                     ▼
[Gửi HTTP POST payload lên ScamShield FastAPI Backend: /api/v1/scan]
                     │
                     ▼
[Mô hình AI: Random Forest (SMS) + Logistic Regression (URL) + Whitelist]
                     │
                     ▼
           [Đánh giá cấp độ rủi ro]
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
[SAFE (An toàn)]           [DANGEROUS / CAUTION (Lừa đảo)]
(Không làm phiền người dùng)        │
                                     ▼
                   [NotificationHelper.kt kích hoạt]
                   - Rung chuông cảnh báo khẩn cấp
                   - Đẩy thông báo đỏ lên màn hình khóa:
                     "🚨 CẢNH BÁO LỪA ĐẢO: Mạo danh ngân hàng! Đừng bấm link!"
```

---

### 3. CÁC QUYỀN ĐẶC BIỆT TRONG FILE ANDROIDMANIFEST.XML

Để ứng dụng Android có thể lắng nghe tin nhắn và gửi thông báo, cần khai báo các quyền sau:

1. **`android.permission.RECEIVE_SMS`:**
   - Cho phép ứng dụng nhận thông điệp khi có tin nhắn SMS mới đến điện thoại.
2. **`android.permission.READ_SMS`:**
   - Cho phép ứng dụng đọc dữ liệu tin nhắn (người gửi, nội dung văn bản).
3. **`android.permission.INTERNET`:**
   - Cho phép ứng dụng gửi nội dung tin nhắn về máy chủ Backend FastAPI (`/api/v1/scan`) để phân tích AI.
4. **`android.permission.POST_NOTIFICATIONS`:**
   - Quyền bắt buộc từ Android 13 (API 33) trở lên để hiển thị thông báo đẩy khẩn cấp lên màn hình người dùng.

---

### 4. ĐẶC THÙ ĐỐI VỚI HỆ ĐIỀU HÀNH APPLE IOS

- Apple áp dụng chính sách hộp cát (Sandbox) nghiêm ngặt hơn Android: Ứng dụng iOS thông thường **không được cấp quyền đọc toàn bộ hộp thư SMS**.
- **Giải pháp chính thống trên iOS:** Apple cung cấp framework **`IdentityLookup`** với thành phần mở rộng **`ILMessageFilterExtension`**.
  - Khi có tin nhắn từ số lạ gửi đến máy iPhone, hệ điều hành iOS sẽ tự động gửi nội dung tin nhắn đó vào hàm `handle(_:context:)` của extension.
  - Extension gửi dữ liệu lên Backend `api.py` của ScamShield AI để kiểm tra.
  - Nếu kết quả là lừa đảo, extension báo cho iOS tự động đẩy tin nhắn đó sang tab **"Tin nhắn rác / Junk"** trong ứng dụng iMessage và cảnh báo người dùng.

---

### 5. CÁCH THỨC DEMO THUYẾT PHỤC VỚI THẦY VÀ HỘI ĐỒNG

Khi bảo vệ đồ án, để chứng minh tính năng Mobile hoạt động 100%, bạn có thể trình bày theo 2 cách:

#### Cách 1: Demo trực tiếp tính năng Giả lập (Simulation) ngay trên app
- Mở ứng dụng Android hoặc mở màn hình `MainActivity`.
- Bấm vào nút màu đỏ: **"⚡ Giả Lập Nhận SMS Lừa Đảo (Demo)"**.
- **Kết quả ngay lập tức:** Điện thoại sẽ rung lên, phát âm thanh cảnh báo và một thông báo biểu tượng đỏ hiện ngay trên thanh trạng thái:
  *"🚨 CẢNH BÁO LỪA ĐẢO TỪ: Vietcombank-Fake - Phát hiện 96% rủi ro: Chứa liên kết mạo danh (.xyz) và từ khóa đe dọa 24h. TUYỆT ĐỐI KHÔNG BẤM LINK!"*
- Chạm vào thông báo sẽ mở ra màn hình phân tích chi tiết của ScamShield AI.

#### Cách 2: Demo thực tế trên máy ảo Android Studio (Emulator)
1. Mở máy ảo Android trong Android Studio.
2. Cài đặt file APK của ScamShield AI và cấp quyền khi mở ứng dụng.
3. Trên thanh công cụ của máy ảo Android Studio, bấm vào dấu **3 chấm (...) -> Phone**.
4. Nhập số người gửi: `Vietcombank` và dán nội dung:
   `Thong bao: Tai khoan VCB cua quy khach bi khoa. Vui long dang nhap http://vcb-verify.xyz de xac minh.`
5. Bấm **"Send Message"**.
6. **Quan sát:** Máy ảo ngay lập tức nhận tin nhắn, `SmsReceiver` kích hoạt ngầm gửi dữ liệu tới FastAPI `api.py`, và màn hình máy ảo lập tức bật thông báo cảnh báo lừa đảo khẩn cấp!

---

### 6. CƠ CHẾ BẢO MẬT TUYỆT ĐỐI MÃ OTP VÀ DỮ LIỆU NHẠY CẢM (PRIVACY BY DESIGN)

Câu hỏi bảo mật sống còn: *"Nếu tin nhắn là mã OTP ngân hàng, làm sao để app không đọc/lưu trộm, và nếu máy chủ bị hacker tấn công thì khách hàng có bị lộ mã OTP hay không?"*

Nhóm phát triển đã thiết kế hệ thống theo nguyên tắc **Zero-Knowledge Privacy** và **Privacy by Design** (Tuân thủ nghiêm ngặt Nghị định 13/2023/NĐ-CP về Bảo vệ dữ liệu cá nhân) thông qua 4 tầng lá chắn:

#### Tầng 1: Cơ chế bỏ qua lập tức tin nhắn OTP thật (Legitimate OTP Fast-Bypass)
- Ngay tại `SmsReceiver.kt` trên điện thoại, hệ thống kiểm tra: Nếu tin nhắn đến từ Brandname ngân hàng chính thức (`TRUSTED_BANK_SENDERS`) và trong nội dung chứa mã OTP thông thường **nhưng hoàn toàn KHÔNG CÓ bất kỳ đường link URL nào**:
- **Hành động:** Ứng dụng lập tức **hủy luồng xử lý (`return`)**, không gửi bất kỳ byte dữ liệu nào ra mạng Internet, xóa nội dung tin nhắn khỏi bộ nhớ RAM của máy ngay trong mili-giây.

#### Tầng 2: Ẩn danh hóa cục bộ tại chỗ trước khi truyền mạng (On-Device Redaction)
- Trong trường hợp tin nhắn từ số lạ có chứa mã số: Ứng dụng Android sử dụng thuật toán Regex chạy cục bộ trên chip của điện thoại để **thay thế toàn bộ dãy số mã OTP thật thành token `[MÃ_OTP_ĐÃ_ẨN_DANH]`**, và số thẻ ngân hàng thành `[SỐ_TÀI_KHOẢN_ĐÃ_ẨN_DANH]`.
- **Hệ quả an toàn:** Dữ liệu gửi qua mạng Internet lên Backend **HOÀN TOÀN KHÔNG CHỨA MÃ OTP THẬT**. Hacker dù có can thiệp bắt gói tin giữa đường (Man-in-the-Middle) cũng chỉ thấy một chuỗi ký tự vô nghĩa đã được ẩn danh.

#### Tầng 3: Kiến trúc máy chủ phi lưu trữ (Zero-Persistence / Stateless Backend)
- Máy chủ Backend FastAPI (`api.py`) được thiết kế **hoàn toàn không có cơ sở dữ liệu (No Database)** để lưu nội dung tin nhắn của người dùng.
- Dữ liệu nhận vào chỉ tồn tại tạm thời trong bộ nhớ RAM trong vòng dưới 10 mili-giây để mô hình AI tính toán xác suất rủi ro, sau đó cơ chế Garbage Collection của hệ thống tự động giải phóng vùng nhớ.
- **Kịch bản Hacker tấn công máy chủ:** Kể cả khi toàn bộ hệ thống máy chủ bị xâm nhập, hacker cũng **hoàn toàn trắng tay** vì không có bất kỳ cơ sở dữ liệu, bảng lưu trữ hay file log nào chứa tin nhắn hay thông tin cá nhân của người dùng.

#### Tầng 4: Mã hóa đường truyền và chứng chỉ bảo mật (Transport Security)
- Toàn bộ kết nối giữa Mobile Client và Backend API đều bắt buộc phải chạy qua giao thức **HTTPS với mã hóa TLS 1.3** và chứng chỉ bảo mật SSL, ngăn chặn triệt để nguy cơ giả mạo máy chủ hoặc nghe lén trên các mạng Wi-Fi công cộng.
