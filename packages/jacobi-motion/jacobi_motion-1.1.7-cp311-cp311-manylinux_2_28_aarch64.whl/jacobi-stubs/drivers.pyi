"""
Drivers sub-module of the Jacobi Motion Library.
"""
from __future__ import annotations
import typing
__all__: list[str] = ['RobotDriverType', 'load_robot_driver']
class RobotDriverType:
    """
    Enumeration of available robot driver types.
    """
    ABB: typing.ClassVar[str] = 'abb'
    ABBIRC5: typing.ClassVar[str] = 'abb_irc5'
    ABBOmniCore: typing.ClassVar[str] = 'abb_omnicore'
    Fanuc: typing.ClassVar[str] = 'fanuc'
    Simulated: typing.ClassVar[str] = 'simulated'
    Universal: typing.ClassVar[str] = 'universal'
    Yaskawa: typing.ClassVar[str] = 'yaskawa'
def load_robot_driver(type: str) -> tuple[typing.Any, typing.Any, typing.Any]:
    ...
