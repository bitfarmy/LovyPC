# LovyPC GUI — Architettura

## Missione
Connettore universale tra PC Windows e Fedora.
TramaMind è UN servizio tra i possibili, non LO scopo.

## Livelli

### L1 — System (sempre visibile)
- Network status (ping)
- Terminale remoto (SSH)
- Cartelle (mount/unmount SSHFS)
- Configurazione (IP, utente, cartella)

### L2 — Services (dinamico, da services.yaml)
- TramaMind: OmniRoute :20128 + OpenHands :3000
- Futuri: qualsiasi servizio con porta e comando pcwin

## File

```
lovypc-gui/
├── backend/
│   ├── server.py          # Flask API
│   └── services.yaml      # Definizione servizi
├── frontend/
│   ├── index.html         # Shell Win95
│   ├── css/win95.css      # Tema
│   └── js/app.js          # Logica dinamica
├── requirements.txt
└── README.md
```

## services.yaml

```yaml
services:
  tramamind:
    name: TramaMind
    description: IA personale multi-modello
    icon: "🧵"
    tunnels:
      - name: omniroute
        display: OmniRoute
        port: 20128
        pcwin_cmd: tramamind
        url: http://localhost:20128/v1
      - name: openhands
        display: OpenHands
        port: 3000
        pcwin_cmd: "tramamind ui"
        url: http://localhost:3000
```

## API Backend

| Route | Metodo | Descrizione |
|---|---|---|
| `/api/health` | GET | Health check (versione, pcwin_found) |
| `/api/status` | GET | Stato completo (network, tunnels, mount) |
| `/api/services` | GET | Lista servizi da services.yaml (solo campi pubblici) |
| `/api/config` | GET/POST | Leggi/Scrivi config (MOUNT_POINT readonly) |
| `/api/connect/<svc>/<tunnel>` | POST | Connetti tunnel specifico |
| `/api/disconnect/<svc>/<tunnel>` | POST | Disconnetti tunnel specifico |
| `/api/connect/service/<svc>` | POST | Connetti tutti i tunnel di un servizio |
| `/api/disconnect/service/<svc>` | POST | Disconnetti tutti i tunnel |
| `/api/mount` | POST | Monta cartelle via SSHFS |
| `/api/unmount` | POST | Smonta cartelle |
| `/api/open-terminal` | POST | Apre gnome-terminal con pcwin term |
| `/api/open-folder` | POST | Apre xdg-open sul mount point |
| `/api/auto/<svc>/<tunnel>/<action>` | POST | Abilita/disabilita avvio automatico |

## Note di design

- CORS ristretto a localhost:8080 e 127.0.0.1:8080
- Validazione input con regex `^[a-zA-Z0-9_-]+$` su service e tunnel
- Naming service systemd costruito da pcwin_cmd:
  - `"tramamind"` → `pcwin-tramamind.service`
  - `"tramamind ui"` → `pcwin-tramamind-ui.service`
- Config non distruttiva: preserva commenti e variabili non gestite
- Escaping Bash con apici singoli + `\''` per apici interni
- Nessuna autenticazione: tool locale, gira su 127.0.0.1 soltanto
