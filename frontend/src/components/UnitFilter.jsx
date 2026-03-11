import React from 'react';

const UnitFilter = ({ units, selectedUnit, onSelect }) => {
  return (
    <div className="form-group">
      <label>Filter by Unit</label>
      <select 
        value={selectedUnit} 
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="All">All Units (Aggregated)</option>
        {units.map((unit) => (
          <option key={unit} value={unit}>
            {unit}
          </option>
        ))}
      </select>
    </div>
  );
};

export default UnitFilter;
