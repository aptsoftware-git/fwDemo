import React, { useState } from 'react';
import { loadDemoData, cleanDemoData } from '../api/client';

/**
 * DEMO: Simplified panel for loading hardcoded demo data
 * Replaces the generic UploadPanel for demo purposes
 */
const DemoLoadPanel = ({ onLoadSuccess }) => {
  const [loadingLoad, setLoadingLoad] = useState(false);
  const [loadingClean, setLoadingClean] = useState(false);
  const [message, setMessage] = useState(null);

  const handleLoad = async () => {
    setLoadingLoad(true);
    setMessage(null);

    try {
      const result = await loadDemoData();
      setMessage({ 
        type: 'success', 
        text: result.message
      });
      
      if (onLoadSuccess) {
        onLoadSuccess();
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || error.message || 'Failed to load demo data'
      });
    } finally {
      setLoadingLoad(false);
    }
  };

  const handleClean = async () => {
    if (!window.confirm('Are you sure you want to delete all data from the database? This action cannot be undone.')) {
      return;
    }

    setLoadingClean(true);
    setMessage(null);

    try {
      const result = await cleanDemoData();
      setMessage({ 
        type: 'success', 
        text: result.message
      });
      
      if (onLoadSuccess) {
        onLoadSuccess();
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || error.message || 'Failed to clean data'
      });
    } finally {
      setLoadingClean(false);
    }
  };

  return (
    <div className="section">
      <h2>Load Demo Data</h2>
      <div style={{ marginBottom: '15px', color: '#666' }}>
        <p>Load Formation D data for November and December 2025.</p>
        <p style={{ fontSize: '13px', marginTop: '5px' }}>
          <strong>Data source:</strong> C:\Anu\APT\apt\army\fortwilliam\code\fwDemo\data\FRS_cleaned
        </p>
      </div>
      
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <button 
          onClick={handleLoad} 
          disabled={loadingLoad || loadingClean}
          style={{ minWidth: '120px' }}
        >
          {loadingLoad ? 'Loading...' : 'Load Data'}
        </button>
        
        <button 
          onClick={handleClean} 
          disabled={loadingLoad || loadingClean}
          className="secondary"
          style={{ 
            minWidth: '120px',
            backgroundColor: '#e74c3c',
            color: 'white',
            border: 'none'
          }}
        >
          {loadingClean ? 'Cleaning...' : 'Clean Database'}
        </button>
      </div>

      {message && (
        <div 
          className={message.type === 'error' ? 'error' : 'success'} 
          style={{ marginTop: '15px' }}
        >
          {message.text}
        </div>
      )}
    </div>
  );
};

export default DemoLoadPanel;
