from flask import Flask, request
import telebot
import os

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Словарь для хранения выбранного языка пользователем
user_lang = {}

# Стартовая команда — выбор языка
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("ru Русский", "il עברית")
    bot.send_message(message.chat.id, "Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=markup)

# После выбора языка — показать меню
@bot.message_handler(func=lambda message: message.text in ["ru Русский", "il עברית"])
def show_menu(message):
    lang = message.text
    user_lang[message.chat.id] = lang

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if "Русский" in lang:
        markup.add("📁 Меню")
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        markup.add("📁 תפריט")
        bot.send_message(message.chat.id, "בחר פעולה:", reply_markup=markup)

# Показать фото хачапури по кнопке меню
@bot.message_handler(func=lambda message: message.text.strip() in ["📁 Меню", "📁 תפריט"])
def show_photos(message):
    lang = user_lang.get(message.chat.id, "ru Русский")  # если вдруг нет — по умолчанию русский
    try:
        with open("images/khachapuri_boat.jpg", "rb") as photo1:
            caption1 = "🔺 חצ׳אפורי סירה\n💰 50 ש" + "\n🕒 15:00–21:00" if "Русский" not in lang else "🔺 Хачапури-лодочка\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo1, caption=caption1)

        with open("images/khachapuri_round.jpg", "rb") as photo2:
            caption2 = "🔍 חצ׳אפורי עגול\n💰 50 ש" + "\n🕒 15:00–21:00" if "Русский" not in lang else "🔍 Хачапури-круглый\n💰 50 шекелей\n🕒 15:00–21:00"
            bot.send_photo(message.chat.id, photo2, caption=caption2)

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при загрузке изображений.")

# Кнопка для отправки телефона
@bot.message_handler(func=lambda message: message.text in ["📞 Оставить номер", "📞 להשאיר מספר"])
def ask_phone(message):
    lang = user_lang.get(message.chat.id, "ru Русский")
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = telebot.types.KeyboardButton(text="📞 Отправить номер" if "Русский" in lang else "📞 שלח מספר", request_contact=True)
    kb.add(btn)
    bot.send_message(message.chat.id, "Хотите, чтобы мы вам перезвонили?" if "Русский" in lang else "רוצה שנחזור אליך?", reply_markup=kb)

@app.route('/', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok'

if __name__ == '__main__':
    app.run(debug=False)


