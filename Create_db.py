import sqlite3 as sql


with sql.connect('Instructions_bot_database.db') as db:
    cursor = db.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Admins(
        id INTEGER PRIMARY KEY,
        access INTEGER DEFAULT 0,
        name_access TEXT
    );

    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        user_status INTEGER,
        user_name TEXT,
        phone_number TEXT,
        password TEXT,
        configuration_pc TEXTб,
        FOREIGN KEY (user_status) REFERENCES Admins(id)
    );

    CREATE TABLE IF NOT EXISTS Commentaries(
        id INTEGER PRIMARY KEY,
        instruction_id INTEGER,
        commenatry TEXT,
        FOREIGN KEY (instruction_id) REFERENCES Instructions(id)
    );

    CREATE TABLE IF NOT EXISTS Programms(
        id INTEGER PRIMARY KEY,
        programm_name TEXT
    );
    
    CREATE TABLE IF NOT EXISTS Instructions(
        id INTEGER PRIMARY KEY,
        programm_id INTEGER,
        author_user_id INTEGER,
        instruction TEXT,
        grade INTEGER DEFAULT 4,
        freshness INTEGER DEFAULT 10,
        FOREIGN KEY (programm_id) REFERENCES Programms(id),
        FOREIGN KEY (author_user_id) REFERENCES Users(id)
    );
    """)

print('ready')


