c"""
Test suite for core modules
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from clyrdia.core.env_loader import EnvironmentLoader, get_api_keys, has_api_keys
from clyrdia.core.console import console, _display_welcome_screen, format_help_text
from clyrdia.core.decorators import require_auth, _is_first_run

class TestEnvironmentLoader:
    """Test environment loader functionality"""

    def test_environment_loader_initialization(self):
        """Test EnvironmentLoader initializes correctly"""
        loader = EnvironmentLoader()
        assert loader is not None
        assert hasattr(loader, '_loaded')
        assert hasattr(loader, '_env_file_path')

    @patch('os.getenv')
    def test_get_api_keys_openai(self, mock_getenv):
        """Test getting OpenAI API key"""
        mock_getenv.side_effect = lambda x: 'sk-test123' if x == 'OPENAI_API_KEY' else None
        
        loader = EnvironmentLoader()
        api_keys = loader.get_api_keys()
        
        assert 'openai' in api_keys
        assert api_keys['openai'] == 'sk-test123'

    @patch('os.getenv')
    def test_get_api_keys_anthropic(self, mock_getenv):
        """Test getting Anthropic API key"""
        mock_getenv.side_effect = lambda x: 'sk-ant-test123' if x == 'ANTHROPIC_API_KEY' else None
        
        loader = EnvironmentLoader()
        api_keys = loader.get_api_keys()
        
        assert 'anthropic' in api_keys
        assert api_keys['anthropic'] == 'sk-ant-test123'

    @patch('os.getenv')
    def test_get_api_keys_both(self, mock_getenv):
        """Test getting both API keys"""
        mock_getenv.side_effect = lambda x: {
            'OPENAI_API_KEY': 'sk-test123',
            'ANTHROPIC_API_KEY': 'sk-ant-test123'
        }.get(x)
        
        loader = EnvironmentLoader()
        api_keys = loader.get_api_keys()
        
        assert 'openai' in api_keys
        assert 'anthropic' in api_keys
        assert len(api_keys) == 2

    @patch('os.getenv')
    def test_get_api_keys_none(self, mock_getenv):
        """Test getting no API keys"""
        mock_getenv.return_value = None
        
        loader = EnvironmentLoader()
        api_keys = loader.get_api_keys()
        
        assert len(api_keys) == 0

    def test_has_api_keys(self):
        """Test has_api_keys function"""
        with patch('clyrdia.core.env_loader.env_loader.get_api_keys') as mock_get:
            mock_get.return_value = {'openai': 'sk-test123'}
            assert has_api_keys() is True
            
            mock_get.return_value = {}
            assert has_api_keys() is False

    def test_get_api_key_specific_provider(self):
        """Test getting specific provider API key"""
        with patch('clyrdia.core.env_loader.env_loader.get_api_keys') as mock_get:
            mock_get.return_value = {'openai': 'sk-test123', 'anthropic': 'sk-ant-test123'}
            
            from clyrdia.core.env_loader import get_api_key
            assert get_api_key('openai') == 'sk-test123'
            assert get_api_key('anthropic') == 'sk-ant-test123'
            assert get_api_key('nonexistent') is None

class TestConsole:
    """Test console functionality"""

    def test_console_object(self):
        """Test console object exists and has expected methods"""
        assert console is not None
        assert hasattr(console, 'print')
        assert hasattr(console, 'rule')

    def test_display_welcome_screen(self):
        """Test welcome screen display"""
        # This function should not raise any errors
        try:
            _display_welcome_screen()
        except Exception as e:
            pytest.fail(f"Welcome screen display failed: {e}")

    def test_format_help_text(self):
        """Test help text formatting"""
        help_text = format_help_text()
        assert isinstance(help_text, str)
        assert len(help_text) > 0

class TestDecorators:
    """Test authentication decorators"""

    @patch('clyrdia.core.decorators.Path')
    def test_is_first_run_true(self, mock_path):
        """Test first run detection when config doesn't exist"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        assert _is_first_run() is True

    @patch('clyrdia.core.decorators.Path')
    def test_is_first_run_false(self, mock_path):
        """Test first run detection when config exists"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        assert _is_first_run() is False

    def test_require_auth_decorator(self):
        """Test require_auth decorator exists"""
        assert require_auth is not None
        assert callable(require_auth)

class TestHelperFunctions:
    """Test helper functions"""

    def test_get_api_keys_function(self):
        """Test get_api_keys function exists and works"""
        assert callable(get_api_keys)
        
        # Test it returns a dict
        api_keys = get_api_keys()
        assert isinstance(api_keys, dict)

    def test_has_api_keys_function(self):
        """Test has_api_keys function exists and works"""
        assert callable(has_api_keys)
        
        # Test it returns a boolean
        result = has_api_keys()
        assert isinstance(result, bool)
