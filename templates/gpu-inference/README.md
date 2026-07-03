# GPU Inference Endpoint on Modal

Serve an AI model with GPU acceleration on Modal.com.
Deploy with a single `git push` using the Git2Modal GitHub Action.

## Quick Start

1. **Set up Modal secrets** in your GitHub repo:
   - `MODAL_TOKEN_ID`
   - `MODAL_TOKEN_SECRET`

2. **Add the Git2Modal Action** to your workflow:

   ```yaml
   name: Deploy to Modal
   on: [push]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: git2modal/action@v1
           with:
             modal_token_id: ${{ secrets.MODAL_TOKEN_ID }}
             modal_token_secret: ${{ secrets.MODAL_TOKEN_SECRET }}
             deploy_path: templates/gpu-inference
   ```

3. **Push to GitHub** — your GPU inference endpoint goes live.

## Local Testing

```bash
pip install modal
modal run inference.py --prompt "Hello, world!"
```

## Customization

- Change the model in `MODEL_NAME` (supports any HuggingFace model)
- Adjust `gpu` type (A10G, A100, T4) and count
- Modify the system prompt for different use cases

## Available Endpoints

- `GET /` — Health check
- `POST /generate` — Generate text from a prompt
- `POST /chat` — Chat completion with conversation history