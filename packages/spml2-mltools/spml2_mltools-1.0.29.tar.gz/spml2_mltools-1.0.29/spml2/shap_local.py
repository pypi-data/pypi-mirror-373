import shap
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import Any, Optional
from pathlib import Path
from typing import Callable, TypeVar, Literal, Protocol
import pandas as pd
import numpy as np

ArrayLike = np.ndarray | pd.DataFrame | pd.Series


class ShapAbstract(ABC):
    def __init__(
        self, model: Any, X: ArrayLike, feature_names: Optional[list[str]] = None
    ):
        self.model = model
        self.X = X
        self.feature_names = feature_names or getattr(X, "columns", None)
        self.shap_vals = None
        self.explainer = self._get_explainer()

    @abstractmethod
    def _get_explainer(self):
        """Return a SHAP explainer for the model."""
        pass

    def shap_values_helper(self):
        return self.explainer.shap_values(self.X)

    def shap_values(self) -> Any:
        if self.shap_vals is None:
            self.shap_vals = self.shap_values_helper()

        return self.shap_vals

    def summary_plot(
        self,
        show: bool = False,
        save_path: Optional[str] = None,
        plot_type: str = "layered_violin",
        **kwargs,
    ):

        shap_values = self.shap_values()
        shap.summary_plot(
            shap_values,
            self.X,
            feature_names=self.feature_names,
            show=show,
            plot_type=plot_type,
            **kwargs,
        )
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
            plt.close()
        if show:
            plt.show()
        else:
            plt.close()


class ShapAuto(ShapAbstract):
    def _get_explainer(self) -> Any:
        import xgboost
        import lightgbm
        from sklearn.ensemble import (
            RandomForestClassifier,
            RandomForestRegressor,
            GradientBoostingClassifier,
            GradientBoostingRegressor,
        )
        from sklearn.linear_model import LogisticRegression, LinearRegression

        # Tree-based models
        if isinstance(
            self.model,
            (
                xgboost.XGBClassifier,
                xgboost.XGBRegressor,
                lightgbm.LGBMClassifier,
                lightgbm.LGBMRegressor,
                RandomForestClassifier,
                RandomForestRegressor,
                GradientBoostingClassifier,
                GradientBoostingRegressor,
            ),
        ):
            return shap.TreeExplainer(self.model)
        # Linear models
        elif isinstance(self.model, (LogisticRegression, LinearRegression)):
            return shap.LinearExplainer(self.model, self.X)
        else:
            # Fallback to KernelExplainer
            return shap.KernelExplainer(self.model.predict, self.X)


class ShapTree(ShapAbstract):
    def _get_explainer(self):
        return shap.TreeExplainer(self.model)


class ShapLinear(ShapAbstract):
    def _get_explainer(self):
        return shap.LinearExplainer(self.model, self.X)
