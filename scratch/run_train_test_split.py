import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix

df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)

# Confirmed statutory violation (ground truth proxy)
# Premature tranche, missing photo, early payment, split tender, overspend
df['confirmed_violation'] = (
    df['rule_premature_tranche'].astype(str).str.lower().isin(['true', '1', 't']) |
    df['rule_missing_photo'].astype(str).str.lower().isin(['true', '1', 't']) |
    df['rule_early_payment'].astype(str).str.lower().isin(['true', '1', 't']) |
    df['rule_split_tender'].astype(str).str.lower().isin(['true', '1', 't']) |
    df['rule_overspend'].astype(str).str.lower().isin(['true', '1', 't'])
)

print(f"Total works: {len(df):,}")
print(f"Confirmed violations: {df['confirmed_violation'].sum():,} ({df['confirmed_violation'].mean()*100:.2f}%)")

# Extract the exact feature set used in Model 1 Isolation Forest
# We can use the existing columns or recompute features
# In fraud_flags.csv we have:
# sanction_amount, total_spent, progress_pct, days_since_sanction, days_to_sanction, etc.
# Let's check features available
features = [
    'sanction_amount',
    'total_spent',
    'progress_pct',
    'days_since_sanction',
    'work_vendor_concentration'
]
X = df[features].copy().fillna(0)
y = df['confirmed_violation'].astype(int)

# 80-20 Train-Test Split (stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Train size: {len(X_train):,}, Test size: {len(X_test):,}")

# Train Isolation Forest ONLY on the 80% train set
iso = IsolationForest(n_estimators=200, contamination=0.20, random_state=42, n_jobs=-1)
iso.fit(X_train)

# Predict on unseen 20% test set
test_raw_scores = -iso.decision_function(X_test)
# min-max normalize test scores
test_scores = (test_raw_scores - test_raw_scores.min()) / (test_raw_scores.max() - test_raw_scores.min())

auc = roc_auc_score(y_test, test_scores)
print(f"Test Set AUC-ROC: {auc:.4f}")

# Top 10% most suspicious in test set
top_10_pct_idx = int(len(test_scores) * 0.10)
top_threshold = np.percentile(test_scores, 90)
y_pred_top10 = (test_scores >= top_threshold).astype(int)

tp_top10 = ((y_pred_top10 == 1) & (y_test == 1)).sum()
fp_top10 = ((y_pred_top10 == 1) & (y_test == 0)).sum()
prec_top10 = tp_top10 / (tp_top10 + fp_top10)

print(f"Precision @ Top 10% in unseen test set: {prec_top10*100:.2f}% (TP={tp_top10:,}, FP={fp_top10:,})")

# Also let's check Ensemble / Risk score AUC-ROC across entire dataset or test set
auc_risk = roc_auc_score(df['confirmed_violation'], df['risk_score'])
print(f"Full Dataset Ensemble Risk Score AUC-ROC: {auc_risk:.4f}")
