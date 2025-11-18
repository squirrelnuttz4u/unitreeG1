"""
Unitree G1 Robot Controller
Handles communication and control of the Unitree G1 EDU robot
"""

import logging
import threading
import time
import subprocess
import sys
import os
import tempfile
from typing import Optional, Callable
from enum import Enum

# Try to import unitree SDK (G1-specific)
try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
    from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
    from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
    UNITREE_SDK_AVAILABLE = True
    print("[SDK] Unitree SDK loaded successfully!")
except ImportError as e:
    UNITREE_SDK_AVAILABLE = False
    print(f"[SDK] Unitree SDK not available: {e}")
    print("[SDK] Running in simulation mode.")


class RobotState(Enum):
    """Robot connection states"""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    ERROR = 3


class MotionMode(Enum):
    """Available motion modes"""
    IDLE = 0
    WALK = 1
    RUN = 2
    STAND = 3
    SIT = 4
    DAMP = 5


def get_network_interface():
    """
    Auto-detect the network interface connected to the robot network.
    Returns the interface name or None if not found.
    """
    try:
        # Try to find interface on 192.168.123.x network
        if sys.platform == "linux":
            result = subprocess.run(
                ["ip", "route", "get", "192.168.123.164"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse output like: "192.168.123.164 dev eth0 src 192.168.123.99"
                parts = result.stdout.split()
                if "dev" in parts:
                    idx = parts.index("dev")
                    if idx + 1 < len(parts):
                        interface = parts[idx + 1]
                        print(f"[Network] Auto-detected interface: {interface}")
                        return interface

            # Fallback: list all interfaces and find one that's up
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'state UP' in line:
                    # Extract interface name
                    parts = line.split(':')
                    if len(parts) >= 2:
                        interface = parts[1].strip().split('@')[0]
                        if interface not in ['lo']:  # Skip loopback
                            print(f"[Network] Using active interface: {interface}")
                            return interface

        # Default fallbacks
        print("[Network] Could not auto-detect interface, trying defaults...")
        return "eth0"

    except Exception as e:
        print(f"[Network] Error detecting interface: {e}")
        return "eth0"


def setup_cyclonedds_config(network_interface: str) -> str:
    """
    Create CycloneDDS XML configuration for robot communication.

    This is CRITICAL for DDS to work properly with the Unitree robot.
    The configuration:
    - Disables multicast (robot uses unicast)
    - Sets the correct network interface
    - Configures peer discovery for the robot IP

    Args:
        network_interface: Network interface name (e.g., "eth0")

    Returns:
        Path to the configuration file
    """
    # CycloneDDS configuration for Unitree robot communication
    config_xml = f'''<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://cdds.io/config https://raw.githubusercontent.com/eclipse-cyclonedds/cyclonedds/master/etc/cyclonedds.xsd">
    <Domain Id="any">
        <General>
            <Interfaces>
                <NetworkInterface name="{network_interface}" priority="default" multicast="false"/>
            </Interfaces>
            <AllowMulticast>false</AllowMulticast>
            <MaxMessageSize>65500B</MaxMessageSize>
        </General>
        <Discovery>
            <EnableTopicDiscoveryEndpoints>true</EnableTopicDiscoveryEndpoints>
            <ParticipantIndex>auto</ParticipantIndex>
            <Peers>
                <Peer address="192.168.123.164"/>
            </Peers>
        </Discovery>
        <Tracing>
            <Verbosity>warning</Verbosity>
            <OutputFile>stderr</OutputFile>
        </Tracing>
    </Domain>
</CycloneDDS>
'''

    # Create config file in temp directory
    config_dir = os.path.join(tempfile.gettempdir(), "unitree_g1")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "cyclonedds.xml")

    with open(config_path, 'w') as f:
        f.write(config_xml)

    print(f"[DDS] Created CycloneDDS config at: {config_path}")
    return config_path


class G1Controller:
    """Main controller for Unitree G1 robot"""

    def __init__(self, robot_ip: str = "192.168.123.164", network_interface: str = None):
        """
        Initialize G1 Controller

        Args:
            robot_ip: IP address of the robot (default: 192.168.123.164)
            network_interface: Network interface name (auto-detected if None)
        """
        self.robot_ip = robot_ip
        self.state = RobotState.DISCONNECTED
        self.motion_mode = MotionMode.IDLE

        # SDK clients (G1-specific)
        self.loco_client = None        # LocoClient for locomotion control
        self.audio_client = None       # AudioClient for audio/LED control

        # Network interface (auto-detect if not specified)
        if network_interface:
            self.network_interface = network_interface
        else:
            self.network_interface = get_network_interface()

        print(f"[Config] Using network interface: {self.network_interface}")
        print(f"[Config] Robot IP: {self.robot_ip}")

        # Status callbacks
        self.status_callbacks = []
        self.video_callbacks = []

        # Threading
        self.lock = threading.RLock()
        self.connected = False

        # SDK initialized flag
        self._sdk_initialized = False

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_network_connectivity(self) -> bool:
        """
        Check if the robot is reachable on the network.

        Returns:
            bool: True if robot is pingable
        """
        try:
            self.logger.info(f"Checking network connectivity to {self.robot_ip}...")

            if sys.platform == "linux":
                # Use ping with 1 second timeout
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", self.robot_ip],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    self.logger.info(f"Robot is reachable at {self.robot_ip}")
                    return True
                else:
                    self.logger.warning(f"Robot not reachable: {result.stderr}")
                    return False
            else:
                # Windows
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", self.robot_ip],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Network check failed: {e}")
            return False

    def get_local_ip(self) -> str:
        """Get the local IP address on the robot network."""
        try:
            if sys.platform == "linux":
                result = subprocess.run(
                    ["ip", "route", "get", self.robot_ip],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    parts = result.stdout.split()
                    if "src" in parts:
                        idx = parts.index("src")
                        if idx + 1 < len(parts):
                            return parts[idx + 1]
        except Exception as e:
            self.logger.error(f"Failed to get local IP: {e}")
        return "unknown"

    def connect(self) -> bool:
        """
        Connect to the G1 robot

        Returns:
            bool: True if connection successful
        """
        self.logger.info(f"Connecting to G1 robot at {self.robot_ip}...")
        self.logger.info(f"Using network interface: {self.network_interface}")
        self.state = RobotState.CONNECTING

        try:
            if UNITREE_SDK_AVAILABLE:
                # Check network connectivity first
                local_ip = self.get_local_ip()
                self.logger.info(f"Local IP on robot network: {local_ip}")

                if not self.check_network_connectivity():
                    self.logger.warning("Robot not reachable via ping - will attempt connection anyway")
                    print("\n" + "="*50)
                    print("WARNING: Robot not responding to ping!")
                    print(f"  - Robot IP: {self.robot_ip}")
                    print(f"  - Local IP: {local_ip}")
                    print(f"  - Interface: {self.network_interface}")
                    print("\nPlease check:")
                    print("  1. Robot is powered on")
                    print("  2. Network cable is connected")
                    print("  3. IP address is correct (192.168.123.164)")
                    print("="*50 + "\n")

                # CRITICAL: Set up CycloneDDS configuration BEFORE initializing SDK
                # This configures the DDS middleware for unicast communication with the robot
                self.logger.info("Setting up CycloneDDS configuration...")
                config_path = setup_cyclonedds_config(self.network_interface)
                os.environ["CYCLONEDDS_URI"] = f"file://{config_path}"
                self.logger.info(f"Set CYCLONEDDS_URI={os.environ['CYCLONEDDS_URI']}")

                # Initialize DDS channel factory (required for SDK)
                # Parameters: domain_id, network_interface
                self.logger.info("Initializing ChannelFactory...")
                ChannelFactoryInitialize(0, self.network_interface)
                self._sdk_initialized = True
                self.logger.info("ChannelFactory initialized successfully")

                # Initialize LocoClient for locomotion control
                self.logger.info("Initializing LocoClient...")
                self.loco_client = LocoClient()
                self.loco_client.SetTimeout(10.0)  # Set timeout for RPC calls
                self.loco_client.Init()
                self.logger.info("LocoClient initialized successfully")

                # Initialize AudioClient for audio/LED control
                try:
                    self.logger.info("Initializing AudioClient...")
                    self.audio_client = AudioClient()
                    self.audio_client.SetTimeout(10.0)
                    self.audio_client.Init()
                    self.logger.info("AudioClient initialized successfully")
                except Exception as e:
                    self.logger.warning(f"AudioClient initialization failed: {e}")
                    self.audio_client = None

                self.connected = True
                self.state = RobotState.CONNECTED
                self.logger.info("Successfully connected to G1 robot!")
                self._notify_status("Connected to robot")

                # Print reminder about robot activation
                print("\n" + "="*50)
                print("IMPORTANT: Make sure to activate the robot!")
                print("1. Press L1 + A on controller (sport mode)")
                print("2. Press L1 + UP on controller (SDK control)")
                print("="*50 + "\n")

                return True
            else:
                # Simulation mode
                self.logger.info("Running in simulation mode (SDK not available)")
                time.sleep(1)  # Simulate connection delay
                self.connected = True
                self.state = RobotState.CONNECTED
                self._notify_status("Connected (Simulation Mode)")
                return True

        except Exception as e:
            self.logger.error(f"Failed to connect to robot: {e}")
            import traceback
            traceback.print_exc()
            self.state = RobotState.ERROR
            self._notify_status(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from the robot"""
        self.logger.info("Disconnecting from robot...")

        try:
            # Stop any ongoing motion
            if self.is_connected():
                self.stop()

            # Close SDK connections
            self.loco_client = None
            self.audio_client = None

            self.connected = False
            self.state = RobotState.DISCONNECTED
            self._notify_status("Disconnected from robot")

        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")

    def is_connected(self) -> bool:
        """Check if robot is connected"""
        return self.connected and self.state == RobotState.CONNECTED

    # Motion Control Methods

    def stand_up(self) -> bool:
        """Make the robot stand up from squat position"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Commanding robot to stand up...")
            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.Squat2StandUp()
                self.logger.info(f"Squat2StandUp() returned: {ret}")
            else:
                self._simulate_motion("Standing up")

            self.motion_mode = MotionMode.STAND
            self._notify_status("Standing up")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stand up: {e}")
            import traceback
            traceback.print_exc()
            return False

    def sit_down(self) -> bool:
        """Make the robot sit down (squat)"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Commanding robot to sit down...")
            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.StandUp2Squat()
                self.logger.info(f"StandUp2Squat() returned: {ret}")
            else:
                self._simulate_motion("Sitting down")

            self.motion_mode = MotionMode.SIT
            self._notify_status("Sitting down")
            return True
        except Exception as e:
            self.logger.error(f"Failed to sit down: {e}")
            import traceback
            traceback.print_exc()
            return False

    def walk(self, velocity_x: float = 0.3, velocity_y: float = 0.0,
             yaw_rate: float = 0.0) -> bool:
        """
        Make the robot walk

        Args:
            velocity_x: Forward/backward velocity (-1.0 to 1.0 m/s)
            velocity_y: Left/right velocity (-1.0 to 1.0 m/s)
            yaw_rate: Rotation rate (-1.0 to 1.0 rad/s)
        """
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info(f"Walking: vx={velocity_x}, vy={velocity_y}, yaw={yaw_rate}")

            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.Move(velocity_x, velocity_y, yaw_rate)
                self.logger.info(f"Move() returned: {ret}")
            else:
                self._simulate_motion(f"Walking (vx={velocity_x:.2f}, vy={velocity_y:.2f})")

            self.motion_mode = MotionMode.WALK
            self._notify_status(f"Walking (velocity: {velocity_x:.2f})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to walk: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, velocity_x: float = 0.6, velocity_y: float = 0.0,
            yaw_rate: float = 0.0) -> bool:
        """
        Make the robot run (faster walking)

        Args:
            velocity_x: Forward/backward velocity (-1.5 to 1.5 m/s)
            velocity_y: Left/right velocity (-1.5 to 1.5 m/s)
            yaw_rate: Rotation rate (-2.0 to 2.0 rad/s)
        """
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info(f"Running: vx={velocity_x}, vy={velocity_y}, yaw={yaw_rate}")

            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.Move(velocity_x, velocity_y, yaw_rate)
                self.logger.info(f"Move() returned: {ret}")
            else:
                self._simulate_motion(f"Running (vx={velocity_x:.2f})")

            self.motion_mode = MotionMode.RUN
            self._notify_status(f"Running (velocity: {velocity_x:.2f})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to run: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop(self) -> bool:
        """Stop all motion"""
        if not self.is_connected():
            return True  # Already stopped if not connected

        try:
            self.logger.info("Stopping robot...")

            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.Move(0.0, 0.0, 0.0)
                self.logger.info(f"Move(0,0,0) returned: {ret}")
            else:
                self._simulate_motion("Stopped")

            self.motion_mode = MotionMode.IDLE
            self._notify_status("Stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop: {e}")
            import traceback
            traceback.print_exc()
            return False

    def damp(self) -> bool:
        """Enter damping mode (motors relaxed)"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Entering damp mode...")

            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.Damp()
                self.logger.info(f"Damp() returned: {ret}")
            else:
                self._simulate_motion("Damp mode")

            self.motion_mode = MotionMode.DAMP
            self._notify_status("Damp mode")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enter damp mode: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Gesture Control Methods

    def wave_hand(self) -> bool:
        """Make the robot wave"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Performing wave gesture...")

            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.WaveHand()
                self.logger.info(f"WaveHand() returned: {ret}")
            else:
                self._simulate_motion("Waving hand")

            self._notify_status("Waving hand")
            return True
        except Exception as e:
            self.logger.error(f"Failed to wave hand: {e}")
            import traceback
            traceback.print_exc()
            return False

    def shake_hand(self) -> bool:
        """Make the robot shake hands"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Performing handshake gesture...")
            # Note: ShakeHand may not be available in all SDK versions
            # Using simulation for now
            self._simulate_motion("Shaking hand")
            self._notify_status("Shaking hand")
            return True
        except Exception as e:
            self.logger.error(f"Failed to shake hand: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Additional G1-Specific Motion Methods

    def high_stand(self) -> bool:
        """Make the robot stand at high position"""
        if not self.is_connected():
            return False

        try:
            self.logger.info("High stand...")
            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.HighStand()
                self.logger.info(f"HighStand() returned: {ret}")
            else:
                self._simulate_motion("High stand")
            self._notify_status("High stand")
            return True
        except Exception as e:
            self.logger.error(f"Failed to high stand: {e}")
            import traceback
            traceback.print_exc()
            return False

    def low_stand(self) -> bool:
        """Make the robot stand at low position"""
        if not self.is_connected():
            return False

        try:
            self.logger.info("Low stand...")
            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.LowStand()
                self.logger.info(f"LowStand() returned: {ret}")
            else:
                self._simulate_motion("Low stand")
            self._notify_status("Low stand")
            return True
        except Exception as e:
            self.logger.error(f"Failed to low stand: {e}")
            import traceback
            traceback.print_exc()
            return False

    def zero_torque(self) -> bool:
        """Set all motors to zero torque"""
        if not self.is_connected():
            return False

        try:
            self.logger.info("Zero torque...")
            if UNITREE_SDK_AVAILABLE and self.loco_client:
                ret = self.loco_client.ZeroTorque()
                self.logger.info(f"ZeroTorque() returned: {ret}")
            else:
                self._simulate_motion("Zero torque")
            self._notify_status("Zero torque mode")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set zero torque: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Audio Methods

    def play_audio(self, audio_file: str) -> bool:
        """Play audio file on robot"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info(f"Playing audio: {audio_file}")

            if UNITREE_SDK_AVAILABLE and self.audio_client:
                ret = self.audio_client.PlayAudio(audio_file)
                self.logger.info(f"PlayAudio() returned: {ret}")
            else:
                self._simulate_motion(f"Playing audio: {audio_file}")

            self._notify_status(f"Playing: {audio_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Status and Callback Methods

    def register_status_callback(self, callback: Callable[[str], None]):
        """Register a callback for status updates"""
        self.status_callbacks.append(callback)

    def register_video_callback(self, callback: Callable):
        """Register a callback for video frames"""
        self.video_callbacks.append(callback)

    def _notify_status(self, message: str):
        """Notify all registered status callbacks"""
        for callback in self.status_callbacks:
            try:
                callback(message)
            except Exception as e:
                self.logger.error(f"Error in status callback: {e}")

    def _simulate_motion(self, action: str):
        """Simulate motion in non-SDK mode"""
        self.logger.info(f"[SIMULATION] {action}")
        time.sleep(0.5)  # Simulate action delay

    def get_telemetry(self) -> dict:
        """Get current robot telemetry data"""
        return {
            "state": self.state.name,
            "motion_mode": self.motion_mode.name,
            "connected": self.connected,
            "robot_ip": self.robot_ip,
            "local_ip": self.get_local_ip(),
            "network_interface": self.network_interface,
            "sdk_available": UNITREE_SDK_AVAILABLE,
            "sdk_initialized": self._sdk_initialized,
            "cyclonedds_uri": os.environ.get("CYCLONEDDS_URI", "not set")
        }

    def diagnose(self) -> dict:
        """
        Run diagnostics on the robot connection.

        Returns:
            dict: Diagnostic information
        """
        diagnostics = {
            "network_interface": self.network_interface,
            "robot_ip": self.robot_ip,
            "local_ip": self.get_local_ip(),
            "robot_pingable": self.check_network_connectivity(),
            "sdk_available": UNITREE_SDK_AVAILABLE,
            "sdk_initialized": self._sdk_initialized,
            "cyclonedds_uri": os.environ.get("CYCLONEDDS_URI", "not set"),
            "connected": self.connected
        }

        print("\n" + "="*50)
        print("G1 Controller Diagnostics")
        print("="*50)
        for key, value in diagnostics.items():
            print(f"  {key}: {value}")
        print("="*50 + "\n")

        return diagnostics
