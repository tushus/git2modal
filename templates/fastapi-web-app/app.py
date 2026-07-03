"""
FastAPI Web App — Git2Modal Starter Template

Deploy a FastAPI web service to Modal.com with git push.

Usage:
    modal run app.py         # local dev
    modal deploy app.py      # manual deploy
"""

from pathlib import Path

import fastapi
import modal

# Create a Modal App
app = modal.App("git2modal-fastapi-webapp")

# Define the container image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.0.0",
    )
)

# The ASGI mount point — FastAPI app lives here
web_app = fastapi.FastAPI(
    title="Git2Modal FastAPI",
    description="Deployed automatically via Git2Modal GitHub Action",
    version="1.0.0",
)


@web_app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Git2Modal FastAPI Starter",
        "message": "Your app is live on Modal!",
    }


@web_app.get("/health")
async def health():
    return {"status": "healthy"}


@app.function(image=image, keep_warm=1)
@modal.asgi_app()
def fastapi_app():
    return web_app