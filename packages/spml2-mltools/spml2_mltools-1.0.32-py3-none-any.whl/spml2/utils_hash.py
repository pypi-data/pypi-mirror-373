import json
import hashlib
from typing import Any


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
        if key in options_dict:
            opts[key] = options_dict[key]
        else:
            import warnings

            warnings.warn(f"Missing key in options_dict: {key}")
    return get_hash_(opts)
