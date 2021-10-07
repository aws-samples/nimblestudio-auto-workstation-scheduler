"""
Configuration file.
"""

import os

def get_config_var(key: str, default: str) -> str:
    var = os.environ.get(key, default)
    print(f"Using {var} for {key}")
    return var


# AWS Region
AWS_REGION: str = get_config_var("AWS_REGION", "us-west-2")

# Name of environment variable declaring the table name
TABLE_NAME_ENV_VAR = "TABLE_NAME"

NIMBLE_STUDIO_AUTO_WORKSTATION_SCHEDULER_CONFIG_TABLE_NAME = get_config_var(TABLE_NAME_ENV_VAR, "nimble_studio_auto_workstation_scheduler_config")
