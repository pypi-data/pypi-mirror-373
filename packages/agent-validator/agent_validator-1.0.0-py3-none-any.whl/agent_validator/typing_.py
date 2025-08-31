"""Type definitions and enums for agent_validator."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union


class ValidationMode(Enum):
    """Validation modes for schema validation."""

    STRICT = "strict"  # No coercion
    COERCE = "coerce"  # Safe coercions like "42" -> 42


@dataclass
class Config:
    """Configuration for validation and logging."""

    max_output_bytes: int = 131072
    max_str_len: int = 8192
    max_list_len: int = 2048
    max_dict_keys: int = 512
    log_to_cloud: bool = False
    cloud_endpoint: str = "https://api.agentvalidator.dev"
    license_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    timeout_s: int = 20
    retries: int = 2


# Type aliases
SchemaDict = dict[str, Any]
RetryFunction = Callable[[str, dict[str, Any]], Union[str, dict[str, Any]]]
ValidatorFunction = Callable[[Any], bool]
