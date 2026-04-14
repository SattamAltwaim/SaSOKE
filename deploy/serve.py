"""
POST /generate — SSE stream of SMPL-X vertex frames.

Optimizations:
  - keep_warm(1): always-hot container, no cold starts
  - Chunked SMPL-X: LM + VQ decode first, then SMPL-X in batches of CHUNK_SIZE
  - Binary encoding: vertices sent as base64 Float32Array (~2x smaller than JSON)

Usage:
    modal serve deploy/serve.py   # dev
    modal deploy deploy/serve.py  # prod
"""

import modal
from deploy.image import app, volume, VOL_MOUNT

CHUNK_SIZE = 8

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from deploy.inference import SOKEInference
        _engine = SOKEInference(device="cuda")
    return _engine


@app.function(
    gpu="A10G",
    volumes={VOL_MOUNT: volume},
    timeout=300,
    scaledown_window=180,
    min_containers=1,
)
@modal.concurrent(max_inputs=4)
@modal.fastapi_endpoint(method="POST", docs=True)
def generate(body: dict):
    import json
    import base64
    import time
    import numpy as np
    from starlette.responses import StreamingResponse

    text = body.get("text", "")
    lang_token = body.get("lang_token", "isharah")
    if not text:
        return {"error": "text is required"}

    engine = _get_engine()

    def stream():
        t0 = time.time()

        # Stage 1: LM + VQ decode (fast, ~2-4s)
        params, T = engine.generate_params(text, lang_token)
        t1 = time.time()
        print(f"[gen] params: {T} frames in {t1 - t0:.2f}s")

        yield f"event: metadata\ndata: {json.dumps({'fps': 30, 'total_frames': T})}\n\n"

        # Stage 2: SMPL-X forward in chunks — stream as we go
        for start in range(0, T, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, T)
            verts = engine.params_to_vertices(params, start, end)  # (chunk, 10475, 3)

            for i in range(verts.shape[0]):
                flat = verts[i].astype(np.float32).tobytes()
                b64 = base64.b64encode(flat).decode("ascii")
                yield f"event: frame\ndata: {json.dumps({'f': start + i, 'v': b64})}\n\n"

        t2 = time.time()
        print(f"[gen] smplx + stream: {t2 - t1:.2f}s  total: {t2 - t0:.2f}s")
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })
