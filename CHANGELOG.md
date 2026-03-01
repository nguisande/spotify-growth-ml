# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-01

### Added
- End-to-end Spotify Growth ML pipeline structure with `src/`, `notebooks/`, `data/`, `reports/` and reproducible local setup via `requirements.txt` + `.env.example`.
- OAuth user authentication flow in `src/auth/spotify_oauth.py` with local callback server, CSRF state validation, token persistence, and refresh support.
- Spotify API client in `src/data_ingestion/spotify_client.py` with:
  - user and app token handling,
  - playlist and track search,
  - playlist item pagination,
  - audio-features retrieval in batches,
  - basic retry/rate-limit handling for HTTP 429.
- Raw ingestion scripts for three complementary sources:
  - `build_spotify_raw_dataset.py` (user playlists),
  - `build_spotify_raw_dataset_public_playlists.py` (public playlists discovered by query),
  - `build_spotify_raw_dataset_search_tracks.py` (track search by generic patterns).
- Raw merge script `src/data_ingestion/merge_raw_datasets.py` to concatenate latest raw datasets and deduplicate by `track_id`.
- Reporting utility `src/utils/generate_report.py` to execute notebooks and export timestamped HTML reports.
- Static analysis documentation in `reports/` for EDA, Feature Engineering and Modeling.
- Modeling performance artifacts in `reports/03_modeling/model_performance/`.

### Changed
- Project documentation updated to reflect actual current state of the pipeline and model stage completion.
- Repository retention policy formalized for timestamped artifacts:
  - keep only latest timestamped version per family for `.csv` and `.parquet`,
  - remove duplicate non-timestamp canonical files when equivalent timestamped outputs exist.
- `README.md` aligned with executed outputs and current model results (winner model, metrics, and artifact map).

### Fixed
- Documentation consistency issues where the project was previously described as pre-modeling while modeling outputs already existed.
- Reporting references adjusted to current analysis naming (`ANALYSIS_YYYYMMDD.md`) used in repository artifacts.

### Notes
- EDA/FE/Modeling latest documented run (v1.0 baseline):
  - EDA report: `reports/01_eda/ANALYSIS_20260301.md`
  - Feature engineering report: `reports/02_feature_engineering/ANALYSIS_20260301.md`
  - Modeling report: `reports/03_modeling/ANALYSIS_20260301.md`
- Baseline winner from latest modeling execution:
  - Model: `RandomForest`
  - ROC-AUC: `0.9438`
  - PR-AUC: `0.8818`
  - F1 (positive class): `0.7934`
  - Accuracy: `0.8699`
