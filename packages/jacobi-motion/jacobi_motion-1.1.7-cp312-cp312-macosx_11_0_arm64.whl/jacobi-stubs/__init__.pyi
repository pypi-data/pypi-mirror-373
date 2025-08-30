"""
Next-Generation Motion Planning for Robots. Calculates highly time-optimized, collision-free, and jerk-constrained motions in less than 1ms.
"""
from __future__ import annotations
from jacobi.exceptions import JacobiError
import os
import pybind11_stubgen.typing_ext
import typing
from . import drivers
from . import exceptions
from . import robots
__all__: list[str] = ['BimanualMotion', 'Box', 'Camera', 'CameraStream', 'Capsule', 'CartesianRegion', 'CartesianRegionBound', 'CartesianWaypoint', 'CircularPath', 'Color', 'Continuous', 'Convex', 'Cylinder', 'Depth', 'DepthMap', 'DynamicRobotTrajectory', 'Element', 'Environment', 'FileReference', 'Fixed', 'Frame', 'FutureExpectedTrajectory', 'Intrinsics', 'JacobiError', 'JointType', 'LinearMotion', 'LinearPath', 'LinearSection', 'LowLevelMotion', 'MeshFile', 'Motion', 'MultiRobotLinearSection', 'MultiRobotPoint', 'Obstacle', 'Path', 'PathCommand', 'PathFollowingMotion', 'Planner', 'PlanningError', 'PointCloud', 'Prismatic', 'Region', 'ReturnCode', 'Revolute', 'Robot', 'RobotArm', 'Sampler', 'Sphere', 'State', 'Studio', 'Trainer', 'Trajectory', 'Twist', 'Waypoint', 'activate_license', 'drivers', 'exceptions', 'robots', 'start_studio_daemon', 'start_telemetry_daemon']
class BimanualMotion:
    """
    Represents a request for a collision-free point-to-point bimanual
    motion for dual-arm robots.
    
    The BimanualMotion class provides an interface for general point-to-
    point motion planning for dual-arm robots with arbitrary waypoints,
    linear approach and retraction, and task constraints. It includes
    parameters for the motion name, robot, start and goal points, and
    additional settings for motion planning, such as intermediate
    waypoints, setting if the bimanual motion should be coordinated, and
    soft failure handling.
    """
    @typing.overload
    def __init__(self, arm_left: RobotArm, arm_right: RobotArm, start: MultiRobotPoint, goal: MultiRobotPoint) -> None:
        """
        Construct a BimanualMotion with left and right robot arms, start and
        goal point.
        
        Parameter ``arm_left``:
            The left robot arm for the motion.
        
        Parameter ``arm_right``:
            The right robot arm for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, name: str, arm_left: RobotArm, arm_right: RobotArm, start: MultiRobotPoint, goal: MultiRobotPoint) -> None:
        """
        Construct a BimanualMotion with a name, left and right robot arms,
        start and goal point.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``arm_left``:
            The left robot arm for the motion.
        
        Parameter ``arm_right``:
            The right robot arm for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, robot: ..., start: MultiRobotPoint, goal: MultiRobotPoint) -> None:
        """
        Construct a BimanualMotion with a robot, start and goal point.
        
        Parameter ``robot``:
            The dual-arm robot for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, name: str, robot: ..., start: MultiRobotPoint, goal: MultiRobotPoint) -> None:
        """
        Construct a BimanualMotion with a name, robot, start and goal point.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``robot``:
            The dual-arm robot for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @property
    def goal(self) -> MultiRobotPoint:
        """
        Goal point of the motion for both arms.
        """
    @goal.setter
    def goal(self, arg0: MultiRobotPoint) -> None:
        ...
    @property
    def is_coordinated(self) -> bool:
        """
        Flag to indicate if the motion is coordinated, in which case the
        follower arm moves with a constant offset to the leader arm.
        """
    @is_coordinated.setter
    def is_coordinated(self, arg0: bool) -> None:
        ...
    @property
    def leader_arm(self) -> RobotArm:
        """
        The leader arm for the coordinated motion. Left arm is used by default
        if this variable is not set.
        """
    @leader_arm.setter
    def leader_arm(self, arg0: RobotArm) -> None:
        ...
    @property
    def linear_approach(self) -> MultiRobotLinearSection | None:
        """
        Optional relative linear cartesian motion for approaching the goal
        pose, specified for one or both arms.
        """
    @linear_approach.setter
    def linear_approach(self, arg0: MultiRobotLinearSection | None) -> None:
        ...
    @property
    def linear_retraction(self) -> MultiRobotLinearSection | None:
        """
        Optional relative linear cartesian motion for retracting from the
        start pose, specified for one or both arms.
        """
    @linear_retraction.setter
    def linear_retraction(self, arg0: MultiRobotLinearSection | None) -> None:
        ...
    @property
    def name(self) -> str:
        """
        The unique name of the bimanual motion.
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def path_length_loss_weight(self) -> float:
        """
        Weight of the loss minimizing the path length of the trajectory.
        """
    @path_length_loss_weight.setter
    def path_length_loss_weight(self, arg0: float) -> None:
        ...
    @property
    def robot(self) -> ...:
        """
        The dual-arm robot for the bimanual motion (e.g. defines the
        kinematics and the joint limits).
        """
    @property
    def start(self) -> MultiRobotPoint:
        """
        Start point of the motion for both arms.
        """
    @start.setter
    def start(self, arg0: MultiRobotPoint) -> None:
        ...
    @property
    def waypoints(self) -> list[MultiRobotPoint]:
        """
        Intermediate waypoints for both arms that the motion passes through
        exactly. The list of waypoints is limited to less than four.
        """
    @waypoints.setter
    def waypoints(self, arg0: list[MultiRobotPoint]) -> None:
        ...
class Box:
    """
    A box collision object.
    
    The Box struct represents a simple 3D rectangular collision object. It
    is defined by its dimensions along the x, y, and z axes, which
    correspond to the width, depth, and height of the box, respectively.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, x: float, y: float, z: float) -> None:
        """
        Construct a box of size x, y, z along the respective axes.
        
        Parameter ``x``:
            The width of the box along the x-axis.
        
        Parameter ``y``:
            The depth of the box along the y-axis.
        
        Parameter ``z``:
            The height of the box along the z-axis.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def x(self) -> float:
        """
        Dimensions of the box [m]
        """
    @property
    def y(self) -> float:
        """
        Dimensions of the box [m]
        """
    @property
    def z(self) -> float:
        """
        Dimensions of the box [m]
        """
class Camera(Element):
    """
    Camera element
    
    The Camera class extends the Element class and includes parameters for
    the camera model and its intrinsic properties. The class allows for
    specifying the camera's model name, its intrinsics, and its position
    in 3D space.
    """
    def __init__(self, model: str, name: str, origin: Frame, intrinsics: Intrinsics) -> None:
        """
        Default constructor.
        """
    @property
    def intrinsics(self) -> Intrinsics:
        """
        The camera intrinsics
        """
    @intrinsics.setter
    def intrinsics(self, arg0: Intrinsics) -> None:
        ...
    @property
    def model(self) -> str:
        """
        The model name of the camera
        """
    @model.setter
    def model(self, arg0: str) -> None:
        ...
class CameraStream:
    """
    Stream types of a camera.
    
    The `CameraStream` enum class defines the types of data streams a
    camera can provide. It is used to specify whether a camera stream is
    for capturing color images or depth information.
    
    Members:
    
      Color : 
    
      Depth : 
    """
    Color: typing.ClassVar[CameraStream]  # value = <CameraStream.Color: 0>
    Depth: typing.ClassVar[CameraStream]  # value = <CameraStream.Depth: 1>
    __members__: typing.ClassVar[dict[str, CameraStream]]  # value = {'Color': <CameraStream.Color: 0>, 'Depth': <CameraStream.Depth: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Capsule:
    """
    A capsule collision object.
    
    The Capsule struct represents a simple 3D collision object shaped like
    a capsule (a cylinder with hemispherical ends). It is defined by its
    radius and length along the z-axis. Capsules are commonly used in
    collision detection due to their computational efficiency.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, radius: float, length: float) -> None:
        """
        Construct a capsule with the given radius and length.
        
        Parameter ``radius``:
            The radius of the capsule.
        
        Parameter ``length``:
            The length of the capsule along the z-axis.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def length(self) -> float:
        """
        Length of the capsule along the z-axis [m]
        """
    @property
    def radius(self) -> float:
        """
        Radius of the capsule [m]
        """
class CartesianRegion(Element):
    """
    A Cartesian-space region with possible minimum and maximum position,
    velocity, and/or acceleration values.
    
    The CartesianRegion class defines a region in Cartesian space with
    optional boundaries for position, velocity, and acceleration. It is
    used to describe constraints on a Cartesian region within which the
    robot end-effector operates. The region can also have an associated
    reference configuration.
    """
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, min_position: CartesianRegionBound, max_position: CartesianRegionBound, reference_config: list[float] | None = None) -> None:
        ...
    @typing.overload
    def __init__(self, min_position: CartesianRegionBound, max_position: CartesianRegionBound, min_velocity: CartesianRegionBound, max_velocity: CartesianRegionBound, reference_config: list[float] | None = None) -> None:
        ...
    @typing.overload
    def __init__(self, min_position: CartesianRegionBound, max_position: CartesianRegionBound, min_velocity: CartesianRegionBound, max_velocity: CartesianRegionBound, min_acceleration: CartesianRegionBound, max_acceleration: CartesianRegionBound, reference_config: list[float] | None = None) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def max_acceleration(self) -> CartesianRegionBound:
        """
        Maximum acceleration boundary of the region.
        """
    @max_acceleration.setter
    def max_acceleration(self, arg0: CartesianRegionBound) -> None:
        ...
    @property
    def max_position(self) -> CartesianRegionBound:
        """
        Maximum position boundary of the region.
        """
    @max_position.setter
    def max_position(self, arg0: CartesianRegionBound) -> None:
        ...
    @property
    def max_velocity(self) -> CartesianRegionBound:
        """
        Maximum velocity boundary of the region.
        """
    @max_velocity.setter
    def max_velocity(self, arg0: CartesianRegionBound) -> None:
        ...
    @property
    def min_acceleration(self) -> CartesianRegionBound:
        """
        Minimum acceleration boundary of the region.
        """
    @min_acceleration.setter
    def min_acceleration(self, arg0: CartesianRegionBound) -> None:
        ...
    @property
    def min_position(self) -> CartesianRegionBound:
        """
        Minimum position boundary of the region.
        """
    @min_position.setter
    def min_position(self, arg0: CartesianRegionBound) -> None:
        ...
    @property
    def min_velocity(self) -> CartesianRegionBound:
        """
        Minimum velocity boundary of the region.
        """
    @min_velocity.setter
    def min_velocity(self, arg0: CartesianRegionBound) -> None:
        ...
    @property
    def reference_config(self) -> list[float] | None:
        """
        Reference configuration for the region, if any.
        """
    @reference_config.setter
    def reference_config(self, arg0: list[float] | None) -> None:
        ...
class CartesianRegionBound:
    """
    The min or max boundary of a Cartesian region.
    
    The CartesianRegionBound struct represents the boundaries of a region
    in Cartesian space. It defines both positional (x, y, z) and
    orientational (gamma, alpha) limits. These boundaries are used to
    constrain the movement or state of an object within a specified
    region.
    """
    def __init__(self, x: float, y: float, z: float, gamma: float = 0.0, alpha: float = 0.0) -> None:
        ...
    @property
    def alpha(self) -> float:
        """
        The rotational component around the x-axis (roll).
        """
    @alpha.setter
    def alpha(self, arg0: float) -> None:
        ...
    @property
    def gamma(self) -> float:
        """
        The rotational component around the z-axis (yaw).
        """
    @gamma.setter
    def gamma(self, arg0: float) -> None:
        ...
    @property
    def x(self) -> float:
        """
        The x-coordinate of the boundary.
        """
    @x.setter
    def x(self, arg0: float) -> None:
        ...
    @property
    def y(self) -> float:
        """
        The y-coordinate of the boundary.
        """
    @y.setter
    def y(self, arg0: float) -> None:
        ...
    @property
    def z(self) -> float:
        """
        The z-coordinate of the boundary.
        """
    @z.setter
    def z(self, arg0: float) -> None:
        ...
class CartesianWaypoint(Element):
    """
    A Cartesian-space waypoint with possible position, velocity, and/or
    acceleration values.
    
    The CartesianWaypoint class represents a point in Cartesian space with
    associated position, velocity, and acceleration frames. It is used to
    define the robot state in Cartesian space at a specific instance, with
    optional reference joint positions for inverse kinematics.
    """
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, position: Frame, reference_config: list[float] | None = None) -> None:
        """
        Construct a Cartesian waypoint with given position and zero velocity
        and acceleration.
        
        Parameter ``position``:
            The position frame to initialize the waypoint.
        
        Parameter ``reference_config``:
            An optional joint configuration for inverse kinematics.
        """
    @typing.overload
    def __init__(self, position: Frame, velocity: Frame, reference_config: list[float] | None = None) -> None:
        """
        Construct a Cartesian waypoint with given position and velocity and
        zero acceleration.
        
        Parameter ``position``:
            The position frame to initialize the waypoint.
        
        Parameter ``velocity``:
            The velocity frame to initialize the waypoint.
        
        Parameter ``reference_config``:
            An optional joint configuration for inverse kinematics.
        """
    @typing.overload
    def __init__(self, position: Frame, velocity: Frame, acceleration: Frame, reference_config: list[float] | None = None) -> None:
        """
        Construct a Cartesian waypoint with given position, velocity, and
        acceleration.
        
        Parameter ``position``:
            The position frame to initialize the waypoint.
        
        Parameter ``velocity``:
            The velocity frame to initialize the waypoint.
        
        Parameter ``acceleration``:
            The acceleration frame to initialize the waypoint.
        
        Parameter ``reference_config``:
            An optional joint configuration for inverse kinematics.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def acceleration(self) -> Frame:
        """
        Frame of the acceleration.
        """
    @acceleration.setter
    def acceleration(self, arg0: Frame) -> None:
        ...
    @property
    def position(self) -> Frame:
        """
        Frame of the position.
        """
    @position.setter
    def position(self, arg0: Frame) -> None:
        ...
    @property
    def reference_config(self) -> list[float] | None:
        """
        An optional joint position that is used as a reference for inverse
        kinematics.
        """
    @reference_config.setter
    def reference_config(self, arg0: list[float] | None) -> None:
        ...
    @property
    def velocity(self) -> Frame:
        """
        Frame of the velocity.
        """
    @velocity.setter
    def velocity(self, arg0: Frame) -> None:
        ...
class CircularPath:
    """
    """
    @typing.overload
    def __init__(self, start: Frame, theta: float, center: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)], normal: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)], keep_tool_to_surface_orientation: bool = True) -> None:
        ...
    @typing.overload
    def __init__(self, start: Frame, goal: Frame, center: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)], keep_tool_to_surface_orientation: bool = True) -> None:
        ...
    @property
    def center(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
        The center of the circle.
        """
    @center.setter
    def center(self, arg0: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]) -> None:
        ...
    @property
    def keep_tool_to_surface_orientation(self) -> bool:
        """
        Whether to maintain the tool-to-surface orientation.
        """
    @keep_tool_to_surface_orientation.setter
    def keep_tool_to_surface_orientation(self, arg0: bool) -> None:
        ...
    @property
    def normal(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
        The normal of the plane in which to create a circular path.
        """
    @normal.setter
    def normal(self, arg0: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]) -> None:
        ...
    @property
    def start(self) -> Frame:
        """
        The start pose of the circular path.
        """
    @start.setter
    def start(self, arg0: Frame) -> None:
        ...
    @property
    def theta(self) -> float:
        """
        The rotation angle of the circular path [rad].
        """
    @theta.setter
    def theta(self, arg0: float) -> None:
        ...
class Convex:
    """
    A convex mesh collision object.
    
    The Convex struct represents a 3D convex mesh, often used for
    collision detection. It supports loading from files, direct vertex and
    triangle specification, and provides utility functions like bounding
    box computation.
    """
    @staticmethod
    def load_from_file(path: os.PathLike, scale: float | None = None) -> list[Convex]:
        """
        .. deprecated::
            Load convex objects from a file.
        
        Parameter ``path``:
            The path to the file (*.obj).
        
        Parameter ``scale``:
            Optional scale to apply when loading the object.
        
        Returns:
            A vector of Convex objects loaded from the file.
        """
    def __init__(self, vertices: list[typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]], triangles: list[typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(3)]]) -> None:
        ...
    @property
    def bounding_box_maximum(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
        Get the maximum bounding box corner.
        
        Returns:
            A 3D vector representing the maximum corner of the bounding box.
        """
    @property
    def bounding_box_minimum(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
        Get the minimum bounding box corner.
        
        Returns:
            A 3D vector representing the minimum corner of the bounding box.
        """
    @property
    def triangles(self) -> list[...]:
        ...
    @property
    def vertices(self) -> list[..., 3, 1, 0, 3, ...]:
        ...
class Cylinder:
    """
    A cylinder collision object.
    
    The Cylinder struct represents a 3D cylindrical collision object. It
    is defined by its radius and length along the z-axis.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, radius: float, length: float) -> None:
        """
        Construct a cylinder with the given radius and length.
        
        Parameter ``radius``:
            The radius of the cylinder.
        
        Parameter ``length``:
            The length of the cylinder along the z-axis.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def length(self) -> float:
        """
        Length of the cylinder along the z-axis [m].
        """
    @property
    def radius(self) -> float:
        """
        Radius of the cylinder [m].
        """
class DepthMap:
    """
    A depth map collision object.
    
    The DepthMap struct represents a 3D collision object based on a depth
    map, which is essentially a grid of depth values.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, depths: list[list[float]], x: float, y: float) -> None:
        """
        Construct a depth map with the given data.
        
        Parameter ``depths``:
            The matrix of depth values.
        
        Parameter ``x``:
            The size of the depth map along the x-axis.
        
        Parameter ``y``:
            The size of the depth map along the y-axis.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def depths(self) -> list[list[float]]:
        """
        Matrix containing the depth values at evenly spaced grid points.
        """
    @depths.setter
    def depths(self, arg0: list[list[float]]) -> None:
        ...
    @property
    def max_depth(self) -> float:
        """
        Maximum depth to check for collisions [m].
        
        This value sets the maximum depth that will be considered during
        collision checking. Any depth greater than this value will be ignored.
        The default value is 100 meters.
        """
    @property
    def x(self) -> float:
        """
        Size along the x-axis [m].
        """
    @property
    def y(self) -> float:
        """
        Size along the y-axis [m].
        """
class DynamicRobotTrajectory:
    """
    A trajectory executed by a robot, in particular used for dynamic
    collision checking.
    """
    def __init__(self, trajectory: Trajectory, robot: Robot, time_offset: float = 0.0) -> None:
        ...
    @property
    def robot(self) -> Robot:
        """
        The robot that executes the trajectory
        """
    @property
    def time_offset(self) -> float:
        """
        A time offset when the robot starts executing the trajectory relative
        to the planning time
        """
    @time_offset.setter
    def time_offset(self, arg0: float) -> None:
        ...
    @property
    def trajectory(self) -> Trajectory:
        """
        The execute trajectory
        """
    @trajectory.setter
    def trajectory(self, arg0: Trajectory) -> None:
        ...
class Element:
    """
    The base element of a scene
    
    The Element struct represents the base element of a scene, such as a
    robot, camera, or obstacle. It contains a name, pose, and tags that
    can be used to identify and categorize the element.
    """
    def get_parameter(self, tag: str) -> str | None:
        """
        Reads the value of a tag parameter `param=value`. Tags are case-
        insensitive.
        
        Parameter ``tag``:
            The tag to read the parameter from.
        
        Returns:
            std::optional<std::string> The value of the parameter if it
            exists, std::nullopt otherwise.
        """
    def has_tag(self, tag: str) -> bool:
        """
        Checks whether a tag is present on the element. Tags are case-
        insensitive.
        
        Parameter ``tag``:
            The tag to check for.
        
        Returns:
            bool True if the tag is present, false otherwise.
        """
    @property
    def name(self) -> str:
        """
        The unique name of the element, for display and identification.
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def origin(self) -> Frame:
        """
        Pose of the element, relative to the parent. Is called "base" for
        robots in Studio.
        """
    @origin.setter
    def origin(self, arg0: Frame) -> None:
        ...
    @property
    def tags(self) -> list[str]:
        """
        Given tags of the element, might be with a parameter `param=value`.
        """
    @tags.setter
    def tags(self, arg0: list[str]) -> None:
        ...
class Environment:
    """
    """
    studio: ...
    @staticmethod
    def carve_point_cloud(point_cloud: Obstacle, obstacle: Obstacle) -> None:
        """
        Carves (subtracts) an obstacle from a point cloud.
        
        This function removes all points from the point cloud that are in
        collision with the obstacle. The point cloud is modified in place. The
        function does not update the collision model and update_point_cloud()
        may be called afterwards.
        
        Parameter ``point_cloud``:
            The point cloud to carve the obstacle from.
        
        Parameter ``obstacle``:
            The obstacle to carve from the point cloud.
        """
    @typing.overload
    def __init__(self, robot: Robot, safety_margin: float = 0.0) -> None:
        """
        Create an environment with a controllable robot
        
        Parameter ``robot``:
            The robot to add to the environment.
        
        Parameter ``safety_margin``:
            The global safety margin for collision checking [m].
        """
    @typing.overload
    def __init__(self, robots: set[Robot], safety_margin: float = 0.0) -> None:
        """
        Create an environment with multiple robots
        
        Parameter ``robots``:
            The robots to add to the environment.
        
        Parameter ``safety_margin``:
            The global safety margin for collision checking [m].
        """
    @typing.overload
    def add_obstacle(self, obstacle: Obstacle) -> Obstacle:
        """
        Add an obstacle to the environment (and returns the pointer to it)
        
        Parameter ``obstacle``:
            The obstacle to add to the environment.
        
        Returns:
            The original shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: Box, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a box-shaped obstacle to the environment
        
        Parameter ``object``:
            The box-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: Capsule, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a capsule-shaped obstacle to the environment
        
        Parameter ``object``:
            The capsule-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: Cylinder, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a cylinder-shaped obstacle to the environment
        
        Parameter ``object``:
            The cylinder-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: DepthMap, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a depth map-shaped obstacle to the environment
        
        Parameter ``object``:
            The depth map-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: MeshFile, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a file obstacle to the environment
        
        Parameter ``object``:
            The file obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: PointCloud, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a point cloud obstacle to the environment
        
        Parameter ``object``:
            The point cloud obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, object: Sphere, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a sphere-shaped obstacle to the environment
        
        Parameter ``object``:
            The sphere-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: Box, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add an obstacle with a name to the environment
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The obstacle to add (of a specific type, e.g., Box, Capsule,
            etc.).
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: Capsule, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Overload for adding an obstacle with a name and various shapes
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The obstacle to add (of a specific type, e.g., Capsule, Convex,
            etc.).
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: Cylinder, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a cylinder-shaped obstacle with a name to the environment
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The cylinder-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: DepthMap, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a depth map-shaped obstacle with a name to the environment
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The depth map-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: MeshFile, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a file obstacle with a name to the environment
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The file obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: PointCloud, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a point cloud obstacle with a name to the environment
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The point cloud obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def add_obstacle(self, name: str, object: Sphere, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0) -> Obstacle:
        """
        Add a sphere-shaped obstacle with a name to the environment
        
        Parameter ``name``:
            The name to assign to the obstacle.
        
        Parameter ``object``:
            The sphere-shaped obstacle to add.
        
        Parameter ``origin``:
            The initial pose of the obstacle in the environment (default is
            Frame::Identity()).
        
        Parameter ``color``:
            The color of the obstacle in hexadecimal format (default is
            "000000").
        
        Parameter ``safety_margin``:
            The safety margin around the obstacle (default is 0.0).
        
        Returns:
            A shared pointer to the added obstacle.
        """
    @typing.overload
    def check_collision(self, robot: Robot, joint_position: list[float]) -> bool:
        """
        Check if a joint position is in collision
        
        Parameter ``robot``:
            The robot to check the joint position for.
        
        Parameter ``joint_position``:
            The joint position to check for collision.
        
        Returns:
            True if the joint position is in collision, false otherwise.
        """
    @typing.overload
    def check_collision(self, joint_position: list[float]) -> bool:
        """
        Check if a joint position is in collision
        
        Parameter ``joint_position``:
            The joint position to check for collision.
        
        Returns:
            True if the joint position is in collision, false otherwise.
        """
    @typing.overload
    def check_collision(self, robot: Robot, waypoint: CartesianWaypoint) -> bool:
        """
        Check if there exists a collision-free inverse kinematics for the
        Cartesian position
        
        Parameter ``robot``:
            The robot to check the Cartesian position for.
        
        Parameter ``waypoint``:
            The Cartesian position to check for collision.
        
        Returns:
            True if there exists a collision-free inverse kinematics for the
            Cartesian position, false otherwise.
        """
    @typing.overload
    def check_collision(self, robot: Robot, tcp: Frame, reference_config: list[float] | None = None) -> bool:
        """
        Check if there exists a collision-free inverse kinematics for the
        given robot and end-effector pose
        
        Parameter ``robot``:
            The robot to check for collision-free inverse kinematics.
        
        Parameter ``tcp``:
            The end-effector pose (transformation) to check for collision.
        
        Parameter ``reference_config``:
            Optional reference configuration for inverse kinematics of the
            end-effector pose.
        
        Returns:
            True if there exists a collision-free inverse kinematics for the
            given end-effector pose, false otherwise.
        """
    @typing.overload
    def check_collision(self, waypoint: CartesianWaypoint) -> bool:
        """
        Check if there exists a collision-free inverse kinematics for the
        Cartesian position
        
        Parameter ``waypoint``:
            The Cartesian position to check for collision.
        
        Returns:
            True if there exists a collision-free inverse kinematics for the
            Cartesian position, false otherwise.
        """
    @typing.overload
    def check_collision(self, tcp: Frame, reference_config: list[float] | None = None) -> bool:
        """
        Check if there exists a collision-free inverse kinematics for the
        given end-effector pose
        
        Parameter ``tcp``:
            The end-effector pose to check for collision.
        
        Parameter ``reference_config``:
            Optional reference configuration for inverse kinematics of the
            end-effector pose.
        
        Returns:
            True if there exists a collision-free inverse kinematics for the
            given end-effector pose, false otherwise.
        """
    def get_camera(self, name: str = '') -> Camera:
        """
        Get a camera from the environment
        
        Parameter ``name``:
            Optional parameter to specify the name of the camera. If not
            provided, an empty string defaults to retrieving a camera without
            a specific name.
        
        Returns:
            A shared pointer to the camera associated with the given name, or
            a default camera if the name is empty.
        """
    def get_camera_by_tag(self, tag: str) -> Camera:
        """
        Get the camera within the environment given a tag. If multiple cameras
        have the same tag, the first one to be found is returned.
        
        Parameter ``tag``:
            The tag associated with the camera to retrieve.
        
        Returns:
            The camera associated with the given tag, or nullptr if no camera
            with the tag is found.
        """
    def get_cameras_by_tag(self, tag: str) -> list[Camera]:
        """
        Get all cameras within the environment that carry the given tag.
        
        Parameter ``tag``:
            The tag associated with the cameras to retrieve.
        
        Returns:
            A vector of shared pointers to the cameras that have the specified
            tag.
        """
    def get_collision_free_joint_position_nearby(self, joint_position: list[float], robot: Robot = None) -> list[float] | None:
        """
        Calculate a collision free joint position close to the reference
        position.
        
        Parameter ``joint_position``:
            The reference joint position to find a collision free joint
            position close to.
        
        Parameter ``robot``:
            The robot to find a collision free joint position for.
        
        Returns:
            An optional containing the collision free joint position close to
            the reference position, or std::nullopt if no such joint position
            exists.
        """
    def get_obstacle(self, name: str) -> Obstacle:
        """
        Get the obstacle with the given name from the environment. Throws an
        error if no obstacle with the name exists.
        
        Parameter ``name``:
            The name of the obstacle to retrieve.
        
        Returns:
            A shared pointer to the obstacle associated with the given name.
        """
    def get_obstacles(self) -> list[Obstacle]:
        """
        Get all obstacles within the environment
        
        This function retrieves a list of all obstacles present in the
        environment.
        
        Returns:
            A vector of shared pointers to the obstacles within the
            environment.
        """
    def get_obstacles_by_tag(self, tag: str) -> list[Obstacle]:
        """
        Get all obstacles within the environment that carry the given tag.
        
        Parameter ``tag``:
            The tag associated with the obstacles to retrieve.
        
        Returns:
            A vector of shared pointers to the obstacles that have the
            specified tag.
        """
    def get_robot(self, name: str = '') -> Robot:
        """
        Get the robot with the given name from the environment.
        
        In case there is only a single robot in the environment, the default
        empty name argument will return this robot. Otherwise throws an error
        if no robot with the name exists.
        
        Parameter ``name``:
            The name of the robot to retrieve.
        
        Returns:
            The shared pointer to a robot object associated with the given
            name.
        """
    def get_robot_by_tag(self, tag: str) -> Robot:
        """
        Get the robot within the environment given a tag. If multiple robots
        have the same tag, the first one to be found is returned.
        
        Parameter ``tag``:
            The tag associated with the robot to retrieve.
        
        Returns:
            The robot associated with the given tag, or nullptr if no robot
            with the tag is found.
        """
    def get_robots(self) -> list[Robot]:
        """
        Get all robots within the environment
        
        Returns:
            A vector of shared pointers to the robots within the environment.
        """
    def get_waypoint(self, name: str) -> list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion:
        """
        Get the waypoint with the given name from the environment. Throws an
        error if no waypoint with the name exists.
        
        Parameter ``name``:
            The name of the waypoint to retrieve.
        
        Returns:
            The waypoint associated with the given name.
        """
    def get_waypoint_by_tag(self, tag: str) -> list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion | None:
        """
        Get a waypoint within the environment given a tag. If multiple
        waypoints have the same tag, the first one to be found is returned.
        
        Parameter ``tag``:
            The tag associated with the waypoint to retrieve.
        
        Returns:
            An optional containing the waypoint associated with the given tag,
            or std::nullopt if no waypoint with the tag is found.
        """
    def get_waypoints(self) -> list[list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion]:
        """
        Get all waypoints within the environment
        
        This function retrieves a list of all waypoints present in the
        environment.
        
        Returns:
            A vector of waypoints within the environment.
        """
    def get_waypoints_by_tag(self, tag: str) -> list[list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion]:
        """
        Get all waypoints within the environment given a tag.
        
        Parameter ``tag``:
            The tag associated with the waypoints to retrieve.
        
        Returns:
            A vector of waypoints that have the specified tag.
        """
    @typing.overload
    def remove_obstacle(self, obstacle: Obstacle) -> None:
        """
        Removes the given obstacles from the environment and from all
        collision checking.
        
        Parameter ``obstacle``:
            The obstacle to remove from the environment.
        """
    @typing.overload
    def remove_obstacle(self, name: str) -> None:
        """
        Removes all obstacles with the given name from the environment and
        from all collision checking.
        
        Parameter ``name``:
            The name of the obstacle to remove from the environment.
        """
    def remove_obstacles_by_tag(self, tag: str) -> None:
        ...
    def sync_with(self, studio: ... = '') -> None:
        """
        Sync with a Studio instance for visualization
        """
    def update_depth_map(self, obstacle: Obstacle) -> None:
        """
        Updates the depths matrix of a given depth map obstacle for the
        internal collision checking.
        
        Parameter ``obstacle``:
            The obstacle to update the depths map for.
        """
    def update_fixed_obstacles(self) -> None:
        """
        Updates all fixed obstacles for the internal collision checking. This
        should be called after changing e.g. the position or size of an
        obstacle.
        """
    def update_joint_position(self, robot: Robot, joint_position: list[float]) -> None:
        """
        Updates the joint position of the given robot for the internal
        collision checking.
        
        Parameter ``robot``:
            The robot to update the joint position for.
        
        Parameter ``joint_position``:
            The new joint position to set for the robot.
        """
    def update_point_cloud(self, obstacle: Obstacle) -> None:
        """
        Updates the point cloud of a given point cloud obstacle for the
        internal collision checking.
        
        Parameter ``obstacle``:
            The point cloud to update the points for.
        """
    def update_robot(self, robot: Robot = None) -> None:
        """
        Updates the given robot (or the default one if none was given) for the
        internal collision checking.
        
        Parameter ``robot``:
            The robot to update the collision model for.
        """
    @property
    def safety_margin(self) -> float:
        """
        Environment's global safety margin for collision checking [m]
        
        Returns:
            The global safety margin for collision checking [m].
        """
    @safety_margin.setter
    def safety_margin(self, arg1: float) -> None:
        ...
class FileReference:
    """
    A reference to a file used in the application.
    """
    @property
    def path(self) -> os.PathLike:
        """
        Path of the object (if loaded from file).
        """
    @path.setter
    def path(self, arg0: os.PathLike) -> None:
        ...
    @property
    def scale(self) -> float | None:
        """
        \\deprecated Scale for loading from file.
        """
    @scale.setter
    def scale(self, arg0: float | None) -> None:
        ...
class Frame:
    """
    Represents a transformation or pose in 3D Cartesian space.
    
    Encapsulates translation and rotation in a unified manner for 3D
    poses.
    """
    @staticmethod
    def Identity() -> Frame:
        """
        Get the identity transformation.
        
        Returns:
            Frame The identity Frame.
        """
    @staticmethod
    def from_euler(x: float, y: float, z: float, a: float, b: float, c: float) -> Frame:
        """
        Create a Frame from Euler angles.
        
        Parameter ``x``:
            The x translation.
        
        Parameter ``y``:
            The y translation.
        
        Parameter ``z``:
            The z translation.
        
        Parameter ``a``:
            The rotation angle around the x-axis.
        
        Parameter ``b``:
            The rotation angle around the y-axis.
        
        Parameter ``c``:
            The rotation angle around the z-axis.
        
        Returns:
            Frame The Frame with the specified translation and Euler angles.
        """
    @staticmethod
    def from_matrix(data: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(16)]) -> Frame:
        """
        Create a Frame from a matrix.
        
        Parameter ``data``:
            A 16-element array representing a 4x4 matrix.
        
        Returns:
            Frame The Frame constructed from the matrix.
        """
    @staticmethod
    def from_quaternion(x: float, y: float, z: float, qw: float, qx: float, qy: float, qz: float) -> Frame:
        """
        Create a Frame from quaternion values.
        
        Parameter ``x``:
            The x component of the quaternion.
        
        Parameter ``y``:
            The y component of the quaternion.
        
        Parameter ``z``:
            The z component of the quaternion.
        
        Parameter ``qw``:
            The scalar component of the quaternion.
        
        Parameter ``qx``:
            The x component of the quaternion.
        
        Parameter ``qy``:
            The y component of the quaternion.
        
        Parameter ``qz``:
            The z component of the quaternion.
        
        Returns:
            Frame The Frame with the specified quaternion.
        """
    @staticmethod
    def from_translation(x: float, y: float, z: float) -> Frame:
        """
        Create a Frame from translation values.
        
        Parameter ``x``:
            The x translation.
        
        Parameter ``y``:
            The y translation.
        
        Parameter ``z``:
            The z translation.
        
        Returns:
            Frame The Frame with the specified translation.
        """
    @staticmethod
    def from_two_vectors(v1: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)], v2: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]) -> Frame:
        """
        Create a Frame representing a rotation that brings two vectors into
        alignment.
        
        Parameter ``v1``:
            The first vector.
        
        Parameter ``v2``:
            The second vector.
        
        Returns:
            Frame The Frame with the rotation between the two vectors.
        """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, *, x: float = 0.0, y: float = 0.0, z: float = 0.0, a: float = 0.0, b: float = 0.0, c: float = 0.0, qw: float = 1.0, qx: float = 0.0, qy: float = 0.0, qz: float = 0.0) -> None:
        ...
    def __mul__(self, arg0: Frame) -> Frame:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def angular_distance(self, other: Frame) -> float:
        """
        Calculate the angular distance between two Frames' orientations.
        
        Parameter ``other``:
            The other Frame to compare against.
        
        Returns:
            double The angular distance.
        """
    def interpolate(self, t: float, other: Frame) -> Frame:
        """
        Interpolate between this Frame and another Frame.
        
        Parameter ``t``:
            The interpolation parameter (0.0 to 1.0).
        
        Parameter ``other``:
            The other Frame to interpolate towards.
        
        Returns:
            Frame The interpolated Frame.
        """
    def inverse(self) -> Frame:
        ...
    def translational_distance(self, other: Frame) -> float:
        """
        Calculate the Euclidean distance between two Frames' positions.
        
        Parameter ``other``:
            The other Frame to compare against.
        
        Returns:
            double The Euclidean distance.
        """
    @property
    def array(self) -> numpy.ndarray[numpy.float64]:
        ...
    @property
    def euler(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(6)]:
        """
        Convert the Frame to Euler angles and translation.
        
        Returns:
            std::array<double, 6> The Frame as Euler angles and translation.
        """
    @property
    def matrix(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(16)]:
        """
        Convert the Frame to a 4x4 matrix.
        
        Returns:
            std::array<double, 16> The Frame as a 4x4 matrix.
        """
    @property
    def quaternion(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(4)]:
        ...
    @property
    def rotation(self) -> Frame:
        ...
    @property
    def translation(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        ...
class FutureExpectedTrajectory:
    def __await__(self) -> FutureExpectedTrajectory:
        ...
    def __next__(self) -> None:
        ...
    def get(self) -> Expected[Trajectory, PlanningError]:
        ...
    def wait(self) -> None:
        ...
class Intrinsics:
    """
    Intrinsics of a camera
    
    Represents the intrinsic parameters of a camera, which include the
    focal lengths, optical center coordinates, and image dimensions.
    """
    @staticmethod
    def load_from_file(file: os.PathLike) -> Intrinsics:
        """
        Load an intrinsic calibration from a file
        """
    def __init__(self, focal_length_x: float, focal_length_y: float, optical_center_x: float, optical_center_y: float, width: int, height: int) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def as_matrix(self) -> numpy.ndarray[numpy.float64]:
        ...
    def save(self, file: os.PathLike) -> None:
        """
        Save an intrinsic calibration to a file
        """
    @property
    def cx(self) -> float:
        """
        The x-coordinate of the optical center [px]
        """
    @cx.setter
    def cx(self, arg0: float) -> None:
        ...
    @property
    def cy(self) -> float:
        """
        The y-coordinate of the optical center [px]
        """
    @cy.setter
    def cy(self, arg0: float) -> None:
        ...
    @property
    def focal_length_x(self) -> float:
        """
        The focal length along the x-axis [px]
        """
    @focal_length_x.setter
    def focal_length_x(self, arg0: float) -> None:
        ...
    @property
    def focal_length_y(self) -> float:
        """
        The focal length along the y-axis [px]
        """
    @focal_length_y.setter
    def focal_length_y(self, arg0: float) -> None:
        ...
    @property
    def fx(self) -> float:
        """
        The focal length along the x-axis [px]
        """
    @fx.setter
    def fx(self, arg0: float) -> None:
        ...
    @property
    def fy(self) -> float:
        """
        The focal length along the y-axis [px]
        """
    @fy.setter
    def fy(self, arg0: float) -> None:
        ...
    @property
    def height(self) -> int:
        """
        The image height [px]
        """
    @height.setter
    def height(self, arg0: int) -> None:
        ...
    @property
    def optical_center_x(self) -> float:
        """
        The x-coordinate of the optical center [px]
        """
    @optical_center_x.setter
    def optical_center_x(self, arg0: float) -> None:
        ...
    @property
    def optical_center_y(self) -> float:
        """
        The y-coordinate of the optical center [px]
        """
    @optical_center_y.setter
    def optical_center_y(self, arg0: float) -> None:
        ...
    @property
    def width(self) -> int:
        """
        The image width [px]
        """
    @width.setter
    def width(self, arg0: int) -> None:
        ...
class JointType:
    """
    Types of joints that can be present in the robot.
    
    Members:
    
      Revolute : A revolute joint that allows rotation.
    
      Continuous : A continuous joint that allows unlimited rotation.
    
      Prismatic : A prismatic joint that allows linear motion.
    
      Fixed : A fixed joint that does not allow any motion.
    """
    Continuous: typing.ClassVar[JointType]  # value = <JointType.Continuous: 1>
    Fixed: typing.ClassVar[JointType]  # value = <JointType.Fixed: 3>
    Prismatic: typing.ClassVar[JointType]  # value = <JointType.Prismatic: 2>
    Revolute: typing.ClassVar[JointType]  # value = <JointType.Revolute: 0>
    __members__: typing.ClassVar[dict[str, JointType]]  # value = {'Revolute': <JointType.Revolute: 0>, 'Continuous': <JointType.Continuous: 1>, 'Prismatic': <JointType.Prismatic: 2>, 'Fixed': <JointType.Fixed: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class LinearMotion:
    """
    Represents a request for a linear Cartesian-space motion.
    
    The LinearMotion struct represents a request for a linear motion in
    Cartesian space. It consists of a start and goal point, as well as a
    robot to perform the motion. It provides an interface for planning
    singularity-free linear motion in Cartesian space between any two
    waypoints.
    """
    @typing.overload
    def __init__(self, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint) -> None:
        """
        Construct a linear motion with a given start, and goal.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, robot: Robot, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint) -> None:
        """
        Construct a linear motion with a given robot, start, and goal.
        
        Parameter ``robot``:
            The robot for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, name: str, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint) -> None:
        """
        Construct a linear motion with a given name, start, and goal.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, name: str, robot: Robot, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint) -> None:
        """
        Construct a linear motion with a given name, robot, start, and goal.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``robot``:
            The robot for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @property
    def goal(self) -> list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint:
        """
        Goal point of the motion.
        """
    @goal.setter
    def goal(self, arg0: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint) -> None:
        ...
    @property
    def ignore_collisions(self) -> bool:
        """
        Whether to ignore collisions
        """
    @ignore_collisions.setter
    def ignore_collisions(self, arg0: bool) -> None:
        ...
    @property
    def name(self) -> str:
        """
        The unique name of the motion.
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def robot(self) -> Robot:
        """
        The robot for the motion (e.g. defines the kinematics and the joint
        limits).
        """
    @property
    def start(self) -> list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint:
        """
        Start point of the motion
        """
    @start.setter
    def start(self, arg0: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint) -> None:
        ...
class LinearPath:
    """
    """
    def __init__(self, start: Frame, goal: Frame) -> None:
        """
        Construct a LinearPath with a given start and goal pose.
        
        Parameter ``start``:
            The starting pose of the linear path.
        
        Parameter ``goal``:
            The ending pose of the linear path.
        """
    @property
    def goal(self) -> Frame:
        """
        The goal pose of the linear path.
        """
    @goal.setter
    def goal(self, arg0: Frame) -> None:
        ...
    @property
    def start(self) -> Frame:
        """
        The start pose of the linear path.
        """
    @start.setter
    def start(self, arg0: Frame) -> None:
        ...
class LinearSection:
    """
    Represents a linear Cartesian section for either the approach to the
    goal or the retraction from the start.
    """
    class Approximation:
        """
        Whether to approximate the Cartesian linear motion in joint space for
        singularity-free calculation.
        
        Members:
        
          Always : 
        
          Never : 
        """
        Always: typing.ClassVar[LinearSection.Approximation]  # value = <Approximation.Always: 1>
        Never: typing.ClassVar[LinearSection.Approximation]  # value = <Approximation.Never: 0>
        __members__: typing.ClassVar[dict[str, LinearSection.Approximation]]  # value = {'Always': <Approximation.Always: 1>, 'Never': <Approximation.Never: 0>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    Always: typing.ClassVar[LinearSection.Approximation]  # value = <Approximation.Always: 1>
    Never: typing.ClassVar[LinearSection.Approximation]  # value = <Approximation.Never: 0>
    approximation: LinearSection.Approximation
    def __init__(self, offset: Frame, speed: float = 1.0, approximation: LinearSection.Approximation = ..., smooth_transition: bool = True) -> None:
        ...
    @property
    def offset(self) -> Frame:
        """
        Relative linear cartesian offset from the reference pose.
        """
    @offset.setter
    def offset(self, arg0: Frame) -> None:
        ...
    @property
    def smooth_transition(self) -> bool:
        """
        Whether to use a smooth transition between this and the next or
        previous section. If false, the robot will come to a complete stop at
        the transition point.
        """
    @smooth_transition.setter
    def smooth_transition(self, arg0: bool) -> None:
        ...
    @property
    def speed(self) -> float:
        """
        Speed of the sub-motion, relative to the overall motion’s speed.
        """
    @speed.setter
    def speed(self, arg0: float) -> None:
        ...
class LowLevelMotion:
    """
    Represents a request for a low-level motion.
    
    The LinearMotion class provides an interface for very efficient
    planning of motion between joint-space waypoints. While low level
    motions are not checked for collisions, they are much faster to
    compute and allow for more flexible constraints such as a minimum
    duration parameter. This motion type is suitable for visual servoing
    task or other real-time control.
    """
    class ControlInterface:
        """
        The control interface for the motion, specifying either position or
        velocity control.
        
        Members:
        
          Position : Position-control: Full control over the entire kinematic state
        (Default)
        
          Velocity : Velocity-control: Ignores the current position, target position, and
        velocity limits
        """
        Position: typing.ClassVar[LowLevelMotion.ControlInterface]  # value = <ControlInterface.Position: 0>
        Velocity: typing.ClassVar[LowLevelMotion.ControlInterface]  # value = <ControlInterface.Velocity: 1>
        __members__: typing.ClassVar[dict[str, LowLevelMotion.ControlInterface]]  # value = {'Position': <ControlInterface.Position: 0>, 'Velocity': <ControlInterface.Velocity: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class DurationDiscretization:
        """
        The duration discretization strategy for the motion, specifying either
        continuous or discrete durations.
        
        Members:
        
          Continuous : Every trajectory synchronization duration is allowed (Default)
        
          Discrete : The trajectory synchronization duration must be a multiple of the
        control cycle
        """
        Continuous: typing.ClassVar[LowLevelMotion.DurationDiscretization]  # value = <DurationDiscretization.Continuous: 0>
        Discrete: typing.ClassVar[LowLevelMotion.DurationDiscretization]  # value = <DurationDiscretization.Discrete: 1>
        __members__: typing.ClassVar[dict[str, LowLevelMotion.DurationDiscretization]]  # value = {'Continuous': <DurationDiscretization.Continuous: 0>, 'Discrete': <DurationDiscretization.Discrete: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class Synchronization:
        """
        The synchronization strategy for the motion, specifying either phase,
        time, time if necessary, or no synchronization.
        
        Members:
        
          Phase : Phase synchronize the DoFs when possible, else fallback to "Time"
        strategy (Default)
        
          Time : Always synchronize the DoFs to reach the target at the same time
        
          TimeIfNecessary : Synchronize only when necessary (e.g. for non-zero target velocity or
        acceleration)
        
          None : Calculate every DoF independently
        """
        None: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.None: 3>
        Phase: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.Phase: 0>
        Time: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.Time: 1>
        TimeIfNecessary: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.TimeIfNecessary: 2>
        __members__: typing.ClassVar[dict[str, LowLevelMotion.Synchronization]]  # value = {'Phase': <Synchronization.Phase: 0>, 'Time': <Synchronization.Time: 1>, 'TimeIfNecessary': <Synchronization.TimeIfNecessary: 2>, 'None': <Synchronization.None: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    Continuous: typing.ClassVar[LowLevelMotion.DurationDiscretization]  # value = <DurationDiscretization.Continuous: 0>
    Discrete: typing.ClassVar[LowLevelMotion.DurationDiscretization]  # value = <DurationDiscretization.Discrete: 1>
    None: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.None: 3>
    Phase: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.Phase: 0>
    Position: typing.ClassVar[LowLevelMotion.ControlInterface]  # value = <ControlInterface.Position: 0>
    Time: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.Time: 1>
    TimeIfNecessary: typing.ClassVar[LowLevelMotion.Synchronization]  # value = <Synchronization.TimeIfNecessary: 2>
    Velocity: typing.ClassVar[LowLevelMotion.ControlInterface]  # value = <ControlInterface.Velocity: 1>
    @typing.overload
    def __init__(self, robot: Robot) -> None:
        """
        Construct a low-level motion with a given robot.
        
        Parameter ``robot``:
            The robot for the motion.
        """
    @typing.overload
    def __init__(self, name: str) -> None:
        """
        Construct a low-level motion with a given name.
        
        Parameter ``name``:
            The unique name of the motion.
        """
    @typing.overload
    def __init__(self, name: str, robot: Robot) -> None:
        """
        Construct a low-level motion with a given name, robot, start, and
        goal.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``robot``:
            The robot for the motion.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor.
        """
    @property
    def control_interface(self) -> LowLevelMotion.ControlInterface:
        """
        The control interface for the motion.
        """
    @control_interface.setter
    def control_interface(self, arg0: LowLevelMotion.ControlInterface) -> None:
        ...
    @property
    def duration_discretization(self) -> LowLevelMotion.DurationDiscretization:
        """
        The duration discretization strategy for the motion.
        """
    @duration_discretization.setter
    def duration_discretization(self, arg0: LowLevelMotion.DurationDiscretization) -> None:
        ...
    @property
    def goal(self) -> Waypoint:
        """
        Goal waypoint of the motion.
        """
    @goal.setter
    def goal(self, arg0: Waypoint) -> None:
        ...
    @property
    def intermediate_positions(self) -> list[list[float]]:
        """
        List of intermediate positions.
        
        For a small number of waypoints (less than 16), the trajectory goes
        exactly through the intermediate waypoints. For a larger number of
        waypoints, first a filtering algorithm is used to keep the resulting
        trajectory close to the original waypoints.
        """
    @intermediate_positions.setter
    def intermediate_positions(self, arg0: list[list[float]]) -> None:
        ...
    @property
    def minimum_duration(self) -> float | None:
        """
        A minimum duration of the motion.
        """
    @minimum_duration.setter
    def minimum_duration(self, arg0: float | None) -> None:
        ...
    @property
    def name(self) -> str:
        """
        The unique name of the motion.
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def robot(self) -> Robot:
        """
        The robot for the motion (e.g. defines the kinematics and the joint
        limits).
        """
    @property
    def start(self) -> Waypoint:
        """
        Start waypoint of the motion.
        """
    @start.setter
    def start(self, arg0: Waypoint) -> None:
        ...
    @property
    def synchronization(self) -> LowLevelMotion.Synchronization:
        """
        The synchronization strategy for the motion.
        """
    @synchronization.setter
    def synchronization(self, arg0: LowLevelMotion.Synchronization) -> None:
        ...
class MeshFile:
    """
    A collision object loaded from a file.
    """
    @typing.overload
    def __init__(self, path: os.PathLike, scale: float | None = None) -> None:
        """
        Load a file obstacle.
        
        Parameter ``path``:
            The path to the collision file (*.obj).
        
        Parameter ``scale``:
            Optional scale to apply when loading the object.
        """
    @typing.overload
    def __init__(self, visual_path: os.PathLike, collision_path: os.PathLike, scale: float | None = None) -> None:
        """
        Load a file obstacle.
        
        Parameter ``visual_path``:
            The path to the visual file.
        
        Parameter ``collision_path``:
            The path to the collision file (*.obj).
        
        Parameter ``scale``:
            Optional scale to apply when loading the object.
        """
    @property
    def collision_reference(self) -> FileReference:
        """
        The reference to the collision file
        """
    @property
    def inside_project(self) -> bool:
        """
        Indicates if the file is part of a Jacobi Studio project. Then, the
        file content is not uploaded when referencing the file in Studio live.
        """
    @inside_project.setter
    def inside_project(self, arg0: bool) -> None:
        ...
    @property
    def original_reference(self) -> FileReference:
        """
        The reference to the original file
        """
    @property
    def visual_reference(self) -> FileReference:
        """
        The reference to a visual file
        """
class Motion:
    """
    Represents a request for a collision-free point-to-point motion.
    
    The Motion class provides an interface for general point-to-point
    motion planning with arbitrary waypoints, linear approach and
    retraction, and task constraints. It includes parameters for the
    motion name, robot, start and goal points, and additional settings for
    motion planning, such as collision checking and soft failure handling.
    """
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> None:
        """
        Construct a Motion with a given start and goal point.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, robot: Robot, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> None:
        """
        Construct a Motion with a name, start and goal point.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, name: str, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> None:
        """
        Construct a Motion with a name, start and goal point.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    @typing.overload
    def __init__(self, name: str, robot: Robot, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> None:
        """
        Construct a Motion with a name, robot, start and goal point.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``robot``:
            The robot for the motion.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def cartesian_tcp_speed_cutoff(self) -> float | None:
        """
        Optional Cartesian TCP speed (translation-only) cutoff. This is a
        post-processing step.
        """
    @cartesian_tcp_speed_cutoff.setter
    def cartesian_tcp_speed_cutoff(self, arg0: float | None) -> None:
        ...
    @property
    def goal(self) -> list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion:
        """
        Goal point of the motion
        """
    @goal.setter
    def goal(self, arg0: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> None:
        ...
    @property
    def ignore_collisions(self) -> bool:
        """
        Whether to ignore collisions
        """
    @ignore_collisions.setter
    def ignore_collisions(self, arg0: bool) -> None:
        ...
    @property
    def initial_waypoints(self) -> list[list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint] | None:
        """
        Optional initial waypoints to start the optimization with (don’t use
        with intermediate waypoints).
        """
    @initial_waypoints.setter
    def initial_waypoints(self, arg0: list[list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint] | None) -> None:
        ...
    @property
    def linear_approach(self) -> LinearSection | None:
        """
        Optional relative linear cartesian motion for approaching the goal
        pose.
        """
    @linear_approach.setter
    def linear_approach(self, arg0: LinearSection | None) -> None:
        ...
    @property
    def linear_retraction(self) -> LinearSection | None:
        """
        Optional relative linear cartesian motion for retracting from the
        start pose.
        """
    @linear_retraction.setter
    def linear_retraction(self, arg0: LinearSection | None) -> None:
        ...
    @property
    def name(self) -> str:
        """
        The unique name of the motion.
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def orientation_loss_weight(self) -> float:
        """
        Weight of the loss minimizing the maximizing deviation of the end-
        effector orientation to the target value.
        """
    @orientation_loss_weight.setter
    def orientation_loss_weight(self, arg0: float) -> None:
        ...
    @property
    def orientation_target(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]:
        """
        Target vector pointing in the direction of the end-effector (TCP)
        orientation in the global coordinate system.
        """
    @orientation_target.setter
    def orientation_target(self, arg0: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]) -> None:
        ...
    @property
    def path_length_loss_weight(self) -> float:
        """
        Weight of the loss minimizing the path length of the trajectory.
        """
    @path_length_loss_weight.setter
    def path_length_loss_weight(self, arg0: float) -> None:
        ...
    @property
    def robot(self) -> Robot:
        """
        The robot for the motion (e.g. defines the kinematics and the joint
        limits).
        """
    @property
    def start(self) -> list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion:
        """
        Start point of the motion
        """
    @start.setter
    def start(self, arg0: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> None:
        ...
    @property
    def waypoints(self) -> list[list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint]:
        """
        Intermediate waypoints that the motion passes through exactly. The
        list of waypoints is limited to less than four, otherwise please take
        a look at LowLevelMotion.
        """
    @waypoints.setter
    def waypoints(self, arg0: list[list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint]) -> None:
        ...
class MultiRobotLinearSection:
    """
    Represents a mapping of robot arms and Cartesian section for either
    the approach to the goal or the retraction from the start.
    """
    def __init__(self, map: dict[Robot, LinearSection]) -> None:
        ...
class MultiRobotPoint:
    def __init__(self, map: dict[..., list[float] | Waypoint | CartesianWaypoint]) -> None:
        ...
class Obstacle(Element):
    """
    """
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, collision: Box, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, collision: Capsule, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, collision: Cylinder, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, collision: DepthMap, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, collision: MeshFile, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, collision: PointCloud, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, collision: Sphere, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: Box, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: Capsule, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: Cylinder, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: DepthMap, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: MeshFile, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: PointCloud, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, collision: Sphere, origin: Frame = ..., color: str = '000000', safety_margin: float = 0.0, tags: list[str] = []) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def with_name(self, name: str) -> Obstacle:
        """
        Clone the current obstacle and update some parameters.
        
        Creates a copy of the current obstacle and updates its name. This
        function is useful for creating modified versions of an obstacle
        without altering the original object.
        
        Parameter ``name``:
            The new name for the cloned obstacle.
        
        Returns:
            Obstacle A new Obstacle instance with the updated origin.
        """
    def with_origin(self, origin: Frame) -> Obstacle:
        """
        Clone the current obstacle and set the new origin.
        
        Creates a copy of the current obstacle and updates its origin to the
        provided frame. This function is useful for creating modified versions
        of an obstacle without altering the original object.
        
        Parameter ``origin``:
            The new pose (origin) for the cloned obstacle.
        
        Returns:
            Obstacle A new Obstacle instance with the updated origin.
        """
    @property
    def collision(self) -> Box | Capsule | Convex | list[Convex] | Cylinder | DepthMap | MeshFile | PointCloud | Sphere:
        """
        The object for collision checking (and/or visualization).
        
        This variant holds the geometric representation of the obstacle. It
        can be any of the supported shapes, including Box, Capsule, Convex,
        ConvexVector, Cylinder, DepthMap, PointCloud or Sphere.
        """
    @collision.setter
    def collision(self, arg0: Box | Capsule | Convex | list[Convex] | Cylinder | DepthMap | MeshFile | PointCloud | Sphere) -> None:
        ...
    @property
    def color(self) -> str:
        """
        The hex-string representation of the obstacle’s color, without the
        leading #.
        
        This string defines the color of the obstacle for visualization
        purposes, formatted as a hex code (e.g., "FF5733" for orange).
        """
    @color.setter
    def color(self, arg0: str) -> None:
        ...
    @property
    def for_collision(self) -> bool:
        """
        Whether this obstacle is used for collision checking.
        
        If true, the obstacle will be considered in collision detection
        calculations. By default, this is set to true.
        """
    @for_collision.setter
    def for_collision(self, arg0: bool) -> None:
        ...
    @property
    def for_visual(self) -> bool:
        """
        Whether this obstacle is used for visualization.
        
        If true, the obstacle will be rendered in the environment's
        visualization in Studio. By default, this is set to true.
        """
    @for_visual.setter
    def for_visual(self, arg0: bool) -> None:
        ...
    @property
    def robot(self) -> ...:
        ...
    @property
    def safety_margin(self) -> float:
        """
        An additional obstacle-specific safety margin for collision checking
        (on top of the environment's global safety margin).
        
        This margin adds an extra buffer around the obstacle during collision
        detection. It is specific to this obstacle and is added on top of any
        global safety margins.
        """
    @safety_margin.setter
    def safety_margin(self, arg0: float) -> None:
        ...
class Path:
    """
    Abstract base class representing a type of path.
    
    The PathType class provides an abstract interface for different types
    of paths.
    """
    @staticmethod
    def from_waypoints(waypoints: list[Frame], blend_radius: float | None = None, keep_tool_to_surface_orientation: bool = True) -> Path:
        """
        Construct a path from a list of waypoints and a blend radius
        
        Parameter ``waypoints``:
            The Cartesian waypoints defining the path.
        
        Parameter ``blend_radius``:
            The radius for the circular blend between waypoints.
        
        Parameter ``keep_tool_to_surface_orientation``:
            Whether to maintain tool-to-surface orientation.
        """
    def __add__(self, arg0: Path) -> Path:
        ...
    def __iadd__(self, arg0: Path) -> None:
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor
        """
    @typing.overload
    def __init__(self, arg0: LinearPath) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: CircularPath) -> None:
        ...
    def position(self, s: float) -> Frame:
        """
        Calculate the position at the path parameter s
        
        Parameter ``s``:
            The path parameter (0.0 to length).
        """
    def sample_positions(self, velocity: float, delta_time: float) -> list[Frame]:
        """
        Sample positions along the path with a given constant velocity and
        time step
        
        Parameter ``velocity``:
            The constant velocity of the end-effector [m/s].
        
        Parameter ``delta_time``:
            The time step for sampling the path [s].
        
        Returns:
            std::vector<Frame> The sampled positions along the path.
        """
    @property
    def length(self) -> float:
        """
        Get the overall length of the path
        """
    @property
    def segments(self) -> list[...]:
        """
        Get the individual segments of the path
        """
class PathCommand:
    """
    Represents a robot path that can be followed by a robot controller
    """
    class SegmentCommand:
        """
        Represents a single segment of a robot path command
        """
        @property
        def blending(self) -> float:
            """
            Distance around waypoints for blending [m]
            """
        @blending.setter
        def blending(self, arg0: float) -> None:
            ...
        @property
        def goal(self) -> list[float]:
            """
            The goal joint position of this segment [rad]
            """
        @goal.setter
        def goal(self, arg0: list[float]) -> None:
            ...
        @property
        def is_cartesian_linear(self) -> bool:
            """
            Whether this segment is linear in Cartesian space
            """
        @is_cartesian_linear.setter
        def is_cartesian_linear(self, arg0: bool) -> None:
            ...
        @property
        def max_speed(self) -> float:
            """
            Relative max. Cartesian speed
            """
        @max_speed.setter
        def max_speed(self, arg0: float) -> None:
            ...
    @staticmethod
    def from_trajectory(trajectory: Trajectory, max_distance: list[float]) -> PathCommand:
        """
        Convert a trajectory to a path command
        """
    def __repr__(self) -> str:
        ...
    @property
    def cumulative_lengths(self) -> list[float]:
        """
        Get list of cumulative lengths (Euclidian distance) between the start
        and segment goal
        """
    @property
    def length(self) -> float:
        """
        Get total length of the path
        """
    @property
    def segments(self) -> list[PathCommand.SegmentCommand]:
        """
        Segments of this path
        """
    @segments.setter
    def segments(self, arg0: list[PathCommand.SegmentCommand]) -> None:
        ...
    @property
    def start(self) -> list[float]:
        """
        The start joint position of this path
        """
    @start.setter
    def start(self, arg0: list[float]) -> None:
        ...
class PathFollowingMotion:
    """
    Represents a request for a Cartesian-space motion to be followed by
    the end-effector.
    
    The PathFollowingMotion class provides an interface for Cartesian-
    space paths to be accurately followed by the robot end-effector with a
    constant velocity. There are currently three different path types that
    are supported: linear, circular and blended. The path-following motion
    is suitable for use cases such as welding, painting, dispensing and
    deburring, where constant end-effector velocity is required for
    successful task execution. It includes parameters for the motion name,
    robot, path type, velocity, and additional settings for motion
    planning, such as collision checking and soft failure handling.
    """
    @typing.overload
    def __init__(self, path: Path, velocity: float = 50.0) -> None:
        """
        Construct a PathFollowingMotion with a given path type and optional
        velocity.
        
        Parameter ``path``:
            The Cartesian path type to follow.
        
        Parameter ``velocity``:
            The desired velocity of the end-effector [m/s]. If not provided,
            the robot will move as fast as possible while respecting velocity
            limits.
        """
    @typing.overload
    def __init__(self, name: str, path: Path, velocity: float = 50.0) -> None:
        """
        Construct a PathFollowingMotion with a name, path type, and optional
        velocity.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``path``:
            The Cartesian path type to follow.
        
        Parameter ``velocity``:
            The desired velocity of the end-effector [m/s]. If not provided,
            the robot will move as fast as possible while respecting velocity
            limits.
        """
    @typing.overload
    def __init__(self, robot: Robot, path: Path, velocity: float = 50.0) -> None:
        """
        Construct a PathFollowingMotion with a robot, path type, and optional
        velocity.
        
        Parameter ``robot``:
            The robot for the motion.
        
        Parameter ``path``:
            The Cartesian path type to follow.
        
        Parameter ``velocity``:
            The desired velocity of the end-effector [m/s]. If not provided,
            the robot will move as fast as possible while respecting velocity
            limits.
        """
    @typing.overload
    def __init__(self, name: str, robot: Robot, path: Path, velocity: float = 50.0) -> None:
        """
        Construct a PathFollowingMotion with a name, robot, path type, and
        optional velocity.
        
        Parameter ``name``:
            The unique name of the motion.
        
        Parameter ``robot``:
            The robot for the motion.
        
        Parameter ``path_type``:
            The Cartesian path type to follow.
        
        Parameter ``velocity``:
            The desired velocity of the end-effector [m/s]. If not provided,
            the robot will move as fast as possible while respecting velocity
            limits.
        """
    def robot_arm(self) -> RobotArm:
        ...
    @property
    def check_collision(self) -> bool:
        """
        If true, the planner will check for collisions during the motion.
        """
    @check_collision.setter
    def check_collision(self, arg0: bool) -> None:
        ...
    @property
    def feasible_velocity(self) -> float:
        """
        The feasible velocity of the end-effector achieved after planning
        [m/s] (only used if soft_failure is true).
        """
    @feasible_velocity.setter
    def feasible_velocity(self, arg0: float) -> None:
        ...
    @property
    def name(self) -> str:
        """
        The unique name of the motion.
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def path(self) -> Path:
        """
        The Cartesian path to follow.
        """
    @path.setter
    def path(self, arg0: Path) -> None:
        ...
    @property
    def reference_config(self) -> list[float] | None:
        """
        Optional reference configuration for the start state of the motion.
        """
    @reference_config.setter
    def reference_config(self, arg0: list[float] | None) -> None:
        ...
    @property
    def robot(self) -> Robot:
        """
        The robot for the motion (e.g. defines the kinematics and the joint
        limits).
        """
    @robot.setter
    def robot(self, arg0: Robot) -> None:
        ...
    @property
    def soft_failure(self) -> bool:
        """
        If true, the planner will adjust path velocity until a solution until
        velocity limits are satisfied.
        """
    @soft_failure.setter
    def soft_failure(self, arg0: bool) -> None:
        ...
    @property
    def velocity(self) -> float:
        """
        The desired velocity of the end-effector [m/s].
        """
    @velocity.setter
    def velocity(self, arg0: float) -> None:
        ...
class Planner:
    """
    """
    @staticmethod
    def load_from_json_file(file: os.PathLike, base_path: os.PathLike) -> Planner:
        ...
    @staticmethod
    def load_from_project_file(file: os.PathLike) -> Planner:
        """
        Loads a planner from a project file.
        
        Parameter ``file``:
            The path to the project file.
        
        Returns:
            A shared pointer to the loaded Planner object.
        """
    @staticmethod
    def load_from_studio(name: str) -> Planner:
        """
        Loads a planner from a Studio project. Make sure to have the access
        token set as an environment variable.
        
        Parameter ``name``:
            The name of the Studio project.
        
        Returns:
            A shared pointer to the loaded Planner object.
        """
    @typing.overload
    def __init__(self, environment: Environment, delta_time: float) -> None:
        """
        Create a planner with an environment and a specific delta time
        parameter.
        
        Parameter ``environment``:
            The environment to plan the robot motions in.
        
        Parameter ``delta_time``:
            The time step for sampling the trajectories in [s].
        """
    @typing.overload
    def __init__(self, robot: Robot, delta_time: float) -> None:
        """
        Create a planner with the robot inside an empty environment and a
        specific delta time parameter.
        
        Parameter ``robot``:
            The robot to plan the motions for.
        
        Parameter ``delta_time``:
            The time step for sampling the trajectories in [s].
        """
    @typing.overload
    def __init__(self, environment: Environment) -> None:
        """
        Create a planner with an environment.
        
        Parameter ``environment``:
            The environment to plan the robot motions in.
        """
    @typing.overload
    def __init__(self, robot: Robot) -> None:
        """
        Create a planner with the robot inside an empty environment.
        
        Parameter ``robot``:
            The robot to plan the motions for.
        """
    def add_motion(self, motion: BimanualMotion | LinearMotion | LowLevelMotion | Motion | PathFollowingMotion) -> None:
        """
        Add (or update when name already exists) a motion to the planner
        
        Parameter ``motion``:
            The motion to add, can be of any type.
        """
    def get_motion(self, name: str) -> BimanualMotion | LinearMotion | LowLevelMotion | Motion | PathFollowingMotion:
        """
        Get a motion by its name
        
        Parameter ``name``:
            The name of the motion to retrieve.
        
        Returns:
            The AnyMotion object associated with the given name.
        """
    def load_motion_plan(self, file: os.PathLike) -> None:
        """
        Load a *.jacobi-plan motion plan for accelerating the planning
        calculation.
        
        Parameter ``file``:
            The path to the *.jacobi-plan file to load.
        """
    @typing.overload
    def plan(self, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> Expected[Trajectory, PlanningError]:
        """
        Plans a time-optimized, collision-free, and jerk-limited motion from
        start to goal.
        
        Parameter ``start``:
            The start point of the motion.
        
        Parameter ``goal``:
            The goal point of the motion.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, name: str, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None) -> Expected[Trajectory, PlanningError]:
        """
        Plans a time-optimized, collision-free, and jerk-limited motion given
        the motion name. In case the motion was specified by a start or goal
        region, the respective exact start or goal positions needs to be
        passed.
        
        Parameter ``name``:
            The name of the motion to plan.
        
        Parameter ``start``:
            The exact start position of the motion.
        
        Parameter ``goal``:
            The exact goal position of the motion.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, motion: Motion, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None) -> Expected[Trajectory, PlanningError]:
        """
        Plans a collision-free point-to-point motion.
        
        Parameter ``motion``:
            The motion to plan.
        
        Parameter ``start``:
            The exact start position of the motion.
        
        Parameter ``goal``:
            The exact goal position of the motion.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, motion: LinearMotion) -> Expected[Trajectory, PlanningError]:
        """
        Plans a linear motion.
        
        Parameter ``motion``:
            The linear motion to plan.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, motion: LowLevelMotion) -> Expected[Trajectory, PlanningError]:
        """
        Plans a low-level motion.
        
        Parameter ``motion``:
            The low-level motion to plan.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, motion: PathFollowingMotion) -> Expected[Trajectory, PlanningError]:
        """
        Plans a path-following motion.
        
        Parameter ``motion``:
            The path-following motion to plan.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, motion: BimanualMotion) -> Expected[Trajectory, PlanningError]:
        """
        Plans a bimanual motion.
        
        Parameter ``motion``:
            The bimanual motion to plan.
        
        Returns:
            The computed trajectory or std::nullopt if the planning failed.
        """
    @typing.overload
    def plan(self, motions: list[BimanualMotion | LinearMotion | LowLevelMotion | Motion | PathFollowingMotion]) -> Expected[list[Trajectory], PlanningError]:
        """
        Plans a feasible sequence of motions.
        
        Parameter ``motions``:
            The sequence of motions to plan.
        
        Returns:
            The computed sequence of trajectories or std::nullopt if the
            planning failed.
        """
    @typing.overload
    def plan_async(self, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> FutureExpectedTrajectory:
        ...
    @typing.overload
    def plan_async(self, motion: Motion, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None) -> FutureExpectedTrajectory:
        ...
    @typing.overload
    def plan_async(self, motion: LinearMotion) -> FutureExpectedTrajectory:
        ...
    @typing.overload
    def plan_path(self, motion: Motion, start: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None, goal: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | None = None) -> Expected[PathCommand, PlanningError]:
        ...
    @typing.overload
    def plan_path(self, motion: BimanualMotion) -> Expected[PathCommand, PlanningError]:
        ...
    def set_seed(self, seed: int | None) -> None:
        """
        Set the seed of the planner's random number generator
        
        Parameter ``seed``:
            The seed to set. If no seed is provided, the generator will be
            seeded with a random value.
        """
    def transfer_trajectory(self, trajectory: Trajectory, robot_from: RobotArm, robot_to: RobotArm, offset: Frame = ...) -> Expected[Trajectory, PlanningError]:
        """
        Transfers a trajectory from one robot to another.
        
        Calculate a trajectory for another robot that follows the TCP of the
        original robot given the trajectory. This method does not check for
        constraints of the new robot.
        
        Parameter ``trajectory``:
            The trajectory to follow.
        
        Parameter ``robot_from``:
            The original robot to transfer from.
        
        Parameter ``robot_to``:
            The new robot to transfer to.
        
        Parameter ``offset``:
            Optional offset between the from and to robot's TCP.
        
        Returns:
            The transferred trajectory or std::nullopt if the planning failed.
        """
    @property
    def delta_time(self) -> float:
        """
        The time step for sampling the trajectories in [s]. Usually, this
        should correspond to the control rate of the robot.
        """
    @property
    def dynamic_robot_trajectories(self) -> list[DynamicRobotTrajectory]:
        """
        Pairs of robot-trajectories that are used for dynamic collision
        checking (e.g. of moving robots)
        """
    @dynamic_robot_trajectories.setter
    def dynamic_robot_trajectories(self, arg0: list[DynamicRobotTrajectory]) -> None:
        ...
    @property
    def environment(self) -> Environment:
        """
        The current environment to plan robot motions in
        """
    @environment.setter
    def environment(self, arg0: Environment) -> None:
        ...
    @property
    def initial_perturbation_scale(self) -> float:
        """
        Initial perturbation for the trajectory optimization
        """
    @initial_perturbation_scale.setter
    def initial_perturbation_scale(self, arg0: float) -> None:
        ...
    @property
    def last_calculation_duration(self) -> float:
        """
        The calculation duration of the last full trajectory computation
        """
    @property
    def last_intermediate_positions(self) -> list[list[float]]:
        ...
    @property
    def max_break_steps(self) -> int:
        """
        Max number of steps without improvement before early stopping
        """
    @max_break_steps.setter
    def max_break_steps(self, arg0: int) -> None:
        ...
    @property
    def max_calculation_duration(self) -> float | None:
        """
        The maximum compute budget (that won't be exceeded)
        """
    @max_calculation_duration.setter
    def max_calculation_duration(self, arg0: float | None) -> None:
        ...
    @property
    def max_optimization_steps(self) -> int:
        """
        Maximum number of optimization steps
        """
    @max_optimization_steps.setter
    def max_optimization_steps(self, arg0: int) -> None:
        ...
    @property
    def meaningful_loss_improvement(self) -> float:
        """
        A meaningful relative improvement to avoid stopping
        """
    @meaningful_loss_improvement.setter
    def meaningful_loss_improvement(self, arg0: float) -> None:
        ...
    @property
    def min_calculation_duration(self) -> float | None:
        """
        The minimum compute budget (that the planner can use regardless)
        """
    @min_calculation_duration.setter
    def min_calculation_duration(self, arg0: float | None) -> None:
        ...
    @property
    def perturbation_change_steps(self) -> int:
        """
        Steps without improvement after which the perturbation scale is
        adapted
        """
    @perturbation_change_steps.setter
    def perturbation_change_steps(self, arg0: int) -> None:
        ...
    @property
    def perturbation_scale_change(self) -> float:
        """
        Change of the perturbation if no improvement could be found recently
        """
    @perturbation_scale_change.setter
    def perturbation_scale_change(self, arg0: float) -> None:
        ...
    @property
    def pre_eps_collision(self) -> float:
        """
        Resolution of the collision checking in the pre-planning stage [rad]
        """
    @pre_eps_collision.setter
    def pre_eps_collision(self, arg0: float) -> None:
        ...
    @property
    def pre_eps_steering(self) -> float:
        """
        Steering epsilon in the pre-planning stage [rad]
        """
    @pre_eps_steering.setter
    def pre_eps_steering(self, arg0: float) -> None:
        ...
    @property
    def pre_max_steps(self) -> float:
        """
        Maximum number of steps in the pre-planning stage before a solution is
        not found
        """
    @pre_max_steps.setter
    def pre_max_steps(self, arg0: float) -> None:
        ...
    @property
    def pre_optimization_steps(self) -> int:
        """
        Number of samples for optimization after finding a solution in the
        pre-plannning stage
        """
    @pre_optimization_steps.setter
    def pre_optimization_steps(self, arg0: int) -> None:
        ...
class PlanningError(ReturnCode):
    """
    Represents the possible outcomes of a trajectory calculation
    """
    Collision: typing.ClassVar[PlanningError]  # value = [-204] Inevitable collision.
    DegreesOfFreedom: typing.ClassVar[PlanningError]  # value = [-103] Mismatch of the degrees of freedom of input data and robot.
    GoalOutsideLimits: typing.ClassVar[PlanningError]  # value = [-203] Specified goal is outside of robot's limits.
    Internal: typing.ClassVar[PlanningError]  # value = [-1] Unknown error.
    InverseKinematics: typing.ClassVar[PlanningError]  # value = [-201] Could not find an inverse kinematics solution due to reachability or collisions.
    JointLimitsExceeded: typing.ClassVar[PlanningError]  # value = [-202] Could not find a trajectory with joint velocities within the limits.
    MotionNotFound: typing.ClassVar[PlanningError]  # value = [-101] Motion with the specified name was not found.
    NotSupported: typing.ClassVar[PlanningError]  # value = [-100] Feature is not supported.
    PathNotFound: typing.ClassVar[PlanningError]  # value = [-200] No path could be found - is a collision-free path between start and goal possible?
    Success: typing.ClassVar[PlanningError]  # value = [1] Success
    WaypointRegionMismatch: typing.ClassVar[PlanningError]  # value = [-102] The given exact waypoint does not correspond to the saved waypoint or region.
class PointCloud:
    points: list[typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]]
    resolution: float
    def __init__(self, points: list[typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)]], resolution: float = 0.01) -> None:
        ...
class Region(Element):
    """
    A joint-space region with possible position, velocity, and/or
    acceleration values.
    
    The Region class defines a region in joint space with boundaries on
    position, velocity, and acceleration. It is used to specify an area
    within which a the robot end-effector operates. The class provides
    methods to construct the region with varying levels of detail and to
    check if a given waypoint falls within the region's boundaries.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, min_position: list[float], max_position: list[float]) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def is_within(self, other: Waypoint) -> bool:
        """
        Check if a given waypoint is within the region.
        
        Parameter ``other``:
            The waypoint to check.
        
        Returns:
            true If the waypoint is within the region's boundaries.
        
        Returns:
            false If the waypoint is not within the region's boundaries.
        
        This method checks if the given waypoint's position, velocity, and
        acceleration fall within the respective boundaries defined by the
        region.
        """
    @property
    def max_acceleration(self) -> list[float]:
        """
        Maximum acceleration boundary of the region.
        """
    @max_acceleration.setter
    def max_acceleration(self, arg0: list[float]) -> None:
        ...
    @property
    def max_position(self) -> list[float]:
        """
        Maximum position boundary of the region.
        """
    @max_position.setter
    def max_position(self, arg0: list[float]) -> None:
        ...
    @property
    def max_velocity(self) -> list[float]:
        """
        Maximum velocity boundary of the region.
        """
    @max_velocity.setter
    def max_velocity(self, arg0: list[float]) -> None:
        ...
    @property
    def min_acceleration(self) -> list[float]:
        """
        Minimum acceleration boundary of the region.
        """
    @min_acceleration.setter
    def min_acceleration(self, arg0: list[float]) -> None:
        ...
    @property
    def min_position(self) -> list[float]:
        """
        Minimum position boundary of the region.
        """
    @min_position.setter
    def min_position(self, arg0: list[float]) -> None:
        ...
    @property
    def min_velocity(self) -> list[float]:
        """
        Minimum velocity boundary of the region.
        """
    @min_velocity.setter
    def min_velocity(self, arg0: list[float]) -> None:
        ...
class ReturnCode:
    """
    A return code with a string description
    """
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        ...
    def __eq__(self, arg0: ReturnCode) -> bool:
        ...
    def __ge__(self, arg0: ReturnCode) -> bool:
        ...
    def __gt__(self, arg0: ReturnCode) -> bool:
        ...
    def __le__(self, arg0: ReturnCode) -> bool:
        ...
    def __lt__(self, arg0: ReturnCode) -> bool:
        ...
    def __ne__(self, arg0: ReturnCode) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def code(self) -> int:
        ...
    @property
    def description(self) -> str:
        ...
class Robot(Element):
    """
    """
    base: Frame
    @staticmethod
    def from_model(model: str) -> Robot:
        ...
    def __repr__(self) -> str:
        ...
    def set_speed(self, speed: float) -> None:
        ...
    @property
    def control_rate(self) -> float | None:
        ...
    @property
    def degrees_of_freedom(self) -> int:
        ...
    @property
    def id(self) -> int:
        ...
    @property
    def joint_types(self) -> list[JointType]:
        ...
    @property
    def max_acceleration(self) -> list[float]:
        ...
    @property
    def max_jerk(self) -> list[float]:
        ...
    @property
    def max_position(self) -> list[float]:
        ...
    @property
    def max_velocity(self) -> list[float]:
        ...
    @property
    def min_position(self) -> list[float]:
        ...
    @property
    def model(self) -> str:
        """
        The model name of the robot
        """
    @model.setter
    def model(self, arg0: str) -> None:
        ...
class RobotArm(Robot):
    """
    """
    def calculate_orientation_deviation(self, joint_position: list[float], target: typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(3)] = [0.0, 0.0, 1.0]) -> float:
        """
        Calculates the orientation deviation between the robot’s TCP and a
        target vector.
        
        Parameter ``joint_position``:
            The joint position of the robot.
        
        Parameter ``target``:
            The target vector to compare against.
        
        Returns:
            The orientation deviation in radians.
        """
    def calculate_tcp(self, joint_position: list[float]) -> Frame:
        """
        Calculates the forward_kinematics and returns the frame of the robot’s
        TCP.
        
        Parameter ``joint_position``:
            The joint position of the robot.
        
        Returns:
            The frame of the robot’s TCP.
        """
    def calculate_tcp_speed(self, joint_position: list[float], joint_velocity: list[float]) -> float:
        """
        Calculates the forward_kinematics and returns the norm of the
        Cartesian velocity of the robot’s TCP.
        
        Parameter ``joint_position``:
            The joint position of the robot.
        
        Parameter ``joint_velocity``:
            The joint velocity of the robot.
        
        Returns:
            The Cartesian speed of the TCP.
        """
    @typing.overload
    def inverse_kinematics(self, waypoint: CartesianWaypoint) -> list[float] | None:
        """
        Computes the inverse kinematics for a Cartesian waypoint.
        
        Parameter ``waypoint``:
            The Cartesian waypoint to compute the inverse kinematics for.
        
        Returns:
            An optional `Config` object representing the joint positions of
            the robot.
        """
    @typing.overload
    def inverse_kinematics(self, tcp: Frame, reference_config: list[float] | None = None) -> list[float] | None:
        """
        Computes the inverse kinematics for a Cartesian position and a
        reference configuration.
        
        Finds a joint position so that the robot’s TCP is at the given frame,
        which is defined in the world coordinate system. In general, the
        solution will try to stay close to the reference_config parameter. We
        use a numerical optimization for robots with more than 6 degrees of
        freedom. Then, the reference configuration is used as a starting point
        for the optimization. This method does not take the environment’s
        collision model into account.
        
        Parameter ``tcp``:
            The Cartesian position to compute the inverse kinematics for.
        
        Parameter ``reference_config``:
            The reference configuration to use for the inverse kinematics.
        
        Returns:
            An optional `Config` object representing the joint positions of
            the robot.
        """
    def set_speed(self, speed: float) -> None:
        """
        Sets the velocity, acceleration, and jerk limits to a factor [0, 1] of
        their respective default (maximum) values.
        
        Parameter ``speed``:
            A double representing the speed to be set for the robot.
        """
    @property
    def control_rate(self) -> float | None:
        """
        The (optional) default control rate. [Hz]
        """
    @property
    def default_position(self) -> list[float]:
        """
        The default robot position - used for initializing the current robot
        position.
        """
    @property
    def degrees_of_freedom(self) -> int:
        """
        The degrees of freedom (or number of axis) of the robot.
        """
    @property
    def end_effector(self) -> Obstacle | None:
        """
        Get the (optional) end effector attached to the robot’s flange.
        
        Returns:
            An (optional) end effector attached to the robot’s flange.
        """
    @end_effector.setter
    def end_effector(self, arg1: Obstacle | None) -> None:
        ...
    @property
    def end_effector_obstacle(self) -> Obstacle | None:
        """
        Get the (optional) end effector attached to the robot’s flange.
        
        Returns:
            An (optional) end effector attached to the robot’s flange.
        """
    @end_effector_obstacle.setter
    def end_effector_obstacle(self, arg1: Obstacle | None) -> None:
        ...
    @property
    def flange_to_tcp(self) -> Frame:
        """
        \\internal The transformation from the robot’s flange to the robot’s
        TCP, e.g., for using inverse kinematics or an item obstacle.
        """
    @flange_to_tcp.setter
    def flange_to_tcp(self, arg1: Frame) -> None:
        ...
    @property
    def item(self) -> Obstacle | None:
        """
        \\internal An (optional) obstacle attached to the robot’s TCP.
        """
    @item.setter
    def item(self, arg1: Obstacle | None) -> None:
        ...
    @property
    def item_obstacle(self) -> Obstacle | None:
        """
        \\internal An (optional) obstacle attached to the robot’s TCP.
        """
    @item_obstacle.setter
    def item_obstacle(self, arg1: Obstacle | None) -> None:
        ...
    @property
    def joint_types(self) -> list[JointType]:
        ...
    @property
    def link_frames(self) -> list[Frame]:
        ...
    @property
    def link_obstacles(self) -> list[Obstacle]:
        """
        The obstacles for each robot link.
        """
    @link_obstacles.setter
    def link_obstacles(self, arg0: list[Obstacle]) -> None:
        ...
    @property
    def max_acceleration(self) -> list[float]:
        """
        Maximum absolute acceleration for each joint. [rad/s^2]
        """
    @max_acceleration.setter
    def max_acceleration(self, arg0: list[float]) -> None:
        ...
    @property
    def max_jerk(self) -> list[float]:
        """
        Maximum absolute jerk for each joint. [rad/s^3]
        """
    @max_jerk.setter
    def max_jerk(self, arg0: list[float]) -> None:
        ...
    @property
    def max_position(self) -> list[float]:
        """
        Maximum position for each joint. [rad]
        """
    @max_position.setter
    def max_position(self, arg0: list[float]) -> None:
        ...
    @property
    def max_velocity(self) -> list[float]:
        """
        Maximum absolute velocity for each joint. [rad/s]
        """
    @max_velocity.setter
    def max_velocity(self, arg0: list[float]) -> None:
        ...
    @property
    def min_position(self) -> list[float]:
        """
        Minimum position for each joint. [rad]
        """
    @min_position.setter
    def min_position(self, arg0: list[float]) -> None:
        ...
    @property
    def number_joints(self) -> int:
        """
        The number of joints with links in between.
        """
    @property
    def tcp(self) -> Frame:
        """
        Retrieves the frame of the robot’s TCP.
        
        Returns:
            A `Frame` representing the frame of the robot’s TCP.
        """
    @property
    def tcp_acceleration(self) -> Twist:
        """
        Retrieves the Cartesian acceleration of the robot’s TCP.
        
        Returns:
            A `Twist` representing the Cartesian acceleration of the robot’s
            TCP.
        """
    @property
    def tcp_position(self) -> Frame:
        """
        Retrieves the frame of the robot’s TCP.
        
        Returns:
            A `Frame` representing the frame of the robot’s TCP.
        """
    @property
    def tcp_velocity(self) -> Twist:
        """
        Retrieves the Cartesian velocity of the robot’s TCP.
        
        Returns:
            A `Twist` representing the Cartesian velocity of the robot’s TCP.
        """
    @property
    def tool(self) -> Obstacle | None:
        """
        Get the (optional) end effector attached to the robot’s flange.
        
        Returns:
            An (optional) end effector attached to the robot’s flange.
        """
    @tool.setter
    def tool(self, arg1: Obstacle | None) -> None:
        ...
class Sampler:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, seed: int) -> None:
        ...
    @typing.overload
    def sample(self, region: Region) -> Waypoint:
        ...
    @typing.overload
    def sample(self, cartesian_region: CartesianRegion) -> CartesianWaypoint:
        ...
class Sphere:
    """
    A sphere collision object.
    
    The Sphere struct represents a 3D spherical collision object, defined
    by its radius, which determines its size in all directions.
    """
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, radius: float) -> None:
        """
        Construct a sphere with the given radius.
        
        Parameter ``radius``:
            The radius of the sphere.
        
        Initializes the sphere with the specified radius.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def radius(self) -> float:
        """
        Radius of the sphere [m]
        """
class State:
    """
    The complete kinematic state of a robot along a trajectory
    
    The State struct contains the kinematic information of a robot at a
    given time along a trajectory. It includes the joint positions,
    velocities, and accelerations.
    """
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get the degrees of freedom of the joint space
        
        Returns:
            The degrees of freedom of the joint space.
        """
    def __repr__(self) -> str:
        ...
    @property
    def acceleration(self) -> list[float]:
        """
        Joint acceleration [rad/s^2]
        """
    @acceleration.setter
    def acceleration(self, arg0: list[float]) -> None:
        ...
    @property
    def position(self) -> list[float]:
        """
        Joint position [rad]
        """
    @position.setter
    def position(self, arg0: list[float]) -> None:
        ...
    @property
    def time(self) -> float:
        """
        The unscaled time
        """
    @time.setter
    def time(self, arg0: float) -> None:
        ...
    @property
    def velocity(self) -> list[float]:
        """
        Joint velocity [rad/s]
        """
    @velocity.setter
    def velocity(self, arg0: list[float]) -> None:
        ...
class Studio:
    """
    """
    class Action:
        """
        An action that can be performed in Jacobi Studio.
        
        The `Action` class represents an action in Jacobi Studio, such as
        setting a robot's joint position, adding an obstacle, or manipulating
        the environment. An action can contain multiple commands, allowing for
        complex interactions in Studio.
        """
    class Events:
        """
        A container that maps a specific timing to one or multiple actions.
        The static methods of this class do not change the visualization in
        Jacobi Studio immediately, but only return an action that can be
        executed later (e.g. alongside a trajectory).
        
        The `Events` struct allows for scheduling actions in Jacobi Studio at
        specific times. Static methods are provided to create various actions,
        which can be executed later.
        """
        @staticmethod
        def add_camera(camera: Camera) -> Studio.Action:
            """
            Returns an action that adds a camera.
            
            Parameter ``camera``:
                The camera to be added.
            
            Returns:
                The action to add the camera.
            """
        @staticmethod
        def add_obstacle(obstacle: Obstacle) -> Studio.Action:
            """
            Returns an action that adds the given obstacle to the environment.
            
            Parameter ``obstacle``:
                The obstacle to be added.
            
            Returns:
                The action to add the obstacle.
            """
        @staticmethod
        def add_robot(robot: Robot) -> Studio.Action:
            """
            Returns an action that adds the given robot to the environment.
            
            Parameter ``robot``:
                The robot to be added.
            
            Returns:
                The action to add the robot.
            """
        @staticmethod
        def add_robot_path(points: list[list[float]], robot: Robot = None, name: str = '', color: str = '', stroke: float = -1.0, arrow_size: float = 1.0) -> Studio.Action:
            """
            Returns an action that adds a visualization of a path for the given
            robot.
            
            Parameter ``points``:
                The points defining the path.
            
            Parameter ``robot``:
                Optional robot associated with the path.
            
            Parameter ``name``:
                Optional name for the path.
            
            Parameter ``color``:
                Optional color for the path visualization.
            
            Parameter ``stroke``:
                Optional stroke width for the path visualization.
            
            Parameter ``arrow_size``:
                Optional size of arrow for end of path
            
            Returns:
                The action to add the robot path visualization.
            """
        @staticmethod
        def add_waypoint(point: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> Studio.Action:
            """
            Returns an action that adds the given Cartesian waypoint to the
            environment.
            
            Parameter ``point``:
                The Cartesian waypoint to be added.
            
            Returns:
                The action to add the Cartesian waypoint.
            """
        @staticmethod
        def remove_by_name(name: str) -> Studio.Action:
            """
            Returns an action that removes the elements of the given name from the
            environment.
            
            Parameter ``name``:
                The name to be removed.
            
            Returns:
                The action to remove the obstacle.
            """
        @staticmethod
        def remove_by_tag(tag: str) -> Studio.Action:
            """
            Returns an action that removes the elements containing the tag from
            the environment.
            
            Parameter ``tag``:
                The tag to be removed.
            
            Returns:
                The action to remove the obstacle.
            """
        @staticmethod
        def remove_camera(camera: Camera) -> Studio.Action:
            """
            Returns an action that removes a camera.
            
            Parameter ``camera``:
                The camera to be removed.
            
            Returns:
                The action to remove the camera.
            """
        @staticmethod
        def remove_obstacle(obstacle: Obstacle) -> Studio.Action:
            """
            Returns an action that removes the given obstacle (by name) from the
            environment.
            
            Parameter ``obstacle``:
                The obstacle to be removed.
            
            Returns:
                The action to remove the obstacle.
            """
        @staticmethod
        def remove_obstacles_by_tag(tag: str) -> Studio.Action:
            """
            Returns an action that removes the obstacles containing the tag from
            the environment.
            
            Parameter ``tag``:
                The tag to be removed.
            
            Returns:
                The action to remove the obstacle.
            """
        @staticmethod
        def remove_robot_path(robot: Robot, name: str) -> Studio.Action:
            """
            Returns an action that removes a visualization of a named path for the
            given robot.
            
            Parameter ``robot``:
                The robot associated with the path.
            
            Parameter ``name``:
                The name of the path to be removed.
            
            Returns:
                The action to remove the robot path visualization.
            """
        @staticmethod
        def set_camera_depth_map(depths: list[list[float]], x: float, y: float, camera: Camera = None) -> Studio.Action:
            """
            Returns an action that sets the depth map visualization of a camera.
            
            Parameter ``depths``:
                The depth map data.
            
            Parameter ``x``:
                Size of the depth map along the x-axis.
            
            Parameter ``y``:
                Size of the depth map along the y-axis.
            
            Parameter ``camera``:
                Optional camera associated with the depth map.
            
            Returns:
                The action to set the camera depth map.
            """
        @staticmethod
        def set_camera_image_encoded(image: str, camera: Camera) -> Studio.Action:
            """
            Returns an action that sets an image for a camera encoded as a string.
            
            Parameter ``image``:
                The encoded image to be set.
            
            Parameter ``camera``:
                Optional camera associated with the image.
            
            Returns:
                The action to set the camera image.
            """
        @staticmethod
        def set_end_effector(obstacle: Obstacle | None, robot: Robot = None) -> Studio.Action:
            """
            Returns an action that sets the end-effector obstacle of the given
            robot, or the last active robot instead.
            
            Parameter ``obstacle``:
                Optional obstacle to be set.
            
            Parameter ``robot``:
                Optional robot associated with the obstacle.
            
            Returns:
                The action to set the item obstacle.
            """
        @staticmethod
        def set_io_signal(name: str, value: int | float, robot: Robot = None) -> Studio.Action:
            """
            Returns an action that sets an I/O signal of the given robot, or the
            last active robot instead.
            
            Parameter ``name``:
                The name of the I/O signal.
            
            Parameter ``value``:
                The value to be set for the I/O signal.
            
            Parameter ``robot``:
                Optional robot associated with the I/O signal.
            
            Returns:
                The action to set the I/O signal.
            """
        @staticmethod
        def set_item(obstacle: Obstacle | None, robot: Robot = None) -> Studio.Action:
            """
            Returns an action that sets the item obstacle of the given robot, or
            the last active robot instead.
            
            Parameter ``obstacle``:
                Optional obstacle to be set.
            
            Parameter ``robot``:
                Optional robot associated with the obstacle.
            
            Returns:
                The action to set the item obstacle.
            """
        @staticmethod
        def set_joint_position(joint_position: list[float], robot: Robot = None) -> Studio.Action:
            """
            Returns an action that sets the joint position of the given robot, or
            the last active robot instead.
            
            Parameter ``joint_position``:
                The desired joint position.
            
            Parameter ``robot``:
                Optional robot to set the joint position for.
            
            Returns:
                The action to set the joint position.
            """
        @staticmethod
        def set_material(material: str, robot: Robot = None) -> Studio.Action:
            """
            Returns an action that sets the material of the given robot, or the
            last active robot instead.
            
            Parameter ``material``:
                The material to be set.
            
            Parameter ``robot``:
                Optional robot associated with the material.
            
            Returns:
                The action to set the material.
            """
        @staticmethod
        def update_camera(camera: Camera) -> Studio.Action:
            """
            Returns an action that updates a camera with the same name.
            
            Parameter ``camera``:
                The camera to be updated.
            
            Returns:
                The action to update the camera.
            """
        @staticmethod
        def update_obstacle(obstacle: Obstacle) -> Studio.Action:
            """
            Returns an action that updates the obstacle with the same name.
            
            Parameter ``obstacle``:
                The obstacle to be updated.
            
            Returns:
                The action to update the obstacle.
            """
        def __init__(self) -> None:
            """
            A container that maps a specific timing to one or multiple actions.
            The static methods of this class do not change the visualization in
            Jacobi Studio immediately, but only return an action that can be
            executed later (e.g. alongside a trajectory).
            
            The `Events` struct allows for scheduling actions in Jacobi Studio at
            specific times. Static methods are provided to create various actions,
            which can be executed later.
            """
        def __setitem__(self, arg0: float, arg1: Studio.Action) -> None:
            ...
    def __init__(self, auto_sync: bool = True, auto_connect: bool = True, timeout: float = 3.0) -> None:
        """
        Interface Jacobi Studio via code. Connects to Jacobi Studio
        automatically - please make sure to enable the Studio Live feature in
        the Jacobi Studio settings.
        
        Parameter ``auto_sync``:
            Whether to sync changes of the environment to Studio Live
            automatically. Only a subset of commands are supported right now,
            including: Environment::add_obstacle,
            Environment::remove_obstacle, Environment::update_joint_position,
            RobotArm::set_end_effector, RobotArm::set_item
        
        Parameter ``auto_connect``:
            Whether to connect to Studio Live automatically.
        
        Parameter ``timeout``:
            The timeout for connecting to Studio Live.
        """
    def add_camera(self, camera: Camera) -> bool:
        """
        Adds a camera in Jacobi Studio.
        
        Parameter ``camera``:
            The camera to be added.
        """
    def add_obstacle(self, obstacle: Obstacle) -> bool:
        """
        Adds the given obstacle to the environment.
        
        Parameter ``obstacle``:
            The obstacle to be added.
        """
    def add_robot(self, robot: Robot) -> bool:
        """
        Adds the given robot to the environment.
        
        Parameter ``robot``:
            The robot to be added.
        """
    def add_robot_path(self, points: list[list[float]], robot: Robot = None, name: str = '', color: str = '', stroke: float = -1.0, arrow_size: float = 1.0) -> bool:
        """
        Adds a visualization of a path for the given robot.
        
        Parameter ``points``:
            The points defining the path.
        
        Parameter ``robot``:
            Optional robot associated with the path.
        
        Parameter ``name``:
            Optional name for the path.
        
        Parameter ``color``:
            Optional color for the path visualization.
        
        Parameter ``stroke``:
            Optional stroke width for the path visualization.
        
        Parameter ``arrow_size``:
            Optional size of arrow for end of path
        """
    def add_waypoint(self, point: list[float] | Waypoint | CartesianWaypoint | MultiRobotPoint | Region | CartesianRegion) -> bool:
        """
        Adds the given Cartesian waypoint to the environment.
        
        Parameter ``point``:
            The Cartesian waypoint to be added.
        """
    def get_camera_image_encoded(self, stream: CameraStream, camera: Camera = None) -> str:
        """
        Get an image from a camera encoded as a string.
        
        Parameter ``stream``:
            The type of camera stream to get.
        
        Parameter ``camera``:
            Optional camera to get the image from.
        
        Returns:
            The encoded image from the camera.
        """
    def get_joint_position(self, robot: Robot = None) -> list[float]:
        """
        Get the joint position of a robot.
        
        Parameter ``robot``:
            Optional robot to get the joint position for.
        
        Returns:
            The joint position of the robot.
        """
    def reconnect(self, timeout: float = 3.0) -> bool:
        """
        Reconnect to Studio Live
        
        Parameter ``timeout``:
            The timeout for reconnecting to Studio Live.
        
        Returns:
            Whether the reconnection was successful.
        """
    def remove_by_name(self, name: str) -> bool:
        """
        Removes the elements of the given name from the environment.
        
        Parameter ``name``:
            The name to be removed.
        """
    def remove_by_tag(self, tag: str) -> bool:
        """
        Removes the elements containing the tag from the environment.
        
        Parameter ``tag``:
            The tag to be removed.
        """
    def remove_camera(self, camera: Camera) -> bool:
        """
        Removes a camera in Jacobi Studio.
        
        Parameter ``camera``:
            The camera to be removed.
        """
    def remove_obstacle(self, obstacle: Obstacle) -> bool:
        """
        Removes the given obstacle (by name) from the environment.
        
        Parameter ``obstacle``:
            The obstacle to be removed.
        """
    def remove_obstacles_by_tag(self, tag: str) -> bool:
        """
        Removes the obstacles containing the tag from the environment.
        
        Parameter ``tag``:
            The tag to be removed.
        """
    def remove_robot_path(self, robot: Robot, name: str) -> bool:
        """
        Removes a named visualization of a path for the given robot.
        
        Parameter ``robot``:
            The robot associated with the path.
        
        Parameter ``name``:
            The name of the path to be removed.
        """
    def reset(self) -> bool:
        """
        Resets the environment to the state before a trajectory or events were
        run. In particular, it removes all obstacles there were added
        dynamically.
        """
    def run_action(self, action: Studio.Action) -> bool:
        """
        Run the given action in Jacobi Studio.
        
        Parameter ``action``:
            The action to be run.
        
        Returns:
            Was the action successfully sent to Studio?
        """
    def run_events(self, events: Studio.Events) -> bool:
        """
        Run the events at the specified timings in Jacobi Studio.
        
        Parameter ``events``:
            The events to be run at the specified timings.
        """
    def run_path_command(self, path_command: PathCommand, duration: float, events: Studio.Events = ..., loop_forever: bool = False, robot: Robot = None) -> bool:
        """
        Visualize a path command for the given robot (or the last active
        robot) in Jacobi Studio, alongside the events at the specified
        timings. Optionally, the visualization can be looped.
        
        Parameter ``path_command``:
            The path command to be run.
        
        Parameter ``duration``:
            The duration of the resulting trajectory.
        
        Parameter ``events``:
            The events to be run at the specified timings.
        
        Parameter ``loop_forever``:
            Whether to loop the visualization forever.
        
        Parameter ``robot``:
            Optional robot to run the trajectory for.
        """
    def run_trajectories(self, trajectories: list[tuple[Trajectory, Robot]], events: Studio.Events = ..., loop_forever: bool = False) -> bool:
        """
        Runs multiple trajectories for different robots in parallel, alongside
        the events at the specified timings. Optionally, the visualization can
        be looped.
        
        Parameter ``trajectories``:
            Pairs of trajectories per robot to be run.
        
        Parameter ``events``:
            The events to be run at the specified timings.
        
        Parameter ``loop_forever``:
            Whether to loop the visualization forever.
        """
    def run_trajectory(self, trajectory: Trajectory, events: Studio.Events = ..., loop_forever: bool = False, robot: Robot = None) -> bool:
        """
        Runs a trajectory for the given robot (or the last active robot) in
        Jacobi Studio, alongside the events at the specified timings.
        Optionally, the visualization can be looped.
        
        Parameter ``trajectory``:
            The trajectory to be run.
        
        Parameter ``events``:
            The events to be run at the specified timings.
        
        Parameter ``loop_forever``:
            Whether to loop the visualization forever.
        
        Parameter ``robot``:
            Optional robot to run the trajectory for.
        """
    def set_camera_depth_map(self, depths: list[list[float]], x: float, y: float, camera: Camera = None) -> bool:
        """
        Sets the depth map visualization of a camera.
        
        Parameter ``depths``:
            The depth map data.
        
        Parameter ``x``:
            Size of the depth map along the x-axis.
        
        Parameter ``y``:
            Size of the depth map along the y-axis.
        
        Parameter ``camera``:
            Optional camera associated with the depth map.
        """
    def set_camera_image_encoded(self, image: str, camera: Camera) -> bool:
        """
        Sets an image for a camera encoded as a string.
        
        Parameter ``image``:
            The encoded image to be set.
        
        Parameter ``camera``:
            Optional camera associated with the image.
        """
    def set_camera_point_cloud(self, points: list[float], camera: Camera = None) -> bool:
        """
        Sets the point cloud visualization of a camera.
        
        Parameter ``points``:
            The point cloud data.
        
        Parameter ``camera``:
            Optional camera associated with the point cloud.
        """
    def set_end_effector(self, obstacle: Obstacle | None, robot: Robot = None) -> bool:
        """
        Sets the end-effector of the given robot, or the last active robot
        instead.
        
        Parameter ``obstacle``:
            Optional obstacle to be set.
        
        Parameter ``robot``:
            Optional robot associated with the obstacle.
        """
    def set_io_signal(self, name: str, value: int | float, robot: Robot = None) -> bool:
        """
        Sets an I/O signal of the given robot, or the last active robot
        instead.
        
        Parameter ``name``:
            The name of the I/O signal.
        
        Parameter ``value``:
            The value to be set for the I/O signal.
        
        Parameter ``robot``:
            Optional robot associated with the I/O signal.
        """
    def set_item(self, obstacle: Obstacle | None, robot: Robot = None) -> bool:
        """
        Sets the item obstacle of the given robot, or the last active robot
        instead.
        
        Parameter ``obstacle``:
            Optional obstacle to be set.
        
        Parameter ``robot``:
            Optional robot associated with the obstacle.
        """
    def set_joint_position(self, joint_position: list[float], robot: Robot = None) -> bool:
        """
        Sets the joint position of the given robot, or the last active robot
        instead.
        
        Parameter ``joint_position``:
            The desired joint position.
        
        Parameter ``robot``:
            Optional robot to set the joint position for.
        """
    def set_material(self, material: str, robot: Robot = None) -> bool:
        """
        Sets the material of the given robot, or the last active robot
        instead.
        
        Parameter ``material``:
            The material to be set.
        
        Parameter ``robot``:
            Optional robot associated with the material.
        """
    def update_camera(self, camera: Camera) -> bool:
        """
        Updates the camera with the same name in Jacobi Studio.
        
        Parameter ``camera``:
            The camera to be updated.
        """
    def update_obstacle(self, obstacle: Obstacle) -> bool:
        """
        Updates the obstacle with the same name.
        
        Parameter ``obstacle``:
            The obstacle to be updated.
        """
    @property
    def is_connected(self) -> bool:
        """
        Whether the library is connected to Studio Live
        
        Returns:
            Whether the library is connected to Studio Live.
        """
    @property
    def port(self) -> int:
        """
        Port of the websocket connection
        """
    @port.setter
    def port(self, arg0: int) -> None:
        ...
    @property
    def speedup(self) -> float:
        """
        A factor to speed up or slow down running trajectories or events.
        """
    @speedup.setter
    def speedup(self, arg0: float) -> None:
        ...
class Trainer:
    class Result:
        @property
        def duration(self) -> float:
            ...
        @property
        def is_valid(self) -> bool:
            ...
        @property
        def loss(self) -> float:
            ...
    def __init__(self, environment: Environment, motion: Motion, max_number_waypoints: int) -> None:
        ...
    def calculate_motion_with_waypoints(self, start: Waypoint, goal: Waypoint, intermediate_positions: list[list[float]]) -> Trainer.Result:
        ...
    def is_direct_motion_valid(self, start: Waypoint, goal: Waypoint) -> bool:
        ...
    @property
    def max_number_waypoints(self) -> int:
        ...
class Trajectory:
    """
    A robot's trajectory as a list of positions, velocities and
    accelerations at specific times.
    
    The Trajectory class represents a sequence of kinematic states of a
    robot over a specified duration. It maintains lists of positions,
    velocities, and accelerations at particular time stamps.
    """
    @staticmethod
    def from_json(json: str) -> Trajectory:
        """
        Loads a trajectory from a json string.
        """
    @staticmethod
    def from_json_file(file: os.PathLike) -> Trajectory:
        """
        Loads a trajectory from a *.json file.
        
        Parameter ``file``:
            The path to the *.json file.
        
        Returns:
            Trajectory The loaded trajectory.
        """
    def __getstate__(self) -> tuple:
        ...
    def __iadd__(self, arg0: Trajectory) -> Trajectory:
        ...
    def __init__(self, degrees_of_freedom: int) -> None:
        """
        Create an empty trajectory with the given degrees of freedom
        
        Parameter ``dofs``:
            The degrees of freedom of the joint space.
        """
    def __len__(self) -> int:
        """
        The number of time steps within the trajectory.
        
        Returns:
            The number of time steps within the trajectory.
        """
    def __repr__(self) -> str:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def append(self, other: Trajectory) -> None:
        """
        Append another trajectory to the current one.
        
        Parameter ``other``:
            The trajectory to append. Ignores the first time step if the
            trajectory starts at zero and the trajectory to append to is
            already non-empty.
        """
    def as_table(self) -> str:
        """
        To pretty print the trajectory as a table of positions
        """
    def at_time(self, time: float) -> tuple:
        ...
    def back(self) -> State:
        """
        Access the last state at t=duration of the trajectory
        
        Returns:
            The last state at t=duration of the trajectory.
        """
    def filter_path(self, max_distance: list[float]) -> list[list[float]]:
        """
        Filter a path of sparse waypoints from the trajectory
        
        The path has a maximum distance per degree of freedom between the
        linear interpolation of the sparse waypoints and the original
        trajectory.
        
        Parameter ``max_distance``:
            The maximum allowable distance between joint positions.
        
        Returns:
            std::vector<Config> A list of sparse waypoints filtered from the
            trajectory.
        """
    def front(self) -> State:
        """
        Access the first state at t=0 of the trajectory
        
        Returns:
            The first state at t=0 of the trajectory.
        """
    def get_step_closest_to(self, position: list[float]) -> int:
        """
        Get step at which the trajectory is closest (in terms of the L2 norm
        in joint space) to the reference position
        
        Returns:
            size_t The step index of the closest position.
        """
    def reverse(self) -> Trajectory:
        """
        Reverse the trajectory's start and goal
        
        Returns:
            Trajectory A new trajectory with the start and end points
            reversed.
        """
    def scale(self, speed: float, keep_delta_time: bool = True) -> Trajectory:
        """
        Temporally scale the trajectory by a given speed factor.
        
        Parameter ``speed``:
            Factor to scale the trajectory speed (greater than 1 speeds up,
            less than 1 slows down).
        
        Parameter ``keep_delta_time``:
            If true (default), maintains the original time intervals between
            trajectory points.
        
        Returns:
            Trajectory A new scaled Trajectory object.
        """
    def slice(self, start: int, steps: int) -> Trajectory:
        """
        Slice a trajectory starting from step start for a length of steps.
        
        Parameter ``start``:
            The starting index of the slice.
        
        Parameter ``steps``:
            The number of steps to include in the slice.
        
        Returns:
            Trajectory A new trajectory containing the specified slice of the
            original.
        """
    def to_json(self) -> str:
        """
        Serializes a trajectory to a json string.
        """
    def to_json_file(self, file: os.PathLike) -> None:
        """
        Saves a trajectory to a *.json file.
        
        Parameter ``file``:
            The path to the *.json file.
        """
    def update_first_position(self, joint_position: list[float]) -> None:
        """
        Update the first position of the trajectory
        
        Parameter ``joint_position``:
            The new position to set at the start of the trajectory.
        """
    @property
    def accelerations(self) -> list[list[float]]:
        """
        The joint accelerations along the trajectory.
        """
    @property
    def duration(self) -> float:
        """
        The total duration in [s]
        """
    @property
    def id(self) -> str:
        """
        Field for identifying trajectories (for the user)
        """
    @id.setter
    def id(self, arg0: str) -> None:
        ...
    @property
    def max_acceleration(self) -> list[float]:
        """
        Get the maximum acceleration along the trajectory for each degree of
        freedom individually
        
        Returns:
            Config The maximum acceleration value for each degree of freedom
            across the trajectory.
        """
    @property
    def max_position(self) -> list[float]:
        """
        Get the maximum position along the trajectory for each degree of
        freedom individually
        
        Returns:
            Config The maximum position value for each degree of freedom
            across the trajectory.
        """
    @property
    def max_velocity(self) -> list[float]:
        """
        Get the maximum velocity along the trajectory for each degree of
        freedom individually
        
        Returns:
            Config The maximum velocity value for each degree of freedom
            across the trajectory.
        """
    @property
    def min_acceleration(self) -> list[float]:
        """
        Get the minimum acceleration along the trajectory for each degree of
        freedom individually
        
        Returns:
            Config The minimum acceleration value for each degree of freedom
            across the trajectory.
        """
    @property
    def min_position(self) -> list[float]:
        """
        Get the minimum position along the trajectory for each degree of
        freedom individually
        
        Returns:
            Config The minimum position value for each degree of freedom
            across the trajectory.
        """
    @property
    def min_velocity(self) -> list[float]:
        """
        Get the minimum velocity along the trajectory for each degree of
        freedom individually
        
        Returns:
            Config The minimum velocity value for each degree of freedom
            across the trajectory.
        """
    @property
    def motion(self) -> str:
        """
        Name of the motion this trajectory was planned for
        """
    @motion.setter
    def motion(self, arg0: str) -> None:
        ...
    @property
    def positions(self) -> list[list[float]]:
        """
        The joint positions along the trajectory.
        """
    @property
    def times(self) -> list[float]:
        """
        The exact time stamps for the position, velocity, and acceleration
        values. The times will usually be sampled at the delta_time distance
        of the Planner class, but might deviate at the final step.
        """
    @property
    def velocities(self) -> list[list[float]]:
        """
        The joint velocities along the trajectory.
        """
class Twist:
    """
    Represents a velocity in 3D Cartesian space.
    
    The Twist struct represents a 6-dimensional vector used to describe
    velocity in 3D Cartesian space. It consists of linear velocities in
    the x, y, and z directions, and angular velocities around these axes.
    """
    def __init__(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> None:
        """
        Default constructor.
        """
class Waypoint(Element):
    """
    A joint-space waypoint with possible position, velocity, and/or
    acceleration values.
    
    The Waypoint class represents a point in the joint space of a robot
    with associated position, velocity, and acceleration values.
    """
    def __getstate__(self) -> tuple:
        ...
    @typing.overload
    def __init__(self, position: list[float]) -> None:
        """
        Construct a waypoint by position data.
        
        Parameter ``data``:
            A list of position values to initialize the waypoint.
        """
    @typing.overload
    def __init__(self, position: list[float], velocity: list[float]) -> None:
        """
        Construct a waypoint with given position and zero velocity and
        acceleration.
        
        Parameter ``position``:
            The joint position to initialize the waypoint.
        """
    @typing.overload
    def __init__(self, position: list[float], velocity: list[float], acceleration: list[float]) -> None:
        """
        Construct a waypoint with given position and velocity and zero
        acceleration.
        
        Parameter ``position``:
            The joint position to initialize the waypoint.
        
        Parameter ``velocity``:
            The joint velocity to initialize the waypoint.
        """
    def __setstate__(self, arg0: tuple) -> None:
        ...
    def is_within(self, other: Waypoint) -> bool:
        ...
    @property
    def acceleration(self) -> list[float]:
        """
        The joint acceleration at the waypoint.
        """
    @acceleration.setter
    def acceleration(self, arg0: list[float]) -> None:
        ...
    @property
    def position(self) -> list[float]:
        """
        The joint position at the waypoint.
        """
    @position.setter
    def position(self, arg0: list[float]) -> None:
        ...
    @property
    def velocity(self) -> list[float]:
        """
        The joint velocity at the waypoint.
        """
    @velocity.setter
    def velocity(self, arg0: list[float]) -> None:
        ...
def activate_license() -> None:
    ...
def start_studio_daemon() -> int:
    ...
def start_telemetry_daemon() -> int:
    ...
Color: CameraStream  # value = <CameraStream.Color: 0>
Continuous: JointType  # value = <JointType.Continuous: 1>
Depth: CameraStream  # value = <CameraStream.Depth: 1>
Fixed: JointType  # value = <JointType.Fixed: 3>
Prismatic: JointType  # value = <JointType.Prismatic: 2>
Revolute: JointType  # value = <JointType.Revolute: 0>
__version__: str = '1.1.7'
