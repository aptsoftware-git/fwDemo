"""
Parsers package for FRS Data Management System.
Contains modules for parsing Dictionary.docx and Excel files.
"""
from .dictionary_parser import parse_dictionary, get_column_mapping
from .excel_parser import parse_excel_file

__all__ = [
    'parse_dictionary',
    'get_column_mapping',
    'parse_excel_file'
]
