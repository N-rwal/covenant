from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_share = get_package_share_directory('covenant_main')

    # --- micro-ROS agent ---
    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        output='screen',
        arguments=[
            'serial',
            '--dev', '/dev/ttyAMA0',
            '-b', '921600'
        ]
    )

    # --- LiDAR ---
    ldlidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ldlidar_node'),
                'launch',
                'ldlidar_bringup.launch.py'
            )
        )
    )

    # --- lifecycle ---
    lc_mgr_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'autostart': True,
            'node_names': [
                'ldlidar_node',
                'slam_toolbox'
            ]
        }]
    )

    # --- TF base -> lidar ---
    base_to_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'base_link',
            'ldlidar_link'
        ]
    )

    # --- fake odom (IMPORTANT) ---
    odom_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'odom',
            'base_link'
        ]
    )

    # --- SLAM ---
    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[
            os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')
        ],
        remappings=[
            ('scan', '/ldlidar_node/scan')
        ],
        output='screen'
    )

    # delay slam until lidar is ready
    delayed = TimerAction(
        period=5.0,
        actions=[slam]
    )

    return LaunchDescription([
        micro_ros_agent,
        ldlidar_launch,
        lc_mgr_node,
        base_to_lidar,
        odom_to_base,
        delayed
    ])
