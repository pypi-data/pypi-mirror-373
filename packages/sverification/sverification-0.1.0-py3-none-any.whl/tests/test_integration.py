"""
Integration tests for the complete verification workflow
"""
import pytest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import sverification


class TestIntegration:
    """Integration tests for the complete verification workflow"""
    
    def test_package_imports(self):
        """Test that package imports work correctly"""
        assert hasattr(sverification, '__version__')
        assert hasattr(sverification, 'extract_all')
        assert hasattr(sverification, 'compare_fields')
        assert hasattr(sverification, 'load_brands')
        assert hasattr(sverification, 'get_company_name')
    
    def test_package_version(self):
        """Test package version is set"""
        assert sverification.__version__ == "0.1.0"
    
    @patch('sverification.pdf_name_extractor.pdfplumber.open')
    @patch('sverification.compare_metadata.extract_pdf_metadata')
    @patch('sverification.compare_metadata.recover_pdf_versions')
    @patch('sverification.compare_metadata.count_pdf_eof_markers')
    @patch('sverification.compare_metadata.check_no_of_versions')
    def test_complete_verification_workflow(self, mock_versions, mock_eof, 
                                          mock_recover, mock_metadata, mock_pdfplumber):
        """Test the complete verification workflow"""
        # Setup mocks for PDF processing
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Contact: support@selcom.co.tz"
        mock_pdf.pages = [mock_page, mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        # Setup mocks for metadata extraction
        mock_metadata.return_value = {
            "PDF Version": "1.4",
            "Creator": "Test Creator",
            "Producer": "iText",
            "CreationDate": "D:20240101120000Z",
            "ModDate": "D:20240101120000Z"
        }
        mock_recover.return_value = []
        mock_eof.return_value = 1
        mock_versions.return_value = 1
        
        # Create temporary brands file
        brands_data = {
            "selcom": [{
                "brand": "selcom",
                "pdf_version": "1.4",
                "creator": "Test Creator",
                "producer": "iText",
                "eof_markers": 1,
                "pdf_versions": 1
            }]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(brands_data, f)
            brands_file = f.name
        
        try:
            # Run the workflow
            pdf_path = "dummy.pdf"
            
            # 1. Extract metadata
            metadata = sverification.extract_all(pdf_path)
            assert isinstance(metadata, dict)
            assert "pdf_version" in metadata
            
            # 2. Detect company
            company = sverification.get_company_name(pdf_path)
            assert company == "selcom"
            
            # 3. Load brands and compare
            brands = sverification.load_brands(brands_file)
            expected = brands.get(company, [{}])[0]
            results, score = sverification.compare_fields(metadata, expected)
            
            # Verify results
            assert isinstance(results, list)
            assert isinstance(score, float)
            assert 0 <= score <= 100
            
        finally:
            # Cleanup
            os.unlink(brands_file)
    
    def test_error_handling_missing_pdf(self):
        """Test error handling for missing PDF file"""
        result = sverification.extract_all("nonexistent_file.pdf")
        # Should return a dict with error indicators when file is missing
        assert isinstance(result, dict)
        assert result['eof_markers'] == -1  # Error indicator from pdforensic
    
    def test_error_handling_invalid_brands_file(self):
        """Test error handling for invalid brands file"""
        with pytest.raises(FileNotFoundError):
            sverification.load_brands("nonexistent_brands.json")
    
    @patch('sverification.pdf_name_extractor.pdfplumber.open')
    def test_company_detection_fallback(self, mock_pdfplumber):
        """Test company detection with unknown content"""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Unknown content with no patterns"
        mock_pdf.pages = [mock_page, mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        result = sverification.get_company_name("dummy.pdf")
        assert isinstance(result, str)  # Should return some string value
    
    def test_metadata_structure(self):
        """Test that extracted metadata has expected structure"""
        with patch('sverification.compare_metadata.extract_pdf_metadata') as mock_meta, \
             patch('sverification.compare_metadata.recover_pdf_versions') as mock_recover, \
             patch('sverification.compare_metadata.count_pdf_eof_markers') as mock_eof, \
             patch('sverification.compare_metadata.check_no_of_versions') as mock_versions:
            
            mock_meta.return_value = {"PDF Version": "1.4"}
            mock_recover.return_value = []
            mock_eof.return_value = 1
            mock_versions.return_value = 1
            
            result = sverification.extract_all("dummy.pdf")
            
            # Check required fields exist
            required_fields = [
                "pdf_version", "author", "subject", "keywords", 
                "creator", "producer", "creationdate", "moddate", 
                "trapped", "eof_markers", "pdf_versions"
            ]
            
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
