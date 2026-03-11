import React from 'react';

const DatasetSelector = ({ datasets, selectedTag, onSelect, label = "Select Dataset" }) => {
  return (
    <div className="form-group">
      <label>{label}</label>
      <select 
        value={selectedTag || ''} 
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="">-- Select --</option>
        {datasets.map((dataset) => (
          <option key={dataset.id} value={dataset.tag}>
            {dataset.tag} ({dataset.month_label || 'Unknown'}) - {dataset.unit_count} unit(s)
          </option>
        ))}
      </select>
    </div>
  );
};

export default DatasetSelector;
