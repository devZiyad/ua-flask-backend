import os
import logging
from typing import Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Internal utilities
from validators import validate_email_general, validate_same_script_email
from mailer import send_confirmation_email
from chatbot import ask_ai, get_current_file, init as chatbot_init
from aiquiz import generate_quiz_questions, init as aiquiz_init
from summarize import generate_summary_and_questions

# ================================
# Setup
# ================================

load_dotenv()

# Preprocess and initialize data
generate_summary_and_questions()
aiquiz_init()
chatbot_init()

SUPPORTED_LANG = {"ar", "en"}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)
CORS(app)

SUBSCRIBERS_FILE = "subscribers.txt"
subscribers: set[str] = set()


def load_subscribers() -> None:
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                email = line.strip()
                if email:
                    subscribers.add(email)
        logging.info(f"Loaded {len(subscribers)} subscribers from file.")
    else:
        logging.info("No subscribers file found. Starting fresh.")


def save_subscriber(email: str) -> None:
    with open(SUBSCRIBERS_FILE, "a", encoding="utf-8") as f:
        f.write(email + "\n")
    logging.info(f"Saved new subscriber: {email}")


load_subscribers()

# ================================
# API Endpoints
# ================================


@app.route("/api/subscribe", methods=["POST", "OPTIONS"])
def subscribe():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data: Dict[str, Any] = request.get_json()
    email: str = data.get("email", "").strip()

    logging.info(f"Received subscription request: {email}")

    if not email or not (
        validate_email_general(email) and validate_same_script_email(email)
    ):
        logging.warning("Invalid email format or mixed scripts detected.")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Invalid email address. Must be properly formatted and use one language/script.",
                }
            ),
            400,
        )

    if email in subscribers:
        logging.info(f"Email {email} already subscribed.")
        return jsonify({"success": False, "message": "Email already subscribed."}), 409

    subscribers.add(email)
    save_subscriber(email)

    try:
        send_confirmation_email(email)
        logging.info(f"Confirmation email sent to {email}.")
    except Exception as e:
        logging.error(f"Error sending confirmation email: {e}")
        return (
            jsonify(
                {"success": False, "message": "Failed to send confirmation email."}
            ),
            500,
        )

    return jsonify(
        {
            "success": True,
            "message": "Subscription successful! Confirmation email sent.",
        }
    )


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data: Dict[str, Any] = request.get_json()
    messages = data.get("messages", [])
    language = data.get("language", "en").lower().strip()

    if not isinstance(messages, list) or not all(isinstance(m, dict) for m in messages):
        return jsonify({"success": False, "message": "Messages list is required."}), 400

    if language not in SUPPORTED_LANG:
        return jsonify({"success": False, "message": "Invalid language provided."}), 400

    filtered_messages = [
        msg for msg in messages if msg.get("role") in ("user", "assistant")
    ]

    if not filtered_messages:
        return (
            jsonify(
                {"success": False, "message": "Valid conversation history required."}
            ),
            400,
        )

    try:
        answer = ask_ai(filtered_messages, language)
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        logging.error(f"Error communicating with Claude: {e}")
        return (
            jsonify({"success": False, "message": "Error communicating with AI."}),
            500,
        )


@app.route("/api/quiz", methods=["GET", "OPTIONS"])
def quiz():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    n = request.args.get("n", default=5, type=int)
    language = request.args.get("language", default="en", type=str).lower().strip()

    if language not in SUPPORTED_LANG:
        return jsonify({"success": False, "message": "Invalid language provided."}), 400

    logging.info(f"Received quiz request for {n} questions in '{language}'.")

    try:
        quiz_data = generate_quiz_questions(n, language)
        return jsonify({"success": True, **quiz_data})
    except Exception as e:
        logging.error(f"Error generating quiz: {e}")
        return jsonify({"success": False, "message": "Error generating quiz."}), 500


@app.route("/api/file", methods=["GET", "OPTIONS"])
def file():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    logging.info("Received request for current selected file.")
    try:
        current_file = get_current_file()
        return jsonify({"success": True, "file": current_file})
    except Exception as e:
        logging.error(f"Error returning file: {e}")
        return (
            jsonify({"success": False, "message": "Could not return current file"}),
            500,
        )


# ================================
# Run Server
# ================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
