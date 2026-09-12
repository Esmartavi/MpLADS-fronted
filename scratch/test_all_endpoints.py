import os
import sys
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== TESTING BHARAT-DRISHTI BACKEND ENDPOINTS ===")

endpoints = [
    ("/docs", 200, "Swagger Docs"),
    ("/api/auth/options", 200, "Auth Options"),
    ("/api/kpis", 200, "Executive KPIs"),
    ("/api/map/states", 200, "Map States"),
    ("/api/map/districts?state=Uttar%20Pradesh", 200, "Map Districts"),
    ("/api/flags?page_size=5", 200, "Flags Feed"),
    ("/api/audit", 200, "Audit Ledger (Supabase Cloud)"),
    ("/api/benford/summary", 200, "Benford Summary"),
    ("/api/benford/distribution", 200, "Benford Distribution"),
    ("/api/vendors/leaderboard?limit=10", 200, "Vendor Leaderboard"),
    ("/api/vendors/network?top_n=10", 200, "Vendor Network Graph"),
    ("/api/image-forensics/results", 200, "Forensics Results"),
    ("/api/explain/models", 200, "LLM Models Info"),
    ("/api/explain/health", 200, "LLM Health"),
]

for url, expected_status, label in endpoints:
    try:
        res = client.get(url)
        status_ok = res.status_code == expected_status
        print(f"[{'PASS' if status_ok else 'FAIL'}] {label:35s} ({url[:30]:30s}) -> Status {res.status_code}")
        if not status_ok:
            print("   Error detail:", res.text[:200])
    except Exception as e:
        print(f"[ERROR] {label} ({url}) -> Exception: {e}")

# Test sample work ID from flags
try:
    flags_res = client.get("/api/flags?page_size=1")
    if flags_res.status_code == 200:
        data = flags_res.json()
        items = data.get("items", [])
        if items:
            sample_id = items[0].get("work_id")
            print(f"\nTesting work endpoints with ID: {sample_id}")
            w_res = client.get(f"/api/work/{sample_id}")
            print(f"[{'PASS' if w_res.status_code == 200 else 'FAIL'}] Work Details -> Status {w_res.status_code}")
            
            print(f"Testing LLM Explain endpoint for work ID: {sample_id}")
            llm_res = client.get(f"/api/explain/work/{sample_id}")
            print(f"[{'PASS' if llm_res.status_code == 200 else 'FAIL'}] LLM Explain -> Status {llm_res.status_code}")
            if llm_res.status_code == 200:
                print("   Verdict:", llm_res.json().get("explanation", {}).get("severity_verdict"))
                print("   Summary:", llm_res.json().get("explanation", {}).get("case_summary")[:120], "...")
except Exception as e:
    print(f"[ERROR] Individual work test error: {e}")
