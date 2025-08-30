"""
Robots sub-module of the Jacobi Library.
"""
from __future__ import annotations
import jacobi
import os
import pybind11_stubgen.typing_ext
import typing
__all__: list[str] = ['ABBGoFaCRB1500010', 'ABBIRB1200590', 'ABBIRB1200770', 'ABBIRB130010115', 'ABBIRB1300714', 'ABBIRB1600612', 'ABBIRB260012185', 'ABBIRB460060205', 'ABBIRB5720125300', 'ABBIRB6640185280', 'ABBIRB6700150320', 'ABBIRB6700155285', 'ABBYuMiIRB14000', 'CustomRobot', 'DualArm', 'FanucCRX30iA', 'FanucLR10iA10', 'FanucLRMate200iD7L', 'FanucM20iB25', 'FanucM20iD25', 'FanucM710iC45M', 'FanucM710iC50', 'FlexivRizon10', 'FlexivRizon10S', 'FlexivRizon4', 'FlexivRizon4S', 'FrankaPanda', 'KinovaGen37DoF', 'KukaIiwa7', 'KukaKR6R700sixx', 'KukaKR70R2100', 'MecademicMeca500', 'UfactoryXArm7', 'UniversalUR10', 'UniversalUR10e', 'UniversalUR20', 'UniversalUR5e', 'YaskawaGP12', 'YaskawaGP180', 'YaskawaGP180120', 'YaskawaGP50', 'YaskawaHC10', 'YaskawaHC20']
class ABBGoFaCRB1500010(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB1200590(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB1200770(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB130010115(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB1300714(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB1600612(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB260012185(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB460060205(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB5720125300(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB6640185280(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB6700150320(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBIRB6700155285(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class ABBYuMiIRB14000(DualArm):
    """
    """
    class Arm(jacobi.RobotArm):
        """
        """
    def __init__(self) -> None:
        ...
class CustomRobot(jacobi.RobotArm):
    """
    A custom robot arm that can be loaded from a URDF file.
    
    The `CustomRobot` class extends the `RobotArm` class and provides the
    functionality to load a robot's configuration from a URDF (Unified
    Robot Description Format) file. It also includes methods for handling
    inverse kinematics and filtering relevant configurations.
    """
    link_translations: list[jacobi.Frame]
    map_dofs_to_joints: list[int]
    map_joints_to_dofs: list[int]
    @staticmethod
    def load_from_urdf_file(file: os.PathLike, base_link: str = 'base_link', end_link: str = 'flange') -> CustomRobot:
        """
        Load the robot from a URDF file
        
        Loads a custom robot from a *.urdf file, and sets the robot arm to the
        kinematic chain between the given base_link and the end_link.
        
        Parameter ``file``:
            The path to the URDF file.
        
        Parameter ``base_link``:
            The name of the base link in the URDF.
        
        Parameter ``end_link``:
            The name of the end link in the URDF.
        
        Returns:
            A shared pointer to the loaded robot.
        """
    def __init__(self, joint_types: list[jacobi.JointType]) -> None:
        ...
    @property
    def child(self) -> jacobi.RobotArm:
        """
        Possible child robot.
        """
    @child.setter
    def child(self, arg0: jacobi.RobotArm) -> None:
        ...
    @property
    def config_joint_names(self) -> list[str]:
        """
        Names of the joints corresponding to a specific joint configuration.
        """
    @config_joint_names.setter
    def config_joint_names(self, arg0: list[str]) -> None:
        ...
    @property
    def joint_axes(self) -> list[typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]]:
        """
        Axes of the joints in the robot.
        """
    @joint_axes.setter
    def joint_axes(self, arg0: list[typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]]) -> None:
        ...
    @property
    def joint_names(self) -> list[str]:
        """
        Names of the joints in the robot.
        """
    @joint_names.setter
    def joint_names(self, arg0: list[str]) -> None:
        ...
class DualArm(jacobi.Robot):
    """
    """
    def __init__(self, left: jacobi.RobotArm, right: jacobi.RobotArm) -> None:
        ...
    @property
    def left(self) -> jacobi.RobotArm:
        """
        The left arm of the robot
        """
    @property
    def right(self) -> jacobi.RobotArm:
        """
        The right arm of the robot
        """
class FanucCRX30iA(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FanucLR10iA10(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FanucLRMate200iD7L(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FanucM20iB25(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FanucM20iD25(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FanucM710iC45M(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FanucM710iC50(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FlexivRizon10(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FlexivRizon10S(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FlexivRizon4(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FlexivRizon4S(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class FrankaPanda(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class KinovaGen37DoF(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class KukaIiwa7(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class KukaKR6R700sixx(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class KukaKR70R2100(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class MecademicMeca500(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class UfactoryXArm7(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class UniversalUR10(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class UniversalUR10e(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class UniversalUR20(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class UniversalUR5e(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class YaskawaGP12(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class YaskawaGP180(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class YaskawaGP180120(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class YaskawaGP50(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class YaskawaHC10(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
class YaskawaHC20(jacobi.RobotArm):
    """
    """
    def __init__(self) -> None:
        ...
