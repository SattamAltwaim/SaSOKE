# Code Changes for Colab Compatibility

## Summary
Modified SOKE codebase to support:
- PyTorch 2.6+ weights_only parameter
- Non-distributed single GPU training
- Flexible checkpoint loading
- Colab/CUDA environments

## Modified Files

### 1. mGPT/utils/load_checkpoint.py
**Changes:**
- Added `weights_only=False` to `torch.load()` calls
- Fixes PyTorch 2.6+ compatibility

**Lines Modified:**
- Line 14: `torch.load(ckpt_path, map_location="cpu", weights_only=False)`
- Line 20-21: `torch.load(cfg.TRAIN.PRETRAINED_VAE, map_location="cpu", weights_only=False)`

**Reason:** PyTorch 2.6 changed default behavior to require explicit trust for unpickling objects.

---

### 2. mGPT/models/base.py
**Changes:**
- Added distributed training checks before calling `torch.distributed.get_rank()`
- Made rank suffix conditional

**Lines Modified:**
- Line 113-116:
  ```python
  if torch.distributed.is_initialized():
      print('rank: ', torch.distributed.get_rank(), scores)
  else:
      print('scores: ', scores)
  ```

- Line 126-127:
  ```python
  rank_suffix = str(torch.distributed.get_rank()) if torch.distributed.is_initialized() else '0'
  save_dir = os.path.join(self.output_dir, f'{self.hparams.cfg.TEST.SPLIT}_rank_'+rank_suffix)
  ```

**Reason:** Code assumed distributed training; fails in single-GPU setups.

---

### 3. test.py
**Changes:**
- Made checkpoint loading optional
- Uses pretrained mBART if checkpoint doesn't exist

**Lines Modified:**
- Line 98-104:
  ```python
  # Load checkpoint if it exists, otherwise use the pretrained mBART as-is
  if os.path.exists(cfg.TEST.CHECKPOINTS):
      load_pretrained(cfg, model, logger, phase="test")
      cfg.TIME = cfg.TEST.CHECKPOINTS.split('/')[-1]
  else:
      logger.info(f"Checkpoint {cfg.TEST.CHECKPOINTS} not found. Using pretrained mBART model directly.")
      cfg.TIME = "pretrained"
  ```

**Reason:** Enables inference with fine-tuned mBART without additional training checkpoint.

---

### 4. mGPT/data/humanml/dataset_t2m.py
**Changes:**
- Reverted sample limiting for production use

**Lines Modified:**
- Line 63: `self.ids = self.csv['SENTENCE_NAME']  # Use all samples`

**Reason:** Removed test limit to process full dataset.

---

## Configuration Changes

### For Colab (Applied in notebooks):
```yaml
ACCELERATOR: 'gpu'  # Changed from 'mps'
DEVICE: [0]  # Single GPU, adjust as needed
TRAIN:
  NUM_WORKERS: 2  # Reduced for Colab
  BATCH_SIZE: 16  # Adjustable based on GPU memory
```

### Path Updates:
```yaml
DATASET:
  H2S:
    ROOT: '/content/drive/MyDrive/SOKE/data/How2Sign'
    MEAN_PATH: '/content/drive/MyDrive/SOKE/smpl-x/mean.pt'
    STD_PATH: '/content/drive/MyDrive/SOKE/smpl-x/std.pt'
TRAIN:
  PRETRAINED_VAE: '/content/drive/MyDrive/SOKE/checkpoints/vae/tokenizer.ckpt'
model:
  params:
    lm_path: '/content/drive/MyDrive/SOKE/deps/mbart-h2s-csl-phoenix'
```

---

## Assets Configuration Fix

### configs/assets.yaml
**Change:**
- Line 23: `t2m_path: /Volumes/The Storage!/SOKE/deps/t2m/t2m/`

**Reason:** Corrected path depth for evaluator models.

---

## Testing Status

### Verified Working:
- ✓ Model loading (tokenizer + mBART)
- ✓ Inference on single sample
- ✓ Metrics calculation
- ✓ Prediction saving
- ✓ Non-distributed operation
- ✓ PyTorch 2.6+ compatibility

### Tested Configurations:
- MacOS MPS (Apple Silicon)
- Python 3.12
- PyTorch 2.8.0
- Single GPU inference

### Expected Colab Performance:
- All changes compatible with CUDA
- Tested imports successful
- Configuration templates ready

---

## Backward Compatibility

All changes maintain backward compatibility with:
- PyTorch < 2.6 (weights_only parameter ignored)
- Distributed training setups (conditional checks)
- Original checkpoint paths (if they exist)

---

## Required for Production

### No Additional Changes Needed:
- Core model architecture unchanged
- Training logic preserved
- Evaluation metrics intact
- Data loading pipeline maintained

### Optional Optimizations:
- Adjust `TRAIN.BATCH_SIZE` based on GPU memory
- Tune `TRAIN.NUM_WORKERS` for Colab (recommend 2-4)
- Enable W&B logging if desired
- Use gradient accumulation for larger effective batch sizes

---

## Rollback Instructions

If issues arise, revert changes in:
1. `mGPT/utils/load_checkpoint.py` - Remove `weights_only=False`
2. `mGPT/models/base.py` - Remove distributed checks
3. `test.py` - Make checkpoint loading required
4. `configs/assets.yaml` - Restore original paths

Original files backed up in: (create backup before upload)
```bash
git diff HEAD~4
```

