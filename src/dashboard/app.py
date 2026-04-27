from pathlib import Path
import json

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Lung Cancer AI Platform", page_icon="🫁", layout="wide")

BASE_PATH = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_PATH / "data" / "raw"
PROCESSED_DIR = BASE_PATH / "data" / "processed"
EXTERNAL_DIR = BASE_PATH / "data" / "external"
SOURCES_PATH = EXTERNAL_DIR / "sources.json"
MANIFEST_PATH = RAW_DIR / "download_manifest.json"
UPLOADED_RANKING_PATH = PROCESSED_DIR / "target_ranking_uploaded.csv"
DEMO_DIR = BASE_PATH / "demo_assets"
DEMO_SOURCES_PATH = DEMO_DIR / "sources_demo.json"
DEMO_MANIFEST_PATH = DEMO_DIR / "download_manifest_demo.json"

st.markdown(
    """
<style>
.upload-highlight {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1e3a8a;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
    font-weight: 600;
}
.lab-help {
    background: #ecfeff;
    border: 1px solid #67e8f9;
    color: #164e63;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}
</style>
""",
    unsafe_allow_html=True,
)


def status_badge(is_ready: bool) -> str:
    return "Listo" if is_ready else "Pendiente"


def _availability_label(primary: Path, fallback: Path | None = None) -> str:
    if primary.exists():
        return "Listo"
    if fallback is not None and fallback.exists():
        return "Demo precargada"
    return "Pendiente"


def _target_paths_for_mode(study_mode: str) -> tuple[Path, Path]:
    mode = study_mode.lower()
    if mode == "global":
        primary = PROCESSED_DIR / "target_ranking.csv"
        fallback = DEMO_DIR / "target_ranking_demo.csv"
        ranking = primary if primary.exists() else fallback
        return (ranking, PROCESSED_DIR / "target_model_metadata.json")
    primary = PROCESSED_DIR / f"target_ranking_{mode}.csv"
    fallback = DEMO_DIR / f"target_ranking_{mode}_demo.csv"
    ranking = primary if primary.exists() else fallback
    return (ranking, PROCESSED_DIR / f"target_model_metadata_{mode}.json")


def load_target_ranking(study_mode: str) -> pd.DataFrame | None:
    ranking_path, _ = _target_paths_for_mode(study_mode)
    if ranking_path.exists():
        return pd.read_csv(ranking_path)
    return None


def load_sources() -> dict | None:
    source_path = SOURCES_PATH if SOURCES_PATH.exists() else DEMO_SOURCES_PATH
    if not source_path.exists():
        return None
    with source_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest() -> list[dict] | None:
    manifest_path = MANIFEST_PATH if MANIFEST_PATH.exists() else DEMO_MANIFEST_PATH
    if not manifest_path.exists():
        return None
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def _build_uploaded_ranking(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    work = _coerce_numeric(df)
    numeric_cols = [c for c in work.columns if pd.api.types.is_numeric_dtype(work[c])]
    if target_col not in numeric_cols:
        raise ValueError("La columna objetivo debe ser numerica.")
    features = [c for c in numeric_cols if c != target_col]
    if len(features) < 1:
        raise ValueError("No hay columnas numericas predictoras disponibles.")
    frame = work[features + [target_col]].dropna(subset=[target_col]).copy()
    if len(frame) < 20:
        raise ValueError("Filas insuficientes para analisis (minimo recomendado: 20).")

    rows = []
    for col in features:
        valid = frame[[col, target_col]].dropna()
        if len(valid) < 8:
            continue
        corr = valid[col].corr(valid[target_col])
        rows.append({"feature": col, "score": abs(float(corr)) if pd.notna(corr) else 0.0})

    ranking = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    ranking["rank"] = range(1, len(ranking) + 1)
    ranking.rename(columns={"score": "consensus_score"}, inplace=True)
    return ranking[["rank", "feature", "consensus_score"]]


st.title("🫁 Lung Cancer AI Platform")
st.caption(
    "Priorizacion de dianas, resistencia y combinaciones terapeuticas con datasets publicos y pipeline reproducible."
)
st.info(
    "Este dashboard no consulta datos remotamente en tiempo real. Solo visualiza artefactos locales generados por el pipeline."
)
st.caption(
    "Si no hay datos propios cargados, la app puede mostrar resultados demo precargados para facilitar la evaluacion inicial."
)

with st.sidebar:
    st.header("Control de estudio")
    study_mode = st.selectbox("Subtipo", options=["Global", "LUAD", "LUSC"], index=0)
    top_n_default = st.slider("Top dianas", 5, 100, 20, step=5)
    st.divider()
    selected_ranking_path, _ = _target_paths_for_mode(study_mode)
    target_ready = selected_ranking_path.exists() or UPLOADED_RANKING_PATH.exists()
    resistance_ready = (PROCESSED_DIR / "resistance_signatures.csv").exists()
    comb_ready = (PROCESSED_DIR / "drug_combination_ranking.csv").exists()
    st.caption("Estado rapido")
    st.write(f"- Dianas: {status_badge(target_ready)}")
    st.write(f"- Resistencia: {status_badge(resistance_ready)}")
    st.write(f"- Combinaciones: {status_badge(comb_ready)}")

col1, col2, col3 = st.columns(3)
col1.metric("Modulo dianas", status_badge(target_ready))
col2.metric("Modulo resistencia", status_badge(resistance_ready))
col3.metric("Modulo combinaciones", status_badge(comb_ready))

tab_overview, tab_trace, tab_targets, tab_upload, tab_lab = st.tabs(
    [
        "Visor de pipeline",
        "Trazabilidad de datos",
        "Priorizacion de dianas",
        "🔵 Carga de datos (demo)",
        "Guia laboratorio (que es esta web)",
    ]
)

with tab_overview:
    st.subheader("Estado de pipeline")
    st.caption("Fuente de datos usada en esta vista: artefactos locales del proyecto (pipeline propio o demo precomputada).")
    sources_state = _availability_label(SOURCES_PATH, DEMO_SOURCES_PATH)
    manifest_state = _availability_label(MANIFEST_PATH, DEMO_MANIFEST_PATH)
    uploaded_state = _availability_label(UPLOADED_RANKING_PATH)
    st.write(f"- Config fuentes (`data/external/sources.json`): **{sources_state}**")
    st.write(f"- Manifiesto descarga (`data/raw/download_manifest.json`): **{manifest_state}**")
    st.write(
        f"- Ranking por carga (`data/processed/target_ranking_uploaded.csv`): "
        f"**{uploaded_state}**"
    )
    processed_files = sorted([p.name for p in PROCESSED_DIR.glob("*") if p.is_file()]) if PROCESSED_DIR.exists() else []
    if not processed_files and DEMO_DIR.exists():
        processed_files = sorted([p.name for p in DEMO_DIR.glob("*ranking*") if p.is_file()])
    st.write(f"- Archivos en `data/processed`: **{len(processed_files)}**")
    if processed_files:
        st.dataframe(pd.DataFrame({"archivo": processed_files}), use_container_width=True)
    else:
        st.info("Todavia no hay artefactos propios en `data/processed`.")

    st.markdown("### Comandos de ejecucion")
    st.code(
        "\n".join(
            [
                "python src/data/download_depmap.py --sources-config data/external/sources.json",
                "python src/data/preprocess.py",
                "python src/data/merge.py",
                "python src/models/target_model.py --subtype global --target-col age_at_initial_pathologic_diagnosis --top-n 80",
                "python src/models/target_model.py --dataset data/processed/LUAD_clinicalMatrix_clean.parquet --subtype luad --target-col age_at_initial_pathologic_diagnosis --top-n 80",
                "python src/models/target_model.py --dataset data/processed/LUSC_clinicalMatrix_clean.parquet --subtype lusc --target-col age_at_initial_pathologic_diagnosis --top-n 80",
                "streamlit run src/dashboard/app.py",
            ]
        ),
        language="bash",
    )

with tab_trace:
    st.subheader("Origen y trazabilidad de datos")
    st.caption("Fuente de datos usada en esta vista: archivos de configuracion y manifiesto de descargas del proyecto.")
    st.markdown(
        "- Las fuentes oficiales se configuran en `data/external/sources.json`.\n"
        "- La descarga local crea `data/raw/download_manifest.json` con URL, ruta local y SHA256."
    )

    sources = load_sources()
    if sources is None:
        st.info("Aun no hay configuracion de fuentes disponible.")
    else:
        if not SOURCES_PATH.exists() and DEMO_SOURCES_PATH.exists():
            st.warning("Mostrando configuracion de fuentes desde datos demo precargados.")
        sources_df = pd.DataFrame(
            [{"dataset": k, "url_configurada": v if v else "(sin URL)"} for k, v in sources.items()]
        )
        st.markdown("### Fuentes configuradas")
        st.dataframe(sources_df, use_container_width=True)

    manifest = load_manifest()
    if manifest is None:
        st.info("Aun no hay manifiesto de descarga disponible.")
    elif len(manifest) == 0:
        st.warning(
            "El manifiesto existe pero esta vacio. Revisa URLs directas en `sources.json` y vuelve a descargar."
        )
    else:
        if not MANIFEST_PATH.exists() and DEMO_MANIFEST_PATH.exists():
            st.warning("Mostrando manifiesto desde datos demo precargados.")
        st.markdown("### Artefactos descargados")
        man_df = pd.DataFrame(manifest)
        st.dataframe(man_df, use_container_width=True)

with tab_targets:
    st.subheader("Ranking de dianas (resultado IA)")
    st.markdown(
        """
**Nivel de evidencia actual del ranking mostrado:** `Reproducido computacionalmente (datos publicos)`

- **Exploratorio:** hallazgo inicial dentro de un dataset.
- **Reproducido computacionalmente:** se obtiene de forma consistente en ejecuciones reproducibles.
- **Validado experimentalmente:** confirmado por ensayos del laboratorio.
"""
    )
    target_ranking_path, target_metadata_path = _target_paths_for_mode(study_mode)
    using_uploaded = UPLOADED_RANKING_PATH.exists()
    ranking_df = pd.read_csv(UPLOADED_RANKING_PATH) if using_uploaded else load_target_ranking(study_mode)
    if ranking_df is None:
        st.info(
            "Aun no hay ranking generado para este modo. Puedes subir un CSV en la pestaña "
            "`Carga de datos (demo)` para ver resultados inmediatos."
        )
    else:
        if using_uploaded:
            st.success("Mostrando ranking generado con el CSV que has subido.")
            st.caption(f"Archivo: `{UPLOADED_RANKING_PATH.name}`")
            st.caption("Fuente de datos usada: CSV subido por el usuario en esta sesion.")
        elif "demo_assets" in str(target_ranking_path):
            st.info(
                "Mostrando ranking precomputado con datos publicos reales (TCGA) "
                f"incluidos para visualizacion inicial: `{target_ranking_path.name}`"
            )
            st.caption("Fuente de datos usada: TCGA LUAD/LUSC (UCSC Xena), precomputada y empaquetada en el proyecto.")
        else:
            st.success(f"Resultado cargado: `{target_ranking_path.name}`")
            st.caption("Fuente de datos usada: pipeline IA local del proyecto (datos publicos procesados).")
        top_n = st.slider("Top N para visualizar", 5, min(100, len(ranking_df)), top_n_default, 5)
        view_df = ranking_df.head(top_n).copy()
        st.dataframe(view_df, use_container_width=True)
        if {"feature", "consensus_score"}.issubset(view_df.columns):
            st.bar_chart(view_df.set_index("feature")["consensus_score"], use_container_width=True)
        if target_metadata_path.exists():
            st.caption(f"Metadata: `{target_metadata_path.name}`")

with tab_upload:
    st.subheader("Carga de datos del laboratorio (demo interactiva)")
    st.markdown(
        "<div class='upload-highlight'>Zona de prueba para subir datos y ver un ranking inmediato.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Sube un archivo `CSV` o `TSV`, selecciona una columna objetivo numerica y genera un ranking "
        "exploratorio inmediato."
    )
    st.warning(
        "El resultado de esta pestaña es **exploratorio**. No implica validacion biologica ni clinica. "
        "Sirve para priorizar hipotesis que luego debe confirmar el laboratorio."
    )
    uploaded = st.file_uploader("Archivo de datos", type=["csv", "tsv", "txt"])

    if uploaded is None:
        st.info(
            "Todavia no se ha subido ningun archivo. "
            "Cuando quieras, sube un CSV/TSV y la plataforma generara un ranking exploratorio."
        )
        st.caption("Fuente de datos usada: pendiente de carga por el usuario.")
    else:
        st.caption(f"Fuente de datos usada: archivo subido por el usuario (`{uploaded.name}`).")
        sep = "," if uploaded.name.lower().endswith(".csv") else "\t"
        raw_df = pd.read_csv(uploaded, sep=sep)
        st.write(f"Filas: **{len(raw_df)}** | Columnas: **{len(raw_df.columns)}**")
        st.dataframe(raw_df.head(20), use_container_width=True)

        numeric_candidates = []
        for col in raw_df.columns:
            numeric = pd.to_numeric(raw_df[col], errors="coerce")
            if numeric.notna().mean() >= 0.2:
                numeric_candidates.append(col)

        if not numeric_candidates:
            st.error("No se detectaron columnas numericas suficientes para generar ranking.")
        else:
            target_col = st.selectbox("Columna objetivo (numerica)", options=numeric_candidates, index=0)
            top_uploaded = st.slider("Top N del ranking subido", 5, 100, 20, step=5)
            if st.button("Generar ranking con archivo subido", type="primary"):
                try:
                    ranking_up = _build_uploaded_ranking(raw_df, target_col=target_col)
                    if ranking_up.empty:
                        st.error("No se pudo calcular ranking (datos insuficientes tras limpieza).")
                    else:
                        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
                        save_path = PROCESSED_DIR / "target_ranking_uploaded.csv"
                        ranking_up.to_csv(save_path, index=False)
                        st.success(f"Ranking generado y guardado en `{save_path.name}`")
                        st.info("Nivel de evidencia: **Exploratorio**")
                        st.dataframe(ranking_up.head(top_uploaded), use_container_width=True)
                        st.bar_chart(
                            ranking_up.head(top_uploaded).set_index("feature")["consensus_score"],
                            use_container_width=True,
                        )
                except Exception as exc:
                    st.error(f"No se pudo generar ranking: {exc}")

with tab_lab:
    st.subheader("Guia para entender la web")
    st.markdown(
        "<div class='lab-help'>Esta pestaña explica para qué sirve cada parte de la plataforma y cómo usar los resultados para tomar decisiones de investigación.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
### ¿Qué es esta web?
Es una plataforma para convertir datos de cáncer de pulmón en hipótesis priorizadas (dianas, resistencia y combinaciones), con trazabilidad y resultados visuales.

### ¿Qué ve el laboratorio aquí?
1. **Visor de pipeline:** si el flujo técnico se ejecutó correctamente.
2. **Trazabilidad de datos:** de dónde salen los datos y qué se descargó.
3. **Priorización de dianas:** ranking de variables/candidatos con score.
4. **Carga de datos:** prueba rápida con un archivo propio para ver utilidad potencial.

### ¿Cómo usar los resultados?
- El ranking no sustituye al laboratorio; sirve para **priorizar** qué validar primero.
- La IP/equipo experimental decide qué candidatos son más plausibles biológicamente.
- El valor práctico es reducir tiempo y coste de exploración inicial.

### Escala de validación
1. **Exploratorio:** ranking en un dataset único.
2. **Reproducido computacionalmente:** resultado estable en múltiples cohortes o corridas.
3. **Validado experimentalmente:** confirmado en líneas celulares / modelos preclínicos del grupo.

### Nota sobre privacidad
Si el laboratorio no quiere subir datos a servidores externos, se ejecuta todo en su propia infraestructura local o interna.
"""
    )
