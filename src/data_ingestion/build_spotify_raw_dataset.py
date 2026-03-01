import logging
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd

from src.config import RAW_DIR
from src.data_ingestion.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def extract_tracks_from_playlist_items(
    items: List[Dict[str, Any]],
    playlist_id: str,
    playlist_name: str,
) -> List[Dict[str, Any]]:
    """
    Convierte la lista cruda de items de playlist en registros tabulares de tracks.
    """
    records: List[Dict[str, Any]] = []

    for item in items:
        track = item.get("track")
        if track is None:
            continue

        track_id = track.get("id")
        if track_id is None:
            continue

        album = track.get("album", {})
        artists = track.get("artists", [])
        primary_artist = artists[0] if artists else {}

        record = {
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
            "added_at": item.get("added_at"),
            "source": "user_playlists",
        }

        records.append(record)

    return records


def get_user_playlists_config(
    client: SpotifyClient,
    limit: int = 50,
    min_tracks: int = 20,
    exclude_spotify_owner: bool = True,
) -> List[Dict[str, Any]]:
    """
    Construye una lista de playlists a usar como fuente,
    basadas en las playlists del usuario actual (/me/playlists).
    """
    data = client.get_current_user_playlists(limit=limit)
    items = data.get("items", [])

    playlists_cfg: List[Dict[str, Any]] = []

    logger.info("Playlists encontradas para el usuario actual: %s", len(items))

    for pl in items:
        owner_id = pl.get("owner", {}).get("id")
        name = pl.get("name")
        pl_id = pl.get("id")
        tracks_total = pl.get("tracks", {}).get("total", 0)

        if exclude_spotify_owner and owner_id == "spotify":
            logger.info(
                "Saltando playlist '%s' (%s) porque owner=spotify",
                name,
                pl_id,
            )
            continue

        if tracks_total < min_tracks:
            logger.info(
                "Saltando playlist '%s' (%s) por tener pocos tracks (%s < %s)",
                name,
                pl_id,
                tracks_total,
                min_tracks,
            )
            continue

        logger.info(
            "Playlist elegida: '%s' (%s) | owner=%s | tracks=%s",
            name,
            pl_id,
            owner_id,
            tracks_total,
        )

        playlists_cfg.append(
            {
                "id": pl_id,
                "name": name,
                "max_items": tracks_total,
            }
        )

    if not playlists_cfg:
        logger.warning(
            "No se encontraron playlists elegibles. "
            "Podés bajar el min_tracks o desactivar exclude_spotify_owner."
        )

    return playlists_cfg


def main() -> None:
    logger.info("Iniciando construcción de dataset crudo de Spotify desde playlists de usuario...")
    client = SpotifyClient()

    # 1) Obtener playlists elegibles del usuario
    playlists_config = get_user_playlists_config(
        client=client,
        limit=50,          # cuántas playlists traer de /me/playlists
        min_tracks=30,     # mínimo de temas para considerar una playlist
        exclude_spotify_owner=True,  # no usar playlists owned by 'spotify'
    )

    all_track_records: List[Dict[str, Any]] = []

    # 2) Traer tracks de cada playlist
    for pl in playlists_config:
        playlist_id = pl["id"]
        playlist_name = pl["name"]
        max_items = pl.get("max_items", 500)

        try:
            items = client.get_all_playlist_tracks(
                playlist_id=playlist_id,
                max_items=max_items,
            )
        except RuntimeError as e:
            logger.error(
                "Error al procesar playlist %s (%s). La salto. Detalle: %s",
                playlist_name,
                playlist_id,
                str(e),
            )
            continue

        records = extract_tracks_from_playlist_items(
            items=items,
            playlist_id=playlist_id,
            playlist_name=playlist_name,
        )
        logger.info(
            "Playlist %s (%s): %s tracks válidos extraídos",
            playlist_name,
            playlist_id,
            len(records),
        )
        all_track_records.extend(records)

    if not all_track_records:
        logger.error("No se extrajo ningún track. Revisar playlists del usuario.")
        return

    # 3) Armar DataFrame de tracks y eliminar duplicados por track_id
    tracks_df = pd.DataFrame(all_track_records)
    logger.info("Total de registros antes de drop_duplicates: %s", len(tracks_df))

    tracks_df = tracks_df.drop_duplicates(subset=["track_id"])
    logger.info("Total de tracks únicos: %s", len(tracks_df))

    # 4) Traer audio features para esos track_ids
    track_ids = tracks_df["track_id"].dropna().unique().tolist()
    logger.info("Trayendo audio features para %s tracks...", len(track_ids))

    from src.data_ingestion.spotify_client import SpotifyClient as _SC
    features_client = _SC()
    
    try:
        features = features_client.get_audio_features_for_tracks(track_ids)
        features_df = pd.DataFrame(features)
    except Exception as e:
        logger.error("Fallo al obtener audio features: %s", str(e))
        features_df = pd.DataFrame()

    if features_df.empty:
        logger.warning("No se obtuvieron audio features. Continuo solo con metadata de tracks.")
        merged_df = tracks_df.copy()
    else:
        features_df = features_df.rename(columns={"id": "track_id"})
        merged_df = tracks_df.merge(features_df, on="track_id", how="left")

    # 5) Guardar dataset crudo en parquet (con timestamp para versionar)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RAW_DIR / f"spotify_tracks_playlists_raw_{ts}.parquet"
    merged_df.to_parquet(out, index=False)
    
    logger.info("Dataset crudo guardado en: %s", out)
    logger.info("Shape final: %s filas, %s columnas", merged_df.shape[0], merged_df.shape[1])
    

if __name__ == "__main__":
    main()
