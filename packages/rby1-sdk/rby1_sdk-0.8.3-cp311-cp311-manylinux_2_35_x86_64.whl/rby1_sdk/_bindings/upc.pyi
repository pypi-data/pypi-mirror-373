"""

Module for controlling and communicating with devices.

Provides utilities for controlling master arm and other devices.
"""
from __future__ import annotations
import _bindings
import numpy
import pybind11_stubgen.typing_ext
import typing
__all__: list[str] = ['GripperDeviceName', 'MasterArm', 'MasterArmDeviceName', 'initialize_device']
class MasterArm:
    """
    
    Master arm control interface.
    
    This class provides control interface for a master arm device
    with 14 degrees of freedom, including joint control, gravity compensation,
    and button/trigger input handling.
    
    Attributes
    ----------
    DOF : int
        Number of degrees of freedom (14).
    DeviceCount : int
        Total number of devices including tools (16).
    TorqueScaling : float
        Torque scaling factor for gravity compensation (0.5).
    MaximumTorque : float
        Maximum allowed torque in Nm (4.0).
    RightToolId : int
        Device ID for right tool (0x80).
    LeftToolId : int
        Device ID for left tool (0x81).
    """
    class ControlInput:
        """
        
        Master arm control input.
        
        This class represents the control input for the master arm
        including target operating modes, positions, and torques.
        
        Attributes
        ----------
        target_operating_mode : numpy.ndarray
            Target operating modes for each joint, shape (14,), dtype=int32.
        target_position : numpy.ndarray
            Target positions for each joint, shape (14,), dtype=float64.
        target_torque : numpy.ndarray
            Target torques for each joint, shape (14,), dtype=float64.
        """
        def __init__(self) -> None:
            """
            Construct a ``ControlInput`` instance with default values.
            """
        @property
        def target_operating_mode(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.int32]]:
            """
            Target operating modes for each joint.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=int32. Target operating mode for each joint.
            """
        @target_operating_mode.setter
        def target_operating_mode(self, arg1: numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.int32]]) -> None:
            ...
        @property
        def target_position(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Target positions for each joint.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Target position for each joint in radians.
            """
        @target_position.setter
        def target_position(self, arg1: numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
            ...
        @property
        def target_torque(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Target torques for each joint.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Target torque for each joint in Nm.
            """
        @target_torque.setter
        def target_torque(self, arg1: numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]) -> None:
            ...
    class State:
        """
        
        Master arm state information.
        
        This class represents the current state of the master arm
        including joint positions, velocities, torques, and tool states.
        
        Attributes
        ----------
        q_joint : numpy.ndarray
            Joint positions, shape (14,), dtype=float64.
        qvel_joint : numpy.ndarray
            Joint velocities, shape (14,), dtype=float64.
        torque_joint : numpy.ndarray
            Joint torques, shape (14,), dtype=float64.
        gravity_term : numpy.ndarray
            Gravity compensation terms, shape (14,), dtype=float64.
        operating_mode : numpy.ndarray
            Operating modes for each joint, shape (14,), dtype=int32.
        button_right : ButtonState
            Right tool button and trigger state.
        button_left : ButtonState
            Left tool button and trigger state.
        T_right : numpy.ndarray
            Right tool transformation matrix, shape (4, 4), dtype=float64.
        T_left : numpy.ndarray
            Left tool transformation matrix, shape (4, 4), dtype=float64.
        """
        def __init__(self) -> None:
            """
            Construct a ``State`` instance with default values.
            """
        def __repr__(self) -> str:
            ...
        def __str__(self) -> str:
            ...
        @property
        def T_left(self) -> numpy.ndarray[tuple[typing.Literal[4], typing.Literal[4]], numpy.dtype[numpy.float64]]:
            """
            Left tool transformation matrix.
            
            Type
            ----
            numpy.ndarray
                Shape (4, 4), dtype=float64. Homogeneous transformation matrix.
            """
        @property
        def T_right(self) -> numpy.ndarray[tuple[typing.Literal[4], typing.Literal[4]], numpy.dtype[numpy.float64]]:
            """
            Right tool transformation matrix.
            
            Type
            ----
            numpy.ndarray
                Shape (4, 4), dtype=float64. Homogeneous transformation matrix.
            """
        @property
        def button_left(self) -> _bindings.DynamixelBus.ButtonState:
            """
            Left tool button and trigger state.
            
            Type
            ----
            ButtonState
                Button and trigger state for left tool.
            """
        @property
        def button_right(self) -> _bindings.DynamixelBus.ButtonState:
            """
            Right tool button and trigger state.
            
            Type
            ----
            ButtonState
                Button and trigger state for right tool.
            """
        @property
        def gravity_term(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Gravity compensation terms.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Gravity compensation torques in Nm.
            """
        @property
        def operating_mode(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.int32]]:
            """
            Operating modes for each joint.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=int32. Operating mode for each joint.
            """
        @property
        def q_joint(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Joint positions.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Joint positions in radians.
            """
        @property
        def qvel_joint(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Joint velocities.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Joint velocities in rad/s.
            """
        @property
        def target_position(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Last joint target positions.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Joint target positions in radians.
            """
        @property
        def torque_joint(self) -> numpy.ndarray[tuple[typing.Literal[14], typing.Literal[1]], numpy.dtype[numpy.float64]]:
            """
            Joint torques.
            
            Type
            ----
            numpy.ndarray
                Shape (14,), dtype=float64. Joint torques in Nm.
            """
    DOF: typing.ClassVar[int] = 14
    DeviceCount: typing.ClassVar[int] = 16
    LeftToolId: typing.ClassVar[int] = 129
    MaximumTorque: typing.ClassVar[float] = 4.0
    RightToolId: typing.ClassVar[int] = 128
    TorqueScaling: typing.ClassVar[float] = 0.5
    def __init__(self, dev_name: str = '/dev/rby1_master_arm') -> None:
        """
        Construct a ``MasterArm`` instance.
        
        Parameters
        ----------
        dev_name : str, optional
            Device name. Default is ``/dev/rby1_master_arm``'.
        """
    def __repr__(self: MasterArm.ControlInput) -> str:
        ...
    def __str__(self: MasterArm.ControlInput) -> str:
        ...
    def disable_torque(self) -> bool:
        """
        disable_torque()
        
        Disable torque of motors
        """
    def enable_torque(self) -> bool:
        """
        enable_torque()
        
        Enable torque of motors
        """
    def initialize(self, verbose: bool = False) -> list[int]:
        """
        Initialize the master arm and detect active devices.
        
        Parameters
        ----------
        verbose : bool, optional
            Whether to print verbose output. Default is False.
        
        Returns
        -------
        list[int]
            List of active device IDs.
        """
    def set_control_period(self, control_period: float) -> None:
        """
        set_control_period(control_period)
        
        Set the control update period.
        
        Parameters
        ----------
        control_period : float
            Control period in seconds.
        """
    def set_model_path(self, model_path: str) -> None:
        """
        Set the path to the URDF model file.
        
        Parameters
        ----------
        model_path : str
            Path to the URDF model file.
        """
    def set_torque_constant(self, torque_constant: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(14)]) -> None:
        """
        Set torque constant.
        
        Parameters
        ----------
        torque_constant : numpy.ndarray (14, )
        
        Parameters
        ----------
        model_path : str
            Path to the URDF model file.
        """
    def start_control(self, control: typing.Callable[[MasterArm.State], MasterArm.ControlInput]) -> bool:
        """
        Start the control loop.
        
        Parameters
        ----------
        control : callable, optional
            Control callback function that takes State and returns ControlInput.
            If None, no control is applied.
        
        Returns
        -------
        bool
        """
    def stop_control(self, torque_disable: bool = False) -> bool:
        """
        stop_control(torque_disable)
        
        Stop the control loop.
        
        Parameters
        ----------
        torque_disable : bool, optional
        
        Returns
        -------
        bool
        """
def initialize_device(device_name: str) -> None:
    """
    initialize_device(device_name)
    
    Initialize a device with the given name.
    
    Sets the latency timer of the device to 1.
    
    Args:
        device_name (str): Name of the device to initialize (e.g., '/dev/ttyUSB0', '/dev/rby1_master_arm').
    
    Returns:
        bool: True if device initialized successfully, False otherwise.
    """
GripperDeviceName: str = '/dev/rby1_gripper'
MasterArmDeviceName: str = '/dev/rby1_master_arm'
