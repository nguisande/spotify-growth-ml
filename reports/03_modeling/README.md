# Reporte Modeling - Modelado de datos

**Notebook fuente:** `notebooks/03_modeling.ipynb`

## Changelog de ejecuciones de modeling

### v2.0

#### 📋 Metadatos del Reporte

- **Fecha de generación:** 2026-04-19
- **Versión del dataset procesado:** spotify_model_ready_20260301_005928.parquet
- **Total de registros procesados:** 66,074
- **Paradigmas cubiertos:** Clasificación supervisada, Regresión supervisada, Aprendizaje no supervisado

#### 📊 Archivos del Reporte

- `ANALYSIS_20260419.md` - Documento de análisis completo v2.0 (referencia vigente)
- `model_performance/` - Artefactos de clasificación (`clf_*`)
- `reg_performance/` - Artefactos de regresión (`reg_*`)
- `unsup_performance/` - Artefactos de clustering (`unsup_*`)

#### 🏆 Resultados clave

- Clasificación: **GradientBoosting_Tuned** — ROC-AUC `0.9518`, F1 clase 1 `0.8083`
- Regresión: **RandomForestRegressor** — CV RMSE `14.14`, CV R² `0.66`
- No supervisado: **KMeans k=2** — Silhouette `0.2191`

#### 🔗 Referencias

- Dataset procesado utilizado: `data/processed/spotify_model_ready_20260301_005928.parquet`

---

### v1.0

#### 📋 Metadatos del Reporte

- **Fecha de generación:** 2026-03-01
- **Versión del dataset procesado:** spotify_model_ready_20260301_005928.parquet
- **Total de registros procesados:** 66,074

#### 📊 Archivos del Reporte

- `ANALYSIS_20260301.md` - Documento de análisis con conclusiones detalladas (reemplazado por v2.0)

#### 🏆 Resultados clave

- Clasificación baseline: **RandomForest** — ROC-AUC `0.9438`, F1 clase 1 `0.7934`

#### 🔗 Referencias

- Dataset procesado utilizado: `data/processed/spotify_model_ready_20260301_005928.parquet`

