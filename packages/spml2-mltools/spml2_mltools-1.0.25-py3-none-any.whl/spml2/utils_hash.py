import json
import hashlib
from typing import Any


def options_hash_from_dict(options_dict: dict[str, Any]) -> str:
    opts = options_dict.copy()
    keys = [
        "roc_plots",
        "shap_plots",
        "output_folder",
        "debug",
        "cache",
        "shap_sample_size",
    ]
    for key in keys:
        if key in opts:
            del opts[key]

    options_str = json.dumps(opts, sort_keys=True, default=str)
    return hashlib.sha256(options_str.encode("utf-8")).hexdigest()[0:6]
