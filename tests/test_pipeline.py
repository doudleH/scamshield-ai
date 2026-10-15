"""
ScamShield AI - Unit & Integration Tests
Kiểm thử tính toàn vẹn của các module và hợp đồng dữ liệu.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.predict_sms import predict_sms
from src.predict_url import predict_url
from src.threat_lookup import lookup_url
from src.risk_engine import build_report

def test_predict_sms_contract():
    res = predict_sms("Thong bao khoa the VCB trong 24h")
    assert "is_scam" in res
    assert "scam_probability" in res
    assert "confidence_level" in res
    assert "detected_signals" in res
    print("[PASS] test_predict_sms_contract")

def test_predict_url_contract():
    res = predict_url("http://192.168.1.1/vcb-login.xyz")
    assert "is_phishing" in res
    assert "phishing_probability" in res
    assert "features" in res
    assert "suspicious_factors" in res
    print("[PASS] test_predict_url_contract")

def test_threat_lookup_contract():
    res = lookup_url("http://example.com")
    assert "status" in res
    assert "source" in res
    assert "details" in res
    print("[PASS] test_threat_lookup_contract")

def test_build_report():
    sms_res = predict_sms("Thong bao khoa the VCB")
    url_res = predict_url("http://vcb-login.xyz")
    lookup_res = lookup_url("http://vcb-login.xyz")
    
    report = build_report(sms_res, url_res, lookup_res)
    assert report["alert_level"] in ["SAFE", "CAUTION", "DANGEROUS"]
    assert "reasons" in report
    assert "advice" in report
    assert "limitations" in report
    print("[PASS] test_build_report")

if __name__ == "__main__":
    test_predict_sms_contract()
    test_predict_url_contract()
    test_threat_lookup_contract()
    test_build_report()
    print("\n[SUCCESS] All 4 tests passed successfully!")
