import React, { useState, useEffect, useCallback } from 'react';
import { ndiApi } from './api/ndiApi';
import SourceSelector from './components/SourceSelector';
import PTZControls from './components/PTZControls';
import OutputManager from './components/OutputManager';
import IPManager from './components/IPManager';
import StatusBar from './components/StatusBar';

function App() {
  const [view, setView] = useState('viewer');
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState(null);
  const [viewerStatus, setViewerStatus] = useState({ running: false });
  const [outputStatus, setOutputStatus] = useState({ running: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSources = useCallback(async () => {
    try {
      const data = await ndiApi.getSources();
      setSources(data.sources || []);
    } catch (err) {
      console.error('Failed to fetch sources:', err);
    }
  }, []);

  const fetchStatus = useCallback(async () => {
    try {
      const [viewer, output] = await Promise.all([
        ndiApi.getViewerStatus(),
        ndiApi.getOutputStatus()
      ]);
      setViewerStatus(viewer);
      setOutputStatus(output);
      if (viewer.source) {
        setSelectedSource(viewer.source);
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  }, []);

  useEffect(() => {
    fetchSources();
    fetchStatus();
    const interval = setInterval(() => {
      fetchSources();
      fetchStatus();
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchSources, fetchStatus]);

  const handleRefreshSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ndiApi.refreshSources(8);
      setSources(data.sources || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSource = async (source) => {
    setError(null);
    try {
      if (viewerStatus.running) {
        await ndiApi.switchSource(source);
      } else {
        await ndiApi.startViewer(source);
      }
      setSelectedSource(source);
      await fetchStatus();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStopViewer = async () => {
    setError(null);
    try {
      await ndiApi.stopViewer();
      setSelectedSource(null);
      await fetchStatus();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Extrashot</h1>
        <nav>
          <button
            className={view === 'viewer' ? 'active' : ''}
            onClick={() => setView('viewer')}
          >
            Viewer
          </button>
          <button
            className={view === 'output' ? 'active' : ''}
            onClick={() => setView('output')}
          >
            Output
          </button>
          <button
            className={view === 'settings' ? 'active' : ''}
            onClick={() => setView('settings')}
          >
            Settings
          </button>
        </nav>
      </header>

      <main>
        {error && <div className="alert error">{error}</div>}

        {view === 'viewer' && (
          <div className="viewer-panel">
            <SourceSelector
              sources={sources}
              selectedSource={selectedSource}
              onSelect={handleSelectSource}
              onRefresh={handleRefreshSources}
              loading={loading}
            />

            <div className="card">
              <h2>Viewer</h2>
              {viewerStatus.running ? (
                <div>
                  <p>Now viewing: <strong>{selectedSource}</strong></p>
                  <button onClick={handleStopViewer}>Stop Viewer</button>
                </div>
              ) : (
                <p className="no-sources">Select a source to start viewing</p>
              )}
            </div>

            <PTZControls
              enabled={viewerStatus.running}
              onError={setError}
            />
          </div>
        )}

        {view === 'output' && (
          <OutputManager
            status={outputStatus}
            onStatusChange={fetchStatus}
            onError={setError}
          />
        )}

        {view === 'settings' && (
          <IPManager onError={setError} />
        )}
      </main>

      <StatusBar
        viewerStatus={viewerStatus}
        outputStatus={outputStatus}
      />
    </div>
  );
}

export default App;
