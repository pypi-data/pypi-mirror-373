"""
Provide instruments communicating via iServer.

Suitable for Newport and Omega devices
"""

from .i800 import I800

__all__ = ["I800"]
