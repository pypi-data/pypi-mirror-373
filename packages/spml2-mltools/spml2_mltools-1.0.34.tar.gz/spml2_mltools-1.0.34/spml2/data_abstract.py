from abc import ABC, abstractmethod
import time

import pandas as pd
import warnings

from .data_ import prepare_data, set_numerical_categ_cols
from .options import Options
from .utils import (
    print_report_initial,
    local_print,
    local_print_df,
)


class DataAbstract(ABC):
    def __init__(
        self,
        options: Options,
        df: pd.DataFrame,
        target_name: str = None,
        numerical_cols=None,
        categorical_cols=None,
        output_area=None,
    ):
        self.options = options
        self.df = df.copy()
        self.target_name = target_name or df.columns[0]
        self.numerical_cols = numerical_cols
        self.categorical_cols = categorical_cols
        self.output_area = output_area
        self.check_data()
        self._infer_column_types()  # TODO
        self.validate()

    def check_data(self) -> None:

        self.df, self.options = set_numerical_categ_cols(
            self.df, self.options, output_area=self.output_area
        )

    def _infer_column_types(self):
        # Infer numerical/categorical columns if not provided
        if self.numerical_cols is None and self.categorical_cols is None:
            self.numerical_cols = self.df.select_dtypes(
                include=["int64", "float64"]
            ).columns.tolist()
            self.categorical_cols = [
                col
                for col in self.df.columns
                if col not in self.numerical_cols and col != self.target_name
            ]
        elif self.numerical_cols is not None:
            self.categorical_cols = [
                col
                for col in self.df.columns
                if col not in self.numerical_cols and col != self.target_name
            ]
        elif self.categorical_cols is not None:
            self.numerical_cols = [
                col
                for col in self.df.columns
                if col not in self.categorical_cols and col != self.target_name
            ]

    def sleep(self, duration: float = 2.0):
        time.sleep(duration)

    def warn(self, msg: str):
        print(f"[DataAbstract] Warning: {msg}")

    def validate(self):
        # Check for missing columns and correct dtypes
        missing_num = [col for col in self.numerical_cols if col not in self.df.columns]
        missing_cat = [
            col for col in self.categorical_cols if col not in self.df.columns
        ]
        if missing_num:
            self.warn(f"Missing numerical columns: {missing_num}")

        if missing_cat:
            self.warn(f"Missing categorical columns: {missing_cat}")
        for col in self.numerical_cols:
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                self.warn(
                    f"Numerical column '{col}' is not numeric (dtype: {self.df[col].dtype})"
                )
        for col in self.categorical_cols:
            if not (
                pd.api.types.is_object_dtype(self.df[col])
                or pd.api.types.is_string_dtype(self.df[col])
            ):
                self.warn(
                    f"Categorical column '{col}' is not string/object (dtype: {self.df[col].dtype})"
                )

    @staticmethod
    def check_data2(df: pd.DataFrame, options: Options, output_area=None):

        df, options = set_numerical_categ_cols(df, options, output_area=output_area)
        return df, options

    def get_X_y(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:

        X_train, X_test, y_train, y_test = prepare_data(
            self.df, self.options, output_area=self.output_area
        )
        return X_train, X_test, y_train, y_test

    def debug_report(self):
        print("\n[DataAbstract] DataFrame dtypes:")
        print(self.df.dtypes)
        print("[DataAbstract] Numerical columns:", self.numerical_cols)
        print("[DataAbstract] Categorical columns:", self.categorical_cols)
        print("[DataAbstract] Target column:", self.target_name)
        print("[DataAbstract] First few rows:")
        print(self.df.head())

    def __repr__(self):
        return f"DataAbstract(target_name={self.target_name}, numerical_cols={self.numerical_cols}, categorical_cols={self.categorical_cols})"

    # Add more utility methods as needed
    def __str__(self):
        t = f"""
        [DataAbstract]
        Shape : {self.df.shape}
        Numerical columns : {self.numerical_cols}
        Categorical columns : {self.categorical_cols}
        Target column : {self.target_name}

        """
        return t


# -- Data Preparation
def get_data_abstract_with_options(options, df, output_area=None) -> DataAbstract:

    if not isinstance(options.data, type(None)):
        df = options.data
        warnings.warn("Using DataFrame provided in options.data")
        time.sleep(2)
    print_report_initial(df, options, output_area=output_area)

    return DataAbstract(
        options=options,
        df=df,
        target_name=options.target_name,
        numerical_cols=options.numerical_cols,
        categorical_cols=options.categorical_cols,
        output_area=output_area,
    )
