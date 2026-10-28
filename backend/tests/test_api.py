import os
os.environ.pop("ANTHROPIC_API_KEY", None)
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
       b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82")


def test_health():
    assert c.get("/api/health").json()["status"] == "ok"


def test_plan():
    r = c.post("/api/planning/estimate", json={"built_area_sqft": 1500, "floors": 2, "quality": "standard"})
    j = r.json()
    assert r.status_code == 200 and j["total_cost"] > 0 and j["schedule"][0]["start_week"] == 1


def test_plan_validation():
    assert c.post("/api/planning/estimate", json={"built_area_sqft": 5}).status_code == 422


def test_valuation():
    r = c.post("/api/valuation/estimate", json={"area_sqft": 1000, "age_years": 5, "amenities": ["lift", "parking"]})
    assert r.status_code == 200 and r.json()["low"] < r.json()["estimated_value"] < r.json()["high"]


def test_safety_and_cracks_demo():
    for ep in ("safety", "cracks"):
        r = c.post(f"/api/{ep}/analyze", files={"image": ("a.png", PNG, "image/png")}, data={"notes": "x"})
        assert r.status_code == 200 and r.json()["source"] == "demo"


def test_bad_upload():
    assert c.post("/api/safety/analyze", files={"image": ("a.txt", b"hi", "text/plain")}).status_code == 415


def test_chat():
    assert "cure" in c.post("/api/assistant/chat", json={"message": "how long to cure?"}).json()["answer"].lower()
