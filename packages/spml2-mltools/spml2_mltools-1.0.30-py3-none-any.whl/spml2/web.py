from typing import Any
import streamlit as st
import os
import sys
import io
import pandas as pd
from pathlib import Path
import importlib.util
import warnings

from spml2.options import Options
from spml2.utils import get_data


warnings.filterwarnings("ignore", module="pyarrow")


def import_user_module(module_name, file_name):
    user_path = Path.cwd() / file_name
    spec = importlib.util.spec_from_file_location(module_name, user_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


models_user = import_user_module("models_user", "models_user.py")
options_user = import_user_module("options_user", "options_user.py")

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
    SHAP_SAMPLE_SIZE,
)


def get_hash(options: dict):
    from spml2.utils_hash import options_hash_from_dict

    return options_hash_from_dict(options)


MODELS = models_user.models

test_mode = st.sidebar.checkbox("Test Mode", value=TEST_MODE)
debug = st.sidebar.checkbox("Debug Mode", value=DEBUG)
target_name = st.sidebar.text_input("Target Column", value=TARGET_NAME)
roc_plots = st.sidebar.checkbox("ROC Plots", value=ROC_PLOTS)
shap_plots = st.sidebar.checkbox("SHAP Plots", value=SHAP_PLOTS)
shap_sample_size = st.sidebar.number_input(
    "SHAP Sample Size", min_value=1, value=SHAP_SAMPLE_SIZE
)
test_df_size = st.sidebar.number_input(
    "Test DataFrame Size", min_value=1, value=TEST_DF_SIZE
)
output_folder = st.sidebar.text_input(
    "Output Folder (blank=default)", value=OUTPUT_FOLDER or ""
)
sampling_strategy = st.sidebar.text_input(
    "SMOTE Sampling Strategy", value=SAMPLING_STRATEGY
)
n_splits = st.sidebar.number_input("CV Splits", min_value=2, value=N_SPLITS)
input_folder = st.text_input(
    "Input folder",
    value=str(ROOT),
    help="You can enter an absolute path here to select a different data folder.",
)

if st.button("Quit App"):
    st.warning(
        "You can now close this tab or stop the server by pressing Ctrl+C in the terminal where Streamlit was started."
    )

st.title("SPML2 User Interface")


def process_with_output(options, models, output_area, plot_area):
    from spml2.core import Process

    Process(options, models=models, output_area=output_area, plot_area=plot_area)


def process_cache_with_output(options, models, output_area, plot_area):
    from spml2.core import Process_cache

    Process_cache(options, models=models, output_area=output_area, plot_area=plot_area)


if os.path.isdir(input_folder):
    files = [
        f
        for f in os.listdir(input_folder)
        if f.endswith((".dta", ".parquet", ".csv", ".xlsx"))
    ]
    selected_file = st.selectbox("Select a data file", files)
else:
    st.warning("Input folder does not exist.")
    selected_file = None

workflow = st.radio("Choose workflow", ["Run fresh", "Process cache"])

current_options = {
    "test_mode": test_mode,
    "debug": debug,
    "target_name": target_name,
    "test_df_size": test_df_size,
    "root": input_folder,
    "real_df_filename": selected_file,
    "output_folder": output_folder if output_folder else None,
    "numerical_cols": NUMERICAL_COLS,
    "sampling_strategy": sampling_strategy,
    "n_splits": n_splits,
    "roc_plots": roc_plots,
    "shap_plots": shap_plots,
}

hash_value = get_hash(current_options)
current_options2 = current_options.copy()

current_options2["hash"] = hash_value

st.json(current_options2)
col1, col2 = st.columns([2, 3])
output_area = col1.empty()
plot_area = col2.empty()

# Initialize output buffer in session state
if "output_buffer" not in st.session_state:
    st.session_state["output_buffer"] = ""


def get_info_df(selected_file, options):
    df = get_data(options)

    columns_list = df.columns.tolist()
    t = f"""
**Shape:** {df.shape}
<details>
<summary><b>Columns ({len(columns_list)})</b></summary>
{columns_list}
</details>
"""
    return t


if selected_file:
    options = Options(**current_options)
    df_info = get_info_df(selected_file, options)
    st.write(f"Selected file: {selected_file}")
    st.write("DataFrame Info:")
    st.markdown(df_info, unsafe_allow_html=True)
if st.button("Run"):
    if selected_file:
        options = Options(**current_options)
        st.write(f"Selected file: {selected_file}")
        with st.spinner(
            "Processing... Please wait. This may take a while for large datasets or complex models."
        ):
            if workflow == "Run fresh":
                st.write("Running fresh process...")
                process_with_output(
                    options, MODELS, output_area=output_area, plot_area=plot_area
                )
            else:
                st.write("Processing cache...")
                process_cache_with_output(
                    options, MODELS, output_area=output_area, plot_area=plot_area
                )

        st.success("Done!")
    else:
        st.error("Please select a file.")
