from dataclasses import dataclass

# ---------- Config and helper functions ----------
dic_var_types = {
    "categorical": 1,
    "numerical": 2,
    "unique": 3  # IDs and other unique values
}

@dataclass
class PipelineConfig:
    data_path: str
    target_column: str
    test_size: float
    val_size: float
    drop_duplicates: bool = True
    id_columns: list[str] = None
    require_target_positive: bool = True
    iqr_clip: bool = False
    iqr_factor: float = 3.0
    cast_features_to: str = "float32"
    cast_target_to: str = "float32"
    random_state: int = 42
    non_negative_columns: list[str] | None = None
