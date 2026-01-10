import React from 'react';

function SourceSelector({ sources, selectedSource, onSelect, onRefresh, loading }) {
  return (
    <div className="source-selector">
      <div className="source-header">
        <h3>NDI Sources</h3>
        <button
          className="secondary"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? 'Scanning...' : 'Refresh'}
        </button>
      </div>

      {sources.length === 0 ? (
        <p className="no-sources">
          {loading ? 'Scanning network...' : 'No NDI sources found'}
        </p>
      ) : (
        <ul className="source-list">
          {sources.map((source, index) => {
            const isActive = selectedSource === source.name;
            return (
              <li
                key={index}
                className={`source-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelect(source.name)}
              >
                <span className="source-name">{source.name}</span>
                {source.address && (
                  <span className="source-address">{source.address}</span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default SourceSelector;
