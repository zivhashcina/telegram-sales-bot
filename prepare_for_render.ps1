<#
.SYNOPSIS
    מכין את פרויקט הבוט להעלאה ל-Render (גיבוי, יצירת קבצים נדרשים, הגדרות Git).
.DESCRIPTION
    סקריפט זה מבצע:
    1. גיבוי מלא של הפרויקט.
    2. יצירת קובץ main.py (נקודת כניסה ל-Webhook).
    3. עדכון bot.py לייצא את אובייקט application.
    4. הכנת קובץ .gitignore.
    5. הוראות לדחיפה ל-GitHub.
.NOTES
    הרץ כמנהל. אין צורך בחיבור לאינטרנט חוץ מפקודות Git.
#>

# ------------------------------ 1. גיבוי ------------------------------
Write-Host "`n=== 1. יצירת גיבוי מלא של הפרויקט ===" -ForegroundColor Cyan
$backupPath = "S:\TelegramBot_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Compress-Archive -Path "$PWD\*" -DestinationPath $backupPath -Force -CompressionLevel Optimal
Write-Host "✅ גיבוי נוצר: $backupPath" -ForegroundColor Green

# ------------------------------ 2. יצירת main.py ------------------------------
Write-Host "`n=== 2. יצירת קובץ main.py (נקודת כניסה ל-Render) ===" -ForegroundColor Cyan
$mainContent = @'
import os
import threading
import logging
from flask import Flask, request, jsonify
from bot import application as bot_application
from admin import app as admin_app
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = admin_app

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
    try:
        from telegram import Update
        update = Update.de_json(update_json, bot_application.bot)
        import asyncio
        asyncio.run(bot_application.process_update(update))
    except Exception as e:
        logger.error(f"Error processing update: {e}")

def setup_webhook():
    webhook_url = f"{os.getenv('RENDER_EXTERNAL_URL', '')}/webhook/{config.BOT_TOKEN}"
    if webhook_url.startswith('https://'):
        import requests
        requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/setWebhook?url={webhook_url}")
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.warning("RENDER_EXTERNAL_URL not set, skipping webhook setup")

if __name__ == "__main__":
    setup_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
'@

if (-not (Test-Path "main.py")) {
    $mainContent | Out-File -FilePath main.py -Encoding utf8
    Write-Host "✅ main.py נוצר בהצלחה." -ForegroundColor Green
} else {
    Write-Host "⚠️ main.py כבר קיים. גבה אותו ידנית אם צריך, ולאחר מכן לחץ Enter להמשך." -ForegroundColor Yellow
    Read-Host
}

# ------------------------------ 3. עדכון bot.py ------------------------------
Write-Host "`n=== 3. עדכון bot.py לייצא את אובייקט application ===" -ForegroundColor Cyan
$botPath = "bot.py"
$botContent = Get-Content $botPath -Raw

# בדיקה אם כבר קיים
if ($botContent -match "(?s)application = Application.builder.*build\(\)") {
    Write-Host "✅ נראה ש-bot.py כבר מכיל את השורה הדרושה." -ForegroundColor Green
} else {
    Write-Host "מוסיף את השורות הנדרשות לתחתית bot.py..." -ForegroundColor Yellow
    # נוסיף לפני הבלוק if __name__
    $insertionPoint = $botContent.LastIndexOf('if __name__ == "__main__":')
    if ($insertionPoint -gt 0) {
        $newContent = $botContent.Substring(0, $insertionPoint) + @"

# יצירת אובייקט application לייצוא
application = Application.builder().token(config.BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(InlineQueryHandler(inline_query))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
# הוספת ConversationHandler (אם קיים)
# application.add_handler(contact_conv)  # יש להעיר אם קיים

"@ + $botContent.Substring($insertionPoint)
        $newContent | Out-File -FilePath $botPath -Encoding utf8
        Write-Host "✅ bot.py עודכן. אנא ודא שה-ConversationHandler נוסף כראוי (יש להעיר שורה 25)." -ForegroundColor Green
    } else {
        Write-Host "⚠️ לא נמצא בלוק if __name__ ב-bot.py. אנא הוסף ידנית את האובייקט application לפני סוף הקובץ." -ForegroundColor Red
    }
}

# ------------------------------ 4. יצירת .gitignore ------------------------------
Write-Host "`n=== 4. יצירת קובץ .gitignore ===" -ForegroundColor Cyan
$gitignoreContent = @'
venv/
__pycache__/
*.pyc
.env
*.log
static/uploads/
'@
if (-not (Test-Path ".gitignore")) {
    $gitignoreContent | Out-File -FilePath .gitignore -Encoding utf8
    Write-Host "✅ .gitignore נוצר." -ForegroundColor Green
} else {
    Write-Host "⚠️ .gitignore כבר קיים. ודא שהוא כולל את venv/, __pycache__/, *.pyc, .env, *.log, static/uploads/." -ForegroundColor Yellow
}

# ------------------------------ 5. בדיקת חבילות ------------------------------
Write-Host "`n=== 5. בדיקת חבילות Python ===" -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ חבילות מעודכנות." -ForegroundColor Green

# ------------------------------ 6. הוראות ל-Git ------------------------------
Write-Host "`n=== 6. הוראות לדחיפה ל-GitHub ===" -ForegroundColor Cyan
Write-Host "כעת עליך:"
Write-Host "1. לוודא שיש לך חשבון GitHub."
Write-Host "2. ליצור מאגר חדש (repository) בשם telegram-sales-bot."
Write-Host "3. להריץ את הפקודות הבאות ב-PowerShell (באותה תיקייה):" -ForegroundColor Yellow
@"
git init
git add .
git commit -m "הגרסה הסופית להעלאה ל-Render"
git branch -M main
git remote add origin https://github.com/YourUserName/telegram-sales-bot.git
git push -u origin main
"@ | Write-Host

Write-Host "`nלאחר הדחיפה, עבור אל https://render.com והמשך לפי המדריך." -ForegroundColor Cyan

Write-Host "`n=== סיום הסקריפט ===" -ForegroundColor Green