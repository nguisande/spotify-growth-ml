import json
import logging
import secrets
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request

from src.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    TOKENS_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Scopes necesarios para leer playlists
SCOPES = "playlist-read-private playlist-read-collaborative user-read-email"

STATE = secrets.token_urlsafe(16)
TOKENS_PATH = TOKENS_DIR / "spotify_tokens.json"

app = Flask(__name__)


def save_token_info(token_info: dict) -> None:
    """
    Guarda el token info (access + refresh + expires_at) en JSON.
    """
    # Calculamos expires_at en epoch seconds
    expires_in = token_info.get("expires_in")
    if expires_in is not None:
        token_info["expires_at"] = int(time.time()) + int(expires_in)

    TOKENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TOKENS_PATH.open("w", encoding="utf-8") as f:
        json.dump(token_info, f, indent=2)
    logger.info("Tokens guardados en %s", TOKENS_PATH)


@app.route("/login")
def login():
    """
    Redirige al usuario a la página de autorización de Spotify.
    """
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPES,
        "state": STATE,
        "show_dialog": "true",
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    logger.info("Redirigiendo a Spotify authorize: %s", url)
    return redirect(url)


@app.route("/callback")
def callback():
    """
    Endpoint al que Spotify redirige con ?code=...&state=...
    Intercambiamos el code por access_token + refresh_token.
    """
    error = request.args.get("error")
    if error:
        logger.error("Error devuelto por Spotify: %s", error)
        return f"Error de Spotify: {error}", 400

    code = request.args.get("code")
    state = request.args.get("state")

    if state != STATE:
        logger.error("Estado inválido. Posible ataque CSRF.")
        return "Estado inválido", 400

    if not code:
        logger.error("No se recibió 'code' en el callback.")
        return "Falta code en callback", 400

    logger.info("Recibido authorization code, solicitando tokens...")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=10)
    if response.status_code != 200:
        logger.error("Error al intercambiar code por token: %s - %s",
                     response.status_code, response.text)
        return "Error al obtener tokens", 500

    token_info = response.json()
    save_token_info(token_info)

    return (
        "<h3>Autenticación exitosa 👌</h3>"
        "<p>Ya podés cerrar esta ventana y volver a la terminal.</p>"
    )


if __name__ == "__main__":
    # Levantamos el servidor local para manejar login + callback
    logger.info("Iniciando servidor OAuth en http://localhost:8888 ...")
    app.run(host="127.0.0.1", port=8888, debug=True)
