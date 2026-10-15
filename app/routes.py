from flask import Blueprint, render_template, request, jsonify
from app.services.ai_service import get_ai_response

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@main.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Lütfen bir mesaj yazın."
        }), 400

    try:
        response = get_ai_response(message.strip())

        return jsonify({
            "reply": response
        })

    except Exception:
        return jsonify({
            "error": "Yapay zekâ yanıtı alınamadı."
        }), 502