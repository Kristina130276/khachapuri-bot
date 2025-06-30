import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

user_lang = {}
user_order = {}

# Команда старт — выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עִברִית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / בחר שפה בבקשה", reply_markup=markup)

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עִברִית"])
def show_menu(message):
    user_lang[message.chat.id] = message.text
    lang = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📷 Меню" if "Русский" in lang else "📷 תפריט")
    bot.send_message(message.chat.id, "Выберите действие:" if "Русский" in lang else "בחר פעולה:", reply_markup=markup)

# Обработка кнопки меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📷 Меню", "📷 תפריט"])
def show_photos(message):
    lang = user_lang.get(message.chat.id, "")
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "⏰ 15:00–21:00 \n\n🍳 50 шекелей\n🥟 Хачапури-лодочка" if "Русский" in lang else "⏰ 15:00–21:00 \n\n🍳 50 ש\"ח\n🥟 חצ'פורי סירה"
            bot.send_photo(message.chat.id, photo1, caption=caption1)
        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "⏰ 15:00–21:00 \n\n🧀 50 шекелей\n🍕 Хачапури-круглый" if "Русский" in lang else "⏰ 15:00–21:00 \n\n🧀 50 ש\"ח\n🍕 חצ'פורי עגול"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton("📞 Оставить номер" if "Русский" in lang else "📞 השאר מספר", request_contact=True)
        markup.add(button)
        bot.send_message(message.chat.id, "Нажмите, чтобы оставить номер:" if "Русский" in lang else "לחץ כדי לשתף מספר טלפון", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Обработка номера телефона
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    admin_id = 1485434212
    phone = message.contact.phone_number
    name = message.contact.first_name
    bot.send_message(admin_id, f"📞 Новый клиент: {name}, номер: {phone}")
    bot.send_message(message.chat.id, "Спасибо! Мы скоро свяжемся с вами.")

    # Новый шаг — уточнение заказа
    lang = user_lang.get(message.chat.id, "")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("📝 Оформить заказ" if "Русский" in lang else "📝 להזמין עכשיו")
    bot.send_message(message.chat.id,
                     "Хотите оформить заказ?" if "Русский" in lang else "האם ברצונך לבצע הזמנה?",
                     reply_markup=markup)

# Старт оформления заказа
@bot.message_handler(func=lambda message: message.text in ["📝 Оформить заказ", "📝 להזמין עכשיו"])
def ask_type(message):
    lang = user_lang.get(message.chat.id, "")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🚤 Лодочка", "⭕ Круглый") if "Русский" in lang else markup.add("🚤 סירה", "⭕ עגול")
    bot.send_message(message.chat.id,
                     "Выберите тип хачапури:" if "Русский" in lang else "בחר סוג חצ'פורי:",
                     reply_markup=markup)

# Обработка выбора типа
@bot.message_handler(func=lambda message: message.text in ["🚤 Лодочка", "⭕ Круглый", "🚤 סירה", "⭕ עגול"])
def ask_quantity(message):
    user_order[message.chat.id] = {'type': message.text}
    lang = user_lang.get(message.chat.id, "")
    bot.send_message(message.chat.id,
                     "Сколько штук вы хотите?" if "Русский" in lang else "כמה חתיכות תרצה?")

# Обработка количества
@bot.message_handler(func=lambda message: message.text.isdigit())
def ask_time(message):
    user_order[message.chat.id]['quantity'] = message.text
    lang = user_lang.get(message.chat.id, "")
    bot.send_message(message.chat.id,
                     "На какое время оформить?" if "Русский" in lang else "לאיזו שעה להזמין?")

# Обработка времени — завершение
@bot.message_handler(func=lambda message: True)
def finish_order(message):
    lang = user_lang.get(message.chat.id, "")
    user_order[message.chat.id]['time'] = message.text
    order = user_order[message.chat.id]
    msg = (f"🧾 Заказ: {order['type']}, {order['quantity']} шт, на {order['time']}"
           if "Русский" in lang else
           f"🧾 הזמנה: {order['type']}, {order['quantity']} יחידות, לשעה {order['time']}")
    bot.send_message(1485434212, f"📬 Новый заказ от клиента:\n{msg}")
    bot.send_message(message.chat.id, "Спасибо, заказ принят!" if "Русский" in lang else "תודה! ההזמנה התקבלה!")

# Flask обработка
@app.route("/", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url="https://khachapuri-bot-1.onrender.com/")  # замени при необходимости
    app.run(host="0.0.0.0", port=5000)

