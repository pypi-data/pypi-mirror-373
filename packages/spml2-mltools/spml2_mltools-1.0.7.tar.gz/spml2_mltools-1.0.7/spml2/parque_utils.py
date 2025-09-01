import os
from pathlib import Path
import pandas as pd


def df_to_stata(df, file_path, version=118):
    """
    Convert a pandas DataFrame to Stata .dta format.
    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str): Path to save the .dta file.
        version (int): Stata version (default 118 for Stata 14+).
    """
    df.columns = [x.strip().replace(" ", "_") for x in df.columns]
    df.to_stata(file_path, version=version, write_index=False)


def parque_not_exist(f: Path):
    parquet_file_name = f.with_suffix(".parquet")  # Correct way to change the suffix
    return not parquet_file_name.exists()


def create_parque_files_for_folder(folder):
    folder = Path(folder)
    files = os.listdir(folder)
    files = [Path(folder) / x for x in files if Path(x).suffix == ".dta"]
    files = [x for x in files if parque_not_exist(x)]
    if not files:
        print("All stata files already have a parquet file!")
        return
    print(files)
    for file in files:
        df = pd.read_stata(file)
        p_file = file.with_suffix(".parquet")
        save_df_to_parquet(df, p_file)


def save_df_to_parquet(df, filepath, compression="snappy"):
    """
    Saves a Pandas DataFrame to a Parquet file.
    Args:
      df: The Pandas DataFrame to save.
      filepath: The path to the Parquet file (including the .parquet extension).
      compression: The compression algorithm to use (default: 'snappy').
                   Other options include 'gzip', 'brotli', 'lz4', 'zstd', or None (no compression).
                   'snappy' is a good balance between compression ratio and speed.
    """
    try:
        df.to_parquet(filepath, engine="pyarrow", compression=compression)
        print(f"DataFrame successfully saved to {filepath}")
    except Exception as e:
        print(f"Error saving DataFrame to Parquet: {e}")
