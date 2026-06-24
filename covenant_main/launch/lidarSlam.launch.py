from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():

    ldlidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ldlidar_node'),
                'launch',
                'ldlidar_bringup.launch.py'
            )
        )
    )

    fake_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'odom',
            'ldlidar_base'
        ]
    )

    slam_params = os.path.join(
        get_package_share_directory('covenant_main'),
        'config',
        'mapper_params_online_async.yaml'
    )

    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params],
        remappings=[
            ('scan', '/ldlidar_node/scan')
        ]
    )
    
    lc_mgr_node = Node(
    	package='nav2_lifecycle_manager',
    	executable='lifecycle_manager',
   	 name='lifecycle_manager',
   	 output='screen',
    	parameters=[{
        	'use_sim_time': False,
        	'autostart': True,
        	'node_names': ['ldlidar_node']
    	}]
)

    return LaunchDescription([
        ldlidar_launch,
        fake_odom,
        slam,
        lc_mgr_node,
    ])
