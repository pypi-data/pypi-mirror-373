import pandas as pd

def merge_files(file_list, output="merged.csv"):
    """Merge multiple CSV files into one CSV file."""
    dfs = [pd.read_csv(f) for f in file_list]
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv(output, index=False)
    return output
