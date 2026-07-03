# Git2Modal Starter Templates

Ready-to-deploy Modal.com templates for the Git2Modal GitHub Action.
Each template is a complete, self-contained Modal app that you can deploy with a single `git push`.

## Available Templates

| Template | Description | Tech Stack |
|----------|-------------|------------|
| [`fastapi-web-app`](./fastapi-web-app/) | Production-ready FastAPI web service | FastAPI, Uvicorn |
| [`scheduled-cron`](./scheduled-cron/) | Serverless cron job with scheduled execution | Modal Scheduler |
| [`gpu-inference`](./gpu-inference/) | GPU-accelerated LLM inference endpoint | Transformers, PyTorch, FastAPI |

## How to Use

### Option 1: Use with Git2Modal Action

Add this workflow to your repo (`.github/workflows/deploy.yml`):

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
          deploy_path: templates/<template-name>
```

> **Note**: Replace `<template-name>` with `fastapi-web-app`, `scheduled-cron`, or `gpu-inference`.

### Option 2: Manual Deploy

```bash
cd templates/<template-name>
pip install modal
modal deploy app.py   # or cron.py, inference.py
```

### Option 3: Scaffold into Your Own Repo

Copy the template into your project:

```bash
cp -r templates/fastapi-web-app my-project/
cd my-project
# Customize app.py, then deploy
```

## Prerequisites

1. **Modal account** — Sign up at [modal.com](https://modal.com)
2. **Modal API tokens** — Create at [modal.com/settings/tokens](https://modal.com/settings/tokens)
3. **GitHub Secrets** — Add `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` to your repo

## Template Structure

Each template follows a consistent structure:

```
template-name/
├── README.md      # Template-specific docs
├── app.py         # Main Modal app file (or cron.py, inference.py)
└── requirements.txt  # (optional) Python dependencies
```

## Adding New Templates

To contribute a new template:

1. Create a new directory under `templates/`
2. Add a `README.md` with usage instructions
3. Add the Modal app file(s) with a clear `modal.App` definition
4. Follow the existing structure for consistency

---

Built with ❤️ by the Git2Modal team.