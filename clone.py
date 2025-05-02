import telebot
import json
import os
import shutil
import subprocess
import re
import time
import uuid
from datetime import datetime, timedelta
from config import bot, ADMIN_IDS, USER_DATA_DIR
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from banned.ban import banned

clone_temp_data = {}

CLONES_FILE = "clones.json"

def load_clones():
    try:
        if os.path.exists(CLONES_FILE):
            with open(CLONES_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading clones: {e}")
        return {}

def save_clones(clones):
    try:
        with open(CLONES_FILE, 'w') as f:
            json.dump(clones, f, indent=2)
    except Exception as e:
        print(f"Error saving clones: {e}")

def validate_bot_token(token):
    try:
        if token == os.getenv("BOT_TOKEN", "YOUR_BIT_TOKEN"):
            raise ValueError("Cannot use the main bot's token")
        temp_bot = telebot.TeleBot(token)
        bot_info = temp_bot.get_me()
        return bot_info.username
    except Exception as e:
        print(f"Invalid bot token: {e}")
        return None

def setup_clone_directory(bot_username, token, admin_id, user):
    clone_dir = os.path.join("clones", bot_username.lstrip('@'))
    os.makedirs(clone_dir, exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "broadcasting"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "banned"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "user_data"), exist_ok=True)

    main_content = """import telebot
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from config import bot, ADMIN_IDS, USER_DATA_DIR, BACKUP_FILE
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import help
from banned.ban import banned

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
            bot.reply_to(message, "Usage: /reply <username or user_id> <message>")
            return

        identifier, reply_text = parts[1], parts[2]
        user_id = get_user_id(identifier)
        if not user_id:
            bot.reply_to(message, f"User Not Found: {identifier}")
            return

        sent -bot.send_message(user_id, reply_text)
        bot.reply_to(message, f"✅")

    except telebot.apihelper.ApiTelegramException as te:
        if "blocked by user" in str(te).lower():
            bot.reply_to(message, f"Cannot send Message To {identifier}: Bot is blocked")
        elif "chat not found" in str(te).lower():
            bot.reply_to(message, f"Cannot Send Message To {identifier}: Invalid user")
        else:
            bot.reply_to(message, f"Error Sending Message: {str(te)}")
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
            bot.reply_to(message, "No User Found for this message")
    except telebot.apihelper.ApiTelegramException as te:
        bot.reply_to(message, f"Error Sending Reply: {str(te)}")
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
    bot.polling()
except Exception as e:
    print(f"Bot crashed: {e}")
    save_backup()
"""
    main_path = os.path.join(clone_dir, "main.py")
    with open(main_path, 'w') as f:
        f.write(main_content)

    with open(main_path, 'r') as f:
        written_content = f.read()
    print(f"Cloned main.py content:\n{written_content}")

    shutil.copy("help.py", clone_dir)
    shutil.copy(os.path.join("broadcasting", "broadcast.py"), os.path.join(clone_dir, "broadcasting"))
    shutil.copy(os.path.join("banned", "ban.py"), os.path.join(clone_dir, "banned"))

    config_content = f"""import telebot
import os

BOT_TOKEN = "{token}"
ADMIN_IDS = {{{admin_id}}}

bot = telebot.TeleBot(BOT_TOKEN)

USER_DATA_DIR = "user_data"
BACKUP_FILE = "message_map_backup.json"

if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)
"""
    config_path = os.path.join(clone_dir, "config.py")
    with open(config_path, 'w') as f:
        f.write(config_content)

    with open(config_path, 'r') as f:
        written_content = f.read()
    print(f"Cloned config.py content:\n{written_content}")

    user_details = f"User ID: {user.id}\nUsername: {user.username or 'None'}\nFirst Name: {user.first_name}\nLast Name: {user.last_name or ''}\nCloned At: {datetime.now()}"
    with open(os.path.join(clone_dir, "user.txt"), 'w') as f:
        f.write(user_details)

    clone_metadata = {
        "bot_username": bot_username,
        "admin_id": admin_id,
        "user_id": user.id,
        "created_at": time.time(),
        "expires_at": (datetime.now() + timedelta(days=3)).timestamp(),
        "approved": False
    }
    with open(os.path.join(clone_dir, "clone_metadata.json"), 'w') as f:
        json.dump(clone_metadata, f, indent=2)

    clones = load_clones()
    clones[bot_username] = {
        "path": clone_dir,
        "user_id": user.id,
        "created_at": time.time()
    }
    save_clones(clones)

    return clone_dir

def run_cloned_bot(clone_dir):
    try:
        bot_username = os.path.basename(clone_dir)
        os.system(f"pkill -f 'python3 {clone_dir}/main.py'")
        process = subprocess.Popen(
            ["python3", os.path.join(clone_dir, "main.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=5)
        if stderr:
            print(f"Cloned bot error: {stderr}")
        return process
    except subprocess.TimeoutExpired:
        return process
    except Exception as e:
        print(f"Error running cloned bot: {e}")
        return None

def restart_cloned_bots():
    clones = load_clones()
    for bot_username, data in clones.items():
        clone_dir = data["path"]
        metadata_path = os.path.join(clone_dir, "clone_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            if metadata["approved"] or datetime.now().timestamp() < metadata["expires_at"]:
                print(f"Restarting cloned bot: {bot_username}")
                run_cloned_bot(clone_dir)
            else:
                print(f"Skipping expired bot: {bot_username}")

@bot.message_handler(commands=['approve_clone'])
def handle_approve_clone_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usᴀɢᴇ: /Aᴘᴘʀᴏᴠᴇ_Cʟᴏɴᴇ <Bᴏᴛ_Usᴇʀɴᴀᴍᴇ>")
            return

        bot_username = parts[1]
        clone_dir = os.path.join("clones", bot_username.lstrip('@'))
        metadata_path = os.path.join(clone_dir, "clone_metadata.json")
        if not os.path.exists(metadata_path):
            bot.reply_to(message, f"Bᴏᴛ Nᴏᴛ Fᴏᴜɴᴅ : {bot_username}")
            return

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        metadata["approved"] = True
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        bot.reply_to(message, f"Bᴏᴛ {bot_username} Aᴘᴘʀᴏᴠᴇᴅ Fᴏʀ Exᴛᴇɴᴅᴇᴅ Usᴇ.")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")
        
        
@bot.message_handler(commands=['clone'])
@banned
def handle_clone_command(message):
    try:
        clones = load_clones()
        user_clones = sum(1 for data in clones.values() if data["user_id"] == message.from_user.id)
        if user_clones >= 1:
            bot.reply_to(message, "Yᴏᴜ Hᴀᴠᴇ Rᴇᴀᴄʜᴇᴅ Tʜᴇ Mᴀxɪᴍᴜᴍ Nᴜᴍʙᴇʀ Oғ Cʟᴏɴᴇs (1).")
            return
        bot.reply_to(message, "Pʟᴇᴀsᴇ Eɴᴛᴇʀ Tʜᴇ Bᴏᴛ Tᴏᴋᴇɴ Oʀ Fᴏʀᴡᴀʀᴅ A Mᴇssᴀɢᴇ Fʀᴏᴍ BᴏᴛFᴀᴛʜᴇʀ.", 
                     reply_markup=InlineKeyboardMarkup().add(
                         InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                     ))
        bot.register_next_step_handler(message, process_clone_token)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

def process_clone_token(message):
    try:
        token = None
        if message.content_type == 'text':
            token = message.text.strip()
        elif message.forward_from and message.forward_from.id == 93372553:
            text = message.text or ""
            token_match = re.search(r"(\d+:[A-Za-z0-9_-]+)", text)
            if token_match:
                token = token_match.group(1)

        if not token:
            bot.reply_to(message, "Iɴᴠᴀʟɪᴅ Tᴏᴋᴇɴ Oʀ BᴏᴛFᴀᴛʜᴇʀ Mᴇssᴀɢᴇ. Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ.",
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton("• Rᴇᴛʀʏ", callback_data="retry_clone"),
                             InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                         ))
            return

        bot_username = validate_bot_token(token)
        if not bot_username:
            bot.reply_to(message, "Iɴᴠᴀʟɪᴅ Bᴏᴛ Tᴏᴋᴇɴ. Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ.",
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton("• Rᴇᴛʀʏ", callback_data="retry_clone"),
                             InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                         ))
            return

        bot.reply_to(message, f"Vᴀʟɪᴅ Bᴏᴛ :  {bot_username}\nPʟᴇᴀsᴇ Eɴᴛᴇʀ Tʜᴇ Aᴅᴍɪɴ ID (ᴇ.ɢ., 1234).",
                     reply_markup=InlineKeyboardMarkup().add(
                         InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                     ))
        bot.register_next_step_handler(message, process_admin_id, token, bot_username)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

def process_admin_id(message, token, bot_username):
    try:
        admin_id = message.text.strip()
        if not admin_id.isdigit():
            bot.reply_to(message, "Iɴᴠᴀʟɪᴅ Aᴅᴍɪɴ ID. Pʟᴇᴀsᴇ Eɴᴛᴇʀ ᴀ Nᴜᴍᴇʀɪᴄ ID.",
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton("• Rᴇᴛʀʏ", callback_data="retry_admin_id"),
                             InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                         ))
            return

        admin_id = int(admin_id)
        clone_id = str(uuid.uuid4())[:8]
        clone_temp_data[clone_id] = {
            "token": token,
            "admin_id": admin_id,
            "bot_username": bot_username,
            "user": message.from_user,
            "created_at": time.time()
        }

        bot.reply_to(message, f"Cʟᴏɴɪɴɢ Bᴏᴛ : {bot_username}\nAᴅᴍɪɴ ID : {admin_id}\n\n» Cᴏɴғɪʀᴍ Tᴏ Pʀᴏᴄᴇᴇᴅ?",
                     reply_markup=InlineKeyboardMarkup().row(
                         InlineKeyboardButton("« Cᴏɴғɪʀᴍ »", callback_data=f"confirm_clone:{clone_id}"),
                         InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                     ))

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        if call.data == "cancel_clone":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Cʟᴏɴɪɴɢ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
        elif call.data == "retry_clone":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Pʟᴇᴀsᴇ Eɴᴛᴇʀ Tʜᴇ Bᴏᴛ Tᴏᴋᴇɴ Oʀ Fᴏʀᴡᴀʀᴅ ᴀ Mᴇssᴀɢᴇ Fʀᴏᴍ BᴏᴛFᴀᴛʜᴇʀ.",
                             reply_markup=InlineKeyboardMarkup().add(
                                 InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                             ))
            bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_clone_token)
        elif call.data == "retry_admin_id":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Pʟᴇᴀsᴇ Eɴᴛᴇʀ Tʜᴇ Aᴅᴍɪɴ ID (ᴇ.ɢ., 1234).",
                             reply_markup=InlineKeyboardMarkup().add(
                                 InlineKeyboardButton("• Cᴀɴᴄᴇʟ", callback_data="cancel_clone")
                             ))
            bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_admin_id, call.message.text, call.message.reply_to_message.text)
        elif call.data.startswith("confirm_clone"):
            _, clone_id = call.data.split(":")
            if clone_id not in clone_temp_data:
                bot.send_message(call.message.chat.id, "Cʟᴏɴɪɴɢ Sᴇssɪᴏɴ Exᴘɪʀᴇᴅ. Pʟᴇᴀsᴇ Sᴛᴀʀᴛ Aɢᴀɪɴ Wɪᴛʜ /clone.")
                return

            clone_data = clone_temp_data.pop(clone_id)
            token = clone_data["token"]
            admin_id = clone_data["admin_id"]
            bot_username = clone_data["bot_username"]
            user = clone_data["user"]

            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f"Cloning {bot_username}...")

            clone_dir = setup_clone_directory(bot_username, token, admin_id, user)
            process = run_cloned_bot(clone_dir)
            if process:
                bot.send_message(call.message.chat.id, f"🎉 Cʟᴏɴɪɴɢ Sᴜᴄᴄᴇssғᴜʟ! Cʜᴇᴄᴋ Yᴏᴜʀ Bᴏᴛ: @{bot_username}\nNᴏᴛᴇ: Tʜɪs Bᴏᴛ Wɪʟʟ Rᴜɴ Fᴏʀ 3 Dᴀʏs. Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ Fᴏʀ Exᴛᴇɴsɪᴏɴ.",
                                 reply_markup=InlineKeyboardMarkup().add(
                                     InlineKeyboardButton("» Cʜᴇᴄᴋ Sᴛᴀᴛᴜs «", callback_data=f"status_clone:{bot_username}")
                                 ))
            else:
                bot.send_message(call.message.chat.id, f"Fᴀɪʟᴇᴅ Tᴏ Sᴛᴀʀᴛ Cʟᴏɴᴇᴅ Bᴏᴛ. Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Lᴏɢs Oʀ Tʀʏ Aɢᴀɪɴ.")

        elif call.data.startswith("status_clone"):
            _, bot_username = call.data.split(":")
            clone_dir = os.path.join("clones", bot_username.lstrip('@'))
            metadata_path = os.path.join(clone_dir, "clone_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                expires_at = datetime.fromtimestamp(metadata["expires_at"])
                status = "Active" if datetime.now().timestamp() < metadata["expires_at"] or metadata["approved"] else "Expired"
                bot.answer_callback_query(call.id, f"Bot: {bot_username}\nStatus: {status}\nExpires: {expires_at}")
            else:
                bot.answer_callback_query(call.id, "Bot Not Found.")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error: {str(e)}")