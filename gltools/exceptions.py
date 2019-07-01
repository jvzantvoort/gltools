"""Exceptions for the gltools package"""

__author__ = "John van Zantvoort"
__email__ = "john.van.zantvoort@proxy.nl"
__copyright__ = "John van Zantvoort"


class GLToolsException(Exception):
    """

    :param message: the error message
    :returns: Formatted exception message
    """
    def __init__(self, message):
        self.message = message
        Exception.__init__(self)

    def __str__(self):
        return "GLTools Error %s" % self.message
