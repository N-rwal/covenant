import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory('covenant_main')

    # === CONFIG PATHS ===
    config_paths = {
        'custom_nav_launch': os.path.join(pkg_share, 'launch', 'custom_navigation_launch.py'),
        'nav2_params': os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
        'default_map': os.path.join(pkg_share, 'config', 'map.yaml'),
    }

    # === LAUNCH CONFIG ===
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    with_nav2 = LaunchConfiguration('nav2', default='true')
    map_yaml = LaunchConfiguration('map', default=config_paths['default_map'])
    params_file = LaunchConfiguration('params_file', default=config_paths['nav2_params'])

    launch_args = [
        DeclareLaunchArgument('nav2', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('map', default_value=config_paths['default_map']),
        DeclareLaunchArgument('params_file', default_value=config_paths['nav2_params']),
    ]

    # === CORE NODES ===
    core_nodes = [

        # micro ROS bridge (your FC)
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=[
                'serial',
                '--dev', '/dev/ttyAMA0',
                '-b', '921600'
            ]
        ),

        # TF: base -> lidar
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_lidar_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'ldlidar_link']
        ),

        # TF: map -> odom (static for now, AMCL will take over later)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='map_to_odom',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
        ),
    ]

    # === LIDAR (delayed startup) ===
    lidar_launch = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory('ldlidar_node'),
                        'launch',
                        'ldlidar_bringup.launch.py'
                    )
                )
            )
        ]
    )

    # === NAVIGATION STACK ===
    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([config_paths['custom_nav_launch']]),
        condition=IfCondition(with_nav2),
        launch_arguments={
            'map': map_yaml,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
        }.items()
    )

    # === CUSTOM NODES ===

    controller_node = Node(
        package='covenant_main',
        executable='nav_controller',
        name='nav_controller',
        output='screen'
    )

    topic_sender = Node(
        package='covenant_main',
        executable='ros_topics_udp_bridge',
        name='ros_topics_udp_bridge',
        output='screen'
    )

    arming = Node(
        package='covenant_main',
        executable='arm_command_udp_server',
        name='arm_command_udp_server',
        output='screen'
    )

    # optional delayed startup (after nav ready)
    delayed_custom = TimerAction(
        period=10.0,
        actions=[controller_node]
    )

    # === FINAL LAUNCH ===
    return LaunchDescription(
        launch_args +
        core_nodes +
        [
            lidar_launch,
            nav_launch,
            delayed_custom,
            topic_sender,
            arming
        ]
    )
