"""
Core functionality tests for xnode

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025
"""

import pytest
# from exonware.xnode import YourMainClass  # Uncomment and modify as needed

class TestCore:
    """Test core functionality."""
    
    def test_import(self):
        """Test that the library can be imported."""
        try:
            import exonware.xnode
            assert True
        except ImportError:
            pytest.fail("Could not import exonware.xnode")
    
    def test_convenience_import(self):
        """Test that the convenience import works."""
        try:
            import xnode
            assert True
        except ImportError:
            pytest.fail("Could not import xnode")
    
    def test_version_info(self):
        """Test that version information is available."""
        import exonware.xnode
        
        assert hasattr(exonware.xnode, '__version__')
        assert hasattr(exonware.xnode, '__author__')
        assert hasattr(exonware.xnode, '__email__')
        assert hasattr(exonware.xnode, '__company__')
        
        # Verify values are strings
        assert isinstance(exonware.xnode.__version__, str)
        assert isinstance(exonware.xnode.__author__, str)
        assert isinstance(exonware.xnode.__email__, str)
        assert isinstance(exonware.xnode.__company__, str)
    
    def test_sample_functionality(self, sample_data):
        """Sample test using fixture data."""
        # Replace this with actual tests for your library
        assert sample_data["test_data"] == "sample"
        assert len(sample_data["numbers"]) == 5
        assert sample_data["nested"]["key"] == "value"
