import os
from typing import Any


# Function to read from environment or default to hardcoded value
def env_or_default(var_name: str, default: Any) -> Any:
    value = os.getenv(f"SEEKR_{var_name}")
    if value is not None:
        return value.split(",") if isinstance(default, list) else value
    return default


# Session constants
TIMEOUT_SECS = int(env_or_default("TIMEOUT_SECS", 600))
MAX_SESSION_LIFETIME_SECS = int(env_or_default("MAX_SESSION_LIFETIME_SECS", 180))
MAX_CONNECTION_RETRIES = int(env_or_default("MAX_CONNECTION_RETRIES", 2))
MAX_RETRIES = int(env_or_default("MAX_RETRIES", 5))
INITIAL_RETRY_DELAY = float(env_or_default("INITIAL_RETRY_DELAY", 0.5))
MAX_RETRY_DELAY = float(env_or_default("MAX_RETRY_DELAY", 8.0))

# API defaults
BASE_URL = env_or_default("BASE_URL", "https://flow.seekr.com/v1")

# Download defaults
DOWNLOAD_BLOCK_SIZE = int(
    env_or_default("DOWNLOAD_BLOCK_SIZE", 10 * 1024 * 1024)
)  # 10 MB
DISABLE_TQDM = bool(
    int(env_or_default("DISABLE_TQDM", 0))
)  # Assumes DISABLE_TQDM set as 0 (False) or 1 (True)

# Messages
MISSING_API_KEY_MESSAGE = env_or_default(
    "MISSING_API_KEY_MESSAGE",
    """SEEKR_API_KEY not found.
Please set it as an environment variable or set it as seekrai.api_key
Find your SEEKR_API_KEY at https://seekr.com/xxx""",
)

# Minimum number of samples required for fine-tuning file
MIN_SAMPLES = int(env_or_default("MIN_SAMPLES", 100))

# the number of bytes in a gigabyte, used to convert bytes to GB for readable comparison
NUM_BYTES_IN_GB = int(env_or_default("NUM_BYTES_IN_GB", 2**30))

# maximum number of GB sized files we support finetuning for
MAX_FILE_SIZE_GB = float(env_or_default("MAX_FILE_SIZE_GB", 4.9))

# expected columns for Parquet files
PARQUET_EXPECTED_COLUMNS = env_or_default(
    "PARQUET_EXPECTED_COLUMNS", ["input_ids", "attention_mask", "labels"]
)
