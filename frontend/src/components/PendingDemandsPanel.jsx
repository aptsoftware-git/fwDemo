import React, { useState } from 'react';
import { getPendingDemands } from '../api/client';

const PendingDemandsPanel = ({ datasets }) => {
  const [demandsData, setDemandsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true);

  // Check if Remote Workshop December 2025 dataset exists
  const hasRemoteWorkshopDec = datasets.some(d => 
    d.tag.toLowerCase().includes('remote workshop') && 
    d.tag.toLowerCase().includes('december') && 
    d.tag.toLowerCase().includes('2025')
  );

  const handleGetDemands = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getPendingDemands();
      setDemandsData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch pending demands');
      setDemandsData(null);
    } finally {
      setLoading(false);
    }
  };

  if (!hasRemoteWorkshopDec) {
    return null; // Don't show the panel if Remote Workshop December dataset doesn't exist
  }

  return (
    <div className="section">
      <h2 
        className="collapsible-header" 
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span>2.1 Have Demands for equipment been placed?</span>
        <span className={`toggle-icon ${isExpanded ? '' : 'collapsed'}`}>▲</span>
      </h2>
      
      {isExpanded && (
        <div className="section-content">
          <h3 style={{ color: '#2c3e50', marginBottom: '15px', fontSize: '16px' }}>
            2.1.1 Have the Demands been controlled? Since how long are demands pending (not controlled)?
          </h3>
          <p style={{ color: '#666', marginBottom: '15px' }}>
            View all pending demands from Remote Workshop (December 2025) where Control date is blank or "NVR".
          </p>
      
          <button
            onClick={handleGetDemands}
            disabled={loading}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? 'Loading Demands...' : 'Show Pending Demands'}
          </button>

          {error && (
            <div style={{ 
              marginTop: '15px', 
              padding: '12px', 
              backgroundColor: '#fee', 
              color: '#c33',
              borderRadius: '4px'
            }}>
              {error}
            </div>
          )}

          {demandsData && (
            <div style={{ marginTop: '30px' }}>
              {/* Report Header */}
              <div style={{ 
                marginBottom: '20px', 
                paddingBottom: '15px', 
                borderBottom: '2px solid #3498db' 
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
                  {demandsData.title}
                </h3>
                <h4 style={{ margin: '0 0 10px 0', color: '#555', fontSize: '15px', fontWeight: 'normal' }}>
                  {demandsData.subtitle}
                </h4>
                <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                  Dataset: {demandsData.dataset} | Total Pending: <strong>{demandsData.total_pending}</strong>
                </p>
              </div>

              {/* Demands Table */}
              {demandsData.data?.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                  No pending demands found (all demands have been controlled)
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '50px' }}>S.No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '100px' }}>NMC Type</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '80px' }}>Category</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '100px' }}>Veh BA No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '80px' }}>Formation</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '150px' }}>Units</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '120px' }}>Maint Wksp</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '150px' }}>Item/Part No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '200px' }}>Nomenclature</th>
                        <th style={{ padding: '10px', textAlign: 'center', minWidth: '50px' }}>Qty</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '150px' }}>Demand No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '120px' }}>Demand Date</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '100px' }}>Control No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '120px' }}>Control Date</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '80px' }}>Depot</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '200px' }}>Remarks</th>
                        <th style={{ 
                          padding: '10px', 
                          textAlign: 'center', 
                          minWidth: '100px',
                          backgroundColor: '#fff3cd',
                          fontWeight: 'bold'
                        }}>
                          Pending (Days)
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {demandsData.data.map((row) => {
                        // Determine row color based on pending days
                        let rowColor = 'transparent';
                        if (row.pending_days !== null) {
                          if (row.pending_days > 90) {
                            rowColor = '#ffe6e6'; // Red tint for > 90 days
                          } else if (row.pending_days > 60) {
                            rowColor = '#fff3cd'; // Yellow tint for > 60 days
                          }
                        }

                        return (
                          <tr 
                            key={row.serial_no} 
                            style={{ 
                              borderBottom: '1px solid #eee',
                              backgroundColor: rowColor
                            }}
                          >
                            <td style={{ padding: '10px' }}>{row.serial_no}</td>
                            <td style={{ 
                              padding: '10px',
                              fontWeight: 'bold',
                              color: row.nmc_type === 'Eng' ? '#e74c3c' : row.nmc_type === 'MUA' ? '#f39c12' : '#3498db'
                            }}>
                              {row.nmc_type}
                            </td>
                            <td style={{ padding: '10px' }}>{row.category}</td>
                            <td style={{ padding: '10px' }}>{row.veh_ba_no}</td>
                            <td style={{ padding: '10px' }}>{row.formation}</td>
                            <td style={{ padding: '10px' }}>{row.units}</td>
                            <td style={{ padding: '10px' }}>{row.maint_wksp}</td>
                            <td style={{ padding: '10px' }}>{row.item_part_no}</td>
                            <td style={{ padding: '10px' }}>{row.nomenclature}</td>
                            <td style={{ padding: '10px', textAlign: 'center' }}>{row.qty}</td>
                            <td style={{ padding: '10px' }}>{row.demand_no}</td>
                            <td style={{ padding: '10px' }}>
                              {row.demand_dt ? new Date(row.demand_dt).toLocaleDateString('en-GB') : '-'}
                            </td>
                            <td style={{ padding: '10px' }}>{row.control_no || '-'}</td>
                            <td style={{ padding: '10px' }}>{row.control_date || '-'}</td>
                            <td style={{ padding: '10px' }}>{row.depot}</td>
                            <td style={{ padding: '10px', maxWidth: '200px', wordWrap: 'break-word' }}>
                              {row.remarks || '-'}
                            </td>
                            <td style={{ 
                              padding: '10px', 
                              textAlign: 'center',
                              fontWeight: 'bold',
                              color: row.pending_days > 90 ? '#c0392b' : row.pending_days > 60 ? '#d68910' : '#27ae60'
                            }}>
                              {row.pending_days !== null ? row.pending_days : '-'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PendingDemandsPanel;
