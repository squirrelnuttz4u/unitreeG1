# Ubuntu 20.04 Installation Guide

Complete guide for installing and running the Unitree G1 Control Application on Ubuntu 20.04 LTS.

## Quick Start (TL;DR)

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip git -y

# Clone repository
git clone <your-repo-url>
cd unitreeG1

# Install Python packages
pip3 install -r requirements.txt

# For real robot control, install Unitree SDK
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip3 install -e .
cd ..

# Run the application
python3 main.py
```

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Options](#installation-options)
3. [Detailed Installation](#detailed-installation)
4. [Network Setup](#network-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS (Focal Fossa)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Python**: 3.8 or higher (included in Ubuntu 20.04)
- **Network**: WiFi or Ethernet adapter

### For Real Robot Control
- Unitree G1 EDU robot
- Network connection to robot (WiFi or Ethernet)
- Robot controller for initial activation

---

## Installation Options

### Option 1: Simulation Mode (No Robot) ✅

**Best for**: Testing the UI, development, demonstrations

**What works**:
- ✅ Full GUI functionality
- ✅ Simulated video feed
- ✅ Simulated SLAM visualization
- ✅ Voice recognition
- ✅ All UI features
- ❌ No actual robot control

**Installation time**: ~5 minutes

### Option 2: Full Installation (With Robot Support) ✅

**Best for**: Controlling your physical G1 robot

**What works**:
- ✅ Everything from simulation mode
- ✅ Real robot control
- ✅ Real video feed (when configured)
- ✅ Real SLAM data (when configured)

**Installation time**: ~10 minutes

---

## Detailed Installation

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install System Dependencies

```bash
# Install Python and development tools
sudo apt install -y python3 python3-pip python3-dev

# Install build essentials (needed for some Python packages)
sudo apt install -y build-essential cmake git

# Install GUI dependencies
sudo apt install -y python3-tk

# Install audio dependencies (for voice control)
sudo apt install -y portaudio19-dev python3-pyaudio

# Install system libraries for OpenCV
sudo apt install -y libopencv-dev python3-opencv
```

### Step 3: Clone the Repository

```bash
cd ~
git clone <your-repo-url>
cd unitreeG1
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip
pip3 install --upgrade pip

# Install application dependencies
pip3 install -r requirements.txt
```

**Note**: This installs everything except the Unitree SDK. The app will run in simulation mode.

### Step 5: Install Unitree SDK (Optional - For Real Robot)

Only needed if you want to control a physical G1 robot:

```bash
# Clone Unitree SDK repository
cd ~
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python

# Install the SDK
pip3 install -e .

# Verify installation
python3 -c "from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient; print('SDK installed successfully!')"
```

If you see "SDK installed successfully!", you're all set!

### Step 6: Install Additional Features (Optional)

#### For Voice Control:
```bash
# Already installed in Step 2, but if needed:
sudo apt install -y portaudio19-dev
pip3 install pyaudio SpeechRecognition pyttsx3
```

#### For Better Audio (espeak):
```bash
sudo apt install -y espeak espeak-data
```

---

## Network Setup

### Connecting to Your G1 Robot

#### Method 1: WiFi Connection (Recommended)

1. **Power on your G1 robot**
   - Wait for it to fully boot (~1-2 minutes)

2. **Connect to robot's WiFi**
   ```bash
   # List available WiFi networks
   nmcli device wifi list

   # Connect to robot's network (replace with actual network name)
   nmcli device wifi connect "Unitree_G1_XXXX" password "your-password"
   ```

3. **Verify connection**
   ```bash
   ping 192.168.123.164
   ```

   You should see responses. Press Ctrl+C to stop.

#### Method 2: Ethernet Connection

1. **Connect Ethernet cable** from your Ubuntu PC to the robot

2. **Configure static IP**
   ```bash
   # Find your ethernet interface name
   ip addr show
   # Look for something like eth0, enp0s31f6, etc.

   # Configure static IP (replace eth0 with your interface)
   sudo ip addr add 192.168.123.99/24 dev eth0
   sudo ip link set eth0 up
   ```

3. **Verify connection**
   ```bash
   ping 192.168.123.164
   ```

#### Network Details

- **Robot IP**: `192.168.123.164`
- **LiDAR IP**: `192.168.123.120`
- **Your PC IP**: `192.168.123.X` (where X is not 164 or 120)

---

## Running the Application

### First Time Setup

1. **Navigate to application directory**
   ```bash
   cd ~/unitreeG1
   ```

2. **Make sure you're on the same network as the robot** (if using physical robot)
   ```bash
   ping 192.168.123.164
   ```

3. **Run the application**
   ```bash
   python3 main.py
   ```

### Application Modes

#### Simulation Mode (Automatic)
If the Unitree SDK is not installed, the app automatically runs in simulation mode:
```bash
python3 main.py
```

You'll see:
- "Unitree SDK not available. Running in simulation mode." in the log
- Simulated video feed with moving graphics
- Simulated SLAM map
- All controls work but don't control a physical robot

#### Robot Control Mode (With SDK)
If the SDK is installed and robot is connected:
```bash
python3 main.py
```

Then in the application:
1. Click **"Connect"** button
2. Wait for "Connected to robot" status
3. **Activate robot with controller** (see below)
4. Start controlling!

### Activating the Robot

**IMPORTANT**: Before SDK control works, activate the robot with the hand controller:

1. Power on the robot
2. Press **L1 + A** (switch to sport mode)
3. Press **L1 + UP** (enable SDK control)
4. Robot LED should indicate ready state

Now the SDK can control the robot!

---

## Using the Application

### Main Interface

The application window has three panels:

**Left Panel - Controls**
- Connection buttons
- Motion controls (Stand, Sit, Walk, Run)
- Directional pad (↑↓←→)
- Emergency STOP button
- Gesture controls (Wave, Shake hand)
- Voice control toggle

**Center Panel - Video Feed**
- Live camera feed from robot
- Snapshot button
- Camera toggle

**Right Panel - Status**
- SLAM map visualization
- Status log
- Telemetry data

### Basic Controls

1. **Connect to Robot**
   - Click "Connect" button
   - Wait for confirmation

2. **Make Robot Stand**
   - Click "Stand Up"
   - Robot transitions from sitting to standing

3. **Walk Forward**
   - Click the ↑ arrow button
   - Robot walks forward
   - Click STOP to halt

4. **Emergency Stop**
   - Click large red "STOP" button
   - Robot immediately stops all motion

5. **Wave Gesture**
   - Click "Wave Hand"
   - Robot performs waving motion

### Voice Control

1. **Enable Voice Recognition**
   - Click "Start Listening" button

2. **Speak Commands**
   - "stand up"
   - "walk forward"
   - "stop"
   - "wave hand"
   - "turn left"
   - "run"

3. **Disable**
   - Click "Stop Listening"

### Keyboard Shortcuts

(If implemented)
- **Space**: Emergency stop
- **W/A/S/D**: Directional movement
- **Q/E**: Rotate left/right
- **R**: Stand up
- **F**: Sit down

---

## Configuration

### Robot IP Address

If your robot uses a different IP, edit `config.json`:

```json
{
  "robot": {
    "ip_address": "192.168.123.164",
    "network_interface": "eth0"
  }
}
```

Or edit `src/robot/g1_controller.py` line 45:
```python
def __init__(self, robot_ip: str = "YOUR_ROBOT_IP"):
```

### Network Interface

Ubuntu uses different interface names. Find yours:

```bash
ip addr show
```

Common names:
- `eth0`, `enp0s31f6` - Ethernet
- `wlan0`, `wlp3s0` - WiFi

Update in `config.json` or `src/robot/g1_controller.py` line 63:
```python
self.network_interface = "eth0"  # Change to your interface
```

---

## Troubleshooting

### Application Won't Start

**Problem**: ModuleNotFoundError

**Solution**:
```bash
pip3 install -r requirements.txt
```

### SDK Import Error

**Problem**: `ModuleNotFoundError: No module named 'unitree_sdk2py'`

**Solution**:
```bash
cd ~/unitree_sdk2_python
pip3 install -e .
```

If not installed, the app will run in simulation mode (this is normal).

### Cannot Connect to Robot

**Problem**: "Connection failed" error

**Solutions**:

1. **Check network connection**
   ```bash
   ping 192.168.123.164
   ```

2. **Verify robot is powered on and booted** (wait 1-2 minutes after power on)

3. **Activate robot with controller**
   - L1 + A (sport mode)
   - L1 + UP (SDK control)

4. **Check firewall**
   ```bash
   sudo ufw status
   # If blocking, allow:
   sudo ufw allow from 192.168.123.0/24
   ```

5. **Verify network interface**
   ```bash
   ip addr show
   # Update interface name in config
   ```

### GUI Not Displaying

**Problem**: GUI window doesn't appear or crashes

**Solutions**:

1. **Install tkinter**
   ```bash
   sudo apt install python3-tk
   ```

2. **Check display**
   ```bash
   echo $DISPLAY
   # Should show :0 or :1
   ```

3. **For remote/SSH sessions**
   ```bash
   # Enable X11 forwarding
   ssh -X user@host
   ```

### Voice Control Not Working

**Problem**: Voice commands not recognized

**Solutions**:

1. **Check microphone**
   ```bash
   arecord -l
   # List recording devices
   ```

2. **Install/reinstall audio packages**
   ```bash
   sudo apt install portaudio19-dev
   pip3 install --upgrade pyaudio SpeechRecognition
   ```

3. **Grant microphone permissions**
   - Check system privacy settings
   - Allow Python to access microphone

### Robot Not Responding

**Problem**: Connected but robot doesn't move

**Solutions**:

1. **Activate SDK control with controller**
   - L1 + A, then L1 + UP

2. **Check robot state**
   - Should show "sport mode" on controller
   - LED should be active (not red)

3. **Check battery**
   - Must be >20% for operation

4. **Try damp mode first**
   - Click "Damp" button
   - Motors should relax
   - Then try "Stand Up"

### Performance Issues

**Problem**: Slow or laggy interface

**Solutions**:

1. **Close other applications**

2. **Reduce video quality** (edit `src/robot/video_feed.py`):
   ```python
   self.camera_width = 640  # Reduced from 1280
   self.camera_height = 480  # Reduced from 720
   ```

3. **Disable SLAM** if not needed

4. **Check system resources**
   ```bash
   htop
   # Look for high CPU/RAM usage
   ```

---

## Advanced Usage

### Running as a Service

To auto-start the application on boot:

1. **Create service file**
   ```bash
   sudo nano /etc/systemd/system/unitree-g1.service
   ```

2. **Add content**:
   ```ini
   [Unit]
   Description=Unitree G1 Control Application
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/home/your-username/unitreeG1
   ExecStart=/usr/bin/python3 /home/your-username/unitreeG1/main.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start**
   ```bash
   sudo systemctl enable unitree-g1
   sudo systemctl start unitree-g1
   sudo systemctl status unitree-g1
   ```

### Development Mode

For development with auto-reload:

```bash
# Install development tools
pip3 install watchdog

# Run with file watching (create a dev script)
while true; do
    python3 main.py
    sleep 1
done
```

### Logging

Enable detailed logging by editing `main.py`:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unitree_g1.log'),
        logging.StreamHandler()
    ]
)
```

---

## Performance Optimization

### For Better Performance on Ubuntu 20.04:

1. **Use Python 3.9+** (optional):
   ```bash
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.9 python3.9-dev python3.9-venv
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install optimized OpenCV**:
   ```bash
   pip3 uninstall opencv-python
   pip3 install opencv-contrib-python
   ```

---

## Security Considerations

### Network Security

1. **Firewall configuration**
   ```bash
   # Only allow robot network
   sudo ufw enable
   sudo ufw allow from 192.168.123.0/24
   ```

2. **Disable unnecessary services**
   ```bash
   sudo systemctl disable bluetooth
   ```

### Application Security

- Don't run as root
- Keep SDK updated
- Review code before running
- Use secure WiFi passwords

---

## Comparison: Ubuntu vs Windows

| Feature | Ubuntu 20.04 | Windows 10/11 |
|---------|-------------|---------------|
| **SDK Installation** | ✅ Native | ⚠️ WSL2 only |
| **Setup Time** | 10 minutes | 20 minutes (WSL2) |
| **Performance** | ✅ Excellent | ✅ Good (WSL2) |
| **Robot Control** | ✅ Direct | ✅ Via WSL2 |
| **Simulation Mode** | ✅ Works | ✅ Works |
| **Recommended?** | ✅ Yes | ✅ Yes (WSL2) |

---

## Next Steps

1. ✅ **Test in Simulation Mode** - Familiarize yourself with the interface
2. ✅ **Connect to Robot** - Try basic movements
3. ✅ **Explore Features** - Voice control, gestures, SLAM
4. 📖 **Read Documentation** - Check [README.md](README.md) for full API
5. 🛠️ **Customize** - Modify for your specific needs

---

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Hardware Setup**: [HARDWARE_SETUP.md](HARDWARE_SETUP.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Unitree SDK**: https://github.com/unitreerobotics/unitree_sdk2_python
- **Official Docs**: https://support.unitree.com/home/en/G1_developer

---

## Getting Help

### Application Issues
- Check logs: `tail -f unitree_g1.log`
- Open GitHub issue with error details
- Include Ubuntu version and Python version

### SDK Issues
- Check Unitree SDK repository
- Review official documentation
- Contact Unitree support

### Ubuntu Issues
- Ubuntu forums: https://ubuntuforums.org/
- Ask Ubuntu: https://askubuntu.com/

---

## Uninstallation

If you need to remove the application:

```bash
# Remove application files
cd ~
rm -rf unitreeG1

# Remove SDK (if installed)
rm -rf unitree_sdk2_python

# Remove Python packages
pip3 uninstall -y customtkinter opencv-python numpy matplotlib

# Remove system packages (careful!)
# sudo apt remove python3-tk portaudio19-dev
```

---

**Enjoy controlling your Unitree G1 on Ubuntu! 🤖🐧**
