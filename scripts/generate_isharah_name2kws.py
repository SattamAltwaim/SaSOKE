import csv
import json
import os

ANNOTATIONS_ROOT = r"R:\SP Datasets\Isharah-500\annotations\SI"

# annotation file -> name2kws json in repo root
SPLITS = {
    "train": ("train.txt", "name2kws_train.json"),
    "val":   ("dev.txt",   "name2kws_val.json"),
    "test":  ("test.txt",  "name2kws_test.json"),
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(gloss: str):
    """Split gloss into individual sign words (keywords)."""
    return [w.strip() for w in gloss.split() if w.strip()]


def main():
    for split, (ann_file, json_file) in SPLITS.items():
        ann_path = os.path.join(ANNOTATIONS_ROOT, ann_file)
        json_path = os.path.join(REPO_ROOT, json_file)

        # Load existing name2kws
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                name2kws = json.load(f)
        else:
            name2kws = {}

        # Read Isharah annotations
        with open(ann_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            rows = list(reader)

        added = 0
        skipped = 0
        for row in rows:
            name = row["id"].strip()
            gloss = row["gloss"].strip()
            if not name or not gloss:
                skipped += 1
                continue
            if name not in name2kws:
                name2kws[name] = extract_keywords(gloss)
                added += 1
            # If already present (re-run safety), leave as-is

        # Save updated file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(name2kws, f, ensure_ascii=False, indent=None)

        print(f"[{split}] {ann_file}: added {added} Isharah entries, "
              f"skipped {skipped} empty rows. Total: {len(name2kws)} entries → {json_file}")


if __name__ == "__main__":
    main()
