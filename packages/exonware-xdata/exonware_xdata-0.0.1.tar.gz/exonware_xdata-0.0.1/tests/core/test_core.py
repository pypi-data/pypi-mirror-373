"""
Core functionality tests for {LIBRARY_NAME}

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: {GENERATION_DATE}
"""

import pytest
# from exonware.{LIBRARY_NAME} import YourMainClass  # Uncomment and modify as needed

class TestCore:
    """Test core functionality."""
    
    def test_import(self):
        """Test that the library can be imported."""
        try:
            import exonware.{LIBRARY_NAME}
            assert True
        except ImportError:
            pytest.fail("Could not import exonware.{LIBRARY_NAME}")
    
    def test_convenience_import(self):
        """Test that the convenience import works."""
        try:
            import {LIBRARY_NAME}
            assert True
        except ImportError:
            pytest.fail("Could not import {LIBRARY_NAME}")
    
    def test_version_info(self):
        """Test that version information is available."""
        import exonware.{LIBRARY_NAME}
        
        assert hasattr(exonware.{LIBRARY_NAME}, '__version__')
        assert hasattr(exonware.{LIBRARY_NAME}, '__author__')
        assert hasattr(exonware.{LIBRARY_NAME}, '__email__')
        assert hasattr(exonware.{LIBRARY_NAME}, '__company__')
        
        # Verify values are strings
        assert isinstance(exonware.{LIBRARY_NAME}.__version__, str)
        assert isinstance(exonware.{LIBRARY_NAME}.__author__, str)
        assert isinstance(exonware.{LIBRARY_NAME}.__email__, str)
        assert isinstance(exonware.{LIBRARY_NAME}.__company__, str)
    
    def test_sample_functionality(self, sample_data):
        """Sample test using fixture data."""
        # Replace this with actual tests for your library
        assert sample_data["test_data"] == "sample"
        assert len(sample_data["numbers"]) == 5
        assert sample_data["nested"]["key"] == "value"
