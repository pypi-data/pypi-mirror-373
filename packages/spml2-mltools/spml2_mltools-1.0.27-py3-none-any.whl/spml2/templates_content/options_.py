options_content = """\n
# --- User-editable configuration ---
from pathlib import Path
from spml2 import Options
from models_user import models


TEST_MODE = False  # Enable test mode for quick runs
DEBUG = False  # Enable debug mode for extra checks
TARGET_NAME = "target"  # Name of the target column
TEST_DF_SIZE = 1000  # Number of rows for test DataFrame
TEST_RATIO = 0.20  # Proportion of the dataset to include in the test split

ROOT = Path("./input")  # Root directory for data
REAL_DF_FILENAME = "example.dta"  # Main data file name (must be .dta)
OUTPUT_FOLDER = "Output"  #  None  # Output folder (None = default root/Output)
NUMERICAL_COLS = None  # List of numerical columns (None = infer from data)
SAMPLING_STRATEGY = "auto"  # SMOTE sampling strategy ('auto' recommended)
N_SPLITS = 5
SHAP_PLOTS = False  # Enable SHAP plots
SHAP_SAMPLE_SIZE = 100  # Number of samples for SHAP plots
ROC_PLOTS = True

options = Options(
    test_mode=TEST_MODE,
    debug=DEBUG,
    target_name=TARGET_NAME,
    test_df_size=TEST_DF_SIZE,
    test_ratio=TEST_RATIO,
    root=ROOT,
    real_df_filename=REAL_DF_FILENAME,
    output_folder=OUTPUT_FOLDER,
    numerical_cols=NUMERICAL_COLS,
    sampling_strategy=SAMPLING_STRATEGY,
    n_splits=N_SPLITS,
    shap_plots=SHAP_PLOTS,
    roc_plots=ROC_PLOTS,
    shap_sample_size=SHAP_SAMPLE_SIZE,
)
print(options)


"""
