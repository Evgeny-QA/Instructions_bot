import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from Db_functions import DataBase


DB = DataBase()
'''Запуск бота, получение первоначальных данных для работы с ботом'''
bot = telebot.TeleBot(DB.get_start_bot_info_from_json())
dict_users_id_info = DB.get_telegram_id_authorized_users()
dict_first_reg_id = dict()  # Информация для регистрации: [шаг регистрации, id пользователя, (1)имя и фамилия,
                            # (2)номер телефона, (3)пароль, (4)конфигурация пк]
print(dict_users_id_info)


kw_reg_or_log = InlineKeyboardMarkup()
kw_reg_or_log.add(InlineKeyboardButton("Войти", callback_data="log_in"),
                  InlineKeyboardButton("Зарегистрироваться", callback_data="registration"))


@bot.message_handler(content_types=['text'])
def start(message):
    user_id = message.from_user.id

    '''Запрос на авторизацию/регистрацию'''
    if message.text == "/start":
        if message.from_user.id not in dict_users_id_info:
            bot.send_message(message.chat.id, "Пожалуйста, войдите или зарегистрируйтесь", reply_markup=kw_reg_or_log)

    '''Регистрация'''
    if dict_first_reg_id[user_id][0] == 1:
        '''Валидация длинны Имени и Фамилии'''
        if len(message.text) <= 40:
            dict_first_reg_id[user_id][0] = 2
            dict_first_reg_id[user_id].append(message.text)  # Имя и Фамилия
            bot.send_message(message.chat.id, "Введите номер телефона (с кодом +375 (+11 символов) или 80 (+11 символов)):")
        else:
            bot.send_message(message.chat.id, "Веденные Имя и Фаилия превышают допустимую длину в 40 символов, "
                                              "повторите ввод:")
    elif dict_first_reg_id[user_id][0] == 2:
        tel = message.text.strip()
        scheme = "('{0}'[:4] == '+375' and '{0}'[1:].isdigit() and len('{0}') == 13) or" \
                 "('{0}'[:2] == '80' and '{0}'[1:].isdigit() and len('{0}') == 11)"
        '''Валидация введенного номера телефона'''
        if eval(scheme.format(tel)):
            dict_first_reg_id[user_id][0] = 3
            dict_first_reg_id[user_id].append(message.text)  # Телефон
            bot.send_message(message.chat.id, "Введите пароль:")
        else:
            bot.send_message(message.chat.id, "Неверный номера телефона, повторите попытку:")
    elif dict_first_reg_id[user_id][0] == 3:
        dict_first_reg_id[user_id][0] = 4
        dict_first_reg_id[user_id].append(message.text)  # Пароль
        bot.send_message(message.chat.id, "Введите вашу конфигурацию компьютера:")
    elif dict_first_reg_id[user_id][0] == 4:
        dict_first_reg_id[user_id][0] = [""]
        dict_first_reg_id[user_id].append(message.text)  # Характеристики ПК
        DB.write_down_actions_to_log_file(f"Пользователь {dict_first_reg_id[user_id][2]} - "
                                          f"({dict_first_reg_id[user_id][3]}) был зарегистрирован")
        dict_users_id_info[dict_first_reg_id[user_id][1]] = ["", "", ""]
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались!")
        print(dict_first_reg_id[user_id])


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    '''Отправка сообщения для регистрации'''
    if call.data == "registration":
        dict_first_reg_id[user_id] = [1, user_id]
        bot.send_message(chat_id, "Введите Имя и Фамилию (не более 40 символов):")
    elif call.data == "log_in":
        bot.send_message(chat_id, "Войти")
