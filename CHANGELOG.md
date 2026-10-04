# Changelog

## GUI v7 (2026-10-04)

- Allineamento frontend/backend (route dinamiche)
- LED aggiornati al primo caricamento (`await loadServices()`)
- `MOUNT_POINT` readonly (evita `$HOME` non espanso)
- `/api/health` con versione
- `parse_bash_value` e `escape_bash_value`
- Polling adattivo 5s/15s
- Versioni allineate a v7 ovunque

## GUI v6 (2026-10-04)

- Fix critici: frontend allineato a server.py generico
- `refreshStatus()` legge `data.tunnels`
- `openTerminal()` chiama `/api/open-terminal`
- Polling adattivo implementato
- `windowEl` null check

## GUI v5 (2026-10-04)

- `escape_bash_value` sanifica newline
- `parse_bash_value` per apici singoli con `\''`
- `save_config` aggiunge header se file nuovo
- `load_services` con gestione errori

## GUI v4 (2026-10-04)

- Validazione input (no path traversal)
- CORS ristretto a localhost
- Config non distruttiva (backup .bak)
- Naming service allineato con pcwin
- PCWIN path rilevato con `shutil.which`
- XSS-safe (`createElement`)
- `openTerminal()` e `openFolder()` reali
- `requirements.txt`
- Logging di base

## GUI v3 (2026-10-04)

- Prima release della GUI
- Tema Win95 completo
- Tab SYSTEM / SERVICES / CONFIG / LOGS
- `services.yaml` per servizi dinamici
- Suoni WebAudio (modem, errore, successo)
