
import os
import re
import hmac
import uuid
import time
import logging

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

from app.services.ai_service import get_ai_response

from app.database import (
    add_contact,
    list_contacts,
    contact_statistics
)


main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


# =====================================
# ANA SAYFALAR
# =====================================

@main.route("/")
def home():
    return render_template("index.html")


@main.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# =====================================
# API ANAHTARI KONTROLÜ
# =====================================

def api_yetkili_mi():
    beklenen = os.getenv("ALVERA_API_KEY", "")
    gelen = request.headers.get("X-API-Key", "")

    return bool(beklenen) and hmac.compare_digest(
        gelen,
        beklenen
    )


# =====================================
# LUMA AI SOHBET
# =====================================

@main.route("/api/chat", methods=["POST"])
def chat():

    request_id = str(uuid.uuid4())
    start_time = time.monotonic()

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Geçerli JSON gönderilmelidir.",
                "request_id": request_id
            }), 400

        message = data.get("message", "")

        if not isinstance(message, str):
            return jsonify({
                "error": "Mesaj metin olmalıdır.",
                "request_id": request_id
            }), 400

        message = message.strip()

        if not message:
            return jsonify({
                "error": "Lütfen bir mesaj yazın.",
                "request_id": request_id
            }), 400

        if len(message) > 2000:
            return jsonify({
                "error": "Mesaj çok uzun.",
                "request_id": request_id
            }), 400

        logger.info(
            "Luma isteği başladı | id=%s",
            request_id
        )

        response = get_ai_response(message)

        if (
            not isinstance(response, str)
            or not response.strip()
        ):
            raise ValueError("AI boş yanıt döndürdü.")

        elapsed = round(
            time.monotonic() - start_time,
            2
        )

        logger.info(
            "Luma yanıtı başarılı | id=%s | süre=%s",
            request_id,
            elapsed
        )

        return jsonify({
            "reply": response.strip(),
            "request_id": request_id
        }), 200

    except Exception:
        logger.exception(
            "Luma AI hatası | id=%s",
            request_id
        )

        return jsonify({
            "error": "Yapay zekâ yanıtı alınamadı.",
            "request_id": request_id
        }), 502


# =====================================
# İLETİŞİM FORMU - KAYIT EKLE
# POST /api/contacts
# =====================================

@main.route("/api/contacts", methods=["POST"])
def create_contact():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Geçerli JSON gönderilmelidir."
        }), 400

    adSoyad = str(
        data.get("adSoyad") or ""
    ).strip()

    telefon = str(
        data.get("telefon") or ""
    ).strip()

    eMail = str(
        data.get("eMail") or ""
    ).strip().lower()

    mesaj = str(
        data.get("mesaj") or ""
    ).strip()

    if not adSoyad or not mesaj or not (telefon or eMail):
        return jsonify({
            "success": False,
            "error": "Zorunlu alanlar eksik."
        }), 400

    if (
        len(adSoyad) > 200 or
        len(telefon) > 40 or
        len(eMail) > 254 or
        len(mesaj) > 5000
    ):
        return jsonify({
            "success": False,
            "error": "Alan uzunlukları geçersiz."
        }), 400

    if eMail and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        eMail
    ):
        return jsonify({
            "success": False,
            "error": "E-posta adresi geçersiz."
        }), 400

    try:
        kayit_id = add_contact(
            adSoyad,
            telefon,
            eMail,
            mesaj
        )

        logger.info(
            "İletişim kaydı oluşturuldu | id=%s",
            kayit_id
        )

        return jsonify({
            "success": True,
            "id": kayit_id,
            "message": "Mesaj başarıyla kaydedildi."
        }), 201

    except Exception:
        logger.exception("SQLite kayıt hatası")

        return jsonify({
            "success": False,
            "error": "Mesaj kaydedilemedi."
        }), 500


# =====================================
# YÖNETİM PANELİ - KAYITLAR
# GET /api/contacts
# =====================================

@main.route("/api/contacts", methods=["GET"])
def get_contacts():

    if not api_yetkili_mi():
        return jsonify({
            "error": "Yetkisiz erişim."
        }), 401

    try:
        items = list_contacts(limit=100)

        return jsonify({
            "success": True,
            "items": items,
            "totalCount": contact_statistics()[
                "totalCount"
            ]
        }), 200

    except Exception:
        logger.exception(
            "SQLite kayıt listeleme hatası"
        )

        return jsonify({
            "success": False,
            "error": "Kayıtlar getirilemedi."
        }), 500


# =====================================
# YÖNETİM PANELİ - İSTATİSTİKLER
# GET /api/contacts/stats
# =====================================

@main.route(
    "/api/contacts/stats",
    methods=["GET"]
)
def get_stats():

    if not api_yetkili_mi():
        return jsonify({
            "error": "Yetkisiz erişim."
        }), 401

    try:
        stats = contact_statistics()

        return jsonify({
            "success": True,
            "totalCount": stats["totalCount"],
            "uniqueCustomers": stats["uniqueCustomers"]
        }), 200

    except Exception:
        logger.exception(
            "SQLite istatistik hatası"
        )

        return jsonify({
            "success": False,
            "error": "İstatistikler alınamadı."
        }), 500
