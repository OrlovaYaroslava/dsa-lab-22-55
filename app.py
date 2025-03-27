#Раздел I. Подготовка сервера с API.
# 1) Реализовать GET эндпоинт /number/, который принимает параметр
# запроса – param с числом. Вернуть рандомно сгенерированное
# число, умноженное на значение из параметра в формате JSON.
# 2) Реализовать POST эндпоинт /number/, который принимает в теле
# запроса JSON с полем jsonParam.Вернуть сгенерировать рандомно
# число, умноженное на то, что пришло в JSON и рандомно выбрать
# операцию.
# 3) Реализовать DELETE эндпоинт /number/, в ответе сгенерировать
# число и рандомную операцию.



from flask import Flask, request, jsonify
import random

# Создание Flask-приложения
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Добро пожаловать в API-сервер Flask</h1>
    <p>Доступные эндпоинты:</p>
    <ul>
        <li><b>GET /number/?param=5</b> - Умножает случайное число на param</li>
        <li><b>POST /number/</b> - Выполняет случайную арифметическую операцию</li>
        <li><b>DELETE /number/</b> - Генерирует случайное число и операцию</li>
    </ul>
    <p>Используйте Postman, curl или браузер для отправки запросов.</p>
    '''


# GET-запрос: принимает параметр param, возвращает случайное число, умноженное на param
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=int)
    if param is None:
        return jsonify({"error": "Параметр 'param' обязателен"}), 400
    
    random_number = random.randint(1, 100)
    result = random_number * param

    return jsonify({
        "operation": "multiplication",
        "random_number": random_number,
        "param": param,
        "result": result
    })

# POST-запрос: принимает JSON с полем jsonParam, выполняет случайную арифметическую операцию
@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    if not data or "jsonParam" not in data:
        return jsonify({"error": "Поле 'jsonParam' обязательно"}), 400

    json_param = data["jsonParam"]
    random_number = random.randint(1, 100)
    operation = random.choice(["sum", "sub", "mul", "div"])

    if operation == "sum":
        result = random_number + json_param
    elif operation == "sub":
        result = random_number - json_param
    elif operation == "mul":
        result = random_number * json_param
    elif operation == "div":
        result = random_number / json_param if json_param != 0 else "Ошибка: деление на 0"

    return jsonify({
        "operation": operation,
        "random_number": random_number,
        "jsonParam": json_param,
        "result": result
    })

# DELETE-запрос: генерирует случайное число и случайную операцию
@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_number = random.randint(1, 100)
    operation = random.choice(["sum", "sub", "mul", "div"])

    return jsonify({
        "operation": operation,
        "random_number": random_number
    })


