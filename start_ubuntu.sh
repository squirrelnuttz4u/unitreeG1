#!/bin/bash
# Unitree G1 Control Application - Ubuntu Launcher
# Quick launcher script with pre-flight checks

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================"
echo "  Unitree G1 Control Application"
echo "======================================"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found${NC}"
    echo "Please run this script from the unitreeG1 directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    echo "Please install Python 3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} detected${NC}"

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

MISSING_DEPS=0

if ! python3 -c "import customtkinter" 2>/dev/null; then
    echo -e "${YELLOW}⚠ customtkinter not installed${NC}"
    MISSING_DEPS=1
fi

if ! python3 -c "import cv2" 2>/dev/null; then
    echo -e "${YELLOW}⚠ opencv-python not installed${NC}"
    MISSING_DEPS=1
fi

if ! python3 -c "import numpy" 2>/dev/null; then
    echo -e "${YELLOW}⚠ numpy not installed${NC}"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Some dependencies are missing${NC}"
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install -r requirements.txt
    else
        echo -e "${RED}Cannot run without dependencies${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ All dependencies installed${NC}"

# Check SDK
SDK_STATUS="Not installed (Simulation mode)"
if python3 -c "from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient" 2>/dev/null; then
    SDK_STATUS="Installed (Robot control enabled)"
fi

echo -e "${BLUE}SDK Status: ${SDK_STATUS}${NC}"

# Check network connectivity
echo -e "${BLUE}Checking robot connectivity...${NC}"

ROBOT_ONLINE=0
if ping -c 1 -W 1 192.168.123.164 &> /dev/null; then
    echo -e "${GREEN}✓ Robot detected at 192.168.123.164${NC}"
    ROBOT_ONLINE=1
else
    echo -e "${YELLOW}⚠ Robot not detected (will run in simulation mode)${NC}"
fi

# Display mode
echo ""
if [ "$SDK_STATUS" == "Installed (Robot control enabled)" ] && [ $ROBOT_ONLINE -eq 1 ]; then
    echo -e "${GREEN}Mode: ROBOT CONTROL${NC}"
    echo "Ready to control your physical G1 robot!"
    echo ""
    echo -e "${YELLOW}Remember to activate the robot:${NC}"
    echo "  1. Press L1 + A on controller"
    echo "  2. Press L1 + UP on controller"
else
    echo -e "${BLUE}Mode: SIMULATION${NC}"
    echo "Running in simulation mode"
    echo ""
    if [ "$SDK_STATUS" == "Not installed (Simulation mode)" ]; then
        echo -e "${YELLOW}To enable robot control:${NC}"
        echo "  Run: ./install_ubuntu.sh"
    elif [ $ROBOT_ONLINE -eq 0 ]; then
        echo -e "${YELLOW}To connect to robot:${NC}"
        echo "  - Connect to robot's WiFi network"
        echo "  - Or configure static IP for Ethernet"
    fi
fi

echo ""
echo -e "${GREEN}Starting application...${NC}"
echo ""

# Launch application
python3 main.py

# Exit status
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Application closed normally${NC}"
else
    echo -e "${RED}Application exited with error code: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
