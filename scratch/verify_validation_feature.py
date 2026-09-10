import urllib.request
import json

res = urllib.request.urlopen('http://127.0.0.1:8000/api/model-validation')
data = json.loads(res.read().decode())
print("HTTP 200 OK - /api/model-validation")
print()

es = data.get("executive_summary", {})
print("=== EXECUTIVE SUMMARY ===")
for k, v in es.items():
    print(f"  {k}: {v}")
print()

a1 = data.get("approach_1_rules_ground_truth", {})
t1 = a1.get("tier1_critical", {})
print("=== CONFUSION MATRIX (TIER 1: CRITICAL ONLY) ===")
print(f"  Flagged: {t1.get('flagged_count', 0):,}")
print(f"  TP: {t1.get('true_positives', 0):,}  FP: {t1.get('false_positives', 0):,}")
print(f"  FN: {t1.get('false_negatives', 0):,}  TN: {t1.get('true_negatives', 0):,}")
print(f"  Precision: {t1.get('precision_pct')}%  Recall: {t1.get('recall_pct')}%  F1: {t1.get('f1_score_pct')}%")
print(f"  False Positive Rate: {t1.get('false_positive_rate_pct')}%")
print()

t2 = a1.get("tier2_ensemble", {})
print("=== CONFUSION MATRIX (TIER 2: CRITICAL + HIGH) ===")
print(f"  Flagged: {t2.get('flagged_count', 0):,}")
print(f"  TP: {t2.get('true_positives', 0):,}  FP: {t2.get('false_positives', 0):,}")
print(f"  FN: {t2.get('false_negatives', 0):,}  TN: {t2.get('true_negatives', 0):,}")
print(f"  Precision: {t2.get('precision_pct')}%  Recall: {t2.get('recall_pct')}%  F1: {t2.get('f1_score_pct')}%")
print(f"  AUC-ROC: {t2.get('auc_roc')}")
print()

m1 = a1.get("model1_isolation_forest_top10", {})
print("=== MODEL 1 ALONE: ISOLATION FOREST TOP 10% ===")
print(f"  Flagged: {m1.get('flagged_count', 0):,}")
print(f"  TP: {m1.get('true_positives', 0):,}  FP: {m1.get('false_positives', 0):,}")
print(f"  Precision: {m1.get('precision_pct')}%  Recall: {m1.get('recall_pct')}%")
print()

a2 = data.get("approach_2_train_test_split", {})
print("=== APPROACH 2: 80-20 STRATIFIED TRAIN-TEST SPLIT ===")
print(f"  Split: {a2.get('test_split_ratio')}")
print(f"  Train: {a2.get('train_samples', 0):,}  Test: {a2.get('test_samples', 0):,}")
print(f"  Isolation Forest test AUC: {a2.get('test_isolation_forest_auc')}")
print(f"  Ensemble Risk test AUC: {a2.get('test_ensemble_risk_auc')}")
print(f"  Precision @ Top 10% in Test: {a2.get('test_precision_at_top_10_pct')}%")
print(f"  Conclusion: {a2.get('conclusion')}")
print()

a3 = data.get("approach_3_benford_cross_validation", {})
print("=== APPROACH 3: BENFORD'S LAW TRIANGULATION ===")
print(f"  MPs evaluated: {a3.get('top_mps_evaluated')}")
print(f"  Non-conformity matches: {a3.get('independent_non_conformity_matches')}")
print(f"  Cross-Method Agreement: {a3.get('cross_method_agreement_pct')}%")
print(f"  Summary: {a3.get('summary')}")
print()

rb = a1.get("rule_breakdown", {})
print("=== STATUTORY RULE BREAKDOWN ===")
for k, v in rb.items():
    name = v.get('name', '').encode('ascii', errors='replace').decode('ascii')
    print(f"  {name}: {v.get('statutory_count', 0):,} works | Ensemble recall: {v.get('recall_pct')}%")
print()

top = data.get("top_audited_works", [])
verified_count = sum(1 for w in top if w.get("is_verified"))
print("=== TOP AUDITED WORKS CASE VERIFICATION ===")
print(f"  {verified_count}/{len(top)} top-ranked works have objective statutory violations ({verified_count/max(1,len(top))*100:.1f}%)")
for w in top[:5]:
    print(f"  #{w['rank']} {w['work_id']} [{w['risk_label']}] Score:{w['risk_score']} -- Violations: {len(w['statutory_violations'])}")
print()

jtp = data.get("judge_talking_points", [])
print(f"=== JUDGE TALKING POINTS: {len(jtp)} Q&A pairs ready ===")
for j in jtp:
    print(f"  Q: {j['question']}")
