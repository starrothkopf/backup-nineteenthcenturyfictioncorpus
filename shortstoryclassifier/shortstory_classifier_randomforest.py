import os
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

NEG_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_novels"
POS_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_shortstory_collections"

# -- helpers

def get_file_df(text_dir, label):
    return pd.DataFrame({
        "filepath": [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")],
        "title": [os.path.splitext(f)[0] for f in os.listdir(text_dir) if f.endswith(".txt")],
        "label": label
    })

def read_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
            start_marker = "*** START OF"
            start_idx = full_text.find(start_marker)
            if start_idx != -1:
                content_start = full_text.find("\n", start_idx)
                text = full_text[content_start:].strip()
            else:
                text = full_text.strip()
            return text[:4000]  # first 4000 chars
    except Exception as e:
        print(f"error with file {filepath}: {e}")
        return None

# -- load and combine all data

pos_df = get_file_df(POS_TEXT_DIR, "short story collection")
neg_df = get_file_df(NEG_TEXT_DIR, "novel")
all_files_df = pd.concat([pos_df, neg_df], ignore_index=True)

texts = []
labels = []
titles = []
paths = []

for row in tqdm(all_files_df.itertuples(), total=len(all_files_df), desc="reading files"):
    text = read_text(row.filepath)
    if text and len(text) > 100:
        texts.append(text)
        labels.append(row.label)
        titles.append(row.title)
        paths.append(row.filepath)

full_df = pd.DataFrame({
    "text": texts,
    "label": labels,
    "title": titles,
    "filepath": paths
})

# -- k-fold sampling

accuracies = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for i, (train_idx, test_idx) in enumerate(skf.split(full_df["text"], full_df["label"])): 
    print(f"\n=== run {i+1}/5 ===")

    pos_sampled_df = full_df[full_df["label"] == "short story collection"]
    neg_sampled_df = full_df[full_df["label"] == "novel"].sample(n=len(pos_sampled_df), random_state=42 + i)
    balanced_df = pd.concat([neg_sampled_df, pos_sampled_df], ignore_index=True).sample(frac=1, random_state=42 + i)

    texts = balanced_df["text"].tolist()
    labels = balanced_df["label"].tolist()
    titles = balanced_df["title"].tolist()
    paths = balanced_df["filepath"].tolist()
    
    X_train, X_test, y_train, y_test, title_train, title_test, path_train, path_test = train_test_split(
    texts, labels, titles, paths,
    test_size=0.2, stratify=labels, random_state=42 + i
    )

    # pipeline: TFIDF + logistic regression
    clf = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), max_features=10000),  # optional: tweak features
        RandomForestClassifier(n_estimators=100, random_state=42)
    )

    clf.fit(X_train, y_train)

    # see important features
    vectorizer = clf.named_steps["tfidfvectorizer"]
    rf_model = clf.named_steps["randomforestclassifier"]
    feature_names = vectorizer.get_feature_names_out()
    importances = rf_model.feature_importances_
    top_features = sorted(zip(importances, feature_names), reverse=True)[:20]
    print("\ntop 20 most important features:")
    for score, name in top_features:
        print(f"{name:<25} {score:.5f}")


    y_pred = clf.predict(X_test)
    acc = sum(y_pred == y_test) / len(y_test)
    accuracies.append(acc)

    print(f"accuracy for run {i+1}: {acc:.2%}")
    print(classification_report(y_test, y_pred, digits=3))

    # show some example titles
    print("\nexamples classified as novels:")
    for title, pred in zip(title_test, y_pred):
        if pred == "novel":
            print("  ", title)
            if sum(p == "novel" for p in y_pred) >= 3:
                break

    print("\nexamples classified as short story collections:")
    for title, pred in zip(title_test, y_pred):
        if pred == "short story collection":
            print("  ", title)
            if sum(p == "short story collection" for p in y_pred) >= 3:
                break

# -- final summary
print(f"\n=== final averaged accuracy over {len(accuracies)} runs ===")
print(f"average accuracy: {sum(accuracies) / len(accuracies):.2%}")
