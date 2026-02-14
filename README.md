# 🛍️ Telegram Smart Sales Bot – ניהול חנות חכמה בטלגרם

בוט טלגרם מתקדם לניהול חנות, מוצרים, קמפיינים ולידים, הכולל דשבורד אדמין מלא (Flask) ומסד נתונים PostgreSQL.

![Version](https://img.shields.io/badge/version-2.0.0-green.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## ✨ תכונות עיקריות

- **בוט חכם** – תפריטים אינטראקטיביים (חיפוש, קטגוריות, מוצרים חמים, צור קשר).
- **דשבורד ניהול** – הוסף/ערוך/מחק מוצרים, צפה בסטטיסטיקות, ניהול קמפיינים.
- **מערכת לידים** – פרטי משתמשים נשמרים אוטומטית, הודעות "צור קשר" נשלחות לקבוצה ייעודית.
- **עוקב אינטראקציות** – כל קליק, צפייה וחיפוש מתועדים לניתוח שיווקי.
- **תמיכה בתמונות** – שליחת מוצרים עם תמונה או טקסט, טיפול בכתובות לא תקינות.
- **מוכן להרצה 24/7** – ניתן להריץ כשירות Windows, או בענן (Render, TeleBotHost, Railway).

---

## 📁 מבנה הפרויקט
telegram_bot/
├── bot.py # קוד הבוט הראשי (טלגרם)
├── admin.py # דשבורד Flask (ניהול)
├── run_admin.py # הרצת הדשבורד עם Waitress
├── config.py # טעינת משתני סביבה
├── database.py # חיבור למסד נתונים
├── models.py # מודלים של SQLAlchemy
├── init_db.py # סקריפט ליצירת טבלאות
├── requirements.txt # רשימת חבילות Python
├── .env.example # תבנית לקובץ הגדרות
│
├── templates/ # תבניות HTML לדשבורד
│ ├── base.html
│ ├── login.html
│ ├── dashboard.html
│ ├── products.html
│ ├── add_product.html
│ ├── edit_product.html
│ ├── campaigns.html
│ └── add_campaign.html
│
└── static/ # קבצים סטטיים
├── style.css
└── uploads/ # תמונות מוצרים (נוצר אוטומטית)

---

## ⚙️ דרישות מערכת

- **Python 3.10 ומעלה**
- **PostgreSQL 12+** (או מסד נתונים PostgreSQL בענן)
- **Windows / Linux / macOS**

---

## 🚀 התקנה מהירה (ב-5 דקות)

### 1. התקנת Python וחבילות
```bash
python -m venv venv
source venv/bin/activate      # ב-Windows: venv\Scripts\Activate
pip install -r requirements.txt
2. יצירת מסד נתונים
psql -U postgres -c "CREATE DATABASE salesbot_db;"
3. הגדרת קובץ .env
cp .env.example .env
# ערוך את הקובץ עם הפרטים שלך (BOT_TOKEN, ADMIN_PASSWORD, LEADS_GROUP_ID וכו')
4. יצירת טבלאות
python init_db.py
5. הרצה
בוט: python bot.py

דשבורד: python run_admin.py (ואז גש ל-http://localhost:5000)
☁️ הרצה בענן (חינם!)
אפשרות א' – TeleBotHost (הכי פשוט, מומלץ לבוטים)
הירשם ב-console.telebothost.com

צור בוט חדש והעלה את קובץ bot.py

הגדר את משתני הסביבה (BOT_TOKEN, DATABASE_URL)

הבוט ירוץ 24/7 אוטומטית.

אפשרות ב' – Render (לפרויקטים מלאים)
צור חשבון ב-render.com

חבר את ה-Git repository (או העלה ZIP)

בחר "Web Service" והגדר:

Build Command: pip install -r requirements.txt

Start Command: gunicorn admin:app & python bot.py (או השתמש ב-Procfile)

הוסף משתני סביבה (BOT_TOKEN, DATABASE_URL, ADMIN_PASSWORD).

מסד נתונים בחינם
Supabase: supabase.com – 500MB, כולל ממשק ניהול.

Neon.tech: neon.tech – 500MB, 190 שעות חישוב בחודש .

Aiven: aiven.io – 1GB, גיבויים יומיים .

📊 שימוש בדשבורד
כתובת: http://localhost:5000 (או כתובת השרת שלך)

התחברות: סיסמת אדמין שהוגדרה בקובץ .env.

ניהול: הוסף, ערוך ומחק מוצרים, צפה בסטטיסטיקות.

🤝 תמיכה וקהילה
באגים ובקשות: פתח Issue ב-GitHub (אם קיים)

טלגרם: @your_support_bot

📜 רישיון
הפרויקט מופץ תחת רישיון MIT. ניתן להשתמש, לשנות ולהפיץ בחופשיות.
נבנה על ידי [השם שלך] עם ❤️

---

# ☁️ שלב 3: העלאה לשרת ציבורי חינמי

## 3.1 בחירת פלטפורמה מתאימה

| פלטפורמה | סוג | חינם? | מתאים ל | קישור |
|----------|------|-------|---------|--------|
| **TeleBotHost** | ייעודי לבוטים | ✅ (24/7) | בוט טלגרם טהור (ללא Flask) | [telebothost.com](https://telebothost.com) [citation:9] |
| **Render** | PaaS | ✅ (דקות שינה) | פרויקט מלא (בוט+דשבורד) | [render.com](https://render.com) [citation:6] |
| **Railway** | PaaS | ✅ (500 שעות/חודש) | פרויקט מלא | [railway.app](https://railway.app) |
| **Supabase** | מסד נתונים | ✅ (500MB) | PostgreSQL בענן | [supabase.com](https://supabase.com) [citation:8] |

## 3.2 הוראות העלאה מפורטות

### אפשרות A: TeleBotHost (הכי קל לבוט)
1. היכנס ל-[console.telebothost.com](https://console.telebothost.com) והתחבר עם טלגרם.
2. לחץ "Create New Bot".
3. העלה את הקובץ `bot.py` (או הדבק את הקוד).
4. בחלון "Environment Variables", הוסף:
BOT_TOKEN=
DATABASE_URL=
ADMIN_IDS=
LEADS_GROUP_ID=
*הערה: עבור מסד נתונים מרוחק, השתמש ב-Supabase או Neon.tech לקבלת `DATABASE_URL` אמיתית.*
5. לחץ "Deploy". הבוט יעלה תוך שניות.

### אפשרות B: Render (לפרויקט המלא)
1. צור חשבון ב-[render.com](https://render.com) (התחבר עם GitHub).
2. לחץ "New +" → "Web Service".
3. חבר את ה-GitHub repository שלך (או העלה ZIP).
4. הגדר:
- **Name:** `telegram-sales-bot`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:**
  ```bash
  gunicorn admin:app & python bot.py
  ```
5. הוסף משתני סביבה (Environment Variables) בדיוק כמו בקובץ `.env`.
6. לחץ "Create Web Service". לאחר כדקה, תקבל כתובת (לדוגמה `https://telegram-sales-bot.onrender.com`). זה יהיה ה-host לדשבורד.
7. **חשוב:** עדכן את ה-`run_admin.py` כדי להאזין ב-`0.0.0.0` (כבר מוגדר). וודא שה-webhook של הבוט מוגדר נכון.

### אפשרות C: מסד נתונים בענן (Supabase)
1. הירשם ב-[supabase.com](https://supabase.com) עם GitHub.
2. צור פרויקט חדש, בחר שם וסיסמה (שמור אותה).
3. לאחר יצירה, עבור ל-"Project Settings" → "Database" → "Connection string".
4. העתק את ה-URI (מתחיל ב-`postgresql://`). הוסף לו `+pg8000`:
5. השתמש במחרוזת זו בקובץ `.env` או במשתני הסביבה של הפלטפורמה שבה בחרת.

---

# 🔄 שלב 4: שחזור והפעלה ממחשב חדש

### 4.1 פקודות PowerShell מלאות לשחזור מהיר
צור קובץ `restore.ps1` והדבק בו:

```powershell
# restore.ps1 – שחזור מלא של הפרויקט
param(
 [string]$backupPath = "S:\TelegramBot_Backup_20250214_153000.zip",
 [string]$restoreDir = "S:\telegram_bot_restored"
)

Write-Host "🔄 מתחיל שחזור..." -ForegroundColor Cyan

# 1. חילוץ הארכיון
Expand-Archive -Path $backupPath -DestinationPath $restoreDir -Force
Write-Host "✅ קבצים חולצו אל: $restoreDir" -ForegroundColor Green

# 2. יצירת סביבה וירטואלית
Set-Location $restoreDir
python -m venv venv
.\venv\Scripts\Activate
Write-Host "✅ סביבה וירטואלית נוצרה" -ForegroundColor Green

# 3. התקנת חבילות
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ חבילות הותקנו" -ForegroundColor Green

# 4. שחזור מסד נתונים (אם קיים קובץ גיבוי)
$dbBackup = "S:\database_backup.sql"
if (Test-Path $dbBackup) {
 $env:PGPASSWORD = "admin123"
 psql -U postgres -h localhost -d salesbot_db -f $dbBackup
 Write-Host "✅ מסד נתונים שוחזר" -ForegroundColor Green
} else {
 Write-Host "⚠️ לא נמצא גיבוי מסד. צור מסד חדש ידנית." -ForegroundColor Yellow
}

Write-Host "🎉 שחזור הושלם! הפעל את הבוט: python bot.py" -ForegroundColor Green

