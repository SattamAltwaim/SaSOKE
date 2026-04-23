"""
Smoke test: text in, SMPL-X vertices out.

Usage: modal run deploy/test.py
"""

from deploy.image import app, volume, VOL_MOUNT


@app.function(gpu="A100", volumes={VOL_MOUNT: volume}, timeout=300)
def test_inference():
    from deploy.inference import SOKEInference

    engine = SOKEInference(device="cuda")
    vertices, joints, T = engine.generate("Hello, how are you?", lang_token="how2sign")

    print(f"\nFrames: {T}")
    print(f"Vertices: {vertices.shape}  (expect ({T}, 10475, 3))")
    print(f"Joints:   {joints.shape}")
    print(f"Range:    [{vertices.min():.4f}, {vertices.max():.4f}]")
    print("PASS")
