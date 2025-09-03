"""
Statement Verification Package

A tool for verifying PDF statements by checking metadata and other attributes.
"""

__version__ = "0.1.0"

# Import main functions for easier access
from .compare_metadata import extract_all, compare_fields, load_brands, verify_statement_verbose, print_verification_report
from .pdf_name_extractor import get_company_name

__all__ = [
    "extract_all",
    "compare_fields", 
    "load_brands",
    "get_company_name",
    "verify_statement_verbose",
    "print_verification_report"
]