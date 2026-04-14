# SaSOKE — Real-Time Saudi/Arabic Sign Language Production

SaSOKE generates 3D sign language animations from text input. Type Arabic or English text, and the system produces a full-body SMPL-X mesh animation of the corresponding sign language in real time.

Built on [SOKE (Signs as Tokens)](https://github.com/EyadAlgha/IsharahSOKE) by Zuo et al. (ICCV 2025), fine-tuned on the [Isharah-500](https://snalyami.github.io/Isharah_CSLR/) dataset — the first large-scale continuous Saudi Sign Language (SSL) dataset featuring 30,000+ video samples signed by deaf and hearing-impaired individuals.

**Live demo:** [sasoke-uj.web.app](https://sasoke-uj.web.app)

## Architecture

```
Browser (React + Three.js)  ←—  SSE stream  ←—  Modal GPU endpoint (SOKE inference)
   Firebase Hosting                                A10G GPU, always-warm
```

**Two-stage model pipeline:**

1. **DETO (Decoupled Tokenizer)** — Three VQ-VAE models discretize sign poses into tokens. Codebook sizes: body=96, left hand=192, right hand=192.
2. **AMG (Autoregressive Multilingual Generator)** — mBART-large-cc25 with multi-head decoding predicts body/hand tokens simultaneously from text. DETO decoder converts tokens back to SMPL-X pose parameters (133 dims/frame).

**Optimizations:**
- Always-warm GPU container (`min_containers=1`) — no cold starts
- Chunked SMPL-X streaming — first frames arrive ~3s after request
- Base64 binary vertex encoding — 2x smaller payloads than JSON
- Server-side Gaussian temporal smoothing — eliminates VQ-VAE jitter
- Client-side 60fps vertex interpolation — smooth motion between keyframes

## Project Structure

```
SaSOKE/
├── deploy/                 # Modal deployment
│   ├── image.py            # App, image, volume definitions
│   ├── inference.py        # SOKEInference engine (text → SMPL-X vertices)
│   ├── serve.py            # POST /generate SSE endpoint
│   ├── extract_faces.py    # Extract SMPL-X mesh topology + T-pose
│   ├── download.py         # One-time model weight download
│   └── test.py             # Smoke test
├── frontend/               # Firebase-hosted web app
│   ├── src/
│   │   ├── App.tsx         # Main app with playback controls
│   │   ├── components/
│   │   │   ├── Scene.tsx       # Three.js canvas + lighting
│   │   │   ├── SignModel.tsx   # SMPL-X mesh with frame interpolation
│   │   │   └── InputBar.tsx    # Glass-style input card
│   │   └── hooks/
│   │       └── useSignStream.ts  # SSE client + playback engine
│   ├── public/
│   │   ├── smplx_faces.bin     # Mesh face topology (static)
│   │   └── smplx_tpose.bin     # Default T-pose vertices
│   ├── firebase.json
│   └── package.json
├── mGPT/                   # Upstream model code (from IsharahSOKE)
│   ├── archs/              # VQ-VAE, mBART, multi-head LM
│   └── utils/              # SMPL-X wrapper, helpers
├── configs/                # OmegaConf YAML model configs
├── name2kws_*.json         # Keyword lookup tables (inference)
└── word2code.json          # Word-to-motion-code mapping (inference)
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Modal](https://modal.com/) account and CLI (`pip install modal && modal setup`)
- [Firebase CLI](https://firebase.google.com/docs/cli) (`npm install -g firebase-tools`)

### 1. Download model weights

Populate the Modal persistent volume with all checkpoints and SMPL-X body models:

```bash
modal run deploy/download.py
```

### 2. Extract frontend assets

Extract SMPL-X mesh topology and default T-pose for the browser:

```bash
modal run deploy/extract_faces.py
```

### 3. Deploy the API

```bash
# Development (hot reload)
modal serve deploy/serve.py

# Production
modal deploy deploy/serve.py
```

### 4. Deploy the frontend

```bash
cd frontend
npm install
npm run build
firebase deploy --only hosting
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
- `metadata` — `{ "fps": 30, "total_frames": N }`
- `frame` — `{ "f": i, "v": "<base64 Float32Array>" }` (10,475 × 3 floats per frame)
- `done` — `{}`

**Supported language tokens:** `isharah` (Saudi SL), `how2sign` (ASL), `csl` (Chinese SL), `phoenix` (German SL)

## Model Details

- **Output:** 133-dim feature vector per frame → SMPL-X mesh (10,475 vertices)
- **Playback:** 30 FPS default (adjustable 10–30 in UI)
- **Typical length:** 40–400 frames (1.3–13 seconds)
- **Body model:** SMPL-X neutral (54 joints including hands and face)
- **Smoothing:** Gaussian temporal filter (σ=1.5) on joint angles + 60fps client-side interpolation

## Acknowledgments

- [SOKE: Unified Sign Language Production](https://github.com/EyadAlgha/IsharahSOKE) — Zuo et al., ICCV 2025
- [Isharah-500 Dataset](https://snalyami.github.io/Isharah_CSLR/) — Large-scale continuous Saudi Sign Language dataset (Alyami et al., IEEE TMM 2026)
- [SMPL-X](https://smpl-x.is.tue.mpg.de/) — Expressive body model

## License

See [license.txt](license.txt).
