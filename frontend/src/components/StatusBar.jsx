import React from 'react';

function StatusBar({ viewerStatus, outputStatus }) {
  return (
    <div className="status-bar">
      <div className="status-indicator">
        <span className={`status-dot ${viewerStatus.running ? 'running' : ''}`}></span>
        <span>
          Viewer: {viewerStatus.running ? viewerStatus.source || 'Active' : 'Stopped'}
        </span>
      </div>

      <div className="status-indicator">
        <span className={`status-dot ${outputStatus.running ? 'running' : ''}`}></span>
        <span>
          Output: {outputStatus.running ? outputStatus.name || 'Active' : 'Stopped'}
        </span>
      </div>
    </div>
  );
}

export default StatusBar;
