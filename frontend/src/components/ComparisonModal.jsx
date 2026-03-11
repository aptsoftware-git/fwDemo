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
PREVIOUS PERIOD DATA: {previous_data}
CURRENT PERIOD DATA: {current_data}

Provide a **Comparative Readiness & Trend Analysis** for the **{sheet_type}** category:

## 1. Inventory Flux 
- Calculate the net change in Held (UH) vs Authorized (UE) quantities
- Identify if the formation is "Gaining Ground" (increasing inventory) or "Depleting" (decreasing inventory)
- Highlight any significant gaps between authorized and held quantities

## 2. Serviceability Delta
- Compare the Fully Mission Capable (FMC) rates between the two periods
- Calculate the percentage point change in mission readiness
- Highlight if technical health is **Improving** or **Deteriorating**

## 3. Maintenance Backlog Evolution
- Analyze the "Remarks" and "Total Non-Functional" columns from both periods
- Identify recurring issues (e.g., Engine/Chassis defects, structural problems)
- Determine if previous issues have been **Resolved** or are **Persisting**
- List any new critical failure patterns that appeared in the current period

## 4. Logistical Pipeline Efficiency
- Compare the number of "Demanded" items between periods
- Assess if the formation is clearing the backlog of parts or if the supply chain is slowing down
- Identify high-demand items or long-lead components

## 5. Executive Conclusion
- Provide an overall **Status Rating**: **Improved** / **Stable** / **Degraded**
- Give one primary actionable recommendation to improve readiness for the coming period
- Highlight the most critical vulnerability that requires immediate attention

Format your response in clear markdown with proper headings and bullet points.`;

const SHEET_TYPE_LABELS = {
  'APPX_A_BVEH': 'Appx A (B veh)',
  'APPX_A_CVEH': 'Appx A (C veh)',
  'ARMT': 'Armt',
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
