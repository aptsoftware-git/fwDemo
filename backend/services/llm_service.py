"""
LLM service for FRS Data Management System.
Provides AI-powered comparison of datasets using local Ollama LLM.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from sqlalchemy.orm import Session

from config import LLM_MODE, OLLAMA_URL, LLM_MODEL, LLM_TIMEOUT, LLM_MAX_ROWS
from models import Dataset, Unit, SheetData
from processors.data_cleaner import json_to_dataframe, aggregate_by_category
from metadata_utils import get_system_prompt_for_comparison
from model_config import get_model_info, get_recommended_settings, DEFAULT_MODEL, get_all_models


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
        return 0.0
    
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
    
    return 0.0


# Global state for current loaded model
_current_model = {
    "name": DEFAULT_MODEL,
    "loaded": False,
    "timeout": LLM_TIMEOUT
}


class LLMClient:
    """Base class for LLM clients"""
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Generated text
        """
        raise NotImplementedError


class OllamaClient(LLMClient):
    """Client for local Ollama LLM using chat endpoint"""
    
    def __init__(self, api_url: str, model_name: str, timeout: int = 35):
        self.api_url = api_url  # Full URL including /api/chat
        self.model_name = model_name
        self.timeout = timeout
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using Ollama chat API"""
        try:
            # Build messages array for chat format
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000  # Limit response length
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            
            # DEBUG: Log the response structure
            print(f"\n=== LLM RESPONSE DEBUG ===")
            print(f"Response keys: {list(result.keys())}")
            if 'message' in result:
                print(f"Message keys: {list(result['message'].keys())}")
                print(f"Content length: {len(result['message'].get('content', ''))}")
                print(f"Content preview: {result['message'].get('content', '')[:200]}...")
            elif 'response' in result:
                print(f"Response length: {len(result.get('response', ''))}")
                print(f"Response preview: {result.get('response', '')[:200]}...")
            else:
                print(f"Full result: {result}")
            print(f"=== END LLM RESPONSE DEBUG ===\n")
            
            # Extract message content from chat response
            if 'message' in result and 'content' in result['message']:
                return result['message']['content']
            return result.get('response', '')
        
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.api_url}. Make sure Ollama is running.")
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out after {self.timeout} seconds. Try reducing data size or increasing timeout.")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")


def get_llm_client() -> LLMClient:
    """
    Get LLM client (Ollama only).
    
    Returns:
        Configured Ollama LLM client using current loaded model
    
    Raises:
        ValueError: If LLM_MODE is not 'local'
    """
    mode = LLM_MODE.lower()
    
    if mode == 'local':
        # Use current loaded model settings
        model_name = _current_model["name"]
        timeout = _current_model["timeout"]
        return OllamaClient(OLLAMA_URL, model_name, timeout)
    else:
        raise ValueError(f"Invalid LLM_MODE: {mode}. Only 'local' mode is supported.")


# === Model Management Functions ===

def get_available_models_from_ollama() -> List[Dict]:
    """
    Fetch list of available models from Ollama server.
    
    Returns:
        List of model dictionaries with name, size, and configuration
    """
    try:
        # Ollama list API endpoint
        base_url = OLLAMA_URL.replace('/api/chat', '')
        list_url = f"{base_url}/api/tags"
        
        response = requests.get(list_url, timeout=10)
        response.raise_for_status()
        
        ollama_models = response.json().get('models', [])
        
        # Enrich with our configuration
        enriched_models = []
        for model in ollama_models:
            model_name = model.get('name', '')
            model_info = get_model_info(model_name)
            
            enriched_models.append({
                "name": model_name,
                "size": model_info.get("size", "N/A"),
                "tier": model_info.get("tier", "Unknown"),
                "description": model_info.get("description", ""),
                "modified_at": model.get('modified_at', ''),
                "ollama_size": model.get('size', 0)
            })
        
        return enriched_models
    
    except Exception as e:
        # Fallback to configured models if Ollama is unreachable
        print(f"Warning: Could not fetch models from Ollama: {e}")
        return get_all_models()


def load_model(model_name: str) -> Dict:
    """
    Load a specific model in Ollama server (warm-up).
    
    Args:
        model_name: Name of the model to load
    
    Returns:
        Status dictionary with success/error info
    """
    try:
        # Get recommended settings for this model
        settings = get_recommended_settings(model_name)
        
        # Make a simple generation request to load the model into memory
        base_url = OLLAMA_URL.replace('/api/chat', '')
        generate_url = f"{base_url}/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": "Hello",
            "stream": False
        }
        
        response = requests.post(generate_url, json=payload, timeout=30)
        response.raise_for_status()
        
        # Update global state
        _current_model["name"] = model_name
        _current_model["loaded"] = True
        _current_model["timeout"] = settings["timeout"]
        
        return {
            "success": True,
            "model": model_name,
            "message": f"Successfully loaded {model_name}",
            "settings": settings
        }
    
    except Exception as e:
        return {
            "success": False,
            "model": model_name,
            "message": f"Failed to load model: {str(e)}"
        }


def get_current_model() -> Dict:
    """
    Get currently loaded model information.
    
    Returns:
        Dictionary with current model details
    """
    model_info = get_model_info(_current_model["name"])
    
    return {
        "name": _current_model["name"],
        "loaded": _current_model["loaded"],
        "timeout": _current_model["timeout"],
        "tier": model_info.get("tier", "Unknown"),
        "size": model_info.get("size", "N/A"),
        "description": model_info.get("description", "")
    }


def initialize_default_model():
    """Initialize the default model on startup."""
    print(f"Initializing default model: {DEFAULT_MODEL}")
    result = load_model(DEFAULT_MODEL)
    if result["success"]:
        print(f"✓ Default model loaded successfully")
    else:
        print(f"Warning: Could not load default model: {result['message']}")
        # Still set it as current even if loading failed (will load on first use)
        _current_model["name"] = DEFAULT_MODEL
        _current_model["loaded"] = False


def generate_differences(data1: List[Dict], data2: List[Dict], sheet_type: str) -> str:
    """
    Generate detailed differences between two datasets for a specific sheet.
    
    Args:
        data1: First dataset (list of row dictionaries)
        data2: Second dataset (list of row dictionaries)
        sheet_type: Sheet type identifier
    
    Returns:
        Formatted string describing differences
    """
    differences = []
    
    # Basic statistics
    differences.append(f"## {sheet_type}")
    differences.append(f"Dataset 1: {len(data1)} rows")
    differences.append(f"Dataset 2: {len(data2)} rows")
    differences.append(f"Row count change: {len(data2) - len(data1):+d}")
    differences.append("")
    
    # If both datasets are empty, skip
    if not data1 and not data2:
        differences.append("Both datasets are empty.")
        return "\n".join(differences)
    
    # Convert to DataFrames for easier comparison
    df1 = json_to_dataframe(data1) if data1 else None
    df2 = json_to_dataframe(data2) if data2 else None
    
    # Line-by-line comparison (first 10 rows for performance with local LLM)
    max_rows = min(10, max(len(data1) if data1 else 0, len(data2) if data2 else 0))
    
    for i in range(max_rows):
        row1 = data1[i] if i < len(data1) else None
        row2 = data2[i] if i < len(data2) else None
        
        if row1 is None and row2 is not None:
            differences.append(f"Row {i+1}: ADDED in Dataset 2")
            differences.append(f"  {json.dumps(row2, indent=2)}")
        elif row1 is not None and row2 is None:
            differences.append(f"Row {i+1}: REMOVED in Dataset 2")
            differences.append(f"  {json.dumps(row1, indent=2)}")
        elif row1 != row2:
            differences.append(f"Row {i+1}: CHANGED")
            # Show column-level differences
            for key in set(list(row1.keys()) + list(row2.keys())):
                val1 = row1.get(key)
                val2 = row2.get(key)
                if val1 != val2:
                    differences.append(f"  {key}: {val1} → {val2}")
    
    if max_rows < max(len(data1), len(data2)):
        differences.append(f"\n... (showing first {max_rows} rows, {max(len(data1), len(data2)) - max_rows} more rows not shown)")
    
    return "\n".join(differences)


def calculate_unit_readiness(unit_id: int, unit_name: str, sheet_type: str, db: Session, debug: bool = True) -> float:
    """
    Calculate FMC% (readiness) for a specific unit and sheet type.
    
    Args:
        unit_id: Unit ID
        unit_name: Unit name (for debug output)
        sheet_type: Sheet type
        db: Database session
        debug: Whether to print debug information
    
    Returns:
        FMC percentage (0-100), or None if cannot be calculated
    """
    if debug:
        print(f"\n=== Calculating Readiness for {unit_name} ({sheet_type}) ===")
    
    sheets = db.query(SheetData).filter(
        SheetData.unit_id == unit_id,
        SheetData.sheet_type == sheet_type
    ).all()
    
    if not sheets:
        if debug:
            print(f"  ✗ No sheets found for {unit_name} - {sheet_type}")
        return None
    
    if debug:
        print(f"  Found {len(sheets)} sheet(s) for {unit_name}")
    
    # Aggregate data from all sheets for this unit
    all_rows = []
    for sheet in sheets:
        all_rows.extend(sheet.row_data)
    
    if not all_rows:
        if debug:
            print(f"  ✗ No row data found in sheets")
        return None
    
    if debug:
        print(f"  Total rows to process: {len(all_rows)}")
    
    # Calculate totals
    total_fmc = 0
    total_held = 0
    row_count = 0
    problematic_rows = []
    
    for row in all_rows:
        fmc = row.get('FMC', 0)
        
        # Try multiple variations of the "Held" field name
        held = (row.get('Held (UH)') or 
                row.get('Held\n(UH)') or 
                row.get('Held') or 
                row.get('Held (UH )') or
                row.get('Held\n(UH )') or
                0)
        
        # Extract numeric values (handles special characters like 17*, 1+@1, 1#, etc.)
        fmc_val = extract_numeric_value(fmc)
        held_val = extract_numeric_value(held)
        
        # Track rows where FMC exists but Held is 0 (potential issue)
        if fmc_val > 0 and held_val == 0:
            if len(problematic_rows) < 3:  # Store first 3 problematic rows
                problematic_rows.append({
                    'row_data': row,
                    'fmc_val': fmc_val,
                    'held_val': held_val
                })
        
        if fmc_val > 0 or held_val > 0:
            row_count += 1
            if debug and row_count <= 3:  # Show first 3 rows
                category = row.get('Category (Make & Type)', row.get('Make & Eqpt', 'Unknown'))
                print(f"    Row {row_count}: {category} - FMC={fmc_val}, Held={held_val}")
        
        total_fmc += fmc_val
        total_held += held_val
    
    # If we have problematic rows, show detailed debug
    if problematic_rows and debug:
        print(f"\n  ⚠️ WARNING: Found {len(problematic_rows)} rows with FMC but no Held value")
        for i, prob in enumerate(problematic_rows[:2], 1):
            row = prob['row_data']
            print(f"\n  Problematic Row {i}:")
            print(f"    Available keys: {list(row.keys())}")
            print(f"    FMC: {prob['fmc_val']}")
            print(f"    Held (UH): {prob['held_val']}")
            # Check for alternative Held field names
            for key in row.keys():
                if 'held' in key.lower() or 'uh' in key.lower():
                    print(f"    {key}: {row[key]}")
    
    if debug:
        print(f"  Total FMC: {total_fmc}")
        print(f"  Total Held (UH): {total_held}")
    
    # Calculate FMC%
    if total_held > 0:
        readiness = (total_fmc / total_held) * 100
        if debug:
            print(f"  ✓ Readiness (FMC%): {readiness:.2f}%")
        return readiness
    
    if debug:
        print(f"  ✗ Cannot calculate readiness - Total Held is 0")
    return None


def compare_datasets(tag1: str, tag2: str, sheet_type: str, 
                    prompt_template: str, db: Session) -> Dict:
    """
    Compare two datasets for a specific sheet type using custom prompt.
    
    Args:
        tag1: First dataset tag (previous/older)
        tag2: Second dataset tag (current/newer)
        sheet_type: Sheet type to compare
        prompt_template: Custom prompt template with placeholders
        db: Database session
    
    Returns:
        Dictionary with comparison_text and readiness_data
    
    Raises:
        ValueError: If datasets not found or no data for sheet type
        Exception: If comparison fails
    """
    # Fetch datasets
    dataset1 = db.query(Dataset).filter(Dataset.tag == tag1).first()
    dataset2 = db.query(Dataset).filter(Dataset.tag == tag2).first()
    
    if not dataset1:
        raise ValueError(f"Dataset not found: {tag1}")
    if not dataset2:
        raise ValueError(f"Dataset not found: {tag2}")
    
    # Fetch all units and sheet data for both datasets
    units1 = db.query(Unit).filter(Unit.dataset_id == dataset1.id).all()
    units2 = db.query(Unit).filter(Unit.dataset_id == dataset2.id).all()
    
    # Collect sheet data for the specific sheet type
    previous_data = []
    current_data = []
    
    # Aggregate data from all units for dataset 1 (previous)
    for unit in units1:
        sheets = db.query(SheetData).filter(
            SheetData.unit_id == unit.id,
            SheetData.sheet_type == sheet_type
        ).all()
        for sheet in sheets:
            previous_data.extend(sheet.row_data)
    
    # Aggregate data from all units for dataset 2 (current)
    for unit in units2:
        sheets = db.query(SheetData).filter(
            SheetData.unit_id == unit.id,
            SheetData.sheet_type == sheet_type
        ).all()
        for sheet in sheets:
            current_data.extend(sheet.row_data)
    
    if not previous_data and not current_data:
        raise ValueError(f"No data found for sheet type: {sheet_type}")
    
    # Apply aggregation (same logic as UI - aggregate data from multiple units)
    if len(units1) > 1:
        print(f"\n=== Aggregating PREVIOUS data from {len(units1)} units ===")
        previous_data = aggregate_by_category(previous_data, use_ai_for_remarks=False)
        print(f"After aggregation: {len(previous_data)} rows\n")
    
    if len(units2) > 1:
        print(f"\n=== Aggregating CURRENT data from {len(units2)} units ===")
        current_data = aggregate_by_category(current_data, use_ai_for_remarks=False)
        print(f"After aggregation: {len(current_data)} rows\n")
    
    # Load metadata
    metadata_file = Path(__file__).parent.parent / 'metadata_summary.json'
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {"note": "Metadata file not found"}
    
    # Format data for LLM (use LLM_MAX_ROWS for each dataset in comparison)
    previous_data_limited = previous_data[:LLM_MAX_ROWS] if previous_data else []
    current_data_limited = current_data[:LLM_MAX_ROWS] if current_data else []
    
    # DEBUG: Print first 2 rows of data being sent to LLM for comparison
    print(f"\n=== COMPARISON DEBUG ===")
    print(f"Sheet Type: {sheet_type}")
    print(f"Previous data total rows: {len(previous_data)}")
    print(f"Current data total rows: {len(current_data)}")
    print(f"Sending to LLM - Previous: {len(previous_data_limited)} rows, Current: {len(current_data_limited)} rows")
    print(f"\nFirst 2 rows of PREVIOUS data:")
    print(json.dumps(previous_data_limited[:2], indent=2))
    print(f"\nFirst 2 rows of CURRENT data:")
    print(json.dumps(current_data_limited[:2], indent=2))
    print(f"=== END COMPARISON DEBUG ===\n")
    
    # Prepare the prompt by replacing placeholders
    formatted_prompt = prompt_template.replace(
        '{metadata}', json.dumps(metadata, indent=2)
    ).replace(
        '{previous_data}', json.dumps(previous_data_limited, indent=2)
    ).replace(
        '{current_data}', json.dumps(current_data_limited, indent=2)
    ).replace(
        '{sheet_type}', sheet_type
    )
    
    # Generate comparison using LLM
    try:
        llm_client = get_llm_client()
        system_prompt = "You are a Senior Military Logistics Analyst specializing in comparative readiness analysis. Format your response in clear, structured markdown."
        comparison_text = llm_client.generate(formatted_prompt, system_prompt)
        
        # Calculate readiness per unit for chart display
        print(f"\n" + "="*80)
        print(f"FORMATION READINESS CALCULATION - {sheet_type}")
        print(f"Dataset 1: {tag1} | Dataset 2: {tag2}")
        print("="*80)
        
        readiness_data = []
        
        # Calculate for dataset 1 (previous period)
        print(f"\n📊 PREVIOUS PERIOD ({tag1}) - Found {len(units1)} formation(s):")
        for unit in units1:
            readiness = calculate_unit_readiness(unit.id, unit.unit_name, sheet_type, db, debug=True)
            if readiness is not None:
                readiness_data.append({
                    "formation": unit.unit_name,
                    "previous_readiness": round(readiness, 2),
                    "current_readiness": None  # Will be filled below
                })
            else:
                print(f"  ⚠️ {unit.unit_name}: Could not calculate readiness")
        
        # Calculate for dataset 2 (current period)
        print(f"\n📊 CURRENT PERIOD ({tag2}) - Found {len(units2)} formation(s):")
        for unit in units2:
            readiness = calculate_unit_readiness(unit.id, unit.unit_name, sheet_type, db, debug=True)
            if readiness is not None:
                # Find matching formation in readiness_data
                matching_entry = next((item for item in readiness_data if item["formation"] == unit.unit_name), None)
                if matching_entry:
                    matching_entry["current_readiness"] = round(readiness, 2)
                else:
                    # Unit exists in dataset2 but not in dataset1
                    readiness_data.append({
                        "formation": unit.unit_name,
                        "previous_readiness": None,
                        "current_readiness": round(readiness, 2)
                    })
            else:
                print(f"  ⚠️ {unit.unit_name}: Could not calculate readiness")
        
        # Print summary table
        print(f"\n" + "="*80)
        print(f"READINESS SUMMARY - {sheet_type}")
        print("="*80)
        print(f"{'Formation':<20} | {'Previous Period':<20} | {'Current Period':<20} | {'Change':<15}")
        print("-" * 80)
        
        for data in readiness_data:
            formation = data['formation']
            prev = data.get('previous_readiness')
            curr = data.get('current_readiness')
            
            prev_str = f"{prev:.2f}%" if prev is not None else "N/A"
            curr_str = f"{curr:.2f}%" if curr is not None else "N/A"
            
            if prev is not None and curr is not None:
                change = curr - prev
                change_str = f"{change:+.2f}%"
            else:
                change_str = "N/A"
            
            print(f"{formation:<20} | {prev_str:<20} | {curr_str:<20} | {change_str:<15}")
        
        print("="*80 + "\n")
        
        return {
            "comparison_text": comparison_text,
            "readiness_data": readiness_data
        }
    
    except Exception as e:
        raise Exception(f"Failed to generate LLM comparison: {str(e)}")


def generate_summary(tag: str, unit_filter: str, sheet_type: str, 
                    prompt_template: str, db: Session) -> str:
    """
    Generate executive summary for selected data using LLM.
    
    Args:
        tag: Dataset tag
        unit_filter: Unit filter ('All' or specific unit name)
        sheet_type: Sheet type to summarize
        prompt_template: Custom prompt template with {metadata} and {data} placeholders
        db: Database session
    
    Returns:
        LLM-generated summary text
    
    Raises:
        ValueError: If dataset not found
        Exception: If summary generation fails
    """
    # Fetch dataset
    dataset = db.query(Dataset).filter(Dataset.tag == tag).first()
    if not dataset:
        raise ValueError(f"Dataset not found: {tag}")
    
    # Fetch units based on filter
    if unit_filter == "All":
        units = db.query(Unit).filter(Unit.dataset_id == dataset.id).all()
    else:
        units = db.query(Unit).filter(
            Unit.dataset_id == dataset.id,
            Unit.unit_name == unit_filter
        ).all()
    
    if not units:
        raise ValueError(f"No units found for filter: {unit_filter}")
    
    # Collect sheet data for specified sheet type
    sheet_data = []
    for unit in units:
        sheets = db.query(SheetData).filter(
            SheetData.unit_id == unit.id,
            SheetData.sheet_type == sheet_type
        ).all()
        for sheet in sheets:
            sheet_data.extend(sheet.row_data)
    
    if not sheet_data:
        raise ValueError(f"No data found for sheet type: {sheet_type}")
    
    # DEBUG: Show which units/datasets are being queried
    print(f"\n=== DATA FETCH DEBUG ===")
    print(f"Unit filter: {unit_filter}")
    print(f"Units queried: {[u.unit_name for u in units]}")
    print(f"Total rows fetched (before aggregation): {len(sheet_data)}")
    
    # Apply aggregation if "All" units selected (same logic as UI)
    if unit_filter == "All" and len(units) > 1:
        print(f"Aggregating data from {len(units)} units...")
        sheet_data = aggregate_by_category(sheet_data, use_ai_for_remarks=False)
        print(f"After aggregation: {len(sheet_data)} rows")
    
    print(f"=== END DATA FETCH DEBUG ===\n")
    
    # Load metadata from JSON file
    import json
    from pathlib import Path
    
    metadata_path = Path(__file__).parent.parent / "metadata_summary.json"
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load metadata: {str(e)}")
    
    # Format metadata as readable text
    metadata_text = json.dumps(metadata, indent=2)
    
    # Format data (limit to configured max rows for performance)
    data_sample = sheet_data[:LLM_MAX_ROWS]
    data_text = json.dumps(data_sample, indent=2)
    
    if len(sheet_data) > LLM_MAX_ROWS:
        data_text += f"\n\n... (showing first {LLM_MAX_ROWS} rows out of {len(sheet_data)} total rows)"
    
    # DEBUG: Print first 2 rows of data being sent to LLM for summary
    print(f"\n=== SUMMARY DEBUG ===")
    print(f"Tag: {tag}")
    print(f"Unit Filter: {unit_filter}")
    print(f"Sheet Type: {sheet_type}")
    print(f"Total rows collected: {len(sheet_data)}")
    print(f"Sending to LLM: {len(data_sample)} rows")
    print(f"Metadata length: {len(metadata_text)} chars")
    print(f"Data length: {len(data_text)} chars")
    print(f"\nFirst 2 rows of data:")
    print(json.dumps(data_sample[:2], indent=2))
    print(f"=== END SUMMARY DEBUG ===\n")
    
    # Fill in the prompt template
    try:
        filled_prompt = prompt_template.format(
            metadata=metadata_text,
            data=data_text
        )
        print(f"\n=== PROMPT LENGTH DEBUG ===")
        print(f"Total prompt length: {len(filled_prompt)} characters")
        print(f"Estimated tokens: ~{len(filled_prompt) // 4}")
        print(f"=== END PROMPT LENGTH DEBUG ===\n")
    except KeyError as e:
        raise ValueError(f"Invalid prompt template: missing placeholder {str(e)}")
    
    # Generate summary using LLM
    try:
        llm_client = get_llm_client()
        
        system_prompt = "You are a Military Logistics Analyst specializing in Formation Readiness State analysis."
        
        summary_text = llm_client.generate(filled_prompt, system_prompt)
        
        print(f"\n=== GENERATE_SUMMARY RETURN DEBUG ===")
        print(f"Summary text length: {len(summary_text)}")
        print(f"Summary text type: {type(summary_text)}")
        print(f"Summary preview (first 200 chars): {summary_text[:200]}")
        print(f"=== END RETURN DEBUG ===\n")
        
        return summary_text
    
    except Exception as e:
        raise Exception(f"Failed to generate LLM summary: {str(e)}")


# For testing and debugging
if __name__ == "__main__":
    # Test LLM client initialization
    try:
        client = get_llm_client()
        print(f"LLM client initialized: {type(client).__name__}")
        
        # Test simple generation
        test_prompt = "Explain the purpose of Formation Readiness State reports in one sentence."
        response = client.generate(test_prompt)
        print(f"\nTest response: {response}")
    
    except Exception as e:
        print(f"Error: {e}")
