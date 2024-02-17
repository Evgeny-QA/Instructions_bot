import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from Db_functions import DataBase


DB = DataBase()
'''Запуск бота, получение первоначальных данных для работы с ботом'''
bot = telebot.TeleBot(DB.get_start_bot_info_from_json())
dict_users_id_info = DB.get_telegram_id_authorized_users()
print(dict_users_id_info)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text in ('/start', '/menu'):
        if message.from_user.id not in dict_users_id_info:
            bot.send_message(message.chat.id, "Пожалуйста, войдите или зарегистрируйтесь")
