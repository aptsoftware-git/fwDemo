import React, { useState } from 'react';
import { getAVehiclesAnalysis } from '../api/client';

const AnalysisPanel = ({ datasets }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true);

  // Check if both November and December 2025 datasets exist
  const hasRequiredDatasets = datasets.some(d => d.tag === 'November 2025') && 
                               datasets.some(d => d.tag === 'December 2025');

  const handleAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getAVehiclesAnalysis();
      setAnalysisData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate analysis');
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };



  if (!hasRequiredDatasets) {
    return null; // Don't show the panel if required datasets don't exist
  }

  return (
    <div className="section">
      <h2 
        className="collapsible-header" 
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span>'A' Vehicles Analysis</span>
        <span className={`toggle-icon ${isExpanded ? '' : 'collapsed'}`}>▲</span>
      </h2>
      
      {isExpanded && (
        <div className="section-content">
          <p style={{ color: '#666', marginBottom: '15px' }}>
            Compare November and December 2025 A Vehicle data to analyze changes in Authorized/Held, Eng/MUA, and NMC status.
          </p>
      
      <button
        onClick={handleAnalysis}
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
        {loading ? 'Generating Analysis...' : 'Analysis'}
      </button>

      {error  && (
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

      {analysisData && (
        <div style={{ marginTop: '30px' }}>
          {/* Report Header */}
          <div style={{ 
            marginBottom: '30px', 
            paddingBottom: '15px', 
            borderBottom: '2px solid #3498db' 
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
              {analysisData.title}
            </h3>
            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
              Previous Month: {analysisData.previous_month} | Current Month: {analysisData.current_month}
            </p>
          </div>

          {/* Section 1: Changes in Authorized/Held */}
          <div style={{ marginBottom: '40px' }}>
            <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
              1. {analysisData.section1.title}
            </h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                    <th style={{ padding: '10px', textAlign: 'left' }}>S.No</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>Equipment</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>Unit</th>
                    <th colSpan="2" style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #ddd' }}>Previous</th>
                    <th colSpan="2" style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #ddd' }}>Current</th>
                    <th colSpan="2" style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #ddd' }}>Delta</th>
                  </tr>
                  <tr style={{ backgroundColor: '#f9f9f9' }}>
                    <th colSpan="3"></th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px', borderLeft: '1px solid #ddd' }}>Auth</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px' }}>Held</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px', borderLeft: '1px solid #ddd' }}>Auth</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px' }}>Held</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px', borderLeft: '1px solid #ddd' }}>Auth</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px' }}>Held</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData.section1.data?.length === 0 ? (
                    <tr>
                      <td colSpan="9" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                        No changes in Authorized/Held values
                      </td>
                    </tr>
                  ) : (
                    (analysisData.section1.data || []).map((row) => (
                      <tr key={row.serial_no} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '10px' }}>{row.serial_no}</td>
                        <td style={{ padding: '10px' }}>{row.equipment}</td>
                        <td style={{ padding: '10px' }}>{row.unit}</td>
                        <td style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #eee' }}>{row.previous_authorized}</td>
                        <td style={{ padding: '10px', textAlign: 'center' }}>{row.previous_held}</td>
                        <td style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #eee' }}>{row.current_authorized}</td>
                        <td style={{ padding: '10px', textAlign: 'center' }}>{row.current_held}</td>
                        <td style={{ 
                          padding: '10px', 
                          textAlign: 'center', 
                          borderLeft: '1px solid #eee',
                          color: row.delta_authorized > 0 ? '#27ae60' : row.delta_authorized < 0 ? '#e74c3c' : 'inherit',
                          fontWeight: row.delta_authorized !== 0 ? 'bold' : 'normal'
                        }}>
                          {row.delta_authorized > 0 ? '+' : ''}{row.delta_authorized}
                        </td>
                        <td style={{ 
                          padding: '10px', 
                          textAlign: 'center',
                          color: row.delta_held > 0 ? '#27ae60' : row.delta_held < 0 ? '#e74c3c' : 'inherit',
                          fontWeight: row.delta_held !== 0 ? 'bold' : 'normal'
                        }}>
                          {row.delta_held > 0 ? '+' : ''}{row.delta_held}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
              Total rows: {analysisData.section1.data?.length || 0}
            </div>
          </div>

          {/* Section 2: Change in Eng/MUA (NMC) */}
          <div style={{ marginBottom: '40px' }}>
            <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
              2. {analysisData.section2.title}
            </h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                    <th style={{ padding: '10px', textAlign: 'left' }}>S.No</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>Equipment</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>Unit</th>
                    <th colSpan="2" style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #ddd' }}>Previous NMC Due to</th>
                    <th colSpan="2" style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #ddd' }}>Current NMC Due to</th>
                    <th colSpan="2" style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #ddd' }}>Delta</th>
                  </tr>
                  <tr style={{ backgroundColor: '#f9f9f9' }}>
                    <th colSpan="3"></th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px', borderLeft: '1px solid #ddd' }}>Eng</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px' }}>MUA</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px', borderLeft: '1px solid #ddd' }}>Eng</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px' }}>MUA</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px', borderLeft: '1px solid #ddd' }}>Eng</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '12px' }}>MUA</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData.section2.data?.length === 0 ? (
                    <tr>
                      <td colSpan="9" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                        No changes in Eng/MUA values
                      </td>
                    </tr>
                  ) : (
                    (analysisData.section2.data || []).map((row) => (
                      <tr key={row.serial_no} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '10px' }}>{row.serial_no}</td>
                        <td style={{ padding: '10px' }}>{row.equipment}</td>
                        <td style={{ padding: '10px' }}>{row.unit}</td>
                        <td style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #eee' }}>{row.previous_eng}</td>
                        <td style={{ padding: '10px', textAlign: 'center' }}>{row.previous_mua}</td>
                        <td style={{ padding: '10px', textAlign: 'center', borderLeft: '1px solid #eee' }}>{row.current_eng}</td>
                        <td style={{ padding: '10px', textAlign: 'center' }}>{row.current_mua}</td>
                        <td style={{ 
                          padding: '10px', 
                          textAlign: 'center', 
                          borderLeft: '1px solid #eee',
                          color: row.delta_eng > 0 ? '#e74c3c' : row.delta_eng < 0 ? '#27ae60' : 'inherit',
                          fontWeight: row.delta_eng !== 0 ? 'bold' : 'normal'
                        }}>
                          {row.delta_eng > 0 ? '+' : ''}{row.delta_eng}
                        </td>
                        <td style={{ 
                          padding: '10px', 
                          textAlign: 'center',
                          color: row.delta_mua > 0 ? '#e74c3c' : row.delta_mua < 0 ? '#27ae60' : 'inherit',
                          fontWeight: row.delta_mua !== 0 ? 'bold' : 'normal'
                        }}>
                          {row.delta_mua > 0 ? '+' : ''}{row.delta_mua}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
              Total rows: {analysisData.section2.data?.length || 0}
            </div>
          </div>

          {/* Section 3: Pending Demands (Remote Workshop) */}
          {analysisData.section3 && (
            <div style={{ marginBottom: '40px' }}>
              <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
                {analysisData.section3.title}
              </h4>
              <h5 style={{ marginBottom: '15px', color: '#555', fontSize: '14px', fontWeight: 'normal' }}>
                {analysisData.section3.subtitle}
              </h5>
              <div style={{ marginBottom: '15px', fontSize: '13px', color: '#666' }}>
                Dataset: {analysisData.section3.dataset} | Total Pending: <strong>{analysisData.section3.total_pending}</strong>
              </div>

              {analysisData.section3.data.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#999', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
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
                      {analysisData.section3.data.map((row) => {
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
                              color: row.nmc_type === 'Eng' ? '#e74c3c' : row.nmc_type === 'VOR Spares' ? '#f39c12' : '#3498db'
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
              <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
                Total rows: {analysisData.section3.data?.length || 0}
              </div>
            </div>
          )}

          {/* Section 4: NMC over 25% */}
          {analysisData.section4 && (
            <div style={{ marginBottom: '40px' }}>
              <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
                3. {analysisData.section4.title}
              </h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                      <th style={{ padding: '10px', textAlign: 'left', width: '60px' }}>S.No</th>
                      <th style={{ padding: '10px', textAlign: 'left', width: '200px' }}>Equipment</th>
                      <th style={{ padding: '10px', textAlign: 'left', width: '150px' }}>Unit</th>
                      <th style={{ padding: '10px', textAlign: 'center', width: '100px' }}>NMC %</th>
                      <th style={{ padding: '10px', textAlign: 'left' }}>Reasons</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysisData.section4.data.length === 0 ? (
                      <tr>
                        <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                          No equipment with NMC over 25%
                        </td>
                      </tr>
                    ) : (
                      analysisData.section4.data.map((row) => (
                        <tr key={row.serial_no} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px' }}>{row.serial_no}</td>
                          <td style={{ padding: '10px' }}>{row.equipment}</td>
                          <td style={{ padding: '10px' }}>{row.unit}</td>
                          <td style={{ 
                            padding: '10px', 
                            textAlign: 'center',
                            color: '#e74c3c',
                            fontWeight: 'bold'
                          }}>
                            {row.nmc_percent.toFixed(2)}
                          </td>
                          <td style={{ padding: '10px', whiteSpace: 'pre-wrap' }}>{row.reasons || '-'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
                Total rows: {analysisData.section4.data?.length || 0}
              </div>
            </div>
          )}

          {/* Section 5: Equipment pending repairs for over three months (Local Workshop) */}
          {analysisData.section5 && (
            <div style={{ marginBottom: '40px' }}>
              <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
                4. {analysisData.section5.title}
              </h4>
              <div style={{ marginBottom: '15px', fontSize: '13px', color: '#666' }}>
                Dataset: {analysisData.section5.dataset} | Total Pending: <strong>{analysisData.section5.total_pending}</strong>
              </div>

              {analysisData.section5.data.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#999', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                  No equipment pending repairs for over three months
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '50px' }}>S.No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '80px' }}>NMC Type</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '150px' }}>Unit</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '120px' }}>Dependent WorkShop</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '150px' }}>Equipment</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '120px' }}>Tk BA No</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '150px' }}>Sys/ Sub Sys</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '200px' }}>Nature of Defect</th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '120px' }}>Defect Date</th>
                        <th style={{ 
                          padding: '10px', 
                          textAlign: 'center', 
                          minWidth: '100px',
                          backgroundColor: '#fff3cd',
                          fontWeight: 'bold'
                        }}>
                          Pending Repairs Since (Days)
                        </th>
                        <th style={{ padding: '10px', textAlign: 'left', minWidth: '400px' }}>Reasons</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisData.section5.data.map((row) => {
                        // Determine row color based on pending days
                        let rowColor = 'transparent';
                        if (row.pending_days !== null) {
                          if (row.pending_days > 180) {
                            rowColor = '#ffe6e6'; // Red tint for > 180 days (6 months)
                          } else if (row.pending_days > 120) {
                            rowColor = '#fff3cd'; // Yellow tint for > 120 days (4 months)
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
                              color: row.nmc_type === 'FR' ? '#e74c3c' : '#3498db'
                            }}>
                              {row.nmc_type}
                            </td>
                            <td style={{ padding: '10px' }}>{row.unit}</td>
                            <td style={{ padding: '10px' }}>{row.dependent_workshop}</td>
                            <td style={{ padding: '10px' }}>{row.equipment}</td>
                            <td style={{ padding: '10px' }}>{row.tk_ba_no}</td>
                            <td style={{ padding: '10px' }}>{row.sys_sub_sys}</td>
                            <td style={{ padding: '10px', maxWidth: '200px', wordWrap: 'break-word' }}>
                              {row.nature_of_defect}
                            </td>
                            <td style={{ padding: '10px' }}>
                              {row.defect_dt ? new Date(row.defect_dt).toLocaleDateString('en-GB') : '-'}
                            </td>
                            <td style={{ 
                              padding: '10px', 
                              textAlign: 'center',
                              fontWeight: 'bold',
                              color: row.pending_days > 180 ? '#c0392b' : row.pending_days > 120 ? '#d68910' : '#27ae60'
                            }}>
                              {row.pending_days !== null ? row.pending_days : '-'}
                            </td>
                            <td style={{ padding: '10px', maxWidth: '400px', wordWrap: 'break-word' }}>
                              {row.reasons || '-'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
              <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
                Total rows: {analysisData.section5.data?.length || 0}
              </div>
            </div>
          )}

          {/* Section 6: Demands not placed or not controlled for over 2 months */}
          {analysisData.section6 && (
            <div style={{ marginBottom: '40px' }}>
              <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
                5. {analysisData.section6.title}
              </h4>
              <div style={{ marginBottom: '15px', fontSize: '13px', color: '#666' }}>
                Dataset: {analysisData.section6.dataset} | Total Pending: <strong>{analysisData.section6.total_pending}</strong>
              </div>

              {analysisData.section6.data.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#999', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                  No demands pending for over 2 months
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
                      {analysisData.section6.data.map((row) => {
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
                              color: row.nmc_type === 'Eng' ? '#e74c3c' : row.nmc_type === 'VOR Spares' ? '#f39c12' : '#3498db'
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
              <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
                Total rows: {analysisData.section6.data?.length || 0}
              </div>
            </div>
          )}
        </div>
      )}
      </div>
    )}
    </div>
  );
};

export default AnalysisPanel;
