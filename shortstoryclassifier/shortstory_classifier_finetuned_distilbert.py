import os
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
import torch

MODEL_DIR = "./shortstory_distilbert"
POS_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_shortstory_collections"
NEG_TEXT_DIR = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/gutenberg_novels"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load fine-tuned model and tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR).to(device)
model.eval()

# label mapping
id2label = {0: "novel", 1: "short story collection"}

def classify_text(text):
    inputs = tokenizer(text, truncation=True, padding=True, max_length=512, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    pred = torch.argmax(logits, dim=-1).item()
    return id2label.get(pred, "unknown")

# classify
for filename in os.listdir(TEXT_DIR):
    if filename.endswith(".txt"):
        path = os.path.join(TEXT_DIR, filename)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()[:2000]  
        label = classify_text(text)
        print(f"{filename}: {label}")
