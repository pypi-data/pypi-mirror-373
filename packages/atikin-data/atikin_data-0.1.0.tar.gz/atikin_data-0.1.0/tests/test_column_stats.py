from atikin_data import column_stats
import pandas as pd

def test_column_stats(tmp_path):
    file = tmp_path / "data.csv"
    pd.DataFrame({"A": [1,2,3,4], "B": [10,20,30,40]}).to_csv(file, index=False)

    stats = column_stats(str(file))
    assert stats["A"]["min"] == 1.0
    assert stats["B"]["max"] == 40.0
