import pandas as pd

def quick_summary(file_path: str):
    """
    Quickly summarize a dataset with row/column count, column names, and data types.
    Supports CSV and Excel.
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),  # ✅ Add this line
        "dtypes": df.dtypes.astype(str).to_dict()
    }
    return summary
