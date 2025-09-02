"""Exceptions for the Sanitana Eden project.

This module defines custom exception classes used to handle errors related to device connections and other project-specific issues.
"""


class DeviceConnectionError(Exception):
    """Exception raised when a connection to a device fails.

    This error should be raised when the application is unable to establish or maintain
    communication with a device, such as due to network issues, device unavailability,
    or authentication failures.
    """
