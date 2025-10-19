FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install pget for faster downloads
RUN curl -o /usr/local/bin/pget -L "https://github.com/replicate/pget/releases/download/v0.5.6/pget_linux_x86_64" && \
    chmod +x /usr/local/bin/pget

# Install PyTorch and dependencies
RUN pip install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install other Python dependencies
RUN pip install --no-cache-dir \
    xformers==0.0.22 \
    opencv-python-headless \
    pillow \
    numpy \
    requests \
    einops \
    soundfile \
    librosa \
    pydub \
    transformers \
    accelerate \
    sentencepiece \
    protobuf

# Clone ComfyUI
WORKDIR /
RUN git clone https://github.com/comfyanonymous/ComfyUI /ComfyUI

# Install ComfyUI requirements
WORKDIR /ComfyUI
RUN pip install --no-cache-dir -r requirements.txt

# Create directory structure
RUN mkdir -p /ComfyUI/models/checkpoints \
    /ComfyUI/models/vae \
    /ComfyUI/models/loras \
    /ComfyUI/models/controlnet \
    /ComfyUI/models/clip_vision \
    /ComfyUI/models/text_encoders \
    /ComfyUI/models/audio \
    /ComfyUI/input \
    /ComfyUI/output \
    /ComfyUI/custom_nodes

# Install custom nodes
WORKDIR /ComfyUI/custom_nodes
RUN git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git && \
    cd ComfyUI-VideoHelperSuite && \
    pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git && \
    cd ComfyUI-WanVideoWrapper && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
WORKDIR /app
COPY predict.py /app/
COPY workflow_api.json /app/

# Set Python path
ENV PYTHONPATH=/ComfyUI:$PYTHONPATH

# Expose port (optional, for local testing)
EXPOSE 5000

# Run prediction script
CMD ["python", "predict.py"]
