"""
Extract SMPL-X face topology + default T-pose vertices for the browser.

Usage:
    modal run deploy/extract_faces.py
    # Outputs: frontend/public/smplx_faces.bin, frontend/public/smplx_tpose.bin
"""

import os
from deploy.image import app, volume, VOL_MOUNT


@app.function(volumes={VOL_MOUNT: volume}, timeout=120)
def extract_assets():
    import torch
    import numpy as np
    import smplx

    model = smplx.create(
        os.path.join(VOL_MOUNT, "deps", "smpl_models"),
        "smplx", gender="NEUTRAL", use_pca=False, use_face_contour=True,
    )

    faces = np.array(model.faces, dtype=np.uint32).flatten()
    print(f"Faces: {len(faces) // 3} triangles")

    with torch.no_grad():
        output = model()
        verts = output.vertices[0].cpu().numpy().astype(np.float32)
    print(f"T-pose vertices: {verts.shape}, range [{verts.min():.3f}, {verts.max():.3f}]")

    return faces.tobytes(), verts.flatten().tobytes()


@app.local_entrypoint()
def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public")
    os.makedirs(out_dir, exist_ok=True)

    faces_bytes, tpose_bytes = extract_assets.remote()

    for name, data in [("smplx_faces.bin", faces_bytes), ("smplx_tpose.bin", tpose_bytes)]:
        path = os.path.join(out_dir, name)
        with open(path, "wb") as f:
            f.write(data)
        print(f"Wrote {name} ({len(data):,} bytes)")
