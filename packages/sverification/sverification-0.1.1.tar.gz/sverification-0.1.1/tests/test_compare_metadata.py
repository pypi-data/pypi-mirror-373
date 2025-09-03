"""
Tests for compare_metadata module
"""
import pytest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sverification.compare_metadata import (
    extract_all, compare_fields, load_brands, normalize_key, 
    normalize_val, coerce_int, pick_first_nonempty
)


class TestCompareMetadata:
    """Test cases for metadata comparison functionality"""
    
    def test_normalize_key(self):
        """Test key normalization"""
        assert normalize_key("PDF Version") == "pdf_version"
        assert normalize_key("Creation Date") == "creation_date"
        assert normalize_key("ModDate") == "moddate"
        assert normalize_key("  Spaced Key  ") == "spaced_key"
    
    def test_normalize_val(self):
        """Test value normalization"""
        assert normalize_val("  Test Value  ") == "test value"
        assert normalize_val("UPPERCASE") == "uppercase"
        assert normalize_val(123) == "123"
        assert normalize_val(None) == ""
    
    def test_coerce_int(self):
        """Test integer coercion"""
        assert coerce_int("123") == (True, 123)
        assert coerce_int(456) == (True, 456)
        assert coerce_int("not_a_number") == (False, 0)
        assert coerce_int("") == (False, 0)
    
    def test_pick_first_nonempty(self):
        """Test picking first non-empty value"""
        assert pick_first_nonempty("", "second", "third") == "second"
        assert pick_first_nonempty(None, "", "third") == "third"
        assert pick_first_nonempty("first", "second") == "first"
        assert pick_first_nonempty("", None, "") == ""
    
    def test_load_brands_valid_json(self, tmp_path):
        """Test loading valid brands JSON"""
        brands_data = {
            "selcom": [{"brand": "selcom", "pdf_version": "1.4"}],
            "vodacom": [{"brand": "vodacom", "pdf_version": "1.7"}]
        }
        
        brands_file = tmp_path / "test_brands.json"
        brands_file.write_text(json.dumps(brands_data))
        
        result = load_brands(str(brands_file))
        assert result == brands_data
    
    def test_load_brands_invalid_json(self, tmp_path):
        """Test loading invalid JSON"""
        brands_file = tmp_path / "invalid.json"
        brands_file.write_text("{ invalid json")
        
        with pytest.raises(json.JSONDecodeError):
            load_brands(str(brands_file))
    
    def test_load_brands_missing_file(self):
        """Test loading missing file"""
        with pytest.raises(FileNotFoundError):
            load_brands("nonexistent_file.json")
    
    @patch('sverification.compare_metadata.extract_pdf_metadata')
    @patch('sverification.compare_metadata.recover_pdf_versions')
    @patch('sverification.compare_metadata.count_pdf_eof_markers')
    @patch('sverification.compare_metadata.check_no_of_versions')
    def test_extract_all(self, mock_versions, mock_eof, mock_recover, mock_metadata):
        """Test extract_all function"""
        # Setup mocks
        mock_metadata.return_value = {
            "PDF Version": "1.4",
            "Creator": "Test Creator",
            "Producer": "Test Producer"
        }
        mock_recover.return_value = ["version_info"]
        mock_eof.return_value = 1
        mock_versions.return_value = 1
        
        result = extract_all("test.pdf")
        
        # Check that all functions were called
        mock_metadata.assert_called_once_with("test.pdf")
        mock_recover.assert_called_once_with("test.pdf")
        mock_eof.assert_called_once_with("test.pdf")
        mock_versions.assert_called_once_with("test.pdf")
        
        # Check result structure
        assert "pdf_version" in result
        assert "creator" in result
        assert "producer" in result
        assert "eof_markers" in result
        assert "pdf_versions" in result
        assert result["pdf_version"] == "1.4"
        assert result["eof_markers"] == 1
    
    def test_compare_fields_perfect_match(self, sample_metadata):
        """Test compare_fields with perfect match"""
        expected = sample_metadata.copy()
        
        results, score = compare_fields(sample_metadata, expected)
        
        assert score == 100.0
        # Check that all comparisons passed
        for field, exp, act, match in results:
            if field != "dates_equal_check":  # Skip the special date check
                assert match == True
    
    def test_compare_fields_partial_match(self, sample_metadata):
        """Test compare_fields with partial match"""
        expected = sample_metadata.copy()
        expected["creator"] = "Different Creator"  # This won't match
        expected["pdf_version"] = "1.7"  # This won't match
        
        results, score = compare_fields(sample_metadata, expected)
        
        assert score < 100.0
        # Should have some failed matches
        failed_matches = [r for r in results if not r[3]]
        assert len(failed_matches) > 0
    
    def test_compare_fields_dates_equal_check(self):
        """Test the special dates equal check"""
        metadata = {
            "creationdate": "D:20240101120000Z",
            "moddate": "D:20240101120000Z",  # Same as creation
            "pdf_version": "1.4"
        }
        expected = {"pdf_version": "1.4"}
        
        results, score = compare_fields(metadata, expected)
        
        # Find the dates_equal_check result
        dates_check = next((r for r in results if r[0] == "dates_equal_check"), None)
        assert dates_check is not None
        assert dates_check[3] == True  # Dates should be equal
    
    def test_compare_fields_dates_not_equal_check(self):
        """Test dates not equal check"""
        metadata = {
            "creationdate": "D:20240101120000Z",
            "moddate": "D:20240102120000Z",  # Different from creation
            "pdf_version": "1.4"
        }
        expected = {"pdf_version": "1.4"}
        
        results, score = compare_fields(metadata, expected)
        
        # Find the dates_equal_check result
        dates_check = next((r for r in results if r[0] == "dates_equal_check"), None)
        assert dates_check is not None
        assert dates_check[3] == False  # Dates should not be equal
    
    def test_compare_fields_numeric_comparison(self):
        """Test numeric field comparison"""
        metadata = {"eof_markers": 2, "pdf_versions": 1}
        expected = {"eof_markers": "2", "pdf_versions": 1}  # Mix of string and int
        
        results, score = compare_fields(metadata, expected)
        
        # Both should match despite type differences
        eof_result = next((r for r in results if r[0] == "eof_markers"), None)
        versions_result = next((r for r in results if r[0] == "pdf_versions"), None)
        
        assert eof_result[3] == True
        assert versions_result[3] == True
