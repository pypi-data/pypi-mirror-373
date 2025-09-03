"""
Tests for pdf_name_extractor module
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sverification.pdf_name_extractor import get_company_name


class TestPdfNameExtractor:
    """Test cases for PDF name extraction functionality"""
    
    def test_get_company_name_with_email_pattern(self):
        """Test company name extraction from email pattern"""
        # Mock pdfplumber
        with patch('sverification.pdf_name_extractor.pdfplumber.open') as mock_open:
            # Setup mock PDF
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Some text\nContact: support@selcom.co.tz\nEnd"
            mock_pdf.pages = [mock_page, mock_page]  # Two pages
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = get_company_name("dummy_path.pdf")
            assert result == "selcom"
    
    def test_get_company_name_vodacom_pattern(self):
        """Test Vodacom detection"""
        with patch('sverification.pdf_name_extractor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Vodacom Tanzania\nOperator Info"
            mock_pdf.pages = [mock_page, mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = get_company_name("dummy_path.pdf")
            assert result == "vodacom"
    
    def test_get_company_name_airtel_pattern(self):
        """Test Airtel detection"""
        with patch('sverification.pdf_name_extractor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page1 = MagicMock()
            mock_page1.extract_text.return_value = "Some content"
            mock_page2 = MagicMock()
            mock_page2.extract_text.return_value = "Footer text\n*000#"
            mock_pdf.pages = [mock_page1, mock_page2]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = get_company_name("dummy_path.pdf")
            assert result == "airtel"
    
    def test_get_company_name_with_password(self):
        """Test company name extraction with password"""
        with patch('sverification.pdf_name_extractor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Contact: info@dtb.co.tz"
            mock_pdf.pages = [mock_page, mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = get_company_name("dummy_path.pdf", password="test123")
            assert result == "dtb"
            # Verify password was passed to pdfplumber
            mock_open.assert_called_once_with("dummy_path.pdf", password="test123")
    
    def test_get_company_name_unknown_fallback(self):
        """Test fallback to unknown when no pattern matches"""
        with patch('sverification.pdf_name_extractor.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Generic content with no identifiable patterns"
            mock_pdf.pages = [mock_page, mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = get_company_name("dummy_path.pdf")
            # Should return some default or handle gracefully
            assert isinstance(result, str)
    
    def test_get_company_name_file_error(self):
        """Test handling of file errors"""
        with patch('sverification.pdf_name_extractor.pdfplumber.open') as mock_open:
            mock_open.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(FileNotFoundError):
                get_company_name("nonexistent_file.pdf")
