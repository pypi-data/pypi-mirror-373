from pathlib import Path
import os
from dataclasses import dataclass
import time
from typing import Any


@dataclass
class Options:
    def __init__(
        self,
        test_mode: bool = False,
        debug: bool = False,
        target_name: str | None = None,
        test_df_size: int = 1000,
        test_ratio: float = 0.20,
        root: str | Path = Path("./input"),
        real_df_filename="data.dta",
        output_folder=None,
        numerical_cols=None,
        sampling_strategy="auto",
        n_splits: int = 5,
        cache: bool = True,
        shap_plots: bool = False,
        roc_plots: bool = True,
        shap_sample_size: int = 100,
    ):
        self.test_ratio = test_ratio
        self.shap_sample_size = shap_sample_size
        self.roc_plots = roc_plots
        self.shap_plots = shap_plots
        self.n_splits = n_splits
        self.cache = cache
        self.sampling_strategy = sampling_strategy
        self.test_mode = test_mode
        self.debug = debug
        self.target_name = target_name
        self.test_df_size = test_df_size
        self.root = Path(root)
        self.real_df_path = self.root / real_df_filename
        self.output_folder = output_folder if output_folder else self.root / "Output"
        self.output_folder = Path(self.output_folder)
        self.numerical_cols = numerical_cols

        self.test_file_name = self.real_df_path.with_stem(
            f"small_df_{self.test_df_size}" + self.real_df_path.stem
        ).with_suffix(".parquet")
        self.test_batch_size = self.test_df_size // 5
        self.size = self.test_df_size // 2 if self.test_mode else None
        self.train_size = self.size // 2 if self.size else None
        if not self.output_folder.exists():
            os.makedirs(self.output_folder)
        self.real_df_path = Path(self.real_df_path)

        if not self.real_df_path.exists():
            print(f"Warning: Data file does not exist: {self.real_df_path}")

        if not self.test_mode and self.debug:
            time.sleep(2)
            print("Ignoring debug mode when test mode is False")
            self.debug = False

    def hash(self):
        from spml2.utils_hash import options_hash_from_dict

        if hasattr(self, "__dict__"):
            options_dict = self.__dict__
        else:
            options_dict = dict(self)
        return options_hash_from_dict(options_dict)

    def __repr__(self):
        return (
            f"hash:{self.hash()}"
            f"Options(test_mode={self.test_mode}, debug={self.debug}, "
            f"target_name='{self.target_name}', test_df_size={self.test_df_size}, "
            f"root='{self.root}', real_df_filename='{self.real_df_path.name}', "
            f"output_folder='{self.output_folder}', numerical_cols={self.numerical_cols}, "
            f"sampling_strategy='{self.sampling_strategy}', "
            f"test_file_name='{self.test_file_name}', "
            f"n_splits={self.n_splits}, "
            f"shap_plots={self.shap_plots}, "
            f"roc_plots={self.roc_plots})"
        )

    def __str__(self):
        template = f"""
        [Options]
        {self.hash()}
        Data / Process options
        ________________________

        test_mode :  {self.test_mode}
        debug :  {self.debug}
        target_name :  {self.target_name}
        test_df_size :  {self.test_df_size}
        root :  {self.root}
        real_df_filename : {self.real_df_path.name}
        output_folder : {self.output_folder}
        numerical_cols : {self.numerical_cols}
        test_file_name : {self.test_file_name}
        shap_plots : {self.shap_plots}
        roc_plots : {self.roc_plots}

        Model options (common for all models)
        ________________________
        n_splits : {self.n_splits}
        sampling_strategy : {self.sampling_strategy}
        """
        return template
