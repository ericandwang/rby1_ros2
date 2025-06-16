from launch import LaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    NotSubstitution,
    AndSubstitution,
)
from launch.actions import (
    ExecuteProcess,
    DeclareLaunchArgument,
    RegisterEventHandler,
    SetEnvironmentVariable,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
import launch_ros
from ament_index_python import get_package_prefix
from launch.substitutions import PathJoinSubstitution, TextSubstitution
from ament_index_python.packages import get_package_share_directory

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
                'lakibeam1_scan_dual_lidar.launch.py'
            ])
        ])
    )

def lidar_merge():
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('multi-laserscan-toolbox-ros2'),
                'launch',
                'laserscan_toolbox.launch.py'
            ])
        ])
    )

def generate_launch_description():
    package_name = 'rby1_description'
    pkg_share = FindPackageShare(package='rby1_description').find('rby1_description')
    #default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'rby2.rviz')
    twist_mux_params = os.path.join(pkg_share,'config','twist_mux.yaml')

    ###################
    use_sim_time = LaunchConfiguration("use_sim_time")
    #use_rviz = LaunchConfiguration("use_rviz")
    use_localization = LaunchConfiguration("use_localization")
    ###################




    # Note: make sure mode in config file is set to desired behavior: mapping or localization (must provide map)
    slam_params = os.path.join(get_package_share_directory(package_name),'config','mapper_params_online_async.yaml')
    slam_node = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','online_async_launch.py'
                )]), launch_arguments={'use_sim_time': use_sim_time,'slam_params_file': slam_params}.items()
    )

    nav2_params = os.path.join(get_package_share_directory(package_name),'config','nav2_params.yaml')
    nav2_node = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','navigation_launch.py'
                )]), launch_arguments={'use_sim_time': use_sim_time,'params_file': nav2_params}.items()
    )

    """
    # Convert TwistStamped to Twist
    unstamper = Node(
        package='twist_stamper',
        executable='twist_unstamper',
        remappings=[
            ('/cmd_vel_in', '/key_vel'),  # Input TwistStamped topic 1
            ('/cmd_vel_out', '/key_vel_unstamped')  # Output Twist topic 1
        ]
    )
    # Multiplex Twist messages
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        arguments=[twist_mux_params, {'use_sim_time': use_sim_time}],
        remappings=[
            ('/cmd_vel_out', '/muxed/cmd_vel_unstamped'),
        ],
    )
    # Convert multiplexed Twist back to TwistStamped
    stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        remappings=[
            ('/cmd_vel_in', '/muxed/cmd_vel_unstamped'),
            ('/cmd_vel_out', '/rby1_base_controller/cmd_vel')
        ],
        parameters=[
            {'frame_id': 'base'}  # Set your desired frame_id
        ]
    )
    """


    return LaunchDescription([
        DeclareLaunchArgument(name='use_sim_time', default_value='False', description='Flag to enable use_sim_time'),
        slam_node,
        #unstamper,
        #stamper,
        #twist_mux,
        # nav2_node,
        bringup_module(),
        lakibeam1_module(),
        lidar_merge()
    ])
