import telebot
import json
import os
import time
from datetime import datetime
from functools import wraps
from config import bot, ADMIN_IDS, USER_DATA_DIR

BANNED_USERS_FILE = "banned_users.json"


def get_user_id(identifier):
    identifier = identifier.lower()
    if identifier.startswith('@'):
        identifier = identifier[1:]
    
    try:
        return int(identifier)
    except ValueError:
        for filename in os.listdir(USER_DATA_DIR):
            if filename.startswith("user_") and filename.endswith(".json"):
                try:
                    with open(os.path.join(USER_DATA_DIR, filename), 'r') as f:
                        data = json.load(f)
                        if data.get('username') == identifier:
                            return data.get('user_id')
                except:
                    continue
    return None
    
    
def load_banned_users():
    try:
        if os.path.exists(BANNED_USERS_FILE):
            with open(BANNED_USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading banned users: {e}")
        return {}

def save_banned_users(banned_users):
    try:
        with open(BANNED_USERS_FILE, 'w') as f:
            json.dump(banned_users, f, indent=2)
    except Exception as e:
        print(f"Error saving banned users: {e}")

banned_users = load_banned_users()

def check_clone_expiry():
    metadata_path = "clone_metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        if not metadata.get("approved") and datetime.now().timestamp() > metadata.get("expires_at", 0):
            return False
    return True

def banned(func):
    @wraps(func)
    def wrapper(message):
        user_id = str(message.from_user.id)
        if user_id in banned_users:
            bot.reply_to(message, "Yᴏᴜ Aʀᴇ Bᴀɴɴᴇᴅ Fʀᴏᴍ Usɪɴɢ Tʜɪs Bᴏᴛ.")
            return
        if not check_clone_expiry():
            bot.reply_to(message, "Tʜɪs Bᴏᴛ Hᴀs Exᴘɪʀᴇᴅ. Cᴏɴᴛᴀᴄᴛ Tʜᴇ Aᴅᴍɪɴ Fᴏʀ Aɴ Exᴛᴇɴsɪᴏɴ.")
            return
        return func(message)
    return wrapper

@bot.message_handler(commands=['ban'])
def handle_ban_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 2:
            bot.reply_to(message, "Usᴀɢᴇ: /ʙᴀɴ <Usᴇʀɴᴀᴍᴇ Oʀ Usᴇʀ_ɪᴅ> [Rᴇᴀsᴏɴ]")
            return

        identifier = parts[1]
        reason = parts[2] if len(parts) > 2 else None

        user_id = get_user_id(identifier)
        if not user_id:
            bot.reply_to(message, f"Usᴇʀ Nᴏᴛ Fᴏᴜɴᴅ : {identifier}")
            return

        user_id_str = str(user_id)
        if user_id_str in banned_users:
            bot.reply_to(message, f"Usᴇʀ {identifier} Is Aʟʀᴇᴀᴅʏ Bᴀɴɴᴇᴅ")
            return

        username = None
        user_file = os.path.join(USER_DATA_DIR, f"user_{user_id}.json")
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    user_data = json.load(f)
                    username = user_data.get('username')
            except Exception as e:
                print(f"Error reading user data for {user_id}: {e}")

        banned_users[user_id_str] = {
            "username": username,
            "reason": reason
        }
        save_banned_users(banned_users)

        bot.reply_to(message, f"Usᴇʀ {identifier} Hᴀs Bᴇᴇɴ Bᴀɴɴᴇᴅ" + (f" (Reason: {reason})" if reason else ""))

    except Exception as e:
        bot.reply_to(message, f"Eʀʀᴏʀ Bᴀɴɴɪɴɢ Usᴇʀ : {str(e)}")

@bot.message_handler(commands=['unban'])
def handle_unban_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usᴀɢᴇ: /Uɴʙᴀɴ <Usᴇʀɴᴀᴍᴇ Oʀ Usᴇʀ_ɪᴅ>")
            return

        identifier = parts[1]
        user_id = get_user_id(identifier)
        if not user_id:
            bot.reply_to(message, f"Usᴇʀ Nᴏᴛ Fᴏᴜɴᴅ : {identifier}")
            return

        user_id_str = str(user_id)
        if user_id_str not in banned_users:
            bot.reply_to(message, f"Usᴇʀ {identifier} Is Nᴏᴛ Bᴀɴɴᴇᴅ")
            return

        del banned_users[user_id_str]
        save_banned_users(banned_users)
        bot.reply_to(message, f"Usᴇʀ {identifier} Hᴀs Bᴇᴇɴ Uɴʙᴀɴɴᴇᴅ")

    except Exception as e:
        bot.reply_to(message, f"Eʀʀᴏʀ Uɴʙᴀɴɴɪɴɢ Usᴇʀ: {str(e)}")

@bot.message_handler(commands=['banned'])
def handle_banned_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        if not banned_users:
            bot.reply_to(message, "Nᴏ Usᴇʀs Aʀᴇ Cᴜʀʀᴇɴᴛʟʏ Bᴀɴɴᴇᴅ")
            return

        banned_list = []
        for user_id, data in banned_users.items():
            username = data.get('username', 'None')
            reason = data.get('reason', 'No reason provided')
            banned_list.append(f"ID: {user_id}, Username: {username}, Reason: {reason}")

        banned_text = "\n".join(banned_list)
        bot.reply_to(message, f"Bᴀɴɴᴇᴅ Usᴇʀs :\n{banned_text}")

    except Exception as e:
        bot.reply_to(message, f"Eʀʀᴏʀ Rᴇᴛʀɪᴇᴠɪɴɢ Bᴀɴɴᴇᴅ Usᴇʀs: {str(e)}")