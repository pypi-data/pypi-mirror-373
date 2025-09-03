
import unittest
import math
from geometry_library.geometry import Point, Line, Circle, Rectangle, Polygon, distance, line_length, circle_area, circle_perimeter, rectangle_area, rectangle_perimeter, polygon_area, polygon_perimeter

class TestGeometry(unittest.TestCase):
    """Unit tests for the geometry library."""

    def test_point_initialization(self):
        """Test Point class initialization."""
        p = Point(10, 20)
        self.assertEqual(p.x_coordinate, 10)
        self.assertEqual(p.y_coordinate, 20)

    def test_line_initialization(self):
        """Test Line class initialization."""
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        line = Line(p1, p2)
        self.assertEqual(line.point1, p1)
        self.assertEqual(line.point2, p2)

        # Test invalid input
        with self.assertRaises(TypeError):
            Line(p1, 123)
        with self.assertRaises(TypeError):
            Line(456, p2)

    def test_circle_initialization(self):
        """Test Circle class initialization."""
        center = Point(0, 0)
        circle = Circle(center, 5)
        self.assertEqual(circle.center_point, center)
        self.assertEqual(circle.radius, 5)

        # Test invalid input
        with self.assertRaises(TypeError):
            Circle(123, 5)
        with self.assertRaises(ValueError):
            Circle(center, -2)
        with self.assertRaises(TypeError):
            Circle(center, "large")

    def test_rectangle_initialization(self):
        """Test Rectangle class initialization."""
        top_left = Point(1, 5)
        rectangle = Rectangle(top_left, 10, 5)
        self.assertEqual(rectangle.top_left_point, top_left)
        self.assertEqual(rectangle.width, 10)
        self.assertEqual(rectangle.height, 5)

        # Test invalid input
        with self.assertRaises(TypeError):
            Rectangle(123, 10, 5)
        with self.assertRaises(ValueError):
            Rectangle(top_left, -10, 5)
        with self.assertRaises(ValueError):
            Rectangle(top_left, 10, -5)
        with self.assertRaises(TypeError):
            Rectangle(top_left, "wide", 5)
        with self.assertRaises(TypeError):
            Rectangle(top_left, 10, "tall")


    def test_polygon_initialization(self):
        """Test Polygon class initialization."""
        points = [Point(0, 0), Point(1, 0), Point(1, 1)]
        polygon = Polygon(points)
        self.assertEqual(polygon.list_of_points, points)

        # Test invalid input
        with self.assertRaises(TypeError):
            Polygon("not a list")
        with self.assertRaises(TypeError):
            Polygon([Point(0,0), "not a point", Point(1,1)])
        with self.assertRaises(ValueError):
            Polygon([Point(0,0), Point(1,0)]) # Less than 3 points

    def test_distance(self):
        """Test the distance function."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        self.assertAlmostEqual(distance(p1, p2), 5.0)

        # Test distance between the same point
        self.assertAlmostEqual(distance(p1, p1), 0.0)

        # Test with negative coordinates
        p3 = Point(-1, -1)
        p4 = Point(2, 3)
        self.assertAlmostEqual(distance(p3, p4), 5.0)

        # Test invalid input
        with self.assertRaises(TypeError):
            distance(p1, 123)
        with self.assertRaises(TypeError):
            distance(456, p2)


    def test_line_length(self):
        """Test the line_length function."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        line = Line(p1, p2)
        self.assertAlmostEqual(line_length(line), 5.0)

        # Test with a line of zero length
        line_zero = Line(p1, p1)
        self.assertAlmostEqual(line_length(line_zero), 0.0)

        # Test invalid input
        with self.assertRaises(TypeError):
            line_length(123)

    def test_circle_area(self):
        """Test the circle_area function."""
        center = Point(0, 0)
        circle = Circle(center, 5)
        self.assertAlmostEqual(circle_area(circle), math.pi * 25)

        # Test circle with radius 0
        circle_zero = Circle(center, 0)
        self.assertAlmostEqual(circle_area(circle_zero), 0.0)

        # Test invalid input
        with self.assertRaises(TypeError):
            circle_area(123)

    def test_circle_perimeter(self):
        """Test the circle_perimeter function."""
        center = Point(0, 0)
        circle = Circle(center, 5)
        self.assertAlmostEqual(circle_perimeter(circle), 2 * math.pi * 5)

        # Test circle with radius 0
        circle_zero = Circle(center, 0)
        self.assertAlmostEqual(circle_perimeter(circle_zero), 0.0)

        # Test invalid input
        with self.assertRaises(TypeError):
            circle_perimeter(123)

    def test_rectangle_area(self):
        """Test the rectangle_area function."""
        top_left = Point(0, 0)
        rectangle = Rectangle(top_left, 10, 5)
        self.assertAlmostEqual(rectangle_area(rectangle), 50.0)

        # Test rectangle with zero width or height
        rectangle_zero_width = Rectangle(top_left, 0, 5)
        self.assertAlmostEqual(rectangle_area(rectangle_zero_width), 0.0)
        rectangle_zero_height = Rectangle(top_left, 10, 0)
        self.assertAlmostEqual(rectangle_area(rectangle_zero_height), 0.0)

        # Test invalid input
        with self.assertRaises(TypeError):
            rectangle_area(123)

    def test_rectangle_perimeter(self):
        """Test the rectangle_perimeter function."""
        top_left = Point(0, 0)
        rectangle = Rectangle(top_left, 10, 5)
        self.assertAlmostEqual(rectangle_perimeter(rectangle), 30.0)

        # Test rectangle with zero width or height
        rectangle_zero_width = Rectangle(top_left, 0, 5)
        self.assertAlmostEqual(rectangle_perimeter(rectangle_zero_width), 10.0)
        rectangle_zero_height = Rectangle(top_left, 10, 0)
        self.assertAlmostEqual(rectangle_perimeter(rectangle_zero_height), 20.0)
         # Test invalid input
        with self.assertRaises(TypeError):
            rectangle_perimeter(123)

    def test_polygon_area(self):
        """Test the polygon_area function."""
        # Square
        square_points = [Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)]
        square = Polygon(square_points)
        self.assertAlmostEqual(polygon_area(square), 16.0)

        # Triangle
        triangle_points = [Point(0, 0), Point(3, 0), Point(0, 4)]
        triangle = Polygon(triangle_points)
        self.assertAlmostEqual(polygon_area(triangle), 6.0)

        # Degenerate polygon (collinear points)
        degenerate_points = [Point(0, 0), Point(1, 0), Point(2, 0)]
        degenerate_polygon = Polygon(degenerate_points)
        self.assertAlmostEqual(polygon_area(degenerate_polygon), 0.0)

        # Test invalid input
        with self.assertRaises(TypeError):
            polygon_area(123)

    def test_polygon_perimeter(self):
        """Test the polygon_perimeter function."""
        # Square
        square_points = [Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)]
        square = Polygon(square_points)
        self.assertAlmostEqual(polygon_perimeter(square), 16.0)

        # Triangle
        triangle_points = [Point(0, 0), Point(3, 0), Point(0, 4)]
        triangle = Polygon(triangle_points)
        self.assertAlmostEqual(polygon_perimeter(triangle), 12.0) # 3 + 4 + 5

        # Degenerate polygon (collinear points)
        degenerate_points = [Point(0, 0), Point(1, 0), Point(2, 0)]
        degenerate_polygon = Polygon(degenerate_points)
        self.assertAlmostEqual(polygon_perimeter(degenerate_polygon), 2.0) # 1 + 1 + 0

        # Test invalid input
        with self.assertRaises(TypeError):
            polygon_perimeter(123)

# To run the tests from the command line:
# python -m unittest tests/test_geometry.py
