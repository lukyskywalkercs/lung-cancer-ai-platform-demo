from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def _choose_key(df: pd.DataFrame) -> str | None:
    priority = [
        "DepMap_ID",
        "sample_id",
        "Sample_ID",
        "sampleID",
        "CELL_LINE_NAME",
        "cell_line",
    ]
    for col in priority:
        if col in df.columns:
            return col
    return None


def merge_processed_tables(output_name: str = "integrated_dataset.parquet") -> Path | None:
    files = sorted(PROCESSED_DIR.glob("*_clean.parquet"))
    if len(files) < 2:
        print("[INFO] Se necesitan al menos 2 tablas procesadas para integrar.")
        return None

    base = pd.read_parquet(files[0])
    key = _choose_key(base)
    if key is None:
        print(f"[INFO] No se encontro clave de union en {files[0].name}.")
        return None

    merged = base.copy()
    print(f"[MERGE] Base: {files[0].name} con clave '{key}'")

    for path in files[1:]:
        df = pd.read_parquet(path)
        df_key = _choose_key(df)
        if df_key is None:
            print(f"[SKIP] {path.name}: sin clave de union compatible.")
            continue

        if df_key != key:
            df = df.rename(columns={df_key: key})

        before = len(merged)
        merged = merged.merge(df, on=key, how="outer", suffixes=("", f"_{path.stem}"))
        print(f"[OK] + {path.name}: {before} -> {len(merged)} filas")

    output = PROCESSED_DIR / output_name
    merged.to_parquet(output, index=False)
    print(f"[DONE] Dataset integrado guardado en {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Integra tablas procesadas en un dataset unico.")
    parser.add_argument(
        "--output-name",
        default="integrated_dataset.parquet",
        help="Nombre del archivo de salida en data/processed.",
    )
    args = parser.parse_args()
    merge_processed_tables(output_name=args.output_name)


if __name__ == "__main__":
    main()
