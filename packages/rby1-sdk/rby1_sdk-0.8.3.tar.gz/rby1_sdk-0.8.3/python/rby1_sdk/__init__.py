from __future__ import annotations
import sys

from ._bindings import *
from ._bindings import __version__

# from ._robot_command import *

from typing import overload


@overload
def create_robot(address: str, model_name: str) -> Robot_A: ...
@overload
def create_robot(address: str, model_name: str) -> Robot_M: ...
@overload
def create_robot(address: str, model_name: str) -> Robot_T5: ...
@overload
def create_robot(address: str, model_name: str) -> Robot_UB: ...


def create_robot(address: str, model_name: str):
    """
    create_robot(address, model_name)
    
    Create a robot instance for a specific RB-Y1 model.

    This function is a thin wrapper around the internal
    `_bindings._create_robot` and provides IDE/type checker
    support via overloads.

    Parameters
    ----------
    address : str
        Network address of the robot, e.g. "192.168.1.100:50051".
    model_name : str
        Robot model identifier (case-insensitive). Supported values are:
        - "a"   → Robot_A
        - "m"   → Robot_M
        - "t5"  → Robot_T5
        - "ub"  → Robot_UB

    Returns
    -------
    Robot_A or Robot_M or Robot_T5 or Robot_UB
        Configured robot instance corresponding to the specified model.

    Raises
    ------
    RuntimeError
        If the model name is unknown or unsupported.

    See Also
    --------
    _bindings.create_robot_a : Directly create a Robot A instance.
    _bindings.create_robot_m : Directly create a Robot M instance.
    _bindings.create_robot_t5 : Directly create a Robot T5 instance.
    _bindings.create_robot_ub : Directly create a Robot UB instance.

    Examples
    --------
    >>> from rby1_sdk import create_robot
    >>> robot = create_robot("192.168.1.100:50051", "a")

    >>> robot = create_robot("192.168.1.100:50051", "ub")
    """
    return _bindings._create_robot(address, model_name)
