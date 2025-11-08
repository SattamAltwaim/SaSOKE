# SaSOKE: Saudi Sign Language Production

Fine-tuning SOKE for Saudi Sign Language (Isharah) dataset.

Forked from [SOKE: Signs as Tokens](https://github.com/2000ZRL/SOKE) by Zuo et al. (ICCV 2025)

**Project:** Senior Project I, University of Jeddah  
---

## Quick Start

### 1. Access Colab Notebooks

Open [Google Colab](https://colab.research.google.com)
- File → Open notebook → GitHub
- Enter: `SattamAltwaim/SaSOKE`
- Select notebook to open

### 2. First-Time Setup

Open `notebooks/1_setup_and_data_prep.ipynb`

**In Colab:**
- Runtime → Change runtime type → GPU (T4, V100, or A100)
- Run all cells to install dependencies and download models

**Downloads to Google Drive:**
- SMPL models
- mBART pretrained model
- Tokenizer checkpoint
- Evaluation models

**Time:** ~15-20 minutes

### 3. Upload Your Dataset

Create folder in Google Drive:
```
/MyDrive/SOKE_data/data/Isharah/
```

Upload your dataset with this structure:
```
/MyDrive/SOKE_data/
├── data/
│   └── Isharah/
│       ├── train/
│       │   ├── poses/
│       │   │   └── [sentence_name]/
│       │   │       └── [sentence_name]_[frame]_3D.pkl
│       │   └── re_aligned/
│       │       └── isharah_realigned_train_preprocessed_fps.csv
│       ├── val/
│       │   ├── poses/
│       │   └── re_aligned/
│       └── test/
│           ├── poses/
│           └── re_aligned/
├── deps/                    # Auto-downloaded by setup
├── smpl-x/                  # Auto-downloaded by setup
└── checkpoints/             # Auto-downloaded by setup
```

**CSV Format Required:**
- VIDEO_ID
- VIDEO_NAME
- SENTENCE_ID
- SENTENCE_NAME
- START_REALIGNED
- END_REALIGNED
- SENTENCE
- fps

### 4. Training

#### Option A: Use Pretrained Tokenizer (Recommended)
Open `notebooks/3_train_soke.ipynb` and run all cells

#### Option B: Train Your Own Tokenizer
1. Open `notebooks/2_train_tokenizer.ipynb` and run all cells
2. Then open `notebooks/3_train_soke.ipynb` and run all cells

**Training Time:**
- T4 GPU (Free): ~72 hours
- V100 GPU (Pro): ~36 hours
- A100 GPU (Pro+): ~18 hours

### 5. Inference

Open `notebooks/4_inference.ipynb` and run all cells

**Outputs:**
- Predictions: `results/mgpt/SOKE/test_rank_0/*.pkl`
- Metrics: `results/mgpt/SOKE/test_rank_0/test_scores.json`

---

## Notebooks Overview

### 1. Setup and Data Preparation
**File:** `notebooks/1_setup_and_data_prep.ipynb`  
**Purpose:** Environment setup and model downloads  
**Run:** Once per Colab session  
**Time:** 15-20 minutes

### 2. Train Tokenizer (Optional)
**File:** `notebooks/2_train_tokenizer.ipynb`  
**Purpose:** Train VQ-VAE to discretize sign poses  
**Skip if:** Using pretrained tokenizer  
**Time:** 24-48 hours  
**Output:** `checkpoints/vae/tokenizer.ckpt` in Drive

### 3. Train SOKE Model
**File:** `notebooks/3_train_soke.ipynb`  
**Purpose:** Fine-tune mBART on sign language data  
**Requires:** Tokenizer checkpoint  
**Time:** 36-72 hours  
**Output:** `experiments/mgpt/SOKE/checkpoints/` in Colab

### 4. Inference
**File:** `notebooks/4_inference.ipynb`  
**Purpose:** Generate sign language predictions  
**Requires:** Trained model  
**Time:** 1-4 hours  
**Output:** Predictions and evaluation metrics

---

## GPU Selection

In Colab: **Runtime → Change runtime type → Hardware accelerator → GPU**

**Free Tier (T4 - 16GB VRAM):**
- Batch size: 8
- Training time: ~72 hours
- Good for: Testing and small datasets

**Colab Pro (V100 - 32GB VRAM):**
- Batch size: 16
- Training time: ~36 hours
- Good for: Full training runs

**Colab Pro+ (A100 - 40GB VRAM):**
- Batch size: 32
- Training time: ~18 hours
- Good for: Fast iteration

---

## Configuration

Notebooks auto-configure paths. No manual editing needed.

**Code Location:** `/content/SaSOKE` (cloned from GitHub)  
**Data Location:** `/content/drive/MyDrive/SOKE_data/` (in Drive)

### Adjust Batch Size (if needed)

Edit config cell in training notebooks:
```python
config['TRAIN']['BATCH_SIZE'] = 8  # Change based on GPU memory
```

### Adjust Workers (if slow)

```python
config['TRAIN']['NUM_WORKERS'] = 2  # Reduce if data loading is slow
```

---

## Monitoring Training

### TensorBoard (Built-in)

In training notebook:
```python
%load_ext tensorboard
%tensorboard --logdir experiments/mgpt/SOKE/
```

### Checkpoints

Auto-saved to Drive every few epochs:
- Latest: `experiments/mgpt/SOKE/checkpoints/last.ckpt`
- Best: `experiments/mgpt/SOKE/checkpoints/best.ckpt`

---

## Troubleshooting

### "Runtime disconnected"
- Reconnect and remount Drive
- Training resumes from last checkpoint
- Re-run setup notebook if packages missing

### "Out of memory"
- Reduce batch size in config
- Use smaller GPU or upgrade to Pro
- Reduce NUM_WORKERS to 2

### "File not found"
- Verify Drive structure: `/MyDrive/SOKE_data/`
- Check dataset uploaded correctly
- Run setup notebook to download models

### "Slow data loading"
- Reduce NUM_WORKERS
- Ensure data is in Drive (not Colab local storage)
- Check internet connection

### "Import errors"
- Re-run setup notebook
- Restart runtime: Runtime → Restart runtime
- Check pip install completed without errors

---

## Updating Code

### Pull Latest Changes

In Colab notebook:
```python
!git pull origin main
```

### Make Local Changes

Edit files in Colab, then commit:
```python
!git config --global user.email "your@email.com"
!git config --global user.name "Your Name"
!git add .
!git commit -m "Your changes"
!git push
```

---

## File Structure

```
SaSOKE/
├── mGPT/                    # Core model code
│   ├── archs/              # VQ-VAE and mBART models
│   ├── data/               # Data loading
│   ├── models/             # Model definitions
│   └── metrics/            # Evaluation
├── configs/                 # Configuration files
│   ├── soke.yaml          # Main config
│   ├── deto.yaml          # Tokenizer config
│   └── assets.yaml        # Model paths
├── notebooks/               # Colab notebooks (start here)
│   ├── 1_setup_and_data_prep.ipynb
│   ├── 2_train_tokenizer.ipynb
│   ├── 3_train_soke.ipynb
│   └── 4_inference.ipynb
├── train.py                # Training script
├── test.py                 # Inference script
└── requirements_colab.txt  # Dependencies
```

---

## Architecture

### Stage 1: Tokenizer (DETO)
- 3 VQ-VAE models: body, left hand, right hand
- Discretizes continuous poses into tokens
- Codebook sizes: body=96, hands=192

### Stage 2: Generator (AMG)
- Base: mBART-large-cc25
- Multi-head decoding for simultaneous prediction
- Fine-tuned on sign language token sequences

---

## Evaluation Metrics

**DTW MPJPE PA** (Dynamic Time Warping Mean Per Joint Position Error, Procrustes Aligned)

Separate metrics for:
- Body
- Left hand
- Right hand

Lower values = better performance

---

## Credits

**Original SOKE:** Zuo et al., "Signs as Tokens: A Retrieval-Enhanced Multilingual Sign Language Generator," ICCV 2025

**Isharah Dataset:** Alyami et. al, "Isharah: A Large-Scale Multi-Scene Dataset for Continuous Sign Language Recognition," SDAIA-KFUPM Joint Research Center for Artificial Intelligence

---
