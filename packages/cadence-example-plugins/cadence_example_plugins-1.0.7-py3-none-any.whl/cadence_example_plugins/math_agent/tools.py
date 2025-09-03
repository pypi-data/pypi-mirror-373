"""Math Agent Tools using Cadence SDK."""

from typing import Union

from cadence_sdk import tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of the two numbers
    """
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Subtract second number from first number.

    Args:
        a: First number
        b: Second number

    Returns:
        Difference of the two numbers
    """
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of the two numbers
    """
    return a * b


@tool
def divide(a: Union[int, float], b: Union[int, float]) -> Union[float, str]:
    """Divide first number by second number.

    Args:
        a: First number (dividend)
        b: Second number (divisor)

    Returns:
        Quotient of the division or error message
    """
    if b == 0:
        return "Error: Division by zero is undefined"
    return float(a) / float(b)


@tool
def power(a: int, b: int) -> Union[int, str]:
    """Raise first number to the power of second number.

    Args:
        a: Base number
        b: Exponent

    Returns:
        Result of a raised to power b or error message
    """
    try:
        if abs(a) > 1000 and abs(b) > 10:
            return "Error: Calculation too large (base > 1000 and exponent > 10)"
        result = a**b
        return result
    except OverflowError:
        return "Error: Result too large to calculate"


@tool
def modulo(a: int, b: int) -> Union[int, str]:
    """Calculate remainder when first number is divided by second.

    Args:
        a: Dividend
        b: Divisor

    Returns:
        Remainder of the division or error message
    """
    if b == 0:
        return "Error: Modulo by zero is undefined"
    return a % b


math_tools = [add, subtract, multiply, divide, power, modulo]
