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
# 🧾 Оформление заказа после того как клиент оставил номер
@bot.message_handler(func=lambda message: message.text.strip() in ["✅ Оформить заказ", "✅ להזמין"])
def start_order_flow(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "")
    if "Русский" in lang:
        bot.send_message(chat_id, "🚚 Самовывоз или доставка?", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton("Самовывоз")], [types.KeyboardButton("Доставка")]],
            resize_keyboard=True, one_time_keyboard=True
        ))
    else:
        bot.send_message(chat_id, "🚚 איסוף עצמי או משלוח?", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton("איסוף עצמי")], [types.KeyboardButton("משלוח")]],
            resize_keyboard=True, one_time_keyboard=True
        ))
    bot.register_next_step_handler(message, ask_pickup_or_delivery)

def ask_pickup_or_delivery(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "")
    choice = message.text.strip()
    if choice in ["Доставка", "משלוח"]:
        if "Русский" in lang:
            bot.send_message(chat_id, "📍 Пожалуйста, напишите адрес доставки:")
        else:
            bot.send_message(chat_id, "📍 אנא כתבו את כתובת המשלוח:")
        bot.register_next_step_handler(message, ask_address)
    else:
        if "Русский" in lang:
            bot.send_message(chat_id, "✅ Самовывоз: עמשא 12, אופקים")
            bot.send_message(chat_id, "Спасибо! Мы скоро с вами свяжемся.")
        else:
            bot.send_message(chat_id, "✅ איסוף עצמי: עמשא 12, אופקים")
            bot.send_message(chat_id, "תודה! ניצור איתך קשר בהקדם.")

def ask_address(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "")
    address = message.text.strip()
    if "Русский" in lang:
        bot.send_message(chat_id, f"🚗 Спасибо! Ваш адрес: {address}\nК заказу добавлено +20 шекелей за доставку.")
        bot.send_message(chat_id, "Мы скоро с вами свяжемся!")
    else:
        bot.send_message(chat_id, f"🚗 תודה! הכתובת שלך: {address}\nנוספו 20 ש״ח למשלוח.")
        bot.send_message(chat_id, "ניצור איתך קשר בהקדם.")


