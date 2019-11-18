"""
Mindsay SDK utilities
"""
import datetime

from mindsay_sdk.exc import ValidationError


def verify_prompt(prompt: str, expected: str = "y"):
    """
    Prompts a message to the user waiting for an input to be verified
    with the expected one.  Raise a ValidationError if they do not
    match.
    """
    input_ = input(prompt)
    if input_ != expected:
        raise ValidationError(f"Expected {expected}, got {input_}")


def parse_timestamp(string_timestamp: str) -> datetime.datetime:
    """Parse a string timestamp from the BOS to datetime"""
    return datetime.datetime.strptime(string_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
