import telebot
from keep_alive import keep_alive
from telebot import types

API_TOKEN = "BOT_TOKEN"
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📋 Меню")
    markup.add(btn)
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.text == "📋 Меню":
        bot.send_message(message.chat.id, "🧀 Хачапури круглый — 50 шекелей\n🕒 15:00–21:00")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите из меню.")

keep_alive()
bot.polling()
