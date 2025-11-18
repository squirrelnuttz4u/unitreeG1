# Quick Start Guide - Unitree G1 Windows App

Get up and running with the Unitree G1 Control Application in 5 minutes!

## Installation (First Time)

### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation: Open Command Prompt and type `python --version`

### Step 2: Install Application
1. Download or clone this repository
2. Open Command Prompt in the `unitreeG1` folder
3. Run the installation script:
   ```batch
   install.bat
   ```
4. Wait for all dependencies to install

## Running the Application

### Method 1: Using Batch File (Easiest)
Double-click `start.bat`

### Method 2: Using Command Prompt
```batch
python main.py
```

## First Use

### 1. Launch Application
- The application window will open
- You'll see three main panels: Controls (left), Video (center), SLAM/Status (right)

### 2. Connect to Robot
1. Make sure your Unitree G1 robot is powered on
2. Connect your PC to the robot's WiFi network or ensure they're on the same network
3. Click the **"Connect"** button in the top-left control panel
4. Wait for "Connected to robot" status message

### 3. Basic Controls

#### Make Robot Stand
- Click **"Stand Up"** button
- Wait for robot to complete standing motion

#### Walk Forward
- Click the **↑** arrow button
- Robot will walk forward
- Click **STOP** (red button) to halt

#### Try a Gesture
- Click **"Wave Hand"** button
- Robot will perform waving gesture

#### Stop Everything
- Click the large red **"STOP"** button
- Robot will immediately halt all motion

## Testing Without Robot (Simulation Mode)

If you don't have a robot connected:
1. Just click "Connect" anyway
2. The app will run in **simulation mode**
3. You'll see:
   - Simulated video feed
   - Simulated SLAM map
   - All controls work (logged to status)
4. Great for learning the interface!

## Voice Control (Optional)

### Enable Voice Commands
1. Click **"Start Listening"** in the Voice Control section
2. Grant microphone permissions if prompted
3. Speak commands clearly:
   - "stand up"
   - "walk forward"
   - "stop"
   - "wave hand"

## Troubleshooting

### Can't Connect to Robot
- ✅ Check robot is powered on
- ✅ Check network connection (ping 192.168.123.164)
- ✅ Try simulation mode to test the app

### No Video Feed
- ✅ Run in simulation mode first
- ✅ Check camera settings in config.json
- ✅ Verify robot camera is working

### Voice Control Not Working
- ✅ Check microphone is connected
- ✅ Grant microphone permissions
- ✅ Speak clearly and reduce background noise

### Application Won't Start
- ✅ Run `python --version` to verify Python is installed
- ✅ Re-run `install.bat`
- ✅ Check error messages in console

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore all control buttons
3. Try voice commands
4. Capture snapshots from video feed
5. Watch SLAM map build in real-time

## Control Reference Card

### Motion Controls
| Button | Action |
|--------|--------|
| Stand Up | Make robot stand |
| Sit Down | Make robot sit |
| Walk | Start walking |
| Run | Start running |
| ↑ | Walk forward |
| ↓ | Walk backward |
| ← | Walk left |
| → | Walk right |
| STOP (red) | Emergency stop |

### Gestures
| Button | Action |
|--------|--------|
| Wave Hand | Wave gesture |
| Shake Hand | Handshake gesture |

### Voice Commands
| Command | Action |
|---------|--------|
| "stand up" | Make robot stand |
| "sit down" | Make robot sit |
| "walk forward" | Walk forward |
| "stop" | Stop motion |
| "wave hand" | Wave gesture |

## Safety Tips

⚠️ **Important Safety Guidelines**:

1. **Always** keep a safe distance when robot is moving
2. **Use** the STOP button if anything unexpected happens
3. **Ensure** clear space around robot before motion commands
4. **Start** with slow commands (walk before run)
5. **Test** in simulation mode first if you're new

## Getting Help

- 📖 Full documentation: [README.md](README.md)
- 🐛 Report issues: Check console output for error messages
- 💬 Unitree support: [support.unitree.com](https://support.unitree.com)

---

**Enjoy controlling your Unitree G1! 🤖**
