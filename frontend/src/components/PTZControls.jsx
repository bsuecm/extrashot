import React, { useState, useCallback, useRef } from 'react';
import { ndiApi } from '../api/ndiApi';

function PTZControls({ enabled, onError }) {
  const [speed, setSpeed] = useState(0.5);
  const moveInterval = useRef(null);

  const startMove = useCallback((panSpeed, tiltSpeed) => {
    if (!enabled) return;

    const doMove = async () => {
      try {
        await ndiApi.ptzMove(panSpeed * speed, tiltSpeed * speed);
      } catch (err) {
        onError(err.message);
      }
    };

    doMove();
    moveInterval.current = setInterval(doMove, 100);
  }, [enabled, speed, onError]);

  const stopMove = useCallback(async () => {
    if (moveInterval.current) {
      clearInterval(moveInterval.current);
      moveInterval.current = null;
    }
    if (!enabled) return;
    try {
      await ndiApi.ptzStop();
    } catch (err) {
      onError(err.message);
    }
  }, [enabled, onError]);

  const handleZoom = useCallback(async (zoomSpeed) => {
    if (!enabled) return;
    try {
      await ndiApi.ptzZoom(zoomSpeed * speed);
    } catch (err) {
      onError(err.message);
    }
  }, [enabled, speed, onError]);

  const handlePreset = useCallback(async (preset) => {
    if (!enabled) return;
    try {
      await ndiApi.ptzRecallPreset(preset);
    } catch (err) {
      onError(err.message);
    }
  }, [enabled, onError]);

  const handleStorePreset = useCallback(async (preset) => {
    if (!enabled) return;
    if (window.confirm(`Store current position as Preset ${preset}?`)) {
      try {
        await ndiApi.ptzStorePreset(preset);
      } catch (err) {
        onError(err.message);
      }
    }
  }, [enabled, onError]);

  const handleAutoFocus = useCallback(async () => {
    if (!enabled) return;
    try {
      await ndiApi.ptzAutoFocus();
    } catch (err) {
      onError(err.message);
    }
  }, [enabled, onError]);

  return (
    <div className={`ptz-controls ${!enabled ? 'disabled' : ''}`}>
      <div className="ptz-section">
        <h3>Pan / Tilt</h3>
        <div className="ptz-pad">
          <div className="ptz-row">
            <button
              onMouseDown={() => startMove(-0.5, 0.5)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(-0.5, 0.5)}
              onTouchEnd={stopMove}
            >
              ↖
            </button>
            <button
              onMouseDown={() => startMove(0, 1)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(0, 1)}
              onTouchEnd={stopMove}
            >
              ↑
            </button>
            <button
              onMouseDown={() => startMove(0.5, 0.5)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(0.5, 0.5)}
              onTouchEnd={stopMove}
            >
              ↗
            </button>
          </div>
          <div className="ptz-row">
            <button
              onMouseDown={() => startMove(-1, 0)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(-1, 0)}
              onTouchEnd={stopMove}
            >
              ←
            </button>
            <button onClick={handleAutoFocus}>AF</button>
            <button
              onMouseDown={() => startMove(1, 0)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(1, 0)}
              onTouchEnd={stopMove}
            >
              →
            </button>
          </div>
          <div className="ptz-row">
            <button
              onMouseDown={() => startMove(-0.5, -0.5)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(-0.5, -0.5)}
              onTouchEnd={stopMove}
            >
              ↙
            </button>
            <button
              onMouseDown={() => startMove(0, -1)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(0, -1)}
              onTouchEnd={stopMove}
            >
              ↓
            </button>
            <button
              onMouseDown={() => startMove(0.5, -0.5)}
              onMouseUp={stopMove}
              onMouseLeave={stopMove}
              onTouchStart={() => startMove(0.5, -0.5)}
              onTouchEnd={stopMove}
            >
              ↘
            </button>
          </div>
        </div>
      </div>

      <div className="ptz-section">
        <h3>Zoom</h3>
        <div className="zoom-controls">
          <button
            onMouseDown={() => handleZoom(-1)}
            onMouseUp={() => handleZoom(0)}
            onMouseLeave={() => handleZoom(0)}
            onTouchStart={() => handleZoom(-1)}
            onTouchEnd={() => handleZoom(0)}
          >
            −
          </button>
          <button
            onMouseDown={() => handleZoom(1)}
            onMouseUp={() => handleZoom(0)}
            onMouseLeave={() => handleZoom(0)}
            onTouchStart={() => handleZoom(1)}
            onTouchEnd={() => handleZoom(0)}
          >
            +
          </button>
        </div>
      </div>

      <div className="ptz-section">
        <h3>Speed</h3>
        <input
          type="range"
          min="0.1"
          max="1"
          step="0.1"
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
        />
        <span>{Math.round(speed * 100)}%</span>
      </div>

      <div className="ptz-section">
        <h3>Presets</h3>
        <div className="preset-grid">
          {[1, 2, 3, 4, 5, 6].map((num) => (
            <button
              key={num}
              onClick={() => handlePreset(num)}
              onContextMenu={(e) => {
                e.preventDefault();
                handleStorePreset(num);
              }}
            >
              {num}
            </button>
          ))}
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          Click to recall, right-click to store
        </p>
      </div>
    </div>
  );
}

export default PTZControls;
