# Installation Troubleshooting Guide

Common installation issues and solutions.

## Issue: open3d gives 404 error

**Error message:**
```
ERROR: Could not find a version that satisfies the requirement open3d>=0.17.0
ERROR: No matching distribution found for open3d
```

**Cause:** Open3D doesn't have pre-built wheels for all Python versions and platforms.

**Solution:** Open3D is **optional** - the app works fine without it!

### Option 1: Use Minimal Requirements (Recommended)

```bash
pip install -r requirements-minimal.txt
```

This installs only the core dependencies needed for the app to run.

### Option 2: Skip open3d

```bash
# Install everything except open3d
pip install customtkinter Pillow opencv-python numpy matplotlib pyttsx3 SpeechRecognition
```

### Option 3: Install open3d separately (if really needed)

```bash
# Try different Python versions
python3.9 -m pip install open3d
# Or
python3.10 -m pip install open3d

# Or build from source (advanced)
pip install open3d --no-binary :all:
```

**Note:** The SLAM visualization uses matplotlib (2D) which works great. Open3D is only for advanced 3D point cloud visualization, which isn't implemented yet.

---

## Issue: pyaudio fails to install

**Error message:**
```
ERROR: Could not find a version that satisfies the requirement pyaudio
```

**Cause:** PyAudio requires system audio libraries.

### Ubuntu/Linux:

```bash
# Install system package first
sudo apt install portaudio19-dev python3-pyaudio

# Then install Python package
pip3 install pyaudio
```

### Windows:

```bash
# Use pipwin (easier than building from source)
pip install pipwin
pipwin install pyaudio
```

### Alternative: Skip voice control

PyAudio is only needed for voice control. If you don't need it:

```bash
# Install without pyaudio
pip install -r requirements-minimal.txt
```

The app will work fine without voice recognition.

---

## Issue: cyclonedds fails on Windows

**Error message:**
```
ERROR: Could not locate cyclonedds
```

**Cause:** CycloneDDS doesn't have Windows wheels for version 0.10.2

**Solution:** This is only needed for the Unitree SDK. See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for solutions:

1. **Use WSL2** (recommended)
2. **Use Simulation Mode** (skip SDK entirely)
3. **Build from source** (advanced)

---

## Issue: opencv-python fails

**Error message:**
```
ERROR: Failed building wheel for opencv-python
```

### Ubuntu/Linux:

```bash
# Install system dependencies
sudo apt install libopencv-dev python3-opencv

# Then try again
pip3 install opencv-python
```

### Alternative: Use system package

```bash
# On Ubuntu, use the system version
sudo apt install python3-opencv
# Skip opencv-python in requirements
```

---

## Issue: All installations fail

### Quick Fix: Use Minimal Requirements

```bash
pip install -r requirements-minimal.txt
```

This installs only the absolute essentials:
- ✅ customtkinter (GUI)
- ✅ Pillow (images)
- ✅ opencv-python (video)
- ✅ numpy (arrays)
- ✅ matplotlib (SLAM)
- ✅ pyttsx3 (speech)
- ✅ SpeechRecognition (voice)

Everything else is optional!

---

## Platform-Specific Installation

### Ubuntu 20.04 (Recommended)

```bash
# System packages
sudo apt update
sudo apt install -y python3 python3-pip python3-dev build-essential \
    python3-tk portaudio19-dev libopencv-dev python3-opencv

# Python packages
pip3 install -r requirements-minimal.txt

# Optional: Unitree SDK (for real robot)
cd ~
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip3 install -e .
```

### Windows 10/11

**Option 1: WSL2 (Recommended)**
```powershell
wsl --install
# Then follow Ubuntu instructions above
```

**Option 2: Native Windows (Minimal)**
```cmd
# Install only core packages
pip install customtkinter Pillow opencv-python numpy matplotlib pyttsx3 SpeechRecognition

# Skip: pyaudio, cyclonedds, open3d, scipy
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 portaudio

# Python packages
pip3 install -r requirements-minimal.txt
```

---

## Dependency Matrix

What you actually need:

| Package | Required? | Used For | Fallback if Missing |
|---------|-----------|----------|-------------------|
| customtkinter | ✅ Yes | GUI | None - app won't run |
| Pillow | ✅ Yes | Images | None - app won't run |
| opencv-python | ✅ Yes | Video | None - app won't run |
| numpy | ✅ Yes | Arrays | None - app won't run |
| matplotlib | ✅ Yes | SLAM | None - app won't run |
| pyttsx3 | ⚠️ Recommended | Speech | App works, no TTS |
| SpeechRecognition | ⚠️ Recommended | Voice | App works, no voice control |
| pyaudio | ❌ Optional | Voice input | Use simulation mode |
| sounddevice | ❌ Optional | Alternative audio | Use simulation mode |
| cyclonedds | ❌ Optional | SDK communication | Simulation mode only |
| open3d | ❌ Optional | 3D visualization | Uses matplotlib instead |
| scipy | ❌ Optional | Advanced math | Not currently used |
| pyserial | ❌ Optional | Serial comms | Not currently used |

---

## Clean Install

If everything is broken, start fresh:

### Ubuntu/Linux:

```bash
# Remove old packages
pip3 uninstall -y customtkinter opencv-python numpy matplotlib \
    pyaudio sounddevice pyttsx3 SpeechRecognition \
    cyclonedds open3d scipy pyserial

# Fresh install (minimal)
pip3 install -r requirements-minimal.txt
```

### Windows:

```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Fresh install
pip install -r requirements-minimal.txt
```

---

## Testing Your Installation

After installing, test if it works:

```bash
# Test core dependencies
python3 -c "import customtkinter; print('GUI: OK')"
python3 -c "import cv2; print('Video: OK')"
python3 -c "import numpy; print('NumPy: OK')"
python3 -c "import matplotlib; print('SLAM: OK')"

# Test optional dependencies
python3 -c "import pyttsx3; print('TTS: OK')" || echo "TTS: Not available"
python3 -c "import speech_recognition; print('Voice: OK')" || echo "Voice: Not available"

# Test SDK (if installed)
python3 -c "from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient; print('SDK: OK')" || echo "SDK: Not available (Simulation mode)"

# Run the app
python3 main.py
```

If you see "GUI: OK", "Video: OK", "NumPy: OK", and "SLAM: OK", you're good to go!

---

## Still Having Issues?

### Try the automatic installer:

**Ubuntu:**
```bash
./install_ubuntu.sh
```

**Windows:**
```cmd
install.bat
```

### Manual minimal installation:

```bash
# Just the essentials
pip install customtkinter==5.2.0 Pillow==10.1.0 opencv-python==4.8.1.78 numpy==1.24.3 matplotlib==3.8.0

# Run app
python3 main.py
```

### Check Python version:

```bash
python3 --version
# Should be 3.8 or higher
```

If Python is too old:
```bash
# Ubuntu
sudo apt install python3.10

# Windows
# Download from python.org
```

---

## Getting Help

If you're still stuck:

1. **Check which package is failing**:
   ```bash
   pip install <package-name> -v
   ```

2. **Check Python version**:
   ```bash
   python3 --version
   ```

3. **Check pip version**:
   ```bash
   pip3 --version
   # Upgrade if old
   pip3 install --upgrade pip
   ```

4. **Use virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows

   pip install -r requirements-minimal.txt
   ```

5. **Open a GitHub issue** with:
   - Your OS and version
   - Python version
   - Full error message
   - Output of `pip list`

---

**Remember:** The app works fine with just the minimal requirements! Don't worry about optional packages like open3d, scipy, or pyserial.
