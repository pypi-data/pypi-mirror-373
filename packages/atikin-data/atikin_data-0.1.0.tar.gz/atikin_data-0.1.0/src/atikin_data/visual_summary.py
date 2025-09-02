import pandas as pd
import matplotlib.pyplot as plt

def visual_summary(file_path: str, numeric_columns: list = None):
    """
    Generate visual summary for numeric columns.
    Displays histogram for each numeric column.
    """
    df = pd.read_csv(file_path)
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include="number").columns.tolist()

    for col in numeric_columns:
        plt.figure(figsize=(6,4))
        df[col].hist(bins=10)
        plt.title(f"{col} distribution")
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.show()
