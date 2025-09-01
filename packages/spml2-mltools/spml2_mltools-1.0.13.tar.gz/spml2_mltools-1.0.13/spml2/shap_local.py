import shap
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod


class ShapAbstract(ABC):
    def __init__(self, model, X, feature_names=None):
        self.model = model
        self.X = X
        self.feature_names = feature_names or getattr(X, "columns", None)
        self.explainer = self._get_explainer()

    @abstractmethod
    def _get_explainer(self):
        """Return a SHAP explainer for the model."""
        pass

    def shap_values(self):
        return self.explainer.shap_values(self.X)

    def summary_plot(self, show=True, save_path=None, **kwargs):
        shap_values = self.shap_values()
        shap.summary_plot(
            shap_values, self.X, feature_names=self.feature_names, show=show, **kwargs
        )
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close()

    def force_plot(self, index=0, show=True, save_path=None, **kwargs):
        shap_values = self.shap_values()
        # Handle multi-output models
        expected_value = self.explainer.expected_value
        if hasattr(expected_value, "__len__") and not isinstance(expected_value, str):
            base_value = expected_value[0]
            shap_val = (
                shap_values[index][..., 0]
                if shap_values[index].ndim > 1
                else shap_values[index]
            )
        else:
            base_value = expected_value
            shap_val = shap_values[index]
        force = shap.plots.force(
            base_value,
            shap_val,
            self.X.iloc[index],
            feature_names=self.feature_names,
            **kwargs,
        )
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close()
        return force


class ShapAuto(ShapAbstract):
    def _get_explainer(self):
        # Try to select the best explainer based on model type
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
            # Fallback to KernelExplainer (works for most models, but slower)
            return shap.KernelExplainer(self.model.predict, self.X)


class ShapTree(ShapAbstract):
    def _get_explainer(self):
        return shap.TreeExplainer(self.model)


class ShapLinear(ShapAbstract):
    def _get_explainer(self):
        return shap.LinearExplainer(self.model, self.X)
