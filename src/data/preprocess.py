from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".csv"}:
        return pd.read_csv(path)
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t")
    if suffix in {".parquet"}:
        return pd.read_parquet(path)
    if path.name.endswith("clinicalMatrix") or suffix == "":
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Formato no soportado para {path.name}")


def _basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    out = out.drop_duplicates()
    if "DepMap_ID" in out.columns:
        out["DepMap_ID"] = out["DepMap_ID"].astype(str).str.strip()
    for col in out.columns:
        if out[col].dtype == "object":
            numeric = pd.to_numeric(out[col], errors="coerce")
            if numeric.notna().mean() >= 0.7:
                out[col] = numeric
    return out


def preprocess_all() -> list[Path]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    candidates = sorted(
        [
            p
            for p in RAW_DIR.glob("*")
            if p.is_file()
            and (
                p.suffix.lower() in {".csv", ".tsv", ".txt", ".parquet"}
                or p.name.endswith("clinicalMatrix")
                or p.suffix == ""
            )
        ]
    )

    if not candidates:
        print("[INFO] No se encontraron tablas crudas en data/raw.")
        return generated

    for src in candidates:
        try:
            df = _read_table(src)
            clean = _basic_clean(df)
            clean["_source_file"] = src.name
            dst = PROCESSED_DIR / f"{src.stem}_clean.parquet"
            clean.to_parquet(dst, index=False)
            generated.append(dst)
            print(f"[OK] {src.name} -> {dst.name} ({len(clean)} filas)")
        except Exception as exc:
            print(f"[ERROR] {src.name}: {exc}")

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocesamiento inicial de tablas publicas.")
    _ = parser.parse_args()
    generated = preprocess_all()
    print(f"[DONE] Archivos generados: {len(generated)}")


if __name__ == "__main__":
    main()
