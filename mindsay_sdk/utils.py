"""
Mindsay SDK utilities
"""
from mindsay_sdk.exc import ValidationError


def verify_prompt(prompt: str, expected: str = "y"):
    """
    Prompts a message to the user waiting for an input to be verified
    with the expected one.  Raise a ValidationError if they do not
    match.
    """
    input_ = input(prompt)
    if input_ != expected:
        raise ValidationError("Expected {}, got {}".format(expected, input_))
