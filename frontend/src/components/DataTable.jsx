import React from 'react';

const DataTable = ({ data, sheetType }) => {
  if (!data || data.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
        No data available for {sheetType}
      </div>
    );
  }

  // Get column names from first row
  const columns = Object.keys(data[0]);

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              {columns.map((col) => {
                const isRemarksColumn = col.toLowerCase().includes('remark');
                const isPercentageColumn = col === 'FMC%' || col === 'NMC%' || col === 'PMC%' || col === 'Avl%';
                
                // Format cell value
                let cellValue = row[col];
                if (cellValue !== null && cellValue !== undefined) {
                  if (isPercentageColumn) {
                    // Convert decimal to percentage (0.8918918918918919 → 89.19%)
                    const numValue = parseFloat(cellValue);
                    if (!isNaN(numValue)) {
                      cellValue = (numValue * 100).toFixed(2) + '%';
                    } else {
                      cellValue = String(cellValue);
                    }
                  } else {
                    cellValue = String(cellValue);
                  }
                } else {
                  cellValue = '-';
                }
                
                return (
                  <td 
                    key={col}
                    style={isRemarksColumn ? { whiteSpace: 'pre-wrap', minWidth: '400px', maxWidth: '600px' } : {}}
                  >
                    {cellValue}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
        Showing {data.length} row(s)
      </div>
    </div>
  );
};

export default DataTable;
