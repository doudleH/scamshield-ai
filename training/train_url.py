"""
ScamShield AI - Training Script for URL Phishing (Real Data: PhishVN v3.1.0)
Huấn luyện mô hình phân loại URL lừa đảo:
- Sử dụng bộ dữ liệu PhishVN thực (53k+ URL Việt Nam)
- Dùng đặc trưng bóc tách từ URL thô (16 đặc trưng hình thái)
  Lưu ý: Dataset PhishVN chứa chủ yếu domain-only URL nên đặc trưng rất phù hợp
- So sánh các mô hình: LogisticRegression, DecisionTree, RandomForest
- Đánh giá bằng Precision, Recall, F1-Score, Confusion Matrix
- Lưu mô hình vào thư mục models/
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score

# Thêm đường dẫn src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Đường dẫn dataset PhishVN (thực tế)
PHISHVN_PATH = os.path.join(
    DATA_DIR,
    "PhishVN A Time-Stamped Vietnamese URL Phishing Dat",
    "PhishVN_v3.1.0_open",
    "data",
    "dataset_url.csv"
)

# Đường dẫn dataset URL mẫu (fallback)
SAMPLE_URL_PATH = os.path.join(DATA_DIR, "sample_urls.csv")


def create_synthetic_url_sample_data(filepath: str):
    """Tạo bộ dữ liệu URL mẫu ban đầu để kiểm thử pipeline."""
    samples = [
        ("http://192.168.1.1/vcb-digibank-login.html", "phishing"),
        ("http://vcb-security-verify.xyz/login.php?user=admin", "phishing"),
        ("https://vietinbank-online-ebanking.top/otp-verify", "phishing"),
        ("http://mbbank-tri-an-qua-tang.cc/nhan-thuong", "phishing"),
        ("http://phatnguoi-canhsat-giaothong.site/nop-phat", "phishing"),
        ("http://bit.ly/nhan-qua-sh-2026", "phishing"),
        ("http://portal-account-update-24h.click/security", "phishing"),
        ("http://shopee-voucher-500k-free.vip/claim", "phishing"),
        ("https://www.vietcombank.com.vn", "benign"),
        ("https://vcbdigibank.vietcombank.com.vn", "benign"),
        ("https://online.mbbank.com.vn", "benign"),
        ("https://chinhphu.vn", "benign"),
        ("https://dantri.com.vn/xa-hoi.htm", "benign"),
        ("https://vnexpress.net/thoi-su", "benign"),
        ("https://github.com/vuthainguyen1602/phishvn", "benign"),
        ("https://google.com.vn/search?q=sic+ai", "benign")
    ]
    df = pd.DataFrame(samples, columns=["url", "label"])
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"Đã tạo dữ liệu mẫu kiểm thử URL tại: {filepath}")
    return df


def extract_phishvn_features(df: pd.DataFrame) -> np.ndarray:
    """
    Trích xuất đặc trưng từ các cột có sẵn trong PhishVN dataset.
    Bộ đặc trưng này được tính từ URL/domain trong dataset (domain-only format).
    Kết hợp với suspicious_tld flag từ TLD list trong dataset.
    """
    # Sử dụng các đặc trưng số học đã có trong dataset PhishVN
    # Bổ sung thêm một số đặc trưng tính từ URL
    from urllib.parse import urlparse
    import re

    SUSPICIOUS_TLDS = {
        "xyz", "top", "club", "tk", "ml", "ga", "cf", "gq", "work", "date",
        "racing", "men", "party", "click", "site", "online", "live", "vip", "cc",
        "pw", "ru", "ws", "info", "biz", "mobi"
    }

    SUSPICIOUS_KEYWORDS = [
        "login", "signin", "verify", "secure", "account", "banking", "ebank", "digibank",
        "otp-verify", "xac-minh", "cap-nhat", "truy-cap",
        "reward", "voucher", "nhan-thuong", "qua-tang", "khuyenmai",
        "phat-nguoi", "kiem-tien", "nhanthuong"
    ]

    feature_matrix = []

    for _, row in df.iterrows():
        url = str(row.get('url', '') or '')
        if not url.startswith('http'):
            url = 'http://' + url

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or ''
            path = parsed.path or ''
            query = parsed.query or ''
        except Exception:
            hostname = ''
            path = ''
            query = ''

        url_len = float(row.get('url_len', len(url)) or len(url))
        num_dots = float(row.get('num_dots', url.count('.')) or url.count('.'))
        num_subdomains = float(row.get('num_subdomains', 0) or 0)
        has_ip = float(row.get('has_ip', 0) or 0)
        has_at = float(row.get('has_at', 0) or 0)
        susp_tld = float(row.get('suspicious_tld', 0) or 0)

        # Thêm đặc trưng bổ sung từ URL
        tld = hostname.split('.')[-1].lower() if '.' in hostname else ''
        is_susp_tld2 = 1.0 if tld in SUSPICIOUS_TLDS else 0.0
        # Combine both TLD signals
        susp_tld_final = max(susp_tld, is_susp_tld2)

        num_hyphens = float(hostname.count('-'))
        hostname_len = float(len(hostname))
        digits_in_hostname = float(sum(c.isdigit() for c in hostname))
        digits_ratio = digits_in_hostname / max(1, hostname_len)

        # Suspicious keyword count (whole-word matching)
        suspicious_kw = 0
        low_url = url.lower()
        for kw in SUSPICIOUS_KEYWORDS:
            if kw in low_url:
                idx = low_url.find(kw)
                before = low_url[idx-1] if idx > 0 else '-'
                after = low_url[idx + len(kw)] if idx + len(kw) < len(low_url) else '-'
                if not before.isalnum() and not after.isalnum():
                    suspicious_kw += 1
        kw_count = float(suspicious_kw)

        shortener_domains = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd"}
        is_shortened = 1.0 if hostname.lower() in shortener_domains else 0.0

        # Feature vector (12 features) - has_path neutralized to 0 to match predict_url.py
        vec = [
            url_len,         # URL length (from dataset)
            num_dots,        # Number of dots
            num_subdomains,  # Number of subdomains
            has_ip,          # Has IP address
            has_at,          # Has @ symbol
            susp_tld_final,  # Suspicious TLD
            num_hyphens,     # Hyphens in hostname
            hostname_len,    # Hostname length
            digits_ratio,    # Digits ratio in hostname
            kw_count,        # Suspicious keyword count
            is_shortened,    # Is shortened URL
            0.0,             # has_path: neutralized (dataset=domain-only, prediction=full URL)
        ]
        feature_matrix.append(vec)

    return np.array(feature_matrix, dtype=np.float64)


def load_phishvn_dataset():
    """
    Tải và chuẩn bị dữ liệu từ PhishVN v3.1.0.
    Sử dụng đặc trưng từ cột dataset + bổ sung tính toán từ URL.
    """
    print(f"Đọc dataset PhishVN từ: {PHISHVN_PATH}")
    df = pd.read_csv(PHISHVN_PATH, low_memory=False)
    print(f"Dataset: {df.shape[0]} dòng | Nhãn: {df['label'].value_counts().to_dict()}")

    df = df[df['channel'] == 'url'].copy()
    df = df.dropna(subset=['url']).reset_index(drop=True)
    print(f"Sau lọc URL: {df.shape[0]} dòng")

    df['y'] = df['label'].map(lambda x: 1 if str(x).lower() == 'phishing' else 0)

    train_df = df[df['split'] == 'train'].copy().reset_index(drop=True)
    test_df  = df[df['split'] == 'test'].copy().reset_index(drop=True)

    print(f"Tập Train: {len(train_df)} | 0={sum(train_df['y']==0)}, 1={sum(train_df['y']==1)}")
    print(f"Tập Test:  {len(test_df)} | 0={sum(test_df['y']==0)}, 1={sum(test_df['y']==1)}")

    print("Trích xuất đặc trưng tập Train...")
    X_train = extract_phishvn_features(train_df)
    print("Trích xuất đặc trưng tập Test...")
    X_test  = extract_phishvn_features(test_df)

    y_train = train_df['y'].values
    y_test  = test_df['y'].values

    return X_train, X_test, y_train, y_test


def build_feature_matrix_for_prediction(urls):
    """
    Bóc tách đặc trưng từ URL thô (domain-only format) để dùng cho dự đoán runtime.
    Đồng bộ với extract_phishvn_features (12 đặc trưng).
    """
    from urllib.parse import urlparse
    import re

    SUSPICIOUS_TLDS = {
        "xyz", "top", "club", "tk", "ml", "ga", "cf", "gq", "work", "date",
        "racing", "men", "party", "click", "site", "online", "live", "vip", "cc",
        "pw", "ru", "ws", "info", "biz", "mobi"
    }

    SUSPICIOUS_KEYWORDS = [
        "login", "signin", "verify", "secure", "account", "banking", "ebank",
        "vcb", "bidv", "vietinbank", "mbbank", "techcom", "otp", "update",
        "reward", "voucher", "phat", "nhan", "xac"
    ]

    rows = []
    for url in urls:
        url = str(url)
        if not url.startswith('http'):
            url_for_parse = 'http://' + url
        else:
            url_for_parse = url

        try:
            parsed = urlparse(url_for_parse)
            hostname = parsed.hostname or ''
            path = parsed.path or ''
        except Exception:
            hostname = ''
            path = ''

        url_len = len(url)
        num_dots = url.count('.')
        parts = hostname.split('.')
        num_subdomains = max(0, len(parts) - 2) if len(parts) > 2 else 0
        has_ip = 1 if re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname) else 0
        has_at = 1 if '@' in url else 0
        tld = parts[-1].lower() if parts else ''
        susp_tld = 1 if tld in SUSPICIOUS_TLDS else 0
        num_hyphens = hostname.count('-')
        hostname_len = len(hostname)
        digits_in_hostname = sum(c.isdigit() for c in hostname)
        digits_ratio = digits_in_hostname / max(1, hostname_len)
        low_url = url.lower()
        kw_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in low_url)
        shortener_domains = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd"}
        is_shortened = 1 if hostname.lower() in shortener_domains else 0

        rows.append([
            url_len, num_dots, num_subdomains, has_ip, has_at, susp_tld,
            num_hyphens, hostname_len, digits_ratio, kw_count, is_shortened,
            float(len(path) > 0),
        ])

    return np.array(rows, dtype=np.float64)


def train_and_evaluate_url(data_path: str = None):
    print("=== BẮT ĐẦU HUẤN LUYỆN MÔ HÌNH PHISHING URL ===")

    if data_path and os.path.exists(data_path):
        print(f"Đọc dữ liệu tùy chỉnh từ: {data_path}")
        df = pd.read_csv(data_path)
        url_col   = "url"   if "url"   in df.columns else df.columns[0]
        label_col = "label" if "label" in df.columns else df.columns[1]
        y = df[label_col].map(lambda x: 1 if str(x).lower() in ['phishing', 'bad', '1', 'malicious', 'scam'] else 0).values
        X = build_feature_matrix_for_prediction(df[url_col].tolist())
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    elif os.path.exists(PHISHVN_PATH):
        X_train, X_test, y_train, y_test = load_phishvn_dataset()

    else:
        print("[CẢNH BÁO] Không tìm thấy dataset thực. Dùng dữ liệu mẫu 16 dòng để kiểm thử.")
        df = create_synthetic_url_sample_data(SAMPLE_URL_PATH)
        y = df['label'].map(lambda x: 1 if str(x).lower() in ['phishing', 'bad', '1', 'malicious', 'scam'] else 0).values
        X = build_feature_matrix_for_prediction(df['url'].tolist())
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    print(f"\nTổng kết dữ liệu:")
    print(f"  X_train shape: {X_train.shape} | 0={sum(y_train==0)}, 1={sum(y_train==1)}")
    print(f"  X_test  shape: {X_test.shape}  | 0={sum(y_test==0)}, 1={sum(y_test==1)}")

    models = {
        "LogisticRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0, random_state=42))
        ]),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, class_weight="balanced", random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=15, class_weight="balanced", n_jobs=-1, random_state=42)
    }

    best_model_name = None
    best_f1 = -1
    best_model = None
    results = []

    for name, model in models.items():
        print(f"\nHuấn luyện {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        prec = precision_score(y_test, y_pred, zero_division=0)
        rec  = recall_score(y_test, y_pred, zero_division=0)
        f1   = f1_score(y_test, y_pred, zero_division=0)

        results.append({
            "Model":     name,
            "Precision": round(prec, 4),
            "Recall":    round(rec, 4),
            "F1_Score":  round(f1, 4)
        })

        print(f"--- Kết quả mô hình URL: {name} ---")
        print(f"Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")
        print("Confusion Matrix (Hàng: Thực tế, Cột: Dự đoán):")
        print(confusion_matrix(y_test, y_pred))
        print(classification_report(y_test, y_pred, target_names=["Lành tính", "Phishing"], zero_division=0))

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model

    # Lưu mô hình tốt nhất
    best_model_path = os.path.join(MODEL_DIR, "url_model.pkl")
    joblib.dump(best_model, best_model_path)
    print(f"\n[OK] Đã lưu mô hình URL tốt nhất ({best_model_name}, F1={best_f1:.4f}) vào: {best_model_path}")

    # Lưu mapping feature extractor info (để predict_url.py dùng đúng)
    meta_path = os.path.join(MODEL_DIR, "url_model_meta.pkl")
    joblib.dump({"version": "phishvn_v2", "n_features": X_train.shape[1]}, meta_path)
    print(f"[OK] Đã lưu metadata mô hình vào: {meta_path}")

    # Xuất báo cáo CSV
    comparison_csv = os.path.join(REPORT_DIR, "url_model_comparison.csv")
    pd.DataFrame(results).to_csv(comparison_csv, index=False, encoding="utf-8")
    print(f"[OK] Đã lưu kết quả đối sánh vào: {comparison_csv}")

    return best_model_name, best_f1


if __name__ == "__main__":
    train_and_evaluate_url()
