"""
Exceptions sub-module of the Jacobi Library.
"""
from __future__ import annotations
__all__: list[str] = ['JacobiError', 'JacobiLicenseError', 'JacobiLoadProjectError']
class JacobiError(Exception):
    pass
class JacobiLicenseError(JacobiError):
    pass
class JacobiLoadProjectError(JacobiError):
    pass
