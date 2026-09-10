# 🏛️ BHARAT-DRISHTI Model Validation & Accuracy Report
**Generated:** 2026-09-10 13:51:50  
**Dataset Scope:** 98,649 MPLADS Works  

## 1. Executive Performance Summary

| Metric | Result | Methodology |
|---|---|---|
| **Statutory Rule Precision (Tier 1)** | **100.0%** | Zero-ambiguity statutory violations (0% FP) |
| **Ensemble Precision (CRITICAL+HIGH)** | **83.66%** | Evaluated against ground-truth statutory labels |
| **Ensemble Recall** | **70.51%** | Percentage of statutory violations captured |
| **Ensemble F1 Score** | **76.52%** | Balanced harmonic mean |
| **Model Generalization AUC-ROC** | **0.8551** | 80/20 Stratified train-test split |
| **Benford's Law Cross-Validation** | **20/20 (100%)** | Top 20 high-risk MPs evaluated independently |

## 2. Confusion Matrix (Ensemble vs Ground Truth)

```
                 Confirmed Violation = True    Confirmed Violation = False
ML Flagged       15878                         3101                       
ML Clean         6642                          73028                      
```
