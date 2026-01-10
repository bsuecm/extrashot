/**
 * NDI Controller API Client
 */

const API_BASE = '/api';

async function handleResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'API request failed');
  }
  return data;
}

export const ndiApi = {
  // Auth
  async login(username, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return handleResponse(res);
  },

  async logout() {
    const res = await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
    return handleResponse(res);
  },

  async getAuthStatus() {
    const res = await fetch(`${API_BASE}/auth/status`);
    return handleResponse(res);
  },

  async changeCredentials(currentPassword, newUsername, newPassword) {
    const res = await fetch(`${API_BASE}/auth/credentials`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: currentPassword,
        username: newUsername || undefined,
        password: newPassword || undefined
      })
    });
    return handleResponse(res);
  },

  // Sources
  async getSources() {
    const res = await fetch(`${API_BASE}/sources/`);
    return handleResponse(res);
  },

  async refreshSources(timeout = 8) {
    const res = await fetch(`${API_BASE}/sources/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timeout })
    });
    return handleResponse(res);
  },

  async getExtraIPs() {
    const res = await fetch(`${API_BASE}/sources/extra-ips`);
    return handleResponse(res);
  },

  async setExtraIPs(ips) {
    const res = await fetch(`${API_BASE}/sources/extra-ips`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ips })
    });
    return handleResponse(res);
  },

  async addExtraIP(ip) {
    const res = await fetch(`${API_BASE}/sources/extra-ips`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip })
    });
    return handleResponse(res);
  },

  async removeExtraIP(ip) {
    const res = await fetch(`${API_BASE}/sources/extra-ips/${encodeURIComponent(ip)}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // Viewer
  async startViewer(source, options = {}) {
    const res = await fetch(`${API_BASE}/viewer/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source,
        backup: options.backup,
        audio: options.audio || false,
        fullscreen: options.fullscreen !== false,
        resolution: options.resolution || '1920x1080'
      })
    });
    return handleResponse(res);
  },

  async stopViewer() {
    const res = await fetch(`${API_BASE}/viewer/stop`, { method: 'POST' });
    return handleResponse(res);
  },

  async switchSource(source, options = {}) {
    const res = await fetch(`${API_BASE}/viewer/switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source,
        backup: options.backup,
        audio: options.audio || false,
        fullscreen: options.fullscreen !== false,
        resolution: options.resolution || '1920x1080'
      })
    });
    return handleResponse(res);
  },

  async getViewerStatus() {
    const res = await fetch(`${API_BASE}/viewer/status`);
    return handleResponse(res);
  },

  // PTZ
  async ptzMove(panSpeed, tiltSpeed) {
    const res = await fetch(`${API_BASE}/ptz/move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pan_speed: panSpeed, tilt_speed: tiltSpeed })
    });
    return handleResponse(res);
  },

  async ptzStop() {
    const res = await fetch(`${API_BASE}/ptz/stop`, { method: 'POST' });
    return handleResponse(res);
  },

  async ptzZoom(speed) {
    const res = await fetch(`${API_BASE}/ptz/zoom`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed })
    });
    return handleResponse(res);
  },

  async ptzRecallPreset(preset, speed = 1.0) {
    const res = await fetch(`${API_BASE}/ptz/preset/recall`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset, speed })
    });
    return handleResponse(res);
  },

  async ptzStorePreset(preset) {
    const res = await fetch(`${API_BASE}/ptz/preset/store`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset })
    });
    return handleResponse(res);
  },

  async ptzAutoFocus() {
    const res = await fetch(`${API_BASE}/ptz/focus`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auto: true })
    });
    return handleResponse(res);
  },

  async ptzWhiteBalance(mode, red = null, blue = null) {
    const body = { mode };
    if (mode === 'manual' && red !== null && blue !== null) {
      body.red = red;
      body.blue = blue;
    }
    const res = await fetch(`${API_BASE}/ptz/whitebalance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return handleResponse(res);
  },

  async ptzExposure(auto, level = null) {
    const body = auto ? { auto: true } : { level };
    const res = await fetch(`${API_BASE}/ptz/exposure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return handleResponse(res);
  },

  // Output
  async startOutput(config) {
    const res = await fetch(`${API_BASE}/output/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return handleResponse(res);
  },

  async stopOutput() {
    const res = await fetch(`${API_BASE}/output/stop`, { method: 'POST' });
    return handleResponse(res);
  },

  async getOutputStatus() {
    const res = await fetch(`${API_BASE}/output/status`);
    return handleResponse(res);
  },

  async getDevices() {
    const res = await fetch(`${API_BASE}/output/devices`);
    return handleResponse(res);
  },

  // Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  }
};

export default ndiApi;
