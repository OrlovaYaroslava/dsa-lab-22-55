# Чтение строки с клавиатуры
text = input("Введите строку: ")

word = ""
words = []

# Разбиение строки на слова вручную
for char in text + " ":
    if char.isalpha():
        word += char
    elif word:
        words.append(word)
        word = ""

# Вывод слов, оканчивающихся на "u"
for word in words:
    if word[-1] == "u":
        print(word)
