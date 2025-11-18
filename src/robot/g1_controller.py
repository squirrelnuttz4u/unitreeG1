"""
Unitree G1 Robot Controller
Handles communication and control of the Unitree G1 EDU robot
"""

import logging
import threading
import time
from typing import Optional, Callable
from enum import Enum

# Try to import unitree SDK
try:
    from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelPublisher
    from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowCmd_
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeCmd_
    from unitree_sdk2py.go2.sport.sport_client import SportClient
    UNITREE_SDK_AVAILABLE = True
except ImportError:
    UNITREE_SDK_AVAILABLE = False
    logging.warning("Unitree SDK not available. Running in simulation mode.")


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


class G1Controller:
    """Main controller for Unitree G1 robot"""

    def __init__(self, robot_ip: str = "192.168.123.164"):
        """
        Initialize G1 Controller

        Args:
            robot_ip: IP address of the robot (default: 192.168.123.164)
        """
        self.robot_ip = robot_ip
        self.state = RobotState.DISCONNECTED
        self.motion_mode = MotionMode.IDLE

        # SDK clients
        self.sport_client = None
        self.loco_client = None
        self.audio_client = None
        self.arm_action_client = None

        # Status callbacks
        self.status_callbacks = []
        self.video_callbacks = []

        # Threading
        self.lock = threading.RLock()
        self.connected = False

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Connect to the G1 robot

        Returns:
            bool: True if connection successful
        """
        self.logger.info(f"Connecting to G1 robot at {self.robot_ip}...")
        self.state = RobotState.CONNECTING

        try:
            if UNITREE_SDK_AVAILABLE:
                # Initialize SDK clients
                self.sport_client = SportClient()
                self.sport_client.Init()

                # TODO: Initialize other clients when available
                # self.loco_client = LocoClient()
                # self.audio_client = AudioClient()
                # self.arm_action_client = G1ArmActionClient()

                self.connected = True
                self.state = RobotState.CONNECTED
                self.logger.info("Successfully connected to G1 robot")
                self._notify_status("Connected to robot")
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
            self.state = RobotState.ERROR
            self._notify_status(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from the robot"""
        self.logger.info("Disconnecting from robot...")

        try:
            # Stop any ongoing motion
            self.stop()

            # Close SDK connections
            if self.sport_client:
                self.sport_client = None

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
        """Make the robot stand up"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Commanding robot to stand up")
            if UNITREE_SDK_AVAILABLE and self.sport_client:
                self.sport_client.StandUp()
            else:
                self._simulate_motion("Standing up")

            self.motion_mode = MotionMode.STAND
            self._notify_status("Standing up")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stand up: {e}")
            return False

    def sit_down(self) -> bool:
        """Make the robot sit down"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Commanding robot to sit down")
            if UNITREE_SDK_AVAILABLE and self.sport_client:
                self.sport_client.SitDown()
            else:
                self._simulate_motion("Sitting down")

            self.motion_mode = MotionMode.SIT
            self._notify_status("Sitting down")
            return True
        except Exception as e:
            self.logger.error(f"Failed to sit down: {e}")
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

            if UNITREE_SDK_AVAILABLE and self.sport_client:
                self.sport_client.Move(velocity_x, velocity_y, yaw_rate)
            else:
                self._simulate_motion(f"Walking (vx={velocity_x:.2f}, vy={velocity_y:.2f})")

            self.motion_mode = MotionMode.WALK
            self._notify_status(f"Walking (velocity: {velocity_x:.2f})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to walk: {e}")
            return False

    def run(self, velocity_x: float = 0.6, velocity_y: float = 0.0,
            yaw_rate: float = 0.0) -> bool:
        """
        Make the robot run

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

            if UNITREE_SDK_AVAILABLE and self.sport_client:
                # Running is just faster walking
                self.sport_client.Move(velocity_x, velocity_y, yaw_rate)
            else:
                self._simulate_motion(f"Running (vx={velocity_x:.2f})")

            self.motion_mode = MotionMode.RUN
            self._notify_status(f"Running (velocity: {velocity_x:.2f})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to run: {e}")
            return False

    def stop(self) -> bool:
        """Stop all motion"""
        if not self.is_connected():
            return True  # Already stopped if not connected

        try:
            self.logger.info("Stopping robot")

            if UNITREE_SDK_AVAILABLE and self.sport_client:
                self.sport_client.StopMove()
            else:
                self._simulate_motion("Stopped")

            self.motion_mode = MotionMode.IDLE
            self._notify_status("Stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop: {e}")
            return False

    def damp(self) -> bool:
        """Enter damping mode (motors relaxed)"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Entering damp mode")

            if UNITREE_SDK_AVAILABLE and self.sport_client:
                self.sport_client.Damp()
            else:
                self._simulate_motion("Damp mode")

            self.motion_mode = MotionMode.DAMP
            self._notify_status("Damp mode")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enter damp mode: {e}")
            return False

    # Gesture Control Methods

    def wave_hand(self) -> bool:
        """Make the robot wave"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Performing wave gesture")

            if UNITREE_SDK_AVAILABLE and self.arm_action_client:
                # TODO: Implement with actual SDK
                # self.arm_action_client.WaveHand()
                pass
            else:
                self._simulate_motion("Waving hand")

            self._notify_status("Waving hand")
            return True
        except Exception as e:
            self.logger.error(f"Failed to wave hand: {e}")
            return False

    def shake_hand(self) -> bool:
        """Make the robot shake hands"""
        if not self.is_connected():
            self.logger.warning("Robot not connected")
            return False

        try:
            self.logger.info("Performing handshake gesture")

            if UNITREE_SDK_AVAILABLE and self.arm_action_client:
                # TODO: Implement with actual SDK
                # self.arm_action_client.ShakeHand()
                pass
            else:
                self._simulate_motion("Shaking hand")

            self._notify_status("Shaking hand")
            return True
        except Exception as e:
            self.logger.error(f"Failed to shake hand: {e}")
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
                # TODO: Implement with actual SDK
                # self.audio_client.PlayAudio(audio_file)
                pass
            else:
                self._simulate_motion(f"Playing audio: {audio_file}")

            self._notify_status(f"Playing: {audio_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
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
            "sdk_available": UNITREE_SDK_AVAILABLE
        }
