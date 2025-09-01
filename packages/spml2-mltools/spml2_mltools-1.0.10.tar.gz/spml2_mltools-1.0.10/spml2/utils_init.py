from pathlib import Path
import pandas as pd
from sklearn.datasets import load_breast_cancer

from spml2.parque_utils import df_to_stata


def get_example_data() -> pd.DataFrame:
    """
    Loads the breast cancer dataset from sklearn and returns it as a pandas DataFrame.
    The target column is named 'target'.
    """
    data = load_breast_cancer(as_frame=True)
    df = data.frame
    return df


def create_example_files(folder: str = "input") -> None:
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    df_to_stata(get_example_data(), folder / "example.dta")
