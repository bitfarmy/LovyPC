## LovyPC v7.0 — GUI Win95 Edition 🖥️

Prima release con GUI integrata nel repo principale.

### Novità
- **GUI web stile Win95** (Flask) in `gui/` — tab SYSTEM / SERVICES / CONFIG / LOGS
- Servizi dinamici da `gui/backend/services.yaml`: aggiungi un blocco YAML e la GUI lo gestisce
- Servizio **Ollama** (debug :11434) incluso in services.yaml
- Rilevamento tunnel in modalità PID file (senza systemd user)
- Terminale: ptyxis (Fedora) con fallback gnome-terminal
- `pcwin tramamind ui auto/noauto` ora funzionante

### Installazione GUI
```bash
cd gui && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cd backend && python server.py
```
→ http://localhost:8080

### ⚠️ Sicurezza
Tool locale senza autenticazione — gira solo su `127.0.0.1:8080`.

### Full changelog
Vedi [CHANGELOG.md](CHANGELOG.md)
