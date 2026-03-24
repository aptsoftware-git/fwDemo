import React, { useState, useEffect } from 'react';
import { getAvailableModels, getCurrentModel, loadModel, cleanDemoData } from '../api/client';

const ModelSelector = ({ onClear, onToggleDetails, showDetails }) => {
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingModels, setLoadingModels] = useState(true);
  const [error, setError] = useState('');
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch available models and current model on mount
  useEffect(() => {
    fetchModelsAndCurrent();
  }, []);

  const fetchModelsAndCurrent = async () => {
    try {
      setLoadingModels(true);
      const [availableModels, current] = await Promise.all([
        getAvailableModels(),
        getCurrentModel()
      ]);

      setModels(availableModels);
      setCurrentModel(current);
      setSelectedModel(current.name);
      setHasChanges(false);
    } catch (err) {
      console.error('Failed to fetch models:', err);
      setError('Failed to load models');
    } finally {
      setLoadingModels(false);
    }
  };

  const handleModelChange = (e) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    setHasChanges(newModel !== currentModel?.name);
  };

  const handleLoadModel = async () => {
    if (!selectedModel || selectedModel === currentModel?.name) {
      return;
    }

    try {
      setLoading(true);
      setError('');

      const result = await loadModel(selectedModel);
      
      // Refresh current model info
      const updatedCurrent = await getCurrentModel();
      setCurrentModel(updatedCurrent);
      setHasChanges(false);

      alert(`✓ Successfully loaded ${result.model}\n\nTimeout: ${result.settings.timeout}s\nContext Length: ${result.settings.max_text_length}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load model');
      console.error('Failed to load model:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!window.confirm('Are you sure you want to clean the database? This will remove all loaded data.')) {
      return;
    }

    try {
      await cleanDemoData();
      if (onClear) {
        onClear();
      }
      alert('Database cleaned successfully!');
    } catch (err) {
      alert('Failed to clean database: ' + (err.response?.data?.detail || err.message));
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      'Fast': '#3498db',
      'Balanced': '#27ae60',
      'High Quality': '#e67e22',
      'Best Quality': '#9b59b6'
    };
    return colors[tier] || '#95a5a6';
  };

  if (loadingModels) {
    return (
      <div className="model-selector">
        <span className="loading-text">Loading models...</span>
      </div>
    );
  }

  return (
    <div className="model-selector">
      <div className="model-status">
        {currentModel && currentModel.loaded && (
          <span className="status-badge">
            <span className="status-indicator">●</span> {currentModel.name}
          </span>
        )}
      </div>

      <div className="model-selection">
        <label htmlFor="model-select" className="model-label">
          LLM Model:
        </label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={handleModelChange}
          disabled={loading}
          className="model-dropdown"
        >
          {models.map((model) => (
            <option key={model.name} value={model.name}>
              {model.name} - {model.tier} ({model.size})
            </option>
          ))}
        </select>

        {hasChanges && (
          <button
            onClick={handleLoadModel}
            disabled={loading}
            className="btn-load-model"
          >
            {loading ? 'Loading...' : 'Apply & Load Model'}
          </button>
        )}
      </div>

      {error && (
        <div className="model-error">
          {error}
        </div>
      )}

      {currentModel && (
        <div className="model-info">
          <span className="model-tier" style={{ color: getTierColor(currentModel.tier) }}>
            {currentModel.tier}
          </span>
          <span className="model-size">{currentModel.size}</span>
          <span className="model-description">{currentModel.description}</span>
        </div>
      )}

      <div className="header-actions">
        <button
          onClick={handleClear}
          className="btn-clear"
        >
          Clear
        </button>
        <button
          onClick={onToggleDetails}
          className="btn-toggle-details"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>
    </div>
  );
};

export default ModelSelector;
