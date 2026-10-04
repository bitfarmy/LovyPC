# Changelog

## v2.2 (2026-10-04)

Fix seconda review.

- `installa-service` ora attiva `loginctl enable-linger` — i service partono anche senza login grafico
- `.desktop`: aggiunti `Keywords=` per la ricerca nel menu GNOME
- README: nota su `loginctl disable-linger` per chi vuole disattivare il comportamento

## v2.1 (2026-10-04)

Fix dalla review della community.

- `pcwin.conf.example` allineato: documentate tutte le variabili usate dallo script
- `pcwin.desktop` — azione principale ora `pcwin tramamind` (era `status`), aggiunti `Actions=` per Term/Monta/Status
- Nuovo comando `pcwin disinstalla-service` — rimuove service systemd e PID file
- README: nuova sezione "Gestione service" con `noauto`, `journalctl`, `disinstalla-service`
- README: chiarito che `scripts/chat.sh` appartiene a TramaMind, non a LovyPC
- README: spiegato quando usare `pcwin ollama` (debug, solo se OmniRoute non risponde)
- CHANGELOG: aggiunta sezione "Migrazione da v1.0"

### Migrazione da v2.0

- Nessuna breaking change rispetto alla v2.0
- Se avevi installato i service con v2.0: riesegui `pcwin installa-service` per aggiornare

### Migrazione da v1.0

- Ferma eventuali tunnel v1: `pcwin ollama stop; pcwin omniroute stop`
- I PID file in `~/.local/state/pcwin/` possono essere rimossi (`pcwin disinstalla-service` lo fa automaticamente)
- La config `~/.config/pcwin.conf` resta valida — le variabili `OMNI_*_PORT` sono state rimosse (le porte sono fisse)
- `pcwin omniroute` continua a funzionare come alias di `pcwin tramamind`

## v2.0 (2026-10-04)

Integrazione con TramaMind e systemd.

- `pcwin tramamind` — tunnel verso OmniRoute :20128 (endpoint principale)
- `pcwin tramamind ui` — tunnel verso OpenHands :3000
- `pcwin tramamind auto/noauto` — avvio automatico al login via systemd user service
- `pcwin installa-service` — genera i `.service` in `~/.config/systemd/user/`
- `pcwin omniroute` — alias retrocompatibile di `tramamind`
- `pcwin ollama` — ora marcato come debug
- SSHFS con opzioni `reconnect` e keepalive
- Pacchetto corretto per Fedora: `fuse-sshfs`

## v1.0 (2026-10-03)

Prima release pubblica.

- `pcwin term` / `pcwin cmd` — terminale remoto
- `pcwin monta` / `smonta` / `gui` — cartelle via SSHFS
- `pcwin ollama` / `omniroute` — tunnel SSH
- `pcwin status` — panoramica
