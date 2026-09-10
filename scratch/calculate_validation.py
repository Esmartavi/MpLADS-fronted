import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)
print(f"Total works: {len(df):,}")

# The 4 legally-certain / statutory rules identified in Approach 1:
# 1. premature tranche (Clause 4.3)
# 2. missing photo (MoSPI reporting guidelines on completed works)
# 3. early payment (payment before sanction date)
# 4. split tender (GFR Rule 149/155 evasion band)
# (Also overspend if disbursed > sanctioned)

rule_cols = ['rule_premature_tranche', 'rule_missing_photo', 'rule_early_payment', 'rule_split_tender', 'rule_overspend']
for col in rule_cols:
    if col in df.columns:
        # ensure boolean
        df[col] = df[col].astype(str).str.lower().isin(['true', '1', 't'])
        print(f"  {col}: {df[col].sum():,} works")

# Approach 1: Core 4 Statutory Rules
df['statutory_violation_4'] = (
    df['rule_premature_tranche'] |
    df['rule_missing_photo'] |
    df['rule_early_payment'] |
    df['rule_split_tender']
)

# All statutory violations (including overspend)
df['confirmed_violation'] = (
    df['rule_premature_tranche'] |
    df['rule_missing_photo'] |
    df['rule_early_payment'] |
    df['rule_split_tender'] |
    df['rule_overspend']
)

print(f"\nTotal works with 4 Statutory Violations: {df['statutory_violation_4'].sum():,} ({df['statutory_violation_4'].mean()*100:.2f}%)")
print(f"Total works with All Confirmed Violations: {df['confirmed_violation'].sum():,} ({df['confirmed_violation'].mean()*100:.2f}%)")

# Let's check Isolation Forest (anomaly_score or anomaly_score_pct)
# Isolation Forest contamination was 0.05 or let's inspect anomaly_score distribution
print("\nAnomaly Score summary:")
print(df['anomaly_score'].describe())
print("\nAnomaly Score Pct summary:")
print(df['anomaly_score_pct'].describe())

# Let's test various thresholds for Isolation forest (e.g. top 10%, top 15%, top 20%, top 25%, anomaly_score_pct >= 80, >= 85, >= 90)
for p in [75, 80, 85, 90, 95]:
    thresh = df['anomaly_score_pct'].quantile(p / 100.0)
    ml_flagged = df['anomaly_score_pct'] >= thresh
    tp = (ml_flagged & df['confirmed_violation']).sum()
    fp = (ml_flagged & ~df['confirmed_violation']).sum()
    fn = (~ml_flagged & df['confirmed_violation']).sum()
    tn = (~ml_flagged & ~df['confirmed_violation']).sum()
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    print(f"\nThreshold Top {100-p}% (anomaly_score_pct >= {thresh:.1f}): Flagged = {ml_flagged.sum():,}")
    print(f"  TP: {tp:,}, FP: {fp:,}, FN: {fn:,}, TN: {tn:,}")
    print(f"  Precision: {prec*100:.2f}%, Recall: {rec*100:.2f}%, F1: {f1*100:.2f}%")

# Also check Risk Score / Risk Label (CRITICAL / HIGH)
for label_set, name in [
    (['CRITICAL'], 'CRITICAL only'),
    (['CRITICAL', 'HIGH'], 'CRITICAL + HIGH'),
]:
    ml_flagged = df['risk_label'].isin(label_set)
    tp = (ml_flagged & df['confirmed_violation']).sum()
    fp = (ml_flagged & ~df['confirmed_violation']).sum()
    fn = (~ml_flagged & df['confirmed_violation']).sum()
    tn = (~ml_flagged & ~df['confirmed_violation']).sum()
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    print(f"\nModel 5 Ensemble ({name}): Flagged = {ml_flagged.sum():,}")
    print(f"  TP: {tp:,}, FP: {fp:,}, FN: {fn:,}, TN: {tn:,}")
    print(f"  Precision: {prec*100:.2f}%, Recall: {rec*100:.2f}%, F1: {f1*100:.2f}%")
