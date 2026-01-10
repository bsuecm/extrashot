import React, { useState, useEffect, useCallback } from 'react';
import { ndiApi } from '../api/ndiApi';
import VideoPreview from './VideoPreview';

function OutputManager({ status, onStatusChange, onError }) {
  const [devices, setDevices] = useState({ v4l2: [], libcamera: [] });
  const [config, setConfig] = useState({
    name: 'Pi Camera',
    device: '',
    type: 'v4l2',
    width: 1920,
    height: 1080,
    fps: 30,
    groups: ''
  });
  const [loading, setLoading] = useState(false);

  const fetchDevices = useCallback(async () => {
    try {
      const data = await ndiApi.getDevices();
      setDevices(data);
      // Auto-select first available device
      if (data.v4l2?.length > 0 && !config.device) {
        setConfig(prev => ({ ...prev, device: data.v4l2[0], type: 'v4l2' }));
      } else if (data.libcamera?.length > 0 && !config.device) {
        setConfig(prev => ({ ...prev, device: data.libcamera[0], type: 'libcamera' }));
      }
    } catch (err) {
      console.error('Failed to fetch devices:', err);
    }
  }, [config.device]);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  const handleStart = async () => {
    setLoading(true);
    try {
      await ndiApi.startOutput({
        name: config.name,
        device: config.device,
        type: config.type,
        width: config.width,
        height: config.height,
        fps: config.fps,
        groups: config.groups || undefined
      });
      onStatusChange();
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await ndiApi.stopOutput();
      onStatusChange();
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const allDevices = [
    ...(devices.v4l2 || []).map(d => ({ path: d, type: 'v4l2' })),
    ...(devices.libcamera || []).map(d => ({ path: d, type: 'libcamera' }))
  ];

  return (
    <div className="card">
      <h2>NDI Output</h2>

      <div className="preview-label">Live Preview</div>
      <VideoPreview enabled={status.running} />

      {status.running ? (
        <div>
          <div className="alert success">
            Output running: <strong>{status.name}</strong>
          </div>
          <p>Device: {status.device}</p>
          <p>Resolution: {status.resolution}</p>
          <button onClick={handleStop} disabled={loading}>
            {loading ? 'Stopping...' : 'Stop Output'}
          </button>
        </div>
      ) : (
        <div className="output-form">
          <div className="form-group">
            <label>Stream Name</label>
            <input
              type="text"
              value={config.name}
              onChange={(e) => setConfig({ ...config, name: e.target.value })}
              placeholder="NDI stream name"
            />
          </div>

          <div className="form-group">
            <label>Camera Device</label>
            <select
              value={`${config.type}:${config.device}`}
              onChange={(e) => {
                const [type, ...pathParts] = e.target.value.split(':');
                const device = pathParts.join(':');
                setConfig({ ...config, type, device });
              }}
            >
              <option value="">Select a camera...</option>
              {allDevices.map((d, i) => (
                <option key={i} value={`${d.type}:${d.path}`}>
                  [{d.type}] {d.path}
                </option>
              ))}
            </select>
            <button
              className="secondary"
              onClick={fetchDevices}
              style={{ marginTop: '0.5rem' }}
            >
              Refresh Devices
            </button>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Width</label>
              <input
                type="number"
                value={config.width}
                onChange={(e) => setConfig({ ...config, width: parseInt(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>Height</label>
              <input
                type="number"
                value={config.height}
                onChange={(e) => setConfig({ ...config, height: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>FPS</label>
              <select
                value={config.fps}
                onChange={(e) => setConfig({ ...config, fps: parseInt(e.target.value) })}
              >
                <option value={24}>24</option>
                <option value={25}>25</option>
                <option value={30}>30</option>
                <option value={50}>50</option>
                <option value={60}>60</option>
              </select>
            </div>
            <div className="form-group">
              <label>NDI Groups (optional)</label>
              <input
                type="text"
                value={config.groups}
                onChange={(e) => setConfig({ ...config, groups: e.target.value })}
                placeholder="e.g., public, cameras"
              />
            </div>
          </div>

          <button onClick={handleStart} disabled={loading || !config.device}>
            {loading ? 'Starting...' : 'Start Output'}
          </button>
        </div>
      )}
    </div>
  );
}

export default OutputManager;
