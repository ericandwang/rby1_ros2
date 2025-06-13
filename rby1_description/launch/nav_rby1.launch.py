from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, TextSubstitution

def bringup_module():
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('rby1_bringup'),
                'launch',
                'bringup.launch.py'
            ])
        ]),
        launch_arguments={
            'robot_ip': TextSubstitution(text='192.168.30.1:50051')
        }.items()
    )

def lakibeam1_module():
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('lakibeam1'),
                'launch',
                'lakibeam1_scan.launch.py'
            ])
        ]),
        launch_arguments={
            'hostip': TextSubstitution(text='192.168.30.10')
        }.items()
    )

def generate_launch_description():
    return LaunchDescription([
        bringup_module(),
        lakibeam1_module()
    ])
