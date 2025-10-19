# Complete Deployment Guide for Replicate

## Step 1: Upload Your Model Files to HuggingFace

You need to host your model files online. HuggingFace is the easiest option.

### 1.1 Create HuggingFace Account
- Go to https://huggingface.co/join
- Create an account (free)

### 1.2 Create a Model Repository
- Go to https://huggingface.co/new
- Choose "Model" repository
- Name it something like `wanvideo-models`
- Set it to **Public** (important for Replicate to download)
- Click "Create repository"

### 1.3 Upload Your Model Files
You have two options:

**Option A: Web Interface (Easier for beginners)**
1. Click "Files and versions" tab
2. Click "Add file" → "Upload files"
3. Upload these 7 files:
   - `Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors`
   - `lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors`
   - `Wan2_1-InfiniTetalk-Single_fp16.safetensors`
   - `clip_vision_h.safetensors`
   - `umt5_xxl_fp16.safetensors`
   - `wan_2.1_vae.safetensors`
   - `wav2vec2-chinese-base_fp16.safetensors`
4. Wait for upload to complete

**Option B: Git LFS (Recommended for large files)**
```bash
# Install Git LFS
git lfs install

# Clone your repo
git clone https://huggingface.co/YOUR_USERNAME/wanvideo-models
cd wanvideo-models

# Copy your model files here
# Then commit and push
git lfs track "*.safetensors"
git add .gitattributes
git add *.safetensors
git commit -m "Add model files"
git push
```

### 1.4 Get Direct Download URLs
After upload, each file will have a URL like:
```
https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/FILENAME.safetensors
```

For example:
```
https://huggingface.co/john/wanvideo-models/resolve/main/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors
```

---

## Step 2: Update predict.py with Model URLs

Open `predict.py` and find lines 30-66. Replace the placeholder URLs:

### BEFORE:
```python
models = {
    "Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors": {
        "url": "YOUR_MODEL_URL_HERE",
        "dest": "/ComfyUI/models/checkpoints/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors"
    },
    # ... etc
}

# Uncomment this when you have your model URLs
# for model_name, model_info in models.items():
#     self.download_weights(model_info["url"], model_info["dest"])
```

### AFTER (with your actual URLs):
```python
models = {
    "Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors",
        "dest": "/ComfyUI/models/checkpoints/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors"
    },
    "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
        "dest": "/ComfyUI/models/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors"
    },
    "Wan2_1-InfiniTetalk-Single_fp16.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/Wan2_1-InfiniTetalk-Single_fp16.safetensors",
        "dest": "/ComfyUI/models/checkpoints/Wan2_1-InfiniTetalk-Single_fp16.safetensors"
    },
    "clip_vision_h.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/clip_vision_h.safetensors",
        "dest": "/ComfyUI/models/clip_vision/clip_vision_h.safetensors"
    },
    "umt5_xxl_fp16.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/umt5_xxl_fp16.safetensors",
        "dest": "/ComfyUI/models/text_encoders/umt5_xxl_fp16.safetensors"
    },
    "wan_2.1_vae.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/wan_2.1_vae.safetensors",
        "dest": "/ComfyUI/models/vae/wan_2.1_vae.safetensors"
    },
    "wav2vec2-chinese-base_fp16.safetensors": {
        "url": "https://huggingface.co/YOUR_USERNAME/wanvideo-models/resolve/main/wav2vec2-chinese-base_fp16.safetensors",
        "dest": "/ComfyUI/models/audio/wav2vec2-chinese-base_fp16.safetensors"
    }
}

# IMPORTANT: Remove the comment marks below!
for model_name, model_info in models.items():
    self.download_weights(model_info["url"], model_info["dest"])
```

**Important:** Replace `YOUR_USERNAME` with your actual HuggingFace username!

---

## Step 3: Install Cog (if not already installed)

### On macOS/Linux:
```bash
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
sudo chmod +x /usr/local/bin/cog
```

### On Windows:
Download from: https://github.com/replicate/cog/releases/latest
Or use WSL2 (recommended)

### Verify installation:
```bash
cog --version
```

---

## Step 4: Build Docker Image Locally (Optional but Recommended)

Test that everything builds correctly:

```bash
cd C:\Users\User\repli
cog build
```

This will:
- Take 15-30 minutes (it's downloading ComfyUI, dependencies, etc.)
- Download all your models from HuggingFace
- Create a Docker image

**If build fails:**
- Check error messages carefully
- Most common issues:
  - Model URLs are not publicly accessible
  - Internet connection issues
  - Docker not running

---

## Step 5: Push to Replicate

### 5.1 Create Replicate Account
- Go to https://replicate.com
- Sign up (free tier available)
- Go to Account Settings → API Tokens
- Copy your API token

### 5.2 Login to Cog
```bash
cog login
```
Paste your API token when prompted

### 5.3 Create Model on Replicate
Go to https://replicate.com/create and:
- Choose a model name (e.g., `wanvideo-i2v`)
- Choose visibility (Public or Private)
- Click "Create model"

### 5.4 Push to Replicate
```bash
cog push r8.im/YOUR_REPLICATE_USERNAME/wanvideo-i2v
```

Replace `YOUR_REPLICATE_USERNAME` with your actual Replicate username.

This will:
- Build the Docker image (if not already built)
- Upload to Replicate
- Create a new model version
- Take 30-60 minutes (uploading large Docker image)

**Output will look like:**
```
Building Docker image...
Pushing image to r8.im...
Pushed https://replicate.com/YOUR_USERNAME/wanvideo-i2v
```

---

## Step 6: Test Your Model on Replicate

### Via Web Interface:
1. Go to https://replicate.com/YOUR_USERNAME/wanvideo-i2v
2. Click on the latest version
3. Upload an image
4. Upload an audio file
5. Click "Run"

### Via API (Python):
```python
import replicate

output = replicate.run(
    "YOUR_USERNAME/wanvideo-i2v:VERSION_ID",
    input={
        "input_image": open("test_image.jpg", "rb"),
        "audio_file": open("test_audio.mp3", "rb"),
        "prompt": "a person speaking with emotions",
        "num_frames": 50,  # Start with fewer frames for faster testing
        "fps": 25,
        "steps": 6,
        "seed": -1
    }
)

# Download the video
import urllib.request
urllib.request.urlretrieve(output, "output.mp4")
print("Video saved as output.mp4")
```

### Via API (cURL):
```bash
curl -X POST https://api.replicate.com/v1/predictions \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "YOUR_MODEL_VERSION_ID",
    "input": {
      "input_image": "https://url-to-your-test-image.jpg",
      "audio_file": "https://url-to-your-test-audio.mp3",
      "prompt": "a person speaking",
      "num_frames": 50
    }
  }'
```

---

## Quick Reference: Model URL Format

Replace in predict.py (lines 32-64):

```
YOUR_MODEL_URL_HERE → https://huggingface.co/YOUR_HF_USERNAME/REPO_NAME/resolve/main/FILENAME.safetensors
```

Example:
- HuggingFace username: `john`
- Repo name: `wanvideo-models`
- File: `clip_vision_h.safetensors`
- URL: `https://huggingface.co/john/wanvideo-models/resolve/main/clip_vision_h.safetensors`

---

## Troubleshooting

### Build fails with "connection timeout"
- Your model files are too large and HuggingFace is timing out
- Solution: Use a different hosting (AWS S3, Google Cloud Storage)

### "Model not found" during build
- Check that your HuggingFace repo is **Public**, not Private
- Verify URLs are correct (copy-paste from HuggingFace)

### Build succeeds but prediction fails
- Check Replicate logs (on the prediction page)
- Common issue: Missing custom nodes or wrong node IDs in workflow

### "Out of memory" during prediction
- Your workflow might be too large for Replicate's GPU
- Solution: Use `force_offload: true` in workflow (already set)

---

## Cost Estimation

Replicate charges based on GPU time:
- Cold start: ~2-3 minutes (downloading models)
- Per prediction: ~30 seconds to 2 minutes depending on num_frames
- GPU cost: ~$0.0002-0.0005 per second

For 100 predictions/month with avg 1 min each:
- Cost: ~$1.20-3.00/month

---

## Next Steps After Deployment

1. **Test thoroughly** with different images/audio
2. **Monitor costs** in Replicate dashboard
3. **Optimize** by caching models or using smaller variants
4. **Integrate** into your app using the API

Need help? Check:
- Replicate Discord: https://discord.gg/replicate
- Cog GitHub Issues: https://github.com/replicate/cog/issues
