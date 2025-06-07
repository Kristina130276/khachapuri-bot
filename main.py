import telebot
from flask import Flask, request
import os

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Кнопки меню
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.row("📋 Меню")

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.text == "📋 Меню":
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            bot.send_photo(message.chat.id, photo1, caption="🥚 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00")
        with open("images/khachapuri_round.jpg", "rb") as photo2:
            bot.send_photo(message.chat.id, photo2, caption="🍳 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите из меню.")

# Webhook обработка (для Render)
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
    app.run(host="0.0.0.0", port=10000)
