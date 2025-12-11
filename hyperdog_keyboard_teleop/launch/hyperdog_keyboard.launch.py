#!/usr/bin/env python3
# __________________________________________________________________________________
# HyperDog Keyboard Backend Launch File
#
# Launches backend nodes for keyboard control:
# - cmd_manager_node (command processing)
# - IK_node (inverse kinematics)
#
# NOTE: keyboard_teleop MUST be run separately in a terminal with keyboard input!
# __________________________________________________________________________________

from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler, LogInfo
from launch.event_handlers import OnProcessStart


def generate_launch_description():
    """
    Launch file for HyperDog keyboard teleoperation backend.

    Usage:
        Terminal 1: ros2 launch hyperdog_gazebo_sim hyperdog_gazebo_sim.launch.py
        Terminal 2: ros2 launch hyperdog_keyboard_teleop hyperdog_keyboard.launch.py
        Terminal 3: ros2 run hyperdog_keyboard_teleop keyboard_teleop

    Why 3 terminals?
    - keyboard_teleop requires direct keyboard input (stdin)
    - Launch files run processes in background without terminal access
    - Therefore, keyboard_teleop must run in a foreground terminal
    """

    # Command manager node (receives keyboard commands via topic)
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
        # Print usage instructions
        LogInfo(msg=''),
        LogInfo(msg='================================================'),
        LogInfo(msg='HyperDog Keyboard Control - Backend Nodes'),
        LogInfo(msg='================================================'),
        LogInfo(msg='Starting cmd_manager and IK_node...'),
        LogInfo(msg=''),
        LogInfo(msg='IMPORTANT: Run keyboard_teleop in another terminal:'),
        LogInfo(msg='  ros2 run hyperdog_keyboard_teleop keyboard_teleop'),
        LogInfo(msg='================================================'),
        LogInfo(msg=''),

        # Start cmd_manager first
        node_cmd_manager,

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
