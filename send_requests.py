#Раздел II. Отправка запросов на сервер с API.
# 1) Отправить запрос GET /number с параметром запроса
# param=[рандомное число от 1 до 10]. В ответ будет выдано число и
# операция - запомнить их.
# 2) Отправить запрос POST /number с телом JSON {"jsonParam":
# [рандомное число от 1 до 10]}. В заголовках необходимо указать
# content-type=application/json. В ответ будет выдано число и операция
# - запомнить их.
# 3) Отправить запрос DELETE /number/. В ответ будет выдано число и
# операция - запомнить их.
# 4) Из полученных ответов составить выражение, посчитать и привести
# полученное значение к int(). Операции выполнять последовательно. 


import requests
import random

# Базовый URL сервера Flask
BASE_URL = "http://127.0.0.1:5000"

# Генерация случайных чисел от 1 до 10
param_value = random.randint(1, 10)
json_param_value = random.randint(1, 10)

# Отправляем GET-запрос
print(f"\nОтправка GET-запроса с param={param_value}")
response_get = requests.get(f"{BASE_URL}/number/", params={"param": param_value})
data_get = response_get.json()
print("Ответ сервера:", data_get)

# Теперь берем result, а не random_number
result = data_get["result"]
operation_1 = data_get["operation"]

# Отправляем POST-запрос
print(f"\nОтправка POST-запроса с jsonParam={json_param_value}")
response_post = requests.post(
    f"{BASE_URL}/number/", 
    json={"jsonParam": json_param_value},
    headers={"Content-Type": "application/json"}
)
data_post = response_post.json()
print("Ответ сервера:", data_post)

num_2 = data_post["random_number"]
operation_2 = data_post["operation"]

# Отправляем DELETE-запрос
print("\nОтправка DELETE-запроса")
response_delete = requests.delete(f"{BASE_URL}/number/")
data_delete = response_delete.json()
print("Ответ сервера:", data_delete)

num_3 = data_delete["random_number"]
operation_3 = data_delete["operation"]

# Выполняем арифметические операции последовательно
print("\nВыполнение арифметических операций")

# Применение первой операции (GET) - уже учтено выше
print(f"После GET: {result}")

# Применение второй операции (POST)
if operation_2 == "sum":
    result += num_2
elif operation_2 == "sub":
    result -= num_2
elif operation_2 == "mul":
    result *= num_2
elif operation_2 == "div":
    result = result / num_2 if num_2 != 0 else result
print(f"После POST: {result}")

# Применение третьей операции (DELETE)
if operation_3 == "sum":
    result += num_3
elif operation_3 == "sub":
    result -= num_3
elif operation_3 == "mul":
    result *= num_3
elif operation_3 == "div":
    result = result / num_3 if num_3 != 0 else result
print(f"После DELETE: {result}")

# Приведение результата к целому числу
final_result = int(result)
print(f"\nИтоговый результат: {final_result}")
