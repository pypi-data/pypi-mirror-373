"""Core validation logic for agent outputs."""

import json
import time
from typing import Any, Optional, Union

from .errors import ValidationError
from .logging_ import log_validation_result
from .schemas import Schema
from .typing_ import Config, RetryFunction, ValidationMode


def validate(
    agent_output: Union[str, dict[str, Any]],
    schema: Schema,
    retry_fn: Optional[RetryFunction] = None,
    retries: int = 2,
    mode: ValidationMode = ValidationMode.STRICT,
    timeout_s: int = 20,
    log_to_cloud: bool = False,
    context: Optional[dict[str, Any]] = None,
    config: Optional[Config] = None,
) -> Any:
    """
    Validate agent output against a schema with optional retries.

    Args:
        agent_output: The output to validate (string or dict)
        schema: Schema to validate against
        retry_fn: Function to call for retries (prompt, context) -> output
        retries: Number of retry attempts
        mode: Validation mode (STRICT or COERCE)
        timeout_s: Timeout per attempt in seconds
        log_to_cloud: Whether to log to cloud service
        context: Additional context for logging
        config: Configuration object

    Returns:
        Validated and coerced output

    Raises:
        ValidationError: If validation fails after all retries
        SchemaError: If schema is malformed
    """
    config = config or Config()
    context = context or {}
    correlation_id = context.get("correlation_id")

    # Store original input for retry function
    original_input = agent_output

    # Parse string output to dict if needed
    if isinstance(agent_output, str):
        try:
            agent_output = json.loads(agent_output)
        except json.JSONDecodeError:
            if mode == ValidationMode.STRICT:
                # If we have a retry function, try to get better output
                if retry_fn:
                    # Don't raise immediately, let the retry logic handle it
                    pass
                else:
                    raise ValidationError(
                        path="root",
                        reason="Invalid JSON",
                        attempt=0,
                        correlation_id=correlation_id,
                    ) from None
            # In COERCE mode, treat as plain string
            agent_output = {"raw_output": agent_output}

    # Check size limits
    output_str = json.dumps(agent_output)
    if len(output_str.encode()) > config.max_output_bytes:
        raise ValidationError(
            path="root",
            reason="size_limit",
            attempt=0,
            correlation_id=correlation_id,
        )

    # Check if we need to retry due to JSON parsing failure
    json_parse_failed = False
    if (
        isinstance(original_input, str)
        and isinstance(agent_output, dict)
        and "raw_output" in agent_output
    ):
        json_parse_failed = True

    # Check if we need to retry due to JSON parsing failure
    json_parse_failed = False
    if (
        isinstance(original_input, str)
        and isinstance(agent_output, dict)
        and "raw_output" in agent_output
    ):
        json_parse_failed = True

    # Initialize retry variables
    start_time = None
    last_error = None

    # If JSON parsing failed and we have a retry function, go directly to retry
    if json_parse_failed and retry_fn:
        start_time = time.time()
        last_error = ValidationError(
            path="root",
            reason="Invalid JSON",
            attempt=0,
            correlation_id=correlation_id,
        )
    else:
        # Validate against schema
        try:
            validated_output = _validate_against_schema(
                agent_output, schema, mode, config
            )

            # Log successful validation
            log_validation_result(
                correlation_id=correlation_id,
                valid=True,
                errors=[],
                attempts=1,
                duration_ms=0,
                mode=mode.value,
                context=context,
                output_sample=output_str[:1000],
                log_to_cloud=log_to_cloud,
                config=config,
            )

            return validated_output

        except ValidationError as e:
            # If no retry function, re-raise immediately
            if not retry_fn:
                log_validation_result(
                    correlation_id=correlation_id,
                    valid=False,
                    errors=[{"path": e.path, "reason": e.reason}],
                    attempts=1,
                    duration_ms=0,
                    mode=mode.value,
                    context=context,
                    output_sample=output_str[:1000],
                    log_to_cloud=log_to_cloud,
                    config=config,
                )
                raise

            # Try retries
            start_time = time.time()
            last_error = e

    # Retry for both JSON parsing failures and schema validation failures
    if start_time is not None and last_error is not None:
        for attempt in range(1, retries + 1):
            try:
                # Call retry function
                new_output = retry_fn(original_input, context)  # type: ignore

                # Parse new output
                if isinstance(new_output, str):
                    try:
                        new_output = json.loads(new_output)
                    except json.JSONDecodeError:
                        if mode == ValidationMode.STRICT:
                            continue
                        new_output = {"raw_output": new_output}

                # Check size limits
                new_output_str = json.dumps(new_output)
                if len(new_output_str.encode()) > config.max_output_bytes:
                    continue

                # Validate new output
                validated_output = _validate_against_schema(
                    new_output, schema, mode, config
                )

                # Log successful validation
                duration_ms = int((time.time() - start_time) * 1000)
                log_validation_result(
                    correlation_id=correlation_id,
                    valid=True,
                    errors=[],
                    attempts=attempt + 1,
                    duration_ms=duration_ms,
                    mode=mode.value,
                    context=context,
                    output_sample=new_output_str[:1000],
                    log_to_cloud=log_to_cloud,
                    config=config,
                )

                return validated_output

            except ValidationError as retry_error:
                last_error = retry_error
                continue

        # All retries failed
        duration_ms = int((time.time() - start_time) * 1000)
        log_validation_result(
            correlation_id=correlation_id,
            valid=False,
            errors=[{"path": last_error.path, "reason": last_error.reason}],
            attempts=retries + 1,
            duration_ms=duration_ms,
            mode=mode.value,
            context=context,
            output_sample=output_str[:1000],
            log_to_cloud=log_to_cloud,
            config=config,
        )

        raise last_error


def _validate_against_schema(
    data: Any,
    schema: Schema,
    mode: ValidationMode,
    config: Config,
    path: str = "root",
) -> Any:
    """Validate data against schema with optional coercion."""

    # Check if data is None (optional field)
    if data is None:
        return None

    # Apply size limits
    if isinstance(data, str) and len(data) > config.max_str_len:
        raise ValidationError(
            path=path,
            reason="size_limit",
            attempt=0,
        )

    if isinstance(data, list) and len(data) > config.max_list_len:
        raise ValidationError(
            path=path,
            reason="size_limit",
            attempt=0,
        )

    if isinstance(data, dict) and len(data) > config.max_dict_keys:
        raise ValidationError(
            path=path,
            reason="size_limit",
            attempt=0,
        )

    # Validate against schema
    if isinstance(schema.schema_dict, dict):
        if not isinstance(data, dict):
            if mode == ValidationMode.STRICT:
                raise ValidationError(
                    path=path,
                    reason=f"Expected dict, got {type(data).__name__}",
                    attempt=0,
                )
            # Try to coerce
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    raise ValidationError(
                        path=path,
                        reason="Cannot coerce to dict",
                        attempt=0,
                    ) from None
            else:
                raise ValidationError(
                    path=path,
                    reason="Cannot coerce to dict",
                    attempt=0,
                )

        result = {}
        for key, expected_type in schema.schema_dict.items():
            if key not in data:
                if expected_type is not None:
                    raise ValidationError(
                        path=f"{path}.{key}",
                        reason="Missing required field",
                        attempt=0,
                    )
                continue

            value = data[key]
            if expected_type is None:
                # Optional field
                result[key] = value
            elif isinstance(expected_type, type):
                result[key] = _validate_type(
                    value, expected_type, mode, f"{path}.{key}", config
                )
            elif isinstance(expected_type, dict):
                # Nested schema
                nested_schema = Schema(expected_type)
                result[key] = _validate_against_schema(
                    value, nested_schema, mode, config, f"{path}.{key}"
                )
            elif isinstance(expected_type, list):
                # List schema
                if not isinstance(value, list):
                    if mode == ValidationMode.STRICT:
                        raise ValidationError(
                            path=f"{path}.{key}",
                            reason=f"Expected list, got {type(value).__name__}",
                            attempt=0,
                        )
                    # Try to coerce
                    if isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            raise ValidationError(
                                path=f"{path}.{key}",
                                reason="Cannot coerce to list",
                                attempt=0,
                            ) from None
                    else:
                        raise ValidationError(
                            path=f"{path}.{key}",
                            reason="Cannot coerce to list",
                            attempt=0,
                        )

                element_type = expected_type[0]
                if isinstance(element_type, type):
                    result[key] = [
                        _validate_type(
                            item, element_type, mode, f"{path}.{key}[{i}]", config
                        )
                        for i, item in enumerate(value)
                    ]
                elif isinstance(element_type, dict):
                    nested_schema = Schema(element_type)
                    result[key] = [
                        _validate_against_schema(
                            item, nested_schema, mode, config, f"{path}.{key}[{i}]"
                        )
                        for i, item in enumerate(value)
                    ]

        return result

    return data  # type: ignore


def _validate_type(
    value: Any,
    expected_type: type,
    mode: ValidationMode,
    path: str,
    config: Optional[Config] = None,
) -> Any:
    """Validate and optionally coerce a value to the expected type."""

    if isinstance(value, expected_type):
        # Apply size limits for strings
        if (
            expected_type is str
            and config
            and isinstance(value, str)
            and len(value) > config.max_str_len
        ):
            raise ValidationError(
                path=path,
                reason="size_limit",
                attempt=0,
            )
        return value

    if mode == ValidationMode.STRICT:
        raise ValidationError(
            path=path,
            reason=f"Expected {expected_type.__name__}, got {type(value).__name__}",
            attempt=0,
        )

    # Coerce in COERCE mode
    if expected_type is int:
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                raise ValidationError(
                    path=path,
                    reason="Cannot coerce to int",
                    attempt=0,
                ) from None
        elif isinstance(value, float):
            return int(value)
        else:
            raise ValidationError(
                path=path,
                reason="Cannot coerce to int",
                attempt=0,
            )

    elif expected_type is float:
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                raise ValidationError(
                    path=path,
                    reason="Cannot coerce to float",
                    attempt=0,
                ) from None
        elif isinstance(value, int):
            return float(value)
        else:
            raise ValidationError(
                path=path,
                reason="Cannot coerce to float",
                attempt=0,
            )

    elif expected_type is bool:
        if isinstance(value, str):
            value_lower = value.strip().lower()
            if value_lower in ("true", "1", "yes", "on"):
                return True
            elif value_lower in ("false", "0", "no", "off"):
                return False
            else:
                raise ValidationError(
                    path=path,
                    reason="Cannot coerce to bool",
                    attempt=0,
                )
        elif isinstance(value, int):
            return bool(value)
        else:
            raise ValidationError(
                path=path,
                reason="Cannot coerce to bool",
                attempt=0,
            )

    elif expected_type is str:
        result = str(value)
        # Apply size limits for coerced strings
        if config and len(result) > config.max_str_len:
            raise ValidationError(
                path=path,
                reason="size_limit",
                attempt=0,
            )
        return result

    else:
        raise ValidationError(
            path=path,
            reason=f"Cannot coerce to {expected_type.__name__}",
            attempt=0,
        )
