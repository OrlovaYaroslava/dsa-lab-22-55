import logging
import asyncio
import os
import aiohttp
import psycopg2
from flask import Flask, request, jsonify

# Создание микросервиса
role_service = Flask(__name__)

# Настройки подключения к БД
DB_CONFIG = {
    'dbname': 'currency_bot',
    'user': 'currency_user',
    'password': 'currency_pass',
    'host': 'localhost',
    'port': 5432
}

# Подключение к базе данных

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# Эндпоинт: проверить, является ли пользователь администратором
@role_service.route('/is_admin/<int:chat_id>', methods=['GET'])
def check_admin(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM admins WHERE chat_id = %s;", (str(chat_id),))
        result = cursor.fetchone()
        return jsonify({'is_admin': result is not None}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    role_service.run(port=5003)
