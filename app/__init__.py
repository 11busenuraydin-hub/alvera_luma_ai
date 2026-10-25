
import os
import logging

from flask import Flask
from flask_cors import CORS

from app.database import init_db


def create_app():

    app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)

    # Wix Studio CORS ayarları
    izinli_adresler = [
        adres.strip()
        for adres in os.getenv(
            "ALLOWED_ORIGINS",
            "https://alvera.live"
        ).split(",")
        if adres.strip()
    ]

    CORS(app)

    # SQLite başlat
    with app.app_context():
        init_db()

        app.logger.info(
            "[ALVERA] SQLite veritabanı hazır."
        )

    # Flask rotalarını yükle
    from app.routes import main

    app.register_blueprint(main)

    app.logger.info(
        "[ALVERA] Flask API başlatıldı."
    )

    return app
