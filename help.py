import telebot
from config import bot, ADMIN_IDS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

HELP_MESSAGES = {
    'en': {
        'user': (
            "👋 Welcome to the Bot!\n\n"
            "This bot allows you to communicate with admins. Simply send a message, photo, video, or any content, and it will be forwarded to the admins. They can reply directly to you.\n\n"
            "Available commands:\n"
            "/start - Start the bot and see the welcome message\n"
            "/help - Show this help message\n"
            "/clone - Clone this bot with your own token and admin ID\n"
            "You can also use custom commands set by admins (if any)."
        ),
        'admin': (
            "🔧 Admin Help\n\n"
            "As an admin, you can manage user messages and communicate with users. Here are the available commands:\n\n"
            "/start - Display the current start message\n"
            "/editstart <message> or reply to a message - Update the bot's start message\n"
            "/addcommand <command> <response> - Add a custom command with a response\n"
            "/filter <trigger> <response> - Add a filter to respond to specific words/phrases\n"
            "/stopfilter <trigger> - Remove a filter\n"
            "/filters - List all active filters\n"
            "/help - Show this help message\n"
            "/reply <username or user_id> <message> - Send a message to a specific user\n"
            "/broadcast <message> - Send a message to all users (supports text, photos, videos, etc.)\n"
            "/users - List all registered users\n"
            "/approve_clone <bot_username> - Approve a cloned bot for extended use\n\n"
            "To reply to a specific user, you can also reply directly to their forwarded message, and the response will be sent to them."
        )
    },
    'hi': {
        'user': (
            "👋 बॉट में आपका स्वागत है!\n\n"
            "यह बॉट आपको व्यवस्थापकों (एडमिन) के साथ संवाद करने की अनुमति देता है। बस एक संदेश, फोटो, वीडियो या कोई भी सामग्री भेजें, और यह व्यवस्थापकों को अग्रेषित कर दिया जाएगा। वे आपको सीधे जवाब दे सकते हैं।\n\n"
            "उपलब्ध कमांड:\n"
            "/start - बॉट शुरू करें और स्वागत संदेश देखें\n"
            "/help - यह सहायता संदेश दिखाएँ\n"
            "/clone - अपने टोकन और व्यवस्थापक आईडी के साथ इस बॉट को क्लोन करें\n"
            "आप व्यवस्थापकों द्वारा सेट किए गए कस्टम कमांड भी उपयोग कर सकते हैं (यदि कोई हों)।"
        ),
        'admin': (
            "🔧 व्यवस्थापक सहायता\n\n"
            "एक व्यवस्थापक के रूप में, आप उपयोगकर्ता संदेशों को प्रबंधित कर सकते हैं और उपयोगकर्ताओं के साथ संवाद कर सकते हैं। उपलब्ध कमांड निम्नलिखित हैं:\n\n"
            "/start - वर्तमान शुरूआती संदेश दिखाएँ\n"
            "/editstart <संदेश> या किसी संदेश का जवाब दें - बॉट का शुरूआती संदेश अपडेट करें\n"
            "/addcommand <कमांड> <प्रतिक्रिया> - एक कस्टम कमांड और उसकी प्रतिक्रिया जोड़ें\n"
            "/filter <ट्रिगर> <प्रतिक्रिया> - विशिष्ट शब्दों/वाक्यांशों के लिए फ़िल्टर जोड़ें\n"
            "/stopfilter <ट्रिगर> - फ़िल्टर हटाएँ\n"
            "/filters - सभी सक्रिय फ़िल्टर की सूची देखें\n"
            "/help - यह सहायता संदेश दिखाएँ\n"
            "/reply <उपयोगकर्ता नाम या उपयोगकर्ता आईडी> <संदेश> - किसी विशिष्ट उपयोगकर्ता को संदेश भेजें\n"
            "/broadcast <संदेश> - सभी उपयोगकर्ताओं को संदेश भेजें (टेक्स्ट, फोटो, वीडियो आदि का समर्थन करता है)\n"
            "/users - सभी पंजीकृत उपयोगकर्ताओं की सूची देखें\n"
            "/approve_clone <बॉट_उपयोगकर्ता_नाम> - क्लोन किए गए बॉट को विस्तारित उपयोग के लिए स्वीकृत करें\n\n"
            "किसी विशिष्ट उपयोगकर्ता को जवाब देने के लिए, आप उनके अग्रेषित संदेश का सीधे जवाब दे सकते हैं, और जवाब उन्हें भेज दिया जाएगा।"
        )
    },
    'es': {
        'user': (
            "👋 ¡Bienvenido al Bot!\n\n"
            "Este bot te permite comunicarte con los administradores. Simplemente envía un mensaje, foto, video o cualquier contenido, y será reenviado a los administradores. Ellos pueden responderte directamente.\n\n"
            "Comandos disponibles:\n"
            "/start - Inicia el bot y ve el mensaje de bienvenida\n"
            "/help - Muestra este mensaje de ayuda\n"
            "/clone - Clona este bot con tu propio token e ID de administrador\n"
            "También puedes usar comandos personalizados establecidos por los administradores (si los hay)."
        ),
        'admin': (
            "🔧 Ayuda para Administradores\n\n"
            "Como administrador, puedes gestionar los mensajes de los usuarios y comunicarte con ellos. Estos son los comandos disponibles:\n\n"
            "/start - Muestra el mensaje de inicio actual\n"
            "/editstart <mensaje> o responde a un mensaje - Actualiza el mensaje de inicio del bot\n"
            "/addcommand <comando> <respuesta> - Añade un comando personalizado con una respuesta\n"
            "/filter <disparador> <respuesta> - Añade un filtro para responder a palabras/frases específicas\n"
            "/stopfilter <disparador> - Elimina un filtro\n"
            "/filters - Lista todos los filtros activos\n"
            "/help - Muestra este mensaje de ayuda\n"
            "/reply <nombre de usuario o ID de usuario> <mensaje> - Envía un mensaje a un usuario específico\n"
            "/broadcast <mensaje> - Envía un mensaje a todos los usuarios (soporta texto, fotos, videos, etc.)\n"
            "/users - Lista todos los usuarios registrados\n"
            "/approve_clone <nombre_de_usuario_del_bot> - Aprueba un bot clonado para uso extendido\n\n"
            "Para responder a un usuario específico, también puedes responder directamente a su mensaje reenviado, y la respuesta se le enviará."
        )
    },
    'fr': {
        'user': (
            "👋 Bienvenue dans le Bot !\n\n"
            "Ce bot vous permet de communiquer avec les administrateurs. Envoyez simplement un message, une photo, une vidéo ou tout autre contenu, et il sera transmis aux administrateurs. Ils peuvent vous répondre directement.\n\n"
            "Commandes disponibles :\n"
            "/start - Démarre le bot et affiche le message de bienvenue\n"
            "/help - Affiche ce message d'aide\n"
            "/clone - Clone ce bot avec votre propre token et ID d'administrateur\n"
            "Vous pouvez également utiliser des commandes personnalisées définies par les administrateurs (s'il y en a)."
        ),
        'admin': (
            "🔧 Aide pour les Administrateurs\n\n"
            "En tant qu'administrateur, vous pouvez gérer les messages des utilisateurs et communiquer avec eux. Voici les commandes disponibles :\n\n"
            "/start - Affiche le message de démarrage actuel\n"
            "/editstart <message> ou répondez à un message - Met à jour le message de démarrage du bot\n"
            "/addcommand <commande> <réponse> - Ajoute une commande personnalisée avec une réponse\n"
            "/filter <déclencheur> <réponse> - Ajoute un filtre pour répondre à des mots/phrases spécifiques\n"
            "/stopfilter <déclencheur> - Supprime un filtre\n"
            "/filters - Liste tous les filtres actifs\n"
            "/help - Affiche ce message d'aide\n"
            "/reply <nom d'utilisateur ou ID d'utilisateur> <message> - Envoie un message à un utilisateur spécifique\n"
            "/broadcast <message> - Envoie un message à tous les utilisateurs (supporte texte, photos, vidéos, etc.)\n"
            "/users - Liste tous les utilisateurs enregistrés\n"
            "/approve_clone <nom_d'utilisateur_du_bot> - Approuve un bot cloné pour une utilisation étendue\n\n"
            "Pour répondre à un utilisateur spécifique, vous pouvez également répondre directement à son message transféré, et la réponse lui sera envoyée."
        )
    },
    'ru': {
        'user': (
            "👋 Добро пожаловать в Бот!\n\n"
            "Этот бот позволяет вам общаться с администраторами. Просто отправьте сообщение, фото, видео или любой контент, и он будет переслан администраторам. Они могут ответить вам напрямую.\n\n"
            "Доступные команды:\n"
            "/start - Запустить бот и увидеть приветственное сообщение\n"
            "/help - Показать это сообщение помощи\n"
            "/clone - Клонировать этот бот с вашим собственным токеном и ID администратора\n"
            "Вы также можете использовать пользовательские команды, установленные администраторами (если они есть)."
        ),
        'admin': (
            "🔧 Помощь для Администраторов\n\n"
            "Как администратор, вы можете управлять сообщениями пользователей и общаться с ними. Вот доступные команды:\n\n"
            "/start - Показать текущее приветственное сообщение\n"
            "/editstart <сообщение> или ответьте на сообщение - Обновить приветственное сообщение бота\n"
            "/addcommand <команда> <ответ> - Добавить пользовательскую команду с ответом\n"
            "/filter <триггер> <ответ> - Добавить фильтр для ответа на определенные слова/фразы\n"
            "/stopfilter <триггер> - Удалить фильтр\n"
            "/filters - Список всех активных фильтров\n"
            "/help - Показать это сообщение помощи\n"
            "/reply <имя пользователя или ID пользователя> <сообщение> - Отправить сообщение конкретному пользователю\n"
            "/broadcast <сообщение> - Отправить сообщение всем пользователям (поддерживает текст, фото, видео и т.д.)\n"
            "/users - Список всех зарегистрированных пользователей\n"
            "/approve_clone <имя_пользователя_бота> - Одобрить клонированный бот для расширенного использования\n\n"
            "Чтобы ответить конкретному пользователю, вы также можете ответить непосредственно на его пересланное сообщение, и ответ будет отправлен ему."
        )
    }
}

DEFAULT_LANGUAGE = 'en'
user_languages = {}  # Temporary storage for user language preferences

def create_language_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("English", callback_data="lang_en"),
        InlineKeyboardButton("हिन्दी", callback_data="lang_hi")
    )
    keyboard.row(
        InlineKeyboardButton("Español", callback_data="lang_es"),
        InlineKeyboardButton("Français", callback_data="lang_fr")
    )
    keyboard.row(
        InlineKeyboardButton("Русский", callback_data="lang_ru")
    )
    return keyboard

@bot.message_handler(commands=['help'])
def handle_help_command(message):
    try:
        user_id = message.from_user.id
        is_admin = user_id in ADMIN_IDS
        help_type = 'admin' if is_admin else 'user'
        language = user_languages.get(user_id, DEFAULT_LANGUAGE)
        if language not in HELP_MESSAGES:
            language = DEFAULT_LANGUAGE
        help_text = HELP_MESSAGES[language][help_type]
        bot.reply_to(message, help_text, reply_markup=create_language_keyboard())
    except Exception as e:
        bot.reply_to(message, f"❌ Error showing help: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    try:
        user_id = call.from_user.id
        language = call.data.split('_')[1]
        if language in HELP_MESSAGES:
            user_languages[user_id] = language
            is_admin = user_id in ADMIN_IDS
            help_type = 'admin' if is_admin else 'user'
            help_text = HELP_MESSAGES[language][help_type]
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=help_text,
                reply_markup=create_language_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, "Language not supported.")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}")