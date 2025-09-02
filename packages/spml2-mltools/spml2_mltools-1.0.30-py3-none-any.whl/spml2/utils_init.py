from pathlib import Path
import pandas as pd
from sklearn.datasets import load_breast_cancer

from .parque_utils import df_to_stata


def get_example_data() -> pd.DataFrame:
    data = load_breast_cancer(as_frame=True)
    df = data.frame
    return df


def create_example_files(folder: str = "input") -> None:
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    file_name = folder / "example.dta"
    if not file_name.exists():
        print(f"Creating example data file: {file_name}")
        df_to_stata(get_example_data(), file_name)
