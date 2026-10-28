"""
ScamShield AI - Module 2 (Backend & MLOps) contract tests.
Chay: python tests/test_module2.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api
from src.pii_mask import mask_pii, mask_sender
from fastapi.testclient import TestClient

# --- PII masking -------------------------------------------------------------
assert mask_pii("Lien he 0912345678 hoac 0912 345 678 nhe") == "Lien he [SĐT] hoac [SĐT] nhe"
assert mask_pii("Ma OTP cua ban la 837492") == "Ma OTP cua ban la [OTP]"
assert mask_pii("Chuyen vao STK 0123456789012 gap") == "Chuyen vao STK [SỐ_TÀI_KHOẢN] gap"
assert mask_pii("gui mail toi scam@bidv.vn") == "gui mail toi [EMAIL]"
assert mask_sender("0912345678") == "091****678"
assert mask_sender("VIETCOMBANK") == "VIETCOMBANK"

with tempfile.TemporaryDirectory() as tmp:
    api.DATA_DIR = Path(tmp)
    client = TestClient(api.app)

    # --- 2.1 Community report -------------------------------------------------
    r = client.post("/api/v1/report", json={
        "sender": "0912345678",
        "message": "Tai khoan bi khoa. Goi 0987654321 hoac nhap OTP 837492 ngay!",
        "risk_percent": 92,
        "reason": "link gia mao",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "success" and body["reported_id"]

    stored = (Path(tmp) / "reported_samples.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(stored) == 1
    rec = json.loads(stored[0])
    assert rec["masked_sender"] == "091****678"
    assert "0987654321" not in rec["message"] and "[SĐT]" in rec["message"]
    assert "837492" not in rec["message"] and "[OTP]" in rec["message"]
    assert rec["status"] == "pending_review"

    # ghi noi tiep, khong ghi de
    client.post("/api/v1/report", json={"sender": "BIDV", "message": "tin thu 2"})
    assert len((Path(tmp) / "reported_samples.jsonl").read_text(encoding="utf-8").splitlines()) == 2

    # tin nhan rong / qua dai bi tu choi o bien tin cay
    assert client.post("/api/v1/report", json={"message": ""}).status_code == 422
    assert client.post("/api/v1/report", json={"message": "x" * 2001}).status_code == 422

# --- 2.2 Rule sync ----------------------------------------------------------
c = TestClient(api.app)
r = c.get("/api/v1/rules/sync")
assert r.status_code == 200, r.text
rules = r.json()
assert rules["version"] and rules["new_emerging_malicious_domains"] and rules["new_scam_keywords"]
etag = r.headers["etag"]
assert etag.startswith('"') and len(etag) > 8

# client da co ban moi nhat -> 304, khong tai lai
assert c.get("/api/v1/rules/sync", headers={"If-None-Match": etag}).status_code == 304

# --- 2.3 Deployment contract ------------------------------------------------
assert c.get("/api/v1/health").json()["status"] == "healthy"
assert (Path(__file__).resolve().parent.parent / "Dockerfile").exists()

print("=== MODULE 2 TESTS PASSED ===")
