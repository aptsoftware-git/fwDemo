# FRS Equipment Readiness Metadata Dictionary

This document defines the standardized reporting columns and metadata for military equipment readiness tracking across all equipment categories.

---

## Equipment Categories

The FRS system tracks five main equipment categories:
1. **APPX_A_BVEH** - B Vehicles (Transport)
2. **APPX_A_CVEH** - C Vehicles (Engineering Plant)
3. **ARMT** - Armament (Artillery, Mortars)
4. **SA** - Small Arms (Individual & Crew-served Weapons)
5. **INST** - Instruments (Optical & Electronic)
6. **CBRN** - CBRN Equipment (Chemical, Biological, Radiological, Nuclear Defense)

---

## 1. B Vehicles (APPX_A_BVEH)

**Description**: Soft-skinned transport vehicles including trucks, jeeps, and utility vehicles.

### Column Definitions

| Column Name | Full Name | Description | Data Type |
|------------|-----------|-------------|-----------|
| Ser No | Serial Number | Sequential order of entries in the report | Integer |
| Category | Make & Type | Manufacturer and specific model/capacity (e.g., 2.5 Ton Truck) | Text |
| Auth (UE) | Authorized (Unit Establishment) | Official number of units permitted by regulation | Integer |
| Held (UH) | Held (Unit Holding) | Actual number of units in inventory | Integer |
| MUA | Minor Under Activity | Units undergoing light, routine maintenance | Integer |
| OH | Overhaul | Units undergoing major reconditioning | Integer |
| R4 | Repair Level 4 | Units requiring specialized workshop repairs | Integer |
| Total NMC | Total Non-Mission Capable | Sum of all unserviceable units (MUA + OH + R4) | Integer |
| FMC | Fully Mission Capable | Units 100% fit for immediate deployment | Integer |
| Remarks | VOR / EOA Details | Notes on Vehicle Off Road (VOR) demands or Equipment On Account (EOA) status | Text |

### Key Metrics
- **Serviceability %** = (FMC / Held) × 100
- **Availability %** = ((Held - Total NMC) / Auth) × 100

---

## 2. C Vehicles (APPX_A_CVEH)

**Description**: Heavy engineering plant equipment including dozers, excavators, graders, and construction vehicles.

### Column Definitions

| Column Name | Full Name | Description | Data Type |
|------------|-----------|-------------|-----------|
| Ser No | Serial Number | Sequential order of entries in the report | Integer |
| Category | Make & Type | Manufacturer and specific model (e.g., D6 Dozer) | Text |
| Auth (UE) | Authorized (Unit Establishment) | Official number of units permitted by regulation | Integer |
| Held (UH) | Held (Unit Holding) | Actual number of units in inventory | Integer |
| MUA | Minor Under Activity | Units undergoing light, routine maintenance | Integer |
| OH | Overhaul | Units undergoing major reconditioning | Integer |
| R4 | Repair Level 4 | Units requiring specialized workshop repairs | Integer |
| Total NMC | Total Non-Mission Capable | Sum of all unserviceable units (MUA + OH + R4) | Integer |
| FMC | Fully Mission Capable | Units 100% fit for immediate deployment | Integer |
| Remarks | VOR / EOA Details | Notes on Vehicle Off Road (VOR) demands or Equipment On Account (EOA) status | Text |

### Key Metrics
- **Serviceability %** = (FMC / Held) × 100
- **Readiness Ratio** = FMC / Auth

---

## 3. Armament (ARMT)

**Description**: Artillery, mortars, and heavy weapon systems.

### Column Definitions

| Column Name | Full Name | Description | Data Type |
|------------|-----------|-------------|-----------|
| Ser No | Serial Number | Sequential order of entries | Integer |
| Make & Eqpt | Nomenclature | Specific model and name (e.g., 155mm Gun, 81mm Mortar) | Text |
| Auth | Authorized | Official number permitted | Integer |
| Held | Held | Actual number in inventory | Integer |
| Eng/Brl | Engineering / Barrel | Failures due to barrel wear-out or structural faults | Integer |
| Spares | Lack of Spares | Equipment grounded due to unavailable parts | Integer |
| OH/MR/FR/R4 | Repair Pipeline | Status in Overhaul, Medium Repair, Field Repair, or Level 4 | Integer |
| OBE | Out of Bounds | Beyond Economic Repair, to be scrapped | Integer |
| PMC (Nos) | Partially Mission Capable | Functional but with minor defects | Integer |
| NMC % | Non-Mission Capable % | Percentage of unserviceable equipment | Percentage |
| FMC % | Fully Mission Capable % | Primary readiness metric | Percentage |
| Avl % | Availability % | Total available (FMC + PMC) percentage | Percentage |
| Remarks | Additional Notes | Detailed status or issues | Text |

### Key Metrics
- **Combat Readiness** = FMC %
- **Total Availability** = Avl %
- **Repair Load** = OH/MR/FR/R4 count

---

## 4. Small Arms (SA)

**Description**: Individual and crew-served firearms including rifles, machine guns, pistols.

### Column Definitions

| Column Name | Full Name | Description | Data Type |
|------------|-----------|-------------|-----------|
| Ser No | Serial Number | Sequential order of entries | Integer |
| Make & Eqpt | Nomenclature | Specific weapon model (e.g., 5.56mm Rifle, 7.62mm MG) | Text |
| Auth | Authorized | Official number permitted | Integer |
| Held | Held | Actual number in inventory | Integer |
| Eng/Brl | Engineering / Barrel | Barrel wear or major structural failures | Integer |
| Spares | Lack of Spares | Grounded due to unavailable parts | Integer |
| OH/MR/FR/R4 | Repair Pipeline | Status in repair facilities | Integer |
| OBE | Out of Bounds | Beyond Economic Repair | Integer |
| PMC (Nos) | Partially Mission Capable | Minor defects but functional | Integer |
| NMC % | Non-Mission Capable % | Percentage unserviceable | Percentage |
| FMC % | Fully Mission Capable % | Percentage ready for combat | Percentage |
| Avl % | Availability % | Total available (FMC + PMC) | Percentage |
| Remarks | Additional Notes | Status details | Text |

### Key Metrics
- **Combat Readiness** = FMC %
- **Spare Parts Impact** = Spares count
- **Barrel Life Management** = Eng/Brl count

---

## 5. Instruments (INST)

**Description**: Sensitive optical and electronic equipment including night vision devices, rangefinders, surveying tools, and communication equipment.

### Column Definitions

| Column Name | Full Name | Description | Data Type |
|------------|-----------|-------------|-----------|
| Ser No | Serial Number | Sequential order of entries | Integer |
| Nomenclature | Equipment Name | Specific instrument model | Text |
| Auth | Authorized | Official number permitted | Integer |
| Held | Held | Actual number in inventory | Integer |
| NMC due to: Spares | Non-Mission Capable (Spares) | Waiting for optical/electronic components | Integer |
| Under OH /R4/FR | Specialized Repair | Undergoing technical calibration or repair | Integer |
| Present loc of eqpt | Physical Location | Workshop or sub-unit with custody | Text |
| FMC | Fully Mission Capable | Ready for immediate use | Integer |
| PMC | Partially Mission Capable | Minor issues but usable | Integer |
| NMC % | Non-Mission Capable % | Percentage unserviceable | Percentage |
| FMC % | Fully Mission Capable % | Percentage fully operational | Percentage |
| Remarks | Additional Notes | Technical status details | Text |

### Key Metrics
- **Operational Readiness** = FMC %
- **Workshop Load** = Under OH/R4/FR count
- **Supply Chain Issue** = NMC due to Spares

---

## 6. CBRN Equipment (CBRN)

**Description**: Chemical, Biological, Radiological, and Nuclear defense equipment including protective suits, masks, detection devices.

### Column Definitions

| Column Name | Full Name | Description | Data Type |
|------------|-----------|-------------|-----------|
| Ser No | Serial Number | Sequential order of entries | Integer |
| Nomenclature | Equipment Name | Specific CBRN equipment model | Text |
| Auth | Authorized | Official number permitted | Integer |
| Held | Held | Actual number in inventory | Integer |
| DRWO | Workshop Order | Equipment with active Divisional Repair Workshop Order | Integer |
| DR Raised | Demand Raised | Formal replacement/repair request initiated | Integer |
| 'S' | Serviceable | Total quantity fit for operational use | Integer |
| UNSV | Unserviceable | Total count of broken or non-functional items | Integer |
| Remarks | Additional Notes | Status and issues | Text |

### Key Metrics
- **Serviceability** = (S / Held) × 100
- **Repair Demand** = DRWO + DR Raised
- **Critical Readiness** = S / Auth

---

## Common Abbreviations

| Abbreviation | Full Form | Context |
|-------------|-----------|---------|
| FMN | Formation | Unit designation |
| EME | Electronics and Mechanical Engineers | Maintenance corps |
| EOA | Equipment On Account | Official inventory |
| VOR | Vehicle Off Road | Unserviceable vehicle |
| UE | Unit Establishment | Authorized strength |
| UH | Unit Holding | Actual inventory |
| MUA | Minor Under Activity | Light maintenance |
| OH | Overhaul | Major reconditioning |
| R4 | Repair Level 4 | Workshop repair |
| NMC | Non-Mission Capable | Unserviceable |
| FMC | Fully Mission Capable | Combat ready |
| PMC | Partially Mission Capable | Limited capability |
| OBE | Out of Bounds | Beyond repair |
| DRWO | Divisional Repair Workshop Order | Repair authorization |
| DR | Demand Raised | Supply request |

---

## Data Quality Rules

### Required Fields
- All equipment categories must have: Auth, Held, FMC values
- Ser No must be sequential and unique within each unit/sheet
- Category/Make & Eqpt must be non-empty

### Validation Rules
- `Held ≤ Auth` (cannot hold more than authorized)
- `FMC ≤ Held` (cannot have more ready than held)
- `Total NMC = MUA + OH + R4` (for vehicles)
- `NMC % = (NMC / Held) × 100`
- `FMC % = (FMC / Held) × 100`
- `Avl % = ((FMC + PMC) / Held) × 100`

### Critical Thresholds
- **Red Alert**: FMC% < 50%
- **Amber Alert**: 50% ≤ FMC% < 70%
- **Green Status**: FMC% ≥ 70%

---

## Usage Notes

### For Data Processing
- This metadata defines the expected column structure for each sheet type
- Use these definitions for data validation and cleaning
- Missing columns should be flagged as warnings
- Extra columns can be preserved but marked as non-standard

### For LLM Analysis
- When comparing datasets, use these definitions to understand column meanings
- Calculate derived metrics (percentages, totals) based on these formulas
- Interpret Remarks fields for qualitative insights
- Consider military context and operational impact in analysis

### For Report Generation
- Group equipment by category first
- Highlight critical items (FMC % < 50%)
- Track month-over-month trends in key metrics
- Summarize repair pipeline (OH, R4) and spare parts issues

---

*Document Version: 1.0*  
*Last Updated: March 4, 2026*  
*Purpose: System prompt and data dictionary for FRS Data Management System*
