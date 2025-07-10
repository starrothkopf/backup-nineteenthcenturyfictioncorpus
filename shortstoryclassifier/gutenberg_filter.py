import csv

input_csv = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/gutenberg_fiction_metadata.csv"
output_csv = "gutenberg_fiction_british_irish_filtered.csv"


def is_british_irish(row):
    bookshelves = row.get("bookshelves", "").lower()
    subjects = row.get("subjects", "").lower()

    # include if these keywords appear
    include_keywords = [
        "british", "england", "england -- fiction", "ireland", 
        "irish", "scotland", "uk", "united kingdom",
        "english", "scottish"
    ]
    
    # exclude if these keywords appear
    exclude_keywords = [
        "american", "american","united states", "usa", "us",
        "canada", "australia", "new zealand",
        "india", "south africa", "mexico",
        "china", "japan", "russia", "germany",
        "france", "italy", "spain", "brazil"
    ]

    if any(kw in bookshelves or kw in subjects for kw in include_keywords):
        if not any(kw in bookshelves or kw in subjects for kw in exclude_keywords):
            return True
    return False

with open(input_csv, newline="", encoding="utf-8") as infile, \
     open(output_csv, "w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    count_included = 0
    count_total = 0

    for row in reader:
        count_total += 1
        if is_british_irish(row):
            writer.writerow(row)
            count_included += 1

print(f"filtered {count_included} British/Irish works out of {count_total} total.")
print(f"output saved to {output_csv}")
