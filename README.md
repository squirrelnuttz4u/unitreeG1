# Unitree G1 Control Application

A comprehensive desktop application for controlling the Unitree G1 EDU humanoid robot, featuring video streaming, SLAM visualization, motion control, gesture commands, and voice recognition.

![Unitree G1](https://img.shields.io/badge/Unitree-G1%20EDU-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![Ubuntu](https://img.shields.io/badge/Ubuntu-20.04%20LTS-orange)

## Features

### 🎮 Motion Control
- **Basic Movements**: Stand up, sit down, walk, run, stop
- **Directional Control**: Move forward, backward, left, right with directional pad
- **Advanced Control**: Adjustable velocity and rotation controls
- **Safety**: Emergency stop button for immediate halt

### 🤖 Gesture Control
- **Wave Hand**: Make the robot wave
- **Shake Hand**: Perform handshake gesture
- **Custom Gestures**: Extensible gesture system

### 📹 Video Feed
- **Live Camera Stream**: Real-time video from robot cameras
- **Snapshot Capture**: Save images from the video feed
- **Multiple Camera Support**: Switch between available cameras
- **High Quality**: 1280×720 @ 30fps (camera dependent)

### 🗺️ SLAM Integration
- **Real-time Mapping**: Live SLAM visualization using LiDAR data
- **Point Cloud Display**: 3D point cloud visualization
- **Occupancy Grid**: 2D map with robot position
- **Navigation**: Visual feedback for robot location and heading

### 🎤 Voice Control
- **Speech Recognition**: Control robot with voice commands
- **Text-to-Speech**: Audio feedback from the robot
- **Supported Commands**:
  - "stand up" / "sit down"
  - "walk forward" / "walk backward"
  - "turn left" / "turn right"
  - "run" / "stop"
  - "wave hand" / "shake hand"

### 📊 Status & Telemetry
- **Real-time Status**: Connection state and robot mode
- **Telemetry Display**: Position, battery, and sensor data
- **Activity Log**: Detailed event logging

## Requirements

### Hardware
- **Computer**: Windows 10/11 PC or Ubuntu 20.04+ Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Network**: WiFi or Ethernet connection to robot
- **Optional**: Microphone for voice control

### Software
- **Python**: 3.8 or higher
- **Unitree G1 EDU Robot**: With SDK v2 support (optional for simulation mode)

## Installation

**Choose your platform:**

- **🐧 Ubuntu 20.04**: See [UBUNTU_INSTALL.md](UBUNTU_INSTALL.md) - BEST option for native SDK support
- **🪟 Windows 10/11**: See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) - Requires WSL2 for robot control
- **🤖 Physical Robot**: See [HARDWARE_SETUP.md](HARDWARE_SETUP.md) for network setup and activation

### Quick Install (Ubuntu 20.04)

```bash
# One-line installation
curl -sSL https://raw.githubusercontent.com/yourusername/unitreeG1/main/install_ubuntu.sh | bash

# Or manual installation
git clone https://github.com/yourusername/unitreeG1.git
cd unitreeG1
./install_ubuntu.sh
```

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/unitreeG1.git
cd unitreeG1
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Unitree SDK2 (Optional - For Physical Robot)

**⚠️ Windows Users**: The SDK does NOT work on native Windows. See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for your options.

**Linux/WSL2 Users** can install from source:

```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```

**Note**: The application will automatically run in **simulation mode** if the SDK is not installed. This is perfect for testing the UI without a robot!

### 4. Install Additional Dependencies (Windows)

For audio support on Windows, you may need:

```bash
pip install pipwin
pipwin install pyaudio
```

## Configuration

### Robot Connection (Physical Hardware)

**Important**: See [HARDWARE_SETUP.md](HARDWARE_SETUP.md) for complete setup instructions including:
- Network configuration
- SDK installation on Windows
- Robot activation procedure
- Troubleshooting guide

By default, the application connects to the robot at `192.168.123.164`. To change this:

1. Edit `config.json` and update the `ip_address` field
2. Or open `src/robot/g1_controller.py` and modify the `robot_ip` parameter

**Network Interface**: Windows users must configure the correct network interface name in `config.json` or `src/robot/g1_controller.py` (line 63)

### Camera Settings

Video feed settings can be adjusted in `src/robot/video_feed.py`:
- `camera_width`: Default 1280
- `camera_height`: Default 720
- `camera_fps`: Default 30

## Usage

### Starting the Application

#### Ubuntu/Linux:
```bash
./start_ubuntu.sh
# Or directly:
python3 main.py
```

#### Windows:
```bash
python main.py
```

Or double-click `start.bat`

### Quick Start Guide

1. **Launch Application**: Run `main.py`
2. **Connect to Robot**: Click "Connect" button in the control panel
3. **Wait for Connection**: Status will show "Connected to robot"
4. **Start Control**:
   - Use buttons for motion control
   - Press directional arrows for movement
   - Click gesture buttons for animations
   - Enable voice control with "Start Listening"

### Control Interface

#### Connection Panel
- **Connect**: Establish connection to robot
- **Disconnect**: Safely disconnect from robot

#### Motion Control Panel
- **Stand Up**: Make robot stand from sitting position
- **Sit Down**: Make robot sit down
- **Walk**: Begin walking at default speed
- **Run**: Begin running (faster walking)
- **Directional Pad**: Control movement direction
  - ↑: Forward
  - ↓: Backward
  - ←: Left
  - →: Right
- **STOP**: Emergency stop (stops all motion)

#### Gesture Control Panel
- **Wave Hand**: Perform waving gesture
- **Shake Hand**: Perform handshake gesture

#### Voice Control Panel
- **Start Listening**: Begin voice command recognition
- **Stop Listening**: Stop voice recognition

### Voice Commands

Speak clearly into your microphone after clicking "Start Listening":

- **Motion**: "stand up", "sit down", "walk forward", "walk backward"
- **Speed**: "run", "stop"
- **Rotation**: "turn left", "turn right"
- **Gestures**: "wave hand", "shake hand"

### Video Feed

The center panel displays the live camera feed from the robot:
- **Snapshot**: Capture current frame to file
- **Toggle Camera**: Switch between available cameras

### SLAM Visualization

The right panel shows the SLAM map:
- **Blue dots**: Point cloud from LiDAR
- **Red circle**: Robot position
- **Red arrow**: Robot heading direction
- **Grayscale map**: Occupancy grid

## Simulation Mode

If the Unitree SDK is not installed or the robot is not connected, the application runs in **simulation mode**:

- ✅ Full UI functionality
- ✅ Simulated video feed
- ✅ Simulated SLAM data
- ✅ Motion command logging
- ❌ No actual robot control

This is useful for:
- Testing the UI
- Development without robot
- Training and demonstration

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to robot

**Solutions**:
1. Verify robot is powered on and fully booted (1-2 minutes)
2. Check network connection: `ping 192.168.123.164`
3. Ensure robot is activated via controller (L1+A, then L1+UP)
4. Verify correct network interface name in config (Windows: use `ipconfig /all`)
5. Check firewall settings aren't blocking Python
6. Verify Unitree SDK is installed: `pip list | grep unitree`
7. **See [HARDWARE_SETUP.md](HARDWARE_SETUP.md) for detailed troubleshooting**

### Video Feed Issues

**Problem**: No video feed or black screen

**Solutions**:
1. Check robot camera is functional
2. Verify RTSP stream URL
3. Try simulation mode to test UI
4. Check OpenCV installation

### Voice Control Issues

**Problem**: Voice commands not recognized

**Solutions**:
1. Check microphone is connected and working
2. Grant microphone permissions to Python
3. Speak clearly and slowly
4. Reduce background noise
5. Check SpeechRecognition installation

### Performance Issues

**Problem**: Slow or laggy interface

**Solutions**:
1. Close other applications
2. Reduce video resolution in settings
3. Disable SLAM visualization if not needed
4. Check CPU/RAM usage

## Development

### Project Structure

```
unitreeG1/
├── src/
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py       # Main GUI application
│   ├── robot/
│   │   ├── __init__.py
│   │   ├── g1_controller.py     # Robot control interface
│   │   └── video_feed.py        # Video streaming
│   ├── slam/
│   │   ├── __init__.py
│   │   └── slam_visualizer.py   # SLAM visualization
│   └── utils/
│       ├── __init__.py
│       └── audio_manager.py     # Audio and voice
├── assets/
│   └── icons/                    # Application icons
├── requirements.txt              # Python dependencies
├── main.py                       # Entry point
└── README.md                     # This file
```

### Adding New Features

#### Adding a New Gesture

1. Add method to `G1Controller` class:
```python
def new_gesture(self) -> bool:
    # Implementation
    pass
```

2. Add button to GUI in `main_window.py`:
```python
ctk.CTkButton(gesture_frame, text="New Gesture",
             command=self._on_new_gesture).pack(pady=5)
```

3. Add event handler:
```python
def _on_new_gesture(self):
    self.robot.new_gesture()
```

#### Adding Voice Commands

Add command parsing in `audio_manager.py`:
```python
elif "new command" in command:
    return {"action": "new_action"}
```

## API Reference

### G1Controller

Main robot control interface using the official Unitree SDK2.

```python
from src.robot import G1Controller

# Initialize controller
robot = G1Controller(robot_ip="192.168.123.164")

# Connect to robot (initializes LocoClient, AudioClient, etc.)
robot.connect()

# Basic motions (using LocoClient)
robot.stand_up()           # Squat2StandUp()
robot.sit_down()           # StandUp2Squat()
robot.walk(0.3, 0.0, 0.0)  # Move(vx, vy, vyaw)
robot.run(0.6, 0.0, 0.0)   # Faster Move()
robot.stop()               # Move(0, 0, 0)
robot.damp()               # Damp() - motors relaxed

# Additional G1 motions
robot.high_stand()         # HighStand()
robot.low_stand()          # LowStand()
robot.zero_torque()        # ZeroTorque()

# Gestures
robot.wave_hand()          # WaveHand()
robot.shake_hand()         # ShakeHand() (via arm controller)

# Disconnect
robot.disconnect()
```

**SDK Classes Used**:
- `LocoClient` - Locomotion control
- `AudioClient` - Audio/LED control
- `G1ArmController` - Arm gesture control

### VideoFeedHandler

Manages video streaming.

```python
from src.robot.video_feed import VideoFeedHandler

video = VideoFeedHandler(robot_ip="192.168.123.164")
video.start_stream(camera_index=0)
frame = video.get_current_frame()
video.capture_snapshot("snapshot.jpg")
video.stop_stream()
```

### SLAMVisualizer

SLAM visualization interface.

```python
from src.slam import SLAMVisualizer

slam = SLAMVisualizer()
slam.start()
slam.update_robot_pose(x=0, y=0, theta=0)
map_image = slam.get_map_image(width=800, height=600)
slam.stop()
```

### AudioManager

Audio and voice control.

```python
from src.utils import AudioManager

audio = AudioManager()
audio.start()
audio.speak("Hello, I am G1 robot")
audio.start_listening()
audio.stop()
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[UBUNTU_INSTALL.md](UBUNTU_INSTALL.md)** - Ubuntu 20.04 installation guide ⭐ RECOMMENDED
- **[WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)** - Windows installation guide
- **[HARDWARE_SETUP.md](HARDWARE_SETUP.md)** - Physical robot setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## Acknowledgments

- **Unitree Robotics**: For the G1 EDU robot and SDK
- **unitree_sdk2_python**: Official Python SDK for G1 control
- **CustomTkinter**: For the modern GUI framework
- **OpenCV**: For video processing
- **Open3D**: For 3D visualization

## Support

For issues and questions:
- **Hardware Setup**: See [HARDWARE_SETUP.md](HARDWARE_SETUP.md)
- **Application Issues**: Open an issue on GitHub
- **Unitree SDK**: https://github.com/unitreerobotics/unitree_sdk2_python
- **Official Docs**: https://support.unitree.com/home/en/G1_developer

## Roadmap

- [ ] Multi-camera view
- [ ] Recording and playback
- [ ] Custom motion sequences
- [ ] Remote control over internet
- [ ] Mobile app companion
- [ ] VR/AR integration
- [ ] Advanced SLAM features
- [ ] Object recognition
- [ ] Autonomous navigation

---

**Built with ❤️ for the Unitree G1 EDU Community**
