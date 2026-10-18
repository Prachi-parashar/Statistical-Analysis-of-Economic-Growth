import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        return data

def post(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, data=b"", method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        return data

def test_all():
    print("1. Testing Health...")
    health = get("/api/health")
    assert health.get("status") == "ok"
    print("  [OK] Health:", health)

    print("\n2. Testing Project Info...")
    proj = get("/api/project")
    print("  [OK] Project title:", proj.get("title"))

    print("\n3. Testing Dataset API...")
    ds = get("/api/dataset")
    assert ds.get("available") == True
    print(f"  [OK] Dataset rows: {len(ds.get('data', []))}, period: {ds.get('data', [])[0]['Year']} to {ds.get('data', [])[-1]['Year']}")

    print("\n4. Testing Descriptive Statistics...")
    desc = get("/api/statistics/descriptive")
    assert desc.get("available") == True
    print(f"  [OK] Descriptive stats variables: {len(desc.get('data', []))}")

    print("\n5. Testing Distribution Analysis...")
    dist = get("/api/statistics/distribution")
    assert dist.get("available") == True
    print(f"  [OK] Distribution analysis variables: {len(dist.get('data', []))}")

    print("\n6. Testing Correlation Analysis...")
    corr = get("/api/statistics/correlation")
    assert corr.get("available") == True
    print(f"  [OK] Pearson correlation pairs: {len(corr.get('data', []))}")

    print("\n7. Testing Regression Analysis...")
    reg = get("/api/statistics/regression")
    assert reg.get("available") == True
    print(f"  [OK] Regression predictors: {len(reg.get('data', []))}")

    print("\n8. Testing Regression Diagnostics...")
    diag = get("/api/statistics/diagnostics")
    assert diag.get("available") == True
    print(f"  [OK] Diagnostic tests: {len(diag.get('data', []))}")

    print("\n9. Testing Interpretations...")
    interp = get("/api/statistics/interpretations")
    assert interp.get("available") == True
    print("  [OK] Key findings count:", len(interp.get("key_findings", [])))

    print("\n10. Testing Current Analysis Metadata...")
    cur = get("/api/analysis/current")
    print(f"  [OK] Current analysis_id: {cur.get('analysis_id')}, country: {cur.get('country')}, range: {cur.get('start_year')} to {cur.get('end_year')}")

    print("\n11. Testing Run Analysis (1st Run)...")
    run1 = post("/api/analysis/run")
    assert run1.get("success") == True
    id1 = run1.get("analysis_id")
    print(f"  [OK] Run 1 success! analysis_id = {id1}")

    print("\n12. Testing Run Analysis (2nd Run)...")
    run2 = post("/api/analysis/run")
    assert run2.get("success") == True
    id2 = run2.get("analysis_id")
    print(f"  [OK] Run 2 success! analysis_id = {id2}")
    assert id1 != id2, "Analysis IDs should be unique per run!"
    print("  [OK] Unique analysis IDs verified across runs!")

    print("\n13. Testing Current Analysis after Run 2...")
    cur2 = get("/api/analysis/current")
    assert cur2.get("analysis_id") == id2
    print(f"  [OK] Current analysis correctly updated to {id2}")

    print("\n==============================================")
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==============================================")

if __name__ == "__main__":
    test_all()
