"""
Provide basic classes to operate scopes
"""

from .sds1104x import SDS1104X
from .sds2304x import SDS2304X
from .sds800xhd import SDS800XHD
from .rigolds1054z import RigolDS1054z

__all__ = ["SDS1104X", "SDS2304X", "SDS800XHD", "RigolDS1054z"]
