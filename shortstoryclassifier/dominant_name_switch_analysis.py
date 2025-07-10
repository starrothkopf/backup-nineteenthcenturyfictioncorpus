from sklearn.metrics import classification_report

import pandas as pd

df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta-backup/shortstoryclassifier/dominant_name_switch_output1.csv")

best_acc = 0
best_threshold = None

for threshold in [x/100 for x in range(50, 101)]:
    df["predicted"] = df["name_switch_ratio"].apply(lambda x: "short story collection" if x > threshold else "novel")
    correct = (df["label"] == df["predicted"]).sum()
    total = len(df)
    acc = correct / total

    # This prints full precision/recall/F1 per threshold:
    report = classification_report(df["label"], df["predicted"], labels=["short story collection", "novel"], digits=3, output_dict=True)
    short_story_recall = report["short story collection"]["recall"]
    short_story_precision = report["short story collection"]["precision"]

    print(f"threshold {threshold:.2f}: acc={acc:.2%} short_story_recall={short_story_recall:.2%} short_story_precision={short_story_precision:.2%}")

    if acc > best_acc:
        best_acc = acc
        best_threshold = threshold

print(f"\nBest overall accuracy: {best_acc:.2%} at threshold {best_threshold:.2f}")
