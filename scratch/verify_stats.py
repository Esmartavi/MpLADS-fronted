import urllib.request
import json
import pandas as pd

df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)
print("=== FRAUD FLAGS DATASET STATS ===")
print("Total rows:", len(df))
print("Unique MPs:", df['mp_name'].nunique())
print("Unique States:", df['state'].nunique())
print("Unique IDAs:", df['ida'].nunique())
print("Sanction Amount Sum:", df['sanction_amount'].sum())
print("Total Spent Sum:", df['total_spent'].sum())
print("\nRisk Tier breakdown:")
print(df['risk_label'].value_counts())

print("\n=== API /api/kpis RESPONSE ===")
req = urllib.request.Request('http://127.0.0.1:8000/api/kpis')
with urllib.request.urlopen(req) as resp:
    kpi = json.loads(resp.read().decode('utf-8'))

for k, v in kpi.items():
    print(f"  {k}: {v}")

tot = kpi['critical_count'] + kpi['high_count'] + kpi['medium_count'] + kpi['low_count']
print(f"\nMath Check 1: Label sum ({tot}) == total_works ({kpi['total_works']}): {tot == kpi['total_works']}")
risk_sum = round(kpi['funds_at_critical_risk'] + kpi['funds_at_high_risk'], 2)
print(f"Math Check 2: Total funds at risk ({kpi['total_funds_at_risk']}) == crit+high ({risk_sum}): {kpi['total_funds_at_risk'] == risk_sum}")

print("\n=== API /api/auth/options RESPONSE ===")
with urllib.request.urlopen('http://127.0.0.1:8000/api/auth/options') as resp:
    opts = json.loads(resp.read().decode('utf-8'))

print("Total States in options:", len(opts['states']))
print("Total MPs in options:", len(opts['mps']))
print("Bihar districts count:", len(opts['districts_by_state'].get('Bihar', [])))
print("UP districts count:", len(opts['districts_by_state'].get('Uttar Pradesh', [])))

print("\n=== API /api/map/states RESPONSE ===")
with urllib.request.urlopen('http://127.0.0.1:8000/api/map/states') as resp:
    map_states = json.loads(resp.read().decode('utf-8'))
print("Total Map States returned:", len(map_states.get('states', [])))

print("\nAll checks completed.")
