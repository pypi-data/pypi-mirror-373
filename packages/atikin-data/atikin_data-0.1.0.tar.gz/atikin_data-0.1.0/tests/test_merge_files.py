from atikin_data import merge_files
import pandas as pd
import os

def test_merge_files(tmp_path):
    f1 = tmp_path / "data1.csv"
    f2 = tmp_path / "data2.csv"

    pd.DataFrame({"A": [1,2]}).to_csv(f1, index=False)
    pd.DataFrame({"A": [3,4]}).to_csv(f2, index=False)

    out = tmp_path / "merged.csv"
    merge_files([str(f1), str(f2)], str(out))

    df = pd.read_csv(out)
    assert len(df) == 4
