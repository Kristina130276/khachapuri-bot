import telebot
import os
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עברית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=markup)

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    lang = message.text
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📁 Меню") if "Русский" in lang else markup.add("📁 תפריט")
    bot.send_message(
        message.chat.id,
        "Выберите действие:" if "Русский" in lang else "בחר פעולה:",
        reply_markup=markup
    )

# Обработка меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📁 Меню", "📁 תפריט"])
def show_photos(message):
    lang = message.text  # определяем язык по кнопке
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "🔺 חצ'אפורי סירה\n💰 50 ש\"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "🔍 חצ'אפורי עגול\n💰 50 ש\"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Кнопка для отправки телефона
@bot.message_handler(func=lambda message: message.text in ["📞 Оставить номер", "📞 להשאיר מספר"])
def request_contact(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = telebot.types.KeyboardButton(text="📞 Отправить номер" if message.text == "📞 Оставить номер" else "📞 שלח מספר", request_contact=True)
    kb.add(button)
    bot.send_message(message.chat.id, "Хотите, чтобы мы вам перезвонили?" if message.text == "📞 Оставить номер" else "רוצה שנחזור אליך?", reply_markup=kb)

# Flask endpoint для webhook (если используется)
@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




