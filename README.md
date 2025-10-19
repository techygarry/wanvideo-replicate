# WanVideo ComfyUI Model for Replicate

This repository contains a Cog-wrapped ComfyUI workflow for WanVideo image-to-video generation with audio sync (InfiniteTalk).

## Prerequisites

1. Install Cog: https://github.com/replicate/cog
2. Install Docker: https://docs.docker.com/get-docker/
3. Have a Replicate account: https://replicate.com

## Model Files Required

Before deploying, you need to download the following model files and update the URLs in `predict.py`:

### Required Models:
- `Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors` - Main WanVideo model
- `lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors` - LoRA
- `Wan2_1-InfiniTetalk-Single_fp16.safetensors` - MultiTalk model
- `clip_vision_h.safetensors` - CLIP Vision model
- `umt5_xxl_fp16.safetensors` - Text encoder
- `wan_2.1_vae.safetensors` - VAE model
- `wav2vec2-chinese-base_fp16.safetensors` - Audio encoder

### Where to Get Models:
You can download these from:
- HuggingFace repositories
- CivitAI
- Official WanVideo releases

### Hosting Model Files:
You need to host these files somewhere accessible via URL:
- HuggingFace (recommended)
- Your own S3/cloud storage
- Direct download links

Then update the `models` dictionary in `predict.py` (around line 25) with your URLs.

## Setup Steps

### 1. Update Model URLs

Edit `predict.py` and replace `YOUR_MODEL_URL_HERE` with actual URLs for each model:

```python
models = {
    "Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors": {
        "url": "https://your-storage.com/path/to/model.safetensors",
        "dest": "/ComfyUI/models/checkpoints/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors"
    },
    # ... update all other models
}
```

Then uncomment the download loop in the `setup()` method (around line 61):

```python
for model_name, model_info in models.items():
    self.download_weights(model_info["url"], model_info["dest"])
```

### 2. Test Locally

Build the Docker image:
```bash
cog build
```

Run a prediction locally:
```bash
cog predict -i input_image=@your_image.jpg -i audio_file=@your_audio.mp3
```

### 3. Push to Replicate

First, create a model on Replicate:
```bash
cog login
cog push r8.im/your-username/your-model-name
```

This will:
1. Build the Docker image
2. Push it to Replicate's registry
3. Create a new version of your model

### 4. Use the API

Once deployed, you can call your model via API:

```python
import replicate

output = replicate.run(
    "your-username/your-model-name:version-id",
    input={
        "input_image": open("image.jpg", "rb"),
        "audio_file": open("audio.mp3", "rb"),
        "prompt": "a person speaking with emotions",
        "num_frames": 100,
        "fps": 25,
        "steps": 6,
        "cfg_scale": 1.0,
        "seed": -1
    }
)

print(output)
```

Or via cURL:
```bash
curl -X POST https://api.replicate.com/v1/predictions \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "your-model-version-id",
    "input": {
      "input_image": "https://url-to-your-image.jpg",
      "audio_file": "https://url-to-your-audio.mp3",
      "prompt": "a person speaking",
      "num_frames": 100
    }
  }'
```

## Parameters

- `input_image`: Input image for video generation (required)
- `audio_file`: Audio file for lip sync (MP3/WAV, optional)
- `prompt`: Text description of the video (default: "a person is speaking with gestures and emotions")
- `negative_prompt`: What to avoid in generation
- `num_frames`: Number of frames (1-1000, default: 100)
- `fps`: Frames per second (10-60, default: 25)
- `steps`: Sampling steps (1-50, default: 6)
- `cfg_scale`: CFG scale (0.1-20.0, default: 1.0)
- `seed`: Random seed (-1 for random)

## Workflow Customization

To use your own ComfyUI workflow:
1. Export your workflow as API format in ComfyUI (Dev menu → Save API Format)
2. Replace `workflow_api.json` with your workflow
3. Update `predict.py` to map the correct node IDs for your workflow

## Troubleshooting

### Build fails
- Check that all custom nodes are properly installed in `cog.yaml`
- Verify CUDA compatibility

### Models not downloading
- Ensure URLs are publicly accessible
- Check network connectivity during build
- Use `pget` for faster downloads (already included)

### Workflow execution fails
- Verify all node IDs in `predict.py` match your workflow
- Check that all required models are downloaded
- Review ComfyUI logs for errors

## File Structure

```
.
├── cog.yaml              # Cog configuration
├── predict.py            # Main prediction script
├── workflow_api.json     # ComfyUI workflow
└── README.md            # This file
```

## Resources

- Cog documentation: https://github.com/replicate/cog
- Replicate docs: https://replicate.com/docs
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- WanVideo: https://github.com/kijai/ComfyUI-WanVideoWrapper

## License

Check the licenses of the models you're using. WanVideo and related models may have specific usage restrictions.
