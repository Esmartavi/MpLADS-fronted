import json
import math
import os
import pandas as pd
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union

# Load official Survey of India boundary GeoJSON (760 district features)
SOI_PATH = 'scratch/soi_india_raw.geojson'
if not os.path.exists(SOI_PATH):
    raise FileNotFoundError(f"Missing {SOI_PATH}")

with open(SOI_PATH, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data['features'])} district features from Survey of India dataset.")

# Projection Parameters
# Covers all 36 States & UTs including Indira Col / Siachen / Aksai Chin at 37.08° N
MIN_LON = 68.0
MAX_LON = 97.5
MIN_LAT = 6.5
MAX_LAT = 37.3

SVG_WIDTH = 800
SVG_HEIGHT = 920
PADDING_X = 25
PADDING_Y = 25

usable_w = SVG_WIDTH - 2 * PADDING_X
usable_h = SVG_HEIGHT - 2 * PADDING_Y

def mercator_y(lat):
    lat_rad = math.radians(max(min(lat, 85), -85))
    return math.log(math.tan(math.pi / 4 + lat_rad / 2))

merc_min_y = mercator_y(MIN_LAT)
merc_max_y = mercator_y(MAX_LAT)

def project_pt(lon, lat):
    norm_x = (lon - MIN_LON) / (MAX_LON - MIN_LON)
    norm_y = (merc_max_y - mercator_y(lat)) / (merc_max_y - merc_min_y)
    x = PADDING_X + norm_x * usable_w
    y = PADDING_Y + norm_y * usable_h
    return round(x, 1), round(y, 1)

# Group districts by state name
state_groups = {}
for feat in raw_data['features']:
    props = feat.get('properties', {})
    st_name = props.get('st_nm') or props.get('ST_NM') or 'Unknown'
    geom = shape(feat['geometry'])
    if st_name not in state_groups:
        state_groups[st_name] = []
    state_groups[st_name].append(geom)

print(f"Aggregating {len(state_groups)} distinct States & Union Territories...")

# Standardize state names to match backend database exactly
NAME_MAP = {
    'Andaman and Nicobar Islands': 'Andaman And Nicobar Islands',
    'Dadra and Nagar Haveli and Daman and Diu': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Jammu and Kashmir': 'Jammu And Kashmir'
}

state_items = []
simplified_features = []

# Special center overrides for tricky concave / island shapes to ensure perfect label placement
CENTER_OVERRIDES = {
    'Jammu And Kashmir': (75.0, 33.6),
    'Ladakh': (76.8, 34.6),
    'Kerala': (76.5, 10.3),
    'Gujarat': (71.5, 22.3),
    'West Bengal': (88.0, 24.0),
    'Assam': (92.8, 26.3),
    'Puducherry': (79.8, 11.9),
    'The Dadra And Nagar Haveli And Daman And Diu': (72.9, 20.3)
}

for raw_name in sorted(state_groups.keys()):
    geoms = state_groups[raw_name]
    db_name = NAME_MAP.get(raw_name, raw_name)
    state_slug = "".join(c.lower() for c in db_name if c.isalnum() or c == '_')

    # Dissolve districts into single unified state boundary
    u = unary_union(geoms)
    if not u.is_valid:
        u = u.buffer(0)

    # Simplify to smooth tolerance (~1 km precision)
    simplified = u.simplify(0.008, preserve_topology=True)
    if not simplified.is_valid:
        simplified = simplified.buffer(0)

    # Extract path commands
    path_commands = []
    all_pts_projected = []

    def process_poly(poly):
        cmds = []
        ext_coords = list(poly.exterior.coords)
        ext_proj = [project_pt(x, y) for x, y in ext_coords]
        all_pts_projected.extend(ext_proj)
        if ext_proj:
            cmds.append(f"M {ext_proj[0][0]},{ext_proj[0][1]} " + " ".join(f"L {x},{y}" for x, y in ext_proj[1:]) + " Z")
        
        for interior in poly.interiors:
            hole_coords = list(interior.coords)
            hole_proj = [project_pt(x, y) for x, y in hole_coords]
            all_pts_projected.extend(hole_proj)
            if hole_proj:
                cmds.append(f"M {hole_proj[0][0]},{hole_proj[0][1]} " + " ".join(f"L {x},{y}" for x, y in hole_proj[1:]) + " Z")
        return " ".join(cmds)

    if simplified.geom_type == 'Polygon':
        path_commands.append(process_poly(simplified))
    elif simplified.geom_type == 'MultiPolygon':
        for sub_poly in simplified.geoms:
            path_commands.append(process_poly(sub_poly))

    full_path_str = " ".join(path_commands)

    # Calculate center point
    if db_name in CENTER_OVERRIDES:
        c_lon, c_lat = CENTER_OVERRIDES[db_name]
        center_x, center_y = project_pt(c_lon, c_lat)
    else:
        rep_pt = simplified.representative_point()
        center_x, center_y = project_pt(rep_pt.x, rep_pt.y)

    # Calculate bbox
    minx, miny, maxx, maxy = simplified.bounds
    p_min = project_pt(minx, maxy)
    p_max = project_pt(maxx, miny)
    bbox = [p_min[0], p_min[1], p_max[0], p_max[1]]

    state_items.append({
        'id': state_slug,
        'name': raw_name,
        'db_name': db_name,
        'path': full_path_str,
        'center': [center_x, center_y],
        'bbox': bbox,
        'point_count': len(all_pts_projected)
    })

    simplified_features.append({
        'type': 'Feature',
        'properties': {
            'NAME_1': raw_name,
            'ST_NM': db_name,
            'db_name': db_name
        },
        'geometry': mapping(simplified)
    })

print(f"Successfully processed all {len(state_items)} States & UTs.")
total_points = sum(s['point_count'] for s in state_items)
print(f"Total vector coordinates across India: {total_points:,}")

# Save simplified GeoJSON
os.makedirs('frontend/public', exist_ok=True)
simp_geojson = {
    'type': 'FeatureCollection',
    'features': simplified_features
}
with open('frontend/public/india_states.geojson', 'w', encoding='utf-8') as f:
    json.dump(simp_geojson, f)

geojson_size = os.path.getsize('frontend/public/india_states.geojson')
print(f"Saved frontend/public/india_states.geojson: {geojson_size / 1024:.1f} KB")

# Load and project the 12 ground-truth GPS records from works_with_gps_and_vendors.csv
gps_df = pd.read_csv('data/processed/works_with_gps_and_vendors.csv')
valid_gps = gps_df[gps_df['latitude'].notna() & (pd.to_numeric(gps_df['latitude'], errors='coerce') > 0)].copy()

gps_records = []
for _, row in valid_gps.iterrows():
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    px, py = project_pt(lon, lat)
    gps_records.append({
        'work_id': str(row.get('work_id', '')),
        'canonical_work_id': str(row.get('canonical_work_id', '')),
        'mp_name': str(row.get('mp_name', '')),
        'state': str(row.get('state', '')),
        'constituency': str(row.get('constituency', '')),
        'latitude': lat,
        'longitude': lon,
        'svg_x': px,
        'svg_y': py,
        'disbursed_amount': float(row.get('disbursed_amount', 0) or 0),
        'gps_source': str(row.get('gps_source', 'Camera Watermark'))
    })

print(f"Projected {len(gps_records)} forensic camera watermark GPS pins.")

# Write frontend/src/data/indiaMapData.js
os.makedirs('frontend/src/data', exist_ok=True)
js_content = f"""/**
 * BHARAT-DRISHTI Geospatial Intelligence Vector Grid
 * Official Survey of India (SOI) Boundaries with Full Crown (J&K + Ladakh) & All 36 States/UTs
 * Mercator Projection onto SVG ViewBox 0 0 {SVG_WIDTH} {SVG_HEIGHT}
 */

export const SVG_MAP_CONFIG = {{
  viewBox: "0 0 {SVG_WIDTH} {SVG_HEIGHT}",
  width: {SVG_WIDTH},
  height: {SVG_HEIGHT},
  minLon: {MIN_LON},
  maxLon: {MAX_LON},
  minLat: {MIN_LAT},
  maxLat: {MAX_LAT}
}};

// Mathematical Mercator Coordinate Projection: (lat, lon) -> [svgX, svgY]
export function projectGeoPoint(lat, lon) {{
  const minLon = {MIN_LON};
  const maxLon = {MAX_LON};
  const minLat = {MIN_LAT};
  const maxLat = {MAX_LAT};
  
  const mercatorY = (l) => {{
    const rad = (Math.max(Math.min(l, 85), -85) * Math.PI) / 180;
    return Math.log(Math.tan(Math.PI / 4 + rad / 2));
  }};
  
  const mercMinY = mercatorY(minLat);
  const mercMaxY = mercatorY(maxLat);
  const normX = (lon - minLon) / (maxLon - minLon);
  const normY = (mercMaxY - mercatorY(lat)) / (mercMaxY - mercMinY);
  
  const px = {PADDING_X} + normX * {usable_w};
  const py = {PADDING_Y} + normY * {usable_h};
  return [Number(px.toFixed(1)), Number(py.toFixed(1))];
}}

// 12 Ground-Truthed Forensic GPS Evidence Works (Extracted via Camera Watermark Vision AI)
export const GPS_EVIDENCE_POINTS = {json.dumps(gps_records, indent=2)};

// Complete Vector Paths for all 36 Indian States & Union Territories (Official SOI Boundaries)
export const INDIA_STATE_PATHS = {json.dumps(state_items, indent=2)};
"""

with open('frontend/src/data/indiaMapData.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

js_size = os.path.getsize('frontend/src/data/indiaMapData.js')
print(f"Saved frontend/src/data/indiaMapData.js: {js_size / 1024:.1f} KB")

# Write standalone preview SVG for inspection
svg_preview = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" style="background:#0b1120;">',
    '<defs>',
    '  <filter id="glow"><feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#38bdf8" floodOpacity="0.8"/></filter>',
    '</defs>'
]

colors = [
    '#0284c7', '#059669', '#d97706', '#dc2626', '#7c3aed', '#db2777', 
    '#0d9488', '#ea580c', '#4f46e5', '#16a34a', '#2563eb', '#ca8a04'
]

for i, s in enumerate(state_items):
    color = colors[i % len(colors)]
    svg_preview.append(
        f'  <path id="{s["id"]}" d="{s["path"]}" fill="{color}" fill-opacity="0.45" stroke="#38bdf8" stroke-width="0.9" fill-rule="evenodd">'
        f'<title>{s["db_name"]}</title></path>'
    )
    # Add label
    cx, cy = s['center']
    name_short = s['db_name'].replace(' Islands', '').replace('The ', '')
    if len(name_short) > 13:
        name_short = name_short[:11] + '..'
    svg_preview.append(
        f'  <text x="{cx}" y="{cy}" font-family="sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="middle" opacity="0.85">{name_short}</text>'
    )

# Add GPS pins
for g in gps_records:
    svg_preview.append(
        f'  <circle cx="{g["svg_x"]}" cy="{g["svg_y"]}" r="5" fill="#f43f5e" stroke="#ffffff" stroke-width="1.5"/>'
    )

svg_preview.append('</svg>')

with open('scratch/soi_india_preview.svg', 'w', encoding='utf-8') as f:
    f.write("\n".join(svg_preview))

print("Saved scratch/soi_india_preview.svg for visual verification.")
