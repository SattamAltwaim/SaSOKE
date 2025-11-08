# Google Drive Upload Checklist

## Files to Upload

### Core Code (Required)
- [ ] `mGPT/` - Entire directory with all subdirectories
- [ ] `configs/` - All configuration files
- [ ] `prepare/` - Setup scripts
- [ ] `scripts/` - Helper scripts
- [ ] `train.py` - Training script
- [ ] `test.py` - Inference script
- [ ] `requirements_colab.txt` - Dependencies

### Notebooks (Required)
- [ ] `notebooks/1_setup_and_data_prep.ipynb`
- [ ] `notebooks/2_train_tokenizer.ipynb`
- [ ] `notebooks/3_train_soke.ipynb`
- [ ] `notebooks/4_inference.ipynb`

### Documentation
- [ ] `README.md` - Project documentation
- [ ] `COLAB_SETUP_GUIDE.md` - Colab-specific instructions
- [ ] `UPLOAD_CHECKLIST.md` - This file

### Data (Upload separately to data/)
- [ ] How2Sign dataset with poses and CSV files
- [ ] CSL-Daily (optional)
- [ ] Phoenix-2014T (optional)

### Models (Will be downloaded by notebooks)
- Downloads handled automatically by setup notebook
- Manual upload optional if slow download:
  - `deps/smpl_models/`
  - `deps/t2m/`
  - `deps/mbart-h2s-csl-phoenix/`
  - `smpl-x/mean.pt` and `std.pt`
  - `checkpoints/vae/tokenizer.ckpt` (if using pretrained)

## Upload Structure

Create in Google Drive:
```
/MyDrive/SOKE/
```

Upload order:
1. Core code (mGPT/, configs/, scripts/, prepare/)
2. Python scripts (train.py, test.py)
3. Notebooks (notebooks/)
4. Documentation (*.md files)
5. Data (data/)
6. Dependencies (optional, can be downloaded)

## Verification Steps

After upload, verify in Colab:
```python
import os
os.chdir('/content/drive/MyDrive/SOKE')
!ls -la
```

Check key files exist:
- `train.py`
- `test.py`
- `mGPT/models/mgpt.py`
- `configs/soke.yaml`
- `notebooks/` directory with 4 notebooks

## Size Estimates

- Core code: ~50 MB
- Notebooks: ~1 MB
- Documentation: <1 MB
- Data (How2Sign test): ~2-5 GB
- Data (How2Sign full): ~50-100 GB
- Dependencies: ~5 GB (if manually uploaded)

Total minimum (code only): ~50 MB
Total with data and deps: ~60-110 GB

## Post-Upload Setup

1. Open `notebooks/1_setup_and_data_prep.ipynb`
2. Run all cells to:
   - Mount Drive
   - Install dependencies
   - Download models
   - Verify setup

3. Proceed to training notebooks when setup complete

## Data Preparation Notes

### How2Sign Structure
Ensure test split has:
```
data/How2Sign/test/
├── poses/
│   └── [sentence_name]/
│       └── [sentence_name]_[frame]_3D.pkl
├── re_aligned/
│   └── how2sign_realigned_test_preprocessed_fps.csv
└── raw_videos/
    └── [sentence_name].mp4
```

### Required CSV Columns
- VIDEO_ID
- VIDEO_NAME  
- SENTENCE_ID
- SENTENCE_NAME
- START_REALIGNED
- END_REALIGNED
- SENTENCE
- fps

## Troubleshooting

### Upload Fails
- Large files: Use Google Drive desktop app
- Slow upload: Upload overnight
- Compression: Zip large directories first

### Drive Full
- Delete previous experiments
- Remove cached models
- Use Colab Pro for more storage

### Path Issues
- Use absolute paths: `/content/drive/MyDrive/SOKE/`
- Check capitalization (case-sensitive)
- Verify Drive mount: `!ls /content/drive/MyDrive/`

