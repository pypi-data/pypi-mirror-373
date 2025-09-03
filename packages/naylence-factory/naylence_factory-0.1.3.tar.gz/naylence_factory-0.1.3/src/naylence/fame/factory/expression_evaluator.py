import os
import re
from typing import Any, Optional


class MissingEnvironmentVariableError(Exception):
    """Raised when an environment variable is required but not defined."""

    pass


class ExpressionEvaluator:
    """
    Pure expression evaluator with no external dependencies.

    Supports expressions like:
    - ${env:VAR:default} - Environment variable with optional default

    Can handle both full-string expressions and partial substitutions within strings.
    Examples:
    - "${env:HOST}" -> "localhost" (full replacement)
    - "${env:HOST}/api/v1" -> "localhost/api/v1" (partial substitution)

    This class only handles the actual evaluation logic.
    Policy decisions about when to evaluate are handled by the caller.
    """

    # Regex pattern for environment variable expressions (global search)
    _env_pattern = re.compile(r"\$\{env:([^:}]+)(?::([^}]*))?\}")

    @classmethod
    def is_expression(cls, value: Any) -> bool:
        """
        Check if a value contains any expressions that can be evaluated.

        Args:
            value: The value to check

        Returns:
            True if the value is a string containing expressions, False otherwise
        """
        if not isinstance(value, str):
            return False

        return cls._env_pattern.search(value) is not None

    @classmethod
    def evaluate(cls, value: Any, target_type: Optional[type] = None) -> Any:
        """
        Evaluate expressions in the given value and optionally convert to target type.

        Args:
            value: The value to evaluate (only strings are processed)
            target_type: Optional target type for scalar conversion (int, float, bool)

        Returns:
            The evaluated value, optionally converted to the target type
        """
        # Only process string values
        if not isinstance(value, str):
            return value

        evaluated = cls._evaluate_string(value)

        # If target type is specified and it's a scalar type, try conversion
        if target_type and target_type in (int, float, bool):
            return cls._convert_to_scalar(evaluated, target_type)

        return evaluated

    @classmethod
    def _evaluate_string(cls, value: str) -> str:
        """
        Evaluate all expressions in a string value using substitution.

        Args:
            value: The string value to evaluate

        Returns:
            The string with all expressions substituted

        Raises:
            MissingEnvironmentVariableError: If an environment variable is required
                                           but not defined and no default is provided
        """

        def replace_env_expression(match):
            """Replace a single environment variable expression."""
            var_name = match.group(1)
            default_value = match.group(2)

            # Check if environment variable exists
            if var_name in os.environ:
                return os.environ[var_name]
            elif default_value is not None:
                # Default was provided in the expression (could be empty string)
                return default_value
            else:
                # No default provided and variable doesn't exist
                raise MissingEnvironmentVariableError(
                    f"Environment variable '{var_name}' is required but not defined. "
                    f"Either set the environment variable or provide a default value in the expression."
                )

        # Substitute all environment variable expressions
        return cls._env_pattern.sub(replace_env_expression, value)

    @classmethod
    def _convert_to_scalar(cls, value: str, target_type: type) -> Any:
        """
        Convert a string value to the target scalar type if possible.

        Args:
            value: The string value to convert
            target_type: The target type (int, float, or bool)

        Returns:
            The converted value, or the original string if conversion fails
        """
        try:
            if target_type is bool:
                # Handle boolean conversion
                lower = value.lower()
                if lower in ("true", "1", "yes", "on"):
                    return True
                elif lower in ("false", "0", "no", "off"):
                    return False
                else:
                    # If it doesn't look like a boolean, keep as string
                    return value
            elif target_type is int:
                # Only convert if it looks like an integer
                if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                    return int(value)
                else:
                    return value
            elif target_type is float:
                # Try to convert to float
                return float(value)
        except ValueError:
            # If conversion fails, return the original string
            pass

        return value
