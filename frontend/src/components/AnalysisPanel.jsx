import React, { useState } from 'react';
import { getAVehiclesAnalysis, generateMailContent } from '../api/client';

const AnalysisPanel = ({ datasets }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true);

  // Mail generation state
  const [mailData, setMailData] = useState(null);
  const [mailLoading, setMailLoading] = useState(false);
  const [mailError, setMailError] = useState(null);
  const [isMailExpanded, setIsMailExpanded] = useState(true);
  const [showMailModal, setShowMailModal] = useState(false);

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

  const handleGenerateMail = async () => {
    setMailLoading(true);
    setMailError(null);
    try {
      const result = await generateMailContent();
      setMailData(result);
      setShowMailModal(true);
    } catch (err) {
      setMailError(err.response?.data?.detail || 'Failed to generate mail content');
      setMailData(null);
    } finally {
      setMailLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!mailData) return;
    
    const printWindow = window.open('', '_blank');
    const htmlContent = generateMailHTML(mailData);
    
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(() => {
      printWindow.print();
    }, 250);
  };

  const generateMailHTML = (data) => {
    const currentDate = new Date();
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = monthNames[currentDate.getMonth()];
    const currentYear = currentDate.getFullYear();
    const formattedDate = `${currentDate.getDate().toString().padStart(2, '0')}-${currentMonth}-${currentYear}`;
    
    // Get dataset month from section5 or section6 data
    const datasetTag = data.section5?.dataset || data.section6?.dataset || '';
    const monthMatch = datasetTag.match(/(November|December|January|February|March|April|May|June|July|August|September|October)\s+(\d{4})/i);
    const datasetMonth = monthMatch ? `${monthMatch[1].toUpperCase()} ${monthMatch[2]}` : '______';
    
    let section5TableRows = '';
    if (data.section5.data && data.section5.data.length > 0) {
      section5TableRows = data.section5.data.map(row => `
        <tr>
          <td style="border: 1px solid #000; padding: 5px; text-align: center;">${row.serial_no}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.nmc_type}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.unit || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.dependent_workshop || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.equipment || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.tk_ba_no || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.sys_sub_sys || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.nature_of_defect || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.defect_dt ? new Date(row.defect_dt).toLocaleDateString('en-GB') : '-'}</td>
          <td style="border: 1px solid #000; padding: 5px; text-align: center;">${row.pending_days ? `>${Math.floor(row.pending_days / 30)} months` : '-'}</td>
          <td style="border: 1px solid #000; padding: 5px; word-wrap: break-word; max-width: 200px;">${row.reasons || '-'}</td>
        </tr>
      `).join('');
    }
    
    let section6TableRows = '';
    if (data.section6.data && data.section6.data.length > 0) {
      section6TableRows = data.section6.data.map(row => `
        <tr>
          <td style="border: 1px solid #000; padding: 5px; text-align: center;">${row.serial_no}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.nmc_type}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.category || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.veh_ba_no || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.formation || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.units || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.maint_wksp || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.item_part_no || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.nomenclature || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px; text-align: center;">${row.qty || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.demand_no || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.demand_dt ? new Date(row.demand_dt).toLocaleDateString('en-GB') : '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.control_no || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.control_date || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px;">${row.depot || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px; word-wrap: break-word; max-width: 200px;">${row.remarks || '-'}</td>
          <td style="border: 1px solid #000; padding: 5px; text-align: center;">${row.pending_days ? `>${Math.floor(row.pending_days / 30)} months` : '-'}</td>
        </tr>
      `).join('');
    }

    return `
<!DOCTYPE html>
<html>
<head>
  <title>Mail Regarding 'A' Vehicle</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; font-size: 14px; background: white; color: #000; }
    .mail-header { margin-bottom: 20px; background: none; padding: 0; }
    .underline { display: inline-block; border-bottom: 1px solid #000; min-width: 150px; text-align: center; padding: 0 5px; }
    .mail-content { margin: 20px 0; text-align: justify; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 11px; }
    th { border: 1px solid #000; padding: 8px; background-color: #f0f0f0; font-weight: bold; text-align: left; }
    td { border: 1px solid #000; padding: 5px; }
    .mail-signature { margin-top: 40px; text-align: left; }
    .mail-copy-to { margin-top: 20px; }
    @media print {
      body { padding: 10px; }
      table { font-size: 10px; }
    }
  </style>
</head>
<body>
  <div class="mail-header">
    <p style="margin: 5px 0; color: #000;">HQ <span class="underline">&nbsp;</span> Cmd (EME)</p>
    <p style="margin: 5px 0; color: #000;">Pin 908542</p>
    <p style="margin: 5px 0; color: #000;">C/O 99 APO</p>
    <p style="margin: 15px 0 5px 0; color: #000;">0037/AE/Tech Cell dt ${formattedDate}</p>
    <p style="margin: 15px 0 5px 0; color: #000;">HQ <span class="underline">&nbsp;</span> Corps(EME)</p>
    <p style="margin: 5px 0; color: #000;">Pin <span class="underline">&nbsp;</span></p>
    <p style="margin: 5px 0; color: #000;">C/O 99 APO</p>
  </div>

  <div class="mail-content">
    <br/>
    <p style="text-align: center; margin: 20px 0; color: #000;"><strong>ANOMALIES IN FRS (A VEHICLES) FOR THE MONTH OF ${datasetMonth}</strong></p>
    
    <p style="margin: 15px 0; color: #000;">1. Please refer to the FRS of your Formation D for the month of ${datasetMonth}</p>
    
    <p style="margin: 15px 0; color: #000;">2. The following aspects have not been updated/mentioned incorrectly and require your attention: -</p>
    
    <p style="margin: 15px 0 10px 40px; color: #000;">2.1. Demands not controlled. The following demands have not been controlled even after two months</p>
    
    ${section6TableRows ? `
    <table>
      <thead>
        <tr>
          <th>Ser</th>
          <th>NMC Type</th>
          <th>Category</th>
          <th>Veh BA No</th>
          <th>Formation</th>
          <th>Units</th>
          <th>Maint Wksp</th>
          <th>Item/Part No</th>
          <th>Nomenclature</th>
          <th>Qty</th>
          <th>Demand No</th>
          <th>Demand Date</th>
          <th>Control No</th>
          <th>Control Date</th>
          <th>Depot</th>
          <th>Remarks</th>
          <th>Pending (Months)</th>
        </tr>
      </thead>
      <tbody>
        ${section6TableRows}
      </tbody>
    </table>
    ` : '<p style="margin-left: 40px; color: #000;"><em>No demands pending for over 2 months.</em></p>'}
    
    <p style="margin: 15px 0 10px 40px; color: #000;">2.2. Equipment pending for repairs for over three months</p>
    
    ${section5TableRows ? `
    <table>
      <thead>
        <tr>
          <th>Ser</th>
          <th>NMC Type</th>
          <th>Unit</th>
          <th>Dependent Workshop</th>
          <th>Equipment</th>
          <th>Tk BA No</th>
          <th>Sys/Sub Sys</th>
          <th>Nature of Defect</th>
          <th>Defect Date</th>
          <th>Pending Repairs Since (Months)</th>
          <th>Reasons</th>
        </tr>
      </thead>
      <tbody>
        ${section5TableRows}
      </tbody>
    </table>
    ` : '<p style="margin-left: 40px; color: #000;"><em>No equipment pending repairs for over 3 months.</em></p>'}
    
    <p style="margin: 15px 0; color: #000;">3. Kindly take corrective action & re-submit your FRS at the earliest. BEME is requested to speak to MGEME with respect to all "demands not controlled" and "equipment pending for repairs for over three months".</p>
    <br/><br/>
  </div>

  <div class="mail-signature">
    <p style="margin: 5px 0; color: #000;">(<span class="underline">&nbsp;</span>)</p>
    <p style="margin: 5px 0; color: #000;">Col EME</p>
    <p style="margin: 5px 0; color: #000;">For MGEME</p>
  </div>

  <div class="mail-copy-to">
    <br/>
    <p style="margin: 5px 0; color: #000;"><strong>Copy to:</strong><br/><br/><span class="underline">&nbsp;</span> EME Brigadier – For info and necessary action please.</p>
  </div>
</body>
</html>
    `;
  };



  if (!hasRequiredDatasets) {
    return null; // Don't show the panel if required datasets don't exist
  }

  return (
    <>
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
            Compare November and December 2025 <strong>A Vehicle</strong> data to analyze changes in Authorized/Held, Eng/MUA, and NMC status.
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
                    (analysisData.section1.data || []).map((row) => {
                      // Check if Auth < Held for both Previous and Current
                      const shouldHighlight = (row.previous_authorized < row.previous_held) && 
                                             (row.current_authorized < row.current_held);
                      const highlightColor = shouldHighlight ? '#fff3cd' : 'transparent'; // Yellow highlight
                      
                      return (
                        <tr key={row.serial_no} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px' }}>{row.serial_no}</td>
                          <td style={{ padding: '10px' }}>{row.equipment}</td>
                          <td style={{ padding: '10px' }}>{row.unit}</td>
                          <td style={{ 
                            padding: '10px', 
                            textAlign: 'center', 
                            borderLeft: '1px solid #eee',
                            backgroundColor: highlightColor
                          }}>
                            {row.previous_authorized}
                          </td>
                          <td style={{ 
                            padding: '10px', 
                            textAlign: 'center',
                            backgroundColor: highlightColor
                          }}>
                            {row.previous_held}
                          </td>
                          <td style={{ 
                            padding: '10px', 
                            textAlign: 'center', 
                            borderLeft: '1px solid #eee',
                            backgroundColor: highlightColor
                          }}>
                            {row.current_authorized}
                          </td>
                          <td style={{ 
                            padding: '10px', 
                            textAlign: 'center',
                            backgroundColor: highlightColor
                          }}>
                            {row.current_held}
                          </td>
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
                      );
                    })
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
                          Pending (Months)
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
                              {row.pending_days !== null ? `>${Math.floor(row.pending_days / 30)} months` : '-'}
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
                          Pending Repairs Since (Months)
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
                              {row.pending_days !== null ? `>${Math.floor(row.pending_days / 30)} months` : '-'}
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
                          Pending (Months)
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
                              {row.pending_days !== null ? `>${Math.floor(row.pending_days / 30)} months` : '-'}
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

    {/* Mail Generation Section */}
    <div className="section" style={{ marginTop: '20px' }}>
      <h2 
        className="collapsible-header" 
        onClick={() => setIsMailExpanded(!isMailExpanded)}
      >
        <span>Generate Mail content Regarding 'A' Vehicle</span>
        <span className={`toggle-icon ${isMailExpanded ? '' : 'collapsed'}`}>▲</span>
      </h2>
      
      {isMailExpanded && (
        <div className="section-content">
          <p style={{ color: '#666', marginBottom: '15px' }}>
            Generate official mail content with equipment pending repairs and demands not controlled for over 2 months.
          </p>
      
          <button
            onClick={handleGenerateMail}
            disabled={mailLoading}
            style={{
              padding: '12px 24px',
              backgroundColor: '#27ae60',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: mailLoading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              opacity: mailLoading ? 0.6 : 1
            }}
          >
            {mailLoading ? 'Generating Mail...' : 'Generate Mail'}
          </button>

          {mailError && (
            <div style={{ 
              marginTop: '15px', 
              padding: '12px', 
              backgroundColor: '#fee', 
              color: '#c33',
              borderRadius: '4px'
            }}>
              {mailError}
            </div>
          )}
        </div>
      )}
    </div>

    {/* Mail Preview Modal */}
    {showMailModal && mailData && (
      <div 
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}
        onClick={() => setShowMailModal(false)}
      >
        <div 
          style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            maxWidth: '95%',
            maxHeight: '90%',
            overflow: 'auto',
            padding: '20px',
            position: 'relative'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div style={{ 
            position: 'sticky', 
            top: 0, 
            backgroundColor: 'white', 
            zIndex: 1,
            paddingBottom: '15px',
            borderBottom: '2px solid #3498db',
            marginBottom: '20px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ margin: 0, color: '#2c3e50' }}>Mail Preview</h3>
            <div>
              <button
                onClick={handleDownloadPDF}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#e74c3c',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  marginRight: '10px'
                }}
              >
                Download PDF
              </button>
              <button
                onClick={() => setShowMailModal(false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#95a5a6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                Close
              </button>
            </div>
          </div>

          <div 
            style={{ 
              fontFamily: 'Arial, sans-serif', 
              lineHeight: '1.6',
              fontSize: '14px'
            }}
            dangerouslySetInnerHTML={{ __html: generateMailHTML(mailData) }}
          />
        </div>
      </div>
    )}
    </>
  );
};

export default AnalysisPanel;
