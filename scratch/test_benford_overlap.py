import json
import pandas as pd

df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)
with open('benford/benford_summary.json') as f:
    benford_data = json.load(f)

top_benford_mps = benford_data.get('drilldowns', {}).get('top_mps_by_mad', [])
benford_mp_names = {item['entity'].lower().strip(): item for item in top_benford_mps}

# MP ranking by CRITICAL count or average risk
mp_summary = df.groupby('mp_name').agg(
    total_works=('work_id', 'count'),
    critical_works=('risk_label', lambda s: (s == 'CRITICAL').sum()),
    high_works=('risk_label', lambda s: (s == 'HIGH').sum()),
    avg_risk=('risk_score', 'mean'),
    avg_anomaly=('anomaly_score', 'mean'),
    total_sanctioned=('sanction_amount', 'sum')
).reset_index()

# Sort by critical works descending
top_critical_mps = mp_summary.sort_values(by=['critical_works', 'avg_risk'], ascending=False).head(20)
print("Top 20 MPs by Critical Works in Isolation Forest / Ensemble:")
print(top_critical_mps[['mp_name', 'total_works', 'critical_works', 'avg_risk']])

# Compare with Benford
print("\nBenford Top MPs by MAD:")
for m in top_benford_mps:
    print(f"  {m['entity']}: MAD={m['mad']}, status={m['conformity_status']}")

# Cross match
matches = []
for idx, r in top_critical_mps.iterrows():
    mp_name = r['mp_name']
    # Match substring or exact
    matched_benford = None
    for b_name, b_info in benford_mp_names.items():
        if b_name in mp_name.lower() or mp_name.lower() in b_name:
            matched_benford = b_info
            break
    if matched_benford:
        matches.append((mp_name, matched_benford['mad'], matched_benford['conformity_status']))

print(f"\nDirect matches in top 10 benford list: {len(matches)}")
for m in matches:
    print(f"  {m[0]} -> MAD: {m[1]} ({m[2]})")
