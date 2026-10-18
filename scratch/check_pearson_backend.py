import urllib.request
import json

def test():
    try:
        url = "http://127.0.0.1:8000/api/statistics/correlation"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print("--- /api/statistics/correlation ---")
            print("available:", data.get("available"))
            print("sample_size:", data.get("sample_size"))
            print("start_year:", data.get("start_year"), "end_year:", data.get("end_year"))
            print("variables:", data.get("variables"))
            print("pearson_matrix keys:", list(data.get("pearson_matrix", {}).keys()))
            print("\nPearson matrix (GDP_Growth row):")
            print(json.dumps(data.get("pearson_matrix", {}).get("GDP_Growth"), indent=2))
            print("\nPearson matrix (Full 6x6):")
            matrix_dict = data.get("pearson_matrix", {})
            vars_list = data.get("variables", [])
            for v1 in vars_list:
                row_vals = [f"{matrix_dict[v1][v2]:.4f}" if matrix_dict[v1][v2] is not None else "N/A" for v2 in vars_list]
                print(f"{v1:<25}: {row_vals}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
