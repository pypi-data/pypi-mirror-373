from atikin_data import quick_preview
import pandas as pd

def test_quick_preview(tmp_path):
    file = tmp_path / "data.csv"
    pd.DataFrame({"A": [1,2,3], "B": ["x","y","z"]}).to_csv(file, index=False)

    preview = quick_preview(str(file), n=2)
    assert len(preview) == 2
    assert preview[0]["A"] == 1
