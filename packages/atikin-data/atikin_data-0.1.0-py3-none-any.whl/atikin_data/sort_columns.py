import pandas as pd

def sort_columns(file_path: str, column: str, ascending: bool = True, output_file: str = None):
    """
    Sort dataset based on a column.
    """
    df = pd.read_csv(file_path)
    sorted_df = df.sort_values(by=column, ascending=ascending)
    if output_file:
        sorted_df.to_csv(output_file, index=False)
    return sorted_df
