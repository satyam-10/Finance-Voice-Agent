"""
Token server — mints short-lived LiveKit JWTs for the browser.

The browser calls GET /token, gets back {token, url}, then connects
to LiveKit directly. The API secret never leaves this container.
"""

import os
import uuid
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from livekit.api import AccessToken, VideoGrants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
CORS(app)

LIVEKIT_URL = os.environ["LIVEKIT_URL"]
LIVEKIT_API_KEY = os.environ["LIVEKIT_API_KEY"]
LIVEKIT_API_SECRET = os.environ["LIVEKIT_API_SECRET"]
ROOM_NAME = os.environ.get("LIVEKIT_ROOM", "markets")


@app.route("/token")
def token():
    identity = f"user-{uuid.uuid4().hex[:8]}"
    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name("Web User")
        .with_grants(VideoGrants(room_join=True, room=ROOM_NAME))
        .to_jwt()
    )
    logger.info(f"Issued token for {identity} → room={ROOM_NAME}")
    return jsonify({"token": token, "url": LIVEKIT_URL})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
