# Runbook operativo para laboratorio

## Objetivo
Ejecutar el pipeline completo con datos publicos reales, generar rankings de dianas y revisar resultados en dashboard.

## Requisitos
- Python disponible en terminal (`python --version`).
- Entorno virtual activo (venv) o Conda.
- Archivo `data/external/sources.json` con URLs oficiales directas.

## Paso 1: configurar fuentes de datos
Editar `data/external/sources.json`:
- `depmap_expression`
- `depmap_mutations`
- `depmap_crispr`
- `depmap_prism`
- `gdsc`
- `tcga_portal`

No usar datos inventados ni rutas de prueba.

## Paso 2: descarga de datos
```bash
python src/data/download_depmap.py --sources-config data/external/sources.json
```

Validacion esperada:
- Se crea `data/raw/download_manifest.json`.
- El manifiesto incluye `key`, `url`, `path`, `sha256`.

## Paso 3: preprocesado
```bash
python src/data/preprocess.py
```

Salida esperada:
- Archivos `*_clean.parquet` en `data/processed`.

## Paso 4: integracion
```bash
python src/data/merge.py
```

Salida esperada:
- `data/processed/integrated_dataset.parquet`.

## Paso 5: entrenamiento IA de dianas
```bash
python src/models/target_model.py --subtype global --target-col age_at_initial_pathologic_diagnosis --top-n 80
python src/models/target_model.py --dataset data/processed/LUAD_clinicalMatrix_clean.parquet --subtype luad --target-col age_at_initial_pathologic_diagnosis --top-n 80
python src/models/target_model.py --dataset data/processed/LUSC_clinicalMatrix_clean.parquet --subtype lusc --target-col age_at_initial_pathologic_diagnosis --top-n 80
```

Salidas esperadas:
- `target_ranking.csv`
- `target_ranking_luad.csv`
- `target_ranking_lusc.csv`
- metadatos `target_model_metadata*.json`

## Paso 6: visualizacion
```bash
streamlit run src/dashboard/app.py
```

Revisar pestañas:
- `Visor de pipeline`
- `Trazabilidad de datos`
- `Priorizacion de dianas`

## Criterios de aceptacion minima
- Fuentes configuradas en `sources.json`.
- Manifiesto de descarga no vacio.
- Ranking generado para el subtipo a evaluar.
- Top de dianas revisado por el equipo experimental.

## Nota para esta demo
- Esta demo usa matrices clinicas TCGA LUAD/LUSC (fuente oficial UCSC Xena) para demostrar pipeline reproducible de extremo a extremo.
- En un proyecto de laboratorio real, el objetivo debe migrar a endpoints biologicos/farmacologicos (dependency, IC50, respuesta a tratamiento) y no quedarse en un endpoint clinico de demostracion.
