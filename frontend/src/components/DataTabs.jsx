import React, { useState } from 'react';
import DataTable from './DataTable';
import SummaryModal from './SummaryModal';

// Formation dataset sheet types
const FORMATION_SHEET_TYPES = [
  { key: 'APPX_A_AVEH', label: 'A Veh' },
  { key: 'APPX_A_BVEH', label: 'B Veh' },
  { key: 'APPX_A_CVEH', label: 'C Veh' },
  { key: 'ARMT', label: 'ARMT' },
  { key: 'SA', label: 'SA' },
];

// Local Workshop sheet types
const LOCAL_WORKSHOP_SHEET_TYPES = [
  { key: 'FR', label: 'FR' },
  { key: 'SPARES', label: 'SPARES' },
];

// Remote Workshop sheet types
const REMOTE_WORKSHOP_SHEET_TYPES = [
  { key: 'Eng', label: 'Eng' },
  { key: 'EOA Spares', label: 'EOA Spares' },
  { key: 'MUA', label: 'MUA' },
];

const DataTabs = ({ data, tag, unitFilter }) => {
  // Determine dataset type from tag
  const isLocalWorkshop = tag && tag.includes('Local Workshop');
  const isRemoteWorkshop = tag && tag.includes('Remote Workshop');
  
  // Select appropriate sheet types based on dataset type
  let SHEET_TYPES;
  let defaultTab;
  
  if (isLocalWorkshop) {
    SHEET_TYPES = LOCAL_WORKSHOP_SHEET_TYPES;
    defaultTab = 'FR';
  } else if (isRemoteWorkshop) {
    SHEET_TYPES = REMOTE_WORKSHOP_SHEET_TYPES;
    defaultTab = 'Eng';
  } else {
    SHEET_TYPES = FORMATION_SHEET_TYPES;
    defaultTab = 'APPX_A_AVEH';
  }
  
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [summaryModalOpen, setSummaryModalOpen] = useState(false);

  // Reset active tab when dataset type changes
  React.useEffect(() => {
    setActiveTab(defaultTab);
  }, [tag, defaultTab]);

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
