# Changelog

All notable changes to the Unitree G1 Windows Control Application will be documented in this file.

## [1.0.0] - 2025-01-18

### Added
- Initial release of Unitree G1 Windows Control Application
- Modern GUI using CustomTkinter framework
- Robot connection and control via Unitree SDK2
- Real-time video feed display from robot cameras
- SLAM visualization with point cloud and occupancy grid
- Motion controls:
  - Stand up / Sit down
  - Walk with directional control
  - Run mode
  - Emergency stop
- Gesture controls:
  - Wave hand
  - Shake hand
- Voice control system:
  - Speech recognition for commands
  - Text-to-speech feedback
  - Support for common motion and gesture commands
- Status and telemetry display:
  - Connection status
  - Robot state
  - Motion mode
  - Activity log
- Simulation mode for testing without robot
- Configuration file (config.json) for customization
- Comprehensive documentation:
  - README.md with full documentation
  - QUICKSTART.md for new users
  - Installation scripts for Windows
- Startup scripts:
  - start.bat for easy launching
  - install.bat for dependency installation

### Features

#### Core Functionality
- Multi-threaded architecture for smooth UI and video streaming
- Automatic reconnection handling
- Safety features with emergency stop
- Real-time status updates

#### Video System
- Configurable camera resolution (default 1280x720 @ 30fps)
- Snapshot capture capability
- Multiple camera support
- Simulation mode with generated video

#### SLAM System
- Real-time map visualization
- Point cloud display
- Occupancy grid mapping
- Robot pose tracking
- Configurable map size and resolution

#### Audio System
- Text-to-speech for robot feedback
- Speech recognition for voice commands
- Configurable voice settings
- Background audio processing

#### User Interface
- Dark theme for reduced eye strain
- Responsive layout with three main panels
- Intuitive control buttons
- Directional pad for movement
- Real-time video and SLAM displays
- Status log with scrolling

### Technical Details
- Python 3.8+ support
- Windows 10/11 compatible
- Modular architecture with separate packages:
  - `src/gui`: User interface
  - `src/robot`: Robot control and video
  - `src/slam`: SLAM visualization
  - `src/utils`: Audio and utilities
- Extensive error handling and logging
- Configuration via JSON file

### Dependencies
- customtkinter: Modern GUI framework
- opencv-python: Video processing
- numpy: Numerical operations
- matplotlib: SLAM visualization
- pyttsx3: Text-to-speech
- SpeechRecognition: Voice commands
- unitree_sdk2py: Robot SDK (optional, simulation mode available)

### Known Limitations
- Unitree SDK may have limited Windows support (simulation mode available as fallback)
- Voice recognition requires internet connection for Google Speech API
- SLAM visualization is 2D only (3D in future version)

### Future Roadmap
- [ ] Multi-camera simultaneous view
- [ ] Video recording and playback
- [ ] Custom motion sequence programming
- [ ] Remote control over internet
- [ ] Mobile companion app
- [ ] VR/AR integration
- [ ] Advanced SLAM with 3D visualization
- [ ] Object recognition and tracking
- [ ] Autonomous navigation
- [ ] Joystick/gamepad support

---

## Version History

- **1.0.0** (2025-01-18): Initial release

---

**Note**: This project follows [Semantic Versioning](https://semver.org/).
