"""
Video Feed Handler for Unitree G1
Manages camera streams and video display
Supports Intel RealSense D435i depth camera
"""

import cv2
import numpy as np
import logging
import threading
import time
from typing import Optional, Callable

# Try to import RealSense SDK
try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
    print("[Camera] Intel RealSense SDK loaded successfully!")
except ImportError:
    REALSENSE_AVAILABLE = False
    print("[Camera] Intel RealSense SDK not available (pip install pyrealsense2)")


class VideoFeedHandler:
    """Handles video streaming from G1 cameras"""

    def __init__(self, robot_ip: str = "192.168.123.164"):
        """
        Initialize video feed handler

        Args:
            robot_ip: IP address of the robot
        """
        self.robot_ip = robot_ip
        self.logger = logging.getLogger(__name__)

        # Video stream
        self.camera_stream = None
        self.is_streaming = False
        self.stream_thread = None

        # Frame storage
        self.current_frame = None
        self.frame_lock = threading.Lock()

        # Callbacks
        self.frame_callbacks = []

        # Camera settings
        self.camera_width = 1280
        self.camera_height = 720
        self.camera_fps = 30

        # RealSense specific
        self.rs_pipeline = None
        self.rs_config = None
        self.rs_align = None
        self.depth_frame = None
        self.use_realsense = False

    def start_stream(self, camera_index: int = 0) -> bool:
        """
        Start video streaming

        Args:
            camera_index: Camera index (0 for main camera)

        Returns:
            bool: True if stream started successfully
        """
        if self.is_streaming:
            self.logger.warning("Stream already running")
            return True

        try:
            self.logger.info(f"Starting video stream from camera {camera_index}")

            # Try Intel RealSense first (G1 has D435i)
            if REALSENSE_AVAILABLE:
                try:
                    self.logger.info("Attempting to connect to Intel RealSense D435i...")
                    self.rs_pipeline = rs.pipeline()
                    self.rs_config = rs.config()

                    # Configure streams
                    self.rs_config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
                    self.rs_config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

                    # Start pipeline
                    profile = self.rs_pipeline.start(self.rs_config)

                    # Create align object for depth to color alignment
                    self.rs_align = rs.align(rs.stream.color)

                    self.use_realsense = True
                    self.logger.info("Intel RealSense D435i connected successfully!")

                except Exception as e:
                    self.logger.warning(f"Failed to connect to RealSense: {e}")
                    self.rs_pipeline = None
                    self.use_realsense = False

            # Try OpenCV camera as fallback
            if not self.use_realsense:
                stream_url = self._get_stream_url(camera_index)
                self.camera_stream = cv2.VideoCapture(stream_url)

                if not self.camera_stream.isOpened():
                    self.logger.warning("Could not open robot camera, using simulation")
                    self.camera_stream = None

            self.is_streaming = True

            # Start streaming thread
            self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.stream_thread.start()

            self.logger.info("Video stream started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start video stream: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop_stream(self):
        """Stop video streaming"""
        self.logger.info("Stopping video stream")
        self.is_streaming = False

        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)

        if self.rs_pipeline:
            self.rs_pipeline.stop()
            self.rs_pipeline = None

        if self.camera_stream:
            self.camera_stream.release()
            self.camera_stream = None

        self.logger.info("Video stream stopped")

    def _get_stream_url(self, camera_index: int) -> str:
        """
        Get stream URL for camera

        Args:
            camera_index: Camera index

        Returns:
            str: Stream URL
        """
        # Try RTSP stream from robot
        # Format: rtsp://192.168.123.164:8554/camera_{index}
        rtsp_url = f"rtsp://{self.robot_ip}:8554/camera_{camera_index}"

        # For simulation, use local camera or generate frames
        return camera_index  # OpenCV camera index

    def _stream_loop(self):
        """Main streaming loop"""
        frame_count = 0

        while self.is_streaming:
            try:
                frame = None

                # Try RealSense first
                if self.use_realsense and self.rs_pipeline:
                    try:
                        # Wait for frames
                        frames = self.rs_pipeline.wait_for_frames(timeout_ms=1000)

                        # Align depth to color
                        aligned_frames = self.rs_align.process(frames)

                        # Get color frame
                        color_frame = aligned_frames.get_color_frame()
                        depth_frame = aligned_frames.get_depth_frame()

                        if color_frame:
                            frame = np.asanyarray(color_frame.get_data())

                            # Store depth frame for potential use
                            if depth_frame:
                                with self.frame_lock:
                                    self.depth_frame = np.asanyarray(depth_frame.get_data())

                    except Exception as e:
                        self.logger.debug(f"RealSense frame error: {e}")

                # Try OpenCV camera
                elif self.camera_stream and self.camera_stream.isOpened():
                    ret, frame = self.camera_stream.read()
                    if not ret:
                        frame = None

                # Generate simulation frame if no real camera
                if frame is None:
                    frame = self._generate_simulation_frame(frame_count)

                # Update current frame and notify callbacks
                with self.frame_lock:
                    self.current_frame = frame.copy()
                self._notify_frame(frame)

                frame_count += 1
                time.sleep(1.0 / self.camera_fps)  # Limit to camera FPS

            except Exception as e:
                self.logger.error(f"Error in stream loop: {e}")
                time.sleep(0.1)

    def get_depth_frame(self) -> Optional[np.ndarray]:
        """
        Get the current depth frame (RealSense only)

        Returns:
            Optional[np.ndarray]: Depth frame or None
        """
        with self.frame_lock:
            if self.depth_frame is not None:
                return self.depth_frame.copy()
        return None

    def _generate_simulation_frame(self, frame_count: int) -> np.ndarray:
        """
        Generate a simulation video frame

        Args:
            frame_count: Current frame number

        Returns:
            np.ndarray: Generated frame
        """
        # Create a blank frame
        frame = np.zeros((self.camera_height, self.camera_width, 3), dtype=np.uint8)

        # Add gradient background
        for y in range(self.camera_height):
            color_val = int((y / self.camera_height) * 255)
            frame[y, :] = [color_val // 3, color_val // 2, color_val]

        # Add text
        text = "Unitree G1 - Simulation Mode"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = (self.camera_width - text_size[0]) // 2
        text_y = (self.camera_height + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2)

        # Add timestamp
        timestamp = f"Frame: {frame_count}"
        cv2.putText(frame, timestamp, (10, 30), font, 0.7, (255, 255, 0), 2)

        # Add moving circle
        center_x = int(self.camera_width // 2 + 200 * np.sin(frame_count * 0.05))
        center_y = int(self.camera_height // 2 + 100 * np.cos(frame_count * 0.05))
        cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), -1)

        return frame

    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Get the current video frame

        Returns:
            Optional[np.ndarray]: Current frame or None
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

    def register_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """
        Register callback for new frames

        Args:
            callback: Function to call with new frames
        """
        self.frame_callbacks.append(callback)

    def _notify_frame(self, frame: np.ndarray):
        """
        Notify all registered callbacks of new frame

        Args:
            frame: New video frame
        """
        for callback in self.frame_callbacks:
            try:
                callback(frame.copy())
            except Exception as e:
                self.logger.error(f"Error in frame callback: {e}")

    def capture_snapshot(self, filename: str) -> bool:
        """
        Capture current frame to file

        Args:
            filename: Output filename

        Returns:
            bool: True if successful
        """
        frame = self.get_current_frame()
        if frame is not None:
            try:
                cv2.imwrite(filename, frame)
                self.logger.info(f"Snapshot saved to {filename}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to save snapshot: {e}")
                return False
        return False
