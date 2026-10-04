# LovyPC GUI v7 — Win95 Edition

Interfaccia grafica stile Windows 95 per [LovyPC](https://github.com/bitfarmy/LovyPC) — **connettore universale tra PC Windows e Fedora**.

## ⚠️ Sicurezza

**Tool locale senza autenticazione.** Il server gira su `127.0.0.1:8080` e non deve essere esposto su rete esterna.

## Installazione

```bash
cd lovypc-gui
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd backend
python server.py
```

Poi apri il browser su **http://localhost:8080**

## Per fermare

`Ctrl+C` nel terminale dove gira `server.py`

## Fix dalla review v6

| # | Problema | Soluzione |
|---|---|---|
| 🔴 | LED non aggiornati al primo giro | `await loadServices()` prima di `refreshStatus()` |
| 🟡 | `$HOME` non espanso in MOUNT_POINT | Campo readonly, escluso da save |
| 🟡 | Versioni disallineate (v3/v4/v6) | Allineate a v7 |

## API Backend

| Route | Metodo | Descrizione |
|---|---|---|
| `/api/health` | GET | Health check (versione, pcwin_found) |
| `/api/status` | GET | Stato completo (network, tunnels, mount) |
| `/api/services` | GET | Lista servizi da services.yaml |
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

## Struttura

```
lovypc-gui/
├── backend/
│   ├── server.py          # Flask API
│   └── services.yaml      # Definizione servizi
├── frontend/
│   ├── index.html         # Shell Win95 con tab
│   ├── css/win95.css      # Tema
│   └── js/app.js          # Logica dinamica
├── requirements.txt
└── README.md
```

## Licenza

MIT
