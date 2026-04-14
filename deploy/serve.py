"""
POST /generate — SSE stream of SMPL-X vertex frames.

Usage:
    modal serve deploy/serve.py   # dev
    modal deploy deploy/serve.py  # prod
"""

import modal
from deploy.image import app, volume, VOL_MOUNT

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from deploy.inference import SOKEInference
        _engine = SOKEInference(device="cuda")
    return _engine


@app.function(gpu="A10G", volumes={VOL_MOUNT: volume}, timeout=300, scaledown_window=120)
@modal.concurrent(max_inputs=4)
@modal.fastapi_endpoint(method="POST", docs=True)
def generate(body: dict):
    import json
    from starlette.responses import StreamingResponse

    text = body.get("text", "")
    lang_token = body.get("lang_token", "isharah")
    if not text:
        return {"error": "text is required"}

    engine = _get_engine()
    vertices, _, T = engine.generate(text, lang_token)
    verts = vertices.cpu().numpy()

    def stream():
        yield f"event: metadata\ndata: {json.dumps({'fps': 20, 'total_frames': T})}\n\n"
        for i in range(T):
            yield f"event: frame\ndata: {json.dumps({'frame': i, 'vertices': verts[i].tolist()})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })
