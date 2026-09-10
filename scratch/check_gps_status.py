import json
import os
import glob
import pandas as pd

def main():
    print("=================================================================")
    print("            BHARAT-DRISHTI: DEEP GPS EXTRACTION AUDIT            ")
    print("=================================================================")

    # 1. Pipeline Queue Overview
    pdf_dir = "images/downloaded_pdfs"
    all_pdfs = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    total_downloaded = len(all_pdfs)

    state_file = "forensics/audit_worker_state.json"
    processed_set = set()
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        processed_set = set(state.get("processed_files", []))
    
    audited_count = len(processed_set)
    remaining_in_queue = total_downloaded - audited_count

    print(f"Total Downloaded PDFs in Local Queue:  {total_downloaded}")
    print(f"Total PDFs Audited So Far:             {audited_count} ({(audited_count/total_downloaded)*100:.1f}%)")
    print(f"Total Downloaded PDFs Remaining:       {remaining_in_queue} ({(remaining_in_queue/total_downloaded)*100:.1f}%)")

    # 2. GPS CSV Analysis
    csv_p = "data/processed/works_with_gps_and_vendors.csv"
    if os.path.exists(csv_p):
        df = pd.read_csv(csv_p)
        total_records = len(df)
        gps_df = df[df["latitude"].notnull() & (df["latitude"].astype(str).str.strip() != "")]
        no_gps_df = df[df["latitude"].isnull() | (df["latitude"].astype(str).str.strip() == "")]
        
        print(f"\nAudit Master Ledger Records:           {total_records}")
        print(f"Verified Extracted GPS Coordinates:    {len(gps_df)} ({len(gps_df)/total_records*100:.1f}% extraction hit rate)")
        print(f"Documents Without GPS (Administrative):{len(no_gps_df)} ({len(no_gps_df)/total_records*100:.1f}%)")

        print("\n" + "-"*65)
        print("          DETAILED LIST OF EXTRACTED GPS COORDINATES             ")
        print("-" * 65)
        for i, (_, r) in enumerate(gps_df.iterrows(), 1):
            print(f"[{i:02d}] Work ID: {r.get('work_id')} | MP: {r.get('mp_name')} | Const: {r.get('constituency')}")
            print(f"     Coordinates:  Latitude {r.get('latitude')}, Longitude {r.get('longitude')}")
            print(f"     Source:       {r.get('gps_source')}")
            print(f"     PDF File:     {r.get('pdf_filename')}")
            print()

        # GPS Geolocation clusters
        print("-" * 65)
        print("                 GEOLOCATION CLUSTERING                          ")
        print("-" * 65)
        clusters = gps_df.groupby(["state", "constituency"]).size()
        for (st, const), count in clusters.items():
            print(f"  • {st} -> Constituency: {const}: {count} geotagged sites")
            
    # 3. Macro Registry Scope (MoSPI Portal)
    reg_file = "forensics/works_with_images_registry.json"
    if os.path.exists(reg_file):
        with open(reg_file, "r", encoding="utf-8") as f:
            reg = json.load(f)
        total_portal_docs = len(reg)
        print("\n" + "=" * 65)
        print("          MACRO PERSPECTIVE (LIVE MoSPI PORTAL)                  ")
        print("=" * 65)
        print(f"Total Document Attachments Registered on Portal: {total_portal_docs:,}")
        print(f"Local Downloaded Sample:                         {total_downloaded:,}")
        print(f"Local Audited Sample:                            {audited_count:,}")
        print(f"Remaining on Portal to Download & Audit:         {total_portal_docs - total_downloaded:,}")

if __name__ == "__main__":
    main()
