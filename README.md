# SaSOKE — Real-Time Saudi/Arabic Sign Language Production

SaSOKE generates 3D sign language animations from text input. Type Arabic or English text, and the system produces a full-body SMPL-X mesh animation of the corresponding sign language.

Built on [SOKE (Signs as Tokens)](https://github.com/EyadAlgha/IsharahSOKE) by Zuo et al. (ICCV 2025), fine-tuned on the [Isharah-500](https://snalyami.github.io/Isharah_CSLR/) dataset — the first large-scale continuous Saudi Sign Language (SSL) dataset featuring 30,000+ video samples signed by deaf and hearing-impaired individuals.

## Architecture

```
Browser (Three.js)  ←—  SSE stream  ←—  Modal GPU endpoint (SOKE inference)
```

**Two-stage model pipeline:**

1. **DETO (Decoupled Tokenizer)** — Three VQ-VAE models discretize sign poses into tokens. Codebook sizes: body=96, left hand=192, right hand=192.
2. **AMG (Autoregressive Multilingual Generator)** — mBART-large-cc25 with multi-head decoding predicts body/hand tokens simultaneously from text. DETO decoder converts tokens back to SMPL-X pose parameters (133 dims/frame at 20 FPS).

## Project Structure

```
SaSOKE/
├── deploy/                 # Modal deployment (our code)
│   ├── image.py            # App, image, volume definitions
│   ├── download.py         # One-time model weight download
│   ├── inference.py        # SOKEInference engine (text → SMPL-X vertices)
│   ├── serve.py            # POST /generate SSE endpoint
│   └── test.py             # Smoke test
├── mGPT/                   # Upstream model code (from IsharahSOKE)
│   ├── archs/              # VQ-VAE, mBART, multi-head LM  ← used in inference
│   ├── utils/              # SMPL-X wrapper, helpers        ← used in inference
│   ├── data/               # Data modules (training only)
│   ├── models/             # MotionGPT wrapper (training only)
│   ├── losses/             # Loss functions (training only)
│   ├── metrics/            # Evaluation metrics (training only)
│   └── render/             # Blender/matplotlib viz (training only)
├── configs/                # OmegaConf YAML model configs
├── scripts/                # Isharah keyword generation scripts
├── name2kws_*.json         # Keyword lookup tables (inference)
├── word2code.json          # Word-to-motion-code mapping (inference)
└── requirements.txt        # Python deps (inference + training sections)
```

## Setup

### Prerequisites

- Python 3.10+
- [Modal](https://modal.com/) account and CLI (`pip install modal && modal setup`)
- Model weights from Google Drive (see below)

### 1. Download model weights

Populate the Modal persistent volume with all checkpoints and SMPL-X body models:

```bash
modal run deploy/download.py
```

This downloads:
- SOKE checkpoint (~4.8 GB)
- DETO checkpoint (~779 MB)
- mBART weights (tokenizer + config)
- SMPL-X body models
- Denormalization tensors (mean.pt, std.pt)

### 2. Verify inference

```bash
modal run deploy/test.py
```

Expected output:
```
Frames: 260
Vertices: torch.Size([260, 10475, 3])
PASS
```

### 3. Run the API

```bash
# Development (hot reload)
modal serve deploy/serve.py

# Production
modal deploy deploy/serve.py
```

## API

### `POST /generate`

Streams SMPL-X vertex frames via Server-Sent Events.

**Request:**
```json
{
  "text": "مرحبا كيف حالك",
  "lang_token": "isharah"
}
```

**SSE Events:**
- `metadata` — `{ "fps": 20, "total_frames": N }`
- `frame` — `{ "frame": i, "vertices": [[x,y,z], ...] }` (10,475 vertices per frame)
- `done` — `{}`

**Supported language tokens:** `isharah` (Saudi SL), `how2sign` (ASL), `csl` (Chinese SL), `phoenix` (German SL)

## Model Details

- **Output:** 133-dim feature vector per frame → SMPL-X mesh (10,475 vertices)
- **Frame rate:** 20 FPS
- **Typical length:** 40–400 frames (2–20 seconds)
- **Body model:** SMPL-X neutral (54 joints including hands and face)

## Acknowledgments

- [SOKE: Unified Sign Language Production](https://github.com/EyadAlgha/IsharahSOKE) — Zuo et al., ICCV 2025
- [Isharah-500 Dataset](https://snalyami.github.io/Isharah_CSLR/) — Large-scale continuous Saudi Sign Language dataset (Alyami et al., IEEE TMM 2026)
- [SMPL-X](https://smpl-x.is.tue.mpg.de/) — Expressive body model

## License

See [license.txt](license.txt).
