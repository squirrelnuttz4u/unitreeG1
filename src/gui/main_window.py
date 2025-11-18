"""
Main GUI Window for Unitree G1 Control Application
Modern Windows interface using CustomTkinter
"""

import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import logging
import threading
import time
from typing import Optional

# Import application modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.robot.g1_controller import G1Controller, RobotState, MotionMode
from src.robot.video_feed import VideoFeedHandler
from src.slam.slam_visualizer import SLAMVisualizer
from src.utils.audio_manager import AudioManager


class UnitreeG1App(ctk.CTk):
    """Main application window for Unitree G1 control"""

    def __init__(self):
        """Initialize main application window"""
        super().__init__()

        # Window configuration
        self.title("Unitree G1 Control - Windows Edition")
        self.geometry("1400x900")

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.robot = G1Controller()
        self.video_feed = VideoFeedHandler()
        self.slam_viz = SLAMVisualizer()
        self.audio_mgr = AudioManager()

        # UI state
        self.video_label = None
        self.slam_label = None
        self.status_text = None
        self.telemetry_labels = {}

        # Update threads
        self.running = True
        self.update_thread = None

        # Setup UI
        self._create_ui()
        self._setup_callbacks()

        # Start components
        self._start_components()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_ui(self):
        """Create user interface"""
        # Create main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel - Controls
        self._create_control_panel()

        # Center panel - Video feeds
        self._create_video_panel()

        # Right panel - SLAM and status
        self._create_info_panel()

    def _create_control_panel(self):
        """Create left control panel"""
        control_frame = ctk.CTkFrame(self, corner_radius=10)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title
        title_label = ctk.CTkLabel(control_frame, text="Robot Control",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)

        # Connection controls
        conn_frame = ctk.CTkFrame(control_frame)
        conn_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(conn_frame, text="Connection",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.connect_btn = ctk.CTkButton(conn_frame, text="Connect",
                                        command=self._on_connect)
        self.connect_btn.pack(pady=5)

        self.disconnect_btn = ctk.CTkButton(conn_frame, text="Disconnect",
                                           command=self._on_disconnect,
                                           state="disabled")
        self.disconnect_btn.pack(pady=5)

        # Motion controls
        motion_frame = ctk.CTkFrame(control_frame)
        motion_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(motion_frame, text="Motion Control",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Basic motions
        btn_frame1 = ctk.CTkFrame(motion_frame)
        btn_frame1.pack(pady=5)

        ctk.CTkButton(btn_frame1, text="Stand Up", width=100,
                     command=self._on_stand_up).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame1, text="Sit Down", width=100,
                     command=self._on_sit_down).pack(side="left", padx=5)

        # Movement buttons
        btn_frame2 = ctk.CTkFrame(motion_frame)
        btn_frame2.pack(pady=5)

        ctk.CTkButton(btn_frame2, text="Walk", width=100,
                     command=self._on_walk).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame2, text="Run", width=100,
                     command=self._on_run).pack(side="left", padx=5)

        # Direction control
        direction_frame = ctk.CTkFrame(motion_frame)
        direction_frame.pack(pady=10)

        ctk.CTkLabel(direction_frame, text="Direction").pack()

        # Arrow buttons
        ctk.CTkButton(direction_frame, text="↑", width=60,
                     command=lambda: self._on_walk_direction(0.3, 0, 0)).pack()

        side_frame = ctk.CTkFrame(direction_frame)
        side_frame.pack()
        ctk.CTkButton(side_frame, text="←", width=60,
                     command=lambda: self._on_walk_direction(0, 0.3, 0)).pack(side="left", padx=5)
        ctk.CTkButton(side_frame, text="◯", width=60,
                     command=self._on_stop).pack(side="left", padx=5)
        ctk.CTkButton(side_frame, text="→", width=60,
                     command=lambda: self._on_walk_direction(0, -0.3, 0)).pack(side="left", padx=5)

        ctk.CTkButton(direction_frame, text="↓", width=60,
                     command=lambda: self._on_walk_direction(-0.3, 0, 0)).pack()

        # Stop button (prominent)
        ctk.CTkButton(motion_frame, text="STOP", width=200,
                     command=self._on_stop,
                     fg_color="red", hover_color="darkred").pack(pady=10)

        # Gesture controls
        gesture_frame = ctk.CTkFrame(control_frame)
        gesture_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(gesture_frame, text="Gestures",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        ctk.CTkButton(gesture_frame, text="Wave Hand",
                     command=self._on_wave).pack(pady=5)
        ctk.CTkButton(gesture_frame, text="Shake Hand",
                     command=self._on_shake_hand).pack(pady=5)

        # Voice control
        voice_frame = ctk.CTkFrame(control_frame)
        voice_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(voice_frame, text="Voice Control",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.voice_btn = ctk.CTkButton(voice_frame, text="Start Listening",
                                       command=self._toggle_voice)
        self.voice_btn.pack(pady=5)

    def _create_video_panel(self):
        """Create center video panel"""
        video_frame = ctk.CTkFrame(self, corner_radius=10)
        video_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Title
        title_label = ctk.CTkLabel(video_frame, text="Camera Feed",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)

        # Video display
        self.video_label = ctk.CTkLabel(video_frame, text="")
        self.video_label.pack(pady=10, expand=True, fill="both")

        # Video controls
        video_controls = ctk.CTkFrame(video_frame)
        video_controls.pack(pady=10)

        ctk.CTkButton(video_controls, text="Snapshot",
                     command=self._on_snapshot).pack(side="left", padx=5)
        ctk.CTkButton(video_controls, text="Toggle Camera",
                     command=self._on_toggle_camera).pack(side="left", padx=5)

    def _create_info_panel(self):
        """Create right info panel"""
        info_frame = ctk.CTkFrame(self, corner_radius=10)
        info_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Title
        title_label = ctk.CTkLabel(info_frame, text="SLAM & Status",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)

        # SLAM display
        slam_section = ctk.CTkFrame(info_frame)
        slam_section.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(slam_section, text="SLAM Map",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

        self.slam_label = ctk.CTkLabel(slam_section, text="")
        self.slam_label.pack(pady=5, expand=True, fill="both")

        # Status section
        status_section = ctk.CTkFrame(info_frame)
        status_section.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(status_section, text="Status",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

        self.status_text = ctk.CTkTextbox(status_section, height=100)
        self.status_text.pack(pady=5, fill="x")

        # Telemetry section
        telemetry_section = ctk.CTkFrame(info_frame)
        telemetry_section.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(telemetry_section, text="Telemetry",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

        # Telemetry labels
        self.telemetry_labels = {}
        for key in ["State", "Mode", "Position", "Battery"]:
            frame = ctk.CTkFrame(telemetry_section)
            frame.pack(fill="x", pady=2)

            ctk.CTkLabel(frame, text=f"{key}:", width=80,
                        anchor="w").pack(side="left", padx=5)
            label = ctk.CTkLabel(frame, text="--", anchor="w")
            label.pack(side="left", padx=5, fill="x", expand=True)
            self.telemetry_labels[key] = label

    def _setup_callbacks(self):
        """Setup callbacks for robot events"""
        # Register status callback
        self.robot.register_status_callback(self._on_robot_status)

        # Register voice command callback
        self.audio_mgr.register_command_callback(self._on_voice_command)

    def _start_components(self):
        """Start all components"""
        # Start audio manager
        self.audio_mgr.start()

        # Start video feed
        self.video_feed.start_stream()

        # Start SLAM visualizer
        self.slam_viz.start()

        # Start UI update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

        self._log_status("Application started")

    # Event handlers

    def _on_connect(self):
        """Handle connect button"""
        self._log_status("Connecting to robot...")
        success = self.robot.connect()

        if success:
            self.connect_btn.configure(state="disabled")
            self.disconnect_btn.configure(state="normal")
            self.audio_mgr.speak("Connected to robot")
        else:
            self._log_status("Connection failed")
            self.audio_mgr.speak("Connection failed")

    def _on_disconnect(self):
        """Handle disconnect button"""
        self.robot.disconnect()
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.audio_mgr.speak("Disconnected")

    def _on_stand_up(self):
        """Handle stand up button"""
        self.robot.stand_up()

    def _on_sit_down(self):
        """Handle sit down button"""
        self.robot.sit_down()

    def _on_walk(self):
        """Handle walk button"""
        self.robot.walk(0.3, 0, 0)

    def _on_run(self):
        """Handle run button"""
        self.robot.run(0.6, 0, 0)

    def _on_stop(self):
        """Handle stop button"""
        self.robot.stop()

    def _on_walk_direction(self, vx: float, vy: float, yaw: float):
        """Handle directional walking"""
        self.robot.walk(vx, vy, yaw)

    def _on_wave(self):
        """Handle wave gesture"""
        self.robot.wave_hand()
        self.audio_mgr.speak("Waving")

    def _on_shake_hand(self):
        """Handle shake hand gesture"""
        self.robot.shake_hand()
        self.audio_mgr.speak("Shaking hand")

    def _toggle_voice(self):
        """Toggle voice recognition"""
        if not self.audio_mgr.is_listening:
            if self.audio_mgr.start_listening():
                self.voice_btn.configure(text="Stop Listening",
                                        fg_color="red")
                self._log_status("Voice recognition started")
        else:
            self.audio_mgr.stop_listening()
            self.voice_btn.configure(text="Start Listening",
                                    fg_color=["#3B8ED0", "#1F6AA5"])
            self._log_status("Voice recognition stopped")

    def _on_snapshot(self):
        """Capture video snapshot"""
        filename = f"snapshot_{int(time.time())}.jpg"
        if self.video_feed.capture_snapshot(filename):
            self._log_status(f"Snapshot saved: {filename}")

    def _on_toggle_camera(self):
        """Toggle camera view"""
        self._log_status("Camera toggle not implemented")

    def _on_robot_status(self, message: str):
        """Handle robot status updates"""
        self._log_status(f"Robot: {message}")

    def _on_voice_command(self, command: str):
        """Handle voice commands"""
        self._log_status(f"Voice: {command}")

        # Parse and execute command
        motion_cmd = self.audio_mgr.parse_motion_command(command)

        if motion_cmd:
            action = motion_cmd["action"]

            if action == "stand":
                self.robot.stand_up()
            elif action == "sit":
                self.robot.sit_down()
            elif action == "walk":
                self.robot.walk(motion_cmd.get("vx", 0),
                              motion_cmd.get("vy", 0),
                              motion_cmd.get("yaw", 0))
            elif action == "run":
                self.robot.run(motion_cmd.get("vx", 0.6),
                             motion_cmd.get("vy", 0),
                             motion_cmd.get("yaw", 0))
            elif action == "stop":
                self.robot.stop()
            elif action == "wave":
                self.robot.wave_hand()
            elif action == "shake_hand":
                self.robot.shake_hand()

            self.audio_mgr.speak(f"Executing {action}")

    # Update loop

    def _update_loop(self):
        """Main update loop for video and SLAM"""
        while self.running:
            try:
                # Update video feed
                self._update_video()

                # Update SLAM display
                self._update_slam()

                # Update telemetry
                self._update_telemetry()

                time.sleep(0.033)  # ~30 FPS

            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                time.sleep(0.1)

    def _update_video(self):
        """Update video display"""
        frame = self.video_feed.get_current_frame()

        if frame is not None:
            # Resize frame to fit display
            display_width = 640
            display_height = 480
            frame_resized = cv2.resize(frame, (display_width, display_height))

            # Convert to PhotoImage
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=img)

            # Update label
            if self.video_label:
                self.video_label.configure(image=photo)
                self.video_label.image = photo  # Keep reference

    def _update_slam(self):
        """Update SLAM display"""
        slam_img = self.slam_viz.get_map_image(400, 300)

        if slam_img is not None:
            # Convert to PhotoImage
            slam_rgb = cv2.cvtColor(slam_img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(slam_rgb)
            photo = ImageTk.PhotoImage(image=img)

            # Update label
            if self.slam_label:
                self.slam_label.configure(image=photo)
                self.slam_label.image = photo  # Keep reference

    def _update_telemetry(self):
        """Update telemetry display"""
        telemetry = self.robot.get_telemetry()

        self.telemetry_labels["State"].configure(text=telemetry["state"])
        self.telemetry_labels["Mode"].configure(text=telemetry["motion_mode"])
        self.telemetry_labels["Position"].configure(text="0, 0, 0")
        self.telemetry_labels["Battery"].configure(text="--")

    def _log_status(self, message: str):
        """Add message to status log"""
        if self.status_text:
            self.status_text.insert("end", f"{message}\n")
            self.status_text.see("end")

    def _on_closing(self):
        """Handle window closing"""
        self.logger.info("Closing application...")

        # Stop components
        self.running = False
        self.robot.disconnect()
        self.video_feed.stop_stream()
        self.slam_viz.stop()
        self.audio_mgr.stop()

        # Wait for threads
        if self.update_thread:
            self.update_thread.join(timeout=2.0)

        self.destroy()


def main():
    """Main entry point"""
    app = UnitreeG1App()
    app.mainloop()


if __name__ == "__main__":
    main()
