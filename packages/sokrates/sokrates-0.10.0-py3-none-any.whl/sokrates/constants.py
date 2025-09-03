from pathlib import Path

class Constants:  
  # Endpoint
  DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
  DEFAULT_API_KEY = "notrequired"
  
  # Model settings
  DEFAULT_MODEL = "qwen3-4b-instruct-2507-mlx"
  DEFAULT_MODEL_TEMPERATURE = 0.7
  
  # paths
  # TODO: refactor this to be a Path and not a string object (see DEFAULT_CODING_PROMPTS_DIRECTORY below)
  DEFAULT_PROMPTS_DIRECTORY = str((Path(__file__).parent / "prompts").resolve())
  DEFAULT_CODING_PROMPTS_DIRECTORY = (Path(__file__).parent / "prompts" / "coding").resolve()
  
  # Task daemon
  DEFAULT_DAEMON_PROCESSING_INTERVAL = 15
  DEFAULT_TASK_DAEMON_DEAD_LETTER_QUEUE_ENABLED = True
  DEFAULT_TASK_DAEMON_BASE_RETRY_DELAY = 2
  DEFAULT_TASK_DAEMON_MAX_RETRIES = 2