import os, glob, pandas as pd, json

# Count total lines of code
total_py_lines = 0
total_jsx_lines = 0
py_files = []
for pyf in glob.glob('**/*.py', recursive=True):
    if 'venv' in pyf or '__pycache__' in pyf:
        continue
    try:
        lines = open(pyf, encoding='utf-8', errors='ignore').readlines()
        total_py_lines += len(lines)
        py_files.append((pyf, len(lines)))
    except:
        pass
for jsxf in glob.glob('**/*.jsx', recursive=True):
    try:
        lines = open(jsxf, encoding='utf-8', errors='ignore').readlines()
        total_jsx_lines += len(lines)
    except:
        pass

print(f'Python lines of code: {total_py_lines:,}')
print(f'JSX/JS lines of code: {total_jsx_lines:,}')
print(f'Total codebase lines: {total_py_lines + total_jsx_lines:,}')
print()
print('Python files and sizes:')
for fn, n in sorted(py_files, key=lambda x: -x[1])[:15]:
    print(f'  {fn}: {n:,} lines')

# Dataset metrics
df = pd.read_csv('data/processed/fraud_flags.csv', low_memory=False)
print(f'\nTotal fraud_flags records: {len(df):,}')
crit = df[df['risk_label'] == 'CRITICAL']
high = df[df['risk_label'] == 'HIGH']
med  = df[df['risk_label'] == 'MEDIUM']
low  = df[df['risk_label'] == 'LOW']
print(f'CRITICAL works: {len(crit):,}')
print(f'HIGH works: {len(high):,}')
print(f'MEDIUM works: {len(med):,}')
print(f'LOW works: {len(low):,}')
total_sanctioned = df['sanction_amount'].sum()
crit_funds = crit['sanction_amount'].sum()
print(f'Total sanctioned (crore): Rs.{total_sanctioned/1e7:.1f} Cr')
print(f'Funds at CRITICAL risk (crore): Rs.{crit_funds/1e7:.1f} Cr')
print(f'% of funds at risk: {crit_funds/total_sanctioned*100:.1f}%')
print()
print(f'Rules triggered:')
for rule_col in ['rule_missing_photo','rule_premature_tranche','rule_split_tender','rule_early_payment','rule_overspend','rule_stalled_execution']:
    if rule_col in df.columns:
        cnt = df[rule_col].astype(str).str.lower().isin(['true','1']).sum()
        print(f'  {rule_col}: {cnt:,}')

# GPS
gps_csv = pd.read_csv('data/processed/works_with_gps_and_vendors.csv')
gps_valid = gps_csv[gps_csv['latitude'].notnull() & (gps_csv['latitude'].astype(str).str.strip() != '')]
print(f'\nGPS audited PDFs: {len(gps_csv)}')
print(f'Valid GPS coordinates extracted: {len(gps_valid)}')

# Vendor alias
alias_csv = pd.read_csv('data/processed/vendor_alias_map.csv')
print(f'Vendor alias map entries: {len(alias_csv):,}')

# Portal images registry
reg = json.load(open('forensics/works_with_images_registry.json'))
print(f'\nPortal image registry entries: {len(reg):,}')

# PDFs
pdfs = glob.glob('images/downloaded_pdfs/*.pdf')
print(f'Downloaded completion certificate PDFs: {len(pdfs)}')

# Phash vault
phash_vault = json.load(open('forensics/phash_vault.json'))
print(f'pHash visual fingerprints stored: {len(phash_vault)}')

# Forensics summary
fsummary = json.load(open('forensics/forensics_summary.json'))
print(f'Forensics summary entries: {len(fsummary) if isinstance(fsummary, list) else len(fsummary.keys())}')

# Duplicate photo flags
dup = json.load(open('forensics/duplicate_photo_flags.json'))
print(f'Duplicate photo flags: {len(dup)}')
