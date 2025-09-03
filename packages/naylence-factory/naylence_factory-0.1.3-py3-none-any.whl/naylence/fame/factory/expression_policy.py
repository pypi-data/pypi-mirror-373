from enum import Enum


class ExpressionEvaluationPolicy(Enum):
    """
    Policy for handling expression evaluation in ResourceConfig.

    Controls whether expressions like ${env:VAR:default} should be:
    - EVALUATE: Processed and replaced with their resolved values
    - LITERAL: Left as-is (literal strings)
    - ERROR: Raise an error when expressions are encountered
    """

    EVALUATE = "evaluate"
    LITERAL = "literal"
    ERROR = "error"
