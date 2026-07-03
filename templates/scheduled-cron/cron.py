"""
Scheduled Cron Job — Git2Modal Starter Template

A Modal cron job that runs periodically. Perfect for:
  - Data pipelines and ETL jobs
  - Model retraining
  - Slack/email notifications
  - Database maintenance

Usage:
    modal run cron.py          # run once (local test)
    modal deploy cron.py       # deploy with schedule
"""

import json
from datetime import datetime, timezone

import modal

# Create Modal App
app = modal.App("git2modal-scheduled-cron")

# Define image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("requests>=2.31.0", "httpx>=0.27.0")
)


@app.function(
    image=image,
    schedule=modal.Period(hours=1),  # Runs every hour
    secrets=[modal.Secret.from_name("my-secrets", required=False)],
)
def scheduled_task():
    """
    Your scheduled job logic goes here.
    Currently logs a timestamp — replace with your own logic.
    """
    now = datetime.now(timezone.utc)
    message = {
        "status": "completed",
        "timestamp": now.isoformat(),
        "task": "git2modal-scheduled-cron",
        "message": "Cron job executed successfully.",
    }
    print(json.dumps(message, indent=2))
    return message


# Also expose an option to run it manually (for testing)
@app.local_entrypoint()
def main():
    print("🧪 Running scheduled_task locally (one-shot)...")
    result = scheduled_task.remote()
    print(f"✅ Result: {result}")