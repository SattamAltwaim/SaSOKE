"""Shared Modal app, image, and volume definitions."""

import modal

VOLUME_NAME = "sasoke-models"
VOL_MOUNT = "/vol/models"

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch==2.1.2",
        "numpy<2",
        "omegaconf==2.3.0",
        "transformers==4.36.2",
        "einops",
        "smplx==0.1.28",
        "chumpy",
        "gdown",
        "scipy",
        "tokenizers",
        "sentencepiece",
        "protobuf",
        "fastapi[standard]",
    )
    .env({"SOKE_DATA_ROOT": VOL_MOUNT, "PYTHONPATH": "/app"})
    .workdir("/app")
    .add_local_file("mGPT/__init__.py", remote_path="/app/mGPT/__init__.py")
    .add_local_dir("mGPT/archs", remote_path="/app/mGPT/archs")
    .add_local_dir("mGPT/utils", remote_path="/app/mGPT/utils")
    .add_local_dir("deploy", remote_path="/app/deploy")
    .add_local_file("name2kws_train.json", remote_path="/app/name2kws_train.json")
    .add_local_file("name2kws_val.json", remote_path="/app/name2kws_val.json")
    .add_local_file("name2kws_test.json", remote_path="/app/name2kws_test.json")
    .add_local_file("word2code.json", remote_path="/app/word2code.json")
)

app = modal.App("sasoke", image=image)
