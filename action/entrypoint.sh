#!/bin/bash
# entrypoint.sh — Git2Modal GitHub Action Entrypoint
#
# This script receives inputs from action.yml, sets up Modal credentials,
# and runs `modal deploy` on the specified path.

set -euo pipefail

# ── Inputs ──────────────────────────────────────────────────────────────
MODAL_TOKEN_ID="${1}"
MODAL_TOKEN_SECRET="${2}"
DEPLOY_PATH="${3:-.}"
APP_NAME="${4:-}"
MODAL_ARGS="${5:-}"
PYTHON_VERSION="${6:-3.11}"
WORKING_DIRECTORY="${7:-.}"

echo "=============================================="
echo " 🚀 Git2Modal — Deploy to Modal.com"
echo "=============================================="
echo "Working directory : ${WORKING_DIRECTORY}"
echo "Deploy path       : ${DEPLOY_PATH}"
echo "App name          : ${APP_NAME:-<auto>}"
echo "Modal args        : ${MODAL_ARGS:-<none>}"
echo "Python version    : ${PYTHON_VERSION}"
echo "=============================================="

# ── Set Modal credentials ──────────────────────────────────────────────
export MODAL_TOKEN_ID="${MODAL_TOKEN_ID}"
export MODAL_TOKEN_SECRET="${MODAL_TOKEN_SECRET}"

# ── Change to working directory ───────────────────────────────────────
cd "${GITHUB_WORKSPACE}/${WORKING_DIRECTORY}"

# ── Validate deploy path exists ───────────────────────────────────────
if [ ! -d "${DEPLOY_PATH}" ] && [ ! -f "${DEPLOY_PATH}" ]; then
    echo "❌ ERROR: Deploy path '${DEPLOY_PATH}' does not exist."
    echo "   Check that your 'deploy_path' input is correct."
    exit 1
fi

# ── Authenticate with Modal ────────────────────────────────────────────
echo "🔑 Authenticating with Modal..."
python3 /modal_deploy.py auth
echo "✅ Authentication successful."

# ── Determine what to deploy ──────────────────────────────────────────
if [ -d "${DEPLOY_PATH}" ]; then
    # If it's a directory, find all .py files and deploy the whole dir
    echo "📁 Deploying directory: ${DEPLOY_PATH}"
    TARGET="${DEPLOY_PATH}"
else
    TARGET="${DEPLOY_PATH}"
fi

# ── Build the deploy command ──────────────────────────────────────────
DEPLOY_CMD="modal deploy"

if [ -n "${APP_NAME}" ]; then
    DEPLOY_CMD="${DEPLOY_CMD} --name ${APP_NAME}"
fi

if [ -n "${MODAL_ARGS}" ]; then
    DEPLOY_CMD="${DEPLOY_CMD} ${MODAL_ARGS}"
fi

DEPLOY_CMD="${DEPLOY_CMD} ${TARGET}"

echo "⚙️  Running: ${DEPLOY_CMD}"

# ── Execute deploy ────────────────────────────────────────────────────
OUTPUT=""
if OUTPUT=$(eval "${DEPLOY_CMD}" 2>&1); then
    echo "✅ Deploy succeeded!"
    echo "${OUTPUT}"

    # Extract deployment URL from output if possible
    DEPLOYMENT_URL=$(echo "${OUTPUT}" | grep -oP 'https?://[^\s]+' | head -1 || true)
    if [ -n "${DEPLOYMENT_URL}" ]; then
        echo "deployment_url=${DEPLOYMENT_URL}" >> "${GITHUB_OUTPUT}"
        echo "🔗 Deployment URL: ${DEPLOYMENT_URL}"
    fi

    echo "deployment_status=success" >> "${GITHUB_OUTPUT}"
else
    EXIT_CODE=$?
    echo "❌ Deploy failed (exit code ${EXIT_CODE})"
    echo "${OUTPUT}"
    echo "deployment_status=failure" >> "${GITHUB_OUTPUT}"
    exit "${EXIT_CODE}"
fi