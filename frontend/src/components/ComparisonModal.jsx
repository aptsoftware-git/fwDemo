import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiClient } from '../api/client';

const DEFAULT_PROMPT_TEMPLATE = `You are a Senior Military Logistics Analyst. You are provided with two datasets representing the same equipment type from two different time periods.

METADATA: {metadata}

{overall_stats}

DETAILED CATEGORY BREAKDOWN:
PREVIOUS PERIOD DATA: {previous_data}
CURRENT PERIOD DATA: {current_data}

---

Provide a **Comparative Readiness & Trend Analysis** for the **{sheet_type}** category:

{section1_answer}

## 2. Inventory Analysis 
- Reference the Total Held values from Section 1 above
- Calculate: Current Total Held - Previous Total Held = Net Change
- Identify if the formation is "Gaining Ground" (positive change) or "Depleting" (negative change)
- Analyze specific equipment categories that show significant changes in Held (UH) between previous and current periods (e.g., B1, B2, B3 in B Veh; C20, C63, C70 in C Veh; D1, D2 in ARMT)

## 3. Serviceability Trends
- Reference the exact FMC% change from Section 1 above
- Analyze the detailed data to identify which specific equipment subcategories (B1, B2, B3, etc.) showed notable changes
- Identify 2-3 equipment types that improved and 2-3 that degraded based on FMC values and remarks
- Assess operational impact of the overall FMC% trend shown in Section 1

## 4. Maintenance & Repair Pipeline
- Analyze the "Remarks" and "Total NMC (Nos)" columns from the detailed data
- Identify recurring issues (e.g., Engine/Chassis defects, structural problems)
- Determine if previous issues are **Resolved** or **Persisting**  
- List any new critical failure patterns
- Note: The overall readiness change from Section 1 indicates the net effect of maintenance activities

## 5. Logistical Efficiency
- Review "MUA" and "Demanded" mentions in the Remarks column
- Assess if demand for parts is increasing or decreasing
- Identify high-demand components (engines, chassis parts, etc.)
- Comment on whether supply chain is keeping pace with demands

## 6. Executive Summary
- Provide one primary actionable recommendation to improve readiness
- Highlight the most critical vulnerability requiring immediate attention
- Connect your recommendations to the overall readiness trend shown in Section 1

**IMPORTANT INSTRUCTIONS:**
1. All numerical values (Auth, Held, FMC, Total NMC, etc.) MUST be directly extracted from the provided data - do NOT calculate or infer values
2. When comparing periods, always reference BOTH previous and current values for the same category (e.g., "B1: Previous Held=50, Current Held=45, Change=-5")
3. Focus inventory analysis on changes between periods, NOT on Auth vs Held gaps
4. Do NOT add concluding statements like "By implementing recommendations..." - end with Section 6

Format your response in clear markdown with proper headings and bullet points.`;

const SHEET_TYPE_LABELS = {
  'APPX_A_AVEH': 'A Veh',
  'APPX_A_BVEH': 'B Veh',
  'APPX_A_CVEH': 'C Veh',
  'ARMT': 'ARMT',
  'SA': 'SA'
};

const ComparisonModal = ({ isOpen, onClose, tag1, tag2, onSubmit }) => {
  const [sheetType, setSheetType] = useState('APPX_A_BVEH');
  const [promptTemplate, setPromptTemplate] = useState(DEFAULT_PROMPT_TEMPLATE);
  const [comparison, setComparison] = useState('');
  const [readinessData, setReadinessData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPromptEditor, setShowPromptEditor] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setComparison('');
    setReadinessData([]);

    try {
      const response = await apiClient.post('/compare', {
        tag1,
        tag2,
        sheet_type: sheetType,
        prompt_template: promptTemplate
      });

      setComparison(response.data.comparison_text);
      setReadinessData(response.data.readiness_data || []);
      if (onSubmit) onSubmit(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate comparison');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setPromptTemplate(DEFAULT_PROMPT_TEMPLATE);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content summary-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Compare Datasets</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="summary-info">
            <p><strong>Previous Period:</strong> {tag1}</p>
            <p><strong>Current Period:</strong> {tag2}</p>
          </div>

          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label htmlFor="sheetType"><strong>Sheet Type:</strong></label>
            <select
              id="sheetType"
              value={sheetType}
              onChange={(e) => setSheetType(e.target.value)}
              style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            >
              {Object.entries(SHEET_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>

          <div className="prompt-section">
            <div className="section-header">
              <h3>Comparison Prompt Template</h3>
              <div>
                <button 
                  className="btn-secondary btn-small"
                  onClick={() => setShowPromptEditor(!showPromptEditor)}
                >
                  {showPromptEditor ? 'Hide' : 'Edit'} Template
                </button>
                {showPromptEditor && (
                  <button 
                    className="btn-secondary btn-small"
                    onClick={handleReset}
                    style={{ marginLeft: '8px' }}
                  >
                    Reset to Default
                  </button>
                )}
              </div>
            </div>

            {showPromptEditor && (
              <div className="prompt-editor">
                <textarea
                  value={promptTemplate}
                  onChange={(e) => setPromptTemplate(e.target.value)}
                  rows={15}
                  placeholder="Enter your comparison prompt template (use {metadata}, {previous_data}, {current_data}, {sheet_type} as placeholders)"
                />
                <p className="help-text">
                  Use <code>{'{{metadata}}'}</code>, <code>{'{{previous_data}}'}</code>, <code>{'{{current_data}}'}</code>, and <code>{'{{sheet_type}}'}</code> as placeholders.
                </p>
              </div>
            )}
          </div>

          <div className="action-section">
            <button 
              className="btn-primary"
              onClick={handleGenerate}
              disabled={loading || !promptTemplate.trim()}
            >
              {loading ? 'Generating Comparison... (This may take 30-60 seconds)' : 'Generate Comparison'}
            </button>
          </div>

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {comparison && (
            <div className="summary-result">
              <h3>Comparison Result</h3>
              
              {readinessData.length > 0 && (
                <>
                  <div className="chart-container" style={{ marginBottom: '30px' }}>
                    <h4>Formation Readiness Comparison (FMC%)</h4>
                    <ResponsiveContainer width="100%" height={350}>
                      <LineChart data={readinessData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="formation" 
                          angle={-45}
                          textAnchor="end"
                          height={80}
                        />
                        <YAxis 
                          label={{ value: 'FMC Readiness (%)', angle: -90, position: 'insideLeft' }}
                          domain={[0, 100]}
                        />
                        <Tooltip formatter={(value) => value !== null ? `${value.toFixed(2)}%` : 'N/A'} />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="previous_readiness" 
                          stroke="#8884d8" 
                          strokeWidth={2}
                          name={`Previous Period (${tag1})`}
                          connectNulls
                        />
                        <Line 
                          type="monotone" 
                          dataKey="current_readiness" 
                          stroke="#82ca9d" 
                          strokeWidth={2}
                          name={`Current Period (${tag2})`}
                          connectNulls
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="readiness-table-container" style={{ marginBottom: '30px', overflowX: 'auto' }}>
                    <h4>Detailed Readiness Summary</h4>
                    <table className="readiness-table" style={{
                      width: '100%',
                      borderCollapse: 'collapse',
                      fontSize: '13px'
                    }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f5f5f5' }}>
                          <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Formation</th>
                          <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }} colSpan="3">Previous Period ({tag1})</th>
                          <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }} colSpan="3">Current Period ({tag2})</th>
                          <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>Change</th>
                        </tr>
                        <tr style={{ backgroundColor: '#fafafa' }}>
                          <th style={{ padding: '8px', border: '1px solid #ddd' }}></th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>Total FMC</th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>Total Held</th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>FMC%</th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>Total FMC</th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>Total Held</th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>FMC%</th>
                          <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>Δ FMC%</th>
                        </tr>
                      </thead>
                      <tbody>
                        {readinessData.map((row, idx) => {
                          const change = row.previous_readiness !== null && row.current_readiness !== null
                            ? row.current_readiness - row.previous_readiness
                            : null;
                          const changeColor = change !== null 
                            ? (change > 0 ? '#28a745' : change < 0 ? '#dc3545' : '#6c757d')
                            : '#6c757d';
                          
                          return (
                            <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#fff' : '#f9f9f9' }}>
                              <td style={{ padding: '8px', border: '1px solid #ddd', fontWeight: 'bold' }}>{row.formation}</td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {row.previous_fmc !== null ? Math.round(row.previous_fmc) : 'N/A'}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {row.previous_held !== null ? Math.round(row.previous_held) : 'N/A'}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {row.previous_readiness !== null ? `${row.previous_readiness.toFixed(2)}%` : 'N/A'}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {row.current_fmc !== null ? Math.round(row.current_fmc) : 'N/A'}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {row.current_held !== null ? Math.round(row.current_held) : 'N/A'}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {row.current_readiness !== null ? `${row.current_readiness.toFixed(2)}%` : 'N/A'}
                              </td>
                              <td style={{ 
                                padding: '8px', 
                                border: '1px solid #ddd', 
                                textAlign: 'center',
                                fontWeight: 'bold',
                                color: changeColor
                              }}>
                                {change !== null ? `${change > 0 ? '+' : ''}${change.toFixed(2)}%` : 'N/A'}
                              </td>
                            </tr>
                          );
                        })}
                        {/* Totals row */}
                        {(() => {
                          const prevFmcTotal = readinessData.reduce((sum, row) => sum + (row.previous_fmc || 0), 0);
                          const prevHeldTotal = readinessData.reduce((sum, row) => sum + (row.previous_held || 0), 0);
                          const currFmcTotal = readinessData.reduce((sum, row) => sum + (row.current_fmc || 0), 0);
                          const currHeldTotal = readinessData.reduce((sum, row) => sum + (row.current_held || 0), 0);
                          
                          const prevOverallReadiness = prevHeldTotal > 0 ? (prevFmcTotal / prevHeldTotal) * 100 : null;
                          const currOverallReadiness = currHeldTotal > 0 ? (currFmcTotal / currHeldTotal) * 100 : null;
                          const overallChange = prevOverallReadiness !== null && currOverallReadiness !== null 
                            ? currOverallReadiness - prevOverallReadiness 
                            : null;
                          const changeColor = overallChange !== null 
                            ? (overallChange > 0 ? '#28a745' : overallChange < 0 ? '#dc3545' : '#6c757d')
                            : '#6c757d';
                          
                          return (
                            <tr style={{ backgroundColor: '#e8e8e8', fontWeight: 'bold' }}>
                              <td style={{ padding: '8px', border: '1px solid #ddd', fontWeight: 'bold' }}>TOTAL</td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {Math.round(prevFmcTotal)}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {Math.round(prevHeldTotal)}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {prevOverallReadiness !== null ? `${prevOverallReadiness.toFixed(2)}%` : 'N/A'}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {Math.round(currFmcTotal)}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {Math.round(currHeldTotal)}
                              </td>
                              <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                                {currOverallReadiness !== null ? `${currOverallReadiness.toFixed(2)}%` : 'N/A'}
                              </td>
                              <td style={{ 
                                padding: '8px', 
                                border: '1px solid #ddd', 
                                textAlign: 'center',
                                fontWeight: 'bold',
                                color: changeColor
                              }}>
                                {overallChange !== null ? `${overallChange > 0 ? '+' : ''}${overallChange.toFixed(2)}%` : 'N/A'}
                              </td>
                            </tr>
                          );
                        })()}
                      </tbody>
                    </table>
                  </div>
                </>
              )}

              <div className="summary-text markdown-preview">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm, remarkMath]} 
                  rehypePlugins={[rehypeKatex]}
                >
                  {comparison}
                </ReactMarkdown>
              </div>
              <button 
                className="btn-secondary"
                onClick={() => {
                  navigator.clipboard.writeText(comparison);
                  alert('Comparison copied to clipboard!');
                }}
              >
                Copy to Clipboard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComparisonModal;
