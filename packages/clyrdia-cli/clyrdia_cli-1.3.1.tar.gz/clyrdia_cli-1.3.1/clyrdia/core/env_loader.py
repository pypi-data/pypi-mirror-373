"""
Environment loader for Clyrdia CLI - seamlessly reads API keys from .env files
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

class EnvironmentLoader:
    """Loads environment variables from .env files and provides seamless API key access"""
    
    def __init__(self):
        self._loaded = False
        self._env_file_path = None
        self._load_environment()
    
    def _load_environment(self):
        """Load environment variables from .env files"""
        if self._loaded:
            return
        
        # Look for .env files in common locations
        env_locations = [
            Path.cwd() / ".env",                    # Current working directory
            Path.cwd() / ".env.local",              # Local environment
            Path.cwd() / ".env.production",         # Production environment
            Path.cwd() / ".env.development",        # Development environment
            Path.home() / ".clyrdia" / ".env",      # User's Clyrdia directory
            Path.home() / ".env",                   # User's home directory
        ]
        
        # Try to load from each location
        for env_path in env_locations:
            if env_path.exists():
                try:
                    load_dotenv(env_path, override=True)
                    self._env_file_path = env_path
                    print(f"✅ Loaded environment from: {env_path}")
                    break
                except Exception as e:
                    print(f"⚠️  Warning: Could not load {env_path}: {e}")
        
        # Also try to load from current directory .env
        if not self._env_file_path:
            try:
                load_dotenv(override=True)
                self._env_file_path = Path.cwd() / ".env"
                if self._env_file_path.exists():
                    print(f"✅ Loaded environment from: {self._env_file_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not load .env file: {e}")
        
        self._loaded = True
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get all available API keys from environment"""
        api_keys = {}
        
        # OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.strip():
            api_keys['openai'] = openai_key.strip()
        
        # Anthropic API key
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key.strip():
            api_keys['anthropic'] = anthropic_key.strip()
        
        return api_keys
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        api_keys = self.get_api_keys()
        return api_keys.get(provider)
    
    def has_api_keys(self) -> bool:
        """Check if any API keys are available"""
        return len(self.get_api_keys()) > 0
    
    def get_available_providers(self) -> list:
        """Get list of available API providers"""
        return list(self.get_api_keys().keys())
    
    def get_env_file_path(self) -> Optional[Path]:
        """Get the path of the loaded .env file"""
        return self._env_file_path
    
    def reload(self):
        """Reload environment variables"""
        self._loaded = False
        self._load_environment()
    
    def print_status(self):
        """Print current environment status"""
        print("🔧 Environment Configuration:")
        print(f"   .env file: {self.get_env_file_path() or 'Not found'}")
        
        api_keys = self.get_api_keys()
        if api_keys:
            print(f"   Available providers: {', '.join(api_keys.keys())}")
            for provider, key in api_keys.items():
                # Show first and last 4 characters of key for security
                masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
                print(f"   {provider.upper()}: {masked_key}")
        else:
            print("   ⚠️  No API keys found")
            print("   💡 Create a .env file with your API keys")
        
        # Show other relevant environment variables
        other_vars = [
            'CLYRDIA_ENV', 'CLYRDIA_LOG_LEVEL', 'CLYRDIA_DASHBOARD_PORT',
            'CLYRDIA_DB_PATH', 'CACHE_TTL_HOURS', 'CACHE_MAX_SIZE_MB'
        ]
        
        print("\n📋 Other Configuration:")
        for var in other_vars:
            value = os.getenv(var)
            if value:
                print(f"   {var}: {value}")

# Global instance
env_loader = EnvironmentLoader()

def get_api_keys() -> Dict[str, str]:
    """Get all available API keys"""
    return env_loader.get_api_keys()

def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a specific provider"""
    return env_loader.get_api_key(provider)

def has_api_keys() -> bool:
    """Check if any API keys are available"""
    return env_loader.has_api_keys()

def reload_environment():
    """Reload environment variables"""
    env_loader.reload()
