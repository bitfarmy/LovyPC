# LovyPC

Controlla il tuo PC Windows dal tuo Fedora con un solo comando: terminale remoto, cartelle condivise e accesso a Ollama e OmniRoute tramite tunnel SSH.

## Funzionalità

- **Terminale remoto** — PowerShell o CMD del PC Windows direttamente nel tuo terminale Fedora
- **Cartelle** — monta le cartelle Windows via SSHFS in `~/pc-windows`, accessibili da qualsiasi programma
- **Ollama** — tunnel SSH che espone l'Ollama del PC Windows su `localhost:11434` del Fedora
- **OmniRoute** — idem, su porta `7337`
- **Tutto cifrato** via SSH, nessuna porta aperta sul Windows oltre alla 22

## Requisiti

- Sul PC Windows: OpenSSH Server attivo ([guida Microsoft](https://learn.microsoft.com/windows-server/administration/openssh/openssh_install_firstuse))
- Sul Fedora: `sudo dnf install sshfs openssh-clients`
- Ollama / OmniRoute in esecuzione sul PC Windows (per i rispettivi comandi)

## Installazione

```bash
sudo cp pcwin /usr/local/bin/pcwin && sudo chmod +x /usr/local/bin/pcwin
mkdir -p ~/.config && cp pcwin.conf.example ~/.config/pcwin.conf
nano ~/.config/pcwin.conf   # inserisci IP e nome utente del PC Windows
```

Opzionale — accesso senza password:
```bash
ssh-keygen -t ed25519
ssh-copy-id UtenteWindows@192.168.1.x
```

## Uso

```bash
pcwin status        # panoramica: rete, tunnel, montaggi
pcwin term          # terminale PowerShell sul PC Windows
pcwin monta         # monta le cartelle in ~/pc-windows
pcwin gui           # monta e apri il Gestore file
pcwin ollama        # tunnel → Ollama su localhost:11434
pcwin omniroute     # tunnel → OmniRoute su localhost:7337
pcwin smonta        # smonta le cartelle
pcwin ollama stop   # chiudi il tunnel Ollama
```

Dopo `pcwin ollama`:
```bash
export OLLAMA_HOST=http://localhost:11434
ollama list
ollama run llama3.2
```

## Licenza

MIT
