import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Временное хранилище языков по chat_id
user_data = {}

# Команда старт — выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עברית")
    bot.send_message(
        message.chat.id,
        "Пожалуйста, выберите язык / אנא בחר שפה",
        reply_markup=markup
    )

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    lang = message.text
    user_data[message.chat.id] = lang
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if "Русский" in lang:
        markup.add("📋 Меню")
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        markup.add("📋 תפריט")
        bot.send_message(message.chat.id, "בחר פעולה:", reply_markup=markup)

# Обработка нажатия кнопки меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📋 Меню", "📋 תפריט"])
def show_photos(message):
    lang = user_data.get(message.chat.id, "ru Русский")
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = (
                "🔺 חצ׳אפורי סירה\n💰 50 ש״ח\n🕒 15:00–21:00"
                if "Русский" not in lang else
                "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            )
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = (
                "🔍 חצ׳אפורי עגול\n💰 50 ש״ח\n🕒 15:00–21:00"
                if "Русский" not in lang else
                "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            )
            bot.send_photo(message.chat.id, photo2, caption=caption2)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Flask обработка webhook
@app.route('/', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

