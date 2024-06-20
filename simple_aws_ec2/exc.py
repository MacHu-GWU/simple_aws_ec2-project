# -*- coding: utf-8 -*-


class StatusError(ValueError):
    """
    Exception raised when an unexpected status is encountered.
    """


class CannotDetectOSTypeError(TypeError):
    """
    raised when unable to use the name and description to detect the OS type
    of the AMI.
    """

    pass
