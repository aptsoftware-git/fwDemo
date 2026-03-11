# FRS Data Management System - Implementation Plan

## Project Timeline

**Estimated Duration**: 5-7 days for MVP (excluding testing and refinement)

## Phase 1: Backend Foundation (Day 1)

### Task 1.1: Project Structure Setup
- [x] Create backend directory
- [x] Create plan directory with architecture.md
- [ ] Initialize Python virtual environment
- [ ] Create requirements.txt with dependencies
- [ ] Create .gitignore for Python and Node.js

### Task 1.2: Configuration Setup
- [ ] Create backend/.env.example template
- [ ] Create backend/.env with actual configuration
- [ ] Create backend/config.py to load environment variables
- [ ] Test configuration loading

### Task 1.3: Database Setup
- [ ] Install PostgreSQL (if not already installed)
- [ ] Create database: frs_db
- [ ] Create backend/database.py with SQLAlchemy engine
- [ ] Test database connection

## Phase 2: Data Models and Parsers (Day 2)

### Task 2.1: Database Models
- [ ] Create backend/models.py with SQLAlchemy models:
  - Dataset model
  - Unit model
  - SheetData model
- [ ] Create backend/schemas.py with Pydantic schemas
- [ ] Run database migrations (SQLAlchemy create_all)

### Task 2.2: Dictionary Parser
- [ ] Create backend/parsers/ directory
- [ ] Create backend/parsers/__init__.py
- [ ] Create backend/parsers/dictionary_parser.py
- [ ] Implement parse_dictionary() function
- [ ] Test with docs/Dictionary.docx
- [ ] Cache dictionary mapping in memory

### Task 2.3: Excel Parser
- [ ] Create backend/parsers/excel_parser.py
- [ ] Implement fuzzy sheet name matching
- [ ] Implement sequence-based fallback
- [ ] Handle .xls and .xlsx formats
- [ ] Test with FRS_Sample data
- [ ] Error handling for malformed files

## Phase 3: Data Processing (Day 3)

### Task 3.1: Data Cleaner
- [ ] Create backend/processors/ directory
- [ ] Create backend/processors/__init__.py
- [ ] Create backend/processors/data_cleaner.py
- [ ] Implement clean_dataframe() function
  - Remove duplicates
  - Handle missing values
  - Standardize formats
  - Validate data types
- [ ] Implement aggregate_units() function
- [ ] Test with sample data

### Task 3.2: Upload Service
- [ ] Create backend/services/ directory
- [ ] Create backend/services/__init__.py
- [ ] Create backend/services/upload_service.py
- [ ] Implement auto-detect month from directory
- [ ] Implement process_directory() function
- [ ] Implement database storage logic
- [ ] Error handling and logging
- [ ] Test with FRS_Sample/Nov and FRS_Sample/Dec

## Phase 4: LLM Integration (Day 3-4)

### Task 4.1: LLM Service
- [ ] Create backend/services/llm_service.py
- [ ] Implement get_llm_client() for mode selection
- [ ] Implement Ollama client (local mode)
- [ ] Implement Anthropic client (Claude mode)
- [ ] Implement compare_datasets() function
- [ ] Implement prompt engineering for comparison
- [ ] Test with both LLM modes

### Task 4.2: Comparison Logic
- [ ] Implement generate_differences() function
- [ ] Format differences by sheet type
- [ ] Handle edge cases (missing sheets, no changes)
- [ ] Optimize prompt length for LLM context limits

## Phase 5: API Development (Day 4)

### Task 5.1: FastAPI Setup
- [ ] Create backend/main.py
- [ ] Initialize FastAPI app
- [ ] Configure CORS middleware
- [ ] Add health check endpoint
- [ ] Test basic server startup

### Task 5.2: API Routers
- [ ] Create backend/routers/ directory
- [ ] Create backend/routers/__init__.py
- [ ] Create backend/routers/data_router.py
- [ ] Implement POST /api/upload endpoint
- [ ] Implement GET /api/datasets endpoint
- [ ] Implement GET /api/data/{tag} endpoint
- [ ] Implement GET /api/data/{tag}/units endpoint
- [ ] Implement POST /api/compare endpoint
- [ ] Add request validation and error handling

### Task 5.3: API Testing
- [ ] Test all endpoints with Postman or curl
- [ ] Verify error responses
- [ ] Test edge cases
- [ ] Document API responses in docs/API.md

## Phase 6: Frontend Setup (Day 5)

### Task 6.1: React Project Setup
- [ ] Create frontend directory
- [ ] Initialize React project (Vite or CRA)
- [ ] Install dependencies (axios, react-router-dom)
- [ ] Configure proxy to backend (if needed)
- [ ] Create basic project structure
- [ ] Test basic app startup

### Task 6.2: Component Structure
- [ ] Create frontend/src/components/ directory
- [ ] Create placeholder components:
  - UploadPanel.jsx
  - DatasetSelector.jsx
  - UnitFilter.jsx
  - DataTabs.jsx
  - DataTable.jsx
  - ComparisonPanel.jsx
- [ ] Create frontend/src/App.jsx with layout

### Task 6.3: API Client
- [ ] Create frontend/src/api/ directory
- [ ] Create frontend/src/api/client.js with axios
- [ ] Implement API functions:
  - uploadDirectory()
  - getDatasets()
  - getData()
  - getUnits()
  - compareDatasets()

## Phase 7: Frontend Implementation (Day 5-6)

### Task 7.1: Upload Component
- [ ] Implement UploadPanel.jsx
- [ ] Directory path input
- [ ] Tag input (auto-generated or manual)
- [ ] Upload button and progress indicator
- [ ] Success/error messages

### Task 7.2: Data Viewer Components
- [ ] Implement DatasetSelector.jsx
  - Fetch and display all datasets
  - Selection callback
- [ ] Implement UnitFilter.jsx
  - "All" option
  - Individual unit options from API
- [ ] Implement DataTabs.jsx
  - 6 tabs for sheet types
  - Active tab state management
- [ ] Implement DataTable.jsx
  - Render data in table format
  - Handle empty data
  - Responsive design

### Task 7.3: Comparison Component
- [ ] Implement ComparisonPanel.jsx
- [ ] Two dataset selectors
- [ ] Compare button
- [ ] Loading state during LLM processing
- [ ] Display formatted comparison results
- [ ] Handle errors

### Task 7.4: State Management
- [ ] Implement React Context or hooks for global state
- [ ] Manage selected dataset
- [ ] Manage selected unit filter
- [ ] Manage active tab
- [ ] Manage comparison results

## Phase 8: Integration and Styling (Day 6-7)

### Task 8.1: Integration Testing
- [ ] Test end-to-end upload flow
- [ ] Test data viewing with All units
- [ ] Test data viewing with individual units
- [ ] Test switching between tabs
- [ ] Test comparison flow
- [ ] Test both LLM modes (local and Claude)

### Task 8.2: UI/UX Polish
- [ ] Add styling (CSS/Tailwind)
- [ ] Responsive design for mobile
- [ ] Loading indicators
- [ ] Error messages and validation
- [ ] Tooltips and help text

### Task 8.3: Error Handling
- [ ] Backend error logging
- [ ] Frontend error boundaries
- [ ] User-friendly error messages
- [ ] Graceful degradation

## Phase 9: Documentation and Deployment Prep (Day 7)

### Task 9.1: Documentation
- [ ] Create README.md at root
  - Project overview
  - Prerequisites
  - Installation instructions
  - Running backend
  - Running frontend
  - Environment configuration
- [ ] Create docs/API.md with endpoint documentation
- [ ] Create backend/README.md with backend specifics
- [ ] Create frontend/README.md with frontend specifics

### Task 9.2: Configuration Files
- [ ] Create .gitignore for root
- [ ] Create backend/.env.example
- [ ] Add comments to configuration files
- [ ] Document LLM setup (Ollama installation)

### Task 9.3: Testing Documentation
- [ ] Document test scenarios
- [ ] Create test data guidelines
- [ ] Document expected behaviors
- [ ] Known issues and limitations

## Phase 10: Testing and Refinement (Day 7+)

### Task 10.1: Functional Testing
- [ ] Test with FRS_Sample data
- [ ] Test with full FRS data (10 formations)
- [ ] Test edge cases:
  - Missing sheets
  - Malformed Excel files
  - Empty data
  - Large datasets
- [ ] Performance testing

### Task 10.2: User Acceptance Testing
- [ ] Test UI usability
- [ ] Test comparison quality
- [ ] Gather feedback
- [ ] Refine based on feedback

### Task 10.3: Bug Fixes and Optimization
- [ ] Fix identified bugs
- [ ] Optimize slow queries
- [ ] Optimize LLM prompts
- [ ] Code refactoring

## Dependencies and Prerequisites

### System Requirements
- Python 3.9 or higher
- Node.js 16 or higher
- PostgreSQL 13 or higher
- Ollama (for local LLM mode)
- 8GB RAM minimum (16GB recommended for local LLM)
- 10GB disk space

### Python Packages (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-decouple==3.8
pandas==2.1.3
openpyxl==3.1.2
xlrd==2.0.1
python-docx==1.1.0
python-multipart==0.0.6
anthropic==0.7.7
requests==2.31.0
pydantic==2.5.0
```

### Node.js Packages (package.json)
```
react==18.2.0
react-dom==18.2.0
axios==1.6.2
react-router-dom==6.20.0
vite==5.0.0 (if using Vite)
```

## Risk Mitigation

### Technical Risks
1. **Excel parsing failures**: Implement robust error handling and logging
2. **LLM API rate limits**: Implement retry logic and caching
3. **Large dataset performance**: Use pagination and lazy loading
4. **Database schema evolution**: Use migration tools (Alembic)

### Operational Risks
1. **Data consistency**: Implement transactional database operations
2. **File format variations**: Extensive testing with real data
3. **LLM costs**: Monitor Claude API usage, prefer local mode for development

## Success Criteria

- [ ] Successfully upload FRS_Sample/Nov directory
- [ ] Successfully upload FRS_Sample/Dec directory
- [ ] View aggregated data across both formations
- [ ] Filter to individual formation data
- [ ] Navigate all 6 tabs with correct data
- [ ] Generate comparison between Nov and Dec
- [ ] LLM produces human-readable differences
- [ ] Switch between local and Claude LLM modes
- [ ] All API endpoints functional
- [ ] Frontend responsive and user-friendly

## Next Steps After MVP

1. Deploy to production environment
2. Implement data export features
3. Add data visualization (charts/graphs)
4. Implement caching for performance
5. Add unit tests and integration tests
6. Set up CI/CD pipeline
7. Add logging and monitoring
8. Implement backup and recovery procedures
