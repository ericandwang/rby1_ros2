from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessStart, OnProcessExit

def generate_launch_description():
    xacro_file = PathJoinSubstitution([
        FindPackageShare('rby1_description'),
        'urdf',
        'rby1.urdf.xacro'
    ])

    robot_description_content = Command([
        'xacro ', xacro_file,
        ' initial_positions_file:=',
        PathJoinSubstitution([
            FindPackageShare('rby1_description'),
            'urdf',
            'initial_positions.yaml'
        ]),
        ' robot_ip:=', LaunchConfiguration('robot_ip')
    ])

    robot_description = ParameterValue(robot_description_content, value_type=str)

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare('rby1_bringup'),
        'config',
        'rby1_controllers.yaml'
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}],
    )

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            controllers_yaml
        ],
        remappings=[('robot_description', '/robot_description')],
        output='screen'
    )

    #dualarm_controller_spawner = Node(
    #    package='controller_manager',
    #    executable='spawner',
    #    arguments=['rby1_dualarm_controller'],
    #    output='screen'
    #)

    left_arm_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['rby1_left_arm_controller'],
        output='screen'
    )

    right_arm_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['rby1_right_arm_controller'],
        output='screen'
    )
    
    base_spawner = Node(
    	package='controller_manager',
    	executable='spawner',
    	arguments=['rby1_base_controller'],
    	output='screen'
    )

    init_base_on_start = Node(
        package='rby1_moveit_client',
        executable='init_base',
        name='init_base_start',
        output='screen'
    )

    #init_base_on_exit = Node(
    #    package='rby1_moveit_client',
    #    executable='init_base',
    #    name='init_base_exit',
    #    output='screen'
    #)

    #wheel_spawner = Node(
    #    package='controller_manager',
    #    executable='spawner',
    #    arguments=['diff_drive_controller'],
    #    output='screen'
    #)

    controller_event_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=ros2_control_node,
            on_start=[left_arm_spawner, right_arm_spawner, base_spawner]
        )
    )

    rqt_controller_manager = ExecuteProcess(
        cmd=['ros2', 'run', 'rqt_controller_manager', 'rqt_controller_manager', '--force-discover'],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        ros2_control_node,
        controller_event_handler,
        rqt_controller_manager,
        RegisterEventHandler(
            OnProcessStart(
                target_action=base_spawner,
                on_start=[
                    init_base_on_start
                ]
            )
        ),
        #RegisterEventHandler(
        #    OnProcessExit(
        #        target_action=base_spawner,
        #        on_exit=[
        #            init_base_on_exit
        #        ]
        #    )
        #),
    ])
