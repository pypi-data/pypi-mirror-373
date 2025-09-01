from .options import Options
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from typing import Any
import pandas as pd


def plot_roc_curve(
    model_name: str,
    model: Any,
    options: Options,
    X_test: pd.Series,
    y_test: pd.Series,
    y_pred_proba: pd.Series | None = None,
    out_name: str = "graph_roc",
    show: bool = False,
    output_area: Any = None,
    plot_area: Any = None,
):
    out_folder = Path(options.output_folder) / "graphs"
    if not out_folder.exists():
        out_folder.mkdir(parents=True, exist_ok=True)
    try:
        if y_pred_proba is None:
            try:
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            except AttributeError:
                print(
                    "Model does not have a predict_proba method. Using predict instead."
                )
                y_pred_proba = model.predict(X_test)
                print(
                    "Warning: Using predict instead of predict_proba. ROC curve might not be accurate."
                )
            except Exception as e:
                print(f"Error during prediction: {e}")
                return

        fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
        auc = roc_auc_score(y_test, y_pred_proba)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f"{model_name} - ROC Curve (AUC = {auc:.2f})")
        plt.plot([0, 1], [0, 1], "k--")  # Add diagonal line
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.grid(True)
        plot_path = out_folder / f"{out_name}.png"
        plt.savefig(plot_path)
        if plot_area is not None:
            try:
                import streamlit as st

                plot_area.image(str(plot_path), caption="ROC Curve")
            except ImportError:
                print("Streamlit is not installed. Skipping web display.")
        if show:
            plt.show()
        plt.close()
    except Exception as e:
        print(f"An error occurred while creating the ROC curve: {e}")
