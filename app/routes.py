
import logging
import time
import uuid

from flask import Blueprint, render_template, request, jsonify
from app.services.ai_service import get_ai_response

main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@main.route("/api/chat", methods=["POST"])
def chat():
    request_id = str(uuid.uuid4())
    start_time = time.monotonic()

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Geçerli bir JSON nesnesi gönderilmelidir.",
                "request_id": request_id
            }), 400

        message = data.get("message", "")

        if not isinstance(message, str) or not message.strip():
            return jsonify({
                "error": "Lütfen bir mesaj yazın.",
                "request_id": request_id
            }), 400

        message = message.strip()

        if len(message) > 2000:
            return jsonify({
                "error": "Mesaj 2000 karakteri aşamaz.",
                "request_id": request_id
            }), 400

        logger.info(
            "Luma isteği başladı | id=%s | karakter=%s",
            request_id,
            len(message)
        )

        response = get_ai_response(message)

        if not isinstance(response, str) or not response.strip():
            raise ValueError("AI servisi boş veya geçersiz yanıt döndürdü.")

        elapsed = round(time.monotonic() - start_time, 2)

        logger.info(
            "Luma isteği başarılı | id=%s | süre=%ss",
            request_id,
            elapsed
        )

        return jsonify({
            "reply": response.strip(),
            "request_id": request_id
        }), 200

    except Exception:
        logger.exception(
            "Luma backend hatası | id=%s",
            request_id
        )

        return jsonify({
            "error": "Yapay zekâ yanıtı alınamadı.",
            "request_id": request_id
        }), 502
