from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'covenant_main'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
    (
        'share/ament_index/resource_index/packages',
        ['resource/' + package_name]
    ),
    (
        'share/' + package_name,
        ['package.xml']
    ),
    (
        os.path.join('share', package_name, 'launch'),
        glob('launch/*.py')
    ),
    (
        os.path.join('share', package_name, 'config'),
        glob('config/*.yaml')
    ),
	],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='glasser',
    maintainer_email='todo@mail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'arm_command_udp_server = covenant_main.arm_command_udp_server:main',
            'ros_topics_udp_bridge = covenant_main.ros_topics_udp_bridge:main',
            'test_udp_sender_lidar = covenant_main.test_udp_sender_lidar:main',
        ],
    },
)
