from .types_ import PipelineConfig, dic_var_types
import pandas as pd
from typing import Dict, Tuple, Any
from sklearn.base import BaseEstimator, TransformerMixin


def extract_csv(config: PipelineConfig) -> pd.DataFrame:
    return pd.read_csv(config.data_path)

def classify_variable_types(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, Dict[str, int]]:
    classified_df: Dict[str, int] = {}
    id_set = set(config.id_columns or [])
    for col in df.columns:
        col_type = df[col].dtype
        if col in id_set:
            classified_df[col] = dic_var_types["unique"]
            continue
        if col_type.kind not in ("i", "u", "f"):  # not int, uint, float
            classified_df[col] = dic_var_types["categorical"]
            continue
        nunq = df[col].nunique(dropna=True)
        if nunq < 10:
            classified_df[col] = dic_var_types["categorical"]
        else:
            classified_df[col] = dic_var_types["numerical"]
    return df, classified_df

class ClassifyTypesTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.classified_: Dict[str, int] | None = None

    def fit(self, X: pd.DataFrame, y: Any = None):
        _, classified = classify_variable_types(X, self.config)
        self.classified_ = classified
        return self

    def transform(self, X: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        if self.classified_ is None:
            raise RuntimeError("Transformer not fitted.")
        return X, self.classified_