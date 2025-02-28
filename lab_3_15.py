import random

# Читаем размер массива
N = 10  # Или введите N вручную
arr = [random.randint(1, 30) * 2 + 1 for _ in range(N)]  # Генерируем нечетные числа

# Числа меньше 10
small_numbers = [num for num in arr if num < 10]

# Умножаем четные индексы на 2
for i in range(0, len(arr), 2):
    arr[i] *= 2

# Вывод результатов
print(f"Исходный массив: {arr}")
print(f"Числа меньше 10: {small_numbers if small_numbers else 'Нет чисел < 10'}")
print(f"Модифицированный массив: {arr}")
