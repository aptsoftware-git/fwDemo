import React, { useState } from 'react';
import { deleteDataset } from '../api/client';

const DatasetManager = ({ datasets, onDatasetDeleted }) => {
  const [deleting, setDeleting] = useState(null);
  const [showConfirm, setShowConfirm] = useState(null);

  const handleDeleteClick = (tag) => {
    setShowConfirm(tag);
  };

  const handleConfirmDelete = async (tag) => {
    setDeleting(tag);
    try {
      await deleteDataset(tag);
      setShowConfirm(null);
      if (onDatasetDeleted) {
        onDatasetDeleted(tag);
      }
    } catch (err) {
      alert(`Failed to delete dataset: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDeleting(null);
    }
  };

  const handleCancelDelete = () => {
    setShowConfirm(null);
  };

  if (datasets.length === 0) {
    return (
      <div className="section">
        <h2>Manage Datasets</h2>
        <p style={{ color: '#666' }}>No datasets uploaded yet. Upload data to get started.</p>
      </div>
    );
  }

  return (
    <div className="section">
      <h2>Manage Datasets</h2>
      <p style={{ color: '#666', fontSize: '14px', marginBottom: '15px' }}>
        View and delete uploaded datasets. Deleting a dataset will remove all associated units and data.
      </p>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          fontSize: '14px'
        }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #ddd', backgroundColor: '#f5f5f5' }}>
              <th style={{ padding: '12px', textAlign: 'left' }}>Tag</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Month</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Description</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Units</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Upload Date</th>
              <th style={{ padding: '12px', textAlign: 'center' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '12px', fontWeight: 'bold' }}>{dataset.tag}</td>
                <td style={{ padding: '12px' }}>{dataset.month_label}</td>
                <td style={{ padding: '12px', color: '#666' }}>{dataset.description || '-'}</td>
                <td style={{ padding: '12px', textAlign: 'center' }}>{dataset.unit_count}</td>
                <td style={{ padding: '12px', color: '#666', fontSize: '13px' }}>
                  {new Date(dataset.upload_date).toLocaleString()}
                </td>
                <td style={{ padding: '12px', textAlign: 'center' }}>
                  {showConfirm === dataset.tag ? (
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                      <button
                        onClick={() => handleConfirmDelete(dataset.tag)}
                        disabled={deleting === dataset.tag}
                        style={{
                          padding: '6px 12px',
                          fontSize: '13px',
                          backgroundColor: '#e74c3c',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: deleting === dataset.tag ? 'not-allowed' : 'pointer',
                          opacity: deleting === dataset.tag ? 0.6 : 1
                        }}
                      >
                        {deleting === dataset.tag ? 'Deleting...' : 'Confirm'}
                      </button>
                      <button
                        onClick={handleCancelDelete}
                        disabled={deleting === dataset.tag}
                        style={{
                          padding: '6px 12px',
                          fontSize: '13px',
                          backgroundColor: '#95a5a6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: deleting === dataset.tag ? 'not-allowed' : 'pointer'
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleDeleteClick(dataset.tag)}
                      disabled={deleting !== null}
                      style={{
                        padding: '6px 16px',
                        fontSize: '13px',
                        backgroundColor: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: deleting !== null ? 'not-allowed' : 'pointer',
                        opacity: deleting !== null ? 0.6 : 1
                      }}
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {showConfirm && (
        <div style={{ 
          marginTop: '15px', 
          padding: '12px', 
          backgroundColor: '#fff3cd', 
          border: '1px solid #ffc107',
          borderRadius: '4px',
          color: '#856404'
        }}>
          <strong>⚠️ Warning:</strong> Are you sure you want to delete dataset "{showConfirm}"? 
          This action cannot be undone and will remove all associated data.
        </div>
      )}
    </div>
  );
};

export default DatasetManager;
