import json
import hashlib
from typing import Any


"""
test_mode: bool = False,
        debug: bool = False,
        target_name: str | None = None,
        test_df_size: int = 1000,
        test_ratio: float = 0.20,
        root: PathStr = Path("./input"),
        real_df_filename="example.dta",
        output_folder: PathStr = None,
        numerical_cols=None,
        sampling_strategy: FloatStr = "auto",
        n_splits: int = 5,

"""


def get_hash_(opts: dict[str, Any]) -> str:
    options_str = json.dumps(opts, sort_keys=True, default=str)
    return hashlib.sha256(options_str.encode("utf-8")).hexdigest()[0:6]


def options_hash_from_dict(options_dict: dict[str, Any]) -> str:
    opts = dict()  # options_dict.copy()
    keys = [
        "test_mode",
        "target_name",
        "output_folder",
        "debug",
        "test_df_size",
        "test_ratio",
        "root",
        "real_df_path",
        "n_splits",
        "numerical_cols",
        "sampling_strategy",
    ]
    for key in keys:
        opts[key] = options_dict[key]

    return get_hash_(opts)


# def options_hash_from_dict2(options_dict: dict[str, Any]) -> str:
#     opts = options_dict.copy()
#     keys = [
#         "roc_plots",
#         "shap_plots",
#         "output_folder",
#         "debug",
#         "cache",
#         "shap_sample_size",
#         "search_kwargs",
#         "pipeline"
#         "self"
#     ]
#     for key in keys:
#         if key in opts:
#             del opts[key]

#     return get_hash_(opts)
