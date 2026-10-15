import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from src.predict_sms import predict_sms
from src.predict_url import predict_url
from src.risk_engine import build_report
from src.threat_lookup import lookup_url

print("=== SMOKE TEST: ScamShield AI Models (Real Data) ===\n")

# Test 1: Phishing SMS
sms1 = "Thong bao: Tai khoan VCB cua ban bi khoa. Truy cap http://vcb-login.xyz de xac minh trong 24h"
res1 = predict_sms(sms1)
print(f"[TEST 1] SMS phishing:")
print(f"  is_scam={res1['is_scam']}, scam_probability={res1['scam_probability']:.3f}, model={res1.get('model_type')}")
assert res1['is_scam'] == True or res1['scam_probability'] > 0.3, "FAIL: should detect phishing SMS"
print("  -> PASS")

# Test 2: Legitimate SMS
sms2 = "Ma xac thuc VCB cua ban la 589712. Khong chia se ma nay cho bat ky ai."
res2 = predict_sms(sms2)
print(f"\n[TEST 2] SMS legitimate:")
print(f"  is_scam={res2['is_scam']}, scam_probability={res2['scam_probability']:.3f}, model={res2.get('model_type')}")
print("  -> PASS (prediction returned)")

# Test 3: Phishing URL
url1 = "http://vcb-digibank-login.xyz/verify?user=admin&token=12345"
res3 = predict_url(url1)
print(f"\n[TEST 3] URL phishing:")
print(f"  is_phishing={res3['is_phishing']}, phishing_probability={res3['phishing_probability']:.3f}, model={res3.get('model_type')}")
print(f"  Suspicious factors: {res3['suspicious_factors']}")
assert res3['is_phishing'] == True or res3['phishing_probability'] > 0.3, "FAIL: should detect phishing URL"
print("  -> PASS")

# Test 4: Safe URL
url2 = "https://www.vietcombank.com.vn/dich-vu-ca-nhan"
res4 = predict_url(url2)
print(f"\n[TEST 4] URL safe:")
print(f"  is_phishing={res4['is_phishing']}, phishing_probability={res4['phishing_probability']:.3f}, model={res4.get('model_type')}")
assert res4['is_phishing'] == False, "FAIL: legitimate URL was incorrectly flagged as phishing"
print("  -> PASS (correctly identified as safe)")

# Test 5: Full report
print("\n[TEST 5] Full risk report:")
lookup = lookup_url(url1)
report = build_report(res1, res3, lookup)
print(f"  alert_level:   {report['alert_level']}")
print(f"  status_label:  {report['status_label']}")
print(f"  sms_prob:      {report.get('sms_probability', 'N/A')}")
print(f"  url_prob:      {report.get('url_probability', 'N/A')}")
print(f"  reasons count: {len(report.get('reasons', []))}")
assert report['alert_level'] in ['DANGEROUS', 'CAUTION', 'SAFE'], "FAIL: unexpected alert_level"
print("  -> PASS")

print("\n=== ALL SMOKE TESTS PASSED ===")
