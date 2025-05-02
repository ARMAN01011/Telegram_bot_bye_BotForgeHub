import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from functools import wraps
from config import bot, ADMIN_IDS

DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "start_message": "Hey there! Welcome, just send any message to contact the admin.",
        "commands": {},
        "filters": {},
        "banned_words": []
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

bot_data = load_data()

def admin_only(func):
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        if message.from_user.id in ADMIN_IDS:
            return func(message, *args, **kwargs)
        else:
            bot.reply_to(message, "🙅")
    return wrapped

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, bot_data["start_message"], parse_mode="Markdown")

@bot.message_handler(commands=['editstart'])
@admin_only
def edit_start(message):
    if message.reply_to_message:
        new_message = message.reply_to_message.text or message.reply_to_message.caption
    else:
        new_message = ' '.join(message.text.split()[1:]) if len(message.text.split()) > 1 else None
    
    if new_message:
        bot_data["start_message"] = new_message
        save_data(bot_data)
        bot.reply_to(message, "Start Message Updated Successfully!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Please Provide a New Nessage Or Reply To a Message.", parse_mode="Markdown")

@bot.message_handler(commands=['addcommand'])
@admin_only
def add_command(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /addcommand <Command> <Response>", parse_mode="Markdown")
        return
    
    command, response = args[1].lstrip('/'), args[2]
    bot_data["commands"][command] = response
    save_data(bot_data)
    bot.reply_to(message, f"Command /{command} Added Successfully!", parse_mode="Markdown")

@bot.message_handler(commands=['filter'])
@admin_only
def add_filter(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /filter <Trigger> <Response>", parse_mode="Markdown")
        return
    
    trigger, response = args[1], args[2]
    bot_data["filters"][trigger.lower()] = response
    save_data(bot_data)
    bot.reply_to(message, f"Filter For '{trigger}' Added Successfully!", parse_mode="Markdown")
    
@bot.message_handler(commands=['stopfilter'])
@admin_only
def stop_filter(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /stopfilter <Trigger>", parse_mode="Markdown")
        return
    
    trigger = args[1].lower()
    if trigger in bot_data["filters"]:
        del bot_data["filters"][trigger]
        save_data(bot_data)
        bot.reply_to(message, f"Filter For '{trigger}' Removed Successfully!", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"No Filter Found For '{trigger}'.", parse_mode="Markdown")

@bot.message_handler(commands=['filters'])
@admin_only
def list_filters(message):
    if bot_data["filters"]:
        filters_list = "\n".join([f"Trigger: {trigger} -> Response: {response}" for trigger, response in bot_data["filters"].items()])
        bot.reply_to(message, f"Active Filters:\n{filters_list}", parse_mode="Markdown")
    else:
        bot.reply_to(message, "No Filters Set.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('/') and message.text[1:] in bot_data["commands"])
def handle_custom_command(message):
    command = message.text[1:].split()[0]
    response = bot_data["commands"][command]
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_filters(message):
    for trigger, response in bot_data["filters"].items():
        if trigger.lower() in message.text.lower():
            bot.reply_to(message, response, parse_mode="Markdown")
            break

@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_media(message):
    caption = message.caption or ""
    bot.forward_message(message.chat.id, message.chat.id, message.message_id)
    if caption:
        bot.send_message(message.chat.id, caption, parse_mode="Markdown")
