from flask import Flask, request, jsonify
import psycopg2

# Инициализация приложения Flask
data_service = Flask(__name__)

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


# Эндпоинт: список всех валют
@data_service.route('/currencies', methods=['GET'])
def get_currencies():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT currency_name, rate FROM currencies;")
        rows = cursor.fetchall()
        currencies = [
            {'currency_name': name, 'rate': float(rate)} for name, rate in rows
        ]
        return jsonify(currencies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Эндпоинт: конвертация валюты в рубли
@data_service.route('/convert', methods=['GET'])
def convert_currency():
    currency_name = request.args.get('currency_name')
    amount = request.args.get('amount')

    if not currency_name or not amount:
        return jsonify({'error': 'Параметры currency_name и amount обязательны'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'amount должен быть числом'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT rate FROM currencies WHERE currency_name = %s;", (currency_name.lower(),))
        result = cursor.fetchone()
        if result is None:
            return jsonify({'error': 'Валюта не найдена'}), 404

        rate = float(result[0])
        converted = amount * rate
        return jsonify({
            'currency_name': currency_name.lower(),
            'rate': rate,
            'amount': amount,
            'converted_to_rub': round(converted, 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    data_service.run(port=5002)
