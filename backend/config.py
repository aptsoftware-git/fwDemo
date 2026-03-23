"""
Configuration management for FRS Data Management System.
Loads environment variables and provides configuration settings.
"""
import os
from pathlib import Path
from decouple import config

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# LLM Configuration
LLM_MODE = config('LLM_MODE', default='local', cast=str)  # Only 'local' supported

# Local LLM (Ollama) Configuration
OLLAMA_URL = config('OLLAMA_URL', default='http://localhost:11434/api/chat', cast=str)
LLM_MODEL = config('LLM_MODEL', default='qwen2.5:3b', cast=str)
LLM_TIMEOUT = config('LLM_TIMEOUT', default=35, cast=int)
LLM_MAX_WORKERS = config('LLM_MAX_WORKERS', default=4, cast=int)
LLM_MAX_ROWS = config('LLM_MAX_ROWS', default=200, cast=int)

# Legacy support (for backward compatibility)
LOCAL_MODEL_URL = OLLAMA_URL  # Deprecated: use OLLAMA_URL
LOCAL_MODEL_NAME = LLM_MODEL   # Deprecated: use LLM_MODEL

# Database Configuration
DATABASE_URL = config('DATABASE_URL', default='postgresql://postgres:password@localhost:5432/frs_db', cast=str)

# API Configuration
BACKEND_HOST = config('BACKEND_HOST', default='0.0.0.0', cast=str)
BACKEND_PORT = config('BACKEND_PORT', default=8000, cast=int)
CORS_ORIGINS = config('CORS_ORIGINS', default='http://localhost:3000,http://localhost:5173', cast=lambda v: [s.strip() for s in v.split(',')])

# Data Directory
DATA_DIR = config('DATA_DIR', default='../data', cast=str)
DATA_DIR_PATH = Path(DATA_DIR) if not Path(DATA_DIR).is_absolute() else Path(DATA_DIR)

# Logging Configuration
LOG_LEVEL = config('LOG_LEVEL', default='INFO', cast=str)

# Sheet Type Mapping (Standard sheet names)
SHEET_TYPES = {
    'APPX_A_AVEH': 'A Veh',  # Tracked/armored vehicles
    'APPX_A_BVEH': 'B Veh',  # Transport vehicles
    'APPX_A_CVEH': 'C Veh',  # Engineering plant
    'ARMT': 'ARMT',
    'SA': 'SA',
    'INST': 'INST',
    'CBRN': 'CBRN'
}

# Sheet Type Order (standard display sequence)
# INST and CBRN temporarily disabled for investigation
SHEET_TYPE_ORDER = [
    'APPX_A_AVEH',
    'APPX_A_BVEH',
    'APPX_A_CVEH',
    'ARMT',
    'SA',
    # 'INST',  # TODO: Temporarily disabled - investigate later
    # 'CBRN'   # TODO: Temporarily disabled - investigate later
]

def get_config_summary():
    """Return a summary of current configuration (without sensitive data)."""
    return {
        'llm_mode': LLM_MODE,
        'ollama_url': OLLAMA_URL,
        'llm_model': LLM_MODEL,
        'llm_timeout': LLM_TIMEOUT,
        'llm_max_workers': LLM_MAX_WORKERS,
        'llm_max_rows': LLM_MAX_ROWS,
        'database_configured': bool(DATABASE_URL),
        'backend_host': BACKEND_HOST,
        'backend_port': BACKEND_PORT,
        'cors_origins': CORS_ORIGINS,
        'data_dir': str(DATA_DIR_PATH),
        'log_level': LOG_LEVEL
    }
