
import logging
import time
import uuid
import os
import re
import hmac

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

from sqlalchemy import func

from app.services.ai_service import get_ai_response

from app.database import (
    SessionLocal,
    Contact,
    serialize_contact,
    count_customers
)


main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


# ==========================================
# ANA SAYFALAR
# ==========================================

@main.route("/")
def home():
    return render_template("index.html")


@main.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ==========================================
# LUMA AI SOHBET
# ==========================================

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
            raise ValueError(
                "AI servisi boş veya geçersiz yanıt döndürdü."
            )

        elapsed = round(
            time.monotonic() - start_time,
            2
        )

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


# ==========================================
# API YETKİ KONTROLÜ
# ==========================================

def api_yetkili_mi():

    beklenen = os.environ.get(
        "ALVERA_API_KEY",
        ""
    )

    gelen = request.headers.get(
        "X-API-Key",
        ""
    )

    return bool(beklenen) and hmac.compare_digest(
        gelen,
        beklenen
    )


# ==========================================
# İLETİŞİM FORMU - KAYIT OLUŞTUR
# ==========================================

@main.route("/api/contacts", methods=["POST"])
def contact_create():

    if not api_yetkili_mi():
        return jsonify({
            "error": "Yetkisiz API isteği."
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Geçerli JSON gönderilmelidir."
        }), 400

    ad = str(
        data.get("adSoyad") or ""
    ).strip()

    telefon = str(
        data.get("telefon") or ""
    ).strip()

    email = str(
        data.get("eMail") or ""
    ).strip().lower()

    mesaj = str(
        data.get("mesaj") or ""
    ).strip()

    # Zorunlu alan kontrolü
    if not ad or not mesaj or not (telefon or email):
        return jsonify({
            "error": "Lütfen zorunlu alanları doldurun."
        }), 400

    # Karakter sınırları
    if (
        len(ad) > 200 or
        len(telefon) > 40 or
        len(email) > 254 or
        len(mesaj) > 5000
    ):
        return jsonify({
            "error": "Alan uzunlukları geçersiz."
        }), 400

    # E-posta doğrulama
    if email and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        return jsonify({
            "error": "Geçersiz e-posta adresi."
        }), 400

    session = SessionLocal()

    try:

        kayit = Contact(
            adSoyad=ad,
            telefon=telefon,
            eMail=email,
            mesaj=mesaj
        )

        session.add(kayit)
        session.commit()

        logger.info(
            "ALVERA iletişim kaydı oluşturuldu | id=%s",
            kayit.id
        )

        return jsonify({
            "success": True,
            "id": kayit.id,
            "message": "Mesajınız başarıyla kaydedildi."
        }), 201

    except Exception:

        session.rollback()

        logger.exception(
            "[ALVERA İLETİŞİM KAYIT HATASI]"
        )

        return jsonify({
            "success": False,
            "error": "İletişim kaydı oluşturulamadı."
        }), 500

    finally:
        session.close()


# ==========================================
# YÖNETİM PANELİ - KAYITLARI GETİR
# ==========================================

@main.route("/api/contacts", methods=["GET"])
def contacts_list():

    if not api_yetkili_mi():
        return jsonify({
            "error": "Yetkisiz API isteği."
        }), 401

    session = SessionLocal()

    try:

        toplam = session.query(
            func.count(Contact.id)
        ).scalar() or 0

        kayitlar = (
            session.query(Contact)
            .order_by(
                Contact.tarih.desc(),
                Contact.id.desc()
            )
            .limit(100)
            .all()
        )

        return jsonify({
            "success": True,
            "totalCount": toplam,
            "items": [
                serialize_contact(k)
                for k in kayitlar
            ]
        }), 200

    except Exception:

        logger.exception(
            "[ALVERA KAYIT LİSTELEME HATASI]"
        )

        return jsonify({
            "success": False,
            "error": "Kayıtlar alınamadı."
        }), 500

    finally:
        session.close()


# ==========================================
# YÖNETİM PANELİ - İSTATİSTİKLER
# ==========================================

@main.route("/api/contacts/stats", methods=["GET"])
def contact_stats():

    if not api_yetkili_mi():
        return jsonify({
            "error": "Yetkisiz API isteği."
        }), 401

    session = SessionLocal()

    try:

        toplam = session.query(
            func.count(Contact.id)
        ).scalar() or 0

        musteri = count_customers(session)

        return jsonify({
            "success": True,
            "totalCount": toplam,
            "uniqueCustomers": musteri
        }), 200

    except Exception:

        logger.exception(
            "[ALVERA İSTATİSTİK HATASI]"
        )

        return jsonify({
            "success": False,
            "error": "İstatistikler alınamadı."
        }), 500

    finally:
        session.close()
