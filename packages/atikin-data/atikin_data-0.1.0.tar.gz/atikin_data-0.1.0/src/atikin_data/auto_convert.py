import pandas as pd
import os

def auto_convert(input_file: str, output_file: str):
    """Convert CSV ⇆ Excel ⇆ JSON automatically based on extension."""
    input_ext = os.path.splitext(input_file)[1].lower()
    output_ext = os.path.splitext(output_file)[1].lower()

    if input_ext == ".csv":
        df = pd.read_csv(input_file)
    elif input_ext in [".xls", ".xlsx"]:
        df = pd.read_excel(input_file)
    elif input_ext == ".json":
        df = pd.read_json(input_file)
    else:
        raise ValueError("Unsupported input format!")

    if output_ext == ".csv":
        df.to_csv(output_file, index=False)
    elif output_ext in [".xls", ".xlsx"]:
        df.to_excel(output_file, index=False)
    elif output_ext == ".json":
        df.to_json(output_file, orient="records", indent=2, force_ascii=False)
    else:
        raise ValueError("Unsupported output format!")

    return output_file
