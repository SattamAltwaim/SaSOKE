"""
Generate word2code entries for the Isharah-500 dataset and merge them into
the existing word2code.json.

Strategy:
  - For each unique gloss word in Isharah, collect all clips that contain it.
  - For each such clip with pre-computed token file, extract the proportional
    segment of tokens corresponding to that word's position in the gloss sequence.
    (e.g. word 2 of 4 → tokens in [T*1/4 : T*2/4]).
  - Resample the extracted segment to exactly MAX_LEN (10) tokens using linspace.
  - Across all clips for a word, take the per-position mode (most common code).
  - Single-word clips are used as-is (full sequence resampled).

Usage (from SOKE root):
    python scripts/generate_isharah_word2code.py
"""

import csv
import json
import os
import numpy as np
from collections import defaultdict
from scipy import stats

# ── Config ─────────────────────────────────────────────────────────────────────
ANNOTATIONS = {
    "train": r"R:\SP Datasets\Isharah-500\annotations\SI\train.txt",
    "val":   r"R:\SP Datasets\Isharah-500\annotations\SI\dev.txt",
    "test":  r"R:\SP Datasets\Isharah-500\annotations\SI\test.txt",
}
TOKEN_DIR   = r"C:\Users\Eyad\Desktop\SOKE\data\How2Sign\TOKENS_h2s_csl_phoenix_isharah\isharah"
WORD2CODE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "word2code.json")
MAX_LEN = 10   # tokens per word (matches max_len_per_part in mgpt_mbart.py)
# ───────────────────────────────────────────────────────────────────────────────


def resample_tokens(tokens: np.ndarray, target_len: int) -> np.ndarray:
    """Resample a (T, 3) token array to (target_len, 3) via nearest-neighbour."""
    T = tokens.shape[0]
    if T == 0:
        return None
    if T == target_len:
        return tokens
    idx = np.round(np.linspace(0, T - 1, target_len)).astype(int)
    return tokens[idx]


def load_token_file(clip_id: str):
    """Return (T, 3) int64 array or None if file is missing/invalid."""
    path = os.path.join(TOKEN_DIR, f"{clip_id}.npy")
    if not os.path.exists(path):
        return None
    arr = np.load(path)          # (1, T, 3)
    if arr.ndim == 3:
        arr = arr[0]             # (T, 3)
    if arr.shape[0] < 1:
        return None
    return arr.astype(np.int64)


def extract_word_tokens(full_tokens: np.ndarray, word_idx: int, num_words: int) -> np.ndarray:
    """Extract the proportional segment for word at position word_idx out of num_words."""
    T = full_tokens.shape[0]
    start = int(round(T * word_idx / num_words))
    end   = int(round(T * (word_idx + 1) / num_words))
    end   = max(start + 1, end)   # ensure at least 1 frame
    return full_tokens[start:end]


def tokens_to_entry(resampled: np.ndarray) -> dict:
    """Convert (MAX_LEN, 3) array → {"body": [...], "lhand": [...], "rhand": [...]}."""
    return {
        "body":   resampled[:, 0].tolist(),
        "lhand":  resampled[:, 1].tolist(),
        "rhand":  resampled[:, 2].tolist(),
    }


def mode_tokens(samples: list) -> np.ndarray:
    """Given a list of (MAX_LEN, 3) arrays, return per-position mode."""
    stack = np.stack(samples, axis=0)   # (N, MAX_LEN, 3)
    result = np.zeros((MAX_LEN, 3), dtype=np.int64)
    for t in range(MAX_LEN):
        for c in range(3):
            col = stack[:, t, c]
            result[t, c] = int(stats.mode(col, keepdims=False).mode)
    return result


def main():
    # ── Collect clips per word ──────────────────────────────────────────────
    word_clips = defaultdict(list)   # word -> [(clip_id, word_idx, num_words)]

    for split, ann_path in ANNOTATIONS.items():
        with open(ann_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            for row in reader:
                clip_id = row["id"].strip()
                words = [w.strip() for w in row["gloss"].split() if w.strip()]
                num_words = len(words)
                for idx, word in enumerate(words):
                    word_clips[word].append((clip_id, idx, num_words))

    print(f"Unique Isharah gloss words: {len(word_clips)}")

    # ── Build word → resampled token samples ───────────────────────────────
    word_samples = defaultdict(list)   # word -> list of (MAX_LEN, 3) arrays
    missing_files = 0
    processed_clips = set()

    for word, clips in word_clips.items():
        for clip_id, word_idx, num_words in clips:
            if (clip_id, word_idx) in processed_clips:
                continue
            processed_clips.add((clip_id, word_idx))

            full_tokens = load_token_file(clip_id)
            if full_tokens is None:
                missing_files += 1
                continue

            segment = extract_word_tokens(full_tokens, word_idx, num_words)
            resampled = resample_tokens(segment, MAX_LEN)
            if resampled is not None:
                word_samples[word].append(resampled)

    print(f"Token files missing: {missing_files}")
    print(f"Words with at least one token sample: {len(word_samples)}")

    # ── Aggregate to one entry per word (mode across clips) ─────────────────
    new_entries = {}
    for word, samples in word_samples.items():
        if len(samples) == 1:
            aggregated = samples[0]
        else:
            aggregated = mode_tokens(samples)
        new_entries[word] = tokens_to_entry(aggregated)

    # ── Merge into existing word2code.json ──────────────────────────────────
    if os.path.exists(WORD2CODE_PATH):
        with open(WORD2CODE_PATH, "r", encoding="utf-8") as f:
            word2code = json.load(f)
    else:
        word2code = {}

    before = len(word2code)
    for word, entry in new_entries.items():
        if word not in word2code:   # don't overwrite existing entries
            word2code[word] = entry

    with open(WORD2CODE_PATH, "w", encoding="utf-8") as f:
        json.dump(word2code, f, ensure_ascii=False)

    after = len(word2code)
    print(f"word2code.json: {before} → {after} entries (+{after - before} Isharah words)")


if __name__ == "__main__":
    main()
