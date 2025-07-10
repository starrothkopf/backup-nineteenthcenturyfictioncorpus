import os
import pandas as pd
from tqdm import tqdm
from transformers import pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from concurrent.futures import ThreadPoolExecutor, as_completed

NEG_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_novels"
POS_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_shortstory_collections"

# -- helpers

def get_file_df(text_dir, label):
    return pd.DataFrame({
        "filepath": [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")],
        "title": [os.path.splitext(f)[0] for f in os.listdir(text_dir) if f.endswith(".txt")],
        "label": label
    })

def classify_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
            start_marker = "*** START OF"
            start_idx = full_text.find(start_marker)
            if start_idx != -1:
                content_start = full_text.find("\n", start_idx)
                text = full_text[content_start:]
            else:
                text = full_text
            if len(text) < 10:
                raise ValueError("text too short")
            result = model(text, labels)
            return result["labels"][0]
    except Exception as e:
        print(f"error with file {path}: {e}")
        return "unknown"

pos_df = get_file_df(POS_TEXT_DIR, "short story collection")
neg_df = get_file_df(NEG_TEXT_DIR, "novel")
labels = ["novel", "short story collection"]
model = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli", device=-1)  # CPU only

# ---- main loop: repeat balanced sampling ---- #
accuracies = []

for i in range(5): 
    print(f"\n=== run {i+1}/5 ===")

    neg_sampled = neg_df.sample(n=len(pos_df), random_state=42 + i)
    balanced_df = pd.concat([neg_sampled, pos_df], ignore_index=True).sample(frac=1, random_state=42 + i)
    train_df, test_df = train_test_split(balanced_df, test_size=0.2, stratify=balanced_df["label"], random_state=42 + i)

    # classify with concurrent futures
    with ThreadPoolExecutor(max_workers=7) as executor:  # adjust # of workers based on your CPU
        futures = {executor.submit(classify_text, path): path for path in test_df["filepath"]}
        predicted_labels = []
        for future in tqdm(as_completed(futures), total=len(futures), desc="classifying"):
            predicted_labels.append(future.result())

    test_df["predicted_label"] = predicted_labels
    test_df = test_df[test_df["predicted_label"] != "unknown"]

    correct = (test_df["predicted_label"] == test_df["label"]).sum()
    total = len(test_df)
    acc = correct / total
    accuracies.append(acc)

    print(f"\naccuracy for run {i+1}: {correct}/{total} = {acc:.2%}")
    print(classification_report(test_df["label"], test_df["predicted_label"], digits=3))

    print("\nexamples classified as novels:")
    print(test_df[test_df["predicted_label"] == "novel"]["title"].head(3).to_string(index=False))

    print("\nexamples classified as short story collections:")
    print(test_df[test_df["predicted_label"] == "short story collection"]["title"].head(3).to_string(index=False))


print(f"\n=== final averaged accuracy over {len(accuracies)} runs ===")
print(f"average accuracy: {sum(accuracies) / len(accuracies):.2%}")
