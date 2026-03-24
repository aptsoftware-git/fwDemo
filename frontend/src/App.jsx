import React, { useState, useEffect } from 'react';
import './App.css';
import { getDatasets, getData, getUnits } from './api/client';
// GENERIC FEATURE: Original UploadPanel hidden for demo
// import UploadPanel from './components/UploadPanel';
// DEMO: Use simplified DemoLoadPanel instead
import DemoLoadPanel from './components/DemoLoadPanel';
import DatasetSelector from './components/DatasetSelector';
import UnitFilter from './components/UnitFilter';
import DataTabs from './components/DataTabs';
import ComparisonPanel from './components/ComparisonPanel';
import DatasetManager from './components/DatasetManager';
import ModelSelector from './components/ModelSelector';
import AnalysisPanel from './components/AnalysisPanel';

function App() {
  const [datasets, setDatasets] = useState([]);
  const [selectedTag, setSelectedTag] = useState('');
  const [units, setUnits] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(true);

  // Load datasets on mount
  useEffect(() => {
    loadDatasets();
  }, []);

  // Load units when dataset selection changes
  useEffect(() => {
    if (selectedTag) {
      // Reset unit selection to ensure data reloads when switching datasets
      setSelectedUnit(null);
      loadUnits(selectedTag);
    } else {
      setUnits([]);
      setSelectedUnit(null);
      setData(null);
    }
  }, [selectedTag]);

  // Load data when unit filter changes
  useEffect(() => {
    if (selectedTag && selectedUnit) {
      loadData(selectedTag, selectedUnit);
    }
  }, [selectedUnit]);

  const loadDatasets = async () => {
    try {
      const result = await getDatasets();
      setDatasets(result);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    }
  };

  const loadUnits = async (tag) => {
    try {
      const result = await getUnits(tag);
      setUnits(result);
      // Set default to first formation instead of 'All'
      setSelectedUnit(result.length > 0 ? result[0] : 'All');
    } catch (err) {
      console.error('Failed to load units:', err);
      setUnits([]);
    }
  };

  const loadData = async (tag, unitFilter) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getData(tag, unitFilter);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    loadDatasets();
  };

  const handleDatasetDeleted = (deletedTag) => {
    // Reload datasets
    loadDatasets();
    
    // Clear selection if deleted dataset was selected
    if (selectedTag === deletedTag) {
      setSelectedTag('');
      setData(null);
      setUnits([]);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <div className="header">
          <div className="header-content">
            <div className="header-text">
              <h1>FRS Data Management System</h1>
              <p>Formation Readiness State Data Analysis & Comparison</p>
            </div>
            <div className="header-controls">
              <ModelSelector onClear={loadDatasets} onToggleDetails={() => setShowDetails(!showDetails)} showDetails={showDetails} />
            </div>
          </div>
        </div>

        {/* DEMO: Simplified load panel with Load button only */}
        <DemoLoadPanel onLoadSuccess={handleUploadSuccess} />

        {/* GENERIC FEATURE: Original upload panel hidden for demo
        <UploadPanel onUploadSuccess={handleUploadSuccess} />
        */}

        {showDetails && datasets.length > 0 && (
          <DatasetManager datasets={datasets} onDatasetDeleted={handleDatasetDeleted} />
        )}

        {showDetails && datasets.length > 0 && (
          <>
            <div className="section">
              <h2>View Data</h2>
              <div className="section-content">
                <DatasetSelector
                  datasets={datasets}
                  selectedTag={selectedTag}
                  onSelect={setSelectedTag}
                  label="Select Dataset"
                />

                {selectedTag && units.length > 0 && (
                  <UnitFilter
                    units={units}
                    selectedUnit={selectedUnit}
                    onSelect={setSelectedUnit}
                  />
                )}

                {loading && <div className="loading">Loading data...</div>}
                {error && <div className="error">{error}</div>}
                
                {data && !loading && (
                  <div style={{ marginTop: '20px' }}>
                    <h3 style={{ marginBottom: '15px', color: '#2c3e50' }}>
                      {data.tag} - {data.unit_filter}
                    </h3>
                    <DataTabs 
                      data={data} 
                      tag={data.tag} 
                      unitFilter={data.unit_filter}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* DEMO: Hide Compare Datasets section
            {datasets.length >= 2 && (
              <ComparisonPanel datasets={datasets} />
            )}
            */}
          </>
        )}

        {/* Analysis Panel for A Vehicles Comparison - Always visible when datasets exist */}
        {datasets.length > 0 && (
          <AnalysisPanel datasets={datasets} />
        )}

        {datasets.length === 0 && (
          <div className="section">
            <p style={{ textAlign: 'center', color: '#999' }}>
              No datasets uploaded yet. Upload a directory to get started.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
