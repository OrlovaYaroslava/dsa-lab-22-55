from flask import Flask, request, jsonify
import psycopg2

currency_service = Flask(__name__)

# Настройки подключения к БД
def get_connection():
    return psycopg2.connect(
        dbname="currency_bot",
        user="currency_user",
        password="currency_pass",
        host="localhost",
        port=5432
    )


# Эндпоинт для добавления валюты
@currency_service.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    name = data.get('currency_name')
    rate = data.get('rate')

    if not name or not rate:
        return jsonify({'error': 'currency_name и rate обязательны'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s);",
            (name.lower(), rate)
        )
        conn.commit()
        return jsonify({'message': f'Валюта {name.upper()} добавлена.'}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'error': 'Такая валюта уже существует.'}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Эндпоинт для обновления курса валюты
@currency_service.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    name = data.get('currency_name')
    new_rate = data.get('rate')

    if not name or not new_rate:
        return jsonify({'error': 'currency_name и rate обязательны'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s;",
            (new_rate, name.lower())
        )
        if cursor.rowcount == 0:
            return jsonify({'error': 'Валюта не найдена.'}), 404
        conn.commit()
        return jsonify({'message': f'Курс валюты {name.upper()} обновлён на {new_rate}.'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Эндпоинт для удаления валюты
@currency_service.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    name = data.get('currency_name')

    if not name:
        return jsonify({'error': 'currency_name обязателен'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM currencies WHERE currency_name = %s;",
            (name.lower(),)
        )
        if cursor.rowcount == 0:
            return jsonify({'error': 'Валюта не найдена.'}), 404
        conn.commit()
        return jsonify({'message': f'Валюта {name.upper()} удалена.'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    currency_service.run(port=5001)
