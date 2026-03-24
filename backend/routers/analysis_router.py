"""
Analysis router for A Vehicles FRS comparison.
Generates analysis reports comparing November and December data.
"""
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

from database import get_db
from models import Dataset, Unit, SheetData
from schemas import MessageResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/a-vehicles")
async def analyze_a_vehicles(db: Session = Depends(get_db)):
    """
    Generate A Vehicles analysis report comparing November 2025 vs December 2025.
    
    Returns:
        Analysis report with three sections:
        1. Changes in Authorized/Held
        2. Changes in Eng/MUA (NMC)
        3. NMC over 25%
    """
    try:
        # Find November and December 2025 datasets
        nov_dataset = db.query(Dataset).filter(Dataset.tag == "November 2025").first()
        dec_dataset = db.query(Dataset).filter(Dataset.tag == "December 2025").first()
        
        if not nov_dataset or not dec_dataset:
            raise HTTPException(
                status_code=404, 
                detail="November 2025 or December 2025 dataset not found"
            )
        
        # Get A Vehicle (APPX_A_AVEH) data for both months
        nov_data = get_a_vehicle_data(db, nov_dataset.id)
        dec_data = get_a_vehicle_data(db, dec_dataset.id)
        
        # Generate analysis sections
        section1 = generate_authorized_held_changes(nov_data, dec_data)
        section2 = generate_eng_mua_changes(nov_data, dec_data)
        section3 = generate_nmc_over_25(dec_data)
        
        return {
            "title": "A Vehicles: FRS Previous vs Current Month changes",
            "previous_month": "November 2025",
            "current_month": "December 2025",
            "section1": {
                "title": "Changes in Authorized/Held",
                "data": section1
            },
            "section2": {
                "title": "Change in Eng/MUA (NMC)",
                "data": section2
            },
            "section3": {
                "title": "NMC over 25%",
                "data": section3
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_a_vehicle_data(db: Session, dataset_id: int) -> List[Dict[str, Any]]:
    """
    Fetch A Vehicle (APPX_A_AVEH) sheet data for a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
    
    Returns:
        List of row data dictionaries
    """
    query = db.query(SheetData).join(Unit).filter(
        Unit.dataset_id == dataset_id,
        SheetData.sheet_type == "APPX_A_AVEH"
    )
    
    sheet_records = query.all()
    
    # Flatten all row_data into a single list
    all_rows = []
    for record in sheet_records:
        if record.row_data:
            all_rows.extend(record.row_data)
    
    return all_rows


def is_valid_entry(equipment: str, unit: str) -> bool:
    """
    Check if equipment and unit values are valid (not empty, None, or common invalid values).
    """
    if not equipment or not unit:
        return False
    
    # Strip whitespace
    equipment = equipment.strip()
    unit = unit.strip()
    
    # Check for empty or whitespace-only strings
    if not equipment or not unit:
        return False
    
    # Check for common invalid values
    invalid_values = ['none', 'nan', 'null', 'n/a', '-', '']
    if equipment.lower() in invalid_values or unit.lower() in invalid_values:
        return False
    
    # Check for numeric-only equipment names (likely invalid)
    if equipment.replace('.', '').replace(',', '').isdigit():
        return False
    
    return True


def generate_authorized_held_changes(nov_data: List[Dict], dec_data: List[Dict]) -> List[Dict]:
    """
    Generate Section 1: Changes in Authorized/Held.
    
    Key: Combination of "Category (Make & Type)" and "Units"
    """
    # Build dictionaries keyed by (Equipment, Unit)
    nov_dict = {}
    for row in nov_data:
        equipment = str(row.get('Category (Make & Type)', '')).strip()
        unit = str(row.get('Units', '')).strip()
        
        # Validate entry before adding
        if is_valid_entry(equipment, unit):
            key = (equipment, unit)
            nov_dict[key] = {
                'authorized': parse_number(row.get('Auth (UE)', 0)),
                'held': parse_number(row.get('Held (UH)', 0))
            }
    
    dec_dict = {}
    for row in dec_data:
        equipment = str(row.get('Category (Make & Type)', '')).strip()
        unit = str(row.get('Units', '')).strip()
        
        # Validate entry before adding
        if is_valid_entry(equipment, unit):
            key = (equipment, unit)
            dec_dict[key] = {
                'authorized': parse_number(row.get('Auth (UE)', 0)),
                'held': parse_number(row.get('Held (UH)', 0))
            }
    
    # Merge and calculate deltas
    all_keys = set(nov_dict.keys()) | set(dec_dict.keys())
    result = []
    
    for idx, key in enumerate(sorted(all_keys), start=1):
        equipment, unit = key
        
        nov_auth = nov_dict.get(key, {}).get('authorized', 0)
        nov_held = nov_dict.get(key, {}).get('held', 0)
        dec_auth = dec_dict.get(key, {}).get('authorized', 0)
        dec_held = dec_dict.get(key, {}).get('held', 0)
        
        result.append({
            'serial_no': idx,
            'equipment': equipment,
            'unit': unit,
            'previous_authorized': nov_auth,
            'previous_held': nov_held,
            'current_authorized': dec_auth,
            'current_held': dec_held,
            'delta_authorized': dec_auth - nov_auth,
            'delta_held': dec_held - nov_held
        })
    
    return result


def generate_eng_mua_changes(nov_data: List[Dict], dec_data: List[Dict]) -> List[Dict]:
    """
    Generate Section 2: Change in Eng/MUA (NMC).
    
    Key: Combination of "Category (Make & Type)" and "Units"
    """
    # Build dictionaries keyed by (Equipment, Unit)
    nov_dict = {}
    for row in nov_data:
        equipment = str(row.get('Category (Make & Type)', '')).strip()
        unit = str(row.get('Units', '')).strip()
        
        # Validate entry before adding
        if is_valid_entry(equipment, unit):
            key = (equipment, unit)
            nov_dict[key] = {
                'eng': parse_number(row.get('Eng', 0)),
                'mua': parse_number(row.get('MUA', 0))
            }
    
    dec_dict = {}
    for row in dec_data:
        equipment = str(row.get('Category (Make & Type)', '')).strip()
        unit = str(row.get('Units', '')).strip()
        
        # Validate entry before adding
        if is_valid_entry(equipment, unit):
            key = (equipment, unit)
            dec_dict[key] = {
                'eng': parse_number(row.get('Eng', 0)),
                'mua': parse_number(row.get('MUA', 0))
            }
    
    # Merge and calculate deltas
    all_keys = set(nov_dict.keys()) | set(dec_dict.keys())
    result = []
    
    for idx, key in enumerate(sorted(all_keys), start=1):
        equipment, unit = key
        
        nov_eng = nov_dict.get(key, {}).get('eng', 0)
        nov_mua = nov_dict.get(key, {}).get('mua', 0)
        dec_eng = dec_dict.get(key, {}).get('eng', 0)
        dec_mua = dec_dict.get(key, {}).get('mua', 0)
        
        result.append({
            'serial_no': idx,
            'equipment': equipment,
            'unit': unit,
            'previous_eng': nov_eng,
            'previous_mua': nov_mua,
            'current_eng': dec_eng,
            'current_mua': dec_mua,
            'delta_eng': dec_eng - nov_eng,
            'delta_mua': dec_mua - nov_mua
        })
    
    return result


def generate_nmc_over_25(dec_data: List[Dict]) -> List[Dict]:
    """
    Generate Section 3: NMC over 25% from December data.
    
    Filters rows where NMC% > 25 and equipment/unit are valid.
    """
    result = []
    serial_no = 1
    
    for row in dec_data:
        equipment = str(row.get('Category (Make & Type)', '')).strip()
        unit = str(row.get('Units', '')).strip()
        
        # Validate entry before processing
        if not is_valid_entry(equipment, unit):
            continue
        
        nmc_pct = parse_number(row.get('NMC %', 0))
        
        # Filter where NMC% > 25 (treating as percentage value)
        if nmc_pct > 25:
            # Try multiple possible column names for remarks
            remarks = (
                str(row.get('Remarks', '')).strip() or
                str(row.get('Remarks (To incl present loc of eqpt EOA)', '')).strip() or
                str(row.get('Remarks (To incl present loc of eqpt at EOA)', '')).strip()
            )
            
            result.append({
                'serial_no': serial_no,
                'equipment': equipment,
                'unit': unit,
                'nmc_percent': nmc_pct,
                'reasons': remarks if remarks else '-'
            })
            serial_no += 1
    
    return result


def parse_number(value: Any) -> float:
    """
    Parse a value to float, handling None and string values.
    """
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
