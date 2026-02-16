import os
import threading
import logging
import asyncio
from threading import Lock
from flask import Flask, request, jsonify, abort
from bot import application as bot_application
from admin import app as admin_app
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = admin_app

# משתנים גלובליים לאתחול בטוח
_initialized = False
_init_lock = Lock()

def ensure_initialized():
    """מבטיח שה-application מאותחל פעם אחת בלבד."""
    global _initialized
    if not _initialized:
        with _init_lock:
            if not _initialized:
                asyncio.run(bot_application.initialize())
                _initialized = True
                logger.info("Bot application initialized successfully")

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route(f'/webhook/{config.BOT_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    if update:
        threading.Thread(target=process_update, args=(update,)).start()
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "bad request"}), 400

def process_update(update_json):
    """מעבד עדכון מ-webhook – יוצר loop חדש לכל thread."""
    try:
        ensure_initialized()

        from telegram import Update
        update = Update.de_json(update_json, bot_application.bot)

        # יצירת loop חדש והרצת הקורוטינה
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(bot_application.process_update(update))
        new_loop.close()
    except Exception as e:
        logger.error(f"Error processing update: {e}")

def setup_webhook():
    webhook_url = f"{os.getenv('RENDER_EXTERNAL_URL', '')}/webhook/{config.BOT_TOKEN}"
    if webhook_url.startswith('https://'):
        import requests
        response = requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/setWebhook?url={webhook_url}")
        if response.status_code == 200:
            logger.info(f"Webhook set to {webhook_url}")
        else:
            logger.error(f"Failed to set webhook: {response.text}")
    else:
        logger.warning("RENDER_EXTERNAL_URL not set, skipping webhook setup")

if __name__ == "__main__":
    setup_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))