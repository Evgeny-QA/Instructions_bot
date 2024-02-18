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
                                  FROM Users U JOIN Admins A ON U.user_status == A.id''')
                id_access = cursor.fetchall()
                users_telegram_id = dict()

                for id_, access in id_access:
                    if id_ is not None:
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
                TOKEN, main_admins, admins = data["TOKEN"], data["main_admins"], data["admins"]
            # print(TOKEN, main_admins, admins, sep="\n")
            with self.db:
                cursor = self.db.cursor()
                registered_phones = DataBase().get_all_sysadmins_and_admins_phones()

                '''Добавление системных админов и админов'''
                for phone_user in main_admins:
                    if phone_user["phone_number"] not in registered_phones:
                        cursor.execute('''INSERT INTO Users (user_status, phone_number, password)
                                          VALUES (3, ?, ?)''', [phone_user["phone_number"], phone_user["password"]])
                for phone_user in admins:
                    if phone_user["phone_number"] not in registered_phones:
                        cursor.execute('''INSERT INTO Users (user_status, phone_number, password)
                                          VALUES (2, ?, ?)''', [phone_user["phone_number"], phone_user["password"]])

            DataBase().write_down_actions_to_log_file("Запуск бота, установка параметров json файла")
            return TOKEN
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def register_new_user(self, info):  # модифицировать под вк
        """Регистрация в бд нового пользователя
        :param: [ид, имя и фамилия, телефон, пароль, сведения о пк]"""
        try:
            with self.db:
                print(0)
                cursor = self.db.cursor()
                print(1)
                print(info)
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
                                  WHERE access IN (2, 3)''')
                return [phone[0] for phone in cursor.fetchall()]
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

    def get_all_registered_phones_and_passwords(self):
        """Получение всех номеров зарегистрированных админов и системных админов
        :return: Возвращает список номеров"""
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT phone_number, access
                                  FROM Users U JOIN Admins A ON U.user_status == A.id''')
                return [phone[0] for phone in cursor.fetchall()]
        except sql.Error as error:
            print(f"Произошла ошибка: {error}")
            return False

# DataBase().get_start_bot_info_from_json()
# DataBase().get_all_telegram_id_authorized_users()
#DataBase().register_new_user([1381570918, 'миви', '+375252223344', '123', 'вощпщшпщпыкоп щоы зп щв'])
