#!/bin/bash
# Unitree G1 Control Application - Ubuntu 20.04 Installation Script
# This script automates the installation process on Ubuntu 20.04

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "======================================"
echo "Unitree G1 Control Application"
echo "Ubuntu 20.04 Installation Script"
echo "======================================"
echo -e "${NC}"

# Check if running on Ubuntu
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" != "ubuntu" ]; then
        echo -e "${YELLOW}Warning: This script is designed for Ubuntu. Your OS: $ID${NC}"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for sudo privileges
echo -e "${BLUE}Checking for sudo privileges...${NC}"
if ! sudo -v; then
    echo -e "${RED}Error: This script requires sudo privileges${NC}"
    exit 1
fi

# Update system
echo -e "${BLUE}Updating system packages...${NC}"
sudo apt update
echo -e "${GREEN}✓ System updated${NC}"

# Install system dependencies
echo -e "${BLUE}Installing system dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-tk \
    build-essential \
    cmake \
    git \
    portaudio19-dev \
    python3-pyaudio \
    libopencv-dev \
    python3-opencv \
    espeak \
    espeak-data

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip3 install --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
fi

# Ask about Unitree SDK installation
echo ""
echo -e "${YELLOW}Do you want to install the Unitree SDK for robot control?${NC}"
echo "  - Yes: Install SDK (required for physical robot)"
echo "  - No: Skip SDK (simulation mode only)"
read -p "Install Unitree SDK? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Installing Unitree SDK...${NC}"

    # Check if SDK already exists
    if [ -d "$HOME/unitree_sdk2_python" ]; then
        echo -e "${YELLOW}SDK directory already exists. Updating...${NC}"
        cd "$HOME/unitree_sdk2_python"
        git pull
    else
        cd "$HOME"
        git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
        cd unitree_sdk2_python
    fi

    pip3 install -e .

    # Verify installation
    if python3 -c "from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient" 2>/dev/null; then
        echo -e "${GREEN}✓ Unitree SDK installed successfully!${NC}"
    else
        echo -e "${YELLOW}⚠ SDK installed but verification failed. May still work.${NC}"
    fi

    cd - > /dev/null
else
    echo -e "${YELLOW}Skipping SDK installation. Application will run in simulation mode.${NC}"
fi

# Create desktop shortcut (optional)
echo ""
read -p "Create desktop shortcut? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_FILE="$HOME/Desktop/UnitreeG1.desktop"
    APP_DIR="$(pwd)"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Unitree G1 Control
Comment=Control your Unitree G1 robot
Exec=python3 $APP_DIR/main.py
Path=$APP_DIR
Icon=$APP_DIR/assets/icons/robot.png
Terminal=true
Categories=Development;Science;
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ Desktop shortcut created${NC}"
fi

# Installation complete
echo ""
echo -e "${GREEN}"
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo -e "${NC}"

echo ""
echo "Next steps:"
echo ""
echo -e "${BLUE}1. Connect to your robot:${NC}"
echo "   - WiFi: Connect to robot's network"
echo "   - Ethernet: Configure static IP (see UBUNTU_INSTALL.md)"
echo ""
echo -e "${BLUE}2. Activate robot with controller:${NC}"
echo "   - Press L1 + A (sport mode)"
echo "   - Press L1 + UP (enable SDK)"
echo ""
echo -e "${BLUE}3. Run the application:${NC}"
echo "   cd $(pwd)"
echo "   python3 main.py"
echo ""
echo -e "${BLUE}4. Read the documentation:${NC}"
echo "   - Full guide: cat UBUNTU_INSTALL.md"
echo "   - Quick start: cat QUICKSTART.md"
echo ""

# Check network connectivity to robot
echo -e "${YELLOW}Checking robot connectivity...${NC}"
if ping -c 1 -W 1 192.168.123.164 &> /dev/null; then
    echo -e "${GREEN}✓ Robot is reachable at 192.168.123.164${NC}"
    echo "  You can run the application now!"
else
    echo -e "${YELLOW}⚠ Robot not detected at 192.168.123.164${NC}"
    echo "  Make sure to connect to the robot's network first"
    echo "  Or run in simulation mode (SDK optional)"
fi

echo ""
echo -e "${GREEN}Enjoy your Unitree G1! 🤖${NC}"
