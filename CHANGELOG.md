# Changelog

## v1.0 (2026-10-04)

Prima release pubblica.

- `pcwin term` / `pcwin cmd` — terminale remoto sul PC Windows (PowerShell / cmd.exe)
- `pcwin monta` / `smonta` / `gui` — cartelle Windows via SSHFS in `~/pc-windows`
- `pcwin ollama` — tunnel SSH verso Ollama del PC Windows (`localhost:11434`)
- `pcwin omniroute` — tunnel SSH verso OmniRoute del PC Windows (`localhost:7337`)
- `pcwin status` — panoramica rete, tunnel e montaggi
- Tunnel con riavvio automatico (`ServerAliveInterval`)
- Configurazione via `~/.config/pcwin.conf`
- Voce nel menu applicazioni GNOME (`.desktop`)
