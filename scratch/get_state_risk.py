import pandas as pd
df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)
crit = df[df['risk_label'] == 'CRITICAL'].groupby('state').size().sort_values(ascending=False).head(10)
high = df[df['risk_label'] == 'HIGH'].groupby('state').size()
risk_funds = df[df['risk_label'].isin(['CRITICAL', 'HIGH'])].groupby('state')['sanction_amount'].sum() / 1e7
for s, c in crit.items():
    h = high.get(s, 0)
    rf = round(risk_funds.get(s, 0.0), 1)
    print(f'{{ state: "{s}", critical: {c}, high: {h}, atRiskCr: {rf} }},')
