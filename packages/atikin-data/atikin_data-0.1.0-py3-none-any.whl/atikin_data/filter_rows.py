import pandas as pd

def filter_rows(file_path: str, condition: str, output_file: str = None):
    """
    Filter rows based on a condition string.
    Example condition: "Age > 25 and City == 'Delhi'"
    """
    df = pd.read_csv(file_path)
    filtered = df.query(condition)
    if output_file:
        filtered.to_csv(output_file, index=False)
    return filtered
