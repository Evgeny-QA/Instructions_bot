import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from Db_functions import DataBase


DB = DataBase()
'''Запуск бота, получение первоначальных данных для работы с ботом'''
bot = telebot.TeleBot(DB.get_start_bot_info_from_json())
dict_users_id_info = DB.get_all_telegram_id_authorized_users()  # {user_id: [access, "", ""]
dict_first_reg_or_log_id = dict()  # Информация для регистрации: [шаг регистрации, id пользователя, (1)имя и фамилия,
                                   # (2)номер телефона, (3)пароль, (4)конфигурация пк] / вход [номер (10), пароль (11)]
print(dict_users_id_info)


kw_reg_or_log = InlineKeyboardMarkup()
kw_reg_or_log.add(InlineKeyboardButton("Войти", callback_data="log_in"),
                  InlineKeyboardButton("Зарегистрироваться", callback_data="registration"))
kw_admin = InlineKeyboardMarkup()
kw_admin.add(InlineKeyboardButton("Добавить", callback_data="add_admin"),
             InlineKeyboardButton("Изменить", callback_data="change_admin"),
             InlineKeyboardButton("Удалить", callback_data="delete_admin"))

@bot.message_handler(content_types=['text'])
def start(message):
    print(message.chat.id)
    user_id = message.from_user.id
    if user_id in dict_users_id_info:
        dict_first_reg_or_log_id[user_id] = [""]
    # if user_id not in dict_first_reg_or_log_id:
    #     dict_first_reg_or_log_id[user_id] = [""]
    # 1381570918 мой
    # -1002011264106 группы
    '''Запрос на авторизацию/регистрацию'''
    if message.text == "/start":
        dict_first_reg_or_log_id[user_id] = [""]
        if message.from_user.id not in dict_users_id_info:
            bot.send_message(message.chat.id, "Пожалуйста, войдите или зарегистрируйтесь", reply_markup=kw_reg_or_log)
        else:
            bot.send_message(message.chat.id, "Введите интересующий вас вопрос:")

    # перенести временно проверку and message.text[0] != "/"
    '''Вход'''
    if dict_first_reg_or_log_id[user_id][0] == 10 and message.text[0] != "/":
        for index, phone in enumerate(dict_first_reg_or_log_id[user_id][2]):
            print(index, phone)
            if message.text == phone[0]:
                dict_first_reg_or_log_id[user_id][0] = 11
                print(phone)
                dict_first_reg_or_log_id[user_id][1] = dict_first_reg_or_log_id[user_id][2][index]
                print(111111, dict_first_reg_or_log_id[user_id][1])
                bot.send_message(message.chat.id, "Введите пароль")
                break
        else:
            bot.send_message(message.chat.id, "Пользователя с таким телефоном нет, повторите попытку:")
    elif dict_first_reg_or_log_id[user_id][0] == 11 and message.text[0] != "/":
        print(dict_first_reg_or_log_id[user_id][1][1])
        if message.text == dict_first_reg_or_log_id[user_id][1][1]:
            print(dict_first_reg_or_log_id[user_id][1][0], 654747773)
            DB.authorize_user_telegram(user_id, dict_first_reg_or_log_id[user_id][1][0])
            bot.send_message(message.chat.id, "Вы успешно авторизовались!")
            bot.send_message(message.chat.id, "Введите интересующий вас вопрос:")
            dict_first_reg_or_log_id[user_id][0] = ""
            print(123)
        else:
            bot.send_message(message.chat.id, "Неверный пароль, повторите попытку:")

    '''Регистрация'''
    if dict_first_reg_or_log_id[user_id][0] == 1 and message.text[0] != "/":
        '''Валидация длинны Имени и Фамилии'''
        if len(message.text) <= 40:
            dict_first_reg_or_log_id[user_id][0] = 2
            dict_first_reg_or_log_id[user_id].append(message.text)  # Имя и Фамилия
            bot.send_message(message.chat.id, "Введите номер телефона (с кодом +375 (+11 символов) или 80 (+11 символов)):")
        else:
            bot.send_message(message.chat.id, "Веденные Имя и Фаилия превышают допустимую длину в 40 символов, "
                                              "повторите ввод:")
    elif dict_first_reg_or_log_id[user_id][0] == 2 and message.text[0] != "/":
        tel = message.text.strip()
        scheme = "('{0}'[:4] == '+375' and '{0}'[1:].isdigit() and len('{0}') == 13) or" \
                 "('{0}'[:2] == '80' and '{0}'[1:].isdigit() and len('{0}') == 11)"
        '''Валидация введенного номера телефона'''
        if eval(scheme.format(tel)):
            dict_first_reg_or_log_id[user_id][0] = 3
            dict_first_reg_or_log_id[user_id].append(message.text)  # Телефон
            bot.send_message(message.chat.id, "Введите пароль:")
        else:
            bot.send_message(message.chat.id, "Неверный номера телефона, повторите попытку:")
    elif dict_first_reg_or_log_id[user_id][0] == 3 and message.text[0] != "/":
        dict_first_reg_or_log_id[user_id][0] = 4
        dict_first_reg_or_log_id[user_id].append(message.text)  # Пароль
        bot.send_message(message.chat.id, "Введите вашу конфигурацию компьютера:")
    elif dict_first_reg_or_log_id[user_id][0] == 4 and message.text[0] != "/":
        dict_first_reg_or_log_id[user_id][0] = [""]
        dict_first_reg_or_log_id[user_id].append(message.text)  # Характеристики ПК
        DB.register_new_user(dict_first_reg_or_log_id[user_id][1:])
        dict_users_id_info[dict_first_reg_or_log_id[user_id][1]] = [1, "", ""]
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались!")

    '''Панель администраторов'''
    if message.text == "/admin" and dict_users_id_info[user_id][0] == 3:
        dict_users_id_info[user_id][1] = message.message_id + 1  # сохранение ид сообщения
        bot.send_message(message.chat.id, "Выберите предпочитаемое действие:", reply_markup=kw_admin)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    '''Нажатие на кнопку регистрации'''
    if call.data == "registration":
        dict_first_reg_or_log_id[user_id] = [1, user_id]
        bot.send_message(chat_id, "Введите Имя и Фамилию (не более 40 символов):")

        '''Нажатие на кнопку входа'''
    elif call.data == "log_in":
        dict_first_reg_or_log_id[user_id] = [10, 11, DB.get_all_registered_phones_and_passwords()]
        bot.send_message(chat_id, "Введите номер телефона:")

    '''Добавление администратора'''
    if call.data == "add_admin":
        kw_only_users = InlineKeyboardMarkup()
        for user, phone in DB.get_users_only_for_add_admin():
            kw_only_users.add(InlineKeyboardButton(f"Имя - {user}, телефон - {phone}",
                                                   callback_data=f"add_new_adm{phone}"))
        bot.edit_message_text("Доступные пользователи, для предоставления прав админа:\n"
                              "(Для предоставления доступа Админа, кликните по пользователю)",
                              chat_id=chat_id, message_id=dict_users_id_info[user_id][1], reply_markup=kw_only_users)
    elif call.data[:11] == "add_new_adm":
        DB.change_user_access_to_admin(call.data[11:])
        bot.delete_message(chat_id=chat_id, message_id=dict_users_id_info[user_id][1])
        bot.send_message(chat_id, f"Пользователь c номером '{call.data[11:]}' успешно повышен до Админа!")

    '''Изменение доступа действующих администраторов'''
    if call.data == "change_admin":
        pass

    '''Удаление действующих администраторов'''
    if call.data == "delete_admin":
        pass


print("Ready")
bot.infinity_polling()
