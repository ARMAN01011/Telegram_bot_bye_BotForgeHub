import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8196431623:AAEXW57-b39_YOUR_BOT_TOKEN")
ADMIN_IDS = {7930646071_YOUR_ADMIN_ID}

bot = telebot.TeleBot(BOT_TOKEN)

USER_DATA_DIR = "user_data"
BACKUP_FILE = "message_map_backup.json"

if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)