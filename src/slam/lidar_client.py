"""
Unitree L1 LiDAR Client
Connects to the L1 LiDAR sensor on the G1 robot for point cloud data
"""

import socket
import struct
import numpy as np
import logging
import threading
import time
from typing import Optional, Callable, List

# Try to import unilidar SDK
try:
    from unilidar_sdk import UnitreeLidar
    UNILIDAR_SDK_AVAILABLE = True
    print("[LiDAR] Unilidar SDK loaded successfully!")
except ImportError:
    UNILIDAR_SDK_AVAILABLE = False
    print("[LiDAR] Unilidar SDK not available, using direct UDP connection")


class LidarClient:
    """Client for Unitree L1 LiDAR sensor"""

    def __init__(self, lidar_ip: str = "192.168.123.120", lidar_port: int = 6101):
        """
        Initialize LiDAR client

        Args:
            lidar_ip: IP address of the L1 LiDAR (default: 192.168.123.120)
            lidar_port: UDP port for point cloud data
        """
        self.lidar_ip = lidar_ip
        self.lidar_port = lidar_port
        self.logger = logging.getLogger(__name__)

        # Connection
        self.socket = None
        self.is_running = False
        self.receive_thread = None

        # Data storage
        self.point_cloud = None
        self.imu_data = None
        self.lock = threading.Lock()

        # Callbacks
        self.point_cloud_callbacks: List[Callable] = []

        # SDK handle
        self.lidar_handle = None

        # Statistics
        self.frames_received = 0
        self.last_frame_time = 0

    def connect(self) -> bool:
        """
        Connect to the LiDAR

        Returns:
            bool: True if connected successfully
        """
        try:
            self.logger.info(f"Connecting to L1 LiDAR at {self.lidar_ip}:{self.lidar_port}")

            if UNILIDAR_SDK_AVAILABLE:
                # Use official SDK
                self.lidar_handle = UnitreeLidar()
                # Initialize with IP
                ret = self.lidar_handle.setIP(self.lidar_ip)
                if ret != 0:
                    self.logger.error(f"Failed to set LiDAR IP: {ret}")
                    return False

                ret = self.lidar_handle.init()
                if ret != 0:
                    self.logger.error(f"Failed to initialize LiDAR: {ret}")
                    return False

                self.logger.info("LiDAR SDK initialized successfully")
            else:
                # Use direct UDP connection
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.settimeout(2.0)

                # Bind to receive data
                self.socket.bind(('0.0.0.0', self.lidar_port))
                self.logger.info(f"UDP socket bound to port {self.lidar_port}")

            self.is_running = True

            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            self.logger.info("LiDAR client connected and receiving data")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to LiDAR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect(self):
        """Disconnect from the LiDAR"""
        self.logger.info("Disconnecting from LiDAR")
        self.is_running = False

        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)

        if self.socket:
            self.socket.close()
            self.socket = None

        if self.lidar_handle:
            self.lidar_handle = None

        self.logger.info("LiDAR client disconnected")

    def _receive_loop(self):
        """Main loop for receiving LiDAR data"""
        while self.is_running:
            try:
                if UNILIDAR_SDK_AVAILABLE and self.lidar_handle:
                    # Get data from SDK
                    cloud = self.lidar_handle.getCloud()
                    if cloud is not None and len(cloud) > 0:
                        with self.lock:
                            self.point_cloud = np.array(cloud)
                            self.frames_received += 1
                            self.last_frame_time = time.time()

                        self._notify_point_cloud(self.point_cloud)

                    # Get IMU data
                    imu = self.lidar_handle.getIMU()
                    if imu is not None:
                        with self.lock:
                            self.imu_data = imu

                elif self.socket:
                    # Direct UDP receive
                    try:
                        data, addr = self.socket.recvfrom(65535)
                        if data:
                            point_cloud = self._parse_point_cloud(data)
                            if point_cloud is not None:
                                with self.lock:
                                    self.point_cloud = point_cloud
                                    self.frames_received += 1
                                    self.last_frame_time = time.time()

                                self._notify_point_cloud(point_cloud)
                    except socket.timeout:
                        pass

                time.sleep(0.01)  # ~100Hz max

            except Exception as e:
                self.logger.error(f"Error in LiDAR receive loop: {e}")
                time.sleep(0.1)

    def _parse_point_cloud(self, data: bytes) -> Optional[np.ndarray]:
        """
        Parse point cloud data from UDP packet

        The L1 LiDAR sends point cloud data in a specific binary format.
        Each point contains: x, y, z, intensity, ring

        Args:
            data: Raw UDP packet data

        Returns:
            np.ndarray: Nx3 array of points (x, y, z) or None
        """
        try:
            # Basic header check
            if len(data) < 42:  # Minimum packet size
                return None

            # Parse header (simplified - actual format may vary)
            # The real format depends on Unitree's packet structure
            points = []

            # Skip header (varies by protocol version)
            offset = 42

            # Each point: 4 bytes each for x, y, z (float32)
            point_size = 12  # 3 * 4 bytes

            while offset + point_size <= len(data):
                x = struct.unpack('<f', data[offset:offset + 4])[0]
                y = struct.unpack('<f', data[offset + 4:offset + 8])[0]
                z = struct.unpack('<f', data[offset + 8:offset + 12])[0]

                # Filter invalid points
                if -100 < x < 100 and -100 < y < 100 and -100 < z < 100:
                    points.append([x, y, z])

                offset += point_size

            if points:
                return np.array(points, dtype=np.float32)

            return None

        except Exception as e:
            self.logger.debug(f"Error parsing point cloud: {e}")
            return None

    def get_point_cloud(self) -> Optional[np.ndarray]:
        """
        Get the latest point cloud

        Returns:
            Optional[np.ndarray]: Nx3 array of points or None
        """
        with self.lock:
            if self.point_cloud is not None:
                return self.point_cloud.copy()
        return None

    def get_imu_data(self) -> Optional[dict]:
        """
        Get the latest IMU data

        Returns:
            Optional[dict]: IMU data dictionary or None
        """
        with self.lock:
            return self.imu_data

    def register_callback(self, callback: Callable[[np.ndarray], None]):
        """
        Register callback for new point cloud data

        Args:
            callback: Function to call with new point cloud
        """
        self.point_cloud_callbacks.append(callback)

    def _notify_point_cloud(self, point_cloud: np.ndarray):
        """Notify all registered callbacks"""
        for callback in self.point_cloud_callbacks:
            try:
                callback(point_cloud.copy())
            except Exception as e:
                self.logger.error(f"Error in point cloud callback: {e}")

    def get_statistics(self) -> dict:
        """
        Get LiDAR statistics

        Returns:
            dict: Statistics dictionary
        """
        with self.lock:
            num_points = len(self.point_cloud) if self.point_cloud is not None else 0
            return {
                "connected": self.is_running,
                "lidar_ip": self.lidar_ip,
                "frames_received": self.frames_received,
                "num_points": num_points,
                "last_frame_age": time.time() - self.last_frame_time if self.last_frame_time > 0 else -1,
                "sdk_available": UNILIDAR_SDK_AVAILABLE
            }

    def check_connectivity(self) -> bool:
        """
        Check if LiDAR is reachable

        Returns:
            bool: True if LiDAR is pingable
        """
        import subprocess
        import sys

        try:
            if sys.platform == "linux":
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", self.lidar_ip],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            else:
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", self.lidar_ip],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error checking LiDAR connectivity: {e}")
            return False


# Convenience function for testing
def test_lidar():
    """Test LiDAR connection"""
    client = LidarClient()

    print("Checking LiDAR connectivity...")
    if client.check_connectivity():
        print(f"LiDAR is reachable at {client.lidar_ip}")
    else:
        print(f"LiDAR not reachable at {client.lidar_ip}")
        return

    print("Connecting to LiDAR...")
    if client.connect():
        print("Connected! Receiving point cloud data...")

        # Wait for some frames
        for i in range(50):
            stats = client.get_statistics()
            print(f"Frame {i}: {stats['num_points']} points, {stats['frames_received']} total frames")
            time.sleep(0.1)

        client.disconnect()
        print("Test complete")
    else:
        print("Failed to connect")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_lidar()
