import React, { useState } from 'react';
import { ndiApi } from '../api/ndiApi';

function CredentialsManager({ onError }) {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccess(null);

    if (!currentPassword) {
      onError('Current password is required');
      return;
    }

    if (!newUsername && !newPassword) {
      onError('Enter a new username or password to change');
      return;
    }

    if (newPassword && newPassword !== confirmPassword) {
      onError('New passwords do not match');
      return;
    }

    if (newPassword && newPassword.length < 4) {
      onError('Password must be at least 4 characters');
      return;
    }

    setLoading(true);
    try {
      await ndiApi.changeCredentials(
        currentPassword,
        newUsername || null,
        newPassword || null
      );
      setSuccess('Credentials updated successfully');
      setCurrentPassword('');
      setNewUsername('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Account Settings</h2>

      <form onSubmit={handleSubmit}>
        {success && <div className="alert success">{success}</div>}

        <div className="settings-section">
          <h3>Change Credentials</h3>

          <div className="form-group">
            <label htmlFor="currentPassword">Current Password *</label>
            <input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="Enter current password"
              autoComplete="current-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="newUsername">New Username (optional)</label>
            <input
              id="newUsername"
              type="text"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              placeholder="Leave blank to keep current"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">New Password (optional)</label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Leave blank to keep current"
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
              autoComplete="new-password"
              disabled={!newPassword}
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Updating...' : 'Update Credentials'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CredentialsManager;
