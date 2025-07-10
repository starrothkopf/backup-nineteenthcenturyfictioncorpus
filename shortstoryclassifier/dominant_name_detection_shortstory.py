import os
import re
from collections import Counter
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

NEG_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta-backup/shortstoryclassifier/gutenberg_novels"
POS_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta-backup/shortstoryclassifier/gutenberg_shortstory_collections"

OUTPUT_CSV = "dominant_name_switch_output1.csv"

STOPWORDS = {"The", "And", "But", "She", "His", "Her", "You", 
                 "Project", "Gutenberg", "Volume", "Chapter", 
                 "Book", "None", "Edition", "License", "Foundation", 
                 "University", "There", "Then", "They", "When", "Its", "Yes"}

COLLECTION_KEYWORDS = [
    "Stories", "Tales", "Sketches", "Novelettes", "Miscellanies",
    "Collected", "Selections", "Anthology", "Scenes", "Anecdotes",
    "Chronicles", "Fables", "Narratives"
]

def get_file_df(text_dir, label):
    return pd.DataFrame({
        "filepath": [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")],
        "title": [os.path.splitext(f)[0] for f in os.listdir(text_dir) if f.endswith(".txt")],
        "label": label
    })

def split_into_sections(text):
    chapter_pattern = re.compile(r'(?i)(^chapter\s+\w+)', re.MULTILINE)
    chapters = chapter_pattern.split(text)
    if len(chapters) > 1:
        sections = []
        for i in range(1, len(chapters), 2):
            sections.append(chapters[i] + chapters[i+1])
        return sections

    caps_pattern = re.compile(r'\n([A-Z][A-Z\s\-]{4,})\n')
    matches = list(caps_pattern.finditer(text))
    if not matches:
        return [text]
    sections = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        section = text[start:end].strip()
        if len(section) > 100:
            sections.append(section)
    return sections if sections else [text]

# === faster than spacy: regex entity names
def get_top_name(text):
    # simple capitalized word extractor
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)

    stopwords = {"The", "And", "But", "She", "His", "Her", "You", 
                 "Project", "Gutenberg", "Volume", "Chapter", 
                 "Book", "None", "Edition", "License", "Foundation", 
                 "University", "There", "Then", "They", "When", "Its", "Yes"}

    words = [w for w in words if w not in stopwords]

    counts = Counter(words)
    return counts.most_common(1)[0][0] if counts else "None"

def get_name_sequence(text):
    sections = split_into_sections(text)
    return [get_top_name(sec) for sec in sections]

def name_change_ratio(sequence):
    if len(sequence) <= 1:
        return 0.0
    return sum(1 for i in range(1, len(sequence)) if sequence[i] != sequence[i-1]) / (len(sequence) - 1)

def classify_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        seq = get_name_sequence(text)
        ratio = name_change_ratio(seq)
        return seq, ratio
    except Exception as e:
        print(f"error with {path}: {e}")
        return [], 0.0

# === run
pos_df = get_file_df(POS_TEXT_DIR, "short story collection")
neg_df = get_file_df(NEG_TEXT_DIR, "novel")
all_df = pd.concat([pos_df, neg_df], ignore_index=True)

results = []

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(classify_file, row["filepath"]): row for _, row in all_df.iterrows()}
    for future in tqdm(as_completed(futures), total=len(futures), desc="processing"):
        row = futures[future]
        seq, ratio = future.result()
        results.append({
            "title": row["title"],
            "label": row["label"],
            "name_sequence": seq,
            "name_switch_ratio": ratio
        })

result_df = pd.DataFrame(results)
print(result_df.groupby("label")["name_switch_ratio"].describe())
result_df.to_csv(OUTPUT_CSV, index=False)
print(f"\nsaved to {OUTPUT_CSV}")
