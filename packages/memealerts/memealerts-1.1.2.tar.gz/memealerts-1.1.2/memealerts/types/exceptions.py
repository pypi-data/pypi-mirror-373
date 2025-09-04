class MAError(Exception):
    """Memealerts error"""


class MATokenExpiredError(MAError):
    """Token is already expired."""


class MAUserNotFoundError(MAError):
    """User not found."""


class MANotAvailableError(MAError):
    """Memealerts is not available."""
