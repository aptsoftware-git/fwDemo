"""
Data cleaning and processing module for FRS Data Management System.
Handles deduplication, null handling, standardization, and aggregation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import re


def extract_numeric_value(value) -> float:
    """
    Extract numeric value from a string that may contain special characters.
    Examples:
        '17*' -> 17.0
        '1+@1' -> 1.0
        '1#' -> 1.0
        '57' -> 57.0
        57 -> 57.0
        None -> 0.0
    """
    if value is None or value == '':
        return None
    
    # If already a number, return it
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and extract first numeric sequence
    value_str = str(value).strip()
    
    # Try to extract numeric value (including decimals)
    # Match patterns like: 17*, *17, 1+@1, 1#, 57, 12.5*, etc.
    match = re.search(r'(\d+\.?\d*)', value_str)
    if match:
        return float(match.group(1))
    
    return None


def standardize_value(value: Any, value_type: str = 'auto') -> Any:
    """
    Standardize a value based on its type.
    
    Args:
        value: Value to standardize
        value_type: Type hint ('number', 'text', 'date', 'auto')
    
    Returns:
        Standardized value
    """
    # Handle null/missing values
    if pd.isna(value) or value is None or (isinstance(value, str) and value.strip() == ''):
        return None
    
    # Auto-detect type if not specified
    if value_type == 'auto':
        if isinstance(value, (int, float)):
            value_type = 'number'
        elif isinstance(value, (datetime, pd.Timestamp)):
            value_type = 'date'
        else:
            value_type = 'text'
    
    try:
        if value_type == 'number':
            # Extract numeric value (handles special characters like 17*, 1+@1, 1#, etc.)
            return extract_numeric_value(value)
        
        elif value_type == 'text':
            # Standardize text: strip leading/trailing whitespace
            text = str(value).strip()
            # Remove extra spaces on each line, but preserve newlines
            # Only collapse multiple spaces/tabs, not newlines
            text = re.sub(r'[ \t]+', ' ', text)
            return text if text else None
        
        elif value_type == 'date':
            # Standardize date format
            if isinstance(value, str):
                return pd.to_datetime(value, errors='coerce')
            return value
        
    except Exception:
        # If conversion fails, return original value
        return value
    
    return value


def clean_dataframe(df: pd.DataFrame, remove_duplicates: bool = True, 
                   fill_strategy: str = 'drop') -> pd.DataFrame:
    """
    Clean a pandas DataFrame by handling duplicates, nulls, and standardizing values.
    
    Args:
        df: Input DataFrame
        remove_duplicates: Whether to remove duplicate rows
        fill_strategy: Strategy for handling nulls ('drop', 'forward', 'zero', 'keep')
    
    Returns:
        Cleaned DataFrame
    """
    if df is None or df.empty:
        return df
    
    # Create a copy to avoid modifying original
    cleaned_df = df.copy()
    
    # 1. Remove completely empty rows
    cleaned_df = cleaned_df.dropna(how='all')
    
    # 2. Remove duplicate rows
    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates()
    
    # 3. Standardize column names (strip whitespace, handle special chars)
    cleaned_df.columns = [str(col).strip() for col in cleaned_df.columns]
    
    # Define columns that should always remain as text (never convert to numeric)
    text_only_columns = [
        'Category (Make & Type)', 'Make & Eqpt', 'Category', 
        'Remarks', 'Remark', 'Comments', 'Comment',
        'Nomenclature', 'Description', 'Type', 'Make'
    ]
    
    # 4. Standardize values in each column
    for col in cleaned_df.columns:
        # Skip numeric conversion for text-only columns
        is_text_only = any(text_col.lower() in col.lower() for text_col in text_only_columns)
        
        # Try to infer the column type
        sample_values = cleaned_df[col].dropna().head(10)
        
        if len(sample_values) > 0:
            # Check if column contains numeric data (skip for text-only columns)
            if not is_text_only:
                try:
                    # Clean special characters from numeric values first
                    numeric_series = cleaned_df[col].apply(extract_numeric_value)
                    # If more than 50% of non-null values are numeric, treat as number
                    if numeric_series.notna().sum() / cleaned_df[col].notna().sum() > 0.5:
                        cleaned_df[col] = numeric_series
                        continue
                except:
                    pass
            
            # Check if column contains dates (skip for text-only columns)
            if not is_text_only:
                try:
                    date_series = pd.to_datetime(cleaned_df[col], errors='coerce', format='mixed')
                    if date_series.notna().sum() / cleaned_df[col].notna().sum() > 0.5:
                        cleaned_df[col] = date_series
                        continue
                except:
                    pass
            
            # Otherwise, treat as text and standardize
            cleaned_df[col] = cleaned_df[col].apply(lambda x: standardize_value(x, 'text'))
    
    # 5. Handle null values based on strategy
    if fill_strategy == 'drop':
        # Drop rows with any null values in critical columns
        # Keep all rows for now (user can filter later)
        pass
    elif fill_strategy == 'forward':
        # Forward fill (use previous value)
        cleaned_df = cleaned_df.fillna(method='ffill')
    elif fill_strategy == 'zero':
        # Fill with 0 for numeric, empty string for text
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype in ['float64', 'int64']:
                cleaned_df[col] = cleaned_df[col].fillna(0)
            else:
                cleaned_df[col] = cleaned_df[col].fillna('')
    # 'keep' strategy - do nothing
    
    # 6. Reset index
    cleaned_df = cleaned_df.reset_index(drop=True)
    
    return cleaned_df


def aggregate_units(sheet_data_list: List[Dict[str, pd.DataFrame]], 
                    aggregation_method: str = 'concat') -> Dict[str, pd.DataFrame]:
    """
    Aggregate data from multiple units into a single dataset.
    
    Args:
        sheet_data_list: List of dictionaries mapping sheet_type to DataFrame
                         Each dict represents one unit's data
        aggregation_method: Method for aggregation ('concat', 'sum', 'mean')
    
    Returns:
        Dictionary mapping sheet_type to aggregated DataFrame
    """
    if not sheet_data_list:
        return {}
    
    # Collect all sheet types
    all_sheet_types = set()
    for unit_data in sheet_data_list:
        all_sheet_types.update(unit_data.keys())
    
    aggregated_data = {}
    
    for sheet_type in all_sheet_types:
        # Collect all DataFrames for this sheet type
        dfs_to_aggregate = []
        
        for unit_data in sheet_data_list:
            if sheet_type in unit_data:
                df = unit_data[sheet_type]
                if not df.empty:
                    dfs_to_aggregate.append(df)
        
        if not dfs_to_aggregate:
            continue
        
        # Perform aggregation based on method
        if aggregation_method == 'concat':
            # Simple concatenation (most common for FRS data)
            aggregated_df = pd.concat(dfs_to_aggregate, ignore_index=True)
            # Remove duplicates that may have been introduced
            aggregated_df = aggregated_df.drop_duplicates()
        
        elif aggregation_method == 'sum':
            # Sum numeric values (assumes same structure)
            aggregated_df = pd.concat(dfs_to_aggregate)
            numeric_cols = aggregated_df.select_dtypes(include=[np.number]).columns
            aggregated_df = aggregated_df.groupby(level=0)[numeric_cols].sum()
        
        elif aggregation_method == 'mean':
            # Average numeric values
            aggregated_df = pd.concat(dfs_to_aggregate)
            numeric_cols = aggregated_df.select_dtypes(include=[np.number]).columns
            aggregated_df = aggregated_df.groupby(level=0)[numeric_cols].mean()
        
        else:
            # Default to concat
            aggregated_df = pd.concat(dfs_to_aggregate, ignore_index=True)
        
        aggregated_data[sheet_type] = aggregated_df
    
    return aggregated_data


def standardize_column_name(col_name: str) -> str:
    """
    Standardize column names to canonical format across all sheet types.
    
    Maps all variations to standard column names for:
    - B veh/C veh: Ser No, Category (Make & Type), Auth (UE), Held (UH), MUA, OH, R4, Total NMC (Nos), FMC, Remarks
    - ARMT: Ser No, Make & Eqpt, Auth (UE), Held (UH), Eng/ Brl, MUA, Spares, OH, MR, FR, R4, OBE, Total NMC (Nos), PMC (Nos) (Due to OH), FMC, NMC%, PMC%, Avl%, Remarks
    """
    # First normalize: remove newlines and extra spaces
    normalized = col_name.replace('\\n', ' ').replace('\n', ' ').replace('\r', ' ')
    normalized = ' '.join(normalized.split()).strip()
    
    # Convert to lowercase for matching
    lower = normalized.lower()
    
    # Map to standard column names (order matters - more specific patterns first)
    
    # Serial number column
    if lower in ['ser', 'sr', 's no', 's.no'] or ('ser' in lower and 'no' in lower):
        return 'Ser No'
    
    # Category/Equipment columns - ARMT uses different naming
    elif 'make' in lower and 'eqpt' in lower:
        # ARMT sheet: "Make & Eqpt"
        return 'Make & Eqpt'
    elif 'category' in lower or ('make' in lower and 'type' in lower):
        # B veh/C veh: "Category (Make & Type)"
        return 'Category (Make & Type)'
    
    # Auth column
    elif 'auth' in lower:
        return 'Auth (UE)'
    
    # Held column
    elif 'held' in lower:
        return 'Held (UH)'
    
    # Eng/Barrel column (ARMT specific)
    elif 'eng' in lower and 'brl' in lower:
        return 'Eng/ Brl'
    elif lower in ['eng', 'eng/', 'eng /', 'eng /']:
        return 'Eng/ Brl'
    
    # MUA column
    elif 'mua' in lower:
        return 'MUA'
    
    # Spares column (ARMT specific)
    elif 'spare' in lower:
        return 'Spares'
    
    # Combined OH/MR/R4/FR column (SA variant)
    elif 'under' in lower and 'oh' in lower and 'mr' in lower and 'base' in lower:
        return 'Under OH /MR/R4/ FR/ Base Repair'
    
    # OH column
    elif lower in ['oh', 'o h', 'o/h']:
        return 'OH'
    
    # MR column (ARMT specific)
    elif lower in ['mr', 'm r', 'm/r']:
        return 'MR'
    
    # FR column (ARMT specific)
    elif lower in ['fr', 'f r', 'f/r']:
        return 'FR'
    
    # R4 column
    elif lower in ['r4', 'r 4', 'r-4']:
        return 'R4'
    
    # OBE column (ARMT specific)
    elif lower in ['obe', 'o b e', 'o/b/e']:
        return 'OBE'
    
    # Total column
    elif 'total' in lower:
        return 'Total NMC (Nos)'
    
    # PMC column (ARMT specific)
    elif 'pmc' in lower and ('nos' in lower or 'due' in lower or 'oh' in lower):
        return 'PMC (Nos) (Due to OH)'
    
    # Percentage columns (ARMT specific) - check these BEFORE non-percentage versions
    elif 'fmc' in lower and '%' in normalized:
        return 'FMC%'
    elif 'nmc' in lower and '%' in normalized:
        return 'NMC%'
    elif 'pmc' in lower and '%' in normalized:
        return 'PMC%'
    elif 'avl' in lower and '%' in normalized:
        return 'Avl%'
    
    # FMC column (count, not percentage) - check AFTER FMC%
    elif 'fmc' in lower:
        return 'FMC'
    
    # Remarks column
    elif 'remark' in lower:
        return 'Remarks'
    
    else:
        # Return normalized version if no match found
        return normalized


def aggregate_by_category(row_data_list: List[Dict[str, Any]], 
                          use_ai_for_remarks: bool = False) -> List[Dict[str, Any]]:
    """
    Aggregate data from multiple units by grouping on Category column.
    
    This creates a consolidated view where:
    - Rows are grouped by Category (e.g., B1, B2, B3...)
    - Serial numbers are regenerated in sequential order
    - Numerical columns are summed (Auth, Held, MUA, OH, R4, Total, FMC)
    - Remarks are concatenated (or AI-summarized if enabled)
    
    Args:
        row_data_list: List of row dictionaries from multiple units
        use_ai_for_remarks: Whether to use AI to consolidate remarks (default: False)
    
    Returns:
        List of aggregated row dictionaries with regenerated serial numbers
    """
    if not row_data_list:
        return []
    
    # Standardize column names to canonical format
    normalized_rows = []
    for row in row_data_list:
        normalized_row = {}
        for key, value in row.items():
            # Use the standardization function
            standard_key = standardize_column_name(key)
            normalized_row[standard_key] = value
        normalized_rows.append(normalized_row)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(normalized_rows)
    
    if df.empty:
        return []
    
    # Detect which type of sheet we're aggregating based on available columns
    # Check for ARMT-specific columns to identify sheet type
    armt_indicators = ['Eng/ Brl', 'Spares', 'MR', 'FR', 'OBE', 'PMC (Nos) (Due to OH)', 'NMC%', 'PMC%', 'Avl%']
    is_armt = any(col in df.columns for col in armt_indicators)
    
    # Determine category column based on sheet type
    if is_armt:
        # ARMT sheets use 'Make & Eqpt', but may have been labeled 'Category (Make & Type)' in source
        if 'Make & Eqpt' in df.columns and 'Category (Make & Type)' in df.columns:
            # Both columns exist - merge them (some units may use one, some the other)
            df['Make & Eqpt'] = df['Make & Eqpt'].fillna(df['Category (Make & Type)'])
            # Drop the redundant column
            df = df.drop(columns=['Category (Make & Type)'])
            category_col = 'Make & Eqpt'
        elif 'Make & Eqpt' in df.columns:
            category_col = 'Make & Eqpt'
        elif 'Category (Make & Type)' in df.columns:
            # Rename to standard ARMT format
            df = df.rename(columns={'Category (Make & Type)': 'Make & Eqpt'})
            category_col = 'Make & Eqpt'
        else:
            return row_data_list
    else:
        # B veh/C veh use 'Category (Make & Type)'
        if 'Category (Make & Type)' in df.columns:
            category_col = 'Category (Make & Type)'
        else:
            return row_data_list
    
    # Clean and normalize the category column values (strip whitespace, handle case)
    df[category_col] = df[category_col].astype(str).str.strip()
    
    # Filter out rows where category is empty/None
    df = df[df[category_col].notna() & (df[category_col] != '') & (df[category_col] != '-') & (df[category_col] != 'nan')]
    
    if df.empty:
        return []
    
    # Define the standard numerical columns for aggregation based on sheet type
    if is_armt:
        # For ARMT, percentage columns will be calculated, not summed
        numerical_cols = ['Auth (UE)', 'Held (UH)', 'Eng/ Brl', 'MUA', 'Spares', 'OH', 'MR', 'FR', 'R4', 'Under OH /MR/R4/ FR/ Base Repair', 'OBE', 'Total NMC (Nos)', 'PMC (Nos) (Due to OH)', 'FMC']
    else:
        numerical_cols = ['Auth (UE)', 'Held (UH)', 'MUA', 'OH', 'R4', 'Total NMC (Nos)', 'FMC']
    
    # Only include numerical columns that actually exist in the dataframe
    numerical_cols = [col for col in numerical_cols if col in df.columns]
    
    # After standardization, we know the exact column names
    remarks_col = 'Remarks' if 'Remarks' in df.columns else None
    ser_no_col = 'Ser No' if 'Ser No' in df.columns else None
    
    # Group by category
    grouped = df.groupby(category_col, sort=False, dropna=False)
    
    aggregated_rows = []
    
    for category, group in grouped:
        agg_row = {}
        
        # Category value
        agg_row[category_col] = category
        
        # Sum numerical columns
        for num_col in numerical_cols:
            # Extract numeric values (handles special characters)
            numeric_values = group[num_col].apply(extract_numeric_value)
            total = numeric_values.sum()
            
            # Handle different data types appropriately
            if pd.isna(total) or total == 0:
                # Default to 0 for numerical columns
                agg_row[num_col] = 0
            else:
                # Use int if no decimals, otherwise float
                if total == int(total):
                    agg_row[num_col] = int(total)
                else:
                    agg_row[num_col] = total
        
        # Calculate percentage columns for ARMT sheets
        if is_armt:
            held_uh = agg_row.get('Held (UH)', 0)
            
            if held_uh > 0:
                # NMC% = Total NMC (Nos) / Held (UH)
                total_nmc = agg_row.get('Total NMC (Nos)', 0)
                agg_row['NMC%'] = total_nmc / held_uh
                
                # PMC% = PMC (Nos) (Due to OH) / Held (UH)
                pmc_nos = agg_row.get('PMC (Nos) (Due to OH)', 0)
                agg_row['PMC%'] = pmc_nos / held_uh
                
                # FMC% = FMC / Held (UH)
                fmc = agg_row.get('FMC', 0)
                agg_row['FMC%'] = fmc / held_uh
                
                # Avl% = PMC% + FMC%
                agg_row['Avl%'] = agg_row['PMC%'] + agg_row['FMC%']
            else:
                # If Held (UH) is 0, set percentages to None (will display as "-")
                agg_row['NMC%'] = None
                agg_row['PMC%'] = None
                agg_row['FMC%'] = None
                agg_row['Avl%'] = None
        
        # Handle remarks - concatenate unique non-empty remarks from ALL remarks columns
        if remarks_col:
            remarks_list = []
            # Check all columns that might contain remarks
            for col in df.columns:
                if 'remark' in col.lower():
                    for remark in group[col]:
                        if pd.notna(remark) and str(remark).strip() and str(remark).lower() not in ['none', 'nan', '-']:
                            remark_str = str(remark).strip()
                            # Avoid exact duplicates
                            if remark_str not in remarks_list:
                                remarks_list.append(remark_str)
            
            if remarks_list:
                if use_ai_for_remarks and len(remarks_list) > 1:
                    # TODO: Implement AI-based remarks consolidation
                    # For now, just join with newline separator
                    agg_row[remarks_col] = '\n'.join(remarks_list)
                else:
                    # Simple concatenation with newline separator
                    agg_row[remarks_col] = '\n'.join(remarks_list)
            else:
                agg_row[remarks_col] = ''  # Empty string instead of None
        
        aggregated_rows.append(agg_row)
    
    # Regenerate serial numbers
    if ser_no_col:
        for idx, row in enumerate(aggregated_rows, start=1):
            row[ser_no_col] = idx
    
    # Convert NaN and numpy types to Python native types for proper JSON serialization
    # Also ensure columns are in the canonical order
    import numpy as np
    cleaned_rows = []
    
    # Define the exact column order based on sheet type
    if is_armt:
        column_order = [
            'Ser No',
            'Make & Eqpt',
            'Auth (UE)',
            'Held (UH)',
            'Eng/ Brl',
            'MUA',
            'Spares',
            'Under OH /MR/R4/ FR/ Base Repair',  # SA variant (combined column)
            'OH',  # Regular ARMT
            'MR',
            'FR',
            'R4',
            'OBE',
            'Total NMC (Nos)',
            'PMC (Nos) (Due to OH)',
            'FMC',
            'NMC%',
            'PMC%',
            'FMC%',
            'Avl%',
            'Remarks'
        ]
    else:
        column_order = [
            'Ser No',
            'Category (Make & Type)',
            'Auth (UE)',
            'Held (UH)',
            'MUA',
            'OH',
            'R4',
            'Total NMC (Nos)',
            'FMC',
            'Remarks'
        ]
    
    for row in aggregated_rows:
        cleaned_row = {}
        
        # Add columns in specified order
        for col_name in column_order:
            if col_name == 'Ser No' and ser_no_col and ser_no_col in row:
                cleaned_row['Ser No'] = row[ser_no_col]
            elif col_name in [category_col, 'Category (Make & Type)', 'Make & Eqpt'] and category_col in row:
                # Use the actual category column name from this sheet type
                cleaned_row[category_col] = row[category_col]
            elif col_name in numerical_cols and col_name in row:
                # Numerical columns with proper type conversion
                value = row[col_name]
                if pd.isna(value):
                    cleaned_row[col_name] = 0
                elif isinstance(value, (np.integer, np.int64, np.int32)):
                    cleaned_row[col_name] = int(value)
                elif isinstance(value, (np.floating, np.float64, np.float32)):
                    cleaned_row[col_name] = float(value)
                else:
                    cleaned_row[col_name] = value
            elif is_armt and col_name in ['NMC%', 'PMC%', 'FMC%', 'Avl%'] and col_name in row:
                # Percentage columns for ARMT (calculated, not summed)
                value = row[col_name]
                if value is None or pd.isna(value):
                    cleaned_row[col_name] = None  # Will display as "-" in frontend
                elif isinstance(value, (np.floating, np.float64, np.float32, float)):
                    cleaned_row[col_name] = float(value)
                else:
                    cleaned_row[col_name] = value
            elif col_name == 'Remarks' and remarks_col and col_name in row:
                # Remarks column
                value = row[col_name]
                if pd.isna(value) or value is None or str(value).lower() in ['none', 'nan', '-', '']:
                    cleaned_row[col_name] = ''
                else:
                    cleaned_row[col_name] = str(value)
        
        cleaned_rows.append(cleaned_row)
    
    return cleaned_rows


def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate data quality and return metrics.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Dictionary with quality metrics
    """
    if df is None or df.empty:
        return {
            'is_valid': False,
            'issues': ['DataFrame is empty'],
            'metrics': {}
        }
    
    issues = []
    metrics = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'null_count': df.isnull().sum().sum(),
        'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        'duplicate_count': df.duplicated().sum()
    }
    
    # Check for excessive nulls
    if metrics['null_percentage'] > 50:
        issues.append(f"High null percentage: {metrics['null_percentage']:.1f}%")
    
    # Check for all-null columns
    null_columns = df.columns[df.isnull().all()].tolist()
    if null_columns:
        issues.append(f"Columns with all null values: {null_columns}")
    
    # Check for duplicate rows
    if metrics['duplicate_count'] > 0:
        issues.append(f"Found {metrics['duplicate_count']} duplicate rows")
    
    is_valid = len(issues) == 0
    
    return {
        'is_valid': is_valid,
        'issues': issues,
        'metrics': metrics
    }


def dataframe_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert DataFrame to JSON-serializable list of dictionaries.
    
    Args:
        df: DataFrame to convert
    
    Returns:
        List of row dictionaries
    """
    if df is None or df.empty:
        return []
    
    # Convert DataFrame to list of dicts
    # Handle NaN/NaT values by converting to None
    records = df.where(pd.notnull(df), None).to_dict('records')
    
    # Convert numpy types and timestamps to Python native types
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, (pd.Timestamp, datetime)):
                # Convert datetime/Timestamp to ISO format string
                record[key] = value.isoformat()
            elif isinstance(value, (np.integer, np.floating)):
                record[key] = value.item()
            elif isinstance(value, np.bool_):
                record[key] = bool(value)
    
    return records


def json_to_dataframe(json_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert JSON data back to DataFrame.
    
    Args:
        json_data: List of row dictionaries
    
    Returns:
        DataFrame
    """
    if not json_data:
        return pd.DataFrame()
    
    return pd.DataFrame(json_data)


# For testing and debugging
if __name__ == "__main__":
    # Test data cleaning with sample DataFrame
    test_data = {
        'Name': ['Item A', 'Item B', 'Item A', 'Item C', None, '  Item D  '],
        'Quantity': ['10', '20', '10', '30', '40', '50'],
        'Status': ['Active', 'Active', 'Active', 'Inactive', '', 'Active']
    }
    
    df = pd.DataFrame(test_data)
    
    print("Original DataFrame:")
    print(df)
    print("\nData Quality:")
    print(validate_data_quality(df))
    
    print("\nCleaned DataFrame:")
    cleaned = clean_dataframe(df)
    print(cleaned)
    print("\nCleaned Data Quality:")
    print(validate_data_quality(cleaned))
