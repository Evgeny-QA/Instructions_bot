import sqlite3 as sql
import json
from datetime import datetime


class DataBase:
    def __init__(self):
        self.db_name = 'Instructions_bot_database.db'
        self.db = sql.connect(self.db_name)

    def write_down_actions_to_log_file(self, text):
        """Сохранение определенных действий в текстовый файл"""
        with open("log_changes.txt", "a") as log:
            log.write(str(datetime.now())[:19] + "\n" + text + "\n")

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
                '''Проверка на наличие админов в бд'''
                cursor.execute('''SELECT phone_number
                                  FROM Users U JOIN Admins A ON U.user_status == A.id
                                  WHERE access IN (2, 3)''')
                registered_phones = [phone[0] for phone in cursor.fetchall()]
                # print(registered_phones)

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
