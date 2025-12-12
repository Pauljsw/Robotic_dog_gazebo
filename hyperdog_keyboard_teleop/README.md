# HyperDog Keyboard Teleoperation

This package provides keyboard control for the HyperDog quadruped robot, as an alternative to the joystick control.

## Installation

This package is already included in the workspace. Build it with:
```bash
cd ~/hyperdog_ws
colcon build --packages-select hyperdog_keyboard_teleop
source install/setup.bash
```

## Usage

**Terminal 1: Gazebo Simulation**
```bash
ros2 launch hyperdog_gazebo_sim hyperdog_gazebo_sim.launch.py
```

**Terminal 2: Control Backend (cmd_manager + IK)**
```bash
ros2 launch hyperdog_keyboard_teleop hyperdog_keyboard.launch.py
```

**Terminal 3: Keyboard Control**
```bash
ros2 run hyperdog_keyboard_teleop keyboard_teleop
```

## Controls

**System:**
- `Enter` - Start/Stop robot
- `V` - Toggle walk mode
- `ESC` - Exit

**Movement:**
- `W` - Forward (100mm step)
- `S` - Backward
- `A` - Turn left (20°)
- `D` - Turn right
- `Q` - Strafe left
- `E` - Strafe right
- `X` - Stop movement

**Adjustments:**
- `R/F` - Increase/Decrease body height (±5mm)
- `T/G` - Increase/Decrease step height (±5mm)

**Gait Patterns:**
- `1` - Give Hand (special pose)
- `2` - Trot (default, recommended)
- `3` - Wave (one leg at a time)
- `4` - Trot Fast

## Known Issues

### Gazebo Sliding Issue (From Original README)

The original HyperDog README states:
> **Known bugs:**
> - gazebo-ros2-control pkg doesn't work properly. So the robot slides on the ground.

**What this means:**
- The robot may appear to slide or not move forward as expected in Gazebo
- This is a known limitation of the `gazebo-ros2-control` package in ROS2 Foxy
- The robot **does work properly on real hardware** using micro-ROS

**Workarounds applied:**
1. Increased ground friction (mu=2.0)
2. Increased foot friction (mu=2.0, restitution=0.0)
3. Optimized physics solver settings
4. Reduced keyboard command values to safe levels

**Realistic expectations in Gazebo:**
- Robot will walk and show proper leg motion
- Forward movement may be limited or slow
- Some sliding may occur despite optimizations
- This is **not a bug in the keyboard teleop** - it's a known Gazebo limitation

### Why Keyboard Values Differ from Joystick

Keyboard is digital (on/off) while joystick is analog (0-100%). Therefore:
- Forward step: 100mm (vs max 250mm) - 40% of maximum
- Turn angle: 20° (vs max 50°) - 40% of maximum
- Strafe: 60mm (vs max 150mm) - 40% of maximum

These conservative values provide stable control and avoid singularities.

## Architecture

```
Keyboard Input (Terminal 3)
    ↓
keyboard_teleop_node
    ↓ (publishes /hyperdog_joy_ctrl_cmd @ 40Hz)
cmd_manager_node (Terminal 2)
    ↓ (publishes /hyperdog_geometry @ 1000Hz)
IK_node (Terminal 2)
    ↓ (publishes /hyperdog_jointController/commands @ 50Hz)
hyperdog_gazebo_joint_ctrl_node (Terminal 1)
    ↓ (publishes /gazebo_joint_controller/commands)
Gazebo Simulation
```

## Comparison with Joystick

| Feature | Joystick | Keyboard |
|---------|----------|----------|
| Input Type | Analog (0-100%) | Digital (Fixed values) |
| Terminals | 2 | 3 |
| Speed Control | Variable | Fixed (40% of max) |
| Best For | Variable speed control | Simple on/off control |

## For Real Hardware

This keyboard teleop works the same way on real hardware. The Gazebo sliding issue does not occur on the physical robot with micro-ROS.

## Troubleshooting

**Robot not moving forward:**
- This is expected to some degree in Gazebo (see Known Issues)
- Check that walk mode is ON (`V` key)
- Verify gait_type is 1 or 2 (press `2` key)

**Robot flipping over:**
- Movement values may be too high
- Current values (100mm, 20°) are tested and stable

**Keyboard input not working:**
- keyboard_teleop MUST run in a foreground terminal (Terminal 3)
- It cannot be launched via launch file due to stdin requirements
