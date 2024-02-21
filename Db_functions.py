import sqlite3 as sql
import json
from datetime import datetime


class DataBase:
    def __init__(self):
        self.db_name = 'Instructions_bot_database.db'
        self.db = sql.connect(self.db_name, check_same_thread=False)

    def write_down_actions_to_log_file(self, text):
        """Сохранение определенных действий в текстовый файл
        :param: текс для записи в лог"""
        with open("log_changes.txt", "a") as log:
            log.write(str(datetime.now())[:19] + "\n" + text + "\n")

    def get_all_telegram_id_authorized_users(self):  # модифицировать под вк
        """Получение авторизованных пользователей при перезапуске бота
        :return: словарь с ключами id пользователей и доступом"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT telegram_id, access
                                  FROM Users U JOIN Admins A ON U.user_status == A.id
                                  WHERE telegram_id IS NOT NULL''')
                id_access = cursor.fetchall()
                users_telegram_id = dict()

                for id_, access in id_access:
                    users_telegram_id[id_] = [access, "", ""]
                return users_telegram_id
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_start_bot_info_from_json(self):
        """Получение для запуска бота и вставка админов в бд, если их нет
        :return: Возвращает TOKEN для подключения к боту"""
        try:
            with open('JSON_CONFIG.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                TOKEN, GROUP_ID = data["TOKEN"], int(data["GROUP_ID"])
                main_admins, admins = ["Системный админ", data["main_admins"]], ["Админ", data["admins"]]
            with self.db:
                cursor = self.db.cursor()
                registered_phones = DataBase().get_all_sysadmins_and_admins_phones()
                '''Добавление системных админов и админов'''
                for info in [main_admins, admins]:
                    name = info[0]
                    for phone_and_password in info[1]:
                        phone_and_password = dict(phone_and_password)
                        if phone_and_password["phone_number"] not in registered_phones:
                            cursor.execute('''INSERT INTO Users (user_status, phone_number, password)
                                              VALUES ((
                                                  SELECT id
                                                  FROM Admins
                                                  WHERE access_name = ?
                                                  ), ?, ?)''', [name, phone_and_password["phone_number"],
                                                                phone_and_password["password"]])
                        else:
                            cursor.execute('''UPDATE Users
                                              SET user_status = (
                                                  SELECT id
                                                  FROM Admins
                                                  WHERE access_name = ?
                                                  ),  password = ?
                                              WHERE phone_number = ?''', [name, phone_and_password["password"],
                                                                          phone_and_password["phone_number"]])
            DataBase().write_down_actions_to_log_file("Запуск бота, установка параметров json файла")
            return [TOKEN, GROUP_ID]
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def register_new_user(self, info):  # модифицировать под вк
        """Регистрация в бд нового пользователя
        :param: [ид, имя и фамилия, телефон, пароль, сведения о пк]"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''INSERT INTO Users (user_status, telegram_id, user_name, phone_number, password, 
                                                     configuration_pc)
                                  VALUES (1, ?, ?, ?, ?, ?)''', info)
                DataBase().write_down_actions_to_log_file(f"Пользователь {info[1]} - ({info[2]}) был зарегистрирован")
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_all_sysadmins_and_admins_phones(self):
        """Получение всех номеров зарегистрированных админов и системных админов
        :return: Возвращает список номеров"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT phone_number
                                  FROM Users U JOIN Admins A ON U.user_status == A.id
                                  WHERE access_name IN ("Системный админ", "Админ")''')
                return [phone[0] for phone in cursor.fetchall()]
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_all_registered_phones_and_passwords(self):
        """Получение всех номеров пользователей
        :return: Возвращает список номеров и паролей всех пользователей"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT phone_number, password
                                  FROM Users
                                  WHERE phone_number IS NOT NULL''')
                return cursor.fetchall()
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def authorize_user_telegram(self, id_, phone):  # модифицировать под вк
        """Авторизация пользователя в бд
        :param: телеграмм ид пользователя, номер телефона"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''UPDATE Users
                                  SET telegram_id = ?
                                  WHERE phone_number = ?''', [id_, phone])
                DataBase().write_down_actions_to_log_file(f"Пользователь с номером {phone} авторизовался в telegram")
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_users_only_for_add_admin(self):
        """Получение информации о пользователях для прав администратора
        :return: список c именем и номером"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT user_name, phone_number
                                  FROM Users U JOIN Admins A ON U.user_status == A.id
                                  WHERE access_name = "Пользователь" AND phone_number IS NOT NULL''')
                return cursor.fetchall()
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def change_user_access_to_admin(self, phone):
        """Повышение доступа пользователя до администратора
        :param: номер телефона пользователя"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''UPDATE Users
                                  SET user_status = (
                                      SELECT id
                                      FROM Admins
                                      WHERE access_name = "Админ"
                                  )
                                  WHERE phone_number = ?''', [phone])
                DataBase().write_down_actions_to_log_file(f"Пользователь с номером '{phone}' был повышен до Админа")
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_admins_only_for_add_user(self):
        """Получение информации об админах для прав пользователя
        :return: список c именем и номером"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT user_name, phone_number
                                  FROM Users U JOIN Admins A ON U.user_status == A.id
                                  WHERE access_name = "Админ" AND phone_number IS NOT NULL''')
                return cursor.fetchall()
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def change_admin_access_to_user(self, phone):
        """Понижение доступа Админа до пользователя
        :param: номер телефона пользователя (Админа)"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''UPDATE Users
                                  SET user_status = (
                                      SELECT id
                                      FROM Admins
                                      WHERE access_name = "Пользователь"
                                  )
                                  WHERE phone_number = ?''', [phone])
                DataBase().write_down_actions_to_log_file(f"Пользователь с номером '{phone}' был лишен прав Админа")
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def add_new_instruction_telegram(self, info):
        """Добавление новой инструкции в базу данных
        :param: [ид пользователя (id_telegram), название программы, название статьи,
                статья (в виде текста из [тип данных, данные]...)]"""
        try:
            with self.db:
                cursor = self.db.cursor()
                info[1] = DataBase().get_id_program_name_by_name(info[1])
                print(info[1])
                cursor.execute('''INSERT INTO Instructions(author_user_id, program_id, instruction_name, instruction)
                                  VALUES ((SELECT id 
                                          FROM Users
                                          WHERE telegram_id = ?),
                                          (SELECT id
                                          FROM Programs
                                          WHERE program_name = ?), 
                                          ?, ?)''', info)
                DataBase().write_down_actions_to_log_file(f"Добавлена новая статья пользователем с "
                                                          f"id_telegram({info[0]}): {info[2]}")
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_id_program_name_by_name(self, name):
        """Получение значения ид по имени программы для вставки в статью
        :param: имя программы
        :return: ид программы"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT id
                                  FROM Programs
                                  WHERE program_name = ?''', [name])
                name_id = cursor.fetchone()
                print(name_id)
                if name_id is None:
                    cursor.execute('''INSERT INTO Programs(program_name)
                                      VALUES (?)''', [name])
                    cursor.execute('''SELECT MAX(id)
                                      FROM Programs''')
                    return cursor.fetchone()[0]
                else:
                    return name_id[0]
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_all_instruction_and_program_names(self):
        """Получение всех имен программа-статья
        :return: [(program_name, instruction)...]"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT program_name, instruction_name
                                  FROM Instructions I JOIN Programs P ON I.program_id = P.id''')
                name_instruction = cursor.fetchall()
                print(name_instruction)
                return name_instruction
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_instruction_id(self, name):
        """Получение id статьи по имени
        :param: название статьи
        :return: имя статьи"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT id
                                  FROM Instructions
                                  WHERE instruction_name = ?''', [name])
                return cursor.fetchone()[0]
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_instruction_info_by_id(self, id_instruction):
        """Получение информации по статье
        :param: id статьи
        :return: id"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT instruction
                                  FROM Instructions
                                  WHERE id = ?''', [id_instruction])
                info = cursor.fetchone()[0]
                info = eval('[' + info + ']')
                print(info)
                return info
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

# DataBase().get_start_bot_info_from_json()
# DataBase().get_all_telegram_id_authorized_users()
# DataBase().register_new_user([1381570918, 'миви', '+375252223344', '123', 'вощпщшпщпыкоп щоы зп щв'])
# DataBase().get_all_registered_phones_and_passwords()
# DataBase().get_all_instruction_and_program_names()
# DataBase().get_instruction_info_by_id(2)
# DataBase().get_id_program_name_by_name("Часы2121")
