from atikin_data import missing_report
import pandas as pd
import numpy as np

def test_missing_report(tmp_path):
    file = tmp_path / "data.csv"
    pd.DataFrame({"A": [1, None, 3], "B": [4, 5, None]}).to_csv(file, index=False)

    report = missing_report(str(file))
    assert report["A"] == 1
    assert report["B"] == 1
