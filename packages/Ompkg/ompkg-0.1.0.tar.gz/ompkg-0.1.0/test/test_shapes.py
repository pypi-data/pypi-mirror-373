import pytest
from CalcArea.calcarea import Rectangle, Square, calculate_area
#from CalcArea import calcarea.py
def test_rectangle_area():
    rect = Rectangle(4, 5)
    assert calculate_area(rect) == 20

def test_square_area():
    square = Square(6)
    assert calculate_area(square) == 36

def test_zero_area():
    assert calculate_area(Rectangle(0, 10)) == 0
    assert calculate_area(Square(0)) == 0

def test_negative_values():
    assert calculate_area(Rectangle(-3, 4)) == -12
    assert calculate_area(Square(-5)) == 25
