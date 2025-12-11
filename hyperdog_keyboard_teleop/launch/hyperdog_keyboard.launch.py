#!/usr/bin/env python3
# __________________________________________________________________________________
# HyperDog Keyboard Teleop Launch File
#
# Launches all necessary nodes for keyboard control:
# - keyboard_teleop_node (keyboard input)
# - cmd_manager_node (command processing)
# - IK_node (inverse kinematics)
# __________________________________________________________________________________

from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler, LogInfo
from launch.event_handlers import OnProcessStart


def generate_launch_description():
    """
    Launch file for HyperDog keyboard teleoperation.

    Usage:
        Terminal 1: ros2 launch hyperdog_gazebo_sim hyperdog_gazebo_sim.launch.py
        Terminal 2: ros2 launch hyperdog_keyboard_teleop hyperdog_keyboard.launch.py
    """

    # Keyboard teleop node (replaces joy_node + hyperdog_teleop_joy_node)
    node_keyboard_teleop = ExecuteProcess(
        cmd=['ros2', 'run', 'hyperdog_keyboard_teleop', 'keyboard_teleop'],
        output='screen'
    )

    # Command manager node (receives keyboard commands)
    node_cmd_manager = ExecuteProcess(
        cmd=['ros2', 'run', 'hyperdog_ctrl', 'cmd_manager_node'],
        output='screen'
    )

    # Inverse kinematics node
    node_IK = ExecuteProcess(
        cmd=['ros2', 'run', 'hyperdog_ctrl', 'IK_node'],
        output='screen'
    )

    return LaunchDescription([
        # Start keyboard_teleop first
        node_keyboard_teleop,

        # When keyboard_teleop starts, launch cmd_manager
        RegisterEventHandler(
            OnProcessStart(
                target_action=node_keyboard_teleop,
                on_start=[
                    LogInfo(msg='Keyboard teleop started, starting cmd_manager'),
                    node_cmd_manager,
                ]
            )
        ),

        # When cmd_manager starts, launch IK_node
        RegisterEventHandler(
            OnProcessStart(
                target_action=node_cmd_manager,
                on_start=[
                    LogInfo(msg='cmd_manager started, starting IK_node'),
                    node_IK
                ]
            )
        ),
    ])
