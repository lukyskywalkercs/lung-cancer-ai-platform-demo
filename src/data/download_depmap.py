from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Fuentes publicas iniciales (URLs oficiales; pueden cambiar por release)
DEFAULT_SOURCES = {
    "depmap_expression": "",
    "depmap_mutations": "",
    "depmap_crispr": "",
    "depmap_prism": "",
    "gdsc": "https://www.cancerrxgene.org/downloads/bulk_download",
    "tcga_portal": "https://portal.gdc.cancer.gov/",
}


def _read_sources_config(path: Path | None) -> dict[str, str]:
    if path is None:
        return DEFAULT_SOURCES.copy()
    with path.open("r", encoding="utf-8") as f:
        user_sources = json.load(f)
    merged = DEFAULT_SOURCES.copy()
    merged.update(user_sources)
    return merged


def _target_filename(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or "downloaded_file"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, destination: Path, timeout: int = 120) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with destination.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descarga datasets publicos para el proyecto de cancer pulmonar."
    )
    parser.add_argument(
        "--sources-config",
        type=Path,
        default=None,
        help="Ruta a JSON con URLs reales de datasets (opcional).",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Lista de claves concretas a descargar.",
    )
    args = parser.parse_args()

    sources = _read_sources_config(args.sources_config)
    selected_keys = set(args.only) if args.only else set(sources.keys())

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RAW_DIR / "download_manifest.json"
    manifest: list[dict[str, str]] = []

    for key, url in sources.items():
        if key not in selected_keys:
            continue

        if not url:
            print(
                f"[SKIP] {key}: sin URL configurada. "
                "Define una URL directa en --sources-config para descargar este dataset."
            )
            continue

        file_name = _target_filename(url)
        target = RAW_DIR / file_name
        print(f"[DOWNLOADING] {key} -> {target}")

        try:
            _download(url, target)
            checksum = _sha256_file(target)
            manifest.append(
                {
                    "key": key,
                    "url": url,
                    "path": str(target.relative_to(PROJECT_ROOT)),
                    "sha256": checksum,
                }
            )
            print(f"[OK] {key}: {target.name} ({checksum[:12]}...)")
        except requests.HTTPError as exc:
            print(f"[ERROR] {key}: HTTP {exc.response.status_code} en {url}")
        except requests.RequestException as exc:
            print(f"[ERROR] {key}: fallo de red -> {exc}")
        except Exception as exc:  # pragma: no cover
            print(f"[ERROR] {key}: fallo inesperado -> {exc}")

    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[MANIFEST] Guardado en {manifest_path}")


if __name__ == "__main__":
    main()
