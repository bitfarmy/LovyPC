# LovyPC — Connettore universale PC Windows ↔ Fedora

LovyPC collega il tuo PC Windows alla tua Fedora: terminale remoto, cartelle
montate via SSHFS e tunnel SSH per i tuoi servizi (TramaMind/OmniRoute,
OpenHands, Ollama e qualunque altro servizio futuro).

Composto da due componenti:

| Componente | Descrizione |
|---|---|
| **`pcwin`** | CLI bash — terminale, mount, tunnel, service systemd |
| **`gui/`** | GUI web stile Win95 (Flask) — tab SYSTEM / SERVICES / CONFIG / LOGS |

## Installazione CLI

```bash
sudo cp pcwin /usr/local/bin/ && sudo chmod +x /usr/local/bin/pcwin
mkdir -p ~/.config && cp pcwin.conf.example ~/.config/pcwin.conf
# Modifica WIN_USER, WIN_IP, WIN_FOLDER in ~/.config/pcwin.conf
```

## Comandi pcwin

```bash
pcwin term              # SSH PowerShell remoto
pcwin cmd               # SSH cmd.exe
pcwin monta             # Mount SSHFS in ~/pc-windows
pcwin smonta            # Unmount
pcwin tramamind         # Tunnel → OmniRoute :20128
pcwin tramamind ui      # Tunnel → OpenHands :3000
pcwin ollama            # Tunnel → Ollama :11434 (debug)
pcwin tramamind stop    # Ferma tunnel
pcwin tramamind auto    # Avvio automatico (systemd user)
pcwin status            # Panoramica
pcwin installa-service  # Crea i service systemd user
```

## GUI (gui/)

```bash
cd gui
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd backend && python server.py
```

Poi apri **http://localhost:8080**

> ⚠️ **Sicurezza**: la GUI è un tool locale senza autenticazione.
> Gira solo su `127.0.0.1:8080` — non esporla su rete esterna.

## Aggiungere un servizio

Modifica `gui/backend/services.yaml` aggiungendo un blocco — la GUI lo
rileva automaticamente al prossimo refresh, senza toccare codice. Vedi i
commenti nel file per la sintassi e il naming dei service systemd.

## Struttura del repo

```
LovyPC/
├── pcwin                  # CLI bash
├── pcwin.conf.example     # Config di esempio
├── pcwin.desktop          # Launcher desktop
├── gui/                   # GUI web (Flask + Win95)
│   ├── backend/           # server.py + services.yaml
│   ├── frontend/          # index.html, css/, js/
│   └── requirements.txt
├── ARCHITECTURE.md        # Architettura e API backend
├── CHANGELOG.md
└── LICENSE                # MIT
```

## Licenza

MIT — vedi [LICENSE](LICENSE)
