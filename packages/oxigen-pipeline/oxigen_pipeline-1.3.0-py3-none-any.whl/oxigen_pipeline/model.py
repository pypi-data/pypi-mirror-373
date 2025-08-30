import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io, base64

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import RandomizedSearchCV
from sklearn.compose import ColumnTransformer

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor



def train_and_evaluate_model(X_train, X_val, X_test, y_train, y_val, y_test, 
                             html_output_path: str, model_name: str):
    """
    Entrena un modelo específico con hyperparam tuning y genera un HTML con métricas + SHAP.
    
    Args:
        X_train, X_val, X_test, y_train, y_val, y_test : datos de entrenamiento, validación y test
        html_output_path (str): ruta para guardar el reporte en HTML
        model_name (str): nombre del modelo a entrenar 
                         ("RandomForest", "XGBoost", "LightGBM", "GBM")
    """

    # =========================
    # Detectar columnas numéricas y categóricas
    # =========================
    numeric_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
    # Reemplaza la línea del OneHotEncoder en tu preprocessor:
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)  # sklearn >=1.2
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)         # sklearn <1.2

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", ohe, categorical_features),
        ],
    )


    # =========================
    # Definir modelos y grids
    # =========================
    models_and_params = {
        "RandomForest": (
            RandomForestRegressor(random_state=42),
            {
                "model__n_estimators": [100, 200, 300],
                "model__max_depth": [None, 10, 20],
                "model__min_samples_split": [2, 5, 10],
            }
        ),
        "XGBoost": (
            XGBRegressor(objective="reg:squarederror", random_state=42, n_jobs=-1, early_stopping_rounds=20),
            {
                "model__n_estimators": [200, 500],
                "model__max_depth": [3, 6, 10],
                "model__learning_rate": [0.01, 0.05, 0.1],
                "model__subsample": [0.8, 1.0],
            }
        ),
        "LightGBM": (
            LGBMRegressor(random_state=42),
            {
                "model__n_estimators": [200, 500],
                "model__max_depth": [-1, 10, 20],
                "model__learning_rate": [0.01, 0.05, 0.1],
                "model__num_leaves": [31, 50, 100],
            }
        ),
        "GBM": (
            GradientBoostingRegressor(random_state=42),
            {
                "model__n_estimators": [100, 200],
                "model__learning_rate": [0.01, 0.05, 0.1],
                "model__max_depth": [3, 5, 7],
            }
        )
    }

    if model_name not in models_and_params:
        raise ValueError(f"Modelo {model_name} no reconocido. Opciones: {list(models_and_params.keys())}")

    model, param_grid = models_and_params[model_name]

    print(f"Entrenando {model_name}...")

    # =========================
    # Pipeline y búsqueda
    # =========================
    pipe = Pipeline([
        ("pre", preprocessor),
        ("model", model)
    ])

    search = RandomizedSearchCV(
        pipe,
        param_distributions=param_grid,
        n_iter=5,
        cv=3,
        scoring="r2",
        verbose=1,
        random_state=42,
        n_jobs=-1
    )

    # Eval set opcional
    fit_params = {}
    if model_name in ["XGBoost", "LightGBM"]:
        fit_params = {"model__eval_set": [(X_val, y_val)], "model__verbose": False}

    search.fit(X_train, y_train, **fit_params)
    best_model = search.best_estimator_

    # =========================
    # Evaluar en validación
    # =========================
    y_val_pred = best_model.predict(X_val)
    val_r2 = r2_score(y_val, y_val_pred)

    # =========================
    # Evaluar en test
    # =========================
    y_test_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_test_pred)
    mae = mean_absolute_error(y_test, y_test_pred)
    r2 = r2_score(y_test, y_test_pred)

    # =========================
    # Generar HTML
    # =========================
    html_content = "<html><head><title>Resultados Modelos</title></head><body>"
    html_content += f"<h1>Reporte del modelo {model_name}</h1>"
    html_content += f"<p>Best Params: {search.best_params_}</p>"
    html_content += f"<p>Validación R²: {val_r2:.4f}</p>"
    html_content += f"<p>Test MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}</p>"

    # =========================
    # SHAP -> embebido en base64 dentro del HTML
    # =========================
    try:
        pre = best_model.named_steps["pre"]
        model_fitted = best_model.named_steps["model"]

        # Data EXACTAMENTE como lo vio el modelo
        X_train_tx = pre.transform(X_train)
        X_test_tx  = pre.transform(X_test)

        # Asegurar salida densa
        if hasattr(X_train_tx, "toarray"): X_train_tx = X_train_tx.toarray()
        if hasattr(X_test_tx,  "toarray"): X_test_tx  = X_test_tx.toarray()

        # Nombres de columnas post-transform
        try:
            feature_names = pre.get_feature_names_out()
        except Exception:
            feature_names = [f"f{i}" for i in range(X_train_tx.shape[1])]

        from shap import TreeExplainer, Explainer
        is_tree = model_name in {"RandomForest", "GBM", "XGBoost", "LightGBM"}

        if is_tree:
            explainer = TreeExplainer(
                model_fitted,
                data=X_train_tx,
                feature_perturbation="interventional"
            )
            shap_values = explainer(X_test_tx, check_additivity=False)
        else:
            explainer = Explainer(model_fitted, X_train_tx)
            shap_values = explainer(X_test_tx)

        # Plot -> buffer -> base64
        X_test_df = pd.DataFrame(X_test_tx, columns=feature_names)
        plt.figure(figsize=(8, 6))
        shap.summary_plot(shap_values, X_test_df, show=False, max_display=25)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("ascii")

        html_content += "<h3>SHAP summary</h3>"
        html_content += f'<img alt="SHAP summary" '
        html_content += f'style="max-width:100%;height:auto" '
        html_content += f'src="data:image/png;base64,{img_b64}"><br>'
    except Exception as e:
        html_content += f"<p>⚠️ No se pudo generar SHAP: {e}</p>"



    html_content += "</body></html>"

    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Reporte guardado en {html_output_path}")
    return best_model, search.best_params_, {"mse": mse, "mae": mae, "r2": r2}
