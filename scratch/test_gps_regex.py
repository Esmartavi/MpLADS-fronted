import re

def dms_to_dd(d, m, s, ref):
    dd = float(d) + float(m)/60.0 + float(s)/3600.0
    if str(ref).upper() in ['S', 'W']:
        dd = -dd
    return dd

def parse_gps_coordinates(text: str):
    """
    Robust multi-pattern GPS extractor:
    1. Hindi / Bilingual Camera Banners (अक्षांश, देशांतर, Lat, Long)
    2. DMS format (Degrees, Minutes, Seconds) used by NoteCam / GPS Map Camera
    3. Standard decimal format with N/E markers
    4. Multi-line separated Latitude and Longitude blocks
    """
    if not text:
        return None

    # Pattern 1: Hindi / Bilingual camera banner
    p_hindi = re.search(r'(?:अक्षांश|Lat(?:itude)?)[^\d]{0,15}([0-9]{1,2}\.[0-9]{3,8})[^\d]{0,40}(?:देशांतर|Long(?:itude)?)[^\d]{0,15}([0-9]{2,3}\.[0-9]{3,8})', text, re.IGNORECASE)
    if p_hindi:
        try:
            lat = float(p_hindi.group(1))
            lon = float(p_hindi.group(2))
            if 6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0:
                return {"latitude": round(lat, 6), "longitude": round(lon, 6), "source": "Watermark (Hindi/Bilingual)"}
        except Exception:
            pass

    # Pattern 2: DMS (Degrees, Minutes, Seconds) e.g. 21°59'14.5"N 82°33'40.2"E
    p_dms = re.search(r'([0-9]{1,2})°\s*([0-9]{1,2})\'\s*([0-9]{1,2}(?:\.[0-9]+)?)\"?\s*([NnSs])[\s,]+([0-9]{2,3})°\s*([0-9]{1,2})\'\s*([0-9]{1,2}(?:\.[0-9]+)?)\"?\s*([EeWw])', text)
    if p_dms:
        try:
            lat = dms_to_dd(p_dms.group(1), p_dms.group(2), p_dms.group(3), p_dms.group(4))
            lon = dms_to_dd(p_dms.group(5), p_dms.group(6), p_dms.group(7), p_dms.group(8))
            if 6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0:
                return {"latitude": round(lat, 6), "longitude": round(lon, 6), "source": "Watermark (DMS)"}
        except Exception:
            pass

    # Pattern 3: Standard decimal degrees with optional degree symbol and N/E
    p_dec = re.search(r'([0-9]{1,2}\.[0-9]{4,8})\s*°?\s*[Nn][\s,]+([0-9]{2,3}\.[0-9]{4,8})\s*°?\s*[Ee]', text)
    if p_dec:
        try:
            lat = float(p_dec.group(1))
            lon = float(p_dec.group(2))
            if 6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0:
                return {"latitude": round(lat, 6), "longitude": round(lon, 6), "source": "Watermark (Decimal Degrees)"}
        except Exception:
            pass

    # Pattern 4: Multi-line independent Lat and Long search
    p_lat = re.search(r'(?:Latitude|Lat|अक्षांश)\s*[:\s]?\s*([0-9]{1,2}\.[0-9]{3,8})', text, re.IGNORECASE)
    p_lon = re.search(r'(?:Longitude|Long|Lon|देशांतर)\s*[:\s]?\s*([0-9]{2,3}\.[0-9]{3,8})', text, re.IGNORECASE)
    if p_lat and p_lon:
        try:
            lat = float(p_lat.group(1))
            lon = float(p_lon.group(1))
            if 6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0:
                return {"latitude": round(lat, 6), "longitude": round(lon, 6), "source": "Watermark (Multi-line)"}
        except Exception:
            pass

    return None

if __name__ == "__main__":
    tests = [
        "GPS Map Camera \n Janjgir, CG \n Lat 21.984234° Long 82.561198° \n 26/09/2024",
        "NoteCam \n 21°59'14.5\"N 82°33'40.2\"E \n Altitude: 240m",
        "अक्षांश: 22.01456 देशांतर: 82.12984",
        "Latitude: 21.4567 N \n Date: 12-Oct-2024 \n Longitude: 82.7891 E",
        "28.6139° N, 77.2090° E New Delhi"
    ]
    for idx, t in enumerate(tests, 1):
        res = parse_gps_coordinates(t)
        print(f"Test {idx}: {res}")
