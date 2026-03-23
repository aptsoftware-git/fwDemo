import React, { useState } from 'react';
import DataTable from './DataTable';
import SummaryModal from './SummaryModal';

const SHEET_TYPES = [
  { key: 'APPX_A_AVEH', label: 'A Veh' },
  { key: 'APPX_A_BVEH', label: 'B Veh' },
  { key: 'APPX_A_CVEH', label: 'C Veh' },
  { key: 'ARMT', label: 'ARMT' },
  { key: 'SA', label: 'SA' },
  // { key: 'INST', label: 'INST' },  // TODO: Temporarily disabled - investigate later
  // { key: 'CBRN', label: 'CBRN' },  // TODO: Temporarily disabled - investigate later
];

const DataTabs = ({ data, tag, unitFilter }) => {
  const [activeTab, setActiveTab] = useState('APPX_A_BVEH');
  const [summaryModalOpen, setSummaryModalOpen] = useState(false);

  if (!data || !data.sheets) {
    return <div className="loading">No data loaded</div>;
  }

  const currentSheetLabel = SHEET_TYPES.find(s => s.key === activeTab)?.label || activeTab;
  const hasData = data.sheets[activeTab] && data.sheets[activeTab].length > 0;

  return (
    <div>
      <div className="tabs-header">
        <div className="tabs">
          {SHEET_TYPES.map((sheet) => (
            <button
              key={sheet.key}
              className={`tab ${activeTab === sheet.key ? 'active' : ''}`}
              onClick={() => setActiveTab(sheet.key)}
            >
              {sheet.label}
            </button>
          ))}
        </div>
        {hasData && (
          <button 
            className="btn-summary"
            onClick={() => setSummaryModalOpen(true)}
            title="Generate AI summary of this data"
          >
            📊 Generate Summary
          </button>
        )}
      </div>
      
      <DataTable 
        data={data.sheets[activeTab] || []} 
        sheetType={currentSheetLabel}
      />

      <SummaryModal
        isOpen={summaryModalOpen}
        onClose={() => setSummaryModalOpen(false)}
        tag={tag}
        unitFilter={unitFilter}
        sheetType={activeTab}
        sheetLabel={currentSheetLabel}
      />
    </div>
  );
};

export default DataTabs;
