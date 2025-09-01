import json
import hashlib
from typing import Any


def options_hash_from_dict(options_dict: dict[str, Any]) -> str:
    opts = options_dict.copy()

    del opts["roc_plots"]
    del opts["shap_plots"]
    del opts["output_folder"]
    del opts["debug"]
    del opts["cache"]

    options_str = json.dumps(opts, sort_keys=True, default=str)
    return hashlib.sha256(options_str.encode("utf-8")).hexdigest()[0:6]
