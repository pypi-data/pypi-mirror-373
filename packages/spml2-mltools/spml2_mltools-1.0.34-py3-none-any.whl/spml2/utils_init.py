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


def get_example_data2():
    import pandas as pd
    import numpy as np
    from sklearn.datasets import load_breast_cancer

    # Load breast cancer data
    data = load_breast_cancer(as_frame=True)
    df = data.frame
    np.random.seed(42)
    df["random_cat"] = np.random.choice(["A", "B", "C"], size=len(df))
    print(df[["random_cat"]].head())
    # df["mean radius"] = df["mean radius"].astype(str)
    return df
