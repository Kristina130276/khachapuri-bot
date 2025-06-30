import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

user_lang = {}

# Команда старт — выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עברית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=markup)

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    user_lang[message.chat.id] = message.text
    lang = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📷 Меню") if "Русский" in lang else markup.add("📷 תפריט")
    bot.send_message(
        message.chat.id,
        "Выберите действие:" if "Русский" in lang else "בחר פעולה:",
        reply_markup=markup
    )

# Обработка кнопки меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📷 Меню", "📷 תפריט"])
def show_photos(message):
    lang = user_lang.get(message.chat.id, "")
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = (
                "🔺 חצ’אפורי סירה\n💰 50 ש״ח\n🕒 15:00–21:00"
                if "Русский" not in lang
                else "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            )
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = (
                "🔍 חצ’אפורי עגול\n💰 50 ש״ח\n🕒 15:00–21:00"
                if "Русский" not in lang
                else "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            )
            bot.send_photo(message.chat.id, photo2, caption=caption2)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton(
            "📞 Оставить номер" if "Русский" in lang else "📞 השאר מספר", request_contact=True
        )
        markup.add(button)
        bot.send_message(
            message.chat.id,
            "Нажмите, чтобы оставить номер:" if "Русский" in lang else "לחץ כדי להשאיר מספר:",
            reply_markup=markup
        )

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

# Flask обработка
@app.route('/', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200
# ➕ Кнопка "Оформить заказ" после меню
def show_order_button(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_text = "✅ Оформить заказ" if "Русский" in lang else "✅ להזמין"
    markup.add(button_text)
    bot.send_message(
        chat_id,
        "☎️ Хотите оформить заказ прямо сейчас?" if "Русский" in lang else "?רוצה להזמין עכשיו",
        reply_markup=markup
    )

# ➕ Русский диалог оформления заказа
@bot.message_handler(func=lambda message: message.text.strip() == "✅ Оформить заказ")
def start_order_flow(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🍽 Какой хачапури вы хотите?\n1️⃣ Круглый\n2️⃣ Лодочка")
    bot.register_next_step_handler(message, ask_quantity)

def ask_quantity(message):
    chat_id = message.chat.id
    hachapuri_type = message.text
    bot.send_message(chat_id, "🧮 Сколько штук?")
    bot.register_next_step_handler(message, ask_time, hachapuri_type)

def ask_time(message, hachapuri_type):
    chat_id = message.chat.id
    quantity = message.text
    bot.send_message(chat_id, "⏰ На какое время?")
    bot.register_next_step_handler(message, finish_order, (hachapuri_type, quantity))

def finish_order(message, data):
    chat_id = message.chat.id
    hachapuri_type, quantity = data
    time = message.text
    text = (
        f"📦 Новый заказ:\n"
        f"🍕 Тип: {hachapuri_type}\n"
        f"🔢 Кол-во: {quantity}\n"
        f"🕒 Время: {time}\n\n"
        f"📞 [Связаться по WhatsApp](https://wa.me/972534869901)"
    )
    bot.send_message(chat_id, text, parse_mode='Markdown')
    bot.send_message(chat_id, "Спасибо! Мы скоро свяжемся с вами 🙏")

# ➕ Иврит-версия
@bot.message_handler(func=lambda message: message.text.strip() == "✅ להזמין")
def start_order_flow_he(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🍽 איזה חצ'אפורי את/ה רוצה?\n1️⃣ עגול\n2️⃣ סירה")
    bot.register_next_step_handler(message, ask_quantity_he)

def ask_quantity_he(message):
    chat_id = message.chat.id
    hachapuri_type = message.text
    bot.send_message(chat_id, "🧮 כמה יחידות?")
    bot.register_next_step_handler(message, ask_time_he, hachapuri_type)

def ask_time_he(message, hachapuri_type):
    chat_id = message.chat.id
    quantity = message.text
    bot.send_message(chat_id, "⏰ לאיזו שעה להכין?")
    bot.register_next_step_handler(message, finish_order_he, (hachapuri_type, quantity))

def finish_order_he(message, data):
    chat_id = message.chat.id
    hachapuri_type, quantity = data
    time = message.text
    text = (
        f"📦 הזמנה חדשה:\n"
        f"🍕 סוג: {hachapuri_type}\n"
        f"🔢 כמות: {quantity}\n"
        f"🕒 שעה: {time}\n\n"
        f"📞 [ליצור קשר ב-WhatsApp](https://wa.me/972534869901)"
    )
    bot.send_message(chat_id, text, parse_mode='Markdown')
    bot.send_message(chat_id, "תודה! נחזור אליך בהקדם 🙏")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://khachapuri-bot-1.onrender.com/")  # замени при необходимости
    app.run(host="0.0.0.0", port=5000)
