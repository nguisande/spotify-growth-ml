# Changelog

Todos los cambios importantes de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-19

### Added
- Módulo 2 de regresión supervisada en `notebooks/03_modeling.ipynb`: 6 modelos (LinearRegression, Ridge, RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, BaggingRegressor), validación KFold(5), RandomizedSearchCV sobre RF y GradientBoosting, scatter y residual plots.
- Módulo 3 de aprendizaje no supervisado en `notebooks/03_modeling.ipynb`: selección de k por método del codo y silhouette, KMeans, AgglomerativeClustering, DBSCAN con búsqueda en grilla, Consensus Clustering (ensamble de 20 KMeans sobre subsample de 5K puntos), análisis de enriquecimiento por cluster, visualización PCA 2D.
- Validación cruzada `StratifiedKFold(5)` aplicada a todos los modelos de clasificación.
- Modelos de ensamble explícitos en clasificación: `AdaBoostClassifier`, `BaggingClassifier`, `ExtraTreesClassifier`.
- `RandomizedSearchCV` en clasificación sobre `RandomForestClassifier` (`n_iter=20`) y `GradientBoostingClassifier` (`n_iter=15`).
- Nuevos directorios de artefactos: `reports/03_modeling/reg_performance/` y `reports/03_modeling/unsup_performance/`.
- Reporte de análisis `reports/03_modeling/ANALYSIS_20260419.md` cubriendo los 3 paradigmas completos (referencia vigente).

### Changed
- `notebooks/03_modeling.ipynb` reestructurado en 3 módulos auto-contenidos (Clasificación, Regresión, No Supervisado), cada uno con comparativa de modelos, resumen ejecutivo y exportación de artefactos.
- Sección de exportación de clasificación actualizada para reflejar resultados post-tuning (`comparison_all_clf` incluye baseline + ensambles + tuned).
- `reports/03_modeling/README.md` actualizado con changelog de ejecuciones v1.0 y v2.0.

### Notes
- Última ejecución documentada de Modeling (v2.0):
  - Reporte: `reports/03_modeling/ANALYSIS_20260419.md`
- Modelo ganador clasificación: `GradientBoosting_Tuned`
  - ROC-AUC: `0.9518`
  - PR-AUC: `0.8999`
  - F1 (clase positiva): `0.8083`
  - Accuracy: `0.8802`
- Modelo ganador regresión: `RandomForestRegressor`
  - CV RMSE: `14.14 ± 0.15`
  - CV R²: `0.66 ± 0.007`
- Modelo ganador no supervisado: `KMeans k=2`
  - Silhouette: `0.2191`
  - Enriquecimiento: Cluster 1 con 45.4% popular vs Cluster 0 con 22.7%

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
