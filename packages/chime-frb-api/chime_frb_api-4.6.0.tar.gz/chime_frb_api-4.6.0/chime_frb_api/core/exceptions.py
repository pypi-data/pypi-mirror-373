#!/usr/bin/env python

"""
CHIME/FRB API Exceptions
"""


class APIError(Exception):
    """
    CHIME/FRB API Error
    """


class ConfigurationError(APIError):
    """
    Configuration error ocurred
    """


class TokenError(APIError):
    """
    Error with CHIME/FRB Tokens
    """
