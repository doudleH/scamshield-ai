"""
ScamShield AI - Training Script for Vietnamese SMS
Huấn luyện mô hình phân loại tin nhắn SMS tiếng Việt:
- Tiền xử lý văn bản
- Trích xuất đặc trưng TF-IDF
- So sánh các mô hình: MultinomialNB, LogisticRegression, RandomForest
- Đánh giá bằng Precision, Recall, F1-Score, Confusion Matrix
- Lưu mô hình tốt nhất vào thư mục models/
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score

# Thêm đường dẫn src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.text_preprocessing import clean_vietnamese_text

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def create_synthetic_vietnamese_sample_data(filepath: str):
    """
    Tạo bộ dữ liệu mẫu ban đầu để kiểm thử pipeline nếu chưa tải kịp dataset lớn.
    """
    samples = [
        # Spam / Phishing
        ("Thong bao: Tai khoan VCB cua ban bi khoa. Vui long truy cap http://vcb-login.xyz de xac minh trong 24h", 1),
        ("Chuc mung ban da trung thuong xe SH tri an khach hang. Nhan thuong ngay tai http://qua-tang-vtv.top", 1),
        ("Cuc Canh sat giao thong thong bao: Phuong tien cua ban co loi phat nguoi. Dong tien tai http://phatnguoi-vn.site", 1),
        ("Quy khach duoc giai ngan khoan vay 50 trieu lai suat 0%. Nhan tien qua zalo 0987654321 hoac click link", 1),
        ("Canh bao: Phat hien giao dich 5.000.000d bat thuong. Neu khong phai ban, nhap ma OTP tai http://bank-secure.cc", 1),
        ("Tuyen dung CTV online lam viec tai nha thu nhap 500k/ngay. Lien he telegram @kiemtienonline", 1),
        ("Tai khoan ViettelPay cua ban se bi tam ngung. Vao ngay http://viettel-pay-capnhat.xyz de cap nhat", 1),
        ("Thong bao tu Bo Cong an: Yeu cau xac minh danh tinh vu an kinh te. Truy cap link ben duoi", 1),
        # Ham / Legitimate
        ("Cam on quy khach da su dung dich vu cua Viettel. Ma xac thuc cua ban la 123456. Khong chia se ma nay cho ai.", 0),
        ("So du tai khoan VCB 0123456789 thay doi +500.000 VND luc 14:30. So du hien tai: 2.500.000 VND.", 0),
        ("Don hang 987654 cua ban da duoc giao thanh cong boi shipper Nguyen Van A. Cam on ban da mua hang tai Shopee.", 0),
        ("Lich hen kham benh cua quy khach tai Benh vien Bach Mai luc 08:30 ngay mai. Vui long den dung gio.", 0),
        ("Cong ty dien luc thong bao tien dien ky 10 cua quy khach la 350.000d. Han thanh toan den het ngay 20/10.", 0),
        ("Chuyen khoan thanh cong 200.000d den Nguyen Thi B. Noi dung: tra tien an trua.", 0),
        ("Lop hoc Trí tuệ nhân tạo SIC se bat dau vao luc 19h00 thu 6. Xin vui long vao dung gio.", 0),
        ("Ma khuyen mai giam 20% chuyen xe Grab cua ban la GRAB20. Ap dung den het ngay mai.", 0)
    ]
    df = pd.DataFrame(samples, columns=["text", "label"])
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"Đã tạo dữ liệu mẫu kiểm thử tại: {filepath}")
    return df

def train_and_evaluate_sms(train_path: str = None, test_path: str = None):
    print("=== BẮT ĐẦU HUẤN LUYỆN MÔ HÌNH SMS PHISHING (TIẾNG VIỆT) ===")
    
    default_train = os.path.join(DATA_DIR, "raw", "train.csv")
    default_test = os.path.join(DATA_DIR, "raw", "test.csv")

    if train_path is None and os.path.exists(default_train):
        train_path = default_train
    if test_path is None and os.path.exists(default_test):
        test_path = default_test

    if train_path and os.path.exists(train_path):
        print(f"Đọc tập Train thực tế từ: {train_path}")
        train_df = pd.read_csv(train_path)
    else:
        sample_path = os.path.join(DATA_DIR, "sample_vietnamese_sms.csv")
        train_df = create_synthetic_vietnamese_sample_data(sample_path)

    # Xác định cột text và label
    def get_text_label_cols(df):
        text_c = "message" if "message" in df.columns else ("text" if "text" in df.columns else df.columns[0])
        label_c = "label" if "label" in df.columns else df.columns[1]
        return text_c, label_c

    t_col, l_col = get_text_label_cols(train_df)

    # 1. Tiền xử lý tập Train
    print("Tiền xử lý văn bản tiếng Việt tập Train...")
    train_df["cleaned_text"] = train_df[t_col].astype(str).apply(clean_vietnamese_text)
    
    if train_df[l_col].dtype == object:
        train_df[l_col] = train_df[l_col].map(lambda x: 1 if str(x).lower() in ["spam", "phishing", "1", "scam"] else 0)

    X_train = train_df["cleaned_text"]
    y_train = train_df[l_col].astype(int)

    print(f"Tập Train: {len(X_train)} mẫu | Phân phối: 0 (Hợp lệ) = {sum(y_train == 0)}, 1 (Lừa đảo) = {sum(y_train == 1)}")

    # 2. Xử lý tập Test độc lập (nếu có)
    if test_path and os.path.exists(test_path):
        print(f"Đọc tập Test độc lập từ: {test_path}")
        test_df = pd.read_csv(test_path)
        tt_col, tl_col = get_text_label_cols(test_df)
        test_df["cleaned_text"] = test_df[tt_col].astype(str).apply(clean_vietnamese_text)
        if test_df[tl_col].dtype == object:
            test_df[tl_col] = test_df[tl_col].map(lambda x: 1 if str(x).lower() in ["spam", "phishing", "1", "scam"] else 0)
        X_test = test_df["cleaned_text"]
        y_test = test_df[tl_col].astype(int)
        print(f"Tập Test độc lập: {len(X_test)} mẫu | Phân phối: 0 = {sum(y_test == 0)}, 1 = {sum(y_test == 1)}")
    else:
        print("Không tìm thấy test.csv độc lập, tiến hành chia Train/Test ngẫu nhiên (Stratified 25%)...")
        X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.25, random_state=42, stratify=y_train)

    # 3. Trích xuất đặc trưng TF-IDF
    print("Trích xuất đặc trưng TF-IDF (N-gram 1-2, max 5000 features)...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 4. Huấn luyện và so sánh các mô hình
    models = {
        "MultinomialNB": MultinomialNB(alpha=0.1),
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    best_model_name = None
    best_f1 = -1
    best_model = None

    results = []

    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        y_pred = model.predict(X_test_vec)

        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        results.append({
            "Model": name,
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1_Score": round(f1, 4)
        })

        print(f"\n--- Đánh giá mô hình: {name} trên tập Test ---")
        print(f"Precision: {prec:.4f} | Recall: {rec:.4f} | F1-Score: {f1:.4f}")
        print("Confusion Matrix (Hàng: Thực tế, Cột: Dự đoán):")
        print(confusion_matrix(y_test, y_pred))

        # Ưu tiên F1-Score (cân bằng giữa Precision và Recall)
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model

    # Lưu mô hình tốt nhất
    best_model_path = os.path.join(MODEL_DIR, "sms_model.pkl")
    best_vec_path = os.path.join(MODEL_DIR, "sms_vectorizer.pkl")

    joblib.dump(best_model, best_model_path)
    joblib.dump(vectorizer, best_vec_path)
    print(f"\n[OK] Đã lưu mô hình SMS tốt nhất ({best_model_name}, F1={best_f1:.4f}) vào: {best_model_path}")
    print(f"[OK] Đã lưu Vectorizer vào: {best_vec_path}")

    # Xuất báo cáo CSV
    comparison_csv = os.path.join(REPORT_DIR, "sms_model_comparison.csv")
    pd.DataFrame(results).to_csv(comparison_csv, index=False, encoding="utf-8")
    print(f"[OK] Đã lưu kết quả đối sánh vào: {comparison_csv}")

    return best_model_name, best_f1

if __name__ == "__main__":
    train_and_evaluate_sms()
