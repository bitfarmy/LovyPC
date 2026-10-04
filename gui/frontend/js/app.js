// ============================================
// LovyPC GUI v7.3 — Frontend
// Allineato a server.py generico (route dinamiche)
// Novità v7.3: setup SSH senza password dalla tab CONFIG
// ============================================

const API = 'http://localhost:8080/api';
let servicesData = null;
let backendOnline = false;

// WebAudio
let audioCtx = null;
function getAudioContext() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return audioCtx;
}

function playModemSound() {
    try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(2400, ctx.currentTime + 2);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 2);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(); osc.stop(ctx.currentTime + 2);
    } catch(e) {}
}

function playErrorSound() {
    try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.setValueAtTime(330, ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(); osc.stop(ctx.currentTime + 0.3);
    } catch(e) {}
}

function playSuccessSound() {
    try {
        const ctx = getAudioContext();
        [523, 659, 784].forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.1);
            gain.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.1);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.1 + 0.2);
            osc.connect(gain); gain.connect(ctx.destination);
            osc.start(ctx.currentTime + i * 0.1); osc.stop(ctx.currentTime + i * 0.1 + 0.2);
        });
    } catch(e) {}
}

// Log
function addLog(msg, type = 'info') {
    const log = document.getElementById('log');
    if (!log) return;
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
}

// Tabs
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        });
    });
}

// Status — FIX: legge data.tunnels, non data.omniroute
async function refreshStatus() {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
        const res = await fetch(`${API}/status`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        backendOnline = true;
        updateLed('network-led', data.network);
        updateLed('mount-led', data.mounted);

        const statusEl = document.getElementById('status-text');
        if (statusEl) {
            statusEl.textContent = data.network ? 'ONLINE' : 'OFFLINE';
            statusEl.className = 'value' + (data.network ? '' : ' error');
        }

        const targetEl = document.getElementById('target-info');
        if (targetEl) {
            targetEl.textContent = data.win_user && data.win_ip 
                ? `${data.win_user}@${data.win_ip}` : 'Not configured';
        }

        // FIX: aggiorna LED tunnel da data.tunnels (dict)
        if (data.tunnels) {
            Object.entries(data.tunnels).forEach(([name, tunnel]) => {
                const led = document.getElementById(`led-${name}`);
                if (led) updateLed(`led-${name}`, tunnel.active);

                const btn = document.getElementById(`btn-${name}`);
                if (btn) {
                    btn.textContent = tunnel.active ? 'DISCONNECT' : 'CONNECT';
                    btn.classList.toggle('disconnect', tunnel.active);
                }

                const autoBtn = document.getElementById(`auto-${name}`);
                if (autoBtn) {
                    autoBtn.textContent = tunnel.enabled ? 'AUTO ✓' : 'AUTO';
                    autoBtn.classList.toggle('on', tunnel.enabled);
                }
            });
        }

    } catch(e) {
        clearTimeout(timeoutId);
        if (backendOnline) {
            backendOnline = false;
            addLog('Backend non raggiungibile — avvia server.py', 'error');
            showError('Backend non raggiungibile. Avvia: python server.py');
        }
    }
}

function updateLed(id, active) {
    const el = document.getElementById(id);
    if (el) el.className = 'led' + (active ? ' active' : '');
}

// Services — XSS-safe
async function loadServices() {
    try {
        const res = await fetch(`${API}/services`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        servicesData = await res.json();
        renderServices(servicesData);
    } catch(e) {
        addLog('Failed to load services: ' + e.message, 'error');
        const container = document.getElementById('services-container');
        if (container) {
            container.textContent = 'Failed to load services. Is backend running?';
        }
    }
}

function renderServices(services) {
    const container = document.getElementById('services-container');
    if (!container) return;
    container.innerHTML = '';

    Object.entries(services).forEach(([key, svc]) => {
        const card = document.createElement('div');
        card.className = 'service-card';

        // Header
        const header = document.createElement('div');
        header.className = 'service-header';

        const icon = document.createElement('span');
        icon.className = 'service-icon';
        icon.textContent = svc.icon || '🔧';

        const info = document.createElement('div');
        const name = document.createElement('div');
        name.className = 'service-name';
        name.textContent = svc.name || key;
        const desc = document.createElement('div');
        desc.className = 'service-desc';
        desc.textContent = svc.description || '';
        info.appendChild(name);
        info.appendChild(desc);

        const actions = document.createElement('div');
        actions.style.marginLeft = 'auto';

        const btnConnectAll = document.createElement('button');
        btnConnectAll.className = 'win95-btn small';
        btnConnectAll.textContent = 'CONNECT ALL';
        btnConnectAll.onclick = () => connectService(key);

        const btnDisconnectAll = document.createElement('button');
        btnDisconnectAll.className = 'win95-btn small';
        btnDisconnectAll.textContent = 'DISCONNECT ALL';
        btnDisconnectAll.onclick = () => disconnectService(key);

        actions.appendChild(btnConnectAll);
        actions.appendChild(btnDisconnectAll);

        header.appendChild(icon);
        header.appendChild(info);
        header.appendChild(actions);
        card.appendChild(header);

        // Tunnels
        (svc.tunnels || []).forEach(tunnel => {
            const tname = `${key}-${tunnel.name}`;
            const row = document.createElement('div');
            row.className = 'tunnel-row';

            const tinfo = document.createElement('div');
            tinfo.className = 'tunnel-info';

            const tnameEl = document.createElement('div');
            tnameEl.className = 'tunnel-name';
            tnameEl.textContent = tunnel.display || tunnel.name;

            const turl = document.createElement('div');
            turl.className = 'tunnel-url';
            turl.textContent = tunnel.url || `port ${tunnel.port}`;

            tinfo.appendChild(tnameEl);
            tinfo.appendChild(turl);

            const led = document.createElement('div');
            led.className = 'led';
            led.id = `led-${tname}`;

            const tactions = document.createElement('div');
            tactions.className = 'tunnel-actions';

            const btn = document.createElement('button');
            btn.className = 'win95-btn small';
            btn.id = `btn-${tname}`;
            btn.textContent = 'CONNECT';
            btn.onclick = () => toggleTunnel(key, tunnel.name);

            const btnAuto = document.createElement('button');
            btnAuto.className = 'win95-btn small';
            btnAuto.id = `auto-${tname}`;
            btnAuto.textContent = 'AUTO';
            btnAuto.title = 'Avvio automatico al login (spento = zero attività in background)';
            btnAuto.onclick = () => toggleAuto(key, tunnel.name);

            tactions.appendChild(btn);
            tactions.appendChild(btnAuto);

            row.appendChild(tinfo);
            row.appendChild(led);
            row.appendChild(tactions);
            card.appendChild(row);
        });

        container.appendChild(card);
    });

    addLog(`Loaded ${Object.keys(services).length} service(s)`, 'info');
}

// Tunnel actions — FIX: route generiche
async function toggleTunnel(svcKey, tunnelName) {
    const btn = document.getElementById(`btn-${svcKey}-${tunnelName}`);
    const isConnected = btn && btn.textContent === 'DISCONNECT';

    addLog(`${isConnected ? 'Disconnecting' : 'Connecting'} ${svcKey}/${tunnelName}...`, 'info');
    showConnectAnimation(isConnected ? 'DISCONNECTING...' : 'CONNECTING...');

    try {
        const endpoint = isConnected ? 'disconnect' : 'connect';
        // FIX: /api/connect/<service_key>/<tunnel_name>
        const res = await fetch(`${API}/${endpoint}/${svcKey}/${tunnelName}`, { method: 'POST' });
        const data = await res.json();

        setTimeout(() => {
            if (data.success) {
                showSuccess(isConnected ? 'DISCONNECTED' : 'CONNECTED ✓');
                addLog(`${svcKey}/${tunnelName} ${isConnected ? 'disconnected' : 'connected'}`, 'info');
            } else {
                showError(data.error || 'Operation failed');
            }
            refreshStatus();
        }, 1000);
    } catch(e) {
        showError(e.message);
    }
}

// FIX: /api/connect/service/<service_key>
async function connectService(svcKey) {
    addLog(`Connecting service ${svcKey}...`, 'info');
    showConnectAnimation(`CONNECTING ${svcKey.toUpperCase()}...`);

    try {
        const res = await fetch(`${API}/connect/service/${svcKey}`, { method: 'POST' });
        const data = await res.json();

        setTimeout(() => {
            if (data.success) {
                showSuccess('SERVICE CONNECTED ✓');
                addLog(`Service ${svcKey} connected`, 'info');
            } else {
                const failed = Object.entries(data.results || {})
                    .filter(([, ok]) => !ok).map(([t]) => t).join(', ');
                showError('Tunnels falliti: ' + (failed || 'unknown'));
                addLog(`Service ${svcKey}: falliti → ${failed}`, 'error');
            }
            refreshStatus();
        }, 1500);
    } catch(e) {
        showError(e.message);
    }
}

// FIX: /api/disconnect/service/<service_key>
async function disconnectService(svcKey) {
    addLog(`Disconnecting service ${svcKey}...`, 'info');

    try {
        await fetch(`${API}/disconnect/service/${svcKey}`, { method: 'POST' });
        addLog(`Service ${svcKey} disconnected`, 'info');
        refreshStatus();
    } catch(e) {
        addLog('Error: ' + e.message, 'error');
    }
}

// AUTO: interruttore avvio automatico — spento = zero attività in background
async function toggleAuto(svcKey, tunnelName) {
    const btn = document.getElementById(`auto-${svcKey}-${tunnelName}`);
    const isOn = btn && btn.classList.contains('on');
    const action = isOn ? 'noauto' : 'auto';
    addLog(`${isOn ? 'Disattivazione' : 'Attivazione'} AUTO per ${svcKey}/${tunnelName}...`, 'info');

    try {
        const res = await fetch(`${API}/auto/${svcKey}/${tunnelName}/${action}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showSuccess(isOn ? 'AUTO OFF' : 'AUTO ON ✓');
            addLog(`AUTO ${isOn ? 'disattivato' : 'attivato'} per ${svcKey}/${tunnelName}`, 'info');
        } else {
            showError('AUTO fallito: ' + (data.error || ''));
        }
        refreshStatus();
    } catch(e) {
        showError(e.message);
    }
}

// System actions
async function mount() {
    addLog('Mounting Windows folders...', 'info');
    try {
        const res = await fetch(`${API}/mount`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showSuccess('MOUNTED ✓');
            addLog('Folders mounted', 'info');
        } else {
            showError('Mount failed: ' + (data.error || 'Unknown'));
        }
        refreshStatus();
    } catch(e) {
        showError(e.message);
    }
}

async function unmount() {
    addLog('Unmounting folders...', 'info');
    try {
        await fetch(`${API}/unmount`, { method: 'POST' });
        addLog('Folders unmounted', 'info');
        refreshStatus();
    } catch(e) {
        addLog('Error: ' + e.message, 'error');
    }
}

// FIX: openTerminal chiama /api/open-terminal
async function openTerminal() {
    addLog('Opening terminal...', 'info');
    try {
        const res = await fetch(`${API}/open-terminal`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            addLog('Terminal opened', 'info');
        } else {
            showError('Failed to open terminal: ' + (data.error || ''));
        }
    } catch(e) {
        showError(e.message);
    }
}

async function openFolder() {
    addLog('Opening folder...', 'info');
    try {
        const res = await fetch(`${API}/open-folder`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            addLog('Folder opened', 'info');
        } else {
            showError('Failed to open folder: ' + (data.error || 'Not mounted?'));
        }
    } catch(e) {
        showError(e.message);
    }
}

// Config
async function loadConfig() {
    try {
        const res = await fetch(`${API}/config`);
        const data = await res.json();
        setInput('cfg-win-user', data.WIN_USER);
        setInput('cfg-win-ip', data.WIN_IP);
        setInput('cfg-win-folder', data.WIN_FOLDER);
        // FIX 3: mostra default se MOUNT_POINT non è nel config
        setInput('cfg-mount-point', data.MOUNT_POINT || '~/.local/share/lovypc/pc-windows (default)');
        addLog('Config loaded', 'info');
    } catch(e) {
        addLog('Config load failed: ' + e.message, 'error');
    }
}

function setInput(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val || '';
}

async function saveConfig() {
    const config = {
        WIN_USER: getInput('cfg-win-user'),
        WIN_IP: getInput('cfg-win-ip'),
        WIN_FOLDER: getInput('cfg-win-folder')
        // MOUNT_POINT escluso: si modifica in ~/.config/pcwin.conf
    };

    try {
        const res = await fetch(`${API}/config`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
        const data = await res.json();
        if (data.success) {
            showSuccess('SAVED ✓');
            addLog('Config saved (backup: pcwin.conf.bak)', 'info');
        } else {
            showError('Save failed: ' + (data.error || ''));
        }
    } catch(e) {
        showError(e.message);
    }
}

function getInput(id) {
    const el = document.getElementById(id);
    return el ? el.value : '';
}

// NOVITÀ v7.3: setup SSH senza password dalla GUI
async function setupSsh() {
    addLog('Setup SSH: controllo accesso senza password...', 'info');
    try {
        const res = await fetch(`${API}/setup-ssh`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showSuccess('SSH OK ✓');
            addLog(data.output || 'SSH setup completato', 'info');
        } else {
            showError('SSH setup fallito: ' + (data.error || ''));
        }
    } catch(e) {
        showError(e.message);
    }
}

// Animations
function showConnectAnimation(text) {
    const overlay = document.getElementById('connect-overlay');
    const progress = document.getElementById('progress-fill');
    if (!overlay || !progress) return;

    document.getElementById('connect-text').textContent = text;
    overlay.classList.add('active');
    progress.style.width = '0%';
    playModemSound();

    let width = 0;
    const interval = setInterval(() => {
        width += Math.random() * 30;
        if (width > 100) width = 100;
        progress.style.width = width + '%';
        if (width >= 100) {
            clearInterval(interval);
            setTimeout(() => overlay.classList.remove('active'), 400);
        }
    }, 250);
}

function showError(msg) {
    const errMsg = document.getElementById('error-msg');
    const overlay = document.getElementById('error-overlay');
    if (errMsg) errMsg.textContent = msg;
    if (overlay) overlay.classList.add('active');
    playErrorSound();
    addLog('ERROR: ' + msg, 'error');
}

function closeError() {
    const overlay = document.getElementById('error-overlay');
    if (overlay) overlay.classList.remove('active');
}

function showSuccess(msg) {
    const flash = document.getElementById('success-flash');
    if (!flash) return;
    flash.textContent = msg;
    flash.classList.add('active');
    playSuccessSound();
    setTimeout(() => flash.classList.remove('active'), 1500);
}

// Drag
let isDragging = false, currentX, currentY, initialX, initialY;
const windowEl = document.getElementById('main-window');
const titleBar = document.querySelector('.title-bar');

if (titleBar && windowEl) {
    titleBar.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('title-bar-button')) return;
        isDragging = true;
        initialX = e.clientX - windowEl.offsetLeft;
        initialY = e.clientY - windowEl.offsetTop;
    });
}

document.addEventListener('mousemove', (e) => {
    if (!isDragging || !windowEl) return;
    e.preventDefault();
    currentX = e.clientX - initialX;
    currentY = e.clientY - initialY;
    windowEl.style.left = currentX + 'px';
    windowEl.style.top = currentY + 'px';
    windowEl.style.transform = 'none';
});

document.addEventListener('mouseup', () => { isDragging = false; });

// Init
window.onload = async () => {
    addLog('LovyPC GUI v7.3 started', 'info');

    // Health check
    try {
        const res = await fetch(`${API}/health`);
        const health = await res.json();
        if (health.status === 'ok') {
            addLog(`Backend v${health.version} ready`, 'info');
            if (!health.pcwin_found) {
                addLog('WARNING: pcwin not found in PATH', 'warning');
            }
        }
    } catch(e) {
        addLog('Backend non raggiungibile — avvia server.py', 'error');
        showError('Backend non raggiungibile. Avvia: python server.py');
    }

    initTabs();
    await loadServices();  // FIX: aspetta che i LED esistano nel DOM
    await loadConfig();
    await refreshStatus();

    // Polling adattivo
    function scheduleNextPoll() {
        const anyActive = document.querySelectorAll('.led.active').length > 0;
        const interval = anyActive ? 5000 : 15000;
        setTimeout(async () => {
            await refreshStatus();
            scheduleNextPoll();
        }, interval);
    }
    scheduleNextPoll();
};
