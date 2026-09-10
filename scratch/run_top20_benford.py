import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from benford.core import BenfordAnalyzer

df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)

# Top 20 MPs by average risk score
mp_stats = df.groupby('mp_name').agg(
    total_works=('work_id', 'count'),
    critical_count=('risk_label', lambda s: (s=='CRITICAL').sum()),
    avg_risk=('risk_score', 'mean'),
    avg_anomaly=('anomaly_score', 'mean')
).reset_index()

# Only consider MPs with at least 50 works for statistical validity
mp_stats = mp_stats[mp_stats['total_works'] >= 50]
top20_mps = mp_stats.sort_values(by=['avg_risk', 'critical_count'], ascending=False).head(20)

print('=== BENFORD TEST ON TOP 20 HIGHEST RISK MPs ===')
non_conform_count = 0
for idx, r in top20_mps.reset_index(drop=True).iterrows():
    mp = r['mp_name']
    amounts = df[df['mp_name'] == mp]['sanction_amount'].dropna()
    amounts = amounts[amounts > 0]
    res = BenfordAnalyzer.evaluate(amounts, test_type='first_digit', min_sample_size=30)
    is_non_conform = 'Non-Conformity' in res.conformity_status or res.mad > 0.015
    if is_non_conform: 
        non_conform_count += 1
    print(f"{idx+1:>2}. {mp[:30]:30s} | Works: {r['total_works']:3d} | Risk: {r['avg_risk']:.1f} | MAD: {res.mad:.4f} | {res.conformity_status}")

print(f"\nTotal Non-Conformity among top 20 MPs: {non_conform_count}/20 ({non_conform_count/20*100:.1f}%)")
