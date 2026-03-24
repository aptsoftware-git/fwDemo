import React, { useState, useRef } from 'react';
import { uploadDirectory } from '../api/client';

/**
 * GENERIC FEATURE: This component is currently hidden for demo purposes.
 * See DemoLoadPanel.jsx for the simplified demo version.
 * To re-enable: Uncomment import and usage in App.jsx
 */
const UploadPanel = ({ onUploadSuccess }) => {
  const [directoryPath, setDirectoryPath] = useState('');
  const [tag, setTag] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [errors, setErrors] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleDirectorySelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
    
    if (files.length > 0) {
      // Extract the common directory path from all files
      const firstFile = files[0].webkitRelativePath || files[0].name;
      const pathParts = firstFile.split('/');
      
      // Build the most specific common directory path
      let commonPath = '';
      if (pathParts.length > 1) {
        // Remove the filename to get directory path
        const dirParts = pathParts.slice(0, -1);
        
        // Find the common path among all files
        for (let i = 0; i < dirParts.length; i++) {
          const testPath = dirParts.slice(0, i + 1).join('/');
          const allMatch = files.every(file => {
            const fp = file.webkitRelativePath || file.name;
            return fp.startsWith(testPath + '/') || fp.startsWith(testPath);
          });
          
          if (allMatch) {
            commonPath = testPath;
          } else {
            break;
          }
        }
      } else {
        // Single level, just use the name
        commonPath = pathParts[0];
      }
      
      // Convert forward slashes to backslashes for Windows paths
      const windowsPath = commonPath.replace(/\//g, '\\');
      setDirectoryPath(windowsPath);
      
      setMessage({ 
        type: 'info', 
        text: `Selected ${files.length} file(s). Detected path: "${windowsPath}". Prepend the full base path (e.g., C:\\data\\FRS_Sample\\) if needed.` 
      });
    }
  };

  const handleBrowse = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!directoryPath) {
      setMessage({ type: 'error', text: 'Please enter a directory path' });
      return;
    }

    setLoading(true);
    setMessage(null);
    setErrors([]);

    try {
      const result = await uploadDirectory(directoryPath, tag || null, description || null);
      
      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: `${result.message}${result.errors.length > 0 ? ` (${result.errors.length} warnings)` : ''}` 
        });
        setErrors(result.errors);
        setDirectoryPath('');
        setTag('');
        setDescription('');
        
        if (onUploadSuccess) {
          onUploadSuccess(result.dataset);
        }
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Upload failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="section">
      <h2>Upload FRS Data</h2>
      <form onSubmit={handleUpload}>
        <div className="form-group">
          <label htmlFor="directoryPath">Directory Path *</label>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
            <input
              type="text"
              id="directoryPath"
              value={directoryPath}
              onChange={(e) => setDirectoryPath(e.target.value)}
              placeholder="e.g., C:\Anu\APT\apt\army\fortwilliam\code\demo1\data\FRS_Sample\Nov"
              disabled={loading}
              style={{ flex: 1 }}
            />
            <button 
              type="button" 
              onClick={handleBrowse}
              disabled={loading}
              className="secondary"
              style={{ minWidth: '100px' }}
            >
              Browse...
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            webkitdirectory="true"
            directory="true"
            multiple
            onChange={handleDirectorySelect}
            style={{ display: 'none' }}
          />
          <small style={{ color: '#666', fontSize: '12px', display: 'block', marginTop: '5px' }}>
            <strong>How to provide the full path:</strong><br/>
            1. Click "Browse" to select directory → relative path will appear above<br/>
            2. Edit to add the base path (e.g., C:\Anu\APT\apt\army\fortwilliam\code\demo1\data\FRS_Sample\)<br/>
            3. OR right-click folder in File Explorer → "Copy as path" → Paste directly<br/>
            4. Final path example: <code style={{ background: '#f0f0f0', padding: '2px 4px' }}>C:\Anu\APT\apt\army\fortwilliam\code\demo1\data\FRS_Sample\Nov</code><br/>
            <em style={{ color: '#e67e22' }}>Note: Browsers cannot access full filesystem paths for security reasons</em>
          </small>
          {selectedFiles.length > 0 && (
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#27ae60' }}>
              ✓ {selectedFiles.length} file(s) selected. Edit the path above to add the base directory (e.g., C:\data\) before the detected path.
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="tag">Tag (optional)</label>
          <input
            type="text"
            id="tag"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="e.g., Fmn November 2025 (auto-generated if empty)"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description (optional)</label>
          <input
            type="text"
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description"
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>

        {message && (
          <div className={
            message.type === 'error' ? 'error' : 
            message.type === 'success' ? 'success' : 
            'info'
          } style={{ marginTop: '10px' }}>
            {message.text}
          </div>
        )}

        {errors.length > 0 && (
          <div style={{ marginTop: '10px', fontSize: '13px' }}>
            <strong>Warnings:</strong>
            <ul style={{ marginTop: '5px', marginLeft: '20px' }}>
              {errors.map((error, index) => (
                <li key={index} style={{ color: '#e67e22' }}>{error}</li>
              ))}
            </ul>
          </div>
        )}
      </form>
    </div>
  );
};

export default UploadPanel;
