import React, { useState, useEffect } from 'react';
import { loadDemoData, getConfig } from '../api/client';

/**
 * DEMO: Simplified panel for loading hardcoded demo data
 * Replaces the generic UploadPanel for demo purposes
 */
const DemoLoadPanel = ({ onLoadSuccess }) => {
  const [loadingLoad, setLoadingLoad] = useState(false);
  const [message, setMessage] = useState(null);
  const [dataSource, setDataSource] = useState('Loading...');

  // Fetch config on component mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const config = await getConfig();
        setDataSource(config.demo_base_path);
      } catch (error) {
        console.error('Failed to fetch config:', error);
        setDataSource('Not available');
      }
    };
    fetchConfig();
  }, []);

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

  return (
    <div className="section">
      <h2>Load Data</h2>
      <div className="section-content">
        <div style={{ marginBottom: '15px', color: '#666' }}>
          <p>Load Formation D data for November and December 2025.</p>
          <p style={{ fontSize: '13px', marginTop: '5px' }}>
            <strong>Data source:</strong> {dataSource}
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button 
            onClick={handleLoad} 
            disabled={loadingLoad}
            style={{ minWidth: '120px' }}
          >
            {loadingLoad ? 'Loading...' : 'Load'}
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
    </div>
  );
};

export default DemoLoadPanel;
