import os
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.config import RAW_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def latest_file(pattern: str) -> Path | None:
    files = sorted(RAW_DIR.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None


def main():
    candidates = [
        latest_file("spotify_tracks_playlists_raw_*.parquet"), # Playlist de usuario
        latest_file("spotify_tracks_public_playlists_raw_*.parquet"), # Playlist públicas   
        latest_file("spotify_tracks_search_raw_*.parquet"), # Tracks buscados
    ]
    paths = [p for p in candidates if p is not None]

    if not paths:
        raise FileNotFoundError("No encontré datasets raw para merge en data/raw/")

    logger.info("Mergeando estos archivos:")
    for p in paths:
        logger.info("- %s", p)

    dfs = [pd.read_parquet(p) for p in paths]
    df = pd.concat(dfs, ignore_index=True)

    before = len(df)
    df = df.drop_duplicates(subset=["track_id"]).reset_index(drop=True)
    after = len(df)

    logger.info("Merge total: %s filas (antes) -> %s filas (dedupe)", before, after)
    
    # Guardarmos el dataset mergeado y dedupeado en parquet
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RAW_DIR / f"spotify_tracks_merged_raw_{ts}.parquet"
    df.to_parquet(out, index=False)
    logger.info("Guardado final: %s", out)
    
    # Guardar también en csv para facilitar inspección manual
    out_csv = RAW_DIR / f"spotify_tracks_merged_raw_{ts}.csv"
    df.to_csv(out_csv, index=False)
    logger.info("Guardado final también en CSV: %s", out_csv)


if __name__ == "__main__":
    main()

