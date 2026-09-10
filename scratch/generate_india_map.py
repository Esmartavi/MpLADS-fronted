import json
import math
import os

# Load raw GeoJSON
with open('scratch/india_states_raw.geojson', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

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
    norm_x = (lon - min_lon) / (max_lon - min_lon)
    norm_y = (merc_max_y - mercator_y(lat)) / (merc_max_y - merc_min_y)
    x = PADDING_X + norm_x * usable_w
    y = PADDING_Y + norm_y * usable_h
    return round(x, 1), round(y, 1)

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

# Map raw GeoJSON name to official DB state name
NAME_MAP = {
    'Andaman and Nicobar': 'Andaman And Nicobar Islands',
    'Andhra Pradesh': 'Andhra Pradesh',
    'Arunachal Pradesh': 'Arunachal Pradesh',
    'Assam': 'Assam',
    'Bihar': 'Bihar',
    'Chandigarh': 'Chandigarh',
    'Chhattisgarh': 'Chhattisgarh',
    'Dadra and Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman and Diu': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Delhi': 'Delhi',
    'Goa': 'Goa',
    'Gujarat': 'Gujarat',
    'Haryana': 'Haryana',
    'Himachal Pradesh': 'Himachal Pradesh',
    'Jammu and Kashmir': 'Jammu And Kashmir',
    'Jharkhand': 'Jharkhand',
    'Karnataka': 'Karnataka',
    'Kerala': 'Kerala',
    'Lakshadweep': 'Lakshadweep',
    'Madhya Pradesh': 'Madhya Pradesh',
    'Maharashtra': 'Maharashtra',
    'Manipur': 'Manipur',
    'Meghalaya': 'Meghalaya',
    'Mizoram': 'Mizoram',
    'Nagaland': 'Nagaland',
    'Orissa': 'Odisha',
    'Puducherry': 'Puducherry',
    'Punjab': 'Punjab',
    'Rajasthan': 'Rajasthan',
    'Sikkim': 'Sikkim',
    'Tamil Nadu': 'Tamil Nadu',
    'Telangana': 'Telangana',
    'Tripura': 'Tripura',
    'Uttar Pradesh': 'Uttar Pradesh',
    'Uttaranchal': 'Uttarakhand',
    'West Bengal': 'West Bengal'
}

# Simplify epsilon in lat/lon degrees
EPSILON_DEG = 0.015 # ~1.5 km tolerance, great detail, compact file

state_items = []
simplified_features = []

for feat in raw_data['features']:
    props = feat['properties']
    raw_name = props.get('NAME_1') or props.get('name') or props.get('ST_NM') or 'Unknown'
    db_name = NAME_MAP.get(raw_name, raw_name)
    geom = feat['geometry']
    gtype = geom['type']
    coords = geom['coordinates']
    
    path_commands = []
    simplified_coords = []
    all_pts_projected = []
    
    if gtype == 'Polygon':
        simp_poly = []
        for ring in coords:
            # ring is list of [lon, lat]
            simp_ring = rdp(ring, EPSILON_DEG)
            if len(simp_ring) < 3:
                simp_ring = ring
            simp_poly.append(simp_ring)
            
            ring_pts = []
            for lon, lat in simp_ring:
                px, py = project_pt(lon, lat)
                ring_pts.append(f"{px},{py}")
                all_pts_projected.append((px, py))
            if ring_pts:
                path_commands.append(f"M{ring_pts[0]}L{'L'.join(ring_pts[1:])}Z")
        simplified_coords = simp_poly
        
    elif gtype == 'MultiPolygon':
        simp_multipoly = []
        for poly in coords:
            simp_poly = []
            for ring in poly:
                simp_ring = rdp(ring, EPSILON_DEG)
                if len(simp_ring) < 3:
                    simp_ring = ring
                simp_poly.append(simp_ring)
                
                ring_pts = []
                for lon, lat in simp_ring:
                    px, py = project_pt(lon, lat)
                    ring_pts.append(f"{px},{py}")
                    all_pts_projected.append((px, py))
                if ring_pts:
                    path_commands.append(f"M{ring_pts[0]}L{'L'.join(ring_pts[1:])}Z")
            simp_multipoly.append(simp_poly)
        simplified_coords = simp_multipoly

    # Calculate center of bounding box
    if all_pts_projected:
        xs = [p[0] for p in all_pts_projected]
        ys = [p[1] for p in all_pts_projected]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        center_x = round((min_x + max_x) / 2, 1)
        center_y = round((min_y + max_y) / 2, 1)
    else:
        center_x, center_y = 400, 450
        min_x, max_x, min_y, max_y = 0, 800, 0, 900
        
    full_path_str = "".join(path_commands)
    state_slug = "".join(c.lower() for c in raw_name if c.isalnum() or c == '_')
    
    state_items.append({
        'id': state_slug,
        'name': raw_name,
        'db_name': db_name,
        'path': full_path_str,
        'center': [center_x, center_y],
        'bbox': [round(min_x, 1), round(min_y, 1), round(max_x, 1), round(max_y, 1)],
        'point_count': len(all_pts_projected)
    })
    
    simplified_features.append({
        'type': 'Feature',
        'properties': {
            'NAME_1': raw_name,
            'ST_NM': db_name,
            'db_name': db_name
        },
        'geometry': {
            'type': gtype,
            'coordinates': simplified_coords
        }
    })

print(f"Processed {len(state_items)} states/UTs.")
total_points = sum(s['point_count'] for s in state_items)
print(f"Total points across all states: {total_points:,}")

# Save simplified GeoJSON to frontend/public/india_states.geojson
os.makedirs('frontend/public', exist_ok=True)
simp_geojson = {
    'type': 'FeatureCollection',
    'features': simplified_features
}
with open('frontend/public/india_states.geojson', 'w', encoding='utf-8') as f:
    json.dump(simp_geojson, f)

geojson_size = os.path.getsize('frontend/public/india_states.geojson')
print(f"Saved frontend/public/india_states.geojson: {geojson_size / 1024:.1f} KB")

# Get the 12 ground-truth GPS records from works_with_gps_and_vendors.csv
import pandas as pd
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

print(f"Prepared {len(gps_records)} GPS evidence points with pixel coordinates.")

# Write frontend/src/data/indiaMapData.js
os.makedirs('frontend/src/data', exist_ok=True)
js_content = f"""/**
 * BHARAT-DRISHTI Geospatial Intelligence Vector Grid
 * Precision Vector Projection & GPS Evidence Coordinates for India (36 States & UTs)
 * Generated from official boundaries with Mercator Projection onto SVG ViewBox 0 0 800 900.
 */

export const SVG_MAP_CONFIG = {{
  viewBox: "0 0 {SVG_WIDTH} {SVG_HEIGHT}",
  width: {SVG_WIDTH},
  height: {SVG_HEIGHT},
  minLon: {min_lon},
  maxLon: {max_lon},
  minLat: {min_lat},
  maxLat: {max_lat}
}};

// Mathematical Mercator Coordinate Projection: (lat, lon) -> [svgX, svgY]
export function projectGeoPoint(lat, lon) {{
  const minLon = {min_lon};
  const maxLon = {max_lon};
  const minLat = {min_lat};
  const maxLat = {max_lat};
  
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

// Complete Vector Paths for all 36 Indian States & Union Territories
export const INDIA_STATE_PATHS = {json.dumps(state_items, indent=2)};
"""

with open('frontend/src/data/indiaMapData.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

js_size = os.path.getsize('frontend/src/data/indiaMapData.js')
print(f"Saved frontend/src/data/indiaMapData.js: {js_size / 1024:.1f} KB")
