import urllib.request
import json
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def verify_dynamic_years():
    print("==================================================")
    print("VERIFYING DYNAMIC YEAR-RANGE HANDLING")
    print("==================================================")

    # 1. Project Info API
    proj = get("/api/project")
    print("1. GET /api/project:")
    print(f"   min_year: {proj.get('min_year')}, max_year: {proj.get('max_year')}")
    print(f"   observation_count: {proj.get('observation_count')}")
    print(f"   year_range: {proj.get('year_range')}")

    assert proj.get('min_year') is not None
    assert proj.get('max_year') is not None
    assert proj.get('observation_count') is not None
    assert proj.get('year_range', {}).get('range_str') == f"{proj.get('min_year')}–{proj.get('max_year')}"

    # 2. Dataset API
    ds = get("/api/dataset")
    print("\n2. GET /api/dataset:")
    print(f"   start_year: {ds.get('start_year')}, end_year: {ds.get('end_year')}")
    print(f"   observation_count: {ds.get('observation_count')}")

    records = ds.get("data", [])
    years = [r["Year"] for r in records if "Year" in r]
    min_calc = min(years)
    max_calc = max(years)
    n_calc = len(years)

    assert ds.get('start_year') == min_calc
    assert ds.get('end_year') == max_calc
    assert ds.get('observation_count') == n_calc
    print(f"   [OK] Data-driven calculation confirmed: {min_calc}–{max_calc} (n={n_calc})")

    # 3. Analysis Current API
    cur = get("/api/analysis/current")
    print("\n3. GET /api/analysis/current:")
    print(f"   start_year: {cur.get('start_year')}, end_year: {cur.get('end_year')}")
    print(f"   observation_count: {cur.get('observation_count')}")

    assert cur.get('start_year') == min_calc
    assert cur.get('end_year') == max_calc
    assert cur.get('observation_count') == n_calc

    # 4. Check consistency across all analysis endpoints
    desc = get("/api/statistics/descriptive")
    dist = get("/api/statistics/distribution")
    corr = get("/api/statistics/correlation")
    reg = get("/api/statistics/regression")

    print("\n4. Checking Consistency Across All Endpoints:")
    endpoints_meta = [
        ("Descriptive", desc.get('start_year'), desc.get('end_year'), desc.get('sample_size')),
        ("Distribution", dist.get('start_year'), dist.get('end_year'), dist.get('sample_size')),
        ("Correlation", corr.get('start_year'), corr.get('end_year'), corr.get('sample_size')),
        ("Regression", reg.get('start_year'), reg.get('end_year'), reg.get('sample_size')),
    ]

    for name, sy, ey, n in endpoints_meta:
        print(f"   {name:<15}: {sy}–{ey} (n={n})")
        assert sy == min_calc, f"{name} start_year mismatched!"
        assert ey == max_calc, f"{name} end_year mismatched!"
        assert n == n_calc, f"{name} sample_size mismatched!"

    print("\n==================================================")
    print("ALL YEAR-RANGE DYNAMIC VERIFICATIONS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    verify_dynamic_years()
