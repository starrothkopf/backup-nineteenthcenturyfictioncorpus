import csv

TXT_FILE = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/hathi_full_20250601.txt"
CSV_IN = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/rich_noveltm_ef_filtered.csv"
CSV_OUT = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/rich_noveltm_ef_filtered_with_google.csv"

def clean_docid(s):
    return ''.join(s.lower().split())  # removes all whitespace, including tabs/newlines

# load TXT file to dict: { docid: (access_profile_code, has_google) }
txt_data = {}
with open(TXT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip('\n\r').split('\t')
        if len(parts) < 2:
            continue
        docid = parts[0].strip().lower()
        access_profile_code = parts[1].strip().lower()
        has_google = "google" in line.lower()
        txt_data[docid] = (access_profile_code, has_google)

print(f"Loaded {len(txt_data)} TXT records.")
print("Sample TXT keys:", list(txt_data.keys())[:10])
with open(CSV_IN, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    csv_docids = [row["docid"].strip().strip('"').lower() for row in reader]
print("Sample CSV docids:", csv_docids[:10])
print(f"TXT keys count: {len(txt_data)}")
print(f"CSV docids count: {len(csv_docids)}")


# read CSV, add new columns, write CSV
with open(CSV_IN, "r", encoding="utf-8") as infile, \
     open(CSV_OUT, "w", encoding="utf-8", newline="") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["access_profile_code", "google_digitized"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    found = 0
    total = 0

    for row in reader:
        total += 1
        docid = row["docid"].strip().strip('"').lower()

        if docid in txt_data:
            found += 1
            access_profile_code, has_google = txt_data[docid]
            if found <= 20:  # Only print first 20 matches so you don't get flooded
                print(f"MATCHED: {docid}  →  access_profile_code={access_profile_code}  google_digitized={has_google}")
        else:
            access_profile_code = ""
            has_google = False

        row["access_profile_code"] = access_profile_code
        row["google_digitized"] = has_google

        writer.writerow(row)

print(f"Matched {found} of {total} CSV rows.")
print(f"Output: {CSV_OUT}")
