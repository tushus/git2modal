"""
GPU Inference Endpoint — Git2Modal Starter Template

Serve an LLM (or any AI model) with GPU acceleration on Modal.
Exposes a FastAPI web endpoint for text generation.

Usage:
    modal run inference.py                       # local test (CLI)
    modal deploy inference.py                    # manual deploy

Example API call after deploy:
    curl -X POST <DEPLOY_URL>/generate \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Hello, how are you?", "max_tokens": 100}'
"""

import fastapi
import modal

# ── Configuration ───────────────────────────────────────────────────────
MODEL_NAME = "microsoft/phi-3-mini-4k-instruct"  # Small, fast, permissive
GPU_CONFIG = modal.gpu.A10G()                     # Change to A100 for bigger models

# ── Modal App ──────────────────────────────────────────────────────────
app = modal.App("git2modal-gpu-inference")

# ── Container Image ────────────────────────────────────────────────────
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "torch>=2.3.0",
        "transformers>=4.43.0",
        "accelerate>=0.30.0",
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.0.0",
    )
)

# ── FastAPI Setup ──────────────────────────────────────────────────────
web_app = fastapi.FastAPI(
    title="Git2Modal GPU Inference",
    description="GPU-accelerated LLM inference via Modal",
    version="1.0.0",
)


# ── Model Volume (cache the model weights across deployments) ──────────
model_volume = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
HUGGINGFACE_CACHE = "/root/.cache/huggingface"


# ── Model Loading (cold start) ─────────────────────────────────────────
@app.cls(
    image=image,
    gpu=GPU_CONFIG,
    timeout=300,
    allow_concurrent_inputs=4,
    container_idle_timeout=300,
    volumes={HUGGINGFACE_CACHE: model_volume},
    secrets=[modal.Secret.from_name("huggingface-token", required=False)],
)
class InferenceModel:
    @modal.build()
    def download_model(self):
        """Download model weights at build time for faster cold starts."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        token = None
        AutoTokenizer.from_pretrained(MODEL_NAME, token=token)
        AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            token=token,
        )

    @modal.enter()
    def load_model(self):
        """Load model into memory when a container starts."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7):
        """Generate text from a prompt."""
        import torch

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


# ── API Routes ─────────────────────────────────────────────────────────

@web_app.get("/")
async def root():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "gpu": str(GPU_CONFIG),
        "endpoints": {"/generate": "POST", "/chat": "POST"},
    }


@web_app.post("/generate")
async def generate(prompt: str = "Hello!", max_tokens: int = 200, temperature: float = 0.7):
    model = InferenceModel()
    result = model.generate.remote(prompt, max_tokens, temperature)
    return {"prompt": prompt, "result": result}


@web_app.post("/chat")
async def chat(messages: list[dict], max_tokens: int = 200, temperature: float = 0.7):
    """Chat completion with conversation history.
    Messages format: [{"role": "user", "content": "..."}, ...]
    """
    import transformers

    # Format conversation using the model's chat template
    formatted = transformers.tokenization_utils_base.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    model = InferenceModel()
    result = model.generate.remote(formatted, max_tokens, temperature)
    return {"result": result}


# ── ASGI entrypoint ────────────────────────────────────────────────────
@app.function(
    image=image,
    gpu=GPU_CONFIG,
    keep_warm=1,
    container_idle_timeout=300,
    allow_concurrent_inputs=4,
    timeout=600,
    volumes={HUGGINGFACE_CACHE: model_volume},
)
@modal.asgi_app()
def serve():
    return web_app


# ── CLI test entrypoint ────────────────────────────────────────────────
@app.local_entrypoint()
def main(prompt: str = "Write a short poem about serverless computing."):
    model = InferenceModel()
    result = model.generate.remote(prompt)
    print(f"\n📝 Prompt: {prompt}\n")
    print(f"✅ Response:\n{result}\n")