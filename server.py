#!/usr/bin/env python3
"""
LovyPC GUI v7 — Backend
Connettore universale PC Windows ↔ Fedora

FIX rispetto a v2:
- Validazione input (no path traversal)
- CORS ristretto a localhost
- Config non distruttiva (preserva commenti e variabili extra)
- Naming service allineato con pcwin
- PCWIN path rilevato automaticamente
- Logging di base
"""

import subprocess
import os
import sys
import shutil
import logging
import re
import signal
import threading
import time
import yaml
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ============ LOGGING ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('lovypc-gui')

# ============ APP ============
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app, origins=['http://localhost:8080', 'http://127.0.0.1:8080'])

# ============ CONFIG ============
CONFIG_FILE = os.path.expanduser('~/.config/pcwin.conf')
SERVICES_FILE = os.path.join(os.path.dirname(__file__), 'services.yaml')
PCWIN = shutil.which('pcwin') or '/usr/local/bin/pcwin'

if not os.path.exists(PCWIN):
    logger.warning(f'pcwin non trovato in {PCWIN}')

# ============ VALIDAZIONE ============
def valid_name(name):
    """Valida nome servizio/tunnel: solo alphanumeric, dash, underscore"""
    return re.match(r'^[a-zA-Z0-9_-]+$', name or '')

def escape_bash_value(val):
    """Racchiude in apici singoli, escapando quelli interni.
    Sanifica newline per evitare valori multi-linea."""
    val = str(val).replace("\n", " ").replace("\r", "")
    return "'" + val.replace("'", "'\\''") + "'"

def shlex_split(cmd_str):
    """Split sicuro di comando con shlex"""
    import shlex
    return shlex.split(cmd_str)

# ============ CONFIG: load/save non distruttivo ============
def parse_bash_value(val):
    """Parsa valore Bash con apici singoli o doppi.
    Gestisce escape standard senza usare source."""
    val = val.strip()
    if val.startswith("'") and val.endswith("'") and len(val) >= 2:
        # Apici singoli: unico escape è '\''
        return val[1:-1].replace("'\\''", "'")
    if val.startswith('"') and val.endswith('"') and len(val) >= 2:
        # Doppi apici: interpreta escape principali
        return val[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return val

def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    config[key.strip()] = parse_bash_value(val)
    return config

def save_config(new_values):
    """
    Salva config preservando commenti e variabili non gestite.
    Usa apici singoli per sicurezza con valori contenenti " o '.
    Fa backup prima di scrivere.
    """
    # Backup
    if os.path.exists(CONFIG_FILE):
        shutil.copy(CONFIG_FILE, CONFIG_FILE + '.bak')

    # Leggi file originale
    lines = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            lines = f.readlines()

    # Variabili già presenti nel file
    existing_keys = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key = stripped.split('=', 1)[0].strip()
            existing_keys.add(key)

    # Header se file nuovo
    if not lines:
        updated_lines = ["# LovyPC configuration\n", "# Generato automaticamente da LovyPC GUI\n\n"]
    else:
        updated_lines = []

    # Aggiorna variabili esistenti
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key = stripped.split('=', 1)[0].strip()
            if key in new_values:
                updated_lines.append(f'{key}={escape_bash_value(new_values[key])}\n')
                continue
        updated_lines.append(line)

    # Aggiungi nuove variabili non presenti
    for key, val in new_values.items():
        if key not in existing_keys:
            updated_lines.append(f'{key}={escape_bash_value(val)}\n')

    # Scrivi
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        f.writelines(updated_lines)

    logger.info(f'Config saved to {CONFIG_FILE} (backup: .bak)')

# Fuori da ~/ : ls, Nautilus e i selettori file non aspettano un FUSE bloccato.
DEFAULT_MOUNT = '~/.local/share/lovypc/pc-windows'
LEGACY_MOUNT = '~/pc-windows'

def expand_mount(raw):
    """Percorso assoluto. Non fa stat sul punto di mount: un FUSE morto blocca stat."""
    home = os.environ.get('HOME') or os.path.expanduser('~')
    path = (raw or '').strip() or DEFAULT_MOUNT
    path = path.replace('${HOME}', home).replace('$HOME', home)
    if path.startswith('~'):
        path = home + path[1:]
    if not os.path.isabs(path):
        path = os.path.join(home, path)
    path = os.path.normpath(path)
    parent = os.path.realpath(os.path.dirname(path))
    return os.path.join(parent, os.path.basename(path))

def is_mounted(path):
    """True se path è un mount, da /proc/self/mountinfo. Non tocca il filesystem."""
    want = expand_mount(path)
    try:
        with open('/proc/self/mountinfo', encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 5:
                    continue
                mp = parts[4].replace('\\040', ' ').replace('\\011', '\t')
                if mp == want:
                    return True
    except OSError as e:
        logger.debug(f'mountinfo: {e}')
    return False

def active_mount(config):
    """Punto configurato, oppure il vecchio ~/pc-windows se è ancora montato."""
    point = expand_mount(config.get('MOUNT_POINT'))
    if is_mounted(point):
        return point, True
    legacy = expand_mount(LEGACY_MOUNT)
    if legacy != point and is_mounted(legacy):
        return legacy, True
    return point, False

# ============ SERVICES ============
def load_services():
    if not os.path.exists(SERVICES_FILE):
        logger.error(f'Services file not found: {SERVICES_FILE}')
        return {}
    try:
        with open(SERVICES_FILE) as f:
            data = yaml.safe_load(f)
        return data.get('services', {}) if data else {}
    except yaml.YAMLError as e:
        logger.error(f'Invalid services.yaml: {e}')
        return {}

# ============ STATUS ============
def get_status():
    config = load_config()
    win_ip = config.get('WIN_IP', '')

    # Network
    network = False
    if win_ip:
        try:
            r = subprocess.run(['ping', '-c1', '-W1', win_ip],
                             capture_output=True, timeout=2)
            network = r.returncode == 0
        except Exception as e:
            logger.debug(f'Ping failed: {e}')

    # Tunnels — naming allineato con pcwin:
    # pcwin-tramamind.service, pcwin-tramamind-ui.service
    services = load_services()
    tunnels = {}
    for svc_key, svc in services.items():
        for tunnel in svc.get('tunnels', []):
            tname = tunnel['name']
            # Costruisci nome service come lo fa pcwin
            # pcwin usa: pcwin-{cmd[0]}{-cmd[1]...}.service
            cmd_parts = tunnel.get('pcwin_cmd', '').split()
            if cmd_parts:
                svc_tname = f"pcwin-{cmd_parts[0]}"
                if len(cmd_parts) > 1:
                    svc_tname += f"-{cmd_parts[1]}"
            else:
                svc_tname = f"pcwin-{svc_key}-{tname}"

            try:
                state = subprocess.run(
                    ['systemctl', '--user', 'is-active', f'{svc_tname}.service'],
                    capture_output=True, text=True).stdout.strip()
                enabled = subprocess.run(
                    ['systemctl', '--user', 'is-enabled', f'{svc_tname}.service'],
                    capture_output=True, text=True).stdout.strip()
                tunnels[f'{svc_key}-{tname}'] = {
                    'active': state == 'active',
                    'enabled': enabled == 'enabled',
                    'state': state,
                    'service': svc_key,
                    'tunnel': tname,
                    'display': tunnel.get('display', tname),
                    'port': tunnel.get('port'),
                    'url': tunnel.get('url'),
                    'systemd_name': svc_tname
                }
            except Exception as e:
                logger.error(f'Error checking tunnel {svc_tname}: {e}')
                tunnels[f'{svc_key}-{tname}'] = {
                    'active': False, 'enabled': False, 'state': 'error',
                    'service': svc_key, 'tunnel': tname,
                    'display': tunnel.get('display', tname),
                    'port': tunnel.get('port'),
                    'url': tunnel.get('url'),
                    'systemd_name': svc_tname
                }

    # Mount — mountinfo, non ismount: ismount fa stat e si blocca se Windows è spento
    mount_point, mounted = active_mount(config)

    return {
        'network': network,
        'win_ip': win_ip,
        'win_user': config.get('WIN_USER', ''),
        'win_folder': config.get('WIN_FOLDER', ''),
        'mount_point': mount_point,
        'mounted': mounted,
        'tunnels': tunnels,
        'config_exists': os.path.exists(CONFIG_FILE),
        'pcwin_found': os.path.exists(PCWIN)
    }

# ============ API ROUTES ============

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status')
def api_status():
    return jsonify(get_status())

@app.route('/api/services')
def api_services():
    """Restituisce solo campi pubblici (no comandi interni)"""
    services = load_services()
    public = {}
    for key, svc in services.items():
        public[key] = {
            'name': svc.get('name', key),
            'description': svc.get('description', ''),
            'icon': svc.get('icon', '🔧'),
            'tunnels': [
                {
                    'name': t.get('name'),
                    'display': t.get('display', t.get('name')),
                    'port': t.get('port'),
                    'url': t.get('url')
                }
                for t in svc.get('tunnels', [])
            ]
        }
    return jsonify(public)

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'POST':
        data = request.json
        if not isinstance(data, dict):
            return jsonify({'success': False, 'error': 'Invalid data'}), 400
        # Solo chiavi valide
        allowed = {'WIN_USER', 'WIN_IP', 'WIN_FOLDER'}  # MOUNT_POINT escluso: contiene $HOME
        filtered = {k: v for k, v in data.items() if k in allowed}
        try:
            save_config(filtered)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f'Config save failed: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify(load_config())

@app.route('/api/connect/<service_key>/<tunnel_name>', methods=['POST'])
def api_connect(service_key, tunnel_name):
    # Validazione
    if not valid_name(service_key) or not valid_name(tunnel_name):
        return jsonify({'success': False, 'error': 'Invalid name'}), 400

    services = load_services()
    if service_key not in services:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    svc = services[service_key]
    tunnel = next((t for t in svc.get('tunnels', []) if t['name'] == tunnel_name), None)
    if not tunnel:
        return jsonify({'success': False, 'error': 'Tunnel not found'}), 404

    cmd = shlex_split(tunnel.get('pcwin_cmd', ''))
    if not cmd:
        return jsonify({'success': False, 'error': 'No command defined'}), 400

    try:
        logger.info(f'Connecting: pcwin {" ".join(cmd)}')
        r = subprocess.run([PCWIN] + cmd, capture_output=True, text=True, timeout=10)
        return jsonify({
            'success': r.returncode == 0,
            'output': r.stdout,
            'error': r.stderr
        })
    except Exception as e:
        logger.error(f'Connect failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/disconnect/<service_key>/<tunnel_name>', methods=['POST'])
def api_disconnect(service_key, tunnel_name):
    if not valid_name(service_key) or not valid_name(tunnel_name):
        return jsonify({'success': False, 'error': 'Invalid name'}), 400

    services = load_services()
    if service_key not in services:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    svc = services[service_key]
    tunnel = next((t for t in svc.get('tunnels', []) if t['name'] == tunnel_name), None)
    if not tunnel:
        return jsonify({'success': False, 'error': 'Tunnel not found'}), 404

    cmd = shlex_split(tunnel.get('pcwin_cmd', '')) + ['stop']

    try:
        logger.info(f'Disconnecting: pcwin {" ".join(cmd)}')
        r = subprocess.run([PCWIN] + cmd, capture_output=True, text=True, timeout=10)
        return jsonify({'success': r.returncode == 0})
    except Exception as e:
        logger.error(f'Disconnect failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/connect/service/<service_key>', methods=['POST'])
def api_connect_service(service_key):
    if not valid_name(service_key):
        return jsonify({'success': False, 'error': 'Invalid name'}), 400

    services = load_services()
    if service_key not in services:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    results = {}
    all_ok = True

    for tunnel in services[service_key].get('tunnels', []):
        cmd = shlex_split(tunnel.get('pcwin_cmd', ''))
        if not cmd:
            continue
        try:
            r = subprocess.run([PCWIN] + cmd, capture_output=True, text=True, timeout=10)
            results[tunnel['name']] = r.returncode == 0
            if r.returncode != 0:
                all_ok = False
        except Exception as e:
            results[tunnel['name']] = False
            all_ok = False
            logger.error(f'Tunnel {tunnel["name"]} failed: {e}')

    return jsonify({'success': all_ok, 'results': results})

@app.route('/api/disconnect/service/<service_key>', methods=['POST'])
def api_disconnect_service(service_key):
    if not valid_name(service_key):
        return jsonify({'success': False, 'error': 'Invalid name'}), 400

    services = load_services()
    if service_key not in services:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    for tunnel in services[service_key].get('tunnels', []):
        cmd = shlex_split(tunnel.get('pcwin_cmd', '')) + ['stop']
        try:
            subprocess.run([PCWIN] + cmd, capture_output=True, timeout=10)
        except Exception as e:
            logger.error(f'Stop tunnel failed: {e}')

    return jsonify({'success': True})

@app.route('/api/mount', methods=['POST'])
def api_mount():
    try:
        r = subprocess.run([PCWIN, 'monta'], capture_output=True, text=True, timeout=15)
        return jsonify({'success': r.returncode == 0, 'output': r.stdout})
    except Exception as e:
        logger.error(f'Mount failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/unmount', methods=['POST'])
def api_unmount():
    try:
        r = subprocess.run([PCWIN, 'smonta'], capture_output=True, text=True, timeout=10)
        return jsonify({'success': r.returncode == 0})
    except Exception as e:
        logger.error(f'Unmount failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

def request_shutdown():
    """Smonta i dischi Windows. Non termina il processo."""
    try:
        r = subprocess.run([PCWIN, 'smonta'], capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return False, 'Lo smontaggio ha impiegato troppo. LovyPC resta aperto.'
    except Exception as e:
        logger.error(f'Shutdown unmount failed: {e}')
        return False, str(e)
    text = (r.stdout or r.stderr or '').strip()
    _, mounted = active_mount(load_config())
    # Conta il disco rimasto, non il codice di uscita: se è via, si può chiudere.
    if mounted:
        return False, text or 'Non riesco a smontare. Chiudi le finestre che usano quelle cartelle.'
    return True, text or 'Smontato.'

def _stop_server():
    time.sleep(0.4)
    os.kill(os.getpid(), signal.SIGTERM)

@app.route('/api/shutdown', methods=['POST'])
def api_shutdown():
    """Smonta e, solo se il disco è via, chiude il server."""
    ok, message = request_shutdown()
    if not ok:
        logger.warning(f'Shutdown rifiutato: {message}')
        return jsonify({'success': False, 'error': message}), 500
    logger.info('Shutdown: dischi smontati, chiusura server')
    threading.Thread(target=_stop_server, daemon=True).start()
    return jsonify({'success': True, 'output': message})

@app.route('/api/open-folder', methods=['POST'])
def api_open_folder():
    """Apre la cartella montata nel file manager"""
    config = load_config()
    mount_point, mounted = active_mount(config)

    if not mounted:
        return jsonify({'success': False, 'error': 'Not mounted'}), 400

    xdg = shutil.which('xdg-open')
    if not xdg:
        return jsonify({'success': False, 'error': 'xdg-open not found'}), 500

    try:
        subprocess.Popen(
            [xdg, mount_point],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Open folder failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/open-terminal', methods=['POST'])
def api_open_terminal():
    """Apre gnome-terminal con pcwin term"""
    term = shutil.which('gnome-terminal')
    if not term:
        return jsonify({'success': False, 'error': 'gnome-terminal not found'}), 500
    try:
        subprocess.Popen(
            [term, '--', 'bash', '-c', f'{PCWIN} term; exec bash'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Open terminal failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auto/<service_key>/<tunnel_name>/<action>', methods=['POST'])
def api_auto(service_key, tunnel_name, action):
    if not valid_name(service_key) or not valid_name(tunnel_name):
        return jsonify({'success': False, 'error': 'Invalid name'}), 400
    if action not in ('auto', 'noauto'):
        return jsonify({'success': False, 'error': 'Invalid action'}), 400

    services = load_services()
    if service_key not in services:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    svc = services[service_key]
    tunnel = next((t for t in svc.get('tunnels', []) if t['name'] == tunnel_name), None)
    if not tunnel:
        return jsonify({'success': False, 'error': 'Tunnel not found'}), 404

    cmd = shlex_split(tunnel.get('pcwin_cmd', '')) + [action]

    try:
        r = subprocess.run([PCWIN] + cmd, capture_output=True, text=True, timeout=10)
        return jsonify({'success': r.returncode == 0})
    except Exception as e:
        logger.error(f'Auto failed: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ MAIN ============
@app.route('/api/health')
def api_health():
    """Health check per frontend"""
    return jsonify({
        'status': 'ok',
        'version': '7.5.0',
        'pcwin_found': os.path.exists(PCWIN),
        'config_exists': os.path.exists(CONFIG_FILE)
    })

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║     LovyPC GUI v7 — Win95 Edition        ║
    ║     Universal PC Connector               ║
    ║                                          ║
    ║     GUI:  http://localhost:8080          ║
    ║                                          ║
    ║     NOTE: Local tool, no authentication  ║
    ║     Ctrl+C to stop                       ║
    ╚══════════════════════════════════════════╝
    """)
    logger.info('Starting LovyPC GUI server v7 on http://localhost:8080')
    app.run(host='127.0.0.1', port=8080, debug=False)
