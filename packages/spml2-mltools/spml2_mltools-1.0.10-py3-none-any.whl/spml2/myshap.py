from typing import Any
from dataclasses import dataclass

try:
    import shap
except ImportError:
    shap = None


class SavedModel:
    def __init__(self, options):
        self.options = options

    def load_result(self):
        return self.options


class MyShapSvo:
    explainer: shap.Explainer = None

    def __init__(self, mdl: Any) -> None:
        self.mdl = mdl
        self.init()

    def init(self):
        self.explainer = shap.Explainer(self.mdl)
        return self.explainer

    def get_shap_values(self, X):
        shap_values = self.explainer.shap_values(X)
        return shap_values

    def get_explainer(self, X):
        explainer = shap.Explainer(self.mdl, X)
        shap_values = explainer(X)
        return shap_values


def get_myshap_svo(model: SavedModel, algo_step_name="model"):
    res = model.load_result()
    algo_ = res["algo"]
    if hasattr(algo_, "best_estimator_"):
        mdl = algo_.best_estimator_.named_steps[algo_step_name]
    else:
        mdl = algo_.best_estimator.named_steps[algo_step_name]
    return MyShapSvo(mdl)
