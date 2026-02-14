import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
LEADS_GROUP_ID = int(os.getenv("LEADS_GROUP_ID", 0))
LEADS_GROUP_INVITE_LINK = os.getenv("LEADS_GROUP_INVITE_LINK")
BUSINESS_WALLET = os.getenv("BUSINESS_WALLET")
