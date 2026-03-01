import logging
from datetime import datetime
from typing import Dict, Any, List

import pandas as pd

from src.config import RAW_DIR
from src.data_ingestion.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


MARKET = "AR"

# Queries genéricas que traen catálogo masivo
TRACK_SEARCH_QUERIES = [
    "a", "e", "o", "la", "de", "the", "feat", "love", "remix", "mix",
    "live", "radio", "version", "edit", "club"
]

# Spotify limita /search a máximo 1000 resultados por query (offset + limit no puede pasar 1000). Por lo tanto, por query podés sacar como mucho ~1000 tracks.
MAX_TRACKS_PER_QUERY = 1000   # 1000 por query * 15 queries = 15k bruto (antes de dedupe)
MAX_OFFSET = 950             # guardrail


def extract_tracks(items: List[Dict[str, Any]], query: str, market: str) -> List[Dict[str, Any]]:
    records = []
    for track in items:
        if not track:
            continue
        track_id = track.get("id")
        if not track_id:
            continue

        album = track.get("album", {})
        artists = track.get("artists", [])
        primary_artist = artists[0] if artists else {}

        records.append({
            "track_id": track_id,
            "track_name": track.get("name"),
            "track_popularity": track.get("popularity"),
            "duration_ms": track.get("duration_ms"),
            "explicit": track.get("explicit"),
            "album_id": album.get("id"),
            "album_name": album.get("name"),
            "album_release_date": album.get("release_date"),
            "artist_id": primary_artist.get("id"),
            "artist_name": primary_artist.get("name"),
            "search_query": query,
            "search_market": market,
            "source": "search_tracks",
        })
    return records


def main():
    client = SpotifyClient()
    all_records: List[Dict[str, Any]] = []

    logger.info("Ingesta masiva por /search (type=track)...")

    for q in TRACK_SEARCH_QUERIES:
        offset = 0 # offset para paginar resultados
        limit = 50 # limit para paginar resultados
        local_records: List[Dict[str, Any]] = [] # lista para almacenar tracks encontrados

        try:
            while len(local_records) < MAX_TRACKS_PER_QUERY:
                # Spotify: offset + limit no puede superar 1000
                if offset + limit > 1000:
                    break

                data = client.search_tracks(query=q, market=MARKET, limit=limit, offset=offset)
                items = data.get("tracks", {}).get("items", [])
                if not items:
                    break

                local_records.extend(extract_tracks(items, q, MARKET))
                offset += limit

                if offset > MAX_OFFSET:
                    break
        except Exception as e:
            logger.error("Query '%s' falló. La salto. Error: %s", q, str(e))

        logger.info("Query '%s': %s registros (bruto)", q, len(local_records))
        all_records.extend(local_records)

    df = pd.DataFrame(all_records).drop_duplicates(subset=["track_id"]).reset_index(drop=True)
    logger.info("Dataset search tracks: %s filas, %s cols", df.shape[0], df.shape[1])

    # Guardamos el dataset crudo en parquet (timestamp para versionar)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RAW_DIR / f"spotify_tracks_search_raw_{ts}.parquet"
    df.to_parquet(out, index=False)
    logger.info("Guardado: %s", out)


if __name__ == "__main__":
    main()
