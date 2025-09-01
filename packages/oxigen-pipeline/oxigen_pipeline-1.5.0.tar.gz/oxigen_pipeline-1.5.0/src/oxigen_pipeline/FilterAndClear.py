import pandas as pd
import numpy as np
from .types_ import PipelineConfig, dic_var_types
from typing import Dict, Tuple, Any
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split

def filter_and_clean(df: pd.DataFrame, classified_df: dict, config: PipelineConfig) -> pd.DataFrame:
    out = df.copy()
    target = config.target_column
    if target not in out.columns:
        raise ValueError(f"Target column '{target}' not found.")

    if getattr(config, "drop_duplicates", True):
        out = out.drop_duplicates(ignore_index=True)

    id_cols = [c for c, t in classified_df.items() if t == dic_var_types["unique"]]
    if config.id_columns:
        id_cols += [c for c in config.id_columns if c in out.columns]
    if id_cols:
        out = out.drop(columns=list(set(id_cols)), errors="ignore")

    for col, var_type in classified_df.items():
        if col not in out.columns or col == target:
            continue
        if var_type == dic_var_types["numerical"]:
            out[col] = pd.to_numeric(out[col], errors="coerce")
        elif var_type == dic_var_types["categorical"]:
            out[col] = out[col].astype("string").str.strip()
            out.loc[out[col].isin(["", "nan", "None", "NULL"]), col] = pd.NA

    out[target] = pd.to_numeric(out[target], errors="coerce")
    out = out.dropna(subset=[target])
    if getattr(config, "require_target_positive", False):
        out = out[out[target] > 0]

    nonneg = getattr(config, "non_negative_columns", []) or []
    for c in nonneg:
        if c in out.columns:
            out.loc[out[c] < 0, c] = np.nan

    if getattr(config, "iqr_clip", False):
        iqr_factor = getattr(config, "iqr_factor", 3.0)
        num_cols = [c for c, t in classified_df.items() if t == dic_var_types["numerical"] and c in out.columns]
        if num_cols:
            Q1 = out[num_cols].quantile(0.25)
            Q3 = out[num_cols].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - iqr_factor * IQR
            upper = Q3 + iqr_factor * IQR
            out[num_cols] = out[num_cols].clip(lower=lower, upper=upper, axis=1)

    feature_cols = [c for c in out.columns if c != target]
    if feature_cols:
        out = out.dropna(how="all", subset=feature_cols)

    if config.cast_features_to:
        for c in feature_cols:
            if pd.api.types.is_numeric_dtype(out[c]):
                out[c] = out[c].astype(config.cast_features_to)
    if config.cast_target_to:
        out[target] = out[target].astype(config.cast_target_to)

    return out.reset_index(drop=True)


class CleanTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, config: PipelineConfig):
        self.config = config

    def fit(self, X_y: Tuple[pd.DataFrame, Dict[str, int]], y: Any = None):
        return self

    def transform(self, X_y: Tuple[pd.DataFrame, Dict[str, int]]) -> pd.DataFrame:
        df, classified = X_y
        return filter_and_clean(df, classified, self.config)

def split_data_and_out(df: pd.DataFrame, config: PipelineConfig):
    target = config.target_column
    X = df.drop(columns=[target])
    y = df[target]

    X_train_tmp, X_test, y_train_tmp, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.random_state
    )
    val_rel = config.val_size / (1.0 - config.test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_tmp, y_train_tmp, test_size=val_rel, random_state=config.random_state
    )
    return X_train, X_val, X_test, y_train, y_val, y_test

class SplitTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, config: PipelineConfig):
        self.config = config

    def fit(self, df: pd.DataFrame, y: Any = None):
        return self

    def transform(self, df: pd.DataFrame):
        return split_data_and_out(df, self.config)