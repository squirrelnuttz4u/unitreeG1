# Hardware Setup Guide for Unitree G1

This guide explains how to set up your Windows PC to connect to and control a physical Unitree G1 EDU robot.

## Prerequisites

- Unitree G1 EDU robot (fully charged)
- Windows PC with WiFi or Ethernet
- Robot controller (for initial activation)
- Python 3.8+ installed

## Network Configuration

### G1 Network Details

The Unitree G1 robot creates its own network with these default settings:

- **Robot IP Address**: `192.168.123.164`
- **LiDAR IP Address**: `192.168.123.120`
- **Your PC should use**: `192.168.123.X` (where X is any number except 164 and 120)

### Method 1: WiFi Connection (Recommended)

1. **Power on the G1 robot**
   - Hold the power button until the robot boots up
   - Wait for initialization (LED indicators will show ready state)

2. **Connect to Robot WiFi**
   - On your Windows PC, open WiFi settings
   - Look for the robot's WiFi network (usually named `Unitree_G1_XXXX`)
   - Connect using the password provided with your robot

3. **Verify Connection**
   ```cmd
   ping 192.168.123.164
   ```
   You should see replies from the robot

### Method 2: Ethernet Connection

1. **Connect via Ethernet cable**
   - Plug an Ethernet cable from your PC to the robot's Ethernet port

2. **Configure Static IP**
   - Open Network Settings > Change adapter options
   - Right-click your Ethernet adapter > Properties
   - Select "Internet Protocol Version 4 (TCP/IPv4)" > Properties
   - Choose "Use the following IP address":
     - IP address: `192.168.123.99`
     - Subnet mask: `255.255.255.0`
     - Default gateway: `192.168.123.164`

3. **Verify Connection**
   ```cmd
   ping 192.168.123.164
   ```

## SDK Installation

### 1. Install Visual C++ Build Tools (Required for Windows)

Download and install Microsoft C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Or install Visual Studio with C++ development tools.

### 2. Install Unitree SDK2 Python

```cmd
# Install from PyPI
pip install unitree-sdk2py

# OR install from source (latest version)
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```

### 3. Install Application Dependencies

```cmd
cd unitreeG1
pip install -r requirements.txt
```

### 4. Install CycloneDDS (Required)

The SDK uses CycloneDDS for communication:

```cmd
pip install cyclonedds
```

## Network Interface Configuration

### Finding Your Network Interface Name

Windows uses different network interface names than Linux. You need to find yours:

```cmd
# List network interfaces
ipconfig /all
```

Look for the adapter connected to the robot. Common names:
- `Ethernet` or `Ethernet 2`
- `Wi-Fi`
- Network adapter name varies by system

### Configure the Application

Edit `config.json` in the application directory:

```json
{
  "robot": {
    "ip_address": "192.168.123.164",
    "network_interface": "Ethernet"  // Change to YOUR interface name
  }
}
```

Or edit `src/robot/g1_controller.py` line 63:

```python
self.network_interface = "Ethernet"  # Change to YOUR interface name
```

## Robot Activation

**IMPORTANT**: Before the robot can be controlled via SDK, you must activate it with the controller.

1. **Power on the robot** and wait for it to boot completely

2. **Using the hand controller**, enter sport mode:
   - Press **L1 + A** (to switch to sport mode)
   - Press **L1 + UP** (to enable SDK control)
   - Robot LED should indicate it's ready for SDK commands

3. **Verify the robot is ready**:
   - Robot should be in "damp" state (motors relaxed)
   - LED indicators should show active state
   - No error beeps or red lights

## Testing Connection

### Test 1: Network Connectivity

```cmd
ping 192.168.123.164
```

Expected: Continuous replies with low latency (<10ms)

### Test 2: SDK Installation

```python
python -c "from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient; print('SDK OK')"
```

Expected: `SDK OK` (no import errors)

### Test 3: Launch Application

```cmd
python main.py
```

Expected: Application window opens, click "Connect" button

### Test 4: Basic Command

Once connected in the app:
1. Click "Stand Up" button
2. Robot should transition from damp/squat to standing position
3. Status should show "Standing up"

## Troubleshooting

### Cannot Connect to Robot

**Problem**: Application shows "Connection failed"

**Solutions**:
1. Verify robot is powered on and booted (wait 1-2 minutes after power on)
2. Check network connection: `ping 192.168.123.164`
3. Verify robot is in SDK control mode (L1+A, L1+UP on controller)
4. Check Windows Firewall isn't blocking Python
5. Verify correct network interface name in config

### SDK Import Errors

**Problem**: `ModuleNotFoundError: No module named 'unitree_sdk2py'`

**Solutions**:
1. Install SDK: `pip install unitree-sdk2py`
2. Check Python version: `python --version` (must be 3.8+)
3. Install from source if PyPI version fails

### Robot Not Responding to Commands

**Problem**: Connection succeeds but robot doesn't move

**Solutions**:
1. Activate sport mode with controller (L1+A, L1+UP)
2. Check robot isn't in emergency stop state
3. Verify battery level is sufficient (>20%)
4. Check robot logs on the robot's display
5. Ensure motors are not in zero-torque or damp mode

### Network Interface Error

**Problem**: `ChannelFactoryInitialize` fails

**Solutions**:
1. Find correct interface name: `ipconfig /all`
2. Update `network_interface` in code or config
3. Run as Administrator (may help with network access)
4. Disable other network adapters temporarily

### Video Feed Not Working

**Problem**: Black screen or no video

**Solutions**:
1. G1 camera access may require WebRTC (different from RTSP)
2. Check if camera examples work from SDK
3. Run in simulation mode to test UI
4. Camera features may require additional setup

### LiDAR/SLAM Not Working

**Problem**: No SLAM visualization

**Solutions**:
1. LiDAR has separate IP: `192.168.123.120`
2. May require unilidar_sdk: `pip install unilidar-sdk`
3. Check if LiDAR is enabled on robot
4. Run SLAM in simulation mode for testing

## Safety Guidelines

⚠️ **IMPORTANT SAFETY INFORMATION**

1. **Clear Space**: Ensure 3+ meters of clear space around robot
2. **Emergency Stop**: Keep controller handy for emergency stop
3. **Start Slow**: Begin with simple commands (stand, sit)
4. **Supervision**: Never leave robot unattended when powered
5. **Battery**: Don't operate below 20% battery
6. **Surface**: Operate on flat, non-slip surfaces only
7. **Obstacles**: Remove trip hazards and obstacles
8. **People**: Keep people (especially children) away during operation

## Advanced Configuration

### Custom Network Settings

If your robot uses different IP addresses, update `config.json`:

```json
{
  "robot": {
    "ip_address": "192.168.1.100",  // Your robot IP
    "connection_timeout": 10,
    "retry_attempts": 3
  }
}
```

### Multiple Robots

To control multiple G1 robots:
1. Each robot needs unique IP address
2. Create separate config files
3. Modify application to select robot
4. Ensure network supports multiple DDS participants

### Performance Tuning

For better performance:
1. Use wired Ethernet instead of WiFi
2. Disable Windows power saving on network adapter
3. Close other network-heavy applications
4. Increase DDS QoS settings if needed

## Next Steps

Once connected successfully:

1. **Test Basic Motions**:
   - Stand Up → Sit Down → Stand Up
   - Walk forward slowly
   - Stop
   - Damp mode

2. **Test Gestures**:
   - Wave hand
   - Try other arm movements

3. **Voice Control**:
   - Enable "Start Listening"
   - Test voice commands

4. **Explore Features**:
   - Take snapshots
   - Monitor telemetry
   - Check SLAM visualization

## Support Resources

- **Unitree Official Docs**: https://support.unitree.com/home/en/G1_developer
- **SDK Repository**: https://github.com/unitreerobotics/unitree_sdk2_python
- **Community Forums**: Check Unitree forums and GitHub issues
- **Application Issues**: Check the application's GitHub repository

---

**Need Help?**

If you encounter issues not covered here:
1. Check the console output for detailed error messages
2. Review Unitree's official documentation
3. Check SDK GitHub issues for similar problems
4. Enable debug logging in the application for more details
