import logging
import os

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import keyring

load_dotenv()
KEYRING_USERNAME = "user"
KEYRING_OPENAI_USERNAME = "openai_user"  # Separate keyring entry for OpenAI key

def get_production_backend_url() -> str:
    """
    Get the production backend URL - uses domain name for reliability.
    """
    return "https://co-datascientist.io"

class Settings(BaseSettings):
    
    service_name: str = "CoDatascientist"
    api_key: SecretStr = ""
    openai_key: SecretStr = ""  # Optional OpenAI key
    log_level: int = logging.ERROR
    host: str = "localhost"
    port: int = 8000
    wait_time_between_checks_seconds: int = 10
    # Centralized timeout from mode-switch.sh via environment variable
    script_execution_timeout: int = int(os.getenv("CO_DATASCIENTIST_SCRIPT_EXECUTION_TIMEOUT", "1800"))  # Use centralized timeout, default 30 minutes
    
    # Production backend URL (default for PyPI installations)
    # Now supports dynamic detection and environment variable override
    co_datascientist_backend_url: str = ""
    co_datascientist_backend_url_dev: str = "http://localhost:8000"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set production backend URL if not provided via environment
        if not self.co_datascientist_backend_url:
            # Check if environment variable is set first
            env_url = os.getenv('CO_DATASCIENTIST_CO_DATASCIENTIST_BACKEND_URL')
            if env_url:
                self.co_datascientist_backend_url = env_url
            else:
                # Use production domain name (stable and reliable)
                self.co_datascientist_backend_url = get_production_backend_url()
    verify_ssl: bool = False  # Set to False for self-signed certificates
    
    # Default to production mode (False) for PyPI installations
    # Only becomes True when:
    # 1. --dev flag is used in CLI
    # 2. CO_DATASCIENTIST_DEV_MODE=true environment variable is set
    dev_mode: bool = False
    
    class Config:
        env_prefix = "CO_DATASCIENTIST_"  # Allow environment variables with this prefix
    
    @property
    def backend_url(self) -> str:
        """Return the appropriate backend URL based on dev_mode setting"""
        if self.dev_mode:
            return self.co_datascientist_backend_url_dev
        else:
            return self.co_datascientist_backend_url
    
    def enable_dev_mode(self):
        """Enable development mode to use local backend"""
        self.dev_mode = True
        print(f"🔧 Development mode enabled")
        print(f"   Using local backend: {self.co_datascientist_backend_url_dev}")
    
    def disable_dev_mode(self):
        """Disable development mode to use production backend"""
        self.dev_mode = False
        print(f"🌐 Production mode enabled")
        print(f"   Using production backend: {self.co_datascientist_backend_url}")

    def get_api_key(self):
        token = keyring.get_password(self.service_name, KEYRING_USERNAME)
        if not token:
            print("\n🔐 Authentication Required")
            token = input("Please enter your API key: ").strip()
            if token:
                keyring.set_password(self.service_name, KEYRING_USERNAME, token)
                print("✅ API key saved securely")
            else:
                print("❌ API key is required to continue")
                exit(1)
        self.api_key = SecretStr(token)
    
    def get_openai_key(self, prompt_if_missing: bool = True):
        """
        Get OpenAI key from keyring or prompt user (optional).
        
        Args:
            prompt_if_missing: If True, prompt user for key if not found. If False, return None silently.
        
        Returns:
            OpenAI key or None if not provided
        """
        openai_key = keyring.get_password(self.service_name, KEYRING_OPENAI_USERNAME)
        if not openai_key and prompt_if_missing:
            print("\n🔑 Optional: OpenAI API Key Setup")
            print("   Provide your OpenAI API key to use your own tokens instead of TropiFlow's free tier.")
            print("   This allows unlimited usage with your OpenAI account.")
            print("   You can skip this by pressing Enter to use TropiFlow's free tier.")
            print()
            openai_key = input("OpenAI API key (optional): ").strip()
            if openai_key:
                keyring.set_password(self.service_name, KEYRING_OPENAI_USERNAME, openai_key)
                print("✅ OpenAI key saved. Your requests will use your OpenAI account.")
            else:
                print("ℹ️  Using TropiFlow's free tier. You can add your OpenAI key later with 'openai_key' command.")
        
        if openai_key:
            self.openai_key = SecretStr(openai_key)
            return openai_key
        return None

    def delete_api_key(self):
        try:
            keyring.delete_password(self.service_name, KEYRING_USERNAME)
            print("✅ API key removed successfully")
        except keyring.errors.PasswordDeleteError:
            print("ℹ️  No API key was stored")
    
    def delete_openai_key(self):
        """Delete stored OpenAI key"""
        try:
            keyring.delete_password(self.service_name, KEYRING_OPENAI_USERNAME)
            self.openai_key = SecretStr("")
            print("✅ OpenAI key removed. Future requests will use TropiFlow's free tier.")
        except keyring.errors.PasswordDeleteError:
            print("ℹ️  No OpenAI key was stored.")

settings = Settings()
