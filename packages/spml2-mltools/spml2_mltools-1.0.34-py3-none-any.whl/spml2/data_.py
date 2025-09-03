import pandas as pd
from abc import ABC, abstractmethod
import copy
import warnings
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple, Dict


import numpy as np
from rich import print
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
)


from .options import Options
from .utils import (
    print_report_initial,
    local_print,
    local_print_df,
)


class TargetColumnNameNotFound(Exception):
    pass


class TargetColumnNotBinary(Exception):
    pass


class SpecialValueError(Exception):
    def __init__(self, message, details=None, friendly_message=None):
        super().__init__(message)
        self.details = details
        self.friendly_message = friendly_message or "A special value error occurred."

    def raise_with_notice(self):
        print(f"\n{self.friendly_message}")
        time.sleep(3)
        raise self

    def __str__(self):
        base = super().__str__()
        if self.details:
            return f"{base}\nDetails: {self.details}"
        return base


def assert_columns_exist(
    df: pd.DataFrame, columns: list, reason="options.categorical_cols"
):
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        err = SpecialValueError(
            f"Missing columns in DataFrame: {missing_cols}",
            details={"missing_columns": missing_cols},
            friendly_message=f"Please check your data or options {reason}!",
        )
        err.raise_with_notice()


def assert_numerical_cols(df, options):
    # Assert all numerical columns are numeric
    for col in options.numerical_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise SpecialValueError(
                f"Column '{col}' in numerical_cols is not numeric!",
                details={"column": col, "dtype": str(df[col].dtype)},
                friendly_message=f"Column '{col}' should be numeric. Please check your data and options.",
            )
    # Assert all categorical columns are object/string
    for col in options.categorical_cols:
        if not (
            pd.api.types.is_object_dtype(df[col])
            or pd.api.types.is_string_dtype(df[col])
        ):
            raise SpecialValueError(
                f"Column '{col}' in categorical_cols is not string/object!",
                details={"column": col, "dtype": str(df[col].dtype)},
                friendly_message=f"Column '{col}' should be string or object. Please check your data and options.",
            )


def set_numerical_categ_cols(df: pd.DataFrame, options: Options, output_area=None):

    df[options.target_name] = pd.to_numeric(df[options.target_name], downcast="integer")
    print("\n[DEBUG] DataFrame dtypes:")
    print(df.dtypes)
    if options.numerical_cols is None and options.categorical_cols is None:
        options.numerical_cols = df.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        options.categorical_cols = [
            col
            for col in df.columns
            if col not in options.numerical_cols and col != options.target_name
        ]
    elif options.numerical_cols is not None:
        assert_columns_exist(
            df, options.numerical_cols, reason="options.numerical_cols"
        )
        options.categorical_cols = [
            col
            for col in df.columns
            if col not in options.numerical_cols and col != options.target_name
        ]
    elif options.categorical_cols is not None:
        assert_columns_exist(
            df, options.categorical_cols, reason="options.categorical_cols"
        )
        options.numerical_cols = [
            col
            for col in df.columns
            if col not in options.categorical_cols and col != options.target_name
        ]
    print("[DEBUG] Numerical columns:", options.numerical_cols)
    print("[DEBUG] Categorical columns:", options.categorical_cols)
    print("[DEBUG] Target column:", options.target_name)
    assert_numerical_cols(df, options)
    return df, options


def prepare_data(
    df: pd.DataFrame, options: Options, output_area: Any = None
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:

    print_report_initial(df, options, output_area=output_area)
    target_name_was = options.target_name
    if options.target_name is None:
        options.target_name = df.columns[0]
        msg = f"No target column specified. Using the first column: '{options.target_name}' as target."
        warnings.warn(msg)
        print(msg)
        time.sleep(2)
    if options.target_name not in df.columns:
        msg = f"Target name '{options.target_name}' not found in DataFrame columns."
        raise TargetColumnNameNotFound(msg)
    target_values = df[options.target_name].dropna().unique()
    if len(target_values) != 2:
        if target_name_was is None:
            msg = f"Target name was not specified. Using the first column: '{options.target_name}' as target."
        target_values_str = ", ".join(map(str, (list(target_values[0:3]) + ["..."])))
        msg += f"\nTarget column '{options.target_name}' is not binary (unique values: {target_values_str}). Please provide a binary target column."
        raise TargetColumnNotBinary(msg)

    X = df.drop(options.target_name, axis=1)
    y = df[options.target_name]
    random_state = options.random_state
    if options.stratify:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=options.test_ratio,
            random_state=random_state,
            stratify=y,
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=options.test_ratio,
            random_state=random_state,
        )

    return X_train, X_test, y_train, y_test   
