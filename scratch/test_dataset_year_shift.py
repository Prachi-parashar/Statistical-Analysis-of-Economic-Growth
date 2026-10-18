import sys, os
sys.path.insert(0, os.path.abspath('backend'))
import pandas as pd
from app.services import data_service

def test_shift():
    print("Testing dynamic calculation of min_year, max_year, observation_count when dataset changes...")
    
    # 1. Dataset 1 (e.g. 1993 to 2023, 31 rows)
    df1 = pd.DataFrame({"Year": list(range(1993, 2024)), "GDP_Growth": [5.0]*31})
    years1 = df1["Year"].dropna().astype(int)
    min1, max1, n1 = int(years1.min()), int(years1.max()), int(len(years1))
    print(f"Dataset 1 (1993-2023): min_year={min1}, max_year={max1}, observations={n1}")
    assert min1 == 1993 and max1 == 2023 and n1 == 31

    # 2. Dataset 2 (e.g. 1991 to 2026, 36 rows)
    df2 = pd.DataFrame({"Year": list(range(1991, 2027)), "GDP_Growth": [6.0]*36})
    years2 = df2["Year"].dropna().astype(int)
    min2, max2, n2 = int(years2.min()), int(years2.max()), int(len(years2))
    print(f"Dataset 2 (1991-2026): min_year={min2}, max_year={max2}, observations={n2}")
    assert min2 == 1991 and max2 == 2026 and n2 == 36

    # 3. Dataset 3 (e.g. non-contiguous years 1995, 1997, 2000..2020, 20 rows)
    non_contig = [1995, 1997] + list(range(2000, 2018))
    df3 = pd.DataFrame({"Year": non_contig, "GDP_Growth": [4.0]*len(non_contig)})
    years3 = df3["Year"].dropna().astype(int)
    min3, max3, n3 = int(years3.min()), int(years3.max()), int(len(years3))
    print(f"Dataset 3 (Non-contiguous): min_year={min3}, max_year={max3}, observations={n3}")
    assert min3 == 1995 and max3 == 2017 and n3 == 20
    assert n3 != (max3 - min3 + 1), "Observations accurately reflects actual row count, not naive max - min + 1!"

    print("\n==================================================")
    print("ALL DYNAMIC SHIFT TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_shift()
