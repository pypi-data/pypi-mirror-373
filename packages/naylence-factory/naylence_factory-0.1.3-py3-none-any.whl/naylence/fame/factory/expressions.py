"""
Expression composition utilities for ResourceConfig.

Provides helper functions to create expressions in a more readable way
than manually constructing the ${env:VAR:default} syntax.
"""

from typing import Optional


class MissingEnvironmentVariableError(Exception):
    """Raised when an environment variable is required but not defined."""

    pass


class Expressions:
    """
    Factory class for creating expression strings used in ResourceConfig.

    Provides static methods to create various types of expressions in a readable way.
    """

    @staticmethod
    def env(var_name: str, default: Optional[str] = None) -> str:
        """
        Create an environment variable expression.

        Args:
            var_name: The name of the environment variable
            default: Optional default value if the environment variable is not set.
                    If not provided and the environment variable is not defined during evaluation,
                    MissingEnvironmentVariableError will be raised by ExpressionEvaluator.

        Returns:
            A formatted expression string like ${env:VAR:default}

        Examples:
            Expressions.env("AUTH_ISSUER") -> "${env:AUTH_ISSUER}"
            Expressions.env("AUTH_ISSUER", "https://auth.dev.local") -> "${env:AUTH_ISSUER:https://auth.dev.local}"
            Expressions.env("PORT", "8080") -> "${env:PORT:8080}"
        """
        if default is None:
            return f"${{env:{var_name}}}"
        else:
            return f"${{env:{var_name}:{default}}}"

    @staticmethod
    def config(key: str, default: Optional[str] = None) -> str:
        """
        Create a configuration value expression (placeholder for future implementation).

        Args:
            key: The configuration key
            default: Optional default value if the configuration key is not set

        Returns:
            A formatted expression string like ${config:KEY:default}

        Note:
            This is a placeholder for future config expression support.
            Currently not implemented in ExpressionEvaluator.

        Examples:
            Expressions.config("database.host") -> "${config:database.host}"
            Expressions.config("database.port", "5432") -> "${config:database.port:5432}"
        """
        if default is None:
            return f"${{config:{key}}}"
        else:
            return f"${{config:{key}:{default}}}"

    @staticmethod
    def literal(value: str) -> str:
        """
        Return a literal string value (no expression).

        This is mainly for consistency when mixing literal and expression values
        in configuration dictionaries, making it clear what's an expression vs literal.

        Args:
            value: The literal string value

        Returns:
            The same string value unchanged

        Examples:
            Expressions.literal("https://api.example.com") -> "https://api.example.com"
        """
        return value

    # Convenience aliases as class methods
    environment = env
    setting = config


# Backward compatibility - keep the function-based API available
def env(var_name: str, default: Optional[str] = None) -> str:
    """Backward compatibility function. Use Expressions.env() instead."""
    return Expressions.env(var_name, default)


def config(key: str, default: Optional[str] = None) -> str:
    """Backward compatibility function. Use Expressions.config() instead."""
    return Expressions.config(key, default)


def literal(value: str) -> str:
    """Backward compatibility function. Use Expressions.literal() instead."""
    return Expressions.literal(value)


# Convenience aliases
environment = env  # Alternative name for env()
setting = config  # Alternative name for config()
