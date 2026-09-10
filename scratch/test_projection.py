import json
import math
import os

# Load raw GeoJSON
with open('scratch/india_states_raw.geojson', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Bounds
min_lon = 68.19
max_lon = 97.42
min_lat = 6.75
max_lat = 35.50

def mercator_y(lat):
    lat_rad = math.radians(max(min(lat, 85), -85))
    return math.log(math.tan(math.pi / 4 + lat_rad / 2))

merc_min_y = mercator_y(min_lat)
merc_max_y = mercator_y(max_lat)

SVG_WIDTH = 800
SVG_HEIGHT = 900
PADDING_X = 35
PADDING_Y = 35

usable_w = SVG_WIDTH - 2 * PADDING_X
usable_h = SVG_HEIGHT - 2 * PADDING_Y

def project_pt(lon, lat):
    # Normalized [0, 1]
    norm_x = (lon - min_lon) / (max_lon - min_lon)
    norm_y = (merc_max_y - mercator_y(lat)) / (merc_max_y - merc_min_y)
    
    x = PADDING_X + norm_x * usable_w
    y = PADDING_Y + norm_y * usable_h
    return round(x, 1), round(y, 1)

# Test project GPS points
gps_pts = [
    (78.314812, 29.343646),
    (78.493202, 29.059515)
]
for lon, lat in gps_pts:
    px, py = project_pt(lon, lat)
    print(f"GPS ({lat}, {lon}) -> SVG pixel ({px}, {py})")

# Ramer-Douglas-Peucker simplification
def point_line_dist(pt, start, end):
    if start == end:
        return math.hypot(pt[0] - start[0], pt[1] - start[1])
    n = abs((end[1] - start[1]) * pt[0] - (end[0] - start[0]) * pt[1] + end[0] * start[1] - end[1] * start[0])
    d = math.hypot(end[1] - start[1], end[0] - start[0])
    return n / d

def rdp(pts, epsilon):
    if len(pts) <= 2:
        return pts
    max_d = 0.0
    idx = 0
    for i in range(1, len(pts) - 1):
        d = point_line_dist(pts[i], pts[0], pts[-1])
        if d > max_d:
            max_d = d
            idx = i
    if max_d > epsilon:
        left = rdp(pts[:idx + 1], epsilon)
        right = rdp(pts[idx:], epsilon)
        return left[:-1] + right
    else:
        return [pts[0], pts[-1]]

print("Projection test passed!")
