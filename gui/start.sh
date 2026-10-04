#!/usr/bin/env bash
# LovyPC GUI — Avvio in un comando
# Uso: ./start.sh   (oppure: bash start.sh)
set -e

GUI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$GUI_DIR")"

# --install-icon: installa il launcher nel menu Applicazioni di Fedora
if [ "$1" = "--install-icon" ]; then
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/lovypc-gui.desktop" <<EOF
[Desktop Entry]
Name=LovyPC GUI
Comment=Connettore universale PC Windows ↔ Fedora — GUI Win95
Exec=bash -c "nohup $GUI_DIR/start.sh >/dev/null 2>&1 &"
Icon=computer
Terminal=false
Type=Application
Categories=Utility;Network;
Keywords=windows;ssh;tunnel;lovypc;pcwin;
EOF
    echo "[OK] Icona installata: la trovi nel menu Applicazioni come 'LovyPC GUI'"
    echo "     (se sposti la cartella del repo, rilancia: bash gui/start.sh --install-icon)"
    exit 0
fi

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

# 1b. Icona nel menu Applicazioni: installata/aggiornata automaticamente
DESKTOP_FILE="$HOME/.local/share/applications/lovypc-gui.desktop"
DESKTOP_CONTENT="[Desktop Entry]
Name=LovyPC GUI
Comment=Connettore universale PC Windows ↔ Fedora — GUI Win95
Exec=bash -c \"$GUI_DIR/start.sh\"
Icon=computer
Terminal=false
Type=Application
Categories=Utility;Network;
Keywords=windows;ssh;tunnel;lovypc;pcwin;"
if [ ! -f "$DESKTOP_FILE" ] || ! cmp -s <(printf '%s\n' "$DESKTOP_CONTENT") "$DESKTOP_FILE" 2>/dev/null; then
    mkdir -p "$HOME/.local/share/applications"
    printf '%s\n' "$DESKTOP_CONTENT" > "$DESKTOP_FILE"
    echo "[OK] Icona nel menu Applicazioni installata"
fi

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

# 4. se il server gira già, apri solo il browser e basta
if curl -sf http://localhost:8080/api/health >/dev/null 2>&1; then
    echo "[OK] GUI già attiva su http://localhost:8080 — apertura browser"
    xdg-open http://localhost:8080 >/dev/null 2>&1
    exit 0
fi

# 5. avvia il server (e apri il browser dopo 2s)
echo "[OK] Avvio GUI su http://localhost:8080"
( sleep 2; xdg-open http://localhost:8080 >/dev/null 2>&1 ) &
cd "$GUI_DIR/backend"
exec "$GUI_DIR/venv/bin/python" server.py
