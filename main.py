import telebot
from flask import Flask, request
import os

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
    markup.add("🗂 Меню") if lang == "ru Русский" else markup.add("🗂 תפריט")
    bot.send_message(
        message.chat.id,
        "Выберите действие:" if lang == "ru Русский" else "בחר פעולה:",
        reply_markup=markup
    )

# Обработка меню
@bot.message_handler(func=lambda message: message.text.strip() in ["🗂 Меню", "🗂 תפריט", "תפריט", "תַפְרִיט"])
def show_photos(message):
    lang = message.text
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "⚠️ חצ׳פורי סירה\n💰 50 ש"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "⚠️ Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "🔍 חצ׳פורי עגול\n💰 50 ש"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

        with open("images/pizza.jpg", "rb") as photo3:
            caption3 = "🍕 פיצה\n💰 50 ש"ח\n🕒 15:00–21:00" if lang != "ru Русский" else "🍕 Пицца\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo3, caption=caption3)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# 📞 Кнопка для отправки телефона
@bot.message_handler(func=lambda message: message.text in ["📞 Оставить номер", "📞 השאר מספר"])
def ask_phone(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="📞 Оставить номер", request_contact=True)
    kb.add(button)
    text = "Хотите, чтобы мы вам перезвонили?" if message.text == "📞 Оставить номер" else "רוצים שנחזור אליכם?"
    bot.send_message(message.chat.id, text, reply_markup=kb)

# Получение телефона
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    phone_number = message.contact.phone_number
    bot.send_message(message.chat.id, "Спасибо! Мы скоро с вами свяжемся.")
    bot.send_message(1485434212, f"📞 Новый клиент | Номер: {phone_number}")

# Webhook обработка
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Проверка главной страницы
@app.route("/", methods=["GET"])
def index():
    return "Бот работает!", 200

if __name__ == "__main__":
    app.run(debug=False)

