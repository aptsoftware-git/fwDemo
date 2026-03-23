import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import DatasetSelector from './DatasetSelector';
import ComparisonModal from './ComparisonModal';

const ComparisonPanel = ({ datasets }) => {
  const [tag1, setTag1] = useState('');
  const [tag2, setTag2] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleCompareClick = () => {
    if (!tag1 || !tag2) {
      setError('Please select both datasets to compare');
      return;
    }

    if (tag1 === tag2) {
      setError('Please select different datasets');
      return;
    }

    setError(null);
    setShowModal(true);
  };

  const handleComparisonComplete = (comparisonResult) => {
    setResult(comparisonResult);
  };

  const getSheetTypeLabel = (sheetType) => {
    const labels = {
      'APPX_A_AVEH': 'A Veh',
      'APPX_A_BVEH': 'B Veh',
      'APPX_A_CVEH': 'C Veh',
      'ARMT': 'ARMT',
      'SA': 'SA'
    };
    return labels[sheetType] || sheetType;
  };

  return (
    <div className="section">
      <h2>Compare Datasets</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <DatasetSelector
          datasets={datasets}
          selectedTag={tag1}
          onSelect={setTag1}
          label="Previous Period (Dataset 1)"
        />
        <DatasetSelector
          datasets={datasets}
          selectedTag={tag2}
          onSelect={setTag2}
          label="Current Period (Dataset 2)"
        />
      </div>

      <button onClick={handleCompareClick} disabled={!tag1 || !tag2}>
        Compare Datasets
      </button>

      {error && <div className="error" style={{ marginTop: '10px' }}>{error}</div>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h3 style={{ marginBottom: '10px', color: '#2c3e50' }}>
            Comparison: {result.tag1} vs {result.tag2} - {getSheetTypeLabel(result.sheet_type)}
          </h3>
          <div className="comparison-result markdown-preview">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm, remarkMath]} 
              rehypePlugins={[rehypeKatex]}
            >
              {result.comparison_text}
            </ReactMarkdown>
          </div>
          <div style={{ marginTop: '15px', display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button 
              className="btn-secondary"
              onClick={() => {
                navigator.clipboard.writeText(result.comparison_text);
                alert('Comparison copied to clipboard!');
              }}
            >
              Copy to Clipboard
            </button>
            <span style={{ fontSize: '12px', color: '#999' }}>
              Generated at: {new Date(result.generated_at).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      <ComparisonModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        tag1={tag1}
        tag2={tag2}
        onSubmit={handleComparisonComplete}
      />
    </div>
  );
};

export default ComparisonPanel;
