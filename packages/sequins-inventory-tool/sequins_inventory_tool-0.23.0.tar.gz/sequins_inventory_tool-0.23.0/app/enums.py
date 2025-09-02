"""Enums used in the application."""

from enum import StrEnum


class Profile(StrEnum):
    """Enum for the different profiles."""

    LOCAL = 'local'
    DEV = 'dev'
    STAGING = 'staging'
    PRODUCTION = 'production'
