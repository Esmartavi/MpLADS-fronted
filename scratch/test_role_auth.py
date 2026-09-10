import requests

BASE = 'http://127.0.0.1:8000'

roles = [
    ('ministry_admin', 'Ministry@2026', 'MoSPI Central Ministry'),
    ('state_nodal_up', 'StateUP@2026', 'State Nodal (UP)'),
    ('district_pilibhit', 'District@2026', 'District (Pilibhit)'),
    ('mp_javed', 'MP@2026', 'MP (Javed Ali Khan)')
]

for user, pwd, label in roles:
    try:
        r = requests.post(f'{BASE}/api/login', json={'username': user, 'password': pwd}, timeout=3)
        token = r.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        kpi_res = requests.get(f'{BASE}/api/kpis', headers=headers).json()
        map_res = requests.get(f'{BASE}/api/map/states', headers=headers).json()
        
        works = kpi_res.get('total_works', 0)
        crit = kpi_res.get('critical_count', 0)
        funds = kpi_res.get('total_funds_at_risk', 0)
        
        print(f"=== {label} ===")
        print(f"  Works Monitored: {works:,}")
        print(f"  Critical Flags:  {crit:,}")
        print(f"  Capital at Risk: Rs. {funds / 1e7:.1f} Cr")
        first_st = map_res[0]['state'] if map_res else 'None'
        print(f"  States in Map:   {len(map_res)} (First: {first_st})\n")
    except Exception as e:
        print(f"Error testing {label}: {e}")
