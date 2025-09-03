"""
Test cases for the new verbose verification function.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import sverification
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sverification


class TestVerboseVerification(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_metadata = {
            'pdf_version': '1.4',
            'creator': 'Test Creator',
            'producer': 'Test Producer',
            'eof_markers': 1,
            'pdf_versions': 1,
            'creationdate': 'D:20240101120000Z',
            'moddate': 'D:20240101120000Z'
        }
        
        self.sample_brands = {
            'testbank': [{
                'brand': 'testbank',
                'pdf_version': '1.4',
                'creator': 'Test Creator',
                'producer': 'Test Producer',
                'eof_markers': 1,
                'pdf_versions': 1
            }]
        }
    
    @patch('sverification.compare_metadata.get_company_name')
    @patch('sverification.compare_metadata.extract_all')
    @patch('sverification.compare_metadata.load_brands')
    @patch('os.path.exists')
    def test_verify_statement_verbose_success(self, mock_exists, mock_load_brands, 
                                            mock_extract, mock_get_company):
        """Test successful verification with perfect match"""
        # Mock all external dependencies
        mock_exists.return_value = True
        mock_get_company.return_value = 'testbank'
        mock_extract.return_value = self.sample_metadata
        mock_load_brands.return_value = self.sample_brands
        
        # Test the function
        result = sverification.verify_statement_verbose('test.pdf')
        
        # Verify result structure
        self.assertIn('pdf_path', result)
        self.assertIn('detected_brand', result)
        self.assertIn('verification_score', result)
        self.assertIn('field_results', result)
        self.assertIn('summary', result)
        
        # Verify values
        self.assertEqual(result['detected_brand'], 'testbank')
        self.assertEqual(result['template_used'], 'testbank')
        self.assertGreater(result['verification_score'], 0)
        self.assertIsInstance(result['field_results'], list)
    
    @patch('sverification.compare_metadata.get_company_name')
    @patch('sverification.compare_metadata.extract_all')
    @patch('sverification.compare_metadata.load_brands')
    @patch('os.path.exists')
    def test_verify_statement_verbose_brand_not_found(self, mock_exists, mock_load_brands,
                                                     mock_extract, mock_get_company):
        """Test verification when brand is not found in templates"""
        # Mock external dependencies
        mock_exists.return_value = True
        mock_get_company.return_value = 'unknownbank'
        mock_extract.return_value = self.sample_metadata
        mock_load_brands.return_value = self.sample_brands
        
        # Test the function
        result = sverification.verify_statement_verbose('test.pdf')
        
        # Verify error handling
        self.assertEqual(result['verification_score'], 0.0)
        self.assertIn('error', result)
        self.assertIn('unknownbank', result['summary'])
    
    def test_print_verification_report(self):
        """Test the print verification report function"""
        # Create a sample result
        sample_result = {
            'pdf_path': '/path/to/test.pdf',
            'detected_brand': 'testbank',
            'template_used': 'testbank',
            'verification_score': 85.5,
            'field_results': [
                {
                    'field': 'pdf_version',
                    'expected': '1.4',
                    'actual': '1.4',
                    'match': True,
                    'status': '✓'
                },
                {
                    'field': 'creator',
                    'expected': 'Expected Creator',
                    'actual': 'Actual Creator',
                    'match': False,
                    'status': '✗'
                }
            ],
            'summary': 'PDF: test.pdf\nDetected brand: testbank\nScore: 85.5%'
        }
        
        # Test that it doesn't raise an exception
        try:
            sverification.print_verification_report(sample_result)
        except Exception as e:
            self.fail(f"print_verification_report raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()
