"""
Local inference server — drop-in replacement for the Modal endpoint.
Streams SMPL-X vertex frames over SSE, identical protocol to deploy/serve.py.
"""

import base64
import json
import time

import numpy as np
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHUNK_SIZE = 8
_engine = None


def get_engine():
    """
    Lazy-load the inference engine.
    Adjust paths below to match where YOUR model files live.
    """
    global _engine
    if _engine is not None:
        return _engine

    import os
    import sys

    # Point this at the SaSOKE repo root so imports work
    # REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
    REPO_ROOT = (
        "/home/eyadalghamdi/Desktop/My Projects/Ai-DS Projects/UJ-Projects/SaSOKE/"
    )
    sys.path.insert(0, REPO_ROOT)

    # --- IMPORTANT: patch VOL_MOUNT before importing inference ---
    # The inference module reads VOL_MOUNT from deploy.image.
    # Override it to point at your local model directory.
    import deploy.image as img

    img.VOL_MOUNT = os.environ.get(
        "SOKE_MODEL_DIR",
        "/home/eyadalghamdi/Desktop/My Projects/Ai-DS Projects/UJ-Projects/SOKE/SOKE/",
    )

    from deploy.inference import SOKEInference

    device = "cuda"  # change to "cpu" if no GPU (will be slow)
    _engine = SOKEInference(device=device)
    return _engine


@app.options("/generate")
async def options_generate(request: Request):
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


@app.post("/generate")
async def generate(request: Request):
    body = await request.json()
    text = body.get("text", "")
    lang_token = body.get("lang_token", "isharah")

    if not text:
        return {"error": "text is required"}

    engine = get_engine()

    def stream():
        # Set seeds
        import random

        import numpy as np
        import torch

        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)

        t0 = time.time()
        params, T = engine.generate_params(text, lang_token)
        t1 = time.time()
        print(f"[gen] params: {T} frames in {t1 - t0:.2f}s")

        yield f"event: metadata\ndata: {json.dumps({'fps': 30, 'total_frames': T})}\n\n"

        for start in range(0, T, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, T)
            verts = engine.params_to_vertices(params, start, end)

            for i in range(verts.shape[0]):
                flat = verts[i].astype(np.float32).tobytes()
                b64 = base64.b64encode(flat).decode("ascii")
                yield f"event: frame\ndata: {json.dumps({'f': start + i, 'v': b64})}\n\n"

        t2 = time.time()
        print(f"[gen] smplx + stream: {t2 - t1:.2f}s  total: {t2 - t0:.2f}s")
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
