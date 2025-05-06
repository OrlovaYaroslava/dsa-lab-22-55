# triangle_class.py

class IncorrectTriangleSides(Exception):
    """Исключение для некорректных сторон треугольника."""
    pass


class Triangle:
    """
    Класс для описания треугольника с тремя сторонами.
    Включает методы для:
    - проверки типа треугольника
    - вычисления периметра треугольника
    """

    def __init__(self, a, b, c):
        """
        Конструктор для создания треугольника.
        
        Параметры:
        a (float): длина первой стороны.
        b (float): длина второй стороны.
        c (float): длина третьей стороны.

        Исключения:
        IncorrectTriangleSides: если хотя бы одна из сторон не положительна
        или не выполняется условие существования треугольника.
        """
        # Проверка на положительные значения сторон.
        if a <= 0 or b <= 0 or c <= 0:
            raise IncorrectTriangleSides("Стороны треугольника должны быть положительными числами.")
        
        # Проверка на корректность треугольника (сумма двух сторон должна быть больше третьей).
        if a + b <= c or a + c <= b or b + c <= a:
            raise IncorrectTriangleSides("Сумма любых двух сторон треугольника должна быть больше третьей.")
        
        # Инициализация сторон треугольника.
        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):
        """
        Метод для определения типа треугольника.

        Возвращает:
        str: тип треугольника ("equilateral", "isosceles", "nonequilateral").
        """
        if self.a == self.b == self.c:
            return "equilateral"  # Равносторонний треугольник
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"  # Равнобедренный треугольник
        else:
            return "nonequilateral"  # Разносторонний треугольник

    def perimeter(self):
        """
        Метод для вычисления периметра треугольника.

        Возвращает:
        float: периметр треугольника.
        """
        return self.a + self.b + self.c
