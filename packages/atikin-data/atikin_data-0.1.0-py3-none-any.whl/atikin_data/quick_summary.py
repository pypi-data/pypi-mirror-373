import pandas as pd

def quick_summary(file_path: str):
    """Show quick summary of dataset (rows, columns, column names, dtypes)."""
    df = pd.read_csv(file_path)
    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }
    return summary
