from atikin_data import filter_rows
import pandas as pd

def test_filter_rows(tmp_path):
    file = tmp_path / "data.csv"
    df = pd.DataFrame({"Age": [20,30,25], "City":["Delhi","Mumbai","Delhi"]})
    df.to_csv(file, index=False)

    result = filter_rows(str(file), "Age > 25")
    assert len(result) == 1
    assert result.iloc[0]["Age"] == 30
