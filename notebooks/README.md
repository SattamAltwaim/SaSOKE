# SOKE Colab Notebooks

Plug-and-play notebooks for training SOKE on Google Colab with CUDA GPUs.

## Quick Start

1. Upload SOKE folder to Google Drive: `/MyDrive/SOKE/`
2. Open `1_setup_and_data_prep.ipynb` in Colab
3. Run all cells in order
4. Proceed to training notebooks

## Notebooks

### 1_setup_and_data_prep.ipynb
**Purpose:** Environment setup and model downloads
**Runtime:** 10-15 minutes
**GPU Required:** No

**Steps:**
- Mounts Google Drive
- Installs Python dependencies
- Downloads SMPL models
- Downloads t2m evaluators
- Downloads mBART pretrained model
- Verifies setup

**Run Once:** Yes (per new Colab session if runtime disconnects)

---

### 2_train_tokenizer.ipynb
**Purpose:** Train VQ-VAE tokenizer (Stage 1)
**Runtime:** 24-48 hours (150 epochs)
**GPU Required:** Yes (T4 minimum, V100 recommended)

**Steps:**
- Configures paths for Colab
- Trains body, left hand, right hand tokenizers
- Saves checkpoint to `checkpoints/vae/tokenizer.ckpt`

**Skip If:** Using pretrained tokenizer (downloaded in setup)

**Output:** `checkpoints/vae/tokenizer.ckpt`

---

### 3_train_soke.ipynb
**Purpose:** Train multilingual sign generator (Stage 2)
**Runtime:** 36-72 hours (150 epochs)
**GPU Required:** Yes (T4 minimum, V100 recommended)

**Prerequisites:**
- Trained or pretrained tokenizer exists
- mBART model downloaded
- Training data in Drive

**Steps:**
- Loads tokenizer checkpoint
- Initializes mBART with sign tokens
- Trains on text-to-sign pairs
- Saves checkpoints to `experiments/mgpt/SOKE/checkpoints/`

**Output:** `experiments/mgpt/SOKE/checkpoints/last.ckpt`

---

### 4_inference.ipynb
**Purpose:** Generate predictions on test data
**Runtime:** 1-4 hours (depends on test set size)
**GPU Required:** Yes (any GPU)

**Prerequisites:**
- Trained SOKE model checkpoint
- Test data in Drive

**Steps:**
- Loads trained model
- Runs inference on test set
- Calculates evaluation metrics
- Saves predictions

**Output:**
- Predictions: `results/mgpt/SOKE/test_rank_0/*.pkl`
- Metrics: `results/mgpt/SOKE/test_rank_0/test_scores.json`

---

## GPU Selection

### In Colab Menu
Runtime → Change runtime type → Hardware accelerator → GPU

### Recommended GPUs
- **T4:** Free tier, 16GB VRAM, slower training
- **V100:** Colab Pro, 32GB VRAM, 2x faster
- **A100:** Colab Pro+, 40GB VRAM, 4x faster

### Batch Size Guidelines
- T4: batch_size=8
- V100: batch_size=16
- A100: batch_size=32

---

## Monitoring

### TensorBoard (Built-in)
```python
%load_ext tensorboard
%tensorboard --logdir experiments/mgpt/SOKE/
```

### Weights & Biases (Optional)
Set in config:
```yaml
LOGGER:
  WANDB: True
  PROJECT: "soke-training"
```

---

## Troubleshooting

### Runtime Disconnected
- Reconnect and remount Drive
- Training resumes from last checkpoint automatically
- Re-run setup notebook if packages missing

### Out of Memory
- Reduce batch size in notebook config cell
- Reduce `NUM_WORKERS` to 2
- Use smaller GPU or Colab Pro

### Slow Training
- Check GPU is enabled (Runtime menu)
- Reduce data loading workers
- Ensure data is in Drive, not local Colab storage

### Import Errors
- Re-run setup notebook
- Restart runtime: Runtime → Restart runtime
- Check pip install completed without errors

### File Not Found
- Verify Drive mount: `!ls /content/drive/MyDrive/SOKE/`
- Check paths in config cells (case-sensitive)
- Ensure all files uploaded per UPLOAD_CHECKLIST.md

---

## Saving Work

### Checkpoints
Automatically saved to Drive every few epochs:
- `experiments/mgpt/*/checkpoints/last.ckpt`
- `experiments/mgpt/*/checkpoints/best.ckpt`

### Logs
- TensorBoard logs: `experiments/mgpt/*/`
- Training logs: `results/mgpt/*/`

### Download Results
Right-click file in Colab file browser → Download
Or use:
```python
from google.colab import files
files.download('results/mgpt/SOKE/test_rank_0/test_scores.json')
```

---

## Best Practices

### Long Training Sessions
- Use Colab Pro for longer runtimes
- Check runtime type limits (T4: 12hr, V100: 24hr)
- Split training into multiple sessions if needed

### Cost Optimization
- Use free T4 for testing/debugging
- Switch to V100/A100 for production training
- Close notebooks when not in use

### Data Management
- Keep datasets in Drive
- Delete old experiment checkpoints
- Compress large result files

---

## Next Steps

After training:
1. Run inference notebook
2. Download predictions
3. Visualize results (see main README.md)
4. Fine-tune on additional data if needed

## Support

- Check COLAB_SETUP_GUIDE.md for detailed instructions
- Review CODE_CHANGES_LOG.md for technical details
- See main README.md for project documentation

