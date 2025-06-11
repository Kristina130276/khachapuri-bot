import os
import telebot
from flask import Flask

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
    markup.add("🗂 Меню") if "Русский" in lang else markup.add("🗂 תפריט")
    bot.send_message(
        message.chat.id,
        "Выберите действие:" if "Русский" in lang else "בחר פעולה:",
        reply_markup=markup
    )

# Обработка меню
@bot.message_handler(func=lambda message: message.text.strip() in ["🗂 Меню", "🗂 תפריט", "תפריט", "תַפְרִיט"])
def show_photos(message):
    lang = message.text  # определяем язык по кнопке
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "🔺 חצ'פורי סירה\n💰 50 ש""ח\n🕒 15:00-21:00" if "Русский" not in lang else "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "🔍 חצ'פורי עגול\n💰 50 ש""ח\n🕒 15:00-21:00" if "Русский" not in lang else "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

        with open("images/pizza.jpg", "rb") as photo3:
            caption3 = "🍕 פיצה\n💰 50 ש""ח\n🕒 15:00-21:00" if "Русский" not in lang else "🍕 Пицца\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo3, caption=caption3)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Кнопка для отправки телефона
@bot.message_handler(func=lambda message: message.text in ["📞 Оставить номер", "📞 להשאיר מספר"])
def ask_for_phone(message):
    lang = message.text
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="📞 Отправить номер" if "Русский" in lang else "📞 שלח מספר", request_contact=True)
    kb.add(button)
    bot.send_message(message.chat.id, "Хотите, чтобы мы вам перезвонили?" if "Русский" in lang else "רוצים שנחזור אליכם?", reply_markup=kb)


    




