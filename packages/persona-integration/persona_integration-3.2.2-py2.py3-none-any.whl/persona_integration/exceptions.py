"""
Exceptions for persona_integration.
"""


class InvalidStatusTransition(Exception):
    """
    This exception is raised if a status transition is not valid.
    """


class PersonaCannotRegisterAttempt(Exception):
    """
    Raised when a Persona cannot register an attempt for any reason.
    """
