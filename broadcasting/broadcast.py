import telebot
import os
from config import bot, USER_DATA_DIR, ADMIN_IDS
import json


@bot.message_handler(commands=['broadcast'])
def handle_broadcast_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        if message.content_type == 'text':
            if len(message.text.split(maxsplit=1)) < 2:
                bot.reply_to(message, "Usᴀɢᴇ: /Bʀᴏᴀᴅᴄᴀsᴛ <Mᴇssᴀɢᴇ>")
                return
            content = message.text.split(maxsplit=1)[1]
        else:
            content = message.caption or ""

        user_ids = []
        for filename in os.listdir(USER_DATA_DIR):
            if filename.startswith("user_") and filename.endswith(".json"):
                try:
                    with open(os.path.join(USER_DATA_DIR, filename), 'r') as f:
                        data = json.load(f)
                        user_id = data.get('user_id')
                        if user_id:
                            user_ids.append(user_id)
                except Exception as e:
                    print(f"Error reading user file {filename}: {e}")

        if not user_ids:
            bot.reply_to(message, "Nᴏ ᴜsᴇʀs ғᴏᴜɴᴅ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ")
            return
            
        success_count = 0
        fail_count = 0
        for user_id in user_ids:
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id, content)
                elif message.content_type == 'photo':
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=content)
                elif message.content_type == 'video':
                    bot.send_video(user_id, message.video.file_id, caption=content)
                elif message.content_type == 'document':
                    bot.send_document(user_id, message.document.file_id, caption=content)
                elif message.content_type == 'audio':
                    bot.send_audio(user_id, message.audio.file_id, caption=content)
                elif message.content_type == 'voice':
                    bot.send_voice(user_id, message.voice.file_id, caption=content)
                elif message.content_type == 'sticker':
                    bot.send_sticker(user_id, message.sticker.file_id)
                success_count += 1
            except telebot.apihelper.ApiTelegramException as te:
                if "blocked by user" in str(te).lower() or "chat not found" in str(te).lower():
                    fail_count += 1
                else:
                    print(f"Error broadcasting to {user_id}: {te}")
                    fail_count += 1
            except Exception as e:
                print(f"Error broadcasting to {user_id}: {e}")
                fail_count += 1

        bot.reply_to(
            message,
            f"𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱:\nSᴜᴄᴄᴇssғᴜʟʟʏ Sᴇɴᴛ Tᴏ {success_count} Usᴇʀs\nFᴀɪʟᴇᴅ Fᴏʀ {fail_count} Usᴇʀs"
        )

    except Exception as e:
        bot.reply_to(message, f"Eʀʀᴏʀ Dᴜʀɪɴɢ Bʀᴏᴀᴅᴄᴀsᴛ : {str(e)}")

@bot.message_handler(commands=['users'])
def handle_users_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🙅")
        return

    try:
        users = []
        for filename in os.listdir(USER_DATA_DIR):
            if filename.startswith("user_") and filename.endswith(".json"):
                try:
                    with open(os.path.join(USER_DATA_DIR, filename), 'r') as f:
                        data = json.load(f)
                        user_info = f"ID: {data.get('user_id')}, Username: {data.get('username') or 'None'}, Name: {data.get('first_name') or ''} {data.get('last_name') or ''}"
                        users.append(user_info)
                except Exception as e:
                    print(f"Error reading user file {filename}: {e}")

        if not users:
            bot.reply_to(message, "Nᴏ Usᴇʀs Fᴏᴜɴᴅ")
            return

        user_list = "\n\n".join(users)
        bot.reply_to(message, f"Rᴇɢɪsᴛᴇʀᴇᴅ Usᴇʀs :\n{user_list}")

    except Exception as e:
        bot.reply_to(message, f"Eʀʀᴏʀ Rᴇᴛʀɪᴇᴠɪɴɢ Usᴇʀs : {str(e)}")