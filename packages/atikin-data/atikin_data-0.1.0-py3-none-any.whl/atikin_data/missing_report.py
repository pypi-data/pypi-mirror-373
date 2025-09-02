import pandas as pd

def missing_report(file_path: str):
    """Report missing values per column."""
    df = pd.read_csv(file_path)
    report = {col: int(df[col].isnull().sum()) for col in df.columns}
    return report
