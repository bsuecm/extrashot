import React, { useState, useEffect } from 'react';

function VideoPreview({ enabled }) {
  const [hasError, setHasError] = useState(false);
  const [key, setKey] = useState(0);

  // Reset error state when enabled changes
  useEffect(() => {
    if (enabled) {
      setHasError(false);
      setKey(prev => prev + 1);
    }
  }, [enabled]);

  if (!enabled) {
    return (
      <div className="video-preview">
        <div className="preview-placeholder">
          <span>No preview available</span>
          <span className="preview-hint">Start output to see preview</span>
        </div>
      </div>
    );
  }

  return (
    <div className="video-preview">
      {hasError ? (
        <div className="preview-placeholder">
          <span>Preview unavailable</span>
          <button
            className="secondary"
            onClick={() => { setHasError(false); setKey(prev => prev + 1); }}
          >
            Retry
          </button>
        </div>
      ) : (
        <img
          key={key}
          src="/api/preview/stream"
          alt="Camera Preview"
          className="preview-stream"
          onError={() => setHasError(true)}
        />
      )}
    </div>
  );
}

export default VideoPreview;
