
import os
import logging

from flask import Flask
from flask_cors import CORS

from app.database import init_db


def create_app():

    app = Flask(__name__)

    # Log ayarları
    logging.basicConfig(level=logging.INFO)

    # Wix Studio ve ALVERA API haberleşmesi
    CORS(app)

    # PostgreSQL veritabanını başlat
    with app.app_context():
        init_db()
        app.logger.info(
            "[ALVERA] Veritabanı hazır."
        )

    # API rotalarını yükle
    from app.routes import main
    app.register_blueprint(main)

    app.logger.info(
        "[ALVERA] Flask uygulaması başlatıldı."
    )

    return app
