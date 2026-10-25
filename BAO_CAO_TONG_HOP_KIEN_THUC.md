# TỔNG HỢP TOÀN BỘ KIẾN THỨC, TÀI NGUYÊN VÀ MÃ NGUỒN DỰ ÁN SCAMSHIELD AI

## PHẦN 1. NGUỒN TÀI NGUYÊN VÀ DỮ LIỆU ĐÃ SỬ DỤNG

### Dữ liệu huấn luyện tin nhắn SMS tiếng Việt
- Nguồn gốc dữ liệu: Bộ dữ liệu vietnamese_sms_dataset thu thập từ kho dữ liệu mở Hugging Face, được công bố bởi tác giả trannguyenthaituan.
- Quy mô mẫu: Tổng cộng 2.991 tin nhắn tiếng Việt thực tế đã được gán nhãn phân loại tin nhắn rác và tin nhắn lừa đảo.
- Tập huấn luyện (Train set): Tuyệt đối tách biệt tại đường dẫn data/raw/train.csv với 2.394 bản ghi, bao gồm 1.754 tin nhắn hợp lệ và 640 tin nhắn rác hoặc lừa đảo.
- Tập kiểm thử độc lập (Test set): Đường dẫn data/raw/test.csv gồm 597 bản ghi, bao gồm 439 tin nhắn hợp lệ và 158 tin nhắn rác hoặc lừa đảo.
- Đặc trưng dữ liệu: Chứa cả tin nhắn tiếng Việt có dấu và không dấu, phản ánh chính xác các hình thức mạo danh thông báo ngân hàng, khóa tài khoản, mã trúng thưởng, cuộc gọi nhỡ và tuyển dụng lừa đảo tại Việt Nam.

### Dữ liệu huấn luyện đường dẫn URL lừa đảo
- Nguồn gốc dữ liệu: Bộ dữ liệu PhishVN phiên bản 3.1.0 (A Time-Stamped Vietnamese URL Phishing Dataset) công bố bởi tác giả Vũ Thái Nguyên và các cộng sự trên kho lưu trữ khoa học Mendeley Data.
- Quy mô mẫu: 53.112 đường dẫn URL thực tế trong bối cảnh không gian mạng Việt Nam, được phân chia theo trục thời gian giúp quá trình đánh giá khách quan và ngăn chặn triệt để hiện tượng rò rỉ dữ liệu tương lai.
- Tập huấn luyện (Train set): 36.905 URL, bao gồm 11.004 URL lành tính và 25.901 URL lừa đảo.
- Tập kiểm thử độc lập (Test set): 8.941 URL, bao gồm 3.845 URL lành tính và 5.096 URL lừa đảo.
- Đặc trưng dữ liệu: Tập lừa đảo bao gồm các tên miền mạo danh thương hiệu, cổng thanh toán và ngân hàng; tập lành tính chủ yếu là các cổng thông tin điện tử của cơ quan nhà nước (.gov.vn).

### Danh bạ tên miền tin cậy (Whitelist)
- Nguồn gốc dữ liệu: Nhóm nghiên cứu tổng hợp thủ công từ danh bạ cổng thông tin chính thức của Ngân hàng Nhà nước Việt Nam, các ngân hàng thương mại cổ phần, báo chí quốc gia, cơ quan chính phủ và sàn thương mại điện tử lớn.
- Khối ngân hàng thương mại và tài chính: Vietcombank, Vietinbank, BIDV, Agribank, Techcombank, MBBank, ACB, Sacombank, VPBank, TPBank, OCB, HDBank, VIB, SHB, SeABank, MSB, Shinhan Bank.
- Khối ví điện tử và cổng thanh toán trung gian: MoMo, ZaloPay, VNPay, Viettel Money.
- Khối cơ quan nhà nước và báo chí chính thống: Toàn bộ hệ thống tên miền cấp cao .gov.vn, chinhphu.vn, ncsc.vn, vnexpress.net, dantri.com.vn, tuoitre.vn, thanhnien.vn, vietnamnet.vn, vtv.vn.
- Khối tiện ích và sàn thương mại điện tử: google.com, facebook.com, youtube.com, zalo.me, shopee.vn, lazada.vn, tiki.vn.

### Công nghệ, thư viện lập trình và hạ tầng triển khai
- Môi trường lập trình: Ngôn ngữ Python phiên bản 3.11 trên nền tảng phân phối Anaconda.
- Thư viện học máy và khoa học dữ liệu: Scikit-learn (phiên bản 1.3 trở lên), NumPy, Pandas, Joblib.
- Thư viện tiền xử lý và biểu thức chính quy: Thư viện chuẩn re, unicodedata, urllib.parse.
- Nền tảng giao diện người dùng: Thư viện Streamlit (phiên bản 1.30 trở lên).
- Công cụ kiểm thử phần mềm tự động: Thư viện Pytest.
- Hệ thống quản lý mã nguồn và tích hợp liên tục: GitHub, GitHub Actions chạy trên máy chủ ảo Ubuntu.
- Nền tảng lưu trữ và vận hành đám mây: Streamlit Community Cloud kết nối trực tiếp với GitHub Repository, tích hợp sẵn chứng chỉ bảo mật SSL/HTTPS.

---

## PHẦN 2. ĐỐI CHIẾU CHI TIẾT KIẾN THỨC VÀ BÀI HỌC THEO TOÀN BỘ 11 CHƯƠNG GIÁO TRÌNH SIC-AI

### Chương 1. Giới thiệu về Trí tuệ nhân tạo (SIC_AI_Chapter 1. Introduction to AI)
- Bài học đối chiếu: Bài 1. Khái niệm trí tuệ nhân tạo.
- Kiến thức đã áp dụng: Hiểu rõ khái niệm và mục tiêu của hệ thống AI là tự động hóa khả năng suy luận, phân loại và hỗ trợ con người ra quyết định trong bài toán nhận diện lừa đảo trực tuyến.
- Bài học đối chiếu: Bài 2. Ứng dụng trí tuệ nhân tạo.
- Kiến thức đã áp dụng: Áp dụng AI vào lĩnh vực an ninh mạng và bảo vệ người dùng số, cụ thể là phân tích ngữ cảnh tin nhắn độc hại và phát hiện các đường link mạo danh thời gian thực.
- Bài học đối chiếu: Bài 3. Kỹ thuật trong trí tuệ nhân tạo.
- Kiến thức đã áp dụng: Lựa chọn kỹ thuật học máy có giám sát (Supervised Learning) kết hợp với các luật suy diễn chuyên gia (Heuristics) để xây dựng hệ thống phòng thủ có độ chính xác cao.
- Bài học đối chiếu: Bài 4. Trí tuệ nhân tạo: Xu hướng, Thị trường và Đạo đức AI.
- Kiến thức đã áp dụng: Tuân thủ các nguyên tắc đạo đức AI và bảo vệ quyền riêng tư người dùng theo Nghị định 13/2023/NĐ-CP; thiết kế hệ thống theo chuẩn an toàn thông tin OWASP và nguyên lý Privacy by Design: xây dựng cơ chế Fast-Bypass tự động bỏ qua tin nhắn OTP ngân hàng chính thống, ẩn danh hóa mã số nhạy cảm (OTP Redaction) tại chỗ trên RAM thiết bị trước khi gửi ra mạng, áp dụng phương pháp phân tích tĩnh hình thái URL (Static Lexical Analysis) mà không gửi request HTTP tới máy chủ kẻ gian, triệt tiêu nguy cơ lỗ hổng SSRF và bảo mật tuyệt đối dữ liệu cá nhân của người tra cứu.
- Vị trí mã nguồn liên quan: File src/predict_url.py, src/text_preprocessing.py, mobile/android/SmsReceiver.kt và giao diện cảnh báo trong app.py.

### Chương 2. Toán học trong Khoa học dữ liệu (SIC_AI_Chapter 2. Math for Data Science)
- Bài học đối chiếu: Bài 1. Tổng quan toán học cho khoa học dữ liệu.
- Kiến thức đã áp dụng: Vận dụng tư duy định lượng trong việc mô hình hóa các hiện tượng lừa đảo qua mạng thành các bài toán tối ưu và phân loại nhị phân.
- Bài học đối chiếu: Bài 2. Toán học cơ bản trong Khoa học dữ liệu.
- Kiến thức đã áp dụng: Ứng dụng hàm số phi tuyến Sigmoid để ánh xạ tổ hợp tuyến tính các đặc trưng về thang đo xác suất liên tục từ 0 đến 1, phục vụ tính toán độ nghi ngờ và phân cấp rủi ro.
- Bài học đối chiếu: Bài 3. Tìm hiểu về Khoa học dữ liệu: Vector.
- Kiến thức đã áp dụng: Chuyển đổi văn bản tin nhắn tiếng Việt thành vector không gian đa chiều thông qua kỹ thuật TF-IDF với độ dài 5.000 chiều; trích xuất 12 đặc trưng hình thái URL thành vector 12 chiều số thực.
- Bài học đối chiếu: Bài 4. Tìm hiểu về Khoa học dữ liệu: Ma trận.
- Kiến thức đã áp dụng: Xử lý ma trận thưa (Sparse Matrix) sinh ra từ tập văn bản lớn và thực hiện các phép nhân ma trận trọng số trong quá trình huấn luyện và dự đoán của mô hình.
- Vị trí mã nguồn liên quan: File training/train_sms.py, training/train_url.py và src/predict_url.py.

### Chương 3. Phân tích dữ liệu khai phá (SIC_AI_Chapter 3. Exploratory Data Analysis - EDA)
- Bài học đối chiếu: Bài 1. Cấu trúc dữ liệu mảng NumPy cho hiệu suất tính toán tối ưu.
- Kiến thức đã áp dụng: Sử dụng mảng NumPy để lưu trữ và biến đổi các vector đặc trưng số học, tăng tốc độ xử lý suy luận xuống dưới 10 mili-giây cho mỗi yêu cầu.
- Bài học đối chiếu: Bài 2. Khám phá dữ liệu tối ưu thông qua Pandas.
- Kiến thức đã áp dụng: Sử dụng DataFrame để khảo sát phân phối mẫu của bộ dữ liệu PhishVN (53.112 bản ghi) và bộ dữ liệu SMS (2.991 bản ghi), phân tích cấu trúc cột, kiểu dữ liệu và tỷ lệ các lớp nhãn.
- Bài học đối chiếu: Bài 3. Tiền xử lý dữ liệu Pandas để thực thi mô hình tối ưu.
- Kiến thức đã áp dụng: Xử lý giá trị trống, làm sạch chuỗi ký tự, tách nhãn mục tiêu và lọc bỏ các bản ghi không hợp lệ; phát hiện tình trạng mất cân bằng mẫu nghiêm trọng trong tập dữ liệu URL (mẫu lừa đảo gấp 2.3 lần mẫu lành tính) để cấu hình tham số class_weight='balanced'.
- Bài học đối chiếu: Bài 4. Trực quan hóa dữ liệu cho các quy mô dữ liệu khác nhau.
- Kiến thức đã áp dụng: Phân tích trực quan tương quan giữa độ dài tên miền, số lượng dấu chấm, sự xuất hiện của từ khóa giả mạo với nhãn lừa đảo; phát hiện thiên lệch dữ liệu (Dataset Bias) khi tập lành tính chỉ có tên miền .gov.vn, từ đó thiết kế giải pháp Whitelist kết hợp để khắc phục hiện tượng báo động nhầm (False Positive).
- Vị trí mã nguồn liên quan: File training/train_sms.py, training/train_url.py và tài liệu reports/evaluation_summary.md.

### Chương 4. Xác suất và Thống kê (SIC_AI_Chapter 4. Probability and Statistics)
- Bài học đối chiếu: Chương 1. Tìm hiểu về Xác suất.
- Kiến thức đã áp dụng: Ứng dụng lý thuyết xác suất có điều kiện và Định lý Bayes để xây dựng mô hình phân loại cơ sở Multinomial Naive Bayes dựa trên xác suất đồng thời xuất hiện của các từ vựng lừa đảo.
- Bài học đối chiếu: Chương 2. Tìm hiểu về Thống kê I.
- Kiến thức đã áp dụng: Tính toán các đại lượng thống kê mô tả gồm trung bình, trung vị, độ lệch chuẩn và tỷ lệ phần trăm phân bố độ dài ký tự của URL và tin nhắn độc hại.
- Bài học đối chiếu: Chương 3. Tìm hiểu về Thống kê II.
- Kiến thức đã áp dụng: Khảo sát phân phối xác suất dự đoán của mô hình để phân chia các vùng tin cậy: vùng an toàn (xác suất dưới 0.35), vùng cảnh báo cần trọng (từ 0.35 đến dưới 0.70) và vùng nguy hiểm (từ 0.70 trở lên).
- Bài học đối chiếu: Chương 4. Kiểm định giả thuyết thống kê.
- Kiến thức đã áp dụng: Đánh giá sự khác biệt có ý nghĩa thống kê giữa các nhóm đặc trưng URL lừa đảo và URL hợp lệ, làm cơ sở lựa chọn bộ 12 đặc trưng hình thái mạnh nhất cho mô hình.
- Vị trí mã nguồn liên quan: File src/risk_engine.py, src/text_preprocessing.py và training/train_sms.py.

### Chương 5. Học máy 1 - Học có giám sát (SIC_AI_Chapter 5. Machine Learning 1)
- Bài học đối chiếu: Bài 1. Phân tích dữ liệu dựa trên học máy.
- Kiến thức đã áp dụng: Xây dựng quy trình học máy chuẩn mực gồm thu thập dữ liệu, phân chia tập huấn luyện và tập kiểm thử độc lập (Train/Test Split), ngăn chặn tuyệt đối rò rỉ dữ liệu (Data Leakage) giữa hai tập.
- Bài học đối chiếu: Bài 2. Ứng dụng của mô hình học có giám sát cho Dự báo số và Phân loại.
- Kiến thức đã áp dụng: Huấn luyện thuật toán hồi quy Logistic (Logistic Regression) kết hợp bộ chuẩn hóa StandardScaler trong một Pipeline đóng gói duy nhất của Scikit-learn, giúp xử lý phân loại URL lừa đảo đạt độ chính xác Precision ấn tượng 95.18% và F1-Score đạt 0.8609.
- Bài học đối chiếu: Bài 3. Ứng dụng của mô hình học có giám sát cho Phân loại và Đánh giá mô hình.
- Kiến thức đã áp dụng: Thử nghiệm mô hình Cây quyết định (Decision Tree); đo lường hiệu năng toàn diện trên tập kiểm thử độc lập thông qua Ma trận nhầm lẫn (Confusion Matrix), Độ chính xác (Precision), Độ nhạy (Recall) và Điểm F1-Score hài hòa, ưu tiên không bỏ sót kẻ gian (Recall cao).
- Vị trí mã nguồn liên quan: File training/train_url.py, training/evaluate.py và reports/url_model_comparison.csv.

### Chương 6. Học máy 2 - Học không giám sát (SIC_AI_Chapter 6. Machine Learning 2)
- Bài học đối chiếu: Bài 1. Thuật toán học máy không giám sát.
- Kiến thức đã áp dụng: Tìm hiểu nguyên lý học không giám sát trong việc phát hiện các dị biệt và mẫu hình bất thường không định trước trong dữ liệu mạng.
- Bài học đối chiếu: Bài 2. Phân cụm phân cấp.
- Kiến thức đã áp dụng: Khảo sát mức độ tương đồng giữa các họ tên miền lừa đảo để gom nhóm các biến thể mạo danh có cùng cấu trúc tên miền phụ.
- Bài học đối chiếu: Bài 3. Phân cụm không phân cấp.
- Kiến thức đã áp dụng: Phân cụm các mẫu hình tạo tên miền giả mạo thành 3 nhóm hành vi điển hình: nhóm dùng đuôi tên miền nguy hiểm giá rẻ (ccTLD bất thường), nhóm ghép nhiều dấu gạch ngang mạo danh thương hiệu, và nhóm tên miền tự sinh tự động bằng thuật toán DGA có tỷ lệ ký tự số cao.
- Bài học đối chiếu: Bài 4. Mô hình hệ số tuyến tính để giảm chiều.
- Kiến thức đã áp dụng: Đánh giá tương quan đa cộng tuyến giữa các đặc trưng hình thái URL, loại bỏ các đặc trưng thừa để giữ lại đúng 12 đặc trưng cô đọng và có lực phân tách tốt nhất.
- Vị trí mã nguồn liên quan: File src/predict_url.py và training/train_url.py.

### Chương 7. Xử lý ngôn ngữ tự nhiên và Mô hình ngôn ngữ trong Khai thác văn bản (SIC_AI_Chapter 7. NLP and Text Mining)
- Bài học đối chiếu: Chương 1 (Bài 1). Khai thác văn bản (Text Mining).
- Kiến thức đã áp dụng: Xác định rõ mục tiêu khai thác văn bản tiếng Việt là bóc tách các thủ thuật tâm lý thao túng, đe dọa khóa tài khoản hoặc dụ dỗ nhận tiền thưởng từ tin nhắn kẻ gian.
- Bài học đối chiếu: Chương 2 (Bài 2). Tiền xử lý văn bản.
- Kiến thức đã áp dụng: Chuẩn hóa toàn bộ bảng mã Unicode tiếng Việt về chuẩn dựng sẵn NFC nhằm triệt tiêu lỗi gõ dấu tổ hợp; chuyển văn bản về chữ thường; dùng biểu thức chính quy Regex để che mặt địa chỉ URL thành token đặc biệt <URL> và số điện thoại thành token <PHONE>; loại bỏ các ký tự rác và khoảng trắng thừa.
- Bài học đối chiếu: Chương 3 (Bài 3). Mô hình ngôn ngữ.
- Kiến thức đã áp dụng: Xây dựng bộ biểu diễn ngôn ngữ TF-IDF kết hợp n-gram đơn và n-gram đôi (ngram_range=(1, 2)) với kích thước từ điển 5.000 cụm từ, ghi nhận hiệu quả các cụm từ đe dọa như "khóa thẻ", "trong 24h", "xác minh ngay".
- Bài học đối chiếu: Chương 4 (Bài 4). Xử lý ngôn ngữ tự nhiên bằng học sâu và thực tiễn.
- Kiến thức đã áp dụng: Xử lý đặc thù ngôn ngữ tiếng Việt viết không dấu bằng cách thiết lập bộ từ điển song song có dấu và không dấu; tích hợp cơ chế hiệu chuẩn Heuristic vùng nhạy cảm khi xuất hiện đồng thời đường dẫn và từ khóa khẩn cấp.
- Vị trí mã nguồn liên quan: File src/text_preprocessing.py, src/predict_sms.py và models/sms_vectorizer.pkl.

### Chương 8. Mạng nơ-ron và Học sâu (SIC_AI_Chapter 8. Neural Network and Deep Learning)
- Bài học đối chiếu: Bài 1. Cơ bản về mạng nơ-ron.
- Kiến thức đã áp dụng: Nghiên cứu cấu trúc nơ-ron nhân tạo Perceptron, mạng nơ-ron đa lớp (MLP), cơ chế truyền thẳng, lan truyền ngược sai số (Backpropagation), thuật toán Gradient Descent và các hàm kích hoạt phi tuyến (Sigmoid, ReLU).
- Bài học đối chiếu: Bài 2. Cơ bản về TensorFlow.
- Kiến thức đã áp dụng: Khảo sát cách xây dựng đồ thị tính toán và cấu trúc luồng dữ liệu của các framework học sâu hiện đại.
- Bài học đối chiếu: Bài 3. Các phương pháp học sâu, đánh giá hiện tượng quá khớp và suy thoái gradient.
- Kiến thức đã áp dụng: Hiểu rõ cơ chế Regularization, Dropout và các nguyên nhân dẫn đến hiện tượng Overfitting khi huấn luyện mô hình sâu trên các tập dữ liệu có quy mô vừa và nhỏ; từ đó làm căn cứ lựa chọn mô hình học kết hợp Random Forest gồm 100 cây quyết định, giúp phân loại SMS tiếng Việt đạt kết quả F1-Score cao nhất 0.8598 mà không bị quá khớp.
- Vị trí mã nguồn liên quan: File training/train_sms.py và models/sms_model.pkl.

### Chương 9. Một số chủ đề về Học sâu (SIC_AI_Chapter 9. Various Deep Learning Topics)
- Bài học đối chiếu: Bài 1. Giới thiệu về mô hình CNN (Mạng nơ-ron tích chập).
- Kiến thức đã áp dụng: Nắm vững nguyên lý trích xuất đặc trưng không gian cục bộ thông qua các bộ lọc tích chập (Convolutional Filters) và phép gộp (Pooling).
- Bài học đối chiếu: Bài 2. Mạng nơ-ron hồi quy (RNN và LSTM) cho dữ liệu tuần tự.
- Kiến thức đã áp dụng: Tìm hiểu cơ chế lưu trữ trạng thái ẩn của mạng hồi quy và các cổng quên trong LSTM để mô hình hóa chuỗi câu từ theo thời gian trong xử lý ngôn ngữ tự nhiên.
- Bài học đối chiếu: Bài 3. Mạng nơ-ron đối nghịch (GAN) và Đánh giá cân bằng hiệu năng kỹ thuật.
- Kiến thức đã áp dụng: Thực hiện phân tích đánh giá đa chiều (Engineering Trade-offs) giữa mô hình Học sâu (như RNN/Transformer) và mô hình Học máy truyền thống: Mô hình Random Forest và Logistic Regression có tốc độ phản hồi siêu nhanh dưới 10 mili-giây, tổng dung lượng file mô hình chỉ khoảng 3.4 MB, hoạt động mượt mà không cần card đồ họa GPU rời, cực kỳ phù hợp cho môi trường máy chủ miễn phí và thiết bị di động.
- Vị trí mã nguồn liên quan: File reports/ai_architecture_sic.md và reports/evaluation_summary.md.

### Chương 10. Thực hành và Tinh chỉnh Mô hình Ngôn ngữ Lớn (SIC_AI_Chapter 10. Practical Use and Fine-Tuning of LLMs)
- Bài học đối chiếu: Bài 1. Sử dụng Hugging Face và API Pipeline.
- Kiến thức đã áp dụng: Khai thác kho dữ liệu mở Hugging Face Hub để tải và tích hợp bộ dữ liệu tin nhắn SMS tiếng Việt thực tế (vietnamese_sms_dataset).
- Bài học đối chiếu: Bài 2. Tinh chỉnh Mô hình Ngôn ngữ Lớn.
- Kiến thức đã áp dụng: Khảo sát chi phí tài nguyên tính toán và độ trễ khi vận hành các mô hình ngôn ngữ lớn (LLMs), từ đó xác định giải pháp kết hợp kiến trúc mô hình học máy tinh gọn chạy cục bộ với khả năng gọi mở rộng API khi cần thiết.
- Bài học đối chiếu: Bài 3. Tối ưu hóa Mô hình và các Kỹ thuật Tinh gọn.
- Kiến thức đã áp dụng: Tối ưu hóa kích thước mô hình học máy thông qua việc giới hạn 5.000 đặc trưng TF-IDF có tần số xuất hiện phù hợp (min_df=2), nén trọng số mô hình bằng Joblib để đạt tổng dung lượng siêu nhẹ 3.4 MB, cho phép lưu trữ và nạp tức thì trên đám mây.
- Bài học đối chiếu: Bài 4. Ứng dụng, Mở rộng, XAI và An toàn AI.
- Kiến thức đã áp dụng: Áp dụng nguyên lý Trí tuệ nhân tạo có thể giải thích (Explainable AI - XAI), thay vì biến mô hình thành một hộp đen khó hiểu, hệ thống bóc tách minh bạch từng yếu tố vi phạm cụ thể (như phát hiện từ khóa áp lực tâm lý, tên miền có nhiều subdomain, tên miền nằm trong danh sách rủi ro) để giải thích cặn kẽ cho người dùng; đồng thời xây dựng module sinh khuyến nghị an toàn số và công bố các tuyên bố miễn trừ trách nhiệm pháp lý.
- Vị trí mã nguồn liên quan: File src/risk_engine.py, src/explanations.py và app.py.

### Chương 11. Bắt đầu một Dự án AI (SIC_AI_Chapter 11. Starting an AI Project)
- Bài học đối chiếu: Bài 1. Chuẩn bị Dự án và Lập kế hoạch.
- Kiến thức đã áp dụng: Xác định bài toán thực tế cấp bách về lừa đảo qua mạng tại Việt Nam theo định hướng "lấy dữ liệu làm trung tâm" (Data-Centric AI); lập kế hoạch triển khai dự án qua 6 giai đoạn chuẩn mực của quy trình CRISP-DM từ thấu hiểu nghiệp vụ, khám phá dữ liệu, tiền xử lý, huấn luyện mô hình, kiểm thử đánh giá đến đóng gói triển khai.
- Bài học đối chiếu: Bài 2. Tư duy thiết kế trong Dự án AI (Design Thinking).
- Kiến thức đã áp dụng: Thấu cảm với người dân và đối tượng người lớn tuổi thường xuyên là nạn nhân của lừa đảo công nghệ cao; thiết kế giao diện đơn giản với thao tác 1 chạm, hỗ trợ dán nhanh dữ liệu mẫu; xây dựng bản mẫu thử nghiệm (Prototype) bằng Streamlit; áp dụng thực hành kỹ nghệ phần mềm chuyên nghiệp với kiểm thử tự động (Unit Test, Smoke Test) và thiết lập đường ống tích hợp liên tục CI/CD thông qua GitHub Actions; triển khai hoàn chỉnh ứng dụng lên nền tảng đám mây Streamlit Community Cloud và cung cấp mã QR cho thiết bị di động.
- Vị trí mã nguồn liên quan: File app.py, tests/test_pipeline.py, smoke_test.py, .github/workflows/ci.yml và reports/qr_code_scamshield.png.

---

## PHẦN 3. TỔNG HỢP TOÀN BỘ CÁC THÀNH PHẦN MÃ NGUỒN ĐÃ XÂY DỰNG

### Nhóm module xử lý thuật toán và nghiệp vụ cốt lõi (Thư mục src/)
- src/text_preprocessing.py:
  - Hàm clean_vietnamese_text: Chuẩn hóa bảng mã Unicode NFC, đưa văn bản về chữ thường, dùng biểu thức chính quy nhận diện và ẩn danh hóa liên kết và số điện thoại, loại bỏ các ký tự gây nhiễu.
  - Hàm extract_sms_heuristic_signals: Rà soát sự hiện diện của đường link, số điện thoại, đếm các từ khóa gây áp lực tâm lý trong danh sách URGENCY_KEYWORDS và tính điểm khẩn cấp sơ bộ.
- src/predict_sms.py:
  - Khởi tạo và nạp mô hình Random Forest (models/sms_model.pkl) cùng bộ vector hóa TF-IDF (models/sms_vectorizer.pkl).
  - Biến đổi văn bản đầu vào thành ma trận vector và tính toán xác suất lừa đảo thông qua hàm predict_proba.
  - Cài đặt cơ chế hiệu chuẩn xác suất ở khoảng giá trị nhạy cảm (từ 0.35 đến 0.65) khi phát hiện đồng thời liên kết và từ khóa khẩn cấp.
  - Tích hợp phương án dự phòng bằng Heuristic Baseline nếu các file mô hình chưa sẵn sàng.
- src/predict_url.py:
  - Định nghĩa danh sách đuôi tên miền rủi ro cao SUSPICIOUS_TLDS, danh sách từ khóa mạo danh SUSPICIOUS_KEYWORDS, và danh bạ tên miền tin cậy TRUSTED_DOMAIN_SUFFIXES.
  - Hàm extract_url_features_v2: Trích xuất chính xác 12 đặc trưng hình thái URL từ hostname mà không gửi yêu cầu HTTP ra mạng bên ngoài.
  - Hàm get_feature_vector_v2: Chuyển đổi tập đặc trưng thành vector số học 12 chiều phục vụ mô hình.
  - Hàm predict_url: Kiểm tra quyền ưu tiên tuyệt đối của danh bạ Whitelist trước; nếu không thuộc Whitelist sẽ đưa qua Pipeline gồm StandardScaler và LogisticRegression để suy luận xác suất.
  - Tự động trích xuất danh sách các yếu tố nghi ngờ để hiển thị minh bạch cho người dùng.
- src/risk_engine.py:
  - Hàm build_report: Tiếp nhận và phối hợp kết quả từ nhánh phân tích tin nhắn, nhánh phân tích đường dẫn và nhánh tra cứu nguồn dữ liệu ngoài.
  - Tổng hợp toàn bộ các bằng chứng phát hiện được thành danh sách rõ ràng.
  - Đánh giá theo hệ thống ngưỡng rủi ro ba cấp độ: DANGEROUS (Nguy hiểm), CAUTION (Cần trọng) và SAFE (An toàn).
  - Tự động đính kèm khuyến nghị phòng tránh và các giới hạn kỹ thuật cần minh bạch với người dùng.
- src/explanations.py:
  - Hàm generate_safety_advice: Sinh lời khuyên an toàn số phù hợp với từng mức độ rủi ro phát hiện được.
  - Cung cấp danh sách các đầu mối phản ánh lừa đảo chính thức của các cơ quan chức năng tại Việt Nam (Tổng đài 156, Tổng đài 5656 và Cổng giám sát an toàn không gian mạng quốc gia).
- src/threat_lookup.py:
  - Hàm lookup_url: Module hỗ trợ mở rộng kết nối tới các cơ sở dữ liệu danh sách đen ngoại vi thông qua biến môi trường API.
  - Trả về trạng thái hoạt động độc lập một cách minh bạch khi hệ thống vận hành thuần AI cục bộ.
- src/url_features.py:
  - Module trích xuất 16 đặc trưng hình thái phiên bản đầu, được duy trì để đảm bảo tính tương thích ngược với các thử nghiệm trước đó.

### Nhóm kịch bản huấn luyện và đánh giá mô hình (Thư mục training/)
- training/train_sms.py:
  - Đọc tự động tập huấn luyện data/raw/train.csv và tập kiểm thử data/raw/test.csv.
  - Thực hiện tiền xử lý và chuẩn hóa toàn bộ dữ liệu văn bản.
  - Khởi tạo bộ vector hóa TfidfVectorizer với unigram và bigram, giới hạn 5.000 đặc trưng.
  - Huấn luyện và so sánh đồng thời 3 thuật toán: MultinomialNB, LogisticRegression (cân bằng trọng số lớp) và RandomForestClassifier (100 cây quyết định).
  - Đánh giá Precision, Recall, F1-Score và Ma trận nhầm lẫn trên tập kiểm thử độc lập.
  - Lưu trữ mô hình chiến thắng (Random Forest đạt F1-Score 0.8598) vào models/sms_model.pkl và models/sms_vectorizer.pkl.
  - Xuất bảng kết quả chi tiết ra file reports/sms_model_comparison.csv.
- training/train_url.py:
  - Kết nối và đọc bộ dữ liệu PhishVN phiên bản 3.1.0 gồm 53.112 đường dẫn URL.
  - Trích xuất đồng nhất 12 đặc trưng hình thái URL cho toàn bộ tập dữ liệu.
  - Tách tập huấn luyện và kiểm thử theo đúng phân chia thời gian nguyên bản của bộ dữ liệu.
  - Huấn luyện và so sánh 3 mô hình: Pipeline gồm StandardScaler kết hợp LogisticRegression, DecisionTreeClassifier và RandomForestClassifier.
  - Lựa chọn mô hình tốt nhất là LogisticRegression Pipeline (F1-Score 0.8609, Precision 0.9518) và lưu thành models/url_model.pkl cùng metadata models/url_model_meta.pkl.
  - Xuất bảng đối chiếu ra file reports/url_model_comparison.csv.
- training/evaluate.py:
  - Tự động đọc dữ liệu kiểm thử từ các file CSV so sánh trong thư mục reports/.
  - Tổng hợp và tạo báo cáo markdown reports/evaluation_summary.md phục vụ tài liệu nghiệm thu.

### Ứng dụng giao diện người dùng Web (File app.py)
- Cấu hình trang với giao diện trực quan, tương thích hiển thị trên cả máy tính để bàn và trình duyệt di động.
- Áp dụng các đoạn mã CSS tùy biến để ẩn hoàn toàn các thanh trạng thái mặc định của nền tảng lưu trữ đám mây, mang lại trải nghiệm sản phẩm phần mềm độc lập và hoàn thiện.
- Thiết kế thanh điều hướng Sidebar chứa cẩm nang hướng dẫn thao tác, các nút bấm điền nhanh dữ liệu mẫu phục vụ trình diễn và danh bạ đường dây nóng hỗ trợ khẩn cấp.
- Tổ chức giao diện thành hai thẻ làm việc: Thẻ Kiểm tra rủi ro và thẻ Cẩm nang an toàn số.
- Tự động nhận diện và bóc tách liên kết URL nếu người dùng dán toàn bộ đoạn tin nhắn vào khung kiểm tra SMS.
- Trình bày kết quả đánh giá đa chiều với banner màu cảnh báo trực quan (Đỏ, Vàng, Xanh), bảng đồng hồ xác suất chi tiết cho từng thành phần, danh sách bằng chứng phát hiện được, lời khuyên hành động và tuyên bố miễn trừ trách nhiệm kỹ thuật.

### Cổng dịch vụ RESTful Backend API cho ứng dụng di động (File api.py)
- Xây dựng độc lập bằng framework hiệu năng cao FastAPI, tự động sinh tài liệu chuẩn quốc tế Swagger UI tại đường dẫn /docs.
- Cấu hình CORS Middleware cho phép mọi ứng dụng di động (Flutter, React Native, Android Kotlin, iOS Swift) kết nối an toàn.
- Điểm cuối /api/v1/scan: Nhận yêu cầu phân tích JSON chứa tin nhắn hoặc đường dẫn URL, thực thi quy trình suy luận AI đa tầng và phản hồi kết quả rủi ro định dạng chuẩn cho Mobile Client.
- Điểm cuối /api/v1/health: Giám sát trạng thái sẵn sàng của dịch vụ máy chủ và các mô hình học máy.

### Ứng dụng di động tự động đọc SMS và đẩy thông báo đẩy (Thư mục mobile/)
- mobile/android/AndroidManifest.xml: Khai báo các quyền hệ thống RECEIVE_SMS, READ_SMS, INTERNET và POST_NOTIFICATIONS (Android 13+).
- mobile/android/SmsReceiver.kt: Lắng nghe sự kiện SMS_RECEIVED thời gian thực trong nền, trích xuất nội dung tin nhắn và tự động gửi request bất đồng bộ tới FastAPI Backend (/api/v1/scan).
- mobile/android/NotificationHelper.kt: Tạo NotificationChannel ưu tiên cao và kích hoạt âm thanh, rung, hiển thị cảnh báo đỏ nổi bật lên màn hình khóa khi phát hiện tin nhắn lừa đảo.
- mobile/android/MainActivity.kt: Giao diện ứng dụng di động hiển thị trạng thái lá chắn bảo vệ 24/7, xin cấp quyền runtime từ người dùng và tích hợp nút giả lập nhận tin nhắn lừa đảo để phục vụ trình diễn trước hội đồng chấm thi.
- mobile/README_MOBILE_ARCHITECTURE.md: Tài liệu phân tích chuyên sâu về kiến trúc bảo mật di động Android và cơ chế mở rộng IdentityLookup MessageFilterExtension trên Apple iOS.

### Hệ thống kiểm thử tự động và tích hợp liên tục (Thư mục tests/, smoke_test.py và .github/)
- tests/test_pipeline.py:
  - Kiểm tra tính đúng đắn của hợp đồng dữ liệu đầu ra cho hàm dự đoán tin nhắn SMS (đầy đủ các trường định danh, xác suất và tín hiệu bóc tách).
  - Kiểm tra tính đúng đắn của hợp đồng dữ liệu đầu ra cho hàm dự đoán đường dẫn URL (đầy đủ các trường định danh, xác suất, vector đặc trưng và các yếu tố nghi ngờ).
  - Kiểm tra tính toàn vẹn của module tra cứu ngoại vi và module Risk Engine.
- smoke_test.py:
  - Kịch bản kiểm tra tích hợp đầu-cuối bao phủ 5 tình huống thực tế:
    - Tin nhắn mạo danh ngân hàng kèm liên kết lạ (hệ thống phải đưa ra mức cảnh báo cao).
    - Tin nhắn biến động số dư hợp lệ của ngân hàng (hệ thống phải xác định xác suất rủi ro thấp).
    - Đường link lừa đảo có cấu trúc tên miền bất thường (hệ thống phải cảnh báo lừa đảo).
    - Đường link chính thức của ngân hàng Vietcombank (hệ thống Whitelist phải xác nhận an toàn tuyệt đối, loại trừ hiện tượng báo nhầm).
    - Kiểm tra tổng thể tính đồng bộ của báo cáo do Risk Engine tạo ra.
- .github/workflows/ci.yml:
  - Quy trình tích hợp liên tục CI tự động kích hoạt trên máy ảo Ubuntu mỗi khi có thay đổi được đẩy lên nhánh main của kho mã nguồn GitHub.
  - Tự động thiết lập môi trường Python 3.11, cài đặt danh sách thư viện và thực thi toàn bộ kịch bản kiểm thử trong tests/test_pipeline.py và smoke_test.py, đảm bảo hệ thống luôn trong trạng thái sẵn sàng vận hành.

### Cấu hình an toàn và quản lý phiên bản mã nguồn (File .gitignore)
- Bỏ qua các file biên dịch trung gian của Python và các thư mục môi trường ảo.
- Bỏ qua các file dữ liệu thô kích thước lớn trong thư mục data/ nhằm giữ cho kho mã nguồn luôn gọn nhẹ và tối ưu tốc độ tải.
- Cho phép lưu trữ trực tiếp các file trọng số mô hình đã huấn luyện trong thư mục models/ vì tổng kích thước chỉ khoảng 3.4 MB, giúp hệ thống trên đám mây có thể chạy ngay lập tức mà không cần quy trình huấn luyện lại tốn thời gian.
- Bỏ qua các file cấu hình chứa thông tin nhạy cảm, khóa bảo mật, kế hoạch kinh doanh và tài liệu thuyết trình nội bộ nhằm bảo vệ quyền sở hữu trí tuệ của nhóm nghiên cứu.
