import os
from pathlib import Path
import pandas as pd


def df_to_stata(df, file_path, version=118) -> None:
    df.columns = [x.strip().replace(" ", "_") for x in df.columns]
    df.to_stata(file_path, version=version, write_index=False)


def parque_not_exist(f: Path) -> bool:
    parquet_file_name = f.with_suffix(".parquet")
    return not parquet_file_name.exists()


def create_parque_files_for_folder(folder: str | Path) -> None:
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


def save_df_to_parquet(
    df: pd.DataFrame, filepath: Path, compression: str = "snappy"
) -> None:
    try:
        df.to_parquet(filepath, engine="pyarrow", compression=compression)
        print(f"DataFrame successfully saved to {filepath}")
    except Exception as e:
        print(f"Error saving DataFrame to Parquet: {e}")
