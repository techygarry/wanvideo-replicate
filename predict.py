import os
import sys
import json
import uuid
import shutil
import random
from typing import Any, Optional
from cog import BasePredictor, Input, Path

sys.path.append('/ComfyUI')

import execution
import server
from nodes import NODE_CLASS_MAPPINGS, init_custom_nodes
import folder_paths


class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        self.comfy_dir = "/ComfyUI"
        self.output_dir = os.path.join(self.comfy_dir, "output")
        self.input_dir = os.path.join(self.comfy_dir, "input")

        # Initialize custom nodes
        init_custom_nodes()

        # Download required models (you'll need to add your model URLs here)
        # Example model downloads - UPDATE THESE WITH YOUR ACTUAL MODEL URLS
        models = {
            # Main model
            "Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors": {
                "url": "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors",
                "dest": "/ComfyUI/models/checkpoints/Wan2_1-I2V-14B-480P_fp8_e4m3fn.safetensors"
            },
            # LoRA
            "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors": {
                "url": "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
                "dest": "/ComfyUI/models/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors"
            },
            # MultiTalk model
            "Wan2_1-InfiniTetalk-Single_fp16.safetensors": {
                "url": "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors",
                "dest": "/ComfyUI/models/checkpoints/Wan2_1-InfiniTetalk-Single_fp16.safetensors"
            },
            # CLIP Vision
            "clip_vision_h.safetensors": {
                "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
                "dest": "/ComfyUI/models/clip_vision/clip_vision_h.safetensors"
            },
            # Text encoder
            "umt5_xxl_fp16.safetensors": {
                "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp16.safetensors",
                "dest": "/ComfyUI/models/text_encoders/umt5_xxl_fp16.safetensors"
            },
            # VAE
            "wan_2.1_vae.safetensors": {
                "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
                "dest": "/ComfyUI/models/vae/wan_2.1_vae.safetensors"
            },
            # Wav2Vec
            "wav2vec2-chinese-base_fp16.safetensors": {
                "url": "https://huggingface.co/Kijai/wav2vec2_safetensors/resolve/main/wav2vec2-chinese-base_fp16.safetensors",
                "dest": "/ComfyUI/models/audio/wav2vec2-chinese-base_fp16.safetensors"
            }
        }

        # Download models when container starts
        for model_name, model_info in models.items():
            self.download_weights(model_info["url"], model_info["dest"])

    def download_weights(self, url: str, dest: str):
        """Download model weights if not already present"""
        if not os.path.exists(dest):
            print(f"Downloading {url} to {dest}")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.system(f"pget {url} {dest}")

    def predict(
        self,
        input_image: Path = Input(
            description="Input image for video generation"
        ),
        audio_file: Path = Input(
            description="Audio file for lip sync (MP3 or WAV)",
            default=None
        ),
        prompt: str = Input(
            description="Text prompt describing the video",
            default="a person is speaking with gestures and emotions"
        ),
        negative_prompt: str = Input(
            description="Negative prompt",
            default="bright tones, overexposed, static, blurred details, worst quality, low quality"
        ),
        num_frames: int = Input(
            description="Number of frames to generate",
            default=100,
            ge=1,
            le=1000
        ),
        fps: int = Input(
            description="Frames per second",
            default=25,
            ge=10,
            le=60
        ),
        steps: int = Input(
            description="Number of sampling steps",
            default=6,
            ge=1,
            le=50
        ),
        cfg_scale: float = Input(
            description="CFG Scale",
            default=1.0,
            ge=0.1,
            le=20.0
        ),
        seed: int = Input(
            description="Random seed. Set to -1 for random",
            default=-1
        ),
    ) -> Path:
        """Run a single prediction on the model"""

        # Set random seed
        if seed == -1:
            seed = random.randint(0, 2**32 - 1)

        # Load the workflow
        with open('workflow_api.json', 'r') as f:
            workflow = json.load(f)

        # Copy input image to ComfyUI input directory
        image_filename = f"input_{uuid.uuid4().hex}.webp"
        image_path = os.path.join(self.input_dir, image_filename)
        shutil.copy(str(input_image), image_path)

        # Copy audio file if provided
        if audio_file:
            audio_ext = os.path.splitext(str(audio_file))[1]
            audio_filename = f"input_{uuid.uuid4().hex}{audio_ext}"
            audio_path = os.path.join(self.input_dir, audio_filename)
            shutil.copy(str(audio_file), audio_path)
        else:
            # Use default audio from workflow
            audio_filename = workflow["19"]["inputs"]["audio"]

        # Update workflow with user inputs
        # Update image (node 12)
        workflow["12"]["inputs"]["image"] = image_filename

        # Update audio (node 19)
        workflow["19"]["inputs"]["audio"] = audio_filename

        # Update prompts (node 17)
        workflow["17"]["inputs"]["positive_prompt"] = prompt
        workflow["17"]["inputs"]["negative_prompt"] = negative_prompt

        # Update sampling parameters (node 16)
        workflow["16"]["inputs"]["seed"] = seed
        workflow["16"]["inputs"]["steps"] = steps
        workflow["16"]["inputs"]["cfg"] = cfg_scale

        # Update num_frames and fps (node 18)
        workflow["18"]["inputs"]["num_frames"] = num_frames
        workflow["18"]["inputs"]["fps"] = fps

        # Update video output fps (node 23)
        workflow["23"]["inputs"]["frame_rate"] = fps

        # Clear previous outputs
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass

        # Execute the workflow
        output_path = self.execute_workflow(workflow)

        if not output_path:
            raise Exception("No output video generated")

        return Path(output_path)

    def execute_workflow(self, workflow: dict) -> str:
        """Execute ComfyUI workflow and return output video path"""

        # Validate the workflow
        prompt_id = str(uuid.uuid4())

        outputs_to_execute = []
        for node_id in workflow:
            outputs_to_execute.append(node_id)

        try:
            # Execute the prompt using ComfyUI's execution system
            executor = execution.PromptExecutor(server.PromptServer(None))

            # Run the execution
            executor.execute(workflow, prompt_id, {}, outputs_to_execute)

            # Wait a bit for files to be written
            import time
            time.sleep(2)

            # Find the output video
            output_files = []
            for file in os.listdir(self.output_dir):
                if file.endswith(('.mp4', '.avi', '.mov', '.webm')):
                    output_files.append(os.path.join(self.output_dir, file))

            if not output_files:
                raise Exception("No output video found")

            # Return the most recent file
            return sorted(output_files, key=os.path.getmtime, reverse=True)[0]

        except Exception as e:
            raise Exception(f"Error executing workflow: {str(e)}")
