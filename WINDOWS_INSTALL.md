# Windows Installation Guide

Quick guide for Windows users to get started with the Unitree G1 Control Application.

## TL;DR - Quick Start

**Just want to try the app?**

```cmd
git clone <your-repo-url>
cd unitreeG1
pip install -r requirements.txt
python main.py
```

The app will run in **simulation mode** - perfect for testing the UI without a robot!

---

## The Windows SDK Problem

The Unitree SDK requires `cyclonedds==0.10.2`, which **doesn't work on native Windows** because:
- No pre-built Windows wheels available
- Requires compilation from source
- Needs CMake + Visual C++ Build Tools
- Complex environment setup

**Bottom line**: You can't easily install `unitree-sdk2py` on Windows using pip.

---

## Your Options

### Option 1: Simulation Mode (Easiest) ✅

**Best for**: Testing the UI, development, demonstrations

**What works**:
- ✅ Full GUI with all controls
- ✅ Simulated video feed
- ✅ Simulated SLAM visualization
- ✅ Voice recognition
- ✅ All UI features
- ❌ No actual robot control

**How to use**:

```cmd
# 1. Clone the repository
git clone <your-repo-url>
cd unitreeG1

# 2. Install dependencies (skip the SDK)
pip install -r requirements.txt

# 3. Run the application
python main.py
```

That's it! The app will automatically detect that the SDK isn't installed and run in simulation mode.

---

### Option 2: WSL2 (For Real Robot Control) ✅

**Best for**: Actually controlling your G1 robot from Windows

**What it is**: Windows Subsystem for Linux - run Linux inside Windows

**Installation Steps**:

#### Step 1: Install WSL2

```powershell
# Open PowerShell as Administrator
wsl --install
```

Restart your computer when prompted.

#### Step 2: Set up Ubuntu

After restart, Ubuntu will automatically open and ask you to create a username/password.

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip git -y
```

#### Step 3: Install Unitree SDK in WSL2

```bash
cd ~
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip3 install -e .
```

#### Step 4: Clone and Run the Application

```bash
cd ~
git clone <your-repo-url>
cd unitreeG1
pip3 install -r requirements.txt
python3 main.py
```

#### Step 5: Connect to Robot

Make sure:
1. Your G1 robot is powered on
2. You're connected to the robot's WiFi (from Windows)
3. WSL2 can access Windows network (it does by default)

The application should now be able to control your physical robot!

---

### Option 3: Native Windows Build (Advanced) ⚠️

**Best for**: Experienced developers who need native Windows

**Difficulty**: Hard

**Requirements**:
- Visual Studio 2019+ with C++ tools
- CMake 3.15+
- Git
- Several hours of troubleshooting

**Not recommended** unless you have specific reasons to avoid WSL2.

<details>
<summary>Click to see advanced Windows build instructions</summary>

#### 1. Install Build Tools

- Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/)
  - Select "Desktop development with C++"
  - Include CMake tools

#### 2. Build CycloneDDS from Source

```cmd
git clone https://github.com/eclipse-cyclonedds/cyclonedds.git
cd cyclonedds
git checkout releases/0.10.x
mkdir build
cd build
cmake -G "Visual Studio 17 2022" -A x64 ..
cmake --build . --config Release
cmake --install . --prefix C:\cyclonedds
```

#### 3. Set Environment Variable

```cmd
setx CYCLONEDDS_HOME "C:\cyclonedds"
```

Close and reopen your terminal.

#### 4. Install Unitree SDK

```cmd
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```

This may still fail due to other dependencies. Good luck! 🙏

</details>

---

## Comparison Table

| Feature | Simulation Mode | WSL2 | Native Windows |
|---------|----------------|------|----------------|
| **Setup Time** | 2 minutes | 10 minutes | 2+ hours |
| **Difficulty** | Easy | Medium | Hard |
| **UI Testing** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Robot Control** | ❌ No | ✅ Yes | ⚠️ Maybe |
| **Video Feed** | ✅ Simulated | ✅ Real | ⚠️ Maybe |
| **SLAM** | ✅ Simulated | ✅ Real | ⚠️ Maybe |
| **Recommended?** | For testing | For robot | Not really |

---

## FAQs

### Q: Why doesn't the SDK work on Windows?

A: The SDK depends on `cyclonedds==0.10.2`, which doesn't provide pre-compiled binaries (wheels) for Windows. You'd need to compile it from source, which requires significant C++ development tools.

### Q: Can I use WSL2 to control the robot?

A: Yes! WSL2 has full network access and can connect to your robot just like a Linux machine.

### Q: Is simulation mode useful?

A: Absolutely! It's perfect for:
- Testing the UI
- Developing new features
- Demonstrating the application
- Training users

### Q: Will you add better Windows support?

A: This depends on Unitree updating their SDK. The issue is in the `cyclonedds` dependency, not this application.

### Q: Can I use VirtualBox/VMware instead of WSL2?

A: Yes, but WSL2 is easier and has better performance. If you prefer a VM:
1. Install Ubuntu 22.04 LTS in your VM
2. Follow the WSL2 instructions above
3. Make sure VM has network access to the robot

---

## Troubleshooting

### Application Won't Start (Missing Dependencies)

```cmd
pip install customtkinter opencv-python numpy matplotlib
```

### "No module named 'unitree_sdk2py'"

This is normal if you're using simulation mode. The app will work without it.

If you want robot control, use WSL2 (Option 2).

### WSL2: "Cannot connect to display"

WSL2 needs GUI support. Install WSLg:

```bash
# In WSL2
sudo apt install -y mesa-utils
```

Or use Windows 11 (has WSLg built-in).

### Robot Not Responding

- Make sure robot is activated (L1+A, L1+UP on controller)
- Verify network connection: `ping 192.168.123.164`
- Check you're using WSL2, not simulation mode

---

## Next Steps

1. **Start with Simulation Mode** to familiarize yourself with the interface
2. **When ready for robot control**, set up WSL2
3. **Read [HARDWARE_SETUP.md](HARDWARE_SETUP.md)** for network configuration and robot activation
4. **Check [QUICKSTART.md](QUICKSTART.md)** for usage instructions

---

## Getting Help

- **UI Issues**: Open a GitHub issue
- **SDK Issues**: Check [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python)
- **WSL2 Help**: [Microsoft WSL Documentation](https://learn.microsoft.com/en-us/windows/wsl/)

---

**Enjoy your Unitree G1! 🤖**
