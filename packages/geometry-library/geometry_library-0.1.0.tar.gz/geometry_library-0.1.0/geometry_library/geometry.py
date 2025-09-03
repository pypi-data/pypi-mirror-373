
# Copyright (c) 2023 Ankit kumar singh. All rights reserved.
# Email: singhkumar50866@gmail.com
import math

class Point:
    """
    Represents a point in 2D space.

    Attributes:
        x_coordinate (float): The x-coordinate of the point.
        y_coordinate (float): The y-coordinate of the point.

    Examples:
        >>> p = Point(5, 10)
        >>> p.x_coordinate
        5
        >>> p.y_coordinate
        10
    """
    def __init__(self, x_coordinate, y_coordinate):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    def __repr__(self):
        return f"Point(x={self.x_coordinate}, y={self.y_coordinate})"

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x_coordinate == other.x_coordinate and self.y_coordinate == other.y_coordinate
        return False


class Line:
    """
    Represents a line defined by two Point objects.

    Attributes:
        point1 (Point): The first Point object defining the line.
        point2 (Point): The second Point object defining the line.

    Raises:
        TypeError: If point1 or point2 are not Point objects.

    Examples:
        >>> p1 = Point(0, 0)
        >>> p2 = Point(3, 4)
        >>> line = Line(p1, p2)
        >>> line.point1
        Point(x=0, y=0)
        >>> line.point2
        Point(x=3, y=4)
    """
    def __init__(self, point1, point2):
        if not isinstance(point1, Point) or not isinstance(point2, Point):
            raise TypeError("Both point1 and point2 must be Point objects.")
        self.point1 = point1
        self.point2 = point2

    def __repr__(self):
        return f"Line(point1={self.point1}, point2={self.point2})"

class Circle:
    """
    Represents a circle.

    Attributes:
        center_point (Point): The center Point object of the circle.
        radius (float): The radius of the circle.

    Raises:
        TypeError: If center_point is not a Point object.
        ValueError: If radius is not a non-negative number.

    Examples:
        >>> center = Point(0, 0)
        >>> circle = Circle(center, 5)
        >>> circle.center_point
        Point(x=0, y=0)
        >>> circle.radius
        5
        >>> Circle(center, -2)
        Traceback (most recent call last):
            ...
        ValueError: radius must be a non-negative number.
    """
    def __init__(self, center_point, radius):
        if not isinstance(center_point, Point):
            raise TypeError("center_point must be a Point object.")
        if not isinstance(radius, (int, float)) or radius < 0:
            raise ValueError("radius must be a non-negative number.")
        self.center_point = center_point
        self.radius = radius

    def __repr__(self):
        return f"Circle(center={self.center_point}, radius={self.radius})"

class Rectangle:
    """
    Represents a rectangle defined by its top-left corner, width, and height.

    Attributes:
        top_left_point (Point): The top-left Point object of the rectangle.
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.

    Raises:
        TypeError: If top_left_point is not a Point object.
        ValueError: If width or height are not non-negative numbers.

    Examples:
        >>> top_left = Point(1, 5)
        >>> rectangle = Rectangle(top_left, 10, 5)
        >>> rectangle.top_left_point
        Point(x=1, y=5)
        >>> rectangle.width
        10
        >>> rectangle.height
        5
    """
    def __init__(self, top_left_point, width, height):
        if not isinstance(top_left_point, Point):
            raise TypeError("top_left_point must be a Point object.")
        if not isinstance(width, (int, float)) or width < 0:
            raise ValueError("width must be a non-negative number.")
        if not isinstance(height, (int, float)) or height < 0:
            raise ValueError("height must be a non-negative number.")
        self.top_left_point = top_left_point
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Rectangle(top_left={self.top_left_point}, width={self.width}, height={self.height})"

class Polygon:
    """
    Represents a polygon defined by a list of Point objects.

    The points should be listed in order, either clockwise or counter-clockwise.

    Attributes:
        list_of_points (list[Point]): A list of Point objects defining the vertices of the polygon.

    Raises:
        TypeError: If list_of_points is not a list or contains non-Point objects.
        ValueError: If the number of points is less than 3.

    Examples:
        >>> p1 = Point(0, 0)
        >>> p2 = Point(4, 0)
        >>> p3 = Point(4, 3)
        >>> p4 = Point(0, 3)
        >>> polygon = Polygon([p1, p2, p3, p4])
        >>> polygon.list_of_points
        [Point(x=0, y=0), Point(x=4, y=0), Point(x=4, y=3), Point(x=0, y=3)]
        >>> Polygon([p1, p2])
        Traceback (most recent call last):
            ...
        ValueError: A polygon must have at least 3 points.
    """
    def __init__(self, list_of_points):
        if not isinstance(list_of_points, list) or not all(isinstance(p, Point) for p in list_of_points):
            raise TypeError("list_of_points must be a list of Point objects.")
        if len(list_of_points) < 3:
             raise ValueError("A polygon must have at least 3 points.")
        self.list_of_points = list_of_points

    def __repr__(self):
        return f"Polygon(points={self.list_of_points})"

def distance(point1, point2):
    """
    Calculates the Euclidean distance between two Point objects.

    Args:
        point1 (Point): The first Point object.
        point2 (Point): The second Point object.

    Returns:
        float: The distance between the two points.

    Raises:
        TypeError: If point1 or point2 are not Point objects.

    Examples:
        >>> p1 = Point(0, 0)
        >>> p2 = Point(3, 4)
        >>> distance(p1, p2)
        5.0
    """
    if not isinstance(point1, Point) or not isinstance(point2, Point):
        raise TypeError("Both inputs must be Point objects.")
    return math.sqrt((point2.x_coordinate - point1.x_coordinate)**2 + (point2.y_coordinate - point1.y_coordinate)**2)

def line_length(line):
    """
    Calculates the length of a Line object.

    Args:
        line (Line): The Line object.

    Returns:
        float: The length of the line.

    Raises:
        TypeError: If the input is not a Line object.

    Examples:
        >>> p1 = Point(0, 0)
        >>> p2 = Point(3, 4)
        >>> line = Line(p1, p2)
        >>> line_length(line)
        5.0
    """
    if not isinstance(line, Line):
        raise TypeError("Input must be a Line object.")
    return distance(line.point1, line.point2)

def circle_area(circle):
    """
    Calculates the area of a Circle object.

    Args:
        circle (Circle): The Circle object.

    Returns:
        float: The area of the circle.

    Raises:
        TypeError: If the input is not a Circle object.

    Examples:
        >>> center = Point(0, 0)
        >>> circle = Circle(center, 5)
        >>> round(circle_area(circle), 2)
        78.54
    """
    if not isinstance(circle, Circle):
        raise TypeError("Input must be a Circle object.")
    return math.pi * circle.radius**2

def circle_perimeter(circle):
    """
    Calculates the perimeter (circumference) of a Circle object.

    Args:
        circle (Circle): The Circle object.

    Returns:
        float: The perimeter of the circle.

    Raises:
        TypeError: If the input is not a Circle object.

    Examples:
        >>> center = Point(0, 0)
        >>> circle = Circle(center, 5)
        >>> round(circle_perimeter(circle), 2)
        31.42
    """
    if not isinstance(circle, Circle):
        raise TypeError("Input must be a Circle object.")
    return 2 * math.pi * circle.radius

def rectangle_area(rectangle):
    """
    Calculates the area of a Rectangle object.

    Args:
        rectangle (Rectangle): The Rectangle object.

    Returns:
        float: The area of the rectangle.

    Raises:
        TypeError: If the input is not a Rectangle object.

    Examples:
        >>> top_left = Point(1, 5)
        >>> rectangle = Rectangle(top_left, 10, 5)
        >>> rectangle_area(rectangle)
        50
    """
    if not isinstance(rectangle, Rectangle):
        raise TypeError("Input must be a Rectangle object.")
    return rectangle.width * rectangle.height

def rectangle_perimeter(rectangle):
    """
    Calculates the perimeter of a Rectangle object.

    Args:
        rectangle (Rectangle): The Rectangle object.

    Returns:
        float: The perimeter of the rectangle.

    Raises:
        TypeError: If the input is not a Rectangle object.

    Examples:
        >>> top_left = Point(1, 5)
        >>> rectangle = Rectangle(top_left, 10, 5)
        >>> rectangle_perimeter(rectangle)
        30
    """
    if not isinstance(rectangle, Rectangle):
        raise TypeError("Input must be a Rectangle object.")
    return 2 * (rectangle.width + rectangle.height)

def polygon_area(polygon):
    """
    Calculates the area of a Polygon object using the shoelace formula.

    Args:
        polygon (Polygon): The Polygon object.

    Returns:
        float: The area of the polygon.

    Raises:
        TypeError: If the input is not a Polygon object.

    Examples:
        >>> p1 = Point(0, 0)
        >>> p2 = Point(4, 0)
        >>> p3 = Point(4, 3)
        >>> p4 = Point(0, 3)
        >>> square = Polygon([p1, p2, p3, p4])
        >>> polygon_area(square)
        12.0
    """
    if not isinstance(polygon, Polygon):
        raise TypeError("Input must be a Polygon object.")
    points = polygon.list_of_points
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i].x_coordinate * points[j].y_coordinate
        area -= points[j].x_coordinate * points[i].y_coordinate
    area = abs(area) / 2.0
    return area

def polygon_perimeter(polygon):
    """
    Calculates the perimeter of a Polygon object by summing the lengths of its sides.

    Args:
        polygon (Polygon): The Polygon object.

    Returns:
        float: The perimeter of the polygon.

    Raises:
        TypeError: If the input is not a Polygon object.

    Examples:
        >>> p1 = Point(0, 0)
        >>> p2 = Point(4, 0)
        >>> p3 = Point(4, 3)
        >>> p4 = Point(0, 3)
        >>> square = Polygon([p1, p2, p3, p4])
        >>> polygon_perimeter(square)
        14.0
        >>> triangle = Polygon([Point(0,0), Point(3,0), Point(0,4)])
        >>> polygon_perimeter(triangle)
        12.0
    """
    if not isinstance(polygon, Polygon):
        raise TypeError("Input must be a Polygon object.")
    points = polygon.list_of_points
    n = len(points)
    perimeter = 0.0
    for i in range(n):
        j = (i + 1) % n
        perimeter += distance(points[i], points[j])
    return perimeter
