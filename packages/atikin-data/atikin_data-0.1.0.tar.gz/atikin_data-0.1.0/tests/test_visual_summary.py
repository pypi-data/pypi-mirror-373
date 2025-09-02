from atikin_data import visual_summary
import pandas as pd

def test_visual_summary(tmp_path):
    file = tmp_path / "data.csv"
    df = pd.DataFrame({"Age": [20,30,25,25], "Salary":[3000,4000,3500,3600]})
    df.to_csv(file, index=False)

    # Just check no error occurs
    visual_summary(str(file))
