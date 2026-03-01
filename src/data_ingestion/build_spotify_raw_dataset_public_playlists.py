import logging
from datetime import datetime
from typing import Dict, Any, List

import pandas as pd

from src.config import RAW_DIR
from src.data_ingestion.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


# Keywords para descubrir playlists grandes (NO Spotify)
PLAYLIST_SEARCH_QUERIES = [
    "argentina", "latin", "reggaeton", "trap", "hits", "rock", "pop", "indie",
    "cumbia", "electronica", "party", "gym", "workout", "focus", "chill"
]

MAX_PLAYLISTS_PER_QUERY = 30          # cuántas playlists tomar por keyword
MIN_TRACKS_PER_PLAYLIST = 150         # para garantizar volumen
MAX_TRACKS_PER_PLAYLIST_TO_FETCH = 400  # cap para no explotarte el tiempo


def extract_tracks_from_playlist_items(items: List[Dict[str, Any]], playlist_id: str, playlist_name: str) -> List[Dict[str, Any]]:
    records = []
    for item in items:
        track = item.get("track")
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
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "source": "public_playlists",
        })
    return records


def main():
    client = SpotifyClient()
    all_records: List[Dict[str, Any]] = []
    chosen_playlists = []

    logger.info("Descubriendo playlists públicas (no Spotify) vía search...")

    for q in PLAYLIST_SEARCH_QUERIES:
        found = 0
        offset = 0
        limit = 50  # max 50

        while found < MAX_PLAYLISTS_PER_QUERY:
            data = client.search_playlists(query=q, limit=limit, offset=offset)
            items = data.get("playlists", {}).get("items", [])
            if not items:
                break

            for pl in items:
                if found >= MAX_PLAYLISTS_PER_QUERY:
                    break

                if not pl:
                    continue

                owner_id = pl.get("owner", {}).get("id")
                if owner_id == "spotify":
                    continue

                tracks_total = pl.get("tracks", {}).get("total", 0)
                if tracks_total < MIN_TRACKS_PER_PLAYLIST:
                    continue

                pl_id = pl.get("id")
                pl_name = pl.get("name")
                if not pl_id:
                    continue

                chosen_playlists.append({
                    "id": pl_id,
                    "name": pl_name,
                    "tracks_total": tracks_total,
                    "query": q,
                    "owner": owner_id,
                })
                found += 1

            offset += limit
            if offset > 1000:
                break

        logger.info("Query '%s': playlists elegidas=%s", q, found)

    if not chosen_playlists:
        logger.error("No se eligieron playlists públicas. Bajá MIN_TRACKS_PER_PLAYLIST o agregá queries.")
        return

    logger.info("Total playlists públicas elegidas: %s", len(chosen_playlists))

    # Bajamos tracks de playlists elegidas
    for pl in chosen_playlists:
        pl_id = pl["id"]
        pl_name = pl["name"]
        to_fetch = min(pl["tracks_total"], MAX_TRACKS_PER_PLAYLIST_TO_FETCH)

        try:
            items = client.get_all_playlist_tracks(playlist_id=pl_id, max_items=to_fetch)
        except Exception as e:
            logger.error("Error bajando playlist '%s' (%s): %s", pl_name, pl_id, str(e))
            continue

        records = extract_tracks_from_playlist_items(items, pl_id, pl_name)
        logger.info("Playlist '%s': tracks extraídos=%s", pl_name, len(records))
        all_records.extend(records)

    if not all_records:
        logger.error("No se extrajo ningún track desde playlists públicas.")
        return

    df = pd.DataFrame(all_records).drop_duplicates(subset=["track_id"]).reset_index(drop=True)
    logger.info("Dataset public playlists: %s filas, %s cols", df.shape[0], df.shape[1])

    # Guardamos el dataset crudo en parquet (timestamp para versionar)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RAW_DIR / f"spotify_tracks_public_playlists_raw_{ts}.parquet"
    df.to_parquet(out, index=False)
    logger.info("Guardado: %s", out)


if __name__ == "__main__":
    main()
