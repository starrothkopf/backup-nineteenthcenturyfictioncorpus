import os
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import gc
from huggingface_hub import snapshot_download
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# upload to WashU RIS server, too intensive for local

local_path = Path.home() / "mistral_models" / "7B-Instruct-v0.3"
local_path.mkdir(parents=True, exist_ok=True)

snapshot_download(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    local_dir=local_path,
    token="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" 
)

model = AutoModelForCausalLM.from_pretrained(local_path)
tokenizer = AutoTokenizer.from_pretrained(local_path)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto"
)

# -- paths 
NEG_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_novels"
POS_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_shortstory_collections"

# -- helpers 
def get_file_df(text_dir, label):
    return pd.DataFrame({
        "filepath": [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")],
        "title": [os.path.splitext(f)[0] for f in os.listdir(text_dir) if f.endswith(".txt")],
        "label": label
    })

FEW_SHOT_EXAMPLES = "Classify the following text as either \"novel\" or \"short story collection\". Example 1:\
Text: \"Classics and other stories. A collection of tales, sketches, and scenes. In this book, other stories by the author appear in the contents section.\"\
Label: short story collection\
Example 2:\
Text: \"A selection of stories for children. Notes,  anecdotes, chronicles, episodes, fables, narratives. This collection features several other stories which originally appeared in 'Atalanta,' 'The Cornhill,' 'The Graphic,' respectively.\"\
Label: short story collection\
Example 3:\
Text: \"CONTENTS.\
  I. Euphemia Among The Pelicans\
 II. The Rudder\
III. Pomona\'s Daughter\
 IV. Tucson Jennie\'s Heart\
  V. The Baker of Barnbury\
 VI. The Water Devil\
VII. The Optimist\
VIII. Going Blind\
IX. Betty Stoggs\'s Baby (fairy tale) \
X. Duffy and the Devil\" \
Label: short story collection\
Now classify: \
"
def make_prompt(text):
    return f"{FEW_SHOT_EXAMPLES}\nText: \"{text}\"\nLabel:"

def classify_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
            start_marker = "*** START OF"
            start_idx = full_text.find(start_marker)
            if start_idx != -1:
                content_start = full_text.find("\n", start_idx)
                text = full_text[content_start:].strip()[:1500]
            else:
                text = full_text.strip()[:1500]

            prompt = make_prompt(text)

            result = pipe(prompt, max_new_tokens=10, do_sample=False)[0]["generated_text"]
            # extract the label after the final "Label:" + handle any weird spacing
            label_part = result.split("Label:")[-1].strip().lower()
            if "short" in label_part:
                return "short story collection"
            elif "novel" in label_part:
                return "novel"
            else:
                return "unknown"
        torch.mps.empty_cache()
        gc.collect()

    except Exception as e:
        print(f"error with file {path}: {e}")
        return "unknown"

pos_df = get_file_df(POS_TEXT_DIR, "short story collection")
neg_df = get_file_df(NEG_TEXT_DIR, "novel")

accuracies = []

# -- main loop
for i in range(5):
    print(f"\n-- run {i+1}/5")

    neg_sampled = neg_df.sample(n=len(pos_df), random_state=42 + i)
    balanced_df = pd.concat([neg_sampled, pos_df], ignore_index=True).sample(frac=1, random_state=42 + i)
    train_df, test_df = train_test_split(balanced_df, test_size=0.2, stratify=balanced_df["label"], random_state=42 + i)

    # LLM classify in parallel
    predicted_labels = []
    for path in tqdm(test_df["filepath"], desc="classifying"):
        predicted_labels.append(classify_text(path))

    test_df["predicted_label"] = predicted_labels
    test_df = test_df[test_df["predicted_label"] != "unknown"]

    if test_df.empty:
        print("no valid predictions for this run. skipping classification report.")
        continue

    print(classification_report(
        test_df["label"], 
        test_df["predicted_label"], 
        labels=["novel", "short story collection"],
        digits=3
    ))

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

print(f"\n-- final averaged accuracy over {len(accuracies)} runs")
print(f"average accuracy: {sum(accuracies) / len(accuracies):.2%}")
