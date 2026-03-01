# Changelog

Todos los cambios importantes de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-01

### Added
- Estructura de pipeline end-to-end de Spotify Growth ML con `src/`, `notebooks/`, `data/`, `reports/` y setup local reproducible mediante `requirements.txt` + `.env.example`.
- Flujo de autenticación OAuth de usuario en `src/auth/spotify_oauth.py` con servidor local de callback, validación de estado CSRF, persistencia de tokens y soporte de refresh.
- Cliente de Spotify API en `src/data_ingestion/spotify_client.py` con:
  - manejo de tokens de usuario y aplicación,
  - búsqueda de playlists y tracks,
  - paginación de ítems de playlists,
  - obtención de audio-features por lotes,
  - manejo básico de reintentos/rate-limit para HTTP 429.
- Scripts de ingesta RAW para tres fuentes complementarias:
  - `build_spotify_raw_dataset.py` (playlists de usuario),
  - `build_spotify_raw_dataset_public_playlists.py` (playlists públicas descubiertas por query),
  - `build_spotify_raw_dataset_search_tracks.py` (búsqueda de tracks por patrones genéricos).
- Script de merge RAW `src/data_ingestion/merge_raw_datasets.py` para concatenar los datasets raw más recientes y deduplicar por `track_id`.
- Utilidad de reportes `src/utils/generate_report.py` para ejecutar notebooks y exportar reportes HTML con timestamp.
- Documentación estática de análisis en `reports/` para EDA, Feature Engineering y Modeling.
- Artefactos de performance de modelado en `reports/03_modeling/model_performance/`.

### Changed
- Documentación del proyecto actualizada para reflejar el estado real actual del pipeline y la finalización de la etapa de modelado.
- Política de retención del repositorio formalizada para artefactos versionados por timestamp:
  - conservar solo la última versión con timestamp por familia para `.csv` y `.parquet`,
  - eliminar archivos canónicos sin timestamp cuando existan artefactos equivalentes con timestamp.
- `README.md` alineado con outputs ejecutados y resultados actuales del modelo (modelo ganador, métricas y mapa de artefactos).

### Fixed
- Inconsistencias de documentación donde el proyecto se describía como pre-modelado, aunque ya existían outputs de modelado.
- Referencias de reportes ajustadas al naming actual de análisis (`ANALYSIS_YYYYMMDD.md`) usado en los artefactos del repositorio.

### Notes
- Última ejecución documentada de EDA/FE/Modeling (baseline v1.0):
  - Reporte EDA: `reports/01_eda/ANALYSIS_20260301.md`
  - Reporte Feature Engineering: `reports/02_feature_engineering/ANALYSIS_20260301.md`
  - Reporte Modeling: `reports/03_modeling/ANALYSIS_20260301.md`
- Modelo baseline ganador de la última ejecución de modelado:
  - Modelo: `RandomForest`
  - ROC-AUC: `0.9438`
  - PR-AUC: `0.8818`
  - F1 (clase positiva): `0.7934`
  - Accuracy: `0.8699`
