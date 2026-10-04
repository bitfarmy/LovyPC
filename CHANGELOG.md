# Changelog

## v2.0 (2026-10-04)

Integrazione con TramaMind e systemd.

- `pcwin tramamind` — tunnel verso OmniRoute :20128 (endpoint principale)
- `pcwin tramamind ui` — tunnel verso OpenHands :3000
- `pcwin tramamind auto/noauto` — avvio automatico al login via systemd user service
- `pcwin installa-service` — genera i `.service` in `~/.config/systemd/user/`
- `pcwin omniroute` — alias retrocompatibile di `tramamind`
- `pcwin ollama` — ora marcato come debug (Ollama resta interno a TramaMind)
- SSHFS con opzioni `reconnect` e keepalive
- Pacchetto corretto per Fedora: `fuse-sshfs`
- `pcwin status` — mostra stato systemd (o PID file come fallback)

## v1.0 (2026-10-03)

Prima release pubblica.

- `pcwin term` / `pcwin cmd` — terminale remoto
- `pcwin monta` / `smonta` / `gui` — cartelle via SSHFS
- `pcwin ollama` / `omniroute` — tunnel SSH
- `pcwin status` — panoramica
