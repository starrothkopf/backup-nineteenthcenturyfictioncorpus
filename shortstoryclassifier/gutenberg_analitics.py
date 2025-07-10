import csv
from collections import Counter

input_csv = "gutenberg_short_stories_metadata.csv"

subjects_counter = Counter()
bookshelves_counter = Counter()

with open(input_csv, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        subjects = row.get("subjects", "")
        bookshelves = row.get("bookshelves", "")

        for subj in subjects.split(";"):
            subj = subj.strip().lower()
            if subj:
                subjects_counter[subj] += 1

        for shelf in bookshelves.split(";"):
            shelf = shelf.strip().lower()
            if shelf:
                bookshelves_counter[shelf] += 1

print("Top 20 Subjects:")
for subj, count in subjects_counter.most_common(20):
    print(f"{subj}: {count}")

print("\nTop 20 Bookshelves:")
for shelf, count in bookshelves_counter.most_common(20):
    print(f"{shelf}: {count}")
