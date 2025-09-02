import pandas as pd

def column_stats(file_path: str):
    """Get min, max, mean for numeric columns."""
    df = pd.read_csv(file_path)
    stats = {}
    for col in df.select_dtypes(include="number").columns:
        stats[col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
        }
    return stats
