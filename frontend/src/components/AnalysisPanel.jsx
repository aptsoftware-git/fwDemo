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

          {/* Section 3: NMC over 25% */}
          <div style={{ marginBottom: '40px' }}>
            <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>
              3. {analysisData.section3.title}
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
                  {analysisData.section3.data.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                        No equipment with NMC over 25%
                      </td>
                    </tr>
                  ) : (
                    analysisData.section3.data.map((row) => (
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
              Total rows: {analysisData.section3.data?.length || 0}
            </div>
          </div>
        </div>
      )}
        </div>
      )}
    </div>
  );
};

export default AnalysisPanel;
