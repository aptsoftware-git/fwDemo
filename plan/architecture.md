# FRS Data Management System - Architecture

## System Overview

A full-stack web application for managing and comparing military Formation Readiness State (FRS) data across multiple units and time periods, with AI-powered comparison capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Upload      │  │  Data Viewer │  │  Comparison  │      │
│  │  Panel       │  │  (6 Tabs)    │  │  Panel       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  API Endpoints                        │   │
│  │  /api/upload  /api/datasets  /api/data  /api/compare │   │
│  └──────┬───────────────────────────────────────┬───────┘   │
│         │                                        │           │
│  ┌──────▼────────┐  ┌──────────────┐  ┌────────▼────────┐  │
│  │  Upload       │  │  Data        │  │  LLM           │  │
│  │  Service      │  │  Cleaner     │  │  Service       │  │
│  └───┬───────────┘  └──────────────┘  └────────────────┘  │
│      │                                                       │
│  ┌───▼──────────┐  ┌──────────────┐                        │
│  │  Dictionary  │  │  Excel       │                        │
│  │  Parser      │  │  Parser      │                        │
│  └──────────────┘  └──────────────┘                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   PostgreSQL Database                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐      │
│  │ Datasets │  │  Units   │  │   SheetData (JSONB)  │      │
│  └──────────┘  └──────────┘  └──────────────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      LLM Integration                         │
│  ┌──────────────────┐           ┌──────────────────┐        │
│  │  Ollama (Local)  │    OR     │  Claude (Cloud)  │        │
│  │  qwen2.5:3b      │           │  Anthropic API   │        │
│  └──────────────────┘           └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 13+
- **ORM**: SQLAlchemy
- **Excel Processing**: openpyxl (xlsx), xlrd (xls)
- **Document Processing**: python-docx
- **Data Processing**: pandas, numpy
- **LLM Integration**: 
  - Local: Ollama (qwen2.5:3b)
  - Cloud: Anthropic Claude API
- **Environment**: python-decouple

### Frontend
- **Framework**: React 18+
- **HTTP Client**: axios
- **UI Components**: Custom components
- **Styling**: CSS/CSS Modules or Tailwind CSS
- **Build Tool**: Vite or Create React App

### Database Schema

```sql
-- Datasets table: Stores uploaded FRS data collections
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(255) UNIQUE NOT NULL,
    upload_date TIMESTAMP DEFAULT NOW(),
    month_label VARCHAR(50),
    description TEXT
);

-- Units table: Individual formation units within a dataset
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    unit_name VARCHAR(100) NOT NULL,
    file_path TEXT,
    UNIQUE(dataset_id, unit_name)
);

-- SheetData table: Actual data from Excel sheets
CREATE TABLE sheet_data (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
    sheet_type VARCHAR(50) NOT NULL,
    row_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sheet_data_unit_sheet ON sheet_data(unit_id, sheet_type);
CREATE INDEX idx_sheet_data_jsonb ON sheet_data USING GIN (row_data);
```

## Component Details

### 1. Dictionary Parser
- **Purpose**: Parse Dictionary.docx to extract sheet definitions and column mappings
- **Input**: Dictionary.docx file
- **Output**: Structured mapping of 6 sheet types to column definitions
- **Implementation**: python-docx library

### 2. Excel Parser
- **Purpose**: Parse Excel files from formation units
- **Features**:
  - Supports both .xls and .xlsx formats
  - Fuzzy sheet name matching with sequence fallback
  - Maps actual sheet names to standard types
- **Sheet Types**:
  1. Appx A (B veh)
  2. Appx A (C veh)
  3. Armt
  4. SA
  5. INST
  6. CBRN

### 3. Data Cleaner
- **Purpose**: Clean and validate parsed data
- **Operations**:
  - Remove duplicates
  - Handle null/missing values
  - Standardize formats (dates, numbers, text)
  - Validate data types and ranges
  - Aggregate data across multiple units

### 4. Upload Service
- **Purpose**: Process uploaded directories
- **Workflow**:
  1. Auto-detect month from directory name
  2. Find unit subdirectories and Excel files
  3. Parse Dictionary mapping
  4. Parse each Excel file
  5. Clean data
  6. Store in database with tag

### 5. LLM Service
- **Purpose**: Generate human-readable comparisons
- **Modes**:
  - **Local**: Ollama with qwen2.5:3b
  - **Cloud**: Anthropic Claude API
- **Process**:
  1. Retrieve two datasets from database
  2. Generate detailed line-by-line differences
  3. Format as structured prompt
  4. Send to LLM for narrative analysis
  5. Return human-readable comparison

## API Endpoints

### POST /api/upload
Upload and process a directory of FRS data
- **Request**: multipart/form-data with directory path and optional tag
- **Response**: Dataset metadata with processing status

### GET /api/datasets
List all saved datasets
- **Response**: Array of dataset metadata (tag, month, upload_date)

### GET /api/data/{tag}
Retrieve clean data for a specific dataset
- **Query Params**: 
  - `unit_filter`: "All" or specific unit name (e.g., "Fmn A")
  - `sheet_type`: Filter by specific sheet type
- **Response**: Aggregated or unit-specific data across 6 sheet types

### GET /api/data/{tag}/units
List all units in a dataset
- **Response**: Array of unit names

### POST /api/compare
Compare two datasets and generate LLM analysis
- **Request**: 
  ```json
  {
    "tag1": "Fmn November 2025",
    "tag2": "Fmn December 2025"
  }
  ```
- **Response**: LLM-generated comparison text

## Data Flow

### Upload Flow
```
User selects directory → Frontend sends to /api/upload
    ↓
Backend identifies month from directory name
    ↓
Backend finds all unit subdirectories
    ↓
For each unit:
    - Parse Excel file (fuzzy match sheets)
    - Apply Dictionary column mapping
    - Clean data (duplicates, nulls, validation)
    - Store in database
    ↓
Return success with dataset tag
```

### View Flow
```
User selects dataset + unit filter → Frontend calls /api/data/{tag}
    ↓
Backend queries database
    ↓
If unit_filter = "All":
    - Aggregate data across all units
Else:
    - Filter to specific unit
    ↓
Return clean data for 6 sheet types
    ↓
Frontend displays in 6 tabs
```

### Compare Flow
```
User selects two datasets → Frontend calls /api/compare
    ↓
Backend queries both datasets from database
    ↓
For each sheet type:
    - Generate line-by-line differences
    - Format changes (added, removed, modified)
    ↓
Construct LLM prompt with differences
    ↓
Send to LLM (Ollama or Claude)
    ↓
Return narrative comparison
    ↓
Frontend displays formatted comparison
```

## Configuration

### Environment Variables (.env)

```env
# LLM Configuration
LLM_MODE=local  # or "claude"

# Local LLM (Ollama)
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=qwen2.5:3b

# Cloud LLM (Claude)
CLAUDE_API_KEY=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
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/frs_db

# API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

## Security Considerations

- No authentication required (as specified)
- CORS configured for frontend origin
- Input validation on all API endpoints
- SQL injection prevention via SQLAlchemy ORM
- File upload validation (Excel formats only)
- Environment variables for sensitive data (API keys)

## Scalability Considerations

- PostgreSQL JSONB for flexible schema
- Indexed queries on dataset tags and sheet types
- Async FastAPI for concurrent requests
- LLM calls can be cached for repeated comparisons
- React frontend optimized with proper state management

## Future Enhancements

1. User authentication and role-based access
2. Export comparison reports to PDF/Word
3. Historical trend analysis across multiple months
4. Automated anomaly detection
5. Real-time collaboration features
6. Mobile-responsive UI
7. Bulk dataset operations
8. Advanced filtering and search
