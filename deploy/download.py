"""
One-time download: pull all model weights from Google Drive into the Modal Volume.

Usage: modal run deploy/download.py
"""

import os
from deploy.image import app, volume, VOL_MOUNT


@app.function(volumes={VOL_MOUNT: volume}, timeout=3600)
def download_models():
    import gdown
    import zipfile

    downloads = [
        ("SOKE ckpt",  "1WtU5-Wqsi82JVKdQ2rvqfy6nXhIcxtcF",
         f"{VOL_MOUNT}/experiments/mgpt/SOKE/checkpoints/last.ckpt"),
        ("DETO ckpt",  "1lAr_oBVZ6kMwsWtVz32OZRW4V4dlvyLf",
         f"{VOL_MOUNT}/experiments/mgpt/DETO/checkpoints/last-v3.ckpt"),
        ("mean.pt",    "1NH-eVtS0nNjMjCwae-A1ii5sxj44C3bo",
         f"{VOL_MOUNT}/deps/mean.pt"),
        ("std.pt",     "1FHHWS0GPM2s6S2PB2JHv4ufdEbzezuKW",
         f"{VOL_MOUNT}/deps/std.pt"),
    ]

    zip_downloads = [
        ("SMPL-X models", "1YIXddvvBJPQVRuKON2Xc9EEDXikRTteo",
         f"{VOL_MOUNT}/deps/smpl_models.zip", f"{VOL_MOUNT}/deps/smpl_models"),
    ]

    folder_downloads = [
        ("mBART weights", "15Mp_q4-03z0C_Qfg74dV3k15iPdbLxgA",
         f"{VOL_MOUNT}/deps/mbart-h2s-csl-phoenix-isharah"),
    ]

    for name, gid, dest in downloads:
        if os.path.isfile(dest):
            print(f"[skip] {name}")
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"[download] {name} -> {dest}")
        try:
            gdown.download(id=gid, output=dest, quiet=False)
        except Exception as e:
            print(f"[WARN] {name}: {e}")

    for name, gid, zip_path, extract_to in zip_downloads:
        if os.path.isdir(extract_to) and os.listdir(extract_to):
            print(f"[skip] {name}")
            continue
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        print(f"[download] {name}")
        try:
            gdown.download(id=gid, output=zip_path, quiet=False)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(extract_to)
            os.remove(zip_path)
        except Exception as e:
            print(f"[WARN] {name}: {e}")

    for name, gid, dest in folder_downloads:
        if os.path.isdir(dest) and os.listdir(dest):
            print(f"[skip] {name}")
            continue
        os.makedirs(dest, exist_ok=True)
        print(f"[download] {name}")
        try:
            gdown.download_folder(id=gid, output=dest, quiet=False)
        except Exception as e:
            print(f"[WARN] {name}: {e}")

    volume.commit()
    print("=== Done ===")
