import json


'''Получение токена для старта бота и админов для управления ботов'''
with open('JSON_CONFIG.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    TOKEN = data["TOKEN"]
    print(TOKEN)
