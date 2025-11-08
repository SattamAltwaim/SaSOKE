# SaSOKE: Saudi Sign Language Production

[![GitHub](https://img.shields.io/badge/GitHub-SaSOKE-blue)](https://github.com/SattamAltwaim/SaSOKE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)

Fine-tuning SOKE for Saudi Sign Language (Isharah) production.

## About

This repository extends [SOKE: Signs as Tokens](https://github.com/2000ZRL/SOKE) by Zuo et al. (ICCV 2025) for Saudi Sign Language generation using the Isharah dataset.

**Project Context:**
- Senior Project I, University of Jeddah
- Collaboration with SDAIA-KFUPM Joint Research Center for Artificial Intelligence
- Focus: Multilingual sign language generation for Saudi Sign Language

## Original SOKE

SOKE (Signs as Tokens) is a retrieval-enhanced multilingual sign language generator that:
- Uses VQ-VAE to discretize continuous sign poses into tokens
- Employs mBART for multilingual text-to-sign generation
- Supports How2Sign, CSL-Daily, and Phoenix-2014T datasets

**Original Paper:** "Signs as Tokens: A Retrieval-Enhanced Multilingual Sign Language Generator" Zuo et al., ICCV 2025

## Our Contribution

SaSOKE adapts SOKE for:
- **Saudi Sign Language (Isharah)** dataset integration
- **Google Colab** training workflow with CUDA support
- **GitHub + Google Drive** hybrid storage for version control and data management
- **Plug-and-play notebooks** for easy setup and training

## Quick Start

### Prerequisites
- Google Account with Drive
- Google Colab (free tier or Pro)
- Isharah dataset (or How2Sign for testing)

### Setup (5 minutes)

1. **Access Notebooks:** Go to [Google Colab](https://colab.research.google.com), File → Open notebook → GitHub, Enter: \`SattamAltwaim/SaSOKE\`
2. **Run Setup:** Open \`notebooks/1_setup_and_data_prep.ipynb\`, Runtime → Change runtime type → GPU, Run all cells
3. **Upload Data:** Upload your dataset to Google Drive: \`/MyDrive/SOKE_data/data/Isharah/\`
4. **Start Training:** Open \`notebooks/3_train_soke.ipynb\`, Run all cells

## Notebooks

- **1_setup_and_data_prep.ipynb**: Downloads dependencies, SMPL models, mBART
- **2_train_tokenizer.ipynb**: Trains VQ-VAE (optional)
- **3_train_soke.ipynb**: Fine-tunes mBART on sign language
- **4_inference.ipynb**: Generates sign predictions from text

## Data Organization

Google Drive structure:
\`\`\`
/MyDrive/SOKE_data/
├── data/Isharah/          # Your dataset
├── deps/                  # Downloaded by setup
├── smpl-x/               # Downloaded by setup
└── checkpoints/          # Training outputs
\`\`\`

## GPU Requirements

- **Minimum**: Colab Free (T4, 16GB) - batch_size=8, ~72hrs
- **Recommended**: Colab Pro (V100, 32GB) - batch_size=16, ~36hrs
- **Optimal**: Colab Pro+ (A100, 40GB) - batch_size=32, ~18hrs

## Citation

### Original SOKE
\`\`\`bibtex
@inproceedings{zuo2025soke,
  title={Signs as Tokens: A Retrieval-Enhanced Multilingual Sign Language Generator},
  author={Zuo, Ronglai and others},
  booktitle={ICCV},
  year={2025}
}
\`\`\`

### SaSOKE
\`\`\`bibtex
@misc{altwaim2025sasoke,
  title={SaSOKE: Saudi Sign Language Production},
  author={Altwaim, Sattam and team},
  year={2025},
  note={Senior Project, University of Jeddah. SDAIA-KFUPM Joint Research Center}
}
\`\`\`

## Acknowledgments

- **Original SOKE**: Zuo et al. for base architecture and pretrained models
- **SDAIA-KFUPM Joint Research Center**: Research support and collaboration
- **University of Jeddah**: Senior project supervision
- **Isharah Dataset**: For Saudi Sign Language data

## Team

University of Jeddah - Senior Project I

Supervised by SDAIA-KFUPM Joint Research Center for Artificial Intelligence

## Resources

- **Original SOKE**: [GitHub](https://github.com/2000ZRL/SOKE) | [Paper](https://arxiv.org/pdf/2411.17799)
- **SaSOKE**: [GitHub](https://github.com/SattamAltwaim/SaSOKE)
- **Documentation**: See \`notebooks/README.md\` and docs folder

## License

Builds upon SOKE and follows its original license terms.
