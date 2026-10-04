# LovyPC

Controlla il tuo PC Windows dal tuo Fedora con un solo comando: **terminale remoto**, **cartelle condivise** e accesso a [TramaMind](https://github.com/bitfarmy/tramamind) — lo stack IA personale multi-modello orchestrato da OmniRoute.

Tutto cifrato via SSH, zero porte aperte sul Windows oltre alla 22.

## Come si collega a TramaMind

TramaMind gira sul PC Windows. LovyPC ne espone i servizi sul tuo Fedora tramite tunnel SSH:

| Servizio TramaMind | Porta remota | Sul Fedora diventa | Uso |
|---|---|---|---|
| **OmniRoute** (router L4) | `20128` | `http://localhost:20128` | Endpoint OpenAI-compatible — **unico necessario** |
| OpenHands (agente L-APP) | `3000` | `http://localhost:3000` | Interfaccia web agente di coding |
| Ollama (runtime L1) | `11434` | `http://localhost:11434` | Solo debug — normalmente passa da OmniRoute |

## Funzionalità

| Cosa | Come |
|---|---|
| **Terminale remoto** | PowerShell o CMD del PC Windows nel tuo terminale Fedora |
| **Cartelle** | Monta le cartelle Windows via SSHFS in `~/pc-windows` |
| **TramaMind** | Un tunnel verso OmniRoute — routing, failover, cache semantica inclusi |
| **OpenHands** | Secondo tunnel opzionale verso l'interfaccia web |

## Requisiti

**Sul PC Windows:**
- OpenSSH Server attivo — [guida Microsoft](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- TramaMind in esecuzione (`scripts/start-all.sh`)

**Sul Fedora:**
```bash
sudo dnf install fuse-sshfs openssh-clients iputils
```

## Installazione

```bash
# 1. Copia lo script
sudo cp pcwin /usr/local/bin/pcwin && sudo chmod +x /usr/local/bin/pcwin

# 2. Configura
mkdir -p ~/.config
cp pcwin.conf.example ~/.config/pcwin.conf
nano ~/.config/pcwin.conf   # modifica WIN_IP, WIN_USER e WIN_FOLDER
```

**Accesso senza password (consigliato):**
```bash
ssh-keygen -t ed25519
ssh-copy-id UtenteWindows@192.168.1.x
```

## Uso

```bash
pcwin status                 # panoramica: rete, tunnel, montaggi
pcwin term                   # terminale PowerShell sul PC Windows
pcwin cmd                    # prompt cmd.exe
pcwin monta                  # monta le cartelle in ~/pc-windows
pcwin gui                    # monta e apri il Gestore file
pcwin smonta                 # smonta

pcwin tramamind              # tunnel → OmniRoute :20128
pcwin tramamind stop         # ferma
pcwin tramamind ui           # tunnel → OpenHands :3000
pcwin tramamind ui stop
pcwin ollama                 # tunnel → Ollama :11434 (debug)
```

**Dopo `pcwin tramamind`** — usa OmniRoute come provider OpenAI:
```bash
export OPENAI_BASE_URL=http://localhost:20128/v1
export OPENAI_API_KEY=omniroute   # o la chiave configurata in OmniRoute
```

Se hai TramaMind clonato anche sul Fedora, puoi usare la sua CLI puntando al PC Windows:
```bash
./scripts/chat.sh "Scrivi un haiku sulla privacy"
```

## Service systemd (tunnel persistenti)

Per avere i tunnel sempre attivi, anche dopo il login:

```bash
pcwin installa-service       # crea i .service in ~/.config/systemd/user/
pcwin tramamind auto         # avvio automatico al login
pcwin tramamind              # avvia/disattiva manualmente
```

**Gestione service:**
```bash
pcwin tramamind noauto       # disattiva avvio automatico
pcwin disinstalla-service    # rimuovi tutti i service e i PID file
journalctl --user -u pcwin-tramamind -f   # log in tempo reale
systemctl --user status pcwin-tramamind   # stato dettagliato
```

> **Nota:** `pcwin installa-service` attiva automaticamente `loginctl enable-linger`, così i tunnel partono anche senza login grafico (es. dopo un riavvio del Fedora). Per disattivare: `loginctl disable-linger $USER`.

## Licenza

[MIT](LICENSE)
