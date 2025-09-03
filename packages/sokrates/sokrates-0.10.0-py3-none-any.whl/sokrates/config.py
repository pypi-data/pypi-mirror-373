# This script defines the `Config` class, which is responsible for managing
# application-wide configuration settings. It loads environment variables
# from a `.env` file, providing default values for API endpoints, API keys,
# and the default LLM model. This centralizes configuration management
# and allows for easy customization via environment variables.

import os
from pathlib import Path
from dotenv import load_dotenv
from .colors import Colors
from .constants import Constants
from threading import Lock

class Config:
  """
  Manages configuration settings for the LLM tools application.
  Loads environment variables from a .env file and provides default values
  for various settings like API endpoint, API key, and default model.
  """
  
  _instance = None  # Class variable to hold the single instance
  _lock = Lock()

  def __new__(cls, *args, **kwargs):
        """
        Singleton pattern implementation to ensure only one instance of Config exists.
        
        Returns:
            Config: The single instance of the Config class.
        """
        if not cls._instance:
            # thread safe 
            with cls._lock:
                # Double-check to prevent race condition
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
  
  def __init__(self, verbose=False) -> None:
    """
    Initializes the Config object.

    Args:
        verbose (bool): If True, prints basic configuration details upon loading.
    """
    if not hasattr(self, 'initialized'):
      # initialization
      self.initialized = True
      self.verbose = verbose
      
      # static settings
      self.daemon_processing_interval = Constants.DEFAULT_DAEMON_PROCESSING_INTERVAL
      
      # Determine the configuration file path. Prioritize SOKRATES_CONFIG_FILEPATH environment variable.
      home_base = Path.home()
      self.home_path: str = os.environ.get(
        'SOKRATES_HOME_PATH', 
        str((home_base / ".sokrates").resolve())
      )
      self.config_path: str = os.environ.get(
        'SOKRATES_CONFIG_FILEPATH', 
        str((Path(self.home_path) / '.env').resolve())
      )
      
      # log paths
      self.logs_path: str = str((Path(self.home_path) / 'logs').resolve())
      self.daemon_logfile_path: str = os.environ.get(
        'SOKRATES_DAEMON_LOGFILE_PATH',
        str((Path(self.logs_path) / 'daemon.log').resolve())
      )
      
      # database path
      self.database_path: str = os.environ.get(
        'SOKRATES_DATABASE_PATH', 
        str((Path(self.home_path) / 'sokrates_database.sqlite').resolve())
      )
      
      self.prompts_directory: str = os.environ.get(
        'SOKRATES_PROMPTS_PATH',
        Constants.DEFAULT_PROMPTS_DIRECTORY
      )
      
      self._load_env()
      self._setup_directories()
      self._log_configuration()
    
  def _log_configuration(self) -> None:
      """
      Prints the current configuration settings to the console in a formatted way.
      
      Returns:
          None
      """
      if self.verbose:
        print(f"{Colors.GREEN}{Colors.BOLD}### Basic Configuration ###{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - home_path: {self.home_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - config_path: {self.config_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - database_path: {self.database_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - logfile_path: {self.daemon_logfile_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - api_endpoint: {self.api_endpoint}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - default_model: {self.default_model}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - default_model_temperature: {self.default_model_temperature}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - daemon_processing_interval: {self.daemon_processing_interval}{Colors.RESET}")
  
  def _load_env(self) -> None:
      """
      Loads environment variables from the specified .env file.
      Sets API endpoint, API key, and default model, applying defaults if not found.
      """
      load_dotenv(self.config_path,override=True)
      self.api_endpoint: str | None = os.environ.get('SOKRATES_API_ENDPOINT', Constants.DEFAULT_API_ENDPOINT)
      self.api_key: str | None = os.environ.get('SOKRATES_API_KEY', Constants.DEFAULT_API_KEY)
      self.default_model: str | None = os.environ.get('SOKRATES_DEFAULT_MODEL', Constants.DEFAULT_MODEL)
      
      temperature = float(os.environ.get('SOKRATES_DEFAULT_MODEL_TEMPERATURE', Constants.DEFAULT_MODEL_TEMPERATURE))
      if not (0 < temperature < 1):
        raise ValueError(f"Temperature must be between 0 and 1 (exclusive), got {temperature}")
      self.default_model_temperature: float | None = temperature
      
  def _setup_directories(self) -> None:
    """
    Creates the necessary directory structure for the application.
    
    This method ensures that the following directories exist:
    - The main sokrates home directory (~/.sokrates)
    - The logs subdirectory (~/.sokrates/logs)
    
    Returns:
        None
    """
    if self.verbose:
      print(f"Creating sokrates home path: {self.home_path}")
    
    try:
      Path(self.home_path).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
      raise RuntimeError(f"Failed to create sokrates home directory at `{self.home_path}`: {e}")
    
    if self.verbose:
      print(f"Creating sokrates logs path at: {self.logs_path}")
    
    try:
      Path(self.logs_path).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
      raise RuntimeError(f"Failed to create sokrates logs directory at `{self.logs_path}`: {e}")

  @staticmethod
  def _get_local_member_value(key):
    """
    Retrieves the value of a local member variable by key.

    This static method is used internally to fetch configuration values
    from the singleton instance of Config. It checks for specific keys and returns
    their corresponding values or None if not found.

    Args:
        key (str): The configuration parameter name to retrieve.

    Returns:
        The value of the requested configuration parameter, or None if not found.
    """
    if hasattr(Config._instance, key):
        return getattr(Config._instance, key)
    return None
  
  @staticmethod
  def get(key, default_value=None) -> str:
    """
    Retrieves configuration value with precedence:
    1. Config instance attribute
    2. Environment variable
    3. Provided default_value
    
    Args:
        key (str): Configuration parameter name
        default_value: Fallback if neither instance nor env var exists
        
    Returns:
        str | None: Configuration value or default_value
    """
    lval = Config._get_local_member_value(key)
    if lval is not None:
      return lval
    return os.environ.get(key, default_value)
