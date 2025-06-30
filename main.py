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
    markup.add("ru Русский", "il עברית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=markup)

# После выбора языка — меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    user_lang[message.chat.id] = message.text
    lang = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 Меню" if "Русский" in lang else "📋 תפריט")
    bot.send_message(message.chat.id, "Выберите действие:" if "Русский" in lang else "בחר פעולה:", reply_markup=markup)

# Отображение меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📋 Меню", "📋 תפריט"])
def show_photos(message):
    lang = user_lang.get(message.chat.id, "")
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "⏰ 15:00–21:00\n\n🍳 חצ'אפורי בצורת סירה\n🟡 50 שקלים" if "Русский" not in lang else "⏰ 15:00–21:00\n\n🛶 Хачапури-лодочка\n🟡 50 шекелей"
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "⏰ 15:00–21:00\n\n⚪ חצ'אפורי עגול\n🟡 50 שקלים" if "Русский" not in lang else "⏰ 15:00–21:00\n\n⚪ Хачапури-круглый\n🟡 50 шекелей"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton("📞 Оставить номер" if "Русский" in lang else "📞 השאר מספר", request_contact=True)
        markup.add(button)
        bot.send_message(message.chat.id, "Нажмите, чтобы оставить номер:" if "Русский" in lang else "לחצו כדי להשאיר מספר:", reply_markup=markup)
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
    ask_order(message)

# Спрашиваем: хотите оформить заказ?
def ask_order(message):
    lang = user_lang.get(message.chat.id, "")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🧾 Оформить заказ" if "Русский" in lang else "🧾 בצע הזמנה")
    bot.send_message(message.chat.id, "Хотите оформить заказ?" if "Русский" in lang else "?האם ברצונך לבצע הזמנה", reply_markup=markup)

# Начинаем заказ
@bot.message_handler(func=lambda message: message.text in ["🧾 Оформить заказ", "🧾 בצע הזמנה"])
def start_order_flow(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "")
    user_order[chat_id] = {}
    msg = "💬 Какой хачапури вы хотите?\n1️⃣ Круглый\n2️⃣ Лодочка" if "Русский" in lang else "💬 איזה חצ'אפורי אתה רוצה?\n1️⃣ עגול\n2️⃣ סירה"
    bot.send_message(chat_id, msg)
    bot.register_next_step_handler(message, ask_quantity)

def ask_quantity(message):
    chat_id = message.chat.id
    user_order[chat_id]["type"] = message.text
    lang = user_lang.get(chat_id, "")
    msg = "Сколько штук вы хотите?" if "Русский" in lang else "?כמה יחידות תרצה"
    bot.send_message(chat_id, msg)
    bot.register_next_step_handler(message, ask_time)

def ask_time(message):
    chat_id = message.chat.id
    user_order[chat_id]["qty"] = message.text
    lang = user_lang.get(chat_id, "")
    msg = "На какое время оформить?" if "Русский" in lang else "?לאיזו שעה להזמין"
    bot.send_message(chat_id, msg)
    bot.register_next_step_handler(message, ask_pickup_or_delivery)

def ask_pickup_or_delivery(message):
    chat_id = message.chat.id
    user_order[chat_id]["time"] = message.text
    lang = user_lang.get(chat_id, "")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🚶 Самовывоз", "🚚 Доставка") if "Русский" in lang else markup.add("🚶 איסוף עצמי", "🚚 משלוח")
    bot.send_message(chat_id, "Самовывоз или доставка?" if "Русский" in lang else "?איסוף עצמי או משלוח", reply_markup=markup)
    bot.register_next_step_handler(message, finish_order)

def finish_order(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "")
    delivery = message.text
    address = "ул. Амаса 12, Офаким"
    price = "50"
    if "🚚" in delivery or "משלוח" in delivery:
        user_order[chat_id]["delivery"] = "Доставка +20₪" if "Русский" in lang else "משלוח +20₪"
        user_order[chat_id]["address"] = ""
        bot.send_message(chat_id, "Напишите адрес доставки:" if "Русский" in lang else ":כתוב כתובת למשלוח")
        bot.register_next_step_handler(message, ask_client_address)
    else:
        send_final_order(chat_id, message, f"{address} (самовывоз)" if "Русский" in lang else f"{address} (איסוף עצמי)")

def ask_client_address(message):
    chat_id = message.chat.id
    user_order[chat_id]["address"] = message.text
    send_final_order(chat_id, message, message.text)

def send_final_order(chat_id, message, final_address):
    lang = user_lang.get(chat_id, "")
    order = user_order.get(chat_id, {})
    admin_id = 1485434212
    msg = f"📦 Новый заказ от клиента:\nЗаказ: {order['type']}, {order['qty']} шт. на {order['time']}\nАдрес: {final_address}\n{order.get('delivery', '')}"
    bot.send_message(admin_id, msg)
    bot.send_message(chat_id, "Спасибо, заказ принят!" if "Русский" in lang else "!תודה, ההזמנה התקבלה")

@app.route("/", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://khachapuri-bot-1.onrender.com/")
    app.run(host="0.0.0.0", port=5000)



