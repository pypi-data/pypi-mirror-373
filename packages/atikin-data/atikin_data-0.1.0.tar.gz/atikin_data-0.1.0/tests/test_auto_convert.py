from atikin_data import auto_convert
import pandas as pd
import os

def test_auto_convert(tmp_path):
    f1 = tmp_path / "data.csv"
    f2 = tmp_path / "data.json"

    pd.DataFrame({"A": [1,2], "B": [3,4]}).to_csv(f1, index=False)

    auto_convert(str(f1), str(f2))
    assert os.path.exists(f2)
