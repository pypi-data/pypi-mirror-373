from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
import io
import pandas as pd
from pathlib import Path
from spml2.options import Options
import importlib.util

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Utility to import user modules
def import_user_module(module_name, file_name):
    user_path = Path.cwd() / file_name
    spec = importlib.util.spec_from_file_location(module_name, user_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


models_user = import_user_module("models_user", "models_user.py")
options_user = import_user_module("options_user", "options_user.py")
MODELS = models_user.models

from options_user import (
    TEST_MODE,
    DEBUG,
    TARGET_NAME,
    TEST_DF_SIZE,
    OUTPUT_FOLDER,
    NUMERICAL_COLS,
    SAMPLING_STRATEGY,
    N_SPLITS,
    ROOT,
    SHAP_PLOTS,
    ROC_PLOTS,
)


def get_hash(options: dict):
    from spml2.utils_hash import options_hash_from_dict

    return options_hash_from_dict(options)


@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    input_folder = str(ROOT)
    files = []
    if os.path.isdir(input_folder):
        files = [
            f
            for f in os.listdir(input_folder)
            if f.endswith((".dta", ".parquet", ".csv", ".xlsx"))
        ]
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "files": files,
            "test_mode": TEST_MODE,
            "debug": DEBUG,
            "target_name": TARGET_NAME,
            "roc_plots": ROC_PLOTS,
            "shap_plots": SHAP_PLOTS,
            "test_df_size": TEST_DF_SIZE,
            "output_folder": OUTPUT_FOLDER,
            "sampling_strategy": SAMPLING_STRATEGY,
            "n_splits": N_SPLITS,
            "input_folder": input_folder,
            "numerical_cols": NUMERICAL_COLS,
        },
    )


from typing import Optional


@app.post("/run", response_class=HTMLResponse)
def run(
    request: Request,
    selected_file: str = Form(...),
    test_mode: bool = Form(False),
    debug: bool = Form(False),
    target_name: str = Form("target"),
    roc_plots: bool = Form(False),
    shap_plots: bool = Form(False),
    test_df_size: int = Form(1000),
    output_folder: Optional[str] = Form(""),
    sampling_strategy: str = Form("auto"),
    n_splits: int = Form(5),
    input_folder: str = Form("input"),
    numerical_cols: Optional[str] = Form(""),
):
    options = {
        "test_mode": test_mode,
        "debug": debug,
        "target_name": target_name,
        "test_df_size": test_df_size,
        "root": input_folder,
        "real_df_filename": selected_file,
        "output_folder": output_folder if output_folder else None,
        "numerical_cols": None,  # [col.strip() for col in numerical_cols.split(",") if col.strip()] if numerical_cols else None,
        "sampling_strategy": sampling_strategy,
        "n_splits": n_splits,
        "roc_plots": roc_plots,
        "shap_plots": shap_plots,
    }
    options_obj = Options(**options)
    from spml2.utils import get_data

    df = get_data(options_obj)
    columns_list = df.columns.tolist()
    shape = df.shape

    output = f"Shape: {shape}\nColumns: {columns_list}"

    # Process(options, models)
    # Process_cache(options, models)

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "files": os.listdir(input_folder),
            "output": output,
            "selected_file": selected_file,
            "test_mode": test_mode,
            "debug": debug,
            "target_name": target_name,
            "roc_plots": roc_plots,
            "shap_plots": shap_plots,
            "test_df_size": test_df_size,
            "output_folder": output_folder,
            "sampling_strategy": sampling_strategy,
            "n_splits": n_splits,
            "input_folder": input_folder,
            "numerical_cols": numerical_cols,
        },
    )


# You need to create a 'templates/main.html' file for the UI.
# You can extend this with more endpoints for cache, plots, etc.


from spml2 import Process, Process_cache
from options_user import options
from models_user import models
