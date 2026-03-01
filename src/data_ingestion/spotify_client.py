import base64
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterable

import requests

from src.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, TOKENS_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

TOKENS_PATH = TOKENS_DIR / "spotify_tokens.json"

class SpotifyClient:
    """
    Cliente para la Spotify Web API con autenticación dual:

    - **OAuth de usuario** (token en tokens/spotify_tokens.json): se usa para endpoints
      que requieren contexto de usuario (playlists del usuario, búsquedas, items de
      playlists). Requiere ejecutar previamente: python -m src.auth.spotify_oauth
    - **Client Credentials** (app token): se usa solo para endpoints que no requieren
      usuario, por ejemplo /audio-features.

    Propósito:
    - Obtener access tokens (usuario y/o aplicación)
    - Traer nuevos lanzamientos (new releases)
    - Traer items de playlists y playlists del usuario actual
    - Traer audio features para tracks (Solo si spotify lo permite. Requiere token de aplicación)
    - Buscar playlists y tracks
    """

    AUTH_URL = "https://accounts.spotify.com/api/token"
    BASE_URL = "https://api.spotify.com/v1"
    
    import time
    import random

    def __init__(self) -> None:
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET

        # Token de usuario (OAuth)
        self.access_token: Optional[str] = None

        # Token de aplicación (client credentials)
        self.app_access_token: Optional[str] = None
        self.app_token_expires_at: Optional[int] = None


    def _get_access_token(self) -> str:
        """
        Obtiene un access token usando Client Credentials Flow.
        """
        if self.access_token is not None:
            return self.access_token

        logger.info("Obteniendo access token de Spotify...")

        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {b64_auth_str}",
        }
        data = {
            "grant_type": "client_credentials",
        }

        response = requests.post(self.AUTH_URL, headers=headers, data=data, timeout=10)
        if response.status_code != 200:
            logger.error(
                "Error al obtener el token de Spotify: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError("No se pudo obtener el access token de Spotify")

        token_info = response.json()
        self.access_token = token_info["access_token"]
        logger.info("Access token obtenido correctamente.")
        return self.access_token

    def _load_token_info(self) -> Dict[str, Any]:
        """Carga tokens desde un archivo JSON."""
        if not TOKENS_PATH.exists():
            raise RuntimeError(
                f"No se encontró el archivo de tokens en {TOKENS_PATH}. "
                "Corré primero: python -m src.auth.spotify_oauth y hacé el login."
            )
        with TOKENS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_token_info(self, token_info: Dict[str, Any]) -> None:
        expires_in = token_info.get("expires_in")
        if expires_in is not None:
            token_info["expires_at"] = int(time.time()) + int(expires_in)
        TOKENS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TOKENS_PATH.open("w", encoding="utf-8") as f:
            json.dump(token_info, f, indent=2)
        logging.getLogger(__name__).info("Token refrescado guardado en %s", TOKENS_PATH)

    def _refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        logging.getLogger(__name__).info("Refrescando access token de Spotify...")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(self.AUTH_URL, data=data, headers=headers, timeout=10)
        if response.status_code != 200:
            logging.getLogger(__name__).error(
                "Error al refrescar token: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError("No se pudo refrescar el access token de Spotify")

        token_info = response.json()

        # Si el refresh_token no viene en la respuesta, reutilizamos el anterior
        if "refresh_token" not in token_info:
            token_info["refresh_token"] = refresh_token

        self._save_token_info(token_info)
        return token_info

    def _get_user_access_token(self) -> str:
        """
        Obtiene un access token de usuario, refrescándolo si está vencido.
        """
        token_info = self._load_token_info()
        expires_at = token_info.get("expires_at")

        if expires_at is None or expires_at - 60 <= time.time():
            # Token vencido o sin expires_at -> refrescamos
            refresh_token = token_info.get("refresh_token")
            if not refresh_token:
                raise RuntimeError(
                    "No hay refresh_token disponible. Volvé a correr el login OAuth."
                )
            token_info = self._refresh_access_token(refresh_token)

        access_token = token_info.get("access_token")
        if not access_token:
            raise RuntimeError("No se encontró access_token en token_info.")

        self.access_token = access_token
        return access_token
    
    def _get_app_access_token(self) -> str:
        """
        Obtiene un access token de aplicación usando Client Credentials Flow.
        Lo usamos para endpoints que no requieren contexto de usuario,
        como /audio-features.
        """
        logger = logging.getLogger(__name__)

        # Si ya tenemos uno vigente, lo reutilizamos
        if self.app_access_token is not None and self.app_token_expires_at:
            if self.app_token_expires_at - 60 > time.time():
                return self.app_access_token

        logger.info("Obteniendo app access token de Spotify (client_credentials)...")

        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
        }

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers,
            data=data,
            timeout=10,
        )
        if response.status_code != 200:
            logger.error(
                "Error al obtener app access token: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError("No se pudo obtener el app access token de Spotify")

        token_info = response.json()
        self.app_access_token = token_info["access_token"]
        expires_in = token_info.get("expires_in", 3600)
        self.app_token_expires_at = int(time.time()) + int(expires_in)

        logger.info("App access token obtenido correctamente.")
        return self.app_access_token

    def _get_headers_user(self) -> Dict[str, str]:
        """Obtiene headers con el token de usuario."""
        token = self._get_user_access_token()
        return {"Authorization": f"Bearer {token}"}

    def _get_headers_app(self) -> Dict[str, str]:
        """Obtiene headers con el token de aplicación."""
        token = self._get_app_access_token()
        return {"Authorization": f"Bearer {token}"}

    def _get_headers(self) -> Dict[str, str]:
        # por compatibilidad con código existente
        return self._get_headers_user()

    def get_new_releases(
        self,
        country: str = "AR",
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Trae nuevos lanzamientos (álbumes) desde la API de Spotify.

        Docs: https://developer.spotify.com/documentation/web-api/reference/get-new-releases

        :param country: Código de país (ej: 'US', 'AR')
        :param limit: Máximo 50 por request
        :param offset: Para paginar resultados
        """
        url = f"{self.BASE_URL}/browse/new-releases"
        params = {
            "country": country,
            "limit": limit,
            "offset": offset,
        }

        logger.info(
            "Llamando a Spotify new releases | country=%s, limit=%s, offset=%s",
            country,
            limit,
            offset,
        )

        response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
        if response.status_code != 200:
            logger.error(
                "Error al obtener nuevos lanzamientos: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError("Error al llamar a /browse/new-releases")

        data = response.json()
        return data

    def get_albums_from_new_releases(
        self,
        country: str = "US",
        total_limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Helper para traerte varios álbums paginando sobre new releases.

        :param country: Código de país
        :param total_limit: cantidad total aproximada de álbumes a recuperar
        """
        albums: List[Dict[str, Any]] = []
        limit = 50
        offset = 0

        while len(albums) < total_limit:
            data = self.get_new_releases(country=country, limit=limit, offset=offset)
            page_albums = data.get("albums", {}).get("items", [])
            if not page_albums:
                break

            albums.extend(page_albums)
            offset += limit

        logger.info("Total de álbumes obtenidos: %s", len(albums))
        return albums[:total_limit]

    def get_playlist_items(
        self,
        playlist_id: str,
        limit: int = 100,
        offset: int = 0,
        market: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Trae items (tracks) de una playlist.
        Máx 100 items por request.

        Docs: https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks
        
        :param market: Código de país ISO 3166-1 alpha-2 (ej: 'US', 'AR'). 
                      Opcional pero recomendado para playlists públicas.
        """
        url = f"{self.BASE_URL}/playlists/{playlist_id}/tracks"
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        # Agregar market si se proporciona (ayuda con playlists públicas)
        if market is not None:
            params["market"] = market

        logger.info(
            "Llamando a playlist items | playlist_id=%s, limit=%s, offset=%s, market=%s",
            playlist_id,
            limit,
            offset,
            market,
        )

        response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
        if response.status_code != 200:
            error_detail = response.json() if response.text else {}
            logger.error(
                "Error al obtener items de playlist: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError(
                f"Error al llamar a /playlists/{playlist_id}/tracks: "
                f"{error_detail.get('error', {}).get('message', 'Unknown error')}"
            )

        return response.json()

    def get_all_playlist_tracks(
        self,
        playlist_id: str,
        max_items: int = 1000,
        market: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Trae todos los tracks (hasta max_items) de una playlist, paginando.
        Devuelve una lista de dicts con el objeto 'track' y metadata de la playlist.
        
        :param market: Código de país ISO 3166-1 alpha-2 (ej: 'US', 'AR').
                      Opcional pero recomendado para playlists públicas.
        """
        all_items: List[Dict[str, Any]] = []
        limit = 100
        offset = 0

        while len(all_items) < max_items:
            data = self.get_playlist_items(
                playlist_id=playlist_id, 
                limit=limit, 
                offset=offset,
                market=market,
            )
            items = data.get("items", [])
            if not items:
                break

            all_items.extend(items)
            offset += limit

        logger.info(
            "Total de items obtenidos de la playlist %s: %s",
            playlist_id,
            len(all_items),
        )
        return all_items[:max_items]

    def get_audio_features_for_tracks(
        self,
        track_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Trae audio features para una lista de track_ids.
        La API permite máx 100 IDs por request.
        """
        if not track_ids:
            return []

        url = f"{self.BASE_URL}/audio-features"
        features: List[Dict[str, Any]] = []

        def chunker(iterable: Iterable[str], size: int) -> Iterable[List[str]]:
            chunk: List[str] = []
            for item in iterable:
                chunk.append(item)
                if len(chunk) == size:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk

        for chunk in chunker(track_ids, 100):
            params = {"ids": ",".join(chunk)}
            logger.info("Llamando a audio-features para %s tracks...", len(chunk))
            response = requests.get(url, headers=self._get_headers_app(), params=params, timeout=10)
            if response.status_code != 200:
                logger.error(
                    "Error al obtener audio features: %s - %s",
                    response.status_code,
                    response.text,
                )
                raise RuntimeError("Error al llamar a /audio-features")

            data = response.json()
            feats = data.get("audio_features", [])
            # Puede haber None si algún track no tiene features
            feats_clean = [f for f in feats if f is not None]
            features.extend(feats_clean)

        logger.info("Total de audio features obtenidos: %s", len(features))
        return features
    
    def get_current_user_playlists(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Trae playlists del usuario actual (/me/playlists).
        Requiere OAuth de usuario.
        """
        url = f"{self.BASE_URL}/me/playlists"
        params = {
            "limit": limit,
            "offset": offset,
        }

        logger.info("Llamando a /me/playlists | limit=%s, offset=%s", limit, offset)

        response = requests.get(
            url,
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        if response.status_code != 200:
            logger.error(
                "Error al obtener playlists de usuario: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError("Error al llamar a /me/playlists")

        return response.json()
    
    def _request(self, method: str, url: str, headers: dict, params: dict | None = None, data: dict | None = None, timeout: int = 20):
        """
        Request wrapper con manejo básico de rate limit (429) y reintentos.
        """
        max_retries = 6
        for attempt in range(max_retries):
            resp = requests.request(method, url, headers=headers, params=params, data=data, timeout=timeout)

            # Rate limit
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                sleep_s = int(retry_after) if retry_after else (2 ** attempt)
                sleep_s = min(sleep_s, 60) + random.random()
                logger.warning("Rate limited (429). Sleep %.2fs y reintento (%s/%s)...", sleep_s, attempt + 1, max_retries)
                time.sleep(sleep_s)
                continue

            return resp

        return resp
    
    def search_playlists(self, query: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Busca playlists públicas por texto.
        """
        url = f"{self.BASE_URL}/search"
        params = {"q": query, "type": "playlist", "limit": limit, "offset": offset}

        resp = self._request("GET", url, headers=self._get_headers_user(), params=params)
        if resp.status_code != 200:
            logger.error("Error en search playlists: %s - %s", resp.status_code, resp.text)
            raise RuntimeError("Error al llamar a /search (type=playlist)")

        return resp.json()

    def search_tracks(self, query: str, market: str = "AR", limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Busca tracks por texto.
        """
        url = f"{self.BASE_URL}/search"
        params = {"q": query, "type": "track", "market": market, "limit": limit, "offset": offset}

        resp = self._request("GET", url, headers=self._get_headers_user(), params=params)
        if resp.status_code != 200:
            logger.error("Error en search tracks: %s - %s", resp.status_code, resp.text)
            raise RuntimeError("Error al llamar a /search (type=track)")

        return resp.json()

