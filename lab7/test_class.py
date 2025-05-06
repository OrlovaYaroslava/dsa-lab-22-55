import pytest
from triangle_class import Triangle, IncorrectTriangleSides

# Позитивные тесты

def test_equilateral_triangle():
    """Тестирование равностороннего треугольника"""
    triangle = Triangle(3, 3, 3)
    assert triangle.triangle_type() == "equilateral"
    assert triangle.perimeter() == 9  # 3 + 3 + 3

def test_isosceles_triangle():
    """Тестирование равнобедренного треугольника"""
    triangle = Triangle(5, 5, 3)
    assert triangle.triangle_type() == "isosceles"
    assert triangle.perimeter() == 13  # 5 + 5 + 3

def test_nonequilateral_triangle():
    """Тестирование разностороннего треугольника"""
    triangle = Triangle(3, 4, 5)
    assert triangle.triangle_type() == "nonequilateral"
    assert triangle.perimeter() == 12  # 3 + 4 + 5

# Негативные тесты

def test_negative_side():
    """Тестирование случая с отрицательной стороной"""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-3, 4, 5)

def test_zero_side():
    """Тестирование случая с нулевой стороной"""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 4, 5)

def test_invalid_triangle():
    """Тестирование случая, когда сумма двух сторон меньше или равна третьей"""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 1, 3)

def test_side_too_large():
    """Тестирование случая, когда одна сторона больше суммы двух других"""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(10, 3, 2)

def test_all_negative_sides():
    """Тестирование случая с отрицательными сторонами"""
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-5, -5, -5)
