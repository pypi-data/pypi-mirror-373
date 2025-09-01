# Runtime image constants for AIAuto
# These images are pre-tested and guaranteed to work with AIAuto

# Available runtime images
RUNTIME_IMAGES = [
    # CPU Images
    "ghcr.io/astral-sh/uv:python3.8-bookworm-slim",
    "ghcr.io/astral-sh/uv:python3.9-bookworm-slim",
    "ghcr.io/astral-sh/uv:python3.10-bookworm-slim",
    "ghcr.io/astral-sh/uv:python3.11-bookworm-slim",
    "ghcr.io/astral-sh/uv:python3.12-bookworm-slim",

    # GPU Images (PyTorch)
    "pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime",
    "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",
    "pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime",

    # GPU Images (TensorFlow)
    "tensorflow/tensorflow:2.15.0-gpu",

    # Custom/Legacy images
    "registry.gitlab.com/01ai/eng/aiauto/aiauto/zipline-prepared:main-v00.00.01-amd64-11ca2c41-250901",
]
