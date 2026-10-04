# LovyPC

Controlla il tuo PC Windows dal tuo Fedora con un solo comando: **terminale remoto**, **cartelle condivise** e accesso a **Ollama** e **OmniRoute** tramite tunnel SSH — tutto cifrato, senza aprire porte sul Windows oltre alla 22.

## Funzionalità

| Cosa | Come |
|---|---|
| **Terminale remoto** | PowerShell o CMD del PC Windows direttamente nel tuo terminale Fedora |
| **Cartelle** | Monta le cartelle Windows via SSHFS in `~/pc-windows`, accessibili da qualsiasi programma |
| **Ollama** | Tunnel SSH che espone l'Ollama del PC Windows su `localhost:11434` |
| **OmniRoute** | Idem, su porta `7337` |

## Requisiti

**Sul PC Windows:** OpenSSH Server attivo — [guida Microsoft](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)

**Sul Fedora:**
```bash
sudo dnf install sshfs openssh-clients fuse3 iputils
```

**Sul PC Windows (opzionale):** Ollama e/o OmniRoute in esecuzione, se vuoi usarli tramite tunnel.

## Installazione

```bash
# 1. Copia lo script
sudo cp pcwin /usr/local/bin/pcwin && sudo chmod +x /usr/local/bin/pcwin

# 2. Crea la tua configurazione
mkdir -p ~/.config
cp pcwin.conf.example ~/.config/pcwin.conf
nano ~/.config/pcwin.conf   # modifica WIN_IP, WIN_USER e WIN_FOLDER
```

**Opzionale — accesso senza password:**
```bash
ssh-keygen -t ed25519
ssh-copy-id UtenteWindows@192.168.1.x
```

## Uso

```bash
pcwin status        # panoramica: rete, tunnel, montaggi
pcwin term          # terminale PowerShell sul PC Windows
pcwin cmd           # prompt cmd.exe sul PC Windows
pcwin monta         # monta le cartelle in ~/pc-windows
pcwin gui           # monta e apri il Gestore file
pcwin smonta        # smonta le cartelle

pcwin ollama        # tunnel → Ollama su localhost:11434
pcwin ollama stop   # chiudi il tunnel Ollama
pcwin omniroute     # tunnel → OmniRoute su localhost:7337
pcwin omniroute stop
```

**Dopo `pcwin ollama`:**
```bash
export OLLAMA_HOST=http://localhost:11434
ollama list
ollama run llama3.2
```

## Licenza

[MIT](LICENSE)
