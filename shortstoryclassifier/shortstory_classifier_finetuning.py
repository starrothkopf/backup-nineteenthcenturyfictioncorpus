import os
import random
import pandas as pd
from tqdm import tqdm

from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)

POS_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_shortstory_collections"
NEG_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_novels"

MAX_SAMPLES_PER_CLASS = 70   # you can raise or lower this!
MAX_TEXT_LEN = 2000           # truncate long texts


def load_texts(text_dir, label):
    rows = []
    for fname in os.listdir(text_dir):
        if fname.endswith(".txt"):
            fpath = os.path.join(text_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read().strip()[:MAX_TEXT_LEN]
                    if len(text) > 20:
                        rows.append({"text": text, "label": label})
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    return rows

pos_samples = load_texts(POS_TEXT_DIR, 1)
neg_samples = load_texts(NEG_TEXT_DIR, 0)

# balance + shuffle
samples = pos_samples[:MAX_SAMPLES_PER_CLASS] + neg_samples[:MAX_SAMPLES_PER_CLASS]
random.shuffle(samples)

df = pd.DataFrame(samples)
print(f"total samples: {len(df)}")

# -- split, tokenize

dataset = Dataset.from_pandas(df)
dataset = dataset.train_test_split(test_size=0.2)

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# -- model 

model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# -- train 

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    save_strategy="epoch",
    learning_rate=2e-5,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    tokenizer=tokenizer,
)

trainer.train()
trainer.evaluate()

model.save_pretrained("./shortstory_distilbert")
tokenizer.save_pretrained("./shortstory_distilbert")
