import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { apiClient } from '../api/client';

const DEFAULT_PROMPT_TEMPLATE = `You are a Military Logistics Analyst. Analyze the following organizational readiness data using the provided metadata.

METADATA: {metadata}
DATA: {data}

Provide a high-level executive summary of the "Formation Readiness State" focusing on:

1. **Inventory Integrity**: Evaluate the gap between Authorized (UE) and Held (UH) quantities. Highlight significant shortages that impact operational scale.
2. **Technical Serviceability**: Identify the Fully Mission Capable (FMC) rate. Categorize non-functional assets by the severity of their defect (e.g., structural vs. component-level).
3. **Logistical Pipeline**: Detail outstanding demands, specifically mentioning high-frequency replacement parts or long-lead items (e.g., assemblies, specific specialized components).
4. **Compliance & Life Cycle**: Note any equipment marked for disposal (CL-V), nearing end-of-life, or pending critical administrative documentation (like missing Receipt Vouchers).
5. **Critical Vulnerabilities**: Flag any specific item that poses an immediate risk to the formation's combat or operational effectiveness.`;

const SummaryModal = ({ isOpen, onClose, tag, unitFilter, sheetType, sheetLabel }) => {
  const [promptTemplate, setPromptTemplate] = useState(DEFAULT_PROMPT_TEMPLATE);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPromptEditor, setShowPromptEditor] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setSummary('');

    try {
      const response = await apiClient.post('/generate-summary', {
        tag,
        unit_filter: unitFilter,
        sheet_type: sheetType,
        prompt_template: promptTemplate
      });

      setSummary(response.data.summary_text);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
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
          <h2>Generate Summary</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="summary-info">
            <p><strong>Dataset:</strong> {tag}</p>
            <p><strong>Unit Filter:</strong> {unitFilter}</p>
            <p><strong>Sheet Type:</strong> {sheetLabel}</p>
          </div>

          <div className="prompt-section">
            <div className="section-header">
              <h3>Prompt Template</h3>
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
                  rows={12}
                  placeholder="Enter your prompt template (use {metadata} and {data} as placeholders)"
                />
                <p className="help-text">
                  Use <code>{'{{metadata}}'}</code> and <code>{'{{data}}'}</code> as placeholders in your template.
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
              {loading ? 'Generating...' : 'Generate Summary'}
            </button>
          </div>

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {summary && (
            <div className="summary-result">
              <h3>Generated Summary</h3>
              <div className="summary-text markdown-preview">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm, remarkMath]} 
                  rehypePlugins={[rehypeKatex]}
                >
                  {summary}
                </ReactMarkdown>
              </div>
              <button 
                className="btn-secondary"
                onClick={() => {
                  navigator.clipboard.writeText(summary);
                  alert('Summary copied to clipboard!');
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

export default SummaryModal;
