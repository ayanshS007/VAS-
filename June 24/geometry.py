import math
from config import GRID_SPACING, UNIT_SCALE

def calculate_polygon_area(points, unit):
    area = 0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        area += (x0 * y1) - (x1 * y0)
    area = abs(area) / 2
    return area * (1 / (GRID_SPACING ** 2)) * (UNIT_SCALE[unit] ** 2)

def calculate_polygon_perimeter(points, unit):
    perimeter = 0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        dist = math.hypot(x1 - x0, y1 - y0)
        perimeter += (dist / GRID_SPACING) * UNIT_SCALE[unit]
    return perimeter