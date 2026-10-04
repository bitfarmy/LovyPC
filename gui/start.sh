#!/usr/bin/env bash
# LovyPC GUI — Avvio in un comando
# Uso: ./start.sh   (oppure: bash start.sh)
set -e

GUI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$GUI_DIR")"

echo "╔══════════════════════════════════════════╗"
echo "║     LovyPC GUI — Avvio                   ║"
echo "╚══════════════════════════════════════════╝"

# 1. pcwin: sincronizza SEMPRE la copia del repo in ~/.local/bin
#    (~/.local/bin ha precedenza sul PATH → niente sudo, aggiornamenti automatici)
if [ -f "$REPO_DIR/pcwin" ]; then
    mkdir -p "$HOME/.local/bin"
    if ! cmp -s "$REPO_DIR/pcwin" "$HOME/.local/bin/pcwin" 2>/dev/null; then
        cp "$REPO_DIR/pcwin" "$HOME/.local/bin/pcwin"
        chmod +x "$HOME/.local/bin/pcwin"
        echo "[OK] pcwin aggiornato in ~/.local/bin"
    else
        echo "[OK] pcwin aggiornato (~/.local/bin)"
    fi
else
    echo "[WARN] pcwin non trovato nel repo"
fi
export PATH="$HOME/.local/bin:$PATH"

# 2. venv: lo creiamo se manca
if [ ! -d "$GUI_DIR/venv" ]; then
    echo "[..] Creazione ambiente virtuale..."
    python3 -m venv "$GUI_DIR/venv"
fi

# 3. dipendenze: installate se mancano
if ! "$GUI_DIR/venv/bin/python" -c "import flask, flask_cors, yaml" &>/dev/null; then
    echo "[..] Installazione dipendenze..."
    "$GUI_DIR/venv/bin/pip" install -q -r "$GUI_DIR/requirements.txt"
fi

# 4. avvia il server
echo "[OK] Avvio GUI su http://localhost:8080"
cd "$GUI_DIR/backend"
exec "$GUI_DIR/venv/bin/python" server.py
