import telebot
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from config import bot, ADMIN_IDS, USER_DATA_DIR, BACKUP_FILE
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from banned.ban import banned
import help
import clone
import start


user_message_map = {}

def load_backup():
    global user_message_map
    try:
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, 'r') as f:
                user_message_map = json.load(f)
    except Exception as e:
        print(f"Error loading backup: {e}")

def save_backup():
    try:
        with open(BACKUP_FILE, 'w') as f:
            json.dump(user_message_map, f)
    except Exception as e:
        print(f"Error saving backup: {e}")

def save_user_data(user):
    user_data = {
        "user_id": user.id,
        "username": user.username.lower() if user.username else None,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": getattr(user, 'bio', None)
    }
    file_path = os.path.join(USER_DATA_DIR, f"user_{user.id}.json")
    try:
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=2)
    except Exception as e:
        print(f"Error saving user data: {e}")

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

load_backup()

@bot.message_handler(commands=['reply'])
def handle_reply_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Usᴀɢᴇ: /ʀᴇᴘʟʏ <Usᴇʀɴᴀᴍᴇ Oʀ Usᴇʀ_ɪᴅ> <Mᴇssᴀɢᴇ>")
            return

        identifier, reply_text = parts[1], parts[2]
        user_id = get_user_id(identifier)
        if not user_id:
            bot.reply_to(message, f"Usᴇʀ Nᴏᴛ Fᴏᴜɴᴅ : {identifier}")
            return

        sent_message = bot.send_message(user_id, reply_text)
        bot.reply_to(message, f"✅")

    except telebot.apihelper.ApiTelegramException as te:
        if "blocked by user" in str(te).lower():
            bot.reply_to(message, f"Cᴀɴɴᴏᴛ Sᴇɴᴅ Mᴇssᴀɢᴇ Tᴏ {identifier}: Bot is blocked")
        elif "chat not found" in str(te).lower():
            bot.reply_to(message, f"Cᴀɴɴᴏᴛ Sᴇɴᴅ Mᴇssᴀɢᴇ Tᴏ {identifier}: Invalid user")
        else:
            bot.reply_to(message, f"Eʀʀᴏʀ Sᴇɴᴅɪɴɢ Mᴇssᴀɢᴇ: {str(te)}")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(func=lambda m: m.reply_to_message and m.from_user.id in ADMIN_IDS)
def handle_admin_reply(message):
    try:
        replied_msg_id = message.reply_to_message.message_id
        if replied_msg_id in user_message_map:
            user_id = user_message_map[replied_msg_id]
            bot.copy_message(user_id, message.chat.id, message.message_id)
            bot.reply_to(message, "✅")
        else:
            bot.reply_to(message, "Nᴏ Usᴇʀ Fᴏᴜɴᴅ Fᴏʀ Tʜɪs Mᴇssᴀɢᴇ")
    except telebot.apihelper.ApiTelegramException as te:
        bot.reply_to(message, f"Eʀʀᴏʀ sᴇɴᴅɪɴɢ ʀᴇᴘʟʏ : {str(te)}")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'document', 'audio', 'sticker'])
def handle_user_message(message):
    try:
        save_user_data(message.from_user)
        for admin_id in ADMIN_IDS:
            forwarded = bot.forward_message(admin_id, message.chat.id, message.message_id)
            user_message_map[forwarded.message_id] = message.chat.id
        save_backup()
    except telebot.apihelper.ApiTelegramException as te:
        print(f"Error forwarding message: {te}")
    except Exception as e:
        print(f"Error handling message: {e}")

try:
    clone.restart_cloned_bots()
    bot.polling()
except Exception as e:
    print(f"Bot crashed: {e}")
    save_backup()