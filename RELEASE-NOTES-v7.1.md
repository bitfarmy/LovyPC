## LovyPC v7.1 — Fix end-to-end + Ollama 🦙

Aggiornamento della GUI Win95 Edition (v7.0) con bugfix dal test end-to-end e un nuovo servizio.

### Fix
- **LED tunnel con PID file**: senza systemd user, `pcwin` usa `~/.local/state/pcwin/*.pid` — ora la GUI rileva anche questi tunnel (prima restavano sempre spenti)
- **Terminale ptyxis**: `/api/open-terminal` prova prima ptyxis (default Fedora) e poi gnome-terminal
- **`pcwin tramamind ui auto/noauto`**: prima avviava il tunnel invece di abilitare/disabilitare l'avvio automatico
- **CONNECT ALL**: l'errore ora elenca i tunnel falliti
- Header frontend allineato alla versione

### Novità
- **Servizio Ollama** (debug :11434) in `gui/backend/services.yaml` — appare automaticamente nella tab SERVICES
- GUI integrata come sottocartella `gui/` nel repo principale, con README radice rinnovato
- 15/15 test end-to-end API passati

### Installazione / aggiornamento
```bash
cd gui && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cd backend && python server.py
```
→ http://localhost:8080

### ⚠️ Sicurezza
Tool locale senza autenticazione — gira solo su `127.0.0.1:8080`.

### Full changelog
Vedi [CHANGELOG.md](CHANGELOG.md)
