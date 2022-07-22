"""
Define exceptions used by the rend system
"""


class RendBaseException(Exception):
    """
    Base Exception for the render system
    """


class RendPipeException(RendBaseException):
    """
    Exception raised when a render pipe is not define or available
    """


class RenderException(RendBaseException):
    """
    Exception raised when a renderer raises an explicit error
    """
