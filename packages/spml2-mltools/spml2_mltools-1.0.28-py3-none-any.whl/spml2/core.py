from abc import ABC, abstractmethod
import json

import warnings
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple, Dict

# Third-party
import numpy as np
import pandas as pd
from rich import print
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
)
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Local
from .models import models
from .options import Options
from .utils import (
    print_report_initial,
    initial_data_check,
    save_results_individual,
    save_results,
    save_model,
    get_data,
    check_cols,
    name_format_estimator,
    results_report,
    limited_models,
    save_pip_freeze,
    save_metrics,
    load_metrics_cache,
    load_model_cache,
    local_print,
    local_print_df,
)
from .plot_roc import plot_roc_curve
from .feature_importances import (
    FeatureImportancesAbstract,
    FeatureImportancesBasic,
    FeatureImportancesSKLEARN,
    save_feature_df,
    save_feature_importances,
    save_feature_importances_basic,
    save_feature_importances_SKLEARN,
)

# / Local imports =============================================================
# ================Warnings=====================================================
warnings.filterwarnings("ignore")


# =================================Core Process================================
def train_and_search(
    model: Any,
    preprocessor: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    options: Options,
    param_grid: dict,
) -> tuple[Any, Any, dict]:

    imb_pipeline = ImbPipeline(
        [
            ("preprocessor", preprocessor),
            (
                "smote",
                SMOTE(random_state=42, sampling_strategy=options.sampling_strategy),
            ),
            ("model", model),
        ]
    )
    random_search = RandomizedSearchCV(
        imb_pipeline,
        param_grid,
        cv=StratifiedKFold(n_splits=options.n_splits, shuffle=True, random_state=42),
        scoring="roc_auc",
        verbose=1,
        n_jobs=-1,
        error_score="raise",
    )
    start = datetime.now()
    random_search.fit(X_train, y_train)
    end = datetime.now()
    duration = end - start
    return random_search.best_estimator_, duration, random_search.best_params_


def evaluate_model(
    model: Any, X_test: pd.DataFrame, y_test: pd.Series
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    y_pred = model.predict(X_test)
    try:
        y_proba = model.predict_proba(X_test)
        if y_proba.shape[1] == 2:
            y_proba = y_proba[:, 1]
    except AttributeError:
        try:
            y_proba = model.decision_function(X_test)
        except AttributeError:
            y_proba = None

    metrics = {
        "F1 Score": f1_score(
            y_test, y_pred, average="binary" if len(np.unique(y_test)) == 2 else "macro"
        ),
        "Confusion Matrix": confusion_matrix(y_test, y_pred),
        "Classification Report": classification_report(
            y_test, y_pred, output_dict=True
        ),
    }
    if y_proba is not None:
        try:
            metrics["ROC AUC"] = roc_auc_score(y_test, y_proba)
        except Exception:
            metrics["ROC AUC"] = None

    return y_pred, y_proba, metrics


class TargetColumnNameNotFound(Exception):
    pass


class TargetColumnNotBinary(Exception):
    pass


def prepare_data(
    df: pd.DataFrame, options: Options, output_area: Any = None
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:

    print_report_initial(df, options, output_area=output_area)
    target_name_was = options.target_name
    # If target_name is None, use the first column
    if options.target_name is None:
        options.target_name = df.columns[0]
        msg = f"No target column specified. Using the first column: '{options.target_name}' as target."
        warnings.warn(msg)
        print(msg)
        time.sleep(2)

    if options.target_name not in df.columns:
        msg = f"Target name '{options.target_name}' not found in DataFrame columns."
        raise TargetColumnNameNotFound(msg)

    # Check if the target column is suitable for binary classification
    target_values = df[options.target_name].dropna().unique()
    if len(target_values) != 2:
        if target_name_was is None:
            msg = f"Target name was not specified. Using the first column: '{options.target_name}' as target."
        target_values_str = ", ".join(map(str, (list(target_values[0:3]) + ["..."])))
        msg += f"\nTarget column '{options.target_name}' is not binary (unique values: {target_values_str}). Please provide a binary target column."
        raise TargetColumnNotBinary(msg)

    df[options.target_name] = pd.to_numeric(df[options.target_name], downcast="integer")
    local_print_df(df.head(), output_area=output_area)
    if options.numerical_cols is None:
        options.numerical_cols = df.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
    categorical_cols = [col for col in df.columns if col not in options.numerical_cols]
    categorical_cols = [col for col in categorical_cols if col != options.target_name]
    X = df.drop(options.target_name, axis=1)
    y = df[options.target_name]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=options.test_ratio,
        train_size=options.train_size,
        random_state=42,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test, categorical_cols, df


def build_preprocessor(options: Options, categorical_cols: list) -> ColumnTransformer:

    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), options.numerical_cols),
            ("cat", "passthrough", categorical_cols),
        ]
    )


class ActionAbstract:
    name: str = "ActionAbstract"
    description: str = "Abstract action"

    def __init__(
        self, options: Options, models: dict, output_area=None, plot_area=None
    ):

        self.options = options
        self.models = models
        self.output_area = output_area
        self.plot_area = plot_area

    def get_df(self):
        initial_data_check(self.options)
        df = get_data(self.options)
        return df

    @abstractmethod
    def get_metrics(self, model, X_test, y_test): ...
    def get_result_name(self, model_name: str) -> str:
        result_name = name_format_estimator(model_name, self.df_final, self.options)
        if self.name != "Fresh":
            result_name = f"repeated_{result_name}"
        return result_name

    def shap_plots(self, model: Any, X: pd.DataFrame, result_name: str):
        if not self.options.shap_plots:
            return
        from .shap_local import ShapTree, ShapLinear, ShapAuto

        folder = self.options.output_folder / "graphs"
        folder.mkdir(parents=True, exist_ok=True)
        rows = self.options.shap_sample_size
        explainer = ShapAuto(model, X.head(rows))
        explainer.summary_plot(save_path=folder / f"shap_summary_{result_name}.png")

    def should_I_pass(self, model_name: str) -> bool:
        if str(model_name).strip().startswith("#") or "cancelled" in model_name.lower():
            local_print(
                f"\n{'='*50}\n Passing {model_name}  \n{'='*50}",
                output_area=self.output_area,
            )
            return True
        return False

    def test_name_when_debug(self, models: dict) -> str:
        if "XGBoost" in models:
            return "XGBoost"

        return list(models.keys())[0]

    def execute(self) -> "ActionAbstract":

        df = self.get_df()
        if self.name == "Fresh":
            save_pip_freeze(self.options)
        X_train, X_test, y_train, y_test, categorical_cols, df = prepare_data(
            df, self.options, output_area=self.output_area
        )
        self.df_final = df
        preprocessor = build_preprocessor(self.options, categorical_cols)
        features = X_train.columns.tolist()
        results = []
        for model_name, config in models.items():
            if self.should_I_pass(model_name):
                continue
            if self.options.debug:
                if model_name != self.test_name_when_debug(models):
                    local_print(
                        f"Debug mode is open passing this {model_name}",
                        output_area=self.output_area,
                    )
                    continue
            local_print(
                f"\n Next Model : {model_name} \n",
                output_area=self.output_area,
            )
            # best_model.named_steps["model"]

            best_model, duration, best_params = self.get_best_model(
                config, preprocessor, X_train, y_train, self.options, model_name
            )
            metrics = self.get_metrics(best_model, X_test, y_test)
            result_name = self.get_result_name(model_name)

            save_model(best_model, result_name, self.options)
            save_metrics(metrics, result_name, self.options)

            # Shap Summary plot
            if self.options.shap_plots:
                X_test_processed = pd.DataFrame(
                    best_model.named_steps["preprocessor"].transform(X_test),
                    columns=features,
                )
                # X_test_processed = pd.DataFrame(best_model.named_steps["preprocessor"].transform(X_test) , columns=features)
                self.shap_plots(
                    best_model.named_steps["model"], X_test_processed, result_name
                )

            # ROC AUC plot
            if self.options.roc_plots:
                plot_roc_curve(
                    model_name,
                    best_model,
                    self.options,
                    X_test,
                    y_test,
                    out_name=result_name,
                    output_area=self.output_area,
                    plot_area=self.plot_area,
                )
            if duration is None:
                duration = " "
            else:
                import datetime as dt

                rounded_seconds = round(duration.total_seconds())
                duration = f" : {rounded_seconds:.2f} seconds"

            local_print(
                f"\n{model_name}{duration} \n ",
                output_area=self.output_area,
            )
            model_results_dict = {
                "Model": model_name,
                "Best Params": str(best_params),
                "ROC AUC": metrics["ROC AUC"],
                "F1 Score": metrics["F1 Score"],
                "Confusion Matrix": metrics["Confusion Matrix"],
                "Classification Report": metrics["Classification Report"],
                "Feature Importance": getattr(
                    best_model.named_steps["model"], "feature_importances_", None
                ),
                "duration": str(duration),
                "nf_estimator": result_name,
            }
            save_feature_importances(
                best_model,
                self.options,
                result_name,
                features=features,
                X_test=X_test,
                y_test=y_test,
                output_area=self.output_area,
            )
            model_results_df = pd.DataFrame([model_results_dict])
            print(model_results_df)
            save_results_individual(
                self.df_final,
                model_name,
                model_results_df,
                self.options,
            )
            results.append(model_results_dict)
            time.sleep(1)
        if self.name == "Fresh":
            results_report(
                results,
                self.df_final,
                self.options,
                output_area=self.output_area,
                plot_area=self.plot_area,
            )
        return self

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)


class ActionFresh(ActionAbstract):
    name = "Fresh"
    description = "Fresh data processing action"

    def get_best_model(
        self, config, preprocessor, X_train, y_train, options, model_name
    ):
        best_model, duration, best_params = train_and_search(
            config["model"], preprocessor, X_train, y_train, options, config["params"]
        )
        return best_model, duration, best_params

    def get_metrics(self, best_model, X_test, y_test):
        y_pred, y_proba, metrics = evaluate_model(best_model, X_test, y_test)
        return metrics


class ActionCache(ActionAbstract):
    name = "Cache"
    description = "Cache data processing action"

    def get_best_model(
        self, config, preprocessor, X_train, y_train, options, model_name
    ):
        local_print(
            f"\n[Checking cache] Next model : { model_name} \n",
            output_area=self.output_area,
        )
        bucket_name = name_format_estimator(model_name, self.df_final, options)
        best_model = load_model_cache(bucket_name, options)
        self.metrics = load_metrics_cache(bucket_name, options)
        return best_model, None, None

    def get_metrics(self, best_model, X_test, y_test):
        return self.metrics


def Process(options: Options, models: dict, output_area=None, plot_area=None):
    return ActionFresh(
        options, models, output_area=output_area, plot_area=plot_area
    ).execute()


def Process_cache(options: Options, models: dict, output_area=None, plot_area=None):
    return ActionCache(
        options, models, output_area=output_area, plot_area=plot_area
    ).execute()
