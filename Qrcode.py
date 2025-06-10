import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import qrcode
import io
from PIL import Image
from pyzbar.pyzbar import decode

# === TOKEN DE TON BOT ===
TOKEN = '7698652360:AAGpsp7uhUTUVspqXgJHVTalOtXBM6qurZQ'
bot = telebot.TeleBot(TOKEN)

# === ÉTATS DES UTILISATEURS ===
user_states = {}

# === /START avec boutons contextuels ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_states.pop(user_id, None)  # Réinitialise l’état à chaque /start
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 Générer", callback_data="generate"),
        InlineKeyboardButton("🔍 Décoder", callback_data="decode")
    )
    bot.send_message(message.chat.id, "👋 Que veux-tu faire avec le QR code ?", reply_markup=markup)

# === Gestion des boutons ===
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if call.data == "generate":
        user_states[user_id] = "generate"
        bot.answer_callback_query(call.id, "📤 Mode GÉNÉRATION activé.")
        bot.send_message(call.message.chat.id, "✏️ Envoie-moi un lien ou un texte à convertir en QR code.")
    elif call.data == "decode":
        user_states[user_id] = "decode"
        bot.answer_callback_query(call.id, "🔍 Mode DÉCODAGE activé.")
        bot.send_message(call.message.chat.id, "📷 Envoie une image contenant un QR code à décoder.")

# === Gestion des messages selon l’état ===
@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    # --- Mode Générer ---
    if state == "generate" and message.text:
        qr = qrcode.make(message.text)
        bio = io.BytesIO()
        bio.name = 'qr.png'
        qr.save(bio, 'PNG')
        bio.seek(0)
        bot.send_photo(message.chat.id, bio, caption="✅ Voici ton QR code.")
        return

    # --- Mode Décoder ---
    elif state == "decode" and message.photo:
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            img = Image.open(io.BytesIO(downloaded_file))
            decoded = decode(img)
            if decoded:
                data = decoded[0].data.decode('utf-8')
                bot.send_message(message.chat.id, f"🔓 QR Code décodé :\n{data}")
            else:
                bot.send_message(message.chat.id, "❌ QR code illisible.")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Erreur : {e}")
        return

    # --- Aucun mode sélectionné ---
    else:
        bot.send_message(message.chat.id, "❗ Utilise /start et choisis une action pour commencer.")

# === Lancement du bot ===
print("🤖 Bot QR Code lancé...")
bot.infinity_polling()
