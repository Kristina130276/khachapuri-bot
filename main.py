import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(_name_)

# Выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עברית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=markup)

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    lang = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if "Русский" in lang:
        markup.add("📁 Меню")
        text = "Выберите действие:"
    else:
        markup.add("📁 תפריט")
        text = "בחר פעולה:"
    bot.send_message(message.chat.id, text, reply_markup=markup)

# Обработка меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📁 Меню", "📁 תפריט"])
def show_photos(message):
    lang = message.text
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "🔺 חצ'אפורי סירה\n💰 50 ש"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "🔍 חצ'אפורי עגול\n💰 50 ש"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Flask webhook
@app.route('/', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return ''

if _name_ == '_main_':
    app.run(debug=False, port=5000)

