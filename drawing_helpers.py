import math
from config import UNIT_SCALE, GRID_SPACING

def get_distance_label(x0, y0, x1, y1, unit):
    dist = math.hypot(x1 - x0, y1 - y0)
    real_dist = (dist / GRID_SPACING) * UNIT_SCALE[unit]
    mid_x, mid_y = (x0 + x1) // 2, (y0 + y1) // 2
    return f"{real_dist:.2f} {unit}", mid_x, mid_y