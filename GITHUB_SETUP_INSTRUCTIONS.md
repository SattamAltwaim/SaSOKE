# SaSOKE GitHub + Google Drive Setup

## Architecture

**GitHub (Code):** Version-controlled code, configs, notebooks
**Google Drive (Data):** Large files, datasets, models, checkpoints

## Step 1: Create GitHub Repo

```bash
# On your Mac, navigate to SOKE directory
cd "/Volumes/The Storage!/SOKE"

# Add all code files
git add .

# Commit changes
git commit -m "Initial SaSOKE setup with Colab notebooks"

# Create new repo on GitHub.com:
# 1. Go to https://github.com/new
# 2. Name: SaSOKE
# 3. Description: "Multilingual Sign Language Generator (fork of SOKE)"
# 4. Public or Private (your choice)
# 5. Don't initialize with README (we have one)
# 6. Click "Create repository"
```

## Step 2: Push to Your Repo

```bash
# Remove old remote
git remote remove origin

# Add your new remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/SaSOKE.git

# Push code
git push -u origin main
# If it says 'master' instead: git push -u origin master
```

## Step 3: Prepare Google Drive

Create this structure in Google Drive:

```
/MyDrive/SOKE_data/
├── data/
│   └── How2Sign/
│       ├── train/
│       ├── val/
│       └── test/
├── deps/
│   ├── smpl_models/      (downloaded by setup notebook)
│   ├── t2m/              (downloaded by setup notebook)
│   └── mbart-h2s-csl-phoenix/  (downloaded by setup notebook)
├── smpl-x/
│   ├── mean.pt           (downloaded by setup notebook)
│   └── std.pt            (downloaded by setup notebook)
└── checkpoints/
    └── vae/
        └── tokenizer.ckpt  (downloaded by setup notebook)
```

## Step 4: Upload Data to Drive

Upload ONLY your dataset to Drive:

```
Upload to: /MyDrive/SOKE_data/data/How2Sign/
```

Models will be downloaded automatically by the setup notebook.

## Step 5: Update Notebooks

In each notebook, replace `YOUR_USERNAME` with your actual GitHub username:

```python
# Change this line in all notebooks:
!git clone https://github.com/YOUR_USERNAME/SaSOKE.git

# To (example):
!git clone https://github.com/yourusername/SaSOKE.git
```

## Step 6: Run in Colab

1. Open Colab: https://colab.research.google.com
2. File → Open notebook → GitHub tab
3. Enter: `YOUR_USERNAME/SaSOKE`
4. Open `notebooks/1_setup_and_data_prep.ipynb`
5. Runtime → Change runtime type → GPU
6. Run all cells

## Workflow Summary

### First Time Setup:
1. Run `1_setup_and_data_prep.ipynb` - Downloads models to Drive
2. Upload your dataset to `/MyDrive/SOKE_data/data/`
3. Ready to train!

### Training:
- Code clones from GitHub (latest version)
- Data loads from Drive (persistent)
- Results save to Drive
- Can commit code changes back to GitHub from Colab

### Updating Code:
```python
# In Colab, pull latest changes:
!git pull origin main

# Or make changes and push:
!git add .
!git commit -m "Update config"
!git push
```

## What Goes Where

### GitHub (SaSOKE repo):
- mGPT/ (all code)
- configs/
- notebooks/
- train.py, test.py
- requirements_colab.txt
- All .md documentation
- .gitignore

### Google Drive (/MyDrive/SOKE_data/):
- data/ (your datasets)
- deps/ (downloaded models)
- smpl-x/ (statistics)
- checkpoints/ (model checkpoints)
- experiments/ (training outputs)
- results/ (inference outputs)

## Benefits

1. **Version Control**: Track code changes, collaborate, rollback
2. **Storage**: Large files stay in Drive, not in git
3. **Collaboration**: Share code via GitHub, data via Drive
4. **Always Updated**: Notebooks pull latest code on each run
5. **Clean Separation**: Code vs Data

## Troubleshooting

### "Repository not found"
- Check username in clone command
- Verify repo is public or you're logged into GitHub

### "Drive files not found"
- Verify Drive structure: `/MyDrive/SOKE_data/`
- Run setup notebook to download models
- Check Drive mount succeeded

### "Authentication required" for push
```python
# In Colab, configure git:
!git config --global user.email "your@email.com"
!git config --global user.name "Your Name"

# Use personal access token for push:
# Create token at: https://github.com/settings/tokens
```

### Sync local Mac changes to GitHub
```bash
# On your Mac:
cd "/Volumes/The Storage!/SOKE"
git pull  # Get latest from GitHub
git add .
git commit -m "Your changes"
git push
```

