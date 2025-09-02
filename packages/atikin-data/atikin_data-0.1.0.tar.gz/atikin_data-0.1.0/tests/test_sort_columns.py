from atikin_data import sort_columns
import pandas as pd

def test_sort_columns(tmp_path):
    file = tmp_path / "data.csv"
    df = pd.DataFrame({"Age": [30,20,25]})
    df.to_csv(file, index=False)

    sorted_df = sort_columns(str(file), "Age")
    assert list(sorted_df["Age"]) == [20,25,30]
