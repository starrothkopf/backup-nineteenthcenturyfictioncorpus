import os
import re
import random
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score
from tqdm import trange, tqdm
from joblib import Parallel, delayed

FIRST_PERSON = re.compile(r"\b(i|me|my|mine|we|us|our|ours)\b", re.I)
THIRD_PERSON = re.compile(r"\b(he|him|his|she|her|hers|they|them|their|theirs)\b", re.I)

FIRST_PERSON_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta-backup/perspectiveclassifier/1st_person"
THIRD_PERSON_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta-backup/perspectiveclassifier/3rd_person"

MAX_WORDS = 10000  # limit to first X words for speed
NUM_RUNS = 10  # stabilizer

DOUBLE_QUOTE_PATTERN = re.compile(r'"((?:.|\n)*?)(?:"|\n\s*\n)', flags=re.DOTALL)
SINGLE_QUOTE_PATTERN = re.compile(r"'((?:.|\n)*?)(?:'|\n\s*\n)", flags=re.DOTALL)

WORD_PATTERN = re.compile(r"\b\w+\b")

# dialogue detection
def normalize_quotes(text):
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    return text

def detect_quote_style(text):
    single_count = text.count("'")
    double_count = text.count('"')
    return "single" if single_count > double_count else "double"

def extract_and_remove_double_quoted_dialogue(text):
    dialogues = DOUBLE_QUOTE_PATTERN.findall(text)
    cleaned_text = DOUBLE_QUOTE_PATTERN.sub(' ', text)
    return dialogues, cleaned_text

def extract_and_remove_single_quoted_dialogue(text):
    dialogues = SINGLE_QUOTE_PATTERN.findall(text)
    cleaned_text = SINGLE_QUOTE_PATTERN.sub(' ', text)
    return dialogues, cleaned_text

def extract_dialogue(text):
    text = normalize_quotes(text)
    style = detect_quote_style(text)
    if style == "double":
        dialogues, cleaned = extract_and_remove_double_quoted_dialogue(text)
    else:
        dialogues, cleaned = extract_and_remove_single_quoted_dialogue(text)

    dialogue_text = " ".join(dialogues)
    narration_text = cleaned
    return dialogue_text, narration_text

def count_features(text):
    dialogue_text, narration_text = extract_dialogue(text)

    total_words = len(WORD_PATTERN.findall(text))
    dialogue_words = len(WORD_PATTERN.findall(dialogue_text))
    narration_words = len(WORD_PATTERN.findall(narration_text))

    tw = max(total_words, 1)
    dw = max(dialogue_words, 1)
    nw = max(narration_words, 1)

    fp_total = len(FIRST_PERSON.findall(text))
    tp_total = len(THIRD_PERSON.findall(text))
    fp_dialogue = len(FIRST_PERSON.findall(dialogue_text))
    tp_dialogue = len(THIRD_PERSON.findall(dialogue_text))
    fp_narration = len(FIRST_PERSON.findall(narration_text))
    tp_narration = len(THIRD_PERSON.findall(narration_text))

    features = [
        fp_total / tw,
        tp_total / tw,
        fp_dialogue / dw,
        tp_dialogue / dw,
        fp_narration / nw,
        tp_narration / nw,
        tp_total / (fp_total + 1),
        tp_dialogue / (fp_dialogue + 1),
        tp_narration / (fp_narration + 1),
        dialogue_words / tw
    ]
    
    return features

def load_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:MAX_WORDS]
    except Exception as e:
        print(f"Error loading {os.path.basename(path)}: {e}")
        return None

def process_text(text, label):
    try:
        print(f"Processing text with label={label} len={len(text) if text else 'None'}", flush=True)
        if text is None:
            return None
        features = count_features(text)
        print(f"Processed features for label={label}", flush=True)
        return (features, label)
    except Exception as e:
        print(f"Error in processing text with label={label}: {e}", flush=True)
        return None


def load_dir_texts(directory):
    paths = [
        os.path.join(directory, fname)
        for fname in os.listdir(directory)
        if fname.endswith(".txt")
    ]
    texts = Parallel(n_jobs=-1)(delayed(load_text)(p) for p in tqdm(paths, desc=f"Loading texts from {directory}"))
    return list(zip(texts, [directory]*len(texts)))

def process_texts_parallel(texts_and_labels):
    results = Parallel(n_jobs=-1)(
        delayed(process_text)(text, 0 if FIRST_PERSON_DIR in label else 1)
        for text, label in tqdm(texts_and_labels, desc="Processing texts")
    )
    return [r for r in results if r is not None]

# usage:
fp_texts = [(text, FIRST_PERSON_DIR) for text in Parallel(n_jobs=-1)(delayed(load_text)(p) for p in tqdm(
    [os.path.join(FIRST_PERSON_DIR, f) for f in os.listdir(FIRST_PERSON_DIR) if f.endswith(".txt")],
    desc="Loading 1st person texts"))]

tp_texts = [(text, THIRD_PERSON_DIR) for text in Parallel(n_jobs=-1)(delayed(load_text)(p) for p in tqdm(
    [os.path.join(THIRD_PERSON_DIR, f) for f in os.listdir(THIRD_PERSON_DIR) if f.endswith(".txt")],
    desc="Loading 3rd person texts"))]

# Then process all texts in parallel
fp_data = process_texts_parallel(fp_texts)
tp_data = process_texts_parallel(tp_texts)


print(f"loaded {len(fp_data)} first-person files, {len(tp_data)} third-person files", flush=True)

min_len = min(len(fp_data), len(tp_data))
print(f"Balancing data to size {min_len} per class")
fp_data = random.sample(fp_data, min_len)
tp_data = random.sample(tp_data, min_len)

print("Shuffling data")
data = fp_data + tp_data
random.shuffle(data)

X = np.array([x[0] for x in data])
y = np.array([x[1] for x in data])

point_metrics = []
NUM_RUNS = 10

# models
rf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
lr = LogisticRegression(max_iter=1000)

# cv once
print("Starting cross-validation")
cv_rf_score = np.mean(cross_val_score(rf, X, y, cv=5))
cv_lr_score = np.mean(cross_val_score(lr, X, y, cv=5))

# loop for split evaluation
for i in trange(NUM_RUNS):
    print(f"\nrun {i + 1} of {NUM_RUNS}")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=random.randint(0, 99999)
    )

    model = rf  # or lr
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average=None, labels=[0, 1]
    )

    point_metrics.append([precision, recall, f1])

point_metrics = np.array(point_metrics)
avg_precision = np.mean(point_metrics[:, 0], axis=0)
avg_recall = np.mean(point_metrics[:, 1], axis=0)
avg_f1 = np.mean(point_metrics[:, 2], axis=0)

print(f"\naveraged over {NUM_RUNS} runs")
print("class: NOT third-person")
print(f"  precision: {avg_precision[0]:.3f}")
print(f"  recall:    {avg_recall[0]:.3f}")
print(f"  f1-score:  {avg_f1[0]:.3f}")

print("class: third-person")
print(f"  precision: {avg_precision[1]:.3f}")
print(f"  recall:    {avg_recall[1]:.3f}")
print(f"  f1-score:  {avg_f1[1]:.3f}")

print("\nmacro avg F1:", np.mean(avg_f1))
print("\navg RF CV accuracy:", cv_rf_score)
print("avg LR CV accuracy:", cv_lr_score)