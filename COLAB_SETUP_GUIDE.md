# SOKE Google Colab Setup Guide

## Directory Structure for Google Drive

Upload the entire SOKE folder to Google Drive at: `/MyDrive/SOKE/`

Required structure:
```
MyDrive/SOKE/
├── mGPT/                    # Core model code
├── configs/                 # Configuration files
├── prepare/                 # Setup scripts
├── scripts/                 # Helper scripts  
├── notebooks/               # Colab notebooks (new)
├── data/                    # Your datasets
│   ├── How2Sign/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   ├── CSL-Daily/          # Optional
│   └── Phoenix-2014T/      # Optional
├── deps/                    # Downloaded dependencies
│   ├── smpl_models/
│   ├── t2m/
│   └── mbart-h2s-csl-phoenix/
├── smpl-x/
│   ├── mean.pt
│   └── std.pt
├── checkpoints/
│   └── vae/
│       └── tokenizer.ckpt
├── train.py
├── test.py
├── requirements.txt
└── README.md
```

## Notebook Execution Order

### 1. Setup (Required, run once)
`1_setup_and_data_prep.ipynb`
- Installs dependencies
- Downloads pretrained models
- Downloads SMPL models and evaluators
- Verifies setup

### 2. Train Tokenizer (Stage 1)
`2_train_tokenizer.ipynb`
- Trains VQ-VAE tokenizer
- Saves checkpoint to `checkpoints/vae/tokenizer.ckpt`
- Skip if using pretrained tokenizer

### 3. Train SOKE (Stage 2)
`3_train_soke.ipynb`
- Trains multilingual sign language generator
- Requires trained tokenizer
- Saves checkpoints to `experiments/mgpt/SOKE/checkpoints/`

### 4. Inference
`4_inference.ipynb`
- Runs inference on test data
- Generates predictions and metrics
- Saves results to `results/mgpt/SOKE/test_rank_0/`

## Dataset Preparation

### How2Sign
Required files in `data/How2Sign/`:
- `train/poses/` - SMPL-X pose files (.pkl)
- `train/re_aligned/how2sign_realigned_train_preprocessed_fps.csv`
- `val/poses/`
- `val/re_aligned/how2sign_realigned_val_preprocessed_fps.csv`
- `test/poses/`
- `test/re_aligned/how2sign_realigned_test_preprocessed_fps.csv`

Ensure poses directory contains subdirectories named by sentence ID with frame files.

## GPU Requirements

### Tokenizer Training
- Minimum: 1x T4 GPU (16GB)
- Recommended: 1x V100 or A100

### SOKE Training  
- Minimum: 1x T4 GPU (16GB) with batch_size=8
- Recommended: 1x V100 (32GB) with batch_size=16
- Optimal: 4x V100 or 2x A100 with batch_size=32

Adjust `TRAIN.BATCH_SIZE` in configs based on available GPU memory.

## Training Times (Approximate)

### Tokenizer (150 epochs)
- T4: ~48 hours
- V100: ~24 hours
- A100: ~12 hours

### SOKE Model (150 epochs)
- T4: ~72 hours
- V100: ~36 hours
- A100: ~18 hours

## Common Issues

### Out of Memory
- Reduce `TRAIN.BATCH_SIZE` in config
- Reduce `TRAIN.NUM_WORKERS` to 2
- Use gradient accumulation

### File Not Found Errors
- Verify all paths in config use absolute paths
- Check Google Drive mount is successful
- Ensure dataset structure matches expected format

### Slow Data Loading
- Reduce `TRAIN.NUM_WORKERS` to 2 or 4
- Check dataset is on Drive, not Colab local storage
- Enable high-RAM runtime if needed

## Monitoring Training

### TensorBoard
```python
%load_ext tensorboard
%tensorboard --logdir experiments/mgpt/SOKE/
```

### Weights & Biases (Optional)
Set `LOGGER.WANDB` in config to enable W&B logging.

## Checkpointing

Checkpoints saved automatically to:
- Tokenizer: `experiments/mgpt/DETO/checkpoints/`
- SOKE: `experiments/mgpt/SOKE/checkpoints/`

Best model: `best.ckpt`
Latest model: `last.ckpt`

## Code Modifications for Colab

Applied automatically in notebooks:
- Fixed PyTorch 2.6+ weights_only loading
- Fixed distributed training checks
- Adjusted paths for Colab environment
- Updated configs for CUDA GPUs

