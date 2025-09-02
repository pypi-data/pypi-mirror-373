import subprocess
import time
import os
from pathlib import Path
import pandas as pd
import random
import string
import joblib
from typing import Any

from .options import Options


def local_print(*args, **kwargs):

    if "output_area" in kwargs:
        output_area = kwargs["output_area"]
    else:
        output_area = None
    if output_area is not None:
        output_area.text(" ".join(map(str, args)))
    print(" ".join(map(str, args)))


def local_print_df(*args, **kwargs):
    if "output_area" in kwargs:
        output_area = kwargs["output_area"]
    else:
        output_area = None
    # If a DataFrame is among args, show as table
    import pandas as pd

    shown = False
    try:
        for arg in args:
            if output_area is not None and isinstance(arg, pd.DataFrame):

                output_area.dataframe(arg)
                shown = True
            elif output_area is not None and isinstance(arg, pd.Series):
                output_area.dataframe(arg.to_frame())
                shown = True
        if not shown and output_area is not None:
            output_area.text(" ".join(map(str, args)))
        print(" ".join(map(str, args)))
    except Exception as e:
        return local_print(*args, output_area=output_area)


def name_format_pip_freeze(options: Options):
    username = os.environ.get("USERNAME", "User")
    output_folder = options.output_folder
    return (
        Path(output_folder) / f"requirements_freeze_{username}_{int(time.time())}.txt"
    )


def save_pip_freeze(options: Options):
    file_name = name_format_pip_freeze(options)
    try:
        result = subprocess.run(
            ["pip", "freeze"], capture_output=True, text=True, check=True
        )
        with open(file_name, "w") as f:
            f.write(result.stdout)
        print(f"Saved pip freeze to {file_name}")
    except Exception as e:
        print(f"Error running pip freeze: {e}")


def results_report(results, df, options, output_area=None, plot_area=None, save=True):
    # 5. Convert results to DataFrame
    results_df = pd.DataFrame(results)
    print(
        results_df[["Model", "ROC AUC", "F1 Score", "duration"]].sort_values(
            "ROC AUC", ascending=False
        )
    )
    best_model_result = results_df.loc[results_df["ROC AUC"].idxmax()]
    local_print(
        f"\n   Best Model: {best_model_result['Model']} (ROC AUC: {best_model_result['ROC AUC']:.4f})",
        output_area=output_area,
    )
    # local_print("\Detailed report:", output_area=output_area)
    report = pd.DataFrame(best_model_result["Classification Report"])
    print(results_df)
    print(report)

    if save:
        save_results(
            df, "Together", results_df, best_model_result, report, options=options
        )


def check_cols(_df, options):
    cols = _df.columns

    def check(x: str):
        return x in cols

    if options.numerical_cols is None:
        return
    res = [y for y in options.numerical_cols if not check(y)]
    if res:
        msg = f"Some columns Not found ! {res}"
        raise ValueError(msg)


def get_data(options: Options) -> pd.DataFrame:
    if options.test_mode:
        df = get_test_data(options)
    else:
        df = get_large_data(options)
    check_cols(df, options)
    return df


def parque_not_exist(f: Path):
    parquet_file_name = f.with_suffix(".parquet")  # Correct way to change the suffix
    return not parquet_file_name.exists()


def create_parque_files_for_folder(folder):
    files = os.listdir(folder)
    files = [Path(folder) / x for x in files if Path(x).suffix == ".dta"]
    files = [x for x in files if parque_not_exist(x)]
    if not files:
        print("All files in this folder already have a parquet file!")
        return
    print(files)
    for file in files:
        df = pd.read_stata(file)
        p_file = file.with_suffix(".parquet")
        save_df_to_parquet(df, p_file)


def initial_data_check(options: Options):
    print(
        "initial check for data formats. This will create Parquet file for stata files"
    )
    create_parque_files_for_folder(options.root)


def save_df_to_parquet(df, filepath, compression="snappy"):
    try:
        df.to_parquet(filepath, engine="pyarrow", compression=compression)
        print(f"DataFrame successfully saved to {filepath}")
    except Exception as e:
        print(f"Error saving DataFrame to Parquet: {e}")


def get_original_data(options: Options):
    real_df_path = options.real_df_path
    if real_df_path.suffix == ".dta":
        df = pd.read_stata(real_df_path)
    elif real_df_path.suffix == ".parquet":
        df = pd.read_parquet(real_df_path, engine="pyarrow")
    else:
        raise ValueError("Original file format not expected")
    return df


def get_test_data(options: Options) -> pd.DataFrame:
    test_file_name = Path(options.test_file_name)
    if not test_file_name.exists():
        create_test_df(options)
    try:
        df = pd.read_parquet(test_file_name, engine="pyarrow")
        return df
    except Exception as e:
        print(f"Error reading Parquet file: {e}")
        raise


def get_large_data(options: Options) -> pd.DataFrame:
    real_df_path = options.real_df_path
    suffix = real_df_path.suffix.lower()
    try:
        if suffix == ".dta":
            df = pd.read_stata(real_df_path)
        elif suffix == ".parquet":
            df = pd.read_parquet(real_df_path, engine="pyarrow")
        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(real_df_path)
        elif suffix == ".csv":
            df = pd.read_csv(real_df_path)
        else:
            raise ValueError(
                "Only accepts Stata (.dta), Parquet (.parquet), Excel (.xlsx, .xls), or CSV (.csv) file formats!"
            )
        return df
    except Exception as e:
        print(f"Error reading data file: {e}")
        raise


# ================ Helper Functions ======================
def create_test_df(options: Options) -> None:
    df = get_original_data(options)
    if options.test_df_size >= len(df):
        df2 = df
    else:
        df2 = df.sample(options.test_df_size)
    print("[creating test df]", options.test_file_name)
    save_df_to_parquet(df2, options.test_file_name)


def get_caches_folder(options):
    dir: Path = options.output_folder / "caches"
    dir.mkdir(parents=True, exist_ok=True)
    return dir


# -- name formats
def name_format_general(type: str, name: str, options: Options):
    dir: Path = get_caches_folder(options)
    name = dir / f"{type}-{name}"
    if ".joblib" not in str(name):
        name = Path(f"{name}.joblib")
    return name


def name_format_metrics(name: str, options: Options):
    return name_format_general("metrics", name, options)


def name_format_model(name: str, options: Options):
    return name_format_general("model", name, options)


# --save model
def save_model(value: Any, name, options: Options) -> None:
    name = name_format_model(name, options)
    try:
        joblib.dump(value, name)
    except Exception as e:
        print(f"Error saving model: {e}")


# -- save metrics
def save_metrics(value: Any, name, options: Options) -> None:
    name = name_format_metrics(name, options)
    try:
        joblib.dump(value, name)
    except Exception as e:
        print(f"Error saving metrics: {e}")


# -- load metrics
def load_metrics_cache(name, options: Options) -> None:
    name = name_format_metrics(name, options)
    if not name.exists():
        raise FileNotFoundError(f"Metrics file not found: {name}")
    return joblib.load(name)


# -- load model
def load_model_cache(name, options: Options) -> None:
    name = name_format_model(name, options)
    if not name.exists():
        raise FileNotFoundError(f"Model Result file not found: {name}")
    print("<Returning Cache>")
    return joblib.load(name)


def print_report_initial(df, options: Options, output_area=None) -> None:
    rows, cols = df.shape
    test_str = (
        "Test mode is open" if options.test_mode else "Full operational mode is active!"
    )
    file_name = options.test_file_name if options.test_mode else options.real_df_path
    t = f"""
=================================================================
    Working mode     : {test_str}
    File to be used : {file_name}
    Rows  : {rows}
    Columns  : {cols}
    test ratio :  = {options.test_ratio}
=================================================================
    """
    local_print(t, output_area=output_area)
    local_print_df(df.head(), output_area=output_area)
    time.sleep(1)


def name_format_estimator(name: str, _df: pd.DataFrame, options: Options):
    username = os.environ.get("USERNAME", "User")
    _hash = options.hash()
    return name_format_estimator_helper(_df, name + f"-{_hash}", options, username)


def name_format_estimator_other(
    name: str,
    _df: pd.DataFrame,
    options: Options,
    username="User",
):
    return name_format_estimator_helper(_df, name, options, username)


def name_format_estimator_helper(
    _df: pd.DataFrame, name: str, options: Options, username: str
):
    rows, cols = _df.shape
    stem = options.real_df_path.stem
    name_f = f"REAL-{stem}-{name}-R{rows}-C{cols}-U{username}"
    if options.debug:
        name_f = f"DEBUG-{stem}-{name}-R{rows}-C{cols}-U{username}"
        return name_f
    if options.test_mode:
        name_f = f"TEST-{stem}-{name}-R{rows}-C{cols}-U{username}"
    return name_f


def name_format(options: Options, df: pd.DataFrame, model_name: str, _name: str = "_"):
    rows, cols = df.shape
    username = os.environ.get("USERNAME", "User")
    stem = options.real_df_path.stem
    if options.debug:
        mode = "debug"
    elif options.test_mode:
        mode = "test"
    else:
        mode = "Real"
    return f"{username}-{mode}-{model_name}-{_name}-Data_{stem}-R{rows}-C{cols}.xlsx"


def random_string(length=5):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def save_excel(_df: pd.DataFrame, _name: Path):
    _name_hash = _name.with_stem(f"{_name.stem}_{random_string()}")
    try:
        _df.to_excel(_name)
    except Exception as e:
        print(f"Error: {e}")
        _df.to_excel(_name_hash)
        print(f"file '{_name_hash}' saved.")


def save_results(
    df: pd.DataFrame,
    model_name: str,
    results_df: pd.DataFrame,
    best_model_result: pd.DataFrame,
    report: pd.DataFrame,
    options: Options,
):
    items = [results_df, best_model_result, report]
    names = ["results_df", "best_model_result", "report"]
    for _df, _name in zip(items, names):
        nf = name_format(options, df, model_name, _name)
        file_name = options.output_folder / nf
        save_excel(_df, file_name)


def save_results_individual(
    df: pd.DataFrame, model_name, results_df: pd.DataFrame, options: Options
):
    for col in results_df.columns:
        if results_df[col].dtype == "object":
            results_df[col] = results_df[col].apply(
                lambda x: str(x) if isinstance(x, (list, dict, tuple)) else x
            )
    nf = name_format(options, df, model_name)
    file_name = options.output_folder / nf
    save_excel(results_df, file_name)


def limited_models(models_: dict, _name: str) -> dict:
    return dict([(_name, models_[_name])])
