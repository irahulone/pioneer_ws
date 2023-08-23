import os

from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node



def generate_launch_description():
    ld = LaunchDescription()
    
    # Nodes to launch
    drive_core = Node(
        package="locomotion_core",
        executable="movebase_kinematics",
    )

    cmd_roboteq = Node(
        package="rsl_roboteq",
        executable="roboteq_node",
    )

    obstacle_node = Node(
        package="navigation_core",
        executable="lidar_node",
    )

    # include another launch file
    launch_joy = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('teleop_twist_joy'),
                'launch/teleop-launch.py'))
    )

     # include another launch file
    launch_lidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rplidar_ros'),
                'launch/rplidar_a3_launch.py'))
    )

    
    ld.add_action(launch_joy)
    ld.add_action(drive_core)
    ld.add_action(cmd_roboteq)
    ld.add_action(launch_lidar)
    ld.add_action(obstacle_node)

    return ld


