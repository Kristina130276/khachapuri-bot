import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Команда старт — выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עברית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=markup)

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    lang = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 Меню") if "Русский" in lang else markup.add("📋 תפריט")
    bot.send_message(
        message.chat.id,
        "Выберите действие:" if "Русский" in lang else "בחר פעולה:",
        reply_markup=markup
    )

# Обработка меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📋 Меню", "📋 תפריט"])
def show_photos(message):
    lang = message.text
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = (
                "🔺 חצ'פורי סירה\n💰 50 ש\"ח\n🕒 15:00–21:00" if "Русский" not in lang else
                "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            )
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = (
                "🔍 חצ'פורי עגול\n💰 50 ש\"ח\n🕒 15:00–21:00" if "Русский" not in lang else
                "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            )
            bot.send_photo(message.chat.id, photo2, caption=caption2)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Кнопка для отправки телефона
@bot.message_handler(func=lambda message: message.text in ["📞 Оставить номер", "📞 להשאיר מספר"])
def ask_phone(message):
    lang = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📱 Поделиться телефоном" if "Русский" in lang else "📱 שתף מספר טלפון", request_contact=True)
    markup.add(button)
    bot.send_message(message.chat.id, "Нажмите кнопку, чтобы отправить номер:" if "Русский" in lang else "לחץ על הכפתור כדי לשלוח את המספר:", reply_markup=markup)

# Обработка номера телефона
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    bot.send_message(YOUR_TELEGRAM_ID, f"📞 Новый клиент: {phone_number}")
    bot.send_message(message.chat.id, "Спасибо! Мы скоро свяжемся с вами.")

# Flask webhook
@app.route("/", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
