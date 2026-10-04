# LovyPC

![Version](https://img.shields.io/badge/version-7.4-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Fedora%20Linux-blue?style=flat-square)
![UI](https://img.shields.io/badge/UI-Win95%20Edition-c0c0c0?style=flat-square)

LovyPC connects a Windows PC to a Fedora machine on the same network. From Fedora you open a remote terminal, browse the Windows folders, and reach the services that run on Windows through SSH tunnels. The services included today are TramaMind (OmniRoute), OpenHands, and Ollama. You can add others later without changing the program.

**Descrizione**

LovyPC collega il tuo PC Windows alla tua Fedora: terminale remoto, cartelle montate via SSHFS e tunnel SSH per i tuoi servizi (TramaMind/OmniRoute, OpenHands, Ollama e qualunque altro servizio futuro).

| Piece | What it does |
|---|---|
| `pcwin` | Command-line tool. Terminal, folder mount, tunnels, systemd services, SSH key setup. |
| `gui/` | Small local web window in a Windows 95 style. Tabs: SYSTEM, SERVICES, CONFIG, LOGS. |

The window listens only on your own computer, at <http://127.0.0.1:8080>. It has no login. Do not expose that address to the rest of the network.

---

## Start

One command creates the Python environment, installs the dependencies, copies `pcwin` into `~/.local/bin`, and opens the window:

```bash
git clone https://github.com/bitfarmy/LovyPC.git
cd LovyPC
bash gui/start.sh
```

Fedora needs `sshfs`:

```bash
sudo dnf install sshfs
```

Windows needs the OpenSSH Server feature turned on.

After the first run, this is enough to pick up later changes:

```bash
git pull && bash gui/start.sh
```

If the window is already open, close it first. Closing the browser tab leaves the server running, and `start.sh` will only open the browser again. Stop the server with Ctrl+C in the terminal where you started it, then run `start.sh` once more.

---

## First visit

1. Open the CONFIG tab. Fill in the Windows user, the Windows IP address, and the Windows folder you want to see. Save. The program writes `~/.config/pcwin.conf` for you.
2. On the same tab, choose SETUP SSH and type the Windows password once. LovyPC installs an SSH key and fixes the file permissions on Windows, including the extra file Windows uses for administrator accounts.
3. Open the SYSTEM tab and choose MOUNT.

You can do the same from the terminal:

```bash
mkdir -p ~/.config
cp pcwin.conf.example ~/.config/pcwin.conf
# edit WIN_USER, WIN_IP, and WIN_FOLDER
pcwin setup-ssh
pcwin monta
```

An example config lives in `pcwin.conf.example`.

---

## Where the Windows folders appear

The Windows disk is mounted at:

```text
~/.local/share/lovypc/pc-windows
```

That path is intentional. An earlier version used `~/pc-windows`, a folder sitting directly inside your home directory. Fedora looks through the home directory all the time: the file manager, the save dialogs, and the shell. When Windows was asleep or switched off, each of those lookups waited on the dead connection, and typing and window movement felt late. The mount now lives one step away from that traffic.

`pcwin monta` also removes a leftover mount at `~/pc-windows` if it finds one. The empty `~/pc-windows` directory, if it is still there, is only a local folder.

You can choose another path with `MOUNT_POINT` in `~/.config/pcwin.conf`. Keep it out of the top of your home directory. The CONFIG tab shows the path and does not let you change it from the window, because a value typed there would not expand `$HOME`.

While the disk is mounted, LovyPC checks `/proc/self/mountinfo` instead of asking the disk itself whether it is there. A sleeping Windows PC cannot stall that check. SSH gives up after a few seconds if the PC does not answer.

---

## The window

| Tab | What you find there |
|---|---|
| SYSTEM | Network and mount lights, remote terminal, mount and unmount, open the folder, refresh. |
| SERVICES | One card for each entry in `services.yaml`. Connect or disconnect a single tunnel, or the whole service. |
| CONFIG | Windows user, IP address, and folder. The mount path is shown and is not editable here. SETUP SSH is on this tab. |
| LOGS | What the window just did. |

### HTTP routes

| Route | Method | Purpose |
|---|---|---|
| `/api/health` | GET | The server is up. Reports the version and whether `pcwin` was found. |
| `/api/status` | GET | Network, tunnels, and mount. |
| `/api/services` | GET | Services listed in `services.yaml`. |
| `/api/config` | GET, POST | Read or write the config. `MOUNT_POINT` is left untouched. |
| `/api/connect/<svc>/<tunnel>` | POST | Open one tunnel. |
| `/api/disconnect/<svc>/<tunnel>` | POST | Close one tunnel. |
| `/api/connect/service/<svc>` | POST | Open every tunnel of a service. |
| `/api/disconnect/service/<svc>` | POST | Close every tunnel of a service. |
| `/api/mount`, `/api/unmount` | POST | Mount or unmount the Windows folders. |
| `/api/setup-ssh` | POST | Install the SSH key. Opens a terminal if Windows asks for the password. |
| `/api/open-terminal` | POST | Open a terminal with `pcwin term`. Ptyxis is preferred, then GNOME Terminal. |
| `/api/open-folder` | POST | Open the mounted folder in the file manager. |
| `/api/auto/<svc>/<tunnel>/<action>` | POST | Turn automatic start on or off (`auto` or `noauto`). |

---

## The `pcwin` command

```bash
pcwin term                 # PowerShell on the Windows PC
pcwin cmd                  # cmd.exe on the Windows PC
pcwin monta | smonta       # mount or unmount ~/.local/share/lovypc/pc-windows
pcwin gui                  # mount, then open the file manager
pcwin setup-ssh            # one-time SSH key, so later commands need no password

pcwin tramamind            # tunnel to OmniRoute on port 20128
pcwin tramamind stop
pcwin tramamind auto       # start that tunnel at login
pcwin tramamind noauto
pcwin tramamind ui         # tunnel to OpenHands on port 3000
pcwin tramamind ui stop

pcwin ollama               # tunnel to Ollama on port 11434, for debugging
pcwin omniroute            # old name for tramamind

pcwin installa-service     # install the user systemd units
pcwin disinstalla-service
pcwin status
```

Systemd is optional. Without it, the tunnels are ordinary SSH processes. Their process ids are stored in `~/.local/state/pcwin/`, and the window notices them there too. With the units installed, a tunnel that drops while Windows is on comes back after a few seconds. If Windows is off, the unit stops retrying instead of pinging forever.

Logs, once the units exist:

```bash
journalctl --user -u pcwin-tramamind -f
```

---

## Add a service

Edit `gui/backend/services.yaml`. The window picks up the new card on the next refresh. You do not need to change the Python or the page.

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
        pcwin_cmd: "custom tunnel command"   # run as: pcwin <cmd> [stop|auto|noauto]
        url: http://localhost:8080
```

The systemd unit name comes from `pcwin_cmd`. `"tramamind"` becomes `pcwin-tramamind.service`. `"tramamind ui"` becomes `pcwin-tramamind-ui.service`.

---

## Layout

```text
LovyPC/
├── pcwin                  # command-line tool
├── pcwin.conf.example     # sample config
├── pcwin.desktop          # desktop launcher
├── gui/
│   ├── start.sh           # one command: environment, dependencies, pcwin, window
│   ├── backend/           # server.py and services.yaml
│   ├── frontend/          # index.html, css/, js/
│   └── requirements.txt
├── ARCHITECTURE.md
├── CHANGELOG.md
└── LICENSE                # MIT
```

---

## When something fails

| What you see | What it usually means | What to do |
|---|---|---|
| MOUNT sits there and then stops after about 15 seconds | SSH is still asking for a password | Run `pcwin setup-ssh`, or use SETUP SSH in the window |
| Setup SSH says the check did not pass | The Windows user is an administrator | Run `pcwin setup-ssh` again. The key is also written to `administrators_authorized_keys` |
| A tunnel address does not answer | The program is not running on Windows | Start TramaMind or OpenHands on Windows, then connect again |
| The window does not open | The server is not running | Run `bash gui/start.sh` and read the terminal |
| Fedora feels slow while LovyPC is open | An old mount is still at `~/pc-windows` | Close LovyPC and run `pcwin smonta`, then `pcwin monta` |

---

## License

MIT. See [LICENSE](LICENSE).
