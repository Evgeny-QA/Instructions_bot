import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from Db_functions import DataBase, write_down_actions_to_log_file
from fuzzywuzzy import process
from time import sleep


DB = DataBase()
'''Запуск бота, получение первоначальных данных для работы с ботом'''
TOKEN, GROUP_ID = DB.get_start_bot_info_from_json()
bot = telebot.TeleBot(TOKEN)

dict_users_id_info = DB.get_all_telegram_id_authorized_users()  # {user_id: [access, [10], ["", ""]]
                                                                # второй элемент списка для чата с пользователем
dict_first_reg_or_log_id = dict()  # Информация для регистрации: [шаг регистрации, id пользователя, (1)имя и фамилия,
                                   # (2)номер телефона, (3)пароль, (4)конфигурация пк] / вход [номер (10), пароль (11)]

kw_reg_or_log = InlineKeyboardMarkup()
kw_reg_or_log.add(InlineKeyboardButton("Войти", callback_data="log_in"),
                  InlineKeyboardButton("Зарегистрироваться", callback_data="registration"))
kw_admin = InlineKeyboardMarkup()
kw_admin.add(InlineKeyboardButton("Добавить", callback_data="add_admin"),
             InlineKeyboardButton("Удалить", callback_data="delete_admin"))


@bot.message_handler(commands=['help'])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    system_admin_info = '''Список всех доступных команд:
        /help - список доступных команд
        /start - прохождение регистрации или авторизация, запрос инструкции
        /call_help - инициализация чата с админом
        /chat_done - завершение чата с админом
        /admin - добавление и удаление админов
        /add_new_instruction - написание новой инструкции
        /instruction_done - завершение и добавление в базу данных
        '''
    admin_info = '''Список всех доступных команд:
        /help - список доступных команд
        /start - прохождение регистрации или авторизация, запрос инструкции
        /call_help - инициализация чата с админом
        /chat_done - завершение чата с админом
        /add_new_instruction - написание новой инструкции
        /instruction_done - завершение и добавление в базу данных
        '''
    user_info = '''Список всех доступных команд:
        /help - список доступных команд
        /start - прохождение регистрации или авторизация, запрос инструкции
        /call_help - инициализация чата с админом
        /chat_done - завершение чата с админом
        '''
    if dict_users_id_info[user_id][0] == 3:
        bot.send_message(chat_id, system_admin_info)
    elif dict_users_id_info[user_id][0] == 2:
        bot.send_message(chat_id, admin_info)
    elif dict_users_id_info[user_id][0] == 1:
        bot.send_message(chat_id, user_info)


@bot.message_handler(commands=['call_help'])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    '''Отправка сообщения о помощи и начале общения с админом'''
    if message.chat.id != GROUP_ID:
        dict_users_id_info[user_id][2][0] = "Chat_activated"
        dict_users_id_info[user_id][1] = ""

        kw_chat = InlineKeyboardMarkup()
        kw_chat.add(InlineKeyboardButton("Начать чат", callback_data=f"start_chat!{chat_id}!{user_id}"))
        chat_member = bot.get_chat_member(chat_id, user_id)
        user_name = chat_member.user.first_name

        bot.send_message(GROUP_ID, f"Пользователю {user_name} срочно нужна помощь!", reply_markup=kw_chat)


@bot.message_handler(commands=['chat_done'])
def start(message):
    user_id = message.from_user.id
    '''Остановка чата для двоих пользователей'''
    for id_ in [user_id, int(dict_users_id_info[user_id][2][1])]:
        dict_users_id_info[id_][2] = ["", ""]
        dict_users_id_info[id_][1] = [10]
        bot.send_message(id_, "Чат завершен!")


@bot.message_handler(content_types=["text", "photo", "video", "document"])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    '''Остановка отлавливания сообщений из чата(группы) админов'''
    if message.chat.id == GROUP_ID:
        return

    '''Отмена действий при отсутствии соединения, в противном случае чат между пользователями'''
    if user_id in dict_users_id_info and dict_users_id_info[user_id][2][0] == "Chat_activated":
        if dict_users_id_info[user_id][2][1] == "":
            return
        else:
            bot.send_message(dict_users_id_info[user_id][2][1], message.text)

    '''Вывод статей'''
    if user_id in dict_users_id_info and dict_users_id_info[user_id][1] == [10]:
        program_instruction = DB.get_all_instruction_and_program_names()
        percent = process.extract(message.text, [instruction_name[1] for instruction_name in program_instruction])
        kw_probably_instructions = InlineKeyboardMarkup()
        for name, perc in percent:
            if perc >= 60:
                for program, instruction in program_instruction:
                    if instruction == name:
                        kw_probably_instructions.add(InlineKeyboardButton(f"Программа: {program} --- "
                                                                          f"Инструкция: {instruction}",
                                                                          callback_data=f"get_instruction{DB.get_instruction_id(instruction)}"))
                        break
        if percent[0][1] < 60:
            bot.send_message(message.chat.id, "Возможных статей не найдено.")
        else:
            bot.send_message(message.chat.id, f"Возможные варианты:", reply_markup=kw_probably_instructions)

    '''Запрос на авторизацию/регистрацию'''
    if message.text == "/start":
        dict_first_reg_or_log_id[user_id] = [""]
        if user_id not in dict_users_id_info:
            bot.send_message(chat_id, "Пожалуйста, войдите или зарегистрируйтесь", reply_markup=kw_reg_or_log)
        else:
            dict_users_id_info[user_id][1] = [10]
            bot.send_message(chat_id, "Введите интересующий вас вопрос:")

    '''Вход'''
    if message.content_type == "text" and message.text[0] != "/" and user_id in dict_first_reg_or_log_id:
        if dict_first_reg_or_log_id[user_id][0] == 10:
            for index, phone in enumerate(dict_first_reg_or_log_id[user_id][2]):
                if message.text == phone[0]:
                    dict_first_reg_or_log_id[user_id][0] = 11
                    dict_first_reg_or_log_id[user_id][1] = dict_first_reg_or_log_id[user_id][2][index]
                    bot.send_message(chat_id, "Введите пароль")
                    break
            else:
                bot.send_message(chat_id, "Пользователя с таким телефоном нет, повторите попытку:")
        elif dict_first_reg_or_log_id[user_id][0] == 11:
            if message.text == dict_first_reg_or_log_id[user_id][1][1]:
                dict_users_id_info[user_id]=DB.authorize_user_telegram(user_id, dict_first_reg_or_log_id[user_id][1][0])
                bot.send_message(chat_id, "Вы успешно авторизовались!")
                bot.send_message(chat_id, "Введите интересующий вас вопрос:")
                dict_first_reg_or_log_id[user_id][0] = ""
                dict_users_id_info[user_id][1] = [10]
            else:
                bot.send_message(chat_id, "Неверный пароль, повторите попытку:")

        '''Регистрация'''
        if dict_first_reg_or_log_id[user_id][0] == 1:
            '''Валидация длинны Имени и Фамилии'''
            if len(message.text) <= 40:
                dict_first_reg_or_log_id[user_id][0] = 2
                dict_first_reg_or_log_id[user_id].append(message.text)  # Имя и Фамилия
                bot.send_message(chat_id, "Введите номер телефона (с кодом +375 (+11 символов) или 80 (+11 символов)):")
            else:
                bot.send_message(chat_id, "Веденные Имя и Фаилия превышают допустимую длину в 40 символов, "
                                          "повторите ввод:")
        elif dict_first_reg_or_log_id[user_id][0] == 2:
            tel = message.text.strip()
            scheme = "('{0}'[:4] == '+375' and '{0}'[1:].isdigit() and len('{0}') == 13) or" \
                     "('{0}'[:2] == '80' and '{0}'[1:].isdigit() and len('{0}') == 11)"
            '''Валидация введенного номера телефона'''
            if eval(scheme.format(tel)):
                dict_first_reg_or_log_id[user_id][0] = 3
                dict_first_reg_or_log_id[user_id].append(message.text)  # Телефон
                bot.send_message(chat_id, "Введите пароль:")
            else:
                bot.send_message(chat_id, "Неверный номера телефона, повторите попытку:")
        elif dict_first_reg_or_log_id[user_id][0] == 3:
            dict_first_reg_or_log_id[user_id][0] = 4
            dict_first_reg_or_log_id[user_id].append(message.text)  # Пароль
            bot.send_message(chat_id, "Введите вашу конфигурацию компьютера:")
        elif dict_first_reg_or_log_id[user_id][0] == 4:
            dict_first_reg_or_log_id[user_id][0] = [""]
            dict_first_reg_or_log_id[user_id].append(message.text)  # Характеристики ПК
            DB.register_new_user(dict_first_reg_or_log_id[user_id][1:])
            dict_users_id_info[dict_first_reg_or_log_id[user_id][1]] = [1, "", ["", ""]]
            dict_users_id_info[user_id][1] = [10]
            bot.send_message(chat_id, "Вы успешно зарегистрировались!")
            bot.send_message(chat_id, "Введите интересующий вас вопрос:")
            return

    '''Панель администраторов'''
    if message.text == "/admin" and dict_users_id_info[user_id][0] == 3:
        dict_users_id_info[user_id][1] = message.message_id + 1  # сохранение ид сообщения
        bot.send_message(chat_id, "Выберите предпочитаемое действие:", reply_markup=kw_admin)
        return

    '''Добавление статьи/инструкции'''
    if user_id in dict_users_id_info:
        if message.text == "/add_new_instruction" and dict_users_id_info[user_id][0] in (2, 3):  # step 1
            dict_users_id_info[user_id][1] = [1]
            bot.send_message(chat_id, "Введите название программы:")
        elif dict_users_id_info[user_id][1] != "" and dict_users_id_info[user_id][1][0] == 1:  # step 2
            dict_users_id_info[user_id][1].append(message.text)
            dict_users_id_info[user_id][1][0] = 2
            bot.send_message(chat_id, "Введите название статьи:")
        elif dict_users_id_info[user_id][1] != "" and dict_users_id_info[user_id][1][0] == 2:  # step 3
            dict_users_id_info[user_id][1].append(message.text)
            dict_users_id_info[user_id][1][0] = 3
            bot.send_message(chat_id, "Введите статью (весь необходимый текст, фото, видео и файлы по одному за "
                                      "сообщение)\nКогда статья будет готова, введите /instruction_done")
        elif message.text == "/instruction_done" and dict_users_id_info[user_id][1][0] == 3:  # занесение статьи в бд(5)
            DB.add_new_instruction_telegram([user_id] + dict_users_id_info[user_id][1][1:3] +
                                            [str(dict_users_id_info[user_id][1][3:])[1:-1]])
            dict_users_id_info[user_id][1] = [10]
            bot.send_message(chat_id, "Статья успешно добавлена в базу данных!")
        elif dict_users_id_info[user_id][1] != "" and dict_users_id_info[user_id][1][0] == 3:  # написание статьи(step4)
            if message.content_type == "text":
                dict_users_id_info[user_id][1].append(["text", message.text])
            elif message.content_type == "photo":
                photo = message.photo[-1]
                file_id = photo.file_id
                dict_users_id_info[user_id][1].append(["photo", file_id])
            elif message.content_type == "video":
                video_id = message.video.file_id
                dict_users_id_info[user_id][1].append(["video", video_id])
            elif message.content_type == "document":
                document_id = message.document.file_id
                dict_users_id_info[user_id][1].append(["document", document_id])


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    '''Нажатие на кнопку регистрации'''
    if call.data == "registration":
        dict_first_reg_or_log_id[user_id] = [1, user_id]
        bot.send_message(chat_id, "Введите Имя и Фамилию (не более 40 символов):")
        return

    # '''Нажатие на кнопку входа'''
    elif call.data == "log_in":
        dict_first_reg_or_log_id[user_id] = [10, 11, DB.get_all_registered_phones_and_passwords()]
        bot.send_message(chat_id, "Введите номер телефона:")
        return

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
        dict_users_id_info[user_id][1] = [10]
        bot.send_message(chat_id, f"Пользователь c номером '{call.data[11:]}' успешно повышен до Админа!")

    '''Удаление действующих администраторов'''
    if call.data == "delete_admin":
        kw_only_admins = InlineKeyboardMarkup()
        for user, phone in DB.get_admins_only_for_add_user():
            kw_only_admins.add(InlineKeyboardButton(f"Имя - {user}, телефон - {phone}",
                                                    callback_data=f"del_adm{phone}"))
        bot.edit_message_text("Доступные админы:\n"
                              "(Для отключения доступа Админ, кликните по пользователю)",
                              chat_id=chat_id, message_id=dict_users_id_info[user_id][1], reply_markup=kw_only_admins)
    elif call.data[:7] == "del_adm":
        DB.change_admin_access_to_user(call.data[7:])
        bot.delete_message(chat_id=chat_id, message_id=dict_users_id_info[user_id][1])
        dict_users_id_info[user_id][1] = [10]
        bot.send_message(chat_id, f"Пользователь c номером '{call.data[7:]}' был успешно лишен прав админа!")

    '''Получение инструкции по запросу пользователя'''
    if call.data[:15] == "get_instruction":
        instruction_info = DB.get_instruction_info_by_id(int(call.data[15:]))
        for type_info, info in instruction_info:
            if type_info == "text":
                bot.send_message(chat_id, info)
            elif type_info == "photo":
                bot.send_photo(chat_id, info)
            elif type_info == "video":
                bot.send_video(chat_id, info)
            elif type_info == "document":
                bot.send_document(chat_id, info)

    '''Старт чата с пользователем'''
    if "!" in call.data and user_id in dict_users_id_info:
        command, users_chat_id, users_user_id = call.data.split("!")
        users_user_id = int(users_user_id)
        message_id = call.message.message_id
        if command == "start_chat":
            chat_member = bot.get_chat_member(users_chat_id, users_user_id)
            user_name = chat_member.user.first_name
            chat_member = bot.get_chat_member(chat_id, user_id)
            admin_name = chat_member.user.first_name

            bot.edit_message_text(f"Чат между {user_name} и {admin_name} инициализирован", GROUP_ID, message_id)
            dict_users_id_info[user_id][2][0] = "Chat_activated"
            '''Предоставление доступа к чатам друг друга'''
            dict_users_id_info[users_user_id][2][1] = user_id
            dict_users_id_info[user_id][2][1] = users_chat_id
            bot.send_message(users_chat_id, f"Подключение админа {admin_name}, приятного общения! "
                                            f"Для завершения общения введите /chat_done")
            bot.send_message(user_id, f"Чат с пользователем {user_name} начат!")


'''Функция для запуска/перезапуска бота'''
def start_bot():
    try:
        print("Bot started!")
        bot.polling()
    except Exception as error:
        print(f"Бот был остановлен из-за ошибки: {error}")
        write_down_actions_to_log_file(f"Бот был остановлен из-за ошибки: {error}\nПерезапуск бота.")
        sleep(10)
        start_bot()  # Перезапустить бота


start_bot()
