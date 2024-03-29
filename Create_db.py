import sqlite3 as sql


with sql.connect('Instructions_bot_database.db') as db:
    cursor = db.cursor()

    '''Создание основной базы данных и заполнение таблицы Admins с уровнями доступов'''
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Admins(
        id INTEGER PRIMARY KEY,
        access INTEGER,
        access_name TEXT
    );
        
    INSERT INTO Admins(access, name_access)
    VALUES (1, "Пользователь"),
           (2, "Админ"),
           (3, "Системный админ");

    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        user_status INTEGER DEFAULT 1,
        user_name TEXT,
        phone_number TEXT UNIQUE,
        password TEXT,
        configuration_pc TEXT,
        telegram_id INTEGER,
        vk_id INTEGER,
        FOREIGN KEY (user_status) REFERENCES Admins(id)
    );

    CREATE TABLE IF NOT EXISTS Commentaries(
        id INTEGER PRIMARY KEY,
        instruction_id INTEGER,
        commentary TEXT,
        FOREIGN KEY (instruction_id) REFERENCES Instructions(id)
    );

    CREATE TABLE IF NOT EXISTS Programs(
        id INTEGER PRIMARY KEY,
        program_name TEXT
    );

    CREATE TABLE IF NOT EXISTS Instructions(
        id INTEGER PRIMARY KEY,
        author_user_id INTEGER,
        program_id INTEGER,
        instruction_name TEXT,
        instruction TEXT,
        grade INTEGER DEFAULT 4,
        freshness INTEGER DEFAULT 10,
        FOREIGN KEY (program_id) REFERENCES Programs(id),
        FOREIGN KEY (author_user_id) REFERENCES Users(id)
    );
    """)

print('ready')

