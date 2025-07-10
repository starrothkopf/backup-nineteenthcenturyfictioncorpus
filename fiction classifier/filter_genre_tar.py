import shutil
from pathlib import Path

vol_ids = set(line.strip() for line in open("corpusbuilding/my_docids.txt"))
source_dir = Path("/Users/starrothkopf/Desktop/HDW/1279201/fiction") 
dest_dir = Path("/Users/starrothkopf/Desktop/HDW/noveltmmeta/genrepredictions")
dest_dir.mkdir(exist_ok=True)

copied = 0
missing = 0

for vol_id in vol_ids:
    json_path = source_dir / f"{vol_id}.json"
    if json_path.exists():
        shutil.copy(json_path, dest_dir / f"{vol_id}.json")
        copied += 1
    else:
        print(f"Missing: {json_path.name}")
        missing += 1

print(f"\nCopied: {copied}")
print(f"Missing: {missing}")
print(f"Total: {copied + missing}")

        
