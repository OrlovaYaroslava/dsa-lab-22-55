import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestTriangleType(unittest.TestCase):
    """
    Класс для тестирования функции get_triangle_type.
    Используем стандартный фреймворк unittest для организации тестов.
    """

    # Позитивные тесты:
    def test_equilateral_triangle(self):
        """Тестирование равностороннего треугольника"""
        result = get_triangle_type(3, 3, 3)
        self.assertEqual(result, "equilateral")

    def test_isosceles_triangle(self):
        """Тестирование равнобедренного треугольника"""
        result = get_triangle_type(5, 5, 3)
        self.assertEqual(result, "isosceles")

    def test_nonequilateral_triangle(self):
        """Тестирование разностороннего треугольника"""
        result = get_triangle_type(3, 4, 5)
        self.assertEqual(result, "nonequilateral")

    # Негативные тесты:
    def test_negative_side(self):
        """Тестирование случая с отрицательной стороной"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-3, 4, 5)

    def test_zero_side(self):
        """Тестирование случая с нулевой стороной"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 4, 5)

    def test_invalid_triangle(self):
        """Тестирование случая, когда сумма двух сторон меньше или равна третьей"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 1, 3)

    def test_side_too_large(self):
        """Тестирование случая, когда одна сторона больше суммы двух других"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(10, 3, 2)

    def test_all_negative_sides(self):
        """Тестирование случая с отрицательными сторонами"""
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-5, -5, -5)


if __name__ == '__main__':
    unittest.main()
