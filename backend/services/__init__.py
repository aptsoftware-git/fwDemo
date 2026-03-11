"""
Services package for FRS Data Management System.
Contains business logic for upload processing and LLM integration.
"""
from .upload_service import process_directory, detect_month_from_path
from .llm_service import get_llm_client, compare_datasets

__all__ = [
    'process_directory',
    'detect_month_from_path',
    'get_llm_client',
    'compare_datasets'
]
