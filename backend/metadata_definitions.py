"""
FRS Equipment Readiness Metadata Definitions

This module provides structured metadata for all equipment categories in the FRS system.
Use this as the definitive source for column definitions, validation rules, and metrics.
"""

from typing import Dict, List, TypedDict


class ColumnDefinition(TypedDict):
    """Structure for column metadata"""
    full_name: str
    description: str
    data_type: str  # 'integer', 'text', 'percentage', 'decimal'
    required: bool


class SheetMetadata(TypedDict):
    """Structure for sheet type metadata"""
    name: str
    description: str
    columns: Dict[str, ColumnDefinition]
    key_metrics: List[str]
    validation_rules: List[str]


# B Vehicles (Transport)
BVEH_METADATA: SheetMetadata = {
    "name": "B Vehicles",
    "description": "Soft-skinned transport vehicles including trucks, jeeps, and utility vehicles",
    "columns": {
        "Ser No": {
            "full_name": "Serial Number",
            "description": "Sequential order of entries in the report",
            "data_type": "integer",
            "required": True
        },
        "Category (Make & Type)": {
            "full_name": "Category Make & Type",
            "description": "Manufacturer and specific model/capacity (e.g., 2.5 Ton Truck)",
            "data_type": "text",
            "required": True
        },
        "Auth (UE)": {
            "full_name": "Authorized (Unit Establishment)",
            "description": "Official number of units permitted by regulation",
            "data_type": "integer",
            "required": True
        },
        "Held (UH)": {
            "full_name": "Held (Unit Holding)",
            "description": "Actual number of units in inventory",
            "data_type": "integer",
            "required": True
        },
        "MUA": {
            "full_name": "Minor Under Activity",
            "description": "Units undergoing light, routine maintenance",
            "data_type": "integer",
            "required": False
        },
        "OH": {
            "full_name": "Overhaul",
            "description": "Units undergoing major reconditioning",
            "data_type": "integer",
            "required": False
        },
        "R4": {
            "full_name": "Repair Level 4",
            "description": "Units requiring specialized workshop repairs",
            "data_type": "integer",
            "required": False
        },
        "Total": {
            "full_name": "Total Non-Mission Capable",
            "description": "Sum of all unserviceable units (MUA + OH + R4)",
            "data_type": "integer",
            "required": True
        },
        "FMC": {
            "full_name": "Fully Mission Capable",
            "description": "Units 100% fit for immediate deployment",
            "data_type": "integer",
            "required": True
        },
        "Remarks (To incl present loc of eqpt EOA)": {
            "full_name": "Remarks and EOA Details",
            "description": "Notes on Vehicle Off Road (VOR) demands or Equipment On Account (EOA) status",
            "data_type": "text",
            "required": False
        }
    },
    "key_metrics": [
        "Serviceability % = (FMC / Held) × 100",
        "Availability % = ((Held - Total) / Auth) × 100"
    ],
    "validation_rules": [
        "Held ≤ Auth",
        "FMC ≤ Held",
        "Total = MUA + OH + R4"
    ]
}


# C Vehicles (Engineering Plant)
CVEH_METADATA: SheetMetadata = {
    "name": "C Vehicles",
    "description": "Heavy engineering plant equipment including dozers, excavators, graders",
    "columns": {
        "Ser No": {
            "full_name": "Serial Number",
            "description": "Sequential order of entries in the report",
            "data_type": "integer",
            "required": True
        },
        "Category (Make & Type)": {
            "full_name": "Category Make & Type",
            "description": "Manufacturer and specific model (e.g., D6 Dozer)",
            "data_type": "text",
            "required": True
        },
        "Auth (UE)": {
            "full_name": "Authorized (Unit Establishment)",
            "description": "Official number of units permitted by regulation",
            "data_type": "integer",
            "required": True
        },
        "Held (UH)": {
            "full_name": "Held (Unit Holding)",
            "description": "Actual number of units in inventory",
            "data_type": "integer",
            "required": True
        },
        "MUA": {
            "full_name": "Minor Under Activity",
            "description": "Units undergoing light, routine maintenance",
            "data_type": "integer",
            "required": False
        },
        "OH": {
            "full_name": "Overhaul",
            "description": "Units undergoing major reconditioning",
            "data_type": "integer",
            "required": False
        },
        "R4": {
            "full_name": "Repair Level 4",
            "description": "Units requiring specialized workshop repairs",
            "data_type": "integer",
            "required": False
        },
        "Total": {
            "full_name": "Total Non-Mission Capable",
            "description": "Sum of all unserviceable units (MUA + OH + R4)",
            "data_type": "integer",
            "required": True
        },
        "FMC": {
            "full_name": "Fully Mission Capable",
            "description": "Units 100% fit for immediate deployment",
            "data_type": "integer",
            "required": True
        },
        "Remarks (To incl present loc of eqpt EOA)": {
            "full_name": "Remarks and EOA Details",
            "description": "Notes on Vehicle Off Road (VOR) demands or Equipment On Account (EOA) status",
            "data_type": "text",
            "required": False
        }
    },
    "key_metrics": [
        "Serviceability % = (FMC / Held) × 100",
        "Readiness Ratio = FMC / Auth"
    ],
    "validation_rules": [
        "Held ≤ Auth",
        "FMC ≤ Held",
        "Total = MUA + OH + R4"
    ]
}


# Armament
ARMT_METADATA: SheetMetadata = {
    "name": "Armament",
    "description": "Artillery, mortars, and heavy weapon systems",
    "columns": {
        "Ser No": {
            "full_name": "Serial Number",
            "description": "Sequential order of entries",
            "data_type": "integer",
            "required": True
        },
        "Make & Eqpt": {
            "full_name": "Nomenclature",
            "description": "Specific model and name (e.g., 155mm Gun, 81mm Mortar)",
            "data_type": "text",
            "required": True
        },
        "Auth": {
            "full_name": "Authorized",
            "description": "Official number permitted",
            "data_type": "integer",
            "required": True
        },
        "Held": {
            "full_name": "Held",
            "description": "Actual number in inventory",
            "data_type": "integer",
            "required": True
        },
        "Eng/Brl": {
            "full_name": "Engineering / Barrel",
            "description": "Failures due to barrel wear-out or structural faults",
            "data_type": "integer",
            "required": False
        },
        "Spares": {
            "full_name": "Lack of Spares",
            "description": "Equipment grounded due to unavailable parts",
            "data_type": "integer",
            "required": False
        },
        "OH/MR/FR/R4": {
            "full_name": "Repair Pipeline",
            "description": "Status in Overhaul, Medium Repair, Field Repair, or Level 4",
            "data_type": "integer",
            "required": False
        },
        "OBE": {
            "full_name": "Out of Bounds",
            "description": "Beyond Economic Repair, to be scrapped",
            "data_type": "integer",
            "required": False
        },
        "PMC (Nos)": {
            "full_name": "Partially Mission Capable",
            "description": "Functional but with minor defects",
            "data_type": "integer",
            "required": False
        },
        "NMC %": {
            "full_name": "Non-Mission Capable %",
            "description": "Percentage of unserviceable equipment",
            "data_type": "percentage",
            "required": False
        },
        "FMC %": {
            "full_name": "Fully Mission Capable %",
            "description": "Primary readiness metric",
            "data_type": "percentage",
            "required": True
        },
        "Avl %": {
            "full_name": "Availability %",
            "description": "Total available (FMC + PMC) percentage",
            "data_type": "percentage",
            "required": False
        },
        "Remarks": {
            "full_name": "Additional Notes",
            "description": "Detailed status or issues",
            "data_type": "text",
            "required": False
        }
    },
    "key_metrics": [
        "Combat Readiness = FMC %",
        "Total Availability = Avl %",
        "Repair Load = OH/MR/FR/R4 count"
    ],
    "validation_rules": [
        "Held ≤ Auth",
        "NMC % = (NMC / Held) × 100",
        "FMC % = (FMC / Held) × 100",
        "Avl % = ((FMC + PMC) / Held) × 100"
    ]
}


# Small Arms
SA_METADATA: SheetMetadata = {
    "name": "Small Arms",
    "description": "Individual and crew-served firearms including rifles, machine guns, pistols",
    "columns": {
        "Ser No": {
            "full_name": "Serial Number",
            "description": "Sequential order of entries",
            "data_type": "integer",
            "required": True
        },
        "Make & Eqpt": {
            "full_name": "Nomenclature",
            "description": "Specific weapon model (e.g., 5.56mm Rifle, 7.62mm MG)",
            "data_type": "text",
            "required": True
        },
        "Auth": {
            "full_name": "Authorized",
            "description": "Official number permitted",
            "data_type": "integer",
            "required": True
        },
        "Held": {
            "full_name": "Held",
            "description": "Actual number in inventory",
            "data_type": "integer",
            "required": True
        },
        "Eng/Brl": {
            "full_name": "Engineering / Barrel",
            "description": "Barrel wear or major structural failures",
            "data_type": "integer",
            "required": False
        },
        "Spares": {
            "full_name": "Lack of Spares",
            "description": "Grounded due to unavailable parts",
            "data_type": "integer",
            "required": False
        },
        "OH/MR/FR/R4": {
            "full_name": "Repair Pipeline",
            "description": "Status in repair facilities",
            "data_type": "integer",
            "required": False
        },
        "OBE": {
            "full_name": "Out of Bounds",
            "description": "Beyond Economic Repair",
            "data_type": "integer",
            "required": False
        },
        "PMC (Nos)": {
            "full_name": "Partially Mission Capable",
            "description": "Minor defects but functional",
            "data_type": "integer",
            "required": False
        },
        "NMC %": {
            "full_name": "Non-Mission Capable %",
            "description": "Percentage unserviceable",
            "data_type": "percentage",
            "required": False
        },
        "FMC %": {
            "full_name": "Fully Mission Capable %",
            "description": "Percentage ready for combat",
            "data_type": "percentage",
            "required": True
        },
        "Avl %": {
            "full_name": "Availability %",
            "description": "Total available (FMC + PMC)",
            "data_type": "percentage",
            "required": False
        },
        "Remarks": {
            "full_name": "Additional Notes",
            "description": "Status details",
            "data_type": "text",
            "required": False
        }
    },
    "key_metrics": [
        "Combat Readiness = FMC %",
        "Spare Parts Impact = Spares count",
        "Barrel Life Management = Eng/Brl count"
    ],
    "validation_rules": [
        "Held ≤ Auth",
        "NMC % = (NMC / Held) × 100",
        "FMC % = (FMC / Held) × 100"
    ]
}


# Instruments
INST_METADATA: SheetMetadata = {
    "name": "Instruments",
    "description": "Sensitive optical and electronic equipment including night vision, rangefinders, surveying tools",
    "columns": {
        "Ser No": {
            "full_name": "Serial Number",
            "description": "Sequential order of entries",
            "data_type": "integer",
            "required": True
        },
        "Nomenclature": {
            "full_name": "Equipment Name",
            "description": "Specific instrument model",
            "data_type": "text",
            "required": True
        },
        "Auth": {
            "full_name": "Authorized",
            "description": "Official number permitted",
            "data_type": "integer",
            "required": True
        },
        "Held": {
            "full_name": "Held",
            "description": "Actual number in inventory",
            "data_type": "integer",
            "required": True
        },
        "NMC due to: Spares": {
            "full_name": "Non-Mission Capable (Spares)",
            "description": "Waiting for optical/electronic components",
            "data_type": "integer",
            "required": False
        },
        "Under OH /R4/FR": {
            "full_name": "Specialized Repair",
            "description": "Undergoing technical calibration or repair",
            "data_type": "integer",
            "required": False
        },
        "Present loc of eqpt": {
            "full_name": "Physical Location",
            "description": "Workshop or sub-unit with custody",
            "data_type": "text",
            "required": False
        },
        "FMC": {
            "full_name": "Fully Mission Capable",
            "description": "Ready for immediate use",
            "data_type": "integer",
            "required": True
        },
        "PMC": {
            "full_name": "Partially Mission Capable",
            "description": "Minor issues but usable",
            "data_type": "integer",
            "required": False
        },
        "NMC %": {
            "full_name": "Non-Mission Capable %",
            "description": "Percentage unserviceable",
            "data_type": "percentage",
            "required": False
        },
        "FMC %": {
            "full_name": "Fully Mission Capable %",
            "description": "Percentage fully operational",
            "data_type": "percentage",
            "required": False
        },
        "Remarks": {
            "full_name": "Additional Notes",
            "description": "Technical status details",
            "data_type": "text",
            "required": False
        }
    },
    "key_metrics": [
        "Operational Readiness = FMC %",
        "Workshop Load = Under OH/R4/FR count",
        "Supply Chain Issue = NMC due to Spares"
    ],
    "validation_rules": [
        "Held ≤ Auth",
        "FMC ≤ Held"
    ]
}


# CBRN Equipment
CBRN_METADATA: SheetMetadata = {
    "name": "CBRN Equipment",
    "description": "Chemical, Biological, Radiological, and Nuclear defense equipment",
    "columns": {
        "Ser No": {
            "full_name": "Serial Number",
            "description": "Sequential order of entries",
            "data_type": "integer",
            "required": True
        },
        "Nomenclature": {
            "full_name": "Equipment Name",
            "description": "Specific CBRN equipment model",
            "data_type": "text",
            "required": True
        },
        "Auth": {
            "full_name": "Authorized",
            "description": "Official number permitted",
            "data_type": "integer",
            "required": True
        },
        "Held": {
            "full_name": "Held",
            "description": "Actual number in inventory",
            "data_type": "integer",
            "required": True
        },
        "DRWO": {
            "full_name": "Workshop Order",
            "description": "Equipment with active Divisional Repair Workshop Order",
            "data_type": "integer",
            "required": False
        },
        "DR Raised": {
            "full_name": "Demand Raised",
            "description": "Formal replacement/repair request initiated",
            "data_type": "integer",
            "required": False
        },
        "'S'": {
            "full_name": "Serviceable",
            "description": "Total quantity fit for operational use",
            "data_type": "integer",
            "required": True
        },
        "UNSV": {
            "full_name": "Unserviceable",
            "description": "Total count of broken or non-functional items",
            "data_type": "integer",
            "required": False
        },
        "Remarks": {
            "full_name": "Additional Notes",
            "description": "Status and issues",
            "data_type": "text",
            "required": False
        }
    },
    "key_metrics": [
        "Serviceability = (S / Held) × 100",
        "Repair Demand = DRWO + DR Raised",
        "Critical Readiness = S / Auth"
    ],
    "validation_rules": [
        "Held ≤ Auth",
        "S + UNSV ≤ Held"
    ]
}


# Master metadata dictionary
SHEET_METADATA: Dict[str, SheetMetadata] = {
    "APPX_A_BVEH": BVEH_METADATA,
    "APPX_A_CVEH": CVEH_METADATA,
    "ARMT": ARMT_METADATA,
    "SA": SA_METADATA,
    "INST": INST_METADATA,
    "CBRN": CBRN_METADATA
}


# Common abbreviations
ABBREVIATIONS = {
    "FMN": "Formation",
    "EME": "Electronics and Mechanical Engineers",
    "EOA": "Equipment On Account",
    "VOR": "Vehicle Off Road",
    "UE": "Unit Establishment",
    "UH": "Unit Holding",
    "MUA": "Minor Under Activity",
    "OH": "Overhaul",
    "R4": "Repair Level 4",
    "NMC": "Non-Mission Capable",
    "FMC": "Fully Mission Capable",
    "PMC": "Partially Mission Capable",
    "OBE": "Out of Bounds",
    "DRWO": "Divisional Repair Workshop Order",
    "DR": "Demand Raised"
}


# Alert thresholds
READINESS_THRESHOLDS = {
    "RED": 50,      # FMC% < 50%
    "AMBER": 70,    # 50% ≤ FMC% < 70%
    "GREEN": 100    # FMC% ≥ 70%
}


def get_column_names(sheet_type: str) -> List[str]:
    """
    Get list of column names for a given sheet type.
    
    Args:
        sheet_type: Sheet type identifier (e.g., 'APPX_A_BVEH')
    
    Returns:
        List of column names in order
    """
    if sheet_type not in SHEET_METADATA:
        return []
    
    return list(SHEET_METADATA[sheet_type]["columns"].keys())


def get_required_columns(sheet_type: str) -> List[str]:
    """
    Get list of required column names for a given sheet type.
    
    Args:
        sheet_type: Sheet type identifier
    
    Returns:
        List of required column names
    """
    if sheet_type not in SHEET_METADATA:
        return []
    
    metadata = SHEET_METADATA[sheet_type]
    return [
        col_name 
        for col_name, col_def in metadata["columns"].items() 
        if col_def["required"]
    ]


def get_column_description(sheet_type: str, column_name: str) -> str:
    """
    Get description for a specific column.
    
    Args:
        sheet_type: Sheet type identifier
        column_name: Column name
    
    Returns:
        Column description or empty string if not found
    """
    if sheet_type not in SHEET_METADATA:
        return ""
    
    columns = SHEET_METADATA[sheet_type]["columns"]
    if column_name not in columns:
        return ""
    
    return columns[column_name]["description"]


def validate_column_presence(sheet_type: str, actual_columns: List[str]) -> tuple[bool, List[str]]:
    """
    Validate that required columns are present.
    
    Args:
        sheet_type: Sheet type identifier
        actual_columns: List of actual column names in data
    
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    required = set(get_required_columns(sheet_type))
    actual = set(actual_columns)
    missing = required - actual
    
    return len(missing) == 0, list(missing)
