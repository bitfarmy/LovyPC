# 🖥️ LovyPC — Connettore universale PC Windows ↔ Fedora

![Version](https://img.shields.io/badge/version-7.4-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Fedora%20Linux-blue?style=flat-square)
![UI](https://img.shields.io/badge/UI-Win95%20Edition-c0c0c0?style=flat-square)

**LovyPC collega il tuo PC Windows alla tua Fedora:** terminale remoto, cartelle
montate via SSHFS e tunnel SSH per i tuoi servizi (TramaMind/OmniRoute,
OpenHands, Ollama e qualunque altro servizio futuro).

| Componente | Descrizione |
|---|---|
| 🖥️ **`pcwin`** | CLI bash — terminale, mount, tunnel, service systemd, setup SSH |
| 🪟 **`gui/`** | GUI web stile Win95 (Flask) — tab SYSTEM / SERVICES / CONFIG / LOGS |

---

## 🚀 Avvio rapido

Un comando solo. Crea l'ambiente, installa le dipendenze, sincronizza `pcwin` e avvia la GUI:

```bash
git clone https://github.com/bitfarmy/LovyPC.git
cd LovyPC
bash gui/start.sh
```

Poi apri **http://localhost:8080** e configura dalla tab **CONFIG** (User, IP, cartella del PC Windows).

> Da ora in poi, ogni aggiornamento è solo:
> ```bash
> git pull && bash gui/start.sh
> ```

---

## ⚙️ Configurazione (prima volta)

1. Apri la GUI → tab **CONFIG** → inserisci **Windows User**, **Windows IP**, **Shared Folder** → **SAVE**
   (la GUI crea da sola `~/.config/pcwin.conf`)
2. Tab **CONFIG** → **SETUP SSH** → inserisci la password Windows **una volta sola**
   (configura la chiave SSH e i permessi su Windows, incluso il caso utente amministratore)
3. Tab **SYSTEM** → **MOUNT** per montare le cartelle

Oppure a mano:

```bash
mkdir -p ~/.config && cp pcwin.conf.example ~/.config/pcwin.conf
# modifica WIN_USER, WIN_IP, WIN_FOLDER
pcwin setup-ssh   # accesso senza password, una tantum
```

> ⚠️ Prerequisiti: `sshfs` (`sudo dnf install sshfs`) e **OpenSSH Server attivo sul PC Windows**.

---

## 🖥️ GUI — Tab

| Tab | Contenuto |
|---|---|
| **SYSTEM** | LED network/mount, terminale remoto, mount/unmount, open folder, refresh |
| **SERVICES** | Card dinamiche da `services.yaml` — CONNECT/DISCONNECT per singolo tunnel o intero servizio |
| **CONFIG** | WIN_USER, WIN_IP, WIN_FOLDER (MOUNT_POINT readonly) + **SETUP SSH** |
| **LOGS** | Log operazioni in tempo reale |

### API backend

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
| `/api/mount` `/api/unmount` | POST | Mount/Unmount SSHFS |
| `/api/setup-ssh` | POST | Setup chiave SSH (apre terminale se serve password) |
| `/api/open-terminal` | POST | Terminale con `pcwin term` (ptyxis → gnome-terminal) |
| `/api/open-folder` | POST | File manager sul mount point |
| `/api/auto/<svc>/<tunnel>/<action>` | POST | Avvio automatico (auto/noauto) |

> 🔒 **Sicurezza**: la GUI è un tool locale senza autenticazione. Gira solo su
> `127.0.0.1:8080` — non esporla su rete esterna.

---

## ⌨️ CLI `pcwin`

```bash
pcwin term                 # SSH PowerShell sul PC Windows
pcwin cmd                  # SSH cmd.exe remoto
pcwin monta | smonta       # Mount/Unmount SSHFS in ~/pc-windows
pcwin gui                  # Monta e apri il gestore file
pcwin setup-ssh            # Accesso senza password (chiave SSH, una tantum)

pcwin tramamind            # Tunnel → OmniRoute :20128 (endpoint principale)
pcwin tramamind stop       # Ferma il tunnel
pcwin tramamind auto       # Avvio automatico al login (systemd user)
pcwin tramamind noauto     # Disattiva avvio automatico
pcwin tramamind ui         # Tunnel → OpenHands :3000
pcwin tramamind ui stop    # Ferma OpenHands

pcwin ollama               # Tunnel → Ollama :11434 (solo debug)
pcwin omniroute            # Alias di tramamind (retrocompatibilità)

pcwin installa-service     # Crea i service systemd user (persistenza anche senza login)
pcwin disinstalla-service  # Rimuovi service e PID file
pcwin status               # Panoramica completa
```

Funziona anche **senza systemd user**: i tunnel vengono avviati come processi
SSH in background con PID file in `~/.local/state/pcwin/` — la GUI rileva
entrambe le modalità.

---

## ➕ Aggiungere un servizio

Modifica `gui/backend/services.yaml` aggiungendo un blocco — la GUI lo
rileva automaticamente al prossimo refresh, **senza toccare codice**:

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
- Il frontend renderizza la nuova card automaticamente al prossimo polling

---

## 🧩 Struttura del repo

```
LovyPC/
├── pcwin                  # CLI bash
├── pcwin.conf.example     # Config di esempio
├── pcwin.desktop          # Launcher desktop
├── gui/                   # GUI web (Flask + Win95)
│   ├── start.sh           # Avvio one-command (venv + deps + sync pcwin)
│   ├── backend/           # server.py + services.yaml
│   ├── frontend/          # index.html, css/, js/
│   └── requirements.txt
├── ARCHITECTURE.md        # Architettura e API backend
├── CHANGELOG.md
└── LICENSE                # MIT
```

---

## 🔧 Risoluzione problemi

| Problema | Causa | Soluzione |
|---|---|---|
| MOUNT va in timeout (15s) | SSH chiede la password | `pcwin setup-ssh` (o pulsante SETUP SSH nella GUI) |
| Setup SSH: "verifica non riuscita" | Utente Windows amministratore | Già gestito: la chiave va anche in `administrators_authorized_keys` — riesegui `pcwin setup-ssh` |
| URL tunnel non risponde | Servizio non avviato su Windows | Avvia TramaMind/OpenHands sul PC Windows, poi CONNECT |
| GUI non si apre | Backend non avviato | `bash gui/start.sh` e controlla il terminale |

---

## Licenza

MIT — vedi [LICENSE](LICENSE)
