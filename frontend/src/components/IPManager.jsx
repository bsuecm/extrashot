import React, { useState, useEffect, useCallback } from 'react';
import { ndiApi } from '../api/ndiApi';

function IPManager({ onError }) {
  const [ips, setIps] = useState([]);
  const [newIp, setNewIp] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchIPs = useCallback(async () => {
    try {
      const data = await ndiApi.getExtraIPs();
      setIps(data.ips || []);
    } catch (err) {
      console.error('Failed to fetch IPs:', err);
    }
  }, []);

  useEffect(() => {
    fetchIPs();
  }, [fetchIPs]);

  const handleAdd = async () => {
    if (!newIp.trim()) return;

    // Basic IP validation
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipRegex.test(newIp.trim())) {
      onError('Invalid IP address format');
      return;
    }

    setLoading(true);
    try {
      await ndiApi.addExtraIP(newIp.trim());
      setNewIp('');
      await fetchIPs();
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (ip) => {
    setLoading(true);
    try {
      await ndiApi.removeExtraIP(ip);
      await fetchIPs();
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAdd();
    }
  };

  return (
    <div className="card">
      <h2>Extra IP Addresses</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
        Add IP addresses for NDI sources outside your local subnet.
        Changes take effect on next source refresh.
      </p>

      {ips.length === 0 ? (
        <p className="no-sources">No extra IPs configured</p>
      ) : (
        <ul className="ip-list">
          {ips.map((ip, index) => (
            <li key={index} className="ip-item">
              <span>{ip}</span>
              <button
                onClick={() => handleRemove(ip)}
                disabled={loading}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="ip-add">
        <input
          type="text"
          value={newIp}
          onChange={(e) => setNewIp(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="192.168.1.100"
          disabled={loading}
        />
        <button onClick={handleAdd} disabled={loading || !newIp.trim()}>
          Add
        </button>
      </div>
    </div>
  );
}

export default IPManager;
