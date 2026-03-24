"""
Analysis router for A Vehicles FRS comparison.
Generates analysis reports comparing November and December data.
"""
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime, timezone

from database import get_db
from models import Dataset, Unit, SheetData, RemoteWorkshop, LocalWorkshop
from schemas import MessageResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/a-vehicles")
async def analyze_a_vehicles(db: Session = Depends(get_db)):
    """
    Generate A Vehicles analysis report comparing November 2025 vs December 2025.
    
    Returns:
        Analysis report with five sections:
        1. Changes in Authorized/Held
        2. Changes in Eng/MUA (NMC)
        3. Pending Demands (Remote Workshop)
        4. Equipment pending repairs for over three months (Local Workshop)
        5. NMC over 25%
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
        
        # Generate section 3: Pending Demands from Remote Workshop December 2025
        section3_pending = generate_pending_demands(db)
        
        # Generate section 4: NMC over 25%
        section4_nmc = generate_nmc_over_25(dec_data)
        
        # Generate section 5: Equipment pending repairs over 3 months from Local Workshop December 2025
        section5_repairs = generate_pending_repairs(db)
        
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
                "title": "2.1 Have Demands for equipment been placed?",
                "subtitle": "2.1.1 Have the Demands been controlled? Since how long are demands pending (not controlled)?",
                "data": section3_pending["data"],
                "dataset": section3_pending["dataset"],
                "total_pending": section3_pending["total_pending"]
            },
            "section4": {
                "title": "NMC over 25%",
                "data": section4_nmc
            },
            "section5": {
                "title": "Equipment pending repairs for over three months",
                "data": section5_repairs["data"],
                "dataset": section5_repairs["dataset"],
                "total_pending": section5_repairs["total_pending"]
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


def generate_pending_demands(db: Session) -> Dict[str, Any]:
    """
    Get pending demands from Remote Workshop (December 2025).
    
    Filters:
    - Dataset: "Remote Workshop December 2025"
    - Sheets: "Eng", "EOA Spares", "MUA"
    - Control date: blank or "NVR"
    
    Returns table with all columns plus:
    - NMC Type (one of: "Eng", "EOA Spares", "MUA")
    - Pending (Days): days between current date and Demand dt
    """
    try:
        # Find Remote Workshop December 2025 dataset
        dataset = db.query(Dataset).filter(
            Dataset.tag.like("%Remote Workshop%"),
            Dataset.tag.like("%December%"),
            Dataset.tag.like("%2025%")
        ).first()
        
        if not dataset:
            # Return empty result if Remote Workshop dataset not found
            return {
                "dataset": "Remote Workshop December 2025 (Not Found)",
                "total_pending": 0,
                "data": []
            }
        
        # Query Remote Workshop data for Eng, EOA Spares, and MUA sheets
        sheet_names = ["Eng", "EOA Spares", "MUA"]
        remote_data = db.query(RemoteWorkshop).filter(
            RemoteWorkshop.dataset_id == dataset.id,
            RemoteWorkshop.sheet_name.in_(sheet_names)
        ).all()
        
        # Process and filter data
        result = []
        serial_no = 1
        current_date = datetime.now(timezone.utc)
        
        for record in remote_data:
            row_data = record.row_data
            control_date = row_data.get("Control date", "")
            
            # Filter: Control date is blank, None, or "NVR"
            if not control_date or str(control_date).strip().upper() in ["", "NVR", "NONE", "NULL"]:
                demand_dt_str = row_data.get("Demand dt")
                
                # Calculate pending days
                pending_days = None
                if demand_dt_str:
                    try:
                        # Parse the demand date (ISO format from database)
                        if isinstance(demand_dt_str, str):
                            demand_dt = datetime.fromisoformat(demand_dt_str.replace('Z', '+00:00'))
                        else:
                            demand_dt = demand_dt_str
                        
                        # Calculate difference in days
                        if demand_dt:
                            delta = current_date - demand_dt.replace(tzinfo=timezone.utc) if demand_dt.tzinfo is None else current_date - demand_dt
                            pending_days = delta.days
                    except Exception as e:
                        print(f"Error parsing date: {e}")
                        pending_days = None
                
                # Build result row
                result_row = {
                    "serial_no": serial_no,
                    "nmc_type": record.sheet_name,  # "Eng", "EOA Spares", or "MUA"
                    "category": row_data.get("Category", ""),
                    "veh_ba_no": row_data.get("Veh BA No", ""),
                    "formation": row_data.get("Formation", ""),
                    "units": row_data.get("Units", ""),
                    "maint_wksp": row_data.get("MalntWksp", ""),
                    "item_part_no": row_data.get("ItemPart No", ""),
                    "nomenclature": row_data.get("Nomenclature", ""),
                    "qty": row_data.get("Qty", ""),
                    "demand_no": row_data.get("Demand No", ""),
                    "demand_dt": demand_dt_str,
                    "control_no": row_data.get("Control No", ""),
                    "control_date": control_date,
                    "depot": row_data.get("Depot", ""),
                    "remarks": row_data.get("Remarks", ""),
                    "pending_days": pending_days
                }
                
                result.append(result_row)
                serial_no += 1
        
        return {
            "dataset": dataset.tag,
            "total_pending": len(result),
            "data": result
        }
    
    except Exception as e:
        print(f"Error generating pending demands: {e}")
        return {
            "dataset": "Error",
            "total_pending": 0,
            "data": []
        }


def generate_pending_repairs(db: Session) -> Dict[str, Any]:
    """
    Get equipment pending repairs for over 3 months from Local Workshop (December 2025).
    
    Filters:
    - Dataset: "Local Workshop December 2025"
    - Sheets: "FR", "SPARES"
    - Repair Status (Yes/ No): "No" or "NO"
    - Pending Repairs Since (days) > 90 days (3 months)
    
    Returns table with:
    - Serial No (sequential)
    - NMC Type ("FR" or "SPARES")
    - Unit
    - Dependent WorkShop
    - Equipment (Category)
    - Tk BA No
    - Sys/ Sub Sys
    - Nature of Defect
    - Defect dt
    - Pending Repairs Since (days)
    - Reasons (Remarks)
    """
    try:
        # Find Local Workshop December 2025 dataset
        dataset = db.query(Dataset).filter(
            Dataset.tag.like("%Local Workshop%"),
            Dataset.tag.like("%December%"),
            Dataset.tag.like("%2025%")
        ).first()
        
        if not dataset:
            # Return empty result if Local Workshop dataset not found
            return {
                "dataset": "Local Workshop December 2025 (Not Found)",
                "total_pending": 0,
                "data": []
            }
        
        # Query Local Workshop data for FR and SPARES sheets
        sheet_names = ["FR", "SPARES"]
        local_data = db.query(LocalWorkshop).filter(
            LocalWorkshop.dataset_id == dataset.id,
            LocalWorkshop.sheet_name.in_(sheet_names)
        ).all()
        
        # Process and filter data
        result = []
        serial_no = 1
        current_date = datetime.now(timezone.utc)
        
        for record in local_data:
            row_data = record.row_data
            
            # Get repair status - check various possible column names (including with newlines and spaces from Excel)
            repair_status = (
                row_data.get("Repair Status (Yes/ No)", "") or
                row_data.get("Repair Status", "") or
                row_data.get("Repair Status (Yes/No)", "") or
                row_data.get("Repair\nStatus\n(Yes/ No)", "") or  # Column name may have newlines from Excel
                row_data.get("Repair\nStatus \n(Yes/ No)", "") or # With space after Status
                row_data.get("Repair\nStatus", "")
            )
            
            # Filter: Repair Status is "No" or "NO"
            if str(repair_status).strip().upper() not in ["NO", "N"]:
                continue
            
            # Get defect date
            defect_dt_str = row_data.get("Defect dt", "")
            
            # Calculate pending days
            pending_days = None
            if defect_dt_str:
                try:
                    # Parse the defect date (ISO format from database)
                    if isinstance(defect_dt_str, str):
                        defect_dt = datetime.fromisoformat(defect_dt_str.replace('Z', '+00:00'))
                    else:
                        defect_dt = defect_dt_str
                    
                    # Calculate difference in days
                    if defect_dt:
                        delta = current_date - defect_dt.replace(tzinfo=timezone.utc) if defect_dt.tzinfo is None else current_date - defect_dt
                        pending_days = delta.days
                except Exception as e:
                    print(f"Error parsing defect date: {e}")
                    pending_days = None
            
            # Filter: Pending days > 90 (3 months)
            if pending_days is None or pending_days <= 90:
                continue
            
            # Build result row
            result_row = {
                "serial_no": serial_no,
                "nmc_type": record.sheet_name,  # "FR" or "SPARES"
                "unit": record.unit,
                "dependent_workshop": row_data.get("Dependent Wksp", "") or row_data.get("Dependent Workshop", ""),
                "equipment": record.category,
                "tk_ba_no": row_data.get("Tk BA No", "") or row_data.get("TK BA No", ""),
                "sys_sub_sys": row_data.get("Sys/ Sub Sys", "") or row_data.get("System/ Sub System", ""),
                "nature_of_defect": row_data.get("Nature of Defect", ""),
                "defect_dt": defect_dt_str,
                "pending_days": pending_days,
                "reasons": row_data.get("Remarks", "") or row_data.get("Reason", "")
            }
            
            result.append(result_row)
            serial_no += 1
        
        return {
            "dataset": dataset.tag,
            "total_pending": len(result),
            "data": result
        }
    
    except Exception as e:
        print(f"Error generating pending repairs: {e}")
        return {
            "dataset": "Error",
            "total_pending": 0,
            "data": []
        }


@router.get("/pending-demands")
async def get_pending_demands(db: Session = Depends(get_db)):
    """
    Legacy endpoint for pending demands. Now integrated into A Vehicles analysis.
    Kept for backward compatibility.
    """
    try:
        result = generate_pending_demands(db)
        return {
            "title": "2.1 Have Demands for equipment been placed?",
            "subtitle": "2.1.1 Have the Demands been controlled? Since how long are demands pending (not controlled)?",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
