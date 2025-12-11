#!/bin/bash
# HyperDog Topic Debug Script

echo "================================================"
echo "HyperDog Topic Debugging"
echo "================================================"
echo ""

echo "1. Checking /hyperdog_joy_ctrl_cmd (keyboard commands):"
echo "   Press Ctrl+C after seeing a few messages..."
timeout 3 ros2 topic echo /hyperdog_joy_ctrl_cmd --once
echo ""

echo "2. Checking /hyperdog_geometry (to IK):"
timeout 3 ros2 topic echo /hyperdog_geometry --once
echo ""

echo "3. Checking /hyperdog_jointController/commands (from IK):"
timeout 3 ros2 topic echo /hyperdog_jointController/commands --once
echo ""

echo "================================================"
echo "Debugging complete!"
echo "================================================"
