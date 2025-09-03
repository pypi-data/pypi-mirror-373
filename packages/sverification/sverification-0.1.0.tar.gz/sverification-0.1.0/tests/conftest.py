"""
Test configuration for pytest
"""
import pytest
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def sample_pdf_path():
    """Fixture for sample PDF path"""
    # This would be a path to a test PDF file
    return os.path.join(project_root, "tests", "fixtures", "sample.pdf")

@pytest.fixture
def sample_brands_json():
    """Fixture for sample brands JSON"""
    return os.path.join(project_root, "sverification", "statements_metadata.json")

@pytest.fixture
def sample_metadata():
    """Fixture for sample metadata dictionary"""
    return {
        "pdf_version": "1.4",
        "author": "",
        "subject": "",
        "keywords": "",
        "creator": "Test Creator",
        "producer": "Test Producer",
        "creationdate": "D:20240101120000Z",
        "moddate": "D:20240101120000Z",
        "trapped": "",
        "eof_markers": 1,
        "pdf_versions": 1,
    }
