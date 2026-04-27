from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNetCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"


TARGET_HINTS = [
    "dependency",
    "crispr",
    "essential",
    "viability",
    "ic50",
    "auc",
    "sensitivity",
]


def _resolve_subtype_mask(df: pd.DataFrame, subtype: str) -> pd.Series:
    if subtype.lower() == "global":
        return pd.Series([True] * len(df), index=df.index)

    query = subtype.lower()
    candidate_cols = [
        c
        for c in df.columns
        if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == "object"
    ]
    if not candidate_cols:
        raise ValueError("No hay columnas de texto para filtrar subtipo LUAD/LUSC.")

    mask = pd.Series([False] * len(df), index=df.index)
    for col in candidate_cols:
        mask = mask | df[col].astype(str).str.lower().str.contains(query, na=False)

    if not mask.any():
        raise ValueError(
            f"No se encontraron filas para subtipo '{subtype}'. "
            "Revisa que exista en columnas de texto del dataset."
        )
    return mask


def _load_integrated_dataset(path: Path | None) -> pd.DataFrame:
    if path is not None:
        return pd.read_parquet(path)

    integrated = PROCESSED_DIR / "integrated_dataset.parquet"
    if integrated.exists():
        return pd.read_parquet(integrated)

    parquet_files = sorted(PROCESSED_DIR.glob("*_clean.parquet"))
    if not parquet_files:
        raise FileNotFoundError(
            "No hay datos procesados. Ejecuta preprocess.py y merge.py antes del modelo."
        )
    return pd.read_parquet(parquet_files[0])


def _find_target_column(df: pd.DataFrame) -> str | None:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    for col in numeric_cols:
        lowered = col.lower()
        if any(hint in lowered for hint in TARGET_HINTS):
            return col
    return None


def _gene_like_features(columns: list[str]) -> list[str]:
    excluded_exact = {"DepMap_ID", "sample_id", "Sample_ID", "CELL_LINE_NAME", "cell_line"}
    out: list[str] = []
    for col in columns:
        if col in excluded_exact:
            continue
        if col.endswith("_id") or col.endswith("_ID"):
            continue
        out.append(col)
    return out


def train_target_prioritization(
    dataset_path: Path | None = None,
    top_n: int = 200,
    subtype: str = "global",
    target_col: str | None = None,
) -> tuple[Path, Path]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = _load_integrated_dataset(dataset_path)
    if df.empty:
        raise ValueError("El dataset cargado esta vacio.")

    subtype_mask = _resolve_subtype_mask(df, subtype=subtype)
    df = df.loc[subtype_mask].copy()
    if df.empty:
        raise ValueError(f"Dataset vacio tras filtrar subtipo '{subtype}'.")

    if target_col is None:
        target_col = _find_target_column(df)
    if target_col is None:
        raise ValueError(
            "No se encontro columna objetivo numerica (dependency/crispr/ic50/etc). "
            "Revisa columnas de entrada reales."
        )
    if target_col not in df.columns:
        raise ValueError(f"La columna objetivo '{target_col}' no existe en el dataset.")

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    feature_cols = [c for c in numeric_cols if c != target_col]
    feature_cols = _gene_like_features(feature_cols)
    if len(feature_cols) < 5:
        raise ValueError("Muy pocas features numericas para entrenar baseline.")

    model_df = df[feature_cols + [target_col]].copy()
    model_df[target_col] = pd.to_numeric(model_df[target_col], errors="coerce")
    model_df = model_df.dropna(subset=[target_col])
    # Evita columnas sin datos observables (fallan en imputacion).
    valid_feature_cols = [c for c in feature_cols if model_df[c].notna().any()]
    feature_cols = valid_feature_cols
    if len(feature_cols) < 5:
        raise ValueError("Muy pocas features validas tras filtrar columnas vacias.")
    X = model_df[feature_cols]
    y = model_df[target_col]

    if len(model_df) < 30:
        raise ValueError("Filas insuficientes para entrenar un baseline robusto (<30).")

    rf = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)),
        ]
    )
    rf.fit(X, y)
    rf_importance = rf.named_steps["model"].feature_importances_

    enet = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", ElasticNetCV(l1_ratio=[0.1, 0.5, 0.9, 1.0], random_state=42)),
        ]
    )
    enet.fit(X, y)
    enet_coef = np.abs(enet.named_steps["model"].coef_)

    ranking = pd.DataFrame(
        {
            "feature": feature_cols,
            "rf_importance": rf_importance,
            "elasticnet_abs_coef": enet_coef,
        }
    )
    ranking["rf_importance_norm"] = ranking["rf_importance"] / (
        ranking["rf_importance"].max() + 1e-12
    )
    ranking["elasticnet_norm"] = ranking["elasticnet_abs_coef"] / (
        ranking["elasticnet_abs_coef"].max() + 1e-12
    )
    ranking["consensus_score"] = (
        0.6 * ranking["rf_importance_norm"] + 0.4 * ranking["elasticnet_norm"]
    )
    ranking = ranking.sort_values("consensus_score", ascending=False).reset_index(drop=True)
    ranking["rank"] = np.arange(1, len(ranking) + 1)

    subtype_slug = subtype.lower()
    ranking_file = "target_ranking.csv" if subtype_slug == "global" else f"target_ranking_{subtype_slug}.csv"
    metadata_file = (
        "target_model_metadata.json"
        if subtype_slug == "global"
        else f"target_model_metadata_{subtype_slug}.json"
    )
    ranking_path = PROCESSED_DIR / ranking_file
    ranking.head(top_n).to_csv(ranking_path, index=False)

    metadata = {
        "subtype": subtype.upper() if subtype_slug != "global" else "GLOBAL",
        "target_column": target_col,
        "n_rows_train": int(len(model_df)),
        "n_features": int(len(feature_cols)),
        "top_n_saved": int(top_n),
        "ranking_path": str(ranking_path.relative_to(PROJECT_ROOT)),
        "models": ["RandomForestRegressor", "ElasticNetCV"],
    }
    metadata_path = PROCESSED_DIR / metadata_file
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return ranking_path, metadata_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline IA para priorizacion de dianas.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Ruta opcional a parquet integrado.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=200,
        help="Numero de features priorizadas a guardar.",
    )
    parser.add_argument(
        "--subtype",
        type=str,
        default="global",
        choices=["global", "luad", "lusc"],
        help="Subtipo para entrenamiento: global, luad o lusc.",
    )
    parser.add_argument(
        "--target-col",
        type=str,
        default=None,
        help="Columna objetivo numerica explicita (opcional).",
    )
    args = parser.parse_args()

    ranking_path, metadata_path = train_target_prioritization(
        dataset_path=args.dataset,
        top_n=args.top_n,
        subtype=args.subtype,
        target_col=args.target_col,
    )
    print(f"[OK] Ranking guardado en: {ranking_path}")
    print(f"[OK] Metadata guardada en: {metadata_path}")


if __name__ == "__main__":
    main()
