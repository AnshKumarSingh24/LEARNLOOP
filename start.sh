#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  start.sh — Starts both servers for captureinprog-main 2 copy
# ═══════════════════════════════════════════════════════════════
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
NODE_BIN="$HOME/.nvm/versions/node/v20.20.2/bin"
OLD_VENV="$HOME/Downloads/captureinprog-main 2/capture_api/venv"
PYTHON="$OLD_VENV/bin/python"

echo "🔧 Starting Darwinity dev servers..."
echo "   Repo: $REPO_DIR"

# ── Kill any stale processes on our ports ────────────────────
echo "🧹 Cleaning up stale processes..."
for PORT in 3000 3001 3002 8080; do
  PID=$(lsof -ti :$PORT 2>/dev/null) && kill $PID 2>/dev/null && echo "  Killed process on port $PORT" || true
done
sleep 1

# ── Start Python capture_api on port 8080 ───────────────────
echo "🐍 Starting capture_api on port 8080..."
cd "$REPO_DIR/capture_api"
"$PYTHON" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload > "$REPO_DIR/.logs/capture_api.log" 2>&1 &
PYTHON_PID=$!
echo "  PID: $PYTHON_PID"

# ── Start Node.js frontend on port 3000 ─────────────────────
echo "🟢 Starting frontend on port 3000..."
cd "$REPO_DIR/frontend"
"$NODE_BIN/node" --require node_modules/tsx/dist/preflight.cjs \
  --import "file://$(pwd)/node_modules/tsx/dist/loader.mjs" \
  server/_core/index.ts --port 3000 > "$REPO_DIR/.logs/frontend.log" 2>&1 &
NODE_PID=$!
echo "  PID: $NODE_PID"

mkdir -p "$REPO_DIR/.logs"

# ── Wait for both to start ───────────────────────────────────
echo "⏳ Waiting for servers to start..."
sleep 4

# Check health
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
  echo "✅ capture_api running → http://localhost:8080"
else
  echo "❌ capture_api failed to start - check .logs/capture_api.log"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null | grep -q "200\|304"; then
  echo "✅ Frontend running  → http://localhost:3000"
else
  echo "⏳ Frontend still starting... check .logs/frontend.log"
fi

echo ""
echo "🚀 Dev environment ready!"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:8080"
echo "   Logs:     .logs/capture_api.log  |  .logs/frontend.log"
