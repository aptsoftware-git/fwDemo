# FRS Data Management System

A comprehensive web application for managing and comparing military Formation Readiness State (FRS) data across multiple units and time periods, featuring AI-powered comparison capabilities.

## Features

- **Data Upload**: Upload directories containing FRS Excel files from multiple formation units
- **Automatic Processing**: Auto-detect months, parse Excel files with fuzzy sheet name matching, clean and validate data
- **Data Visualization**: View clean data in 6 tabs (Appx A B veh, Appx A C veh, Armt, SA, INST, CBRN)
- **Unit Filtering**: View aggregated data across all units or filter by individual formation
- **AI-Powered Comparison**: Compare datasets between different months using LLM for detailed human-readable analysis
- **Flexible LLM Support**: Use local LLM (Ollama with qwen2.5:3b) or cloud LLM (Claude API)

## Architecture

- **Backend**: Python FastAPI with PostgreSQL database
- **Frontend**: React with Vite
- **LLM Integration**: Ollama (local) or Anthropic Claude (cloud)
- **Data Processing**: pandas, openpyxl, xlrd for Excel handling

## Prerequisites

### Required Software

1. **Python 3.9+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **Node.js 16+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version`

3. **PostgreSQL 13+**
   - Download from [postgresql.org](https://www.postgresql.org/download/)
   - Verify: `psql --version`

4. **Ollama** (for local LLM mode - optional)
   - Download from [ollama.ai](https://ollama.ai/)
   - Pull qwen2.5:3b model: `ollama pull qwen2.5:3b`
   - Verify: `ollama list`

### System Requirements

- **RAM**: 8GB minimum (16GB recommended for local LLM)
- **Disk Space**: 10GB free space
- **OS**: Windows, macOS, or Linux

## Installation

### 1. Clone/Download Repository

```bash
cd c:\Anu\APT\apt\army\fortwilliam\code\demo1
```

### 2. Setup PostgreSQL Database

#### Windows (if psql not in PATH):
```powershell
# Find your PostgreSQL version (usually in C:\Program Files\PostgreSQL)
Get-ChildItem "C:\Program Files\PostgreSQL" -Directory

# Use full path to create database (replace 16 with your version)
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE frs_db;"

# Optional: Add to PATH for easier access
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

#### Alternative (if psql is in PATH):
```bash
# Interactive mode
psql -U postgres
CREATE DATABASE frs_db;
\q

# Or single command
psql -U postgres -c "CREATE DATABASE frs_db;"
```

**Note**: You'll be prompted for the PostgreSQL password you set during installation.

### 3. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env file with your settings
# Set database credentials, LLM mode, etc.
```

**Important**: Edit [backend/.env](backend/.env) file:
- Set `DATABASE_URL` with your PostgreSQL credentials
- Set `LLM_MODE` to `local` or `claude`
- If using Claude, set `CLAUDE_API_KEY`

### 4. Setup Frontend

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install
```

## Running the Application

### 1. Start PostgreSQL

Ensure PostgreSQL service is running:

**Windows**:
```powershell
# Check status
Get-Service postgresql*

# Start if not running
Start-Service postgresql-x64-13  # Adjust version as needed
```

**Linux/Mac**:
```bash
sudo systemctl start postgresql
```

### 2. Start Ollama (Optional - for local LLM mode)

If using local LLM mode:

```bash
# Start Ollama server
ollama serve

# In another terminal, verify model is available
ollama list
# Should see qwen2.5:3b in the list
```

**Performance Note**: Local Ollama mode uses a simplified comparison that only analyzes row count statistics (not detailed row data) to ensure fast response times (~1 minute). For detailed line-by-line analysis with full row comparisons, use Claude mode instead.

### 3. Start Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Run backend server
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

API documentation: **http://localhost:8000/docs**

### 4. Start Frontend

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Run development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Usage Guide

### 1. Upload Data

1. Open the application in your browser: http://localhost:3000
2. In the "Upload FRS Data" section:
   - **Option A**: Click "Browse..." button to preview files, then copy the directory path from Windows File Explorer
   - **Option B**: Right-click the folder in File Explorer → "Copy as path" → Paste into the Directory Path field
   - **Option C**: Manually type the full path (e.g., `c:\Anu\APT\apt\army\fortwilliam\code\demo1\data\FRS_Sample\Nov`)
   - Optionally provide a custom tag (auto-generated if left empty)
   - Click "Upload"
3. Wait for processing to complete
4. Review any warnings or errors

**Tips for getting the directory path:**
- In Windows File Explorer, navigate to the folder, click the address bar, and copy the path
- Or hold Shift, right-click the folder, and select "Copy as path"
- The path should point to a month folder (e.g., `Nov` or `Dec`) that contains unit subdirectories

**Example paths**:
- Full Windows path: `C:\Anu\APT\apt\army\fortwilliam\code\demo1\data\FRS_Sample\Nov`
- Relative path: `data\FRS_Sample\Nov` or `data/FRS_Sample/Nov`
- Alternative format: `C:/Anu/APT/apt/army/fortwilliam/code/demo1/data/FRS_Sample/Nov`

### 2. View Data

1. Select a dataset from the "Select Dataset" dropdown
2. Choose unit filter:
   - "All Units (Aggregated)" - see combined data from all formations
   - Specific unit (e.g., "Fmn A") - see individual formation data
3. Navigate through 6 tabs to view different sheet types:
   - Appx A (B veh)
   - Appx A (C veh)
   - Armt
   - SA
   - INST
   - CBRN

### 3. Compare Datasets

1. Scroll to "Compare Datasets" section
2. Select two different datasets (e.g., "FRS November 2025" and "FRS December 2025")
3. Click "Compare"
4. Wait for LLM to generate analysis (may take 30-60 seconds)
5. Review the detailed line-by-line comparison

### 4. Switch LLM Modes

To switch between local and cloud LLM:

1. Stop the backend server
2. Edit [backend/.env](backend/.env)
3. Change `LLM_MODE=local` to `LLM_MODE=claude` (or vice versa)
4. If using Claude, ensure `CLAUDE_API_KEY` is set
5. Restart backend server

## Configuration

### Backend Configuration ([backend/.env](backend/.env))

```env
# LLM Mode
LLM_MODE=local  # or "claude"

# Local LLM (Ollama)
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=qwen2.5:3b

# Cloud LLM (Claude)
CLAUDE_API_KEY=sk-ant-api03-your-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/frs_db

# API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Project Structure

```
demo1/
├── backend/              # Python FastAPI backend
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration management
│   ├── database.py      # Database setup
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── parsers/         # Excel and dictionary parsers
│   ├── processors/      # Data cleaning logic
│   ├── services/        # Business logic (upload, LLM)
│   ├── routers/         # API endpoints
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment configuration
├── frontend/            # React frontend
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # React components
│   │   ├── App.jsx     # Main application
│   │   └── main.jsx    # Entry point
│   ├── package.json    # Node dependencies
│   └── vite.config.js  # Vite configuration
├── data/               # FRS data files
│   ├── FRS_Sample/     # Sample data for testing
│   └── FRS/           # Full production data
├── docs/               # Documentation
│   └── Dictionary.docx # Column definitions
└── plan/              # Planning documents
    ├── architecture.md # System architecture
    └── implementation-plan.md
```

## API Endpoints

- `POST /api/upload` - Upload directory of FRS data
- `GET /api/datasets` - List all datasets
- `GET /api/data/{tag}` - Get data for a dataset
- `GET /api/data/{tag}/units` - Get units in a dataset
- `POST /api/compare` - Compare two datasets
- `GET /api/health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

## Troubleshooting

### Backend Issues

**Database connection error**:
- Verify PostgreSQL is running
- Check credentials in `.env` file
- Ensure database `frs_db` exists

**Import errors**:
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

**Ollama connection error**:
- Verify Ollama is running: `ollama serve`
- Check model is available: `ollama list`
- Verify URL in `.env`: `LOCAL_MODEL_URL=http://localhost:11434`

### Frontend Issues

**Cannot connect to backend**:
- Verify backend is running on port 8000
- Check CORS configuration in [backend/.env](backend/.env)

**npm install fails**:
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

### Data Processing Issues

**Excel file not parsing**:
- Verify file is `.xls` or `.xlsx` format
- Check for temporary files (`~$*.xlsx`) and close Excel
- Review error messages in upload response

**Missing sheets**:
- System uses fuzzy matching - check sheet names in Excel file
- Refer to expected names in Dictionary.docx

## Development

### Running Tests

```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
# Initialize Alembic (if needed)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Security Notes

- This system does not include authentication (as per requirements)
- API keys in `.env` should not be committed to version control
- `.env` file is excluded via `.gitignore`
- Use environment variables for sensitive configuration

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Architecture**: See [plan/architecture.md](plan/architecture.md)
- **Implementation Plan**: See [plan/implementation-plan.md](plan/implementation-plan.md)

## License

Internal use only - Military FRS Data Management System

## Version

1.0.0 - Initial Release
