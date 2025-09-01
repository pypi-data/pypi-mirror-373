import joblib
import pandas as pd
from .options import Options


class ResultCache:
    def __init__(self, options: Options, df: pd.DataFrame):
        self.options = options
        self.df = df

    def name_format(self):
        return f"results_{self.options.id}_{self.df.shape[0]}.pkl"

    def save(self, results):
        joblib.dump(results, self.name_format())

    def load(self, file_path):
        return joblib.load(file_path)
