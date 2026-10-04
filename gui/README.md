# LovyPC GUI v7 — Win95 Edition

Interfaccia grafica stile Windows 95 per [LovyPC](../README.md) — **connettore universale tra PC Windows e Fedora**.

## ⚠️ Sicurezza

**Tool locale senza autenticazione.** Il server gira su `127.0.0.1:8080` e non deve essere esposto su rete esterna.

## Installazione

```bash
cd gui
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd backend
python server.py
```

Poi apri il browser su **http://localhost:8080**

Per fermare: `Ctrl+C` nel terminale dove gira `server.py`

## Tab

| Tab | Contenuto |
|---|---|
| SYSTEM | Network LED, mount LED, terminale, mount/unmount, refresh |
| SERVICES | Card dinamiche da `services.yaml` (CONNECT/DISCONNECT per tunnel o per intero servizio) |
| CONFIG | WIN_USER, WIN_IP, WIN_FOLDER (MOUNT_POINT readonly) |
| LOGS | Log operazioni frontend |

## Aggiungere un servizio

Modifica `backend/services.yaml`:

```yaml
services:
  mioservizio:
    name: Mio Servizio
    description: Cosa fa
    icon: "🚀"
    tunnels:
      - name: main
        display: Main
        port: 8080
        pcwin_cmd: "custom tunnel command"   # eseguito come: pcwin <cmd> [stop|auto|noauto]
        url: http://localhost:8080
```

- Il nome del service systemd è costruito da `pcwin_cmd`:
  `"tramamind"` → `pcwin-tramamind.service`, `"tramamind ui"` → `pcwin-tramamind-ui.service`
- Il frontend lo renderizza automaticamente al prossimo polling

## Novità in v7.1

| # | Problema | Soluzione |
|---|---|---|
| 🔴 | LED sempre spenti senza systemd (modalità PID file di pcwin) | Fallback `~/.local/state/pcwin/*.pid` in `get_status()` |
| 🟡 | Terminale: solo gnome-terminal | Preferenza ptyxis → gnome-terminal fallback |
| 🟡 | `pcwin tramamind ui auto/noauto` avviava il tunnel | Gestione auto/noauto nel subcomando `ui` |
| 🟢 | Header app.js "v6" | Allineato a v7 |
| 🟢 | Errore "CONNECT ALL" senza dettagli | Elenco tunnel falliti nel messaggio |

(fix v6 ereditati: LED primo caricamento, MOUNT_POINT readonly, versioni allineate, polling adattivo)

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
| `/api/open-terminal` | POST | Apre il terminale con pcwin term |
| `/api/open-folder` | POST | Apre xdg-open sul mount point |
| `/api/auto/<svc>/<tunnel>/<action>` | POST | Abilita/disabilita avvio automatico |

## Licenza

MIT
