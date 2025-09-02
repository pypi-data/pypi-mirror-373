import pandas as pd

def quick_preview(file_path: str, n: int = 5):
    """Preview first n rows of dataset."""
    df = pd.read_csv(file_path)
    preview = df.head(n).to_dict(orient="records")
    return preview
