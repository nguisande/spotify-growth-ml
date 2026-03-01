# Spotify Growth ML — Prediccion de Popularidad y Senales de Engagement

## Descripcion del proyecto

Proyecto de Data Science end-to-end orientado a Growth Marketing para predecir `popular_high` (popularidad alta) de canciones en Spotify.

El flujo cubre:
- Ingesta via Spotify Web API con OAuth de usuario.
- Consolidacion de datasets RAW versionados.
- EDA y definicion de target binario (P70).
- Feature engineering para cerrar un dataset model-ready.
- Modelado supervisado y comparacion de baselines.

## Objetivo

Anticipar potencial de engagement de canciones usando metadatos de tracks, artistas y playlists, con practicas reproducibles de pipeline y documentacion.

## Estructura del proyecto

```bash
spotify-growth-ml/
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_hipothesis.ipynb
├── src/
│   ├── config.py
│   ├── auth/
│   │   └── spotify_oauth.py
│   ├── data_ingestion/
│   │   ├── spotify_client.py
│   │   ├── build_spotify_raw_dataset.py
│   │   ├── build_spotify_raw_dataset_public_playlists.py
│   │   ├── build_spotify_raw_dataset_search_tracks.py
│   │   └── merge_raw_datasets.py
│   └── utils/
│       └── generate_report.py
├── reports/
│   ├── 01_eda/
│   ├── 02_feature_engineering/
│   ├── 03_modeling/
│   └── README.md
└── tokens/
```

## Data source y limitaciones

Fuente principal: [Spotify Developer](https://developer.spotify.com/)

Limitaciones relevantes:
- `/search` de Spotify limita paginacion a `offset + limit <= 1000`.
- Se escala volumen combinando 3 fuentes (`user_playlists`, `public_playlists`, `search_tracks`) y deduplicando por `track_id`.

## Dataset RAW (merged)

Columnas principales:
- `track_id`, `track_name`, `track_popularity`, `duration_ms`, `explicit`
- `album_id`, `album_name`, `album_release_date`
- `artist_id`, `artist_name`
- `playlist_id`, `playlist_name`, `added_at`
- `source`, `search_query`, `search_market`

Notas:
- `search_query` y `search_market` son nulos cuando la fuente es playlist.
- `playlist_id/playlist_name` pueden ser nulos cuando la fuente es `search_tracks`.

## Como replicar

### 1) Setup

```bash
git clone <repo_url>
cd spotify-growth-ml
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Completar `.env`:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### 2) OAuth de usuario

```bash
python -m src.auth.spotify_oauth
```

Abrir:

```text
http://127.0.0.1:8888/login
```

Se genera `tokens/spotify_tokens.json`.

### 3) Ingesta RAW

```bash
python -m src.data_ingestion.build_spotify_raw_dataset
python -m src.data_ingestion.build_spotify_raw_dataset_public_playlists
python -m src.data_ingestion.build_spotify_raw_dataset_search_tracks
python -m src.data_ingestion.merge_raw_datasets
```

### 4) EDA / FE / Modeling

```bash
jupyter notebook
```

Orden recomendado:
- `notebooks/01_eda.ipynb`
- `notebooks/02_feature_engineering.ipynb`
- `notebooks/03_modeling.ipynb`

## Estado actual (v1.0.0)

- Ingesta OAuth + 3 fuentes RAW: completado.
- EDA y definicion de target `popular_high` (P70): completado.
- Feature engineering y dataset model-ready: completado.
- Modelado baseline y comparacion de 5 modelos: completado.

## Resultado de modelado (ultima corrida)

Dataset usado: `data/processed/spotify_model_ready_20260301_005928.parquet`

Modelo ganador por metrica primaria (ROC-AUC): **RandomForest**
- ROC-AUC: `0.9438`
- PR-AUC: `0.8818`
- F1 (clase positiva): `0.7934`
- Accuracy: `0.8699`

Artefactos en `reports/03_modeling/model_performance/`:
- `model_comparison_*.csv`
- `best_model_test_predictions_*.csv`
- `best_model_classification_report_*.csv`
- `best_model_confusion_matrix_*.csv`
- `best_model_feature_importance_*.csv`

## Documentacion y reportes

Los notebooks contienen codigo ejecutable.
`reports/` contiene documentacion estatica de ejecuciones puntuales.

Analisis versionados actuales:
- `reports/01_eda/ANALYSIS_20260301.md`
- `reports/02_feature_engineering/ANALYSIS_20260301.md`
- `reports/03_modeling/ANALYSIS_20260301.md`

## Politica de versionado de artefactos (GitHub)

Para evitar crecimiento innecesario del repositorio:
- Se conserva solo la **ultima version con timestamp por familia** para `.csv` y `.parquet`.
- Se eliminan versiones historicas anteriores.
- Se eliminan archivos canonicos sin timestamp cuando duplican la misma familia (por ejemplo en `model_performance`).

Familias administradas:
- RAW: `spotify_tracks_playlists_raw_*`, `spotify_tracks_public_playlists_raw_*`, `spotify_tracks_search_raw_*`, `spotify_tracks_merged_raw_*`
- INTERIM: `spotify_tracks_interim_*`
- PROCESSED: `spotify_model_ready_*`
- MODEL PERFORMANCE CSV: `model_comparison_*`, `best_model_test_predictions_*`, `best_model_classification_report_*`, `best_model_confusion_matrix_*`, `best_model_feature_importance_*`

## Roadmap sugerido (v1.1+)

- Validacion cruzada y/o validacion temporal para robustez.
- Tuning de hiperparametros en RandomForest y GradientBoosting.
- Definicion de umbral operativo segun objetivo de negocio (precision vs recall).
- Integracion de senales externas (por ejemplo Google Trends).

---

Autor: Nicolas Guisande
