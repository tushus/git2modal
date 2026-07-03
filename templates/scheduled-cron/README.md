# Scheduled Cron Job on Modal

A serverless cron job that runs on a schedule using Modal's `@app.function(schedule=...)` decorator.
Deploy with a single `git push` using the Git2Modal GitHub Action.

## Quick Start

1. **Set up Modal secrets** in your GitHub repo:
   - `MODAL_TOKEN_ID`
   - `MODAL_TOKEN_SECRET`

2. **Add the Git2Modal Action** to your workflow (`.github/workflows/deploy.yml`):

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
             deploy_path: templates/scheduled-cron
   ```

3. **Push to GitHub** — your cron job deploys and runs on schedule.

## Local Development

```bash
pip install modal
modal run cron.py
```

## Customization

Edit the `schedule` parameter in `cron.py` to change the interval.
Available schedules: `modal.Period(days=1)`, `modal.Cron("0 9 * * *")`, etc.