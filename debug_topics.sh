#!/bin/bash
# HyperDog Topic Debug Script

echo "================================================"
echo "HyperDog Topic Debugging"
echo "================================================"
echo ""
echo "Make sure robot is started and you pressed W key!"
echo ""

echo "1. Checking /hyperdog_joy_ctrl_cmd (keyboard commands):"
timeout 2 ros2 topic echo /hyperdog_joy_ctrl_cmd | head -30
echo ""

echo "2. Checking /hyperdog_geometry (to IK):"
timeout 2 ros2 topic echo /hyperdog_geometry | head -30
echo ""

echo "3. Checking /hyperdog_jointController/commands (from IK):"
timeout 2 ros2 topic echo /hyperdog_jointController/commands | head -20
echo ""

echo "================================================"
echo "Debugging complete!"
echo "================================================"
