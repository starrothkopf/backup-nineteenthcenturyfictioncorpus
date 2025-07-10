import csv

CSV_IN = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/rich_noveltm_ef_filtered_with_google.csv"

matched = 0
google_digitized = 0

with open(CSV_IN, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        if row["access_profile_code"]:  
            matched += 1
            if row["google_digitized"].strip().lower() in ["true", "1", "yes"]:
                google_digitized += 1

print(f"matched rows with data: {matched}")
print(f"of those, google digitized: {google_digitized}")
print(f"percentage google digitized: {100 * google_digitized / matched:.2f}%")

"""
matched rows with data: 5603
of those, google digitized: 5524
percentage google digitized: 98.59%
"""