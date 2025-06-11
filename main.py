# LANGUAGE SELECTION
from telebot.types import ReplyKeyboardMarkup

def start(update, context):
    keyboard = [["🇷🇺 Русский", "🇮🇱 עברית"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Пожалуйста, выберите язык / אנא בחר שפה", reply_markup=reply_markup)

def handle_language(update, context):
    user_language = update.message.text
    context.user_data['lang'] = user_language
    if user_language == "🇷🇺 Русский":
        send_menu_ru(update, context)
    elif user_language == "🇮🇱 עברית":
        send_menu_il(update, context)

def send_menu_ru(update, context):
    photo_file = open("images/khachapuri.jpg", "rb")
    caption = "🥟 Хачапури по-имеретински — 50 шекелей.\nХотите, чтобы мы вам перезвонили?"
    update.message.reply_photo(photo=photo_file, caption=caption)

def send_menu_il(update, context):
    photo_file = open("images/khachapuri.jpg", "rb")
    caption = "🥟 חצ'פורי חם עם גבינה — 50 ש" + "\"ח.\nרוצים שנחזור אליכם?"
    update.message.reply_photo(photo=photo_file, caption=caption)

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_language))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



