Lung Cancer AI Platform – Proyecto Público
Plataforma computacional para priorización de dianas, análisis de resistencia y combinaciones terapéuticas en cáncer de pulmón usando datasets públicos

📌 1. Objetivo del proyecto
Desarrollar una plataforma computacional basada en datos públicos que permita:

Priorizar nuevas dianas terapéuticas.

Identificar mecanismos de resistencia.

Explorar combinaciones de fármacos.

Generar dashboards interactivos para investigadores.

Demostrar que un técnico informático puede colaborar en remoto con un laboratorio experimental.

Todo el proyecto se construye con datos públicos, IA reproducible y código abierto.

📌 2. Datasets públicos utilizados
Los datos provienen exclusivamente de fuentes abiertas:

DepMap Public (CCLE)
RNA-seq

Mutaciones

CRISPR knockout (gene dependency)

PRISM drug response

https://depmap.org

GDSC (Genomics of Drug Sensitivity in Cancer)
IC50 de cientos de fármacos

Datos moleculares asociados

https://www.cancerrxgene.org/

TCGA LUAD / LUSC
RNA-seq

Mutaciones

Datos clínicos

https://portal.gdc.cancer.gov/ (portal.gdc.cancer.gov in Bing)

📌 3. Arquitectura del proyecto
Código
lung-cancer-ai-platform/
│
├── data/
│   ├── raw/                # Datos públicos descargados sin modificar
│   ├── processed/          # Datos limpios y normalizados
│   └── external/           # Anotaciones de genes, targets de fármacos
│
├── notebooks/
│   ├── 01_data_overview.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_target_prioritization.ipynb
│   ├── 04_resistance_analysis.ipynb
│   ├── 05_drug_combinations.ipynb
│   └── 06_dashboard_prototype.ipynb
│
├── src/
│   ├── data/
│   │   ├── download_depmap.py
│   │   ├── preprocess.py
│   │   └── merge.py
│   │
│   ├── models/
│   │   ├── target_model.py
│   │   ├── resistance_model.py
│   │   └── synergy_model.py
│   │
│   ├── utils/
│   │   ├── plotting.py
│   │   ├── metrics.py
│   │   └── io.py
│   │
│   └── dashboard/
│       └── app.py
│
├── models/
│   ├── target_model.pkl
│   ├── resistance_classifier.pkl
│   └── synergy_predictor.pkl
│
├── docs/
│   ├── project_overview.md
│   ├── data_sources.md
│   ├── methods.md
│   └── results/
│
├── environment.yml
├── README.md
└── .gitignore

📌 4. Tecnologías utilizadas
Lenguaje
Python 3.10+

IA / Machine Learning
scikit-learn

XGBoost

Scanpy

DeepChem

Procesamiento de datos
pandas

numpy

scipy

Visualización
seaborn

matplotlib

plotly

Dashboard
Streamlit

Gradio (opcional)

📌 5. Módulos del proyecto
Módulo 1 — Priorización de dianas
Usa:

RNA-seq

CRISPR knockout

Mutaciones

Respuesta a fármacos

Técnicas:

Modelos supervisados (Random Forest, ElasticNet)

Importancia de características

Análisis diferencial

Redes de coexpresión

Salida:

Ranking de dianas con evidencia múltiple.

Módulo 2 — Mecanismos de resistencia
Usa:

Líneas sensibles vs resistentes

Expresión génica

Dependencia genética

Técnicas:

PCA / UMAP

Clustering

Clasificadores sensibles/resistentes

Salida:

Rutas alteradas

Genes asociados a resistencia

Vulnerabilidades potenciales

Módulo 3 — Combinaciones terapéuticas
Usa:

PRISM drug response

GDSC IC50

Targets de fármacos

Técnicas:

Modelos de sinergia (DeepChem)

Recomendadores basados en similitud

Regresión multivariante

Salida:

Lista priorizada de combinaciones candidatas

Módulo 4 — Dashboard web
Prototipo en Streamlit:

Exploración de dianas

Visualización de resistencia

Combinaciones sugeridas

Gráficos interactivos

📌 6. Flujo de trabajo
Descarga de datos públicos

Limpieza y normalización

Integración de datasets

Entrenamiento de modelos IA

Generación de informes

Construcción del dashboard

Documentación para la IP

📌 7. Plan de trabajo (6 semanas)
Semana	Actividad
1	Descarga de datos + overview
2	Preprocesamiento + integración
3	Módulo de dianas
4	Módulo de resistencia
5	Módulo de combinaciones
6	Dashboard + documentación

📌 8. Coste del proyecto
El proyecto puede ejecutarse con coste 0 €, usando:

Datos públicos

Python local

Streamlit Cloud (gratis)

GitHub privado (gratis)

Coste opcional (si se desea GPU o hosting premium): 5–20 €/mes.

📌 9. Objetivo final para la IP
Entregar:

Un repositorio funcional

Un dashboard navegable

Resultados reales con datos públicos

Un informe claro y reproducible

Demostración de que puedes trabajar en remoto con rigor científico
