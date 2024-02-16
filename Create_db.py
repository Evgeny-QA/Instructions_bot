import sqlite3 as sql


with sql.connect('Instructions_bot_database.db') as db:
    cursor = db.cursor()
