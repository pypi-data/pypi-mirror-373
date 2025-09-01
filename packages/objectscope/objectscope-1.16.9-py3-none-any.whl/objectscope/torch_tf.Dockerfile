# Use an NVIDIA CUDA runtime base image.
#FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04
FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

# Metadata labels.
#LABEL maintainer="your.email@example.com"
#LABEL description="Container with Python 3.12, PyTorch & TensorFlow GPU support"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
# Install system dependencies required for building Python.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


RUN apt update
RUN apt install -y \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender1

# Download, compile, and install Python 3.12.
# Note: Adjust the Python version (3.12.0) if a newer patch version is desired.
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
    tar xzf Python-3.12.0.tgz && \
    cd Python-3.12.0 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.12.0 Python-3.12.0.tgz

# Upgrade pip using the newly installed Python 3.12.
RUN python3.12 -m pip install --upgrade pip

# Install PyTorch and TensorFlow with GPU support.
# The PyTorch installation fetches the CUDA 11.8-specific wheel.
RUN python3.12 -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118 \
    && python3.12 -m pip install tensorflow

RUN python3.12 -m pip install 'tensorflow[and-cuda]'

RUN pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu129


    # Create a working directory.
WORKDIR /workspace

# Set the default command to launch Python 3.12 interactive shell.
CMD ["python3.12"]
