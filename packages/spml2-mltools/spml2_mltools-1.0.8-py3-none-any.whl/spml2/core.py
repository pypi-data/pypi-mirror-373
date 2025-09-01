from abc import ABC, abstractmethod
import warnings
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Any

# Third-party libraries
import pandas as pd
import matplotlib
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

matplotlib.use("Agg")
# Local imports
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
warnings.filterwarnings("ignore", message="resource_tracker:.*")


# =================================Core Process================================
def train_and_search(
    model: Any,
    preprocessor: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    options: Options,
    param_grid: dict,
) -> tuple[Any, Any, dict]:
    """
    Train a model pipeline with hyperparameter search.
    Returns: best_estimator, duration, best_params
    """
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


def evaluate_model(model, X_test, y_test) -> tuple[pd.Series, pd.Series, dict]:
    """
    Evaluate a fitted model on test data. Returns predictions, probabilities, and metrics dict.
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    metrics = {
        "ROC AUC": roc_auc_score(y_test, y_proba),
        "F1 Score": f1_score(y_test, y_pred),
        "Confusion Matrix": confusion_matrix(y_test, y_pred),
        "Classification Report": classification_report(
            y_test, y_pred, output_dict=True
        ),
    }
    return y_pred, y_proba, metrics


def prepare_data(
    df: pd.DataFrame, options: Options, output_area: Any = None
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """
    Prepare data: set target, infer numerical/categorical columns, split train/test.
    Returns: X_train, X_test, y_train, y_test, categorical_cols, df
    """
    print_report_initial(df, options, output_area=output_area)
    if options.target_name not in df.columns:
        warnings.warn(
            f"Target name '{options.target_name}' not found in DataFrame columns. Using the first column as target."
        )
        options.target_name = df.columns[0]
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
        X, y, test_size=0.2, train_size=options.train_size, random_state=42, stratify=y
    )
    return X_train, X_test, y_train, y_test, categorical_cols, df


def build_preprocessor(options: Options, categorical_cols: list) -> ColumnTransformer:
    """
    Build a ColumnTransformer for numerical and categorical columns.
    """
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
        """
        ActionAbstract(options, models, output_area=output_area, plot_area=plot_area)
           ActionFresh(options, models, output_area=output_area, plot_area=plot_area)
           ActionCache(options, models, output_area=output_area, plot_area=plot_area)
        """
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

    def shap_plots(self, model, X):
        if not self.options.shap_plots:
            return
        from .shap_local import ShapTree, ShapLinear, ShapAuto

        folder = self.options.output_folder / "graphs"
        folder.mkdir(parents=True, exist_ok=True)
        explainer = ShapAuto(model, X.head(100))
        explainer.summary_plot(
            save_path=folder / f"shap_summary_{model.__class__.__name__}.png"
        )
        explainer.force_plot(
            save_path=folder / f"shap_force_{model.__class__.__name__}.png"
        )

    def execute(self) -> None:
        """Execute the action: prepare data, train/evaluate models, save results."""
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
            if (
                str(model_name).strip().startswith("#")
                or "cancelled" in model_name.lower()
            ):
                local_print(
                    f"\n{'='*50}\n Passing {model_name}  \n{'='*50}",
                    output_area=self.output_area,
                )
                continue
            if self.options.debug:
                if model_name != "KNN":
                    local_print(
                        f"Debug mode is open passing this {model_name}",
                        output_area=self.output_area,
                    )
                    continue
            local_print(
                f"\n{'='*50}\n Next Model : {model_name} \n{'='*50}",
                output_area=self.output_area,
            )
            best_model, duration, best_params = self.get_best_model(
                config, preprocessor, X_train, y_train, self.options, model_name
            )
            metrics = self.get_metrics(best_model, X_test, y_test)
            result_name = self.get_result_name(model_name)

            save_model(best_model, result_name, self.options)
            save_metrics(metrics, result_name, self.options)
            self.shap_plots(best_model.named_steps["model"], X_test)
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
            local_print(
                f"\n{'='*50}\n {model_name} : {duration} \n{'='*50}",
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
            save_results_individual(
                self.df_final,
                model_name,
                pd.DataFrame([model_results_dict]),
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
            f"\n{'='*50}\n [Checkin Cache] Next model : { model_name} \n{'='*50}",
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
