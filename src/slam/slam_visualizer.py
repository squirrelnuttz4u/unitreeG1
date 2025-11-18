"""
SLAM Visualization for Unitree G1
Displays point clouds and occupancy grids from LiDAR data
"""

import numpy as np
import logging
import threading
import time
from typing import Optional, List, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg


class SLAMVisualizer:
    """Visualizes SLAM data from G1 LiDAR"""

    def __init__(self):
        """Initialize SLAM visualizer"""
        self.logger = logging.getLogger(__name__)

        # SLAM data
        self.point_cloud = None
        self.occupancy_grid = None
        self.robot_pose = (0, 0, 0)  # x, y, theta

        # Visualization
        self.fig = None
        self.map_image = None
        self.lock = threading.Lock()

        # Map settings
        self.map_size = 100  # meters
        self.resolution = 0.1  # meters per cell
        self.grid_size = int(self.map_size / self.resolution)

        # Initialize occupancy grid
        self.occupancy_grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)

        # Simulation data
        self.simulation_mode = True
        self.sim_update_thread = None
        self.is_running = False

    def start(self):
        """Start SLAM visualization"""
        self.logger.info("Starting SLAM visualizer")
        self.is_running = True

        if self.simulation_mode:
            self.sim_update_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.sim_update_thread.start()

    def stop(self):
        """Stop SLAM visualization"""
        self.logger.info("Stopping SLAM visualizer")
        self.is_running = False

        if self.sim_update_thread:
            self.sim_update_thread.join(timeout=2.0)

    def update_point_cloud(self, points: np.ndarray):
        """
        Update point cloud data

        Args:
            points: Nx3 array of 3D points
        """
        with self.lock:
            self.point_cloud = points
            self._update_occupancy_grid(points)

    def update_robot_pose(self, x: float, y: float, theta: float):
        """
        Update robot pose

        Args:
            x: X position (meters)
            y: Y position (meters)
            theta: Heading angle (radians)
        """
        with self.lock:
            self.robot_pose = (x, y, theta)

    def _update_occupancy_grid(self, points: np.ndarray):
        """
        Update occupancy grid from point cloud

        Args:
            points: Nx3 array of 3D points
        """
        if points is None or len(points) == 0:
            return

        # Convert 3D points to 2D grid coordinates
        center = self.grid_size // 2

        for point in points:
            x, y = point[0], point[1]

            # Convert to grid coordinates
            grid_x = int(center + x / self.resolution)
            grid_y = int(center + y / self.resolution)

            # Check bounds
            if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                self.occupancy_grid[grid_y, grid_x] = min(
                    self.occupancy_grid[grid_y, grid_x] + 0.1, 1.0
                )

    def get_map_image(self, width: int = 800, height: int = 600) -> Optional[np.ndarray]:
        """
        Generate map visualization image

        Args:
            width: Image width
            height: Image height

        Returns:
            Optional[np.ndarray]: Map image in BGR format
        """
        try:
            with self.lock:
                # Create figure
                fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
                ax = fig.add_subplot(111)

                # Plot occupancy grid
                ax.imshow(self.occupancy_grid, cmap='gray_r', origin='lower',
                         extent=[-self.map_size / 2, self.map_size / 2,
                                -self.map_size / 2, self.map_size / 2])

                # Plot robot position
                x, y, theta = self.robot_pose
                ax.plot(x, y, 'ro', markersize=10, label='Robot')

                # Plot robot heading
                arrow_length = 2.0
                dx = arrow_length * np.cos(theta)
                dy = arrow_length * np.sin(theta)
                ax.arrow(x, y, dx, dy, head_width=0.5, head_length=0.5,
                        fc='red', ec='red')

                # Plot point cloud if available
                if self.point_cloud is not None and len(self.point_cloud) > 0:
                    pc_x = self.point_cloud[:, 0]
                    pc_y = self.point_cloud[:, 1]
                    ax.scatter(pc_x, pc_y, c='blue', s=1, alpha=0.3, label='Point Cloud')

                ax.set_xlabel('X (m)')
                ax.set_ylabel('Y (m)')
                ax.set_title('SLAM Map Visualization')
                ax.grid(True, alpha=0.3)
                ax.legend()
                ax.set_aspect('equal')

                # Convert to image
                canvas = FigureCanvasAgg(fig)
                canvas.draw()
                buf = canvas.buffer_rgba()
                image = np.asarray(buf)

                # Convert RGBA to BGR
                image = image[:, :, [2, 1, 0]]

                plt.close(fig)

                return image

        except Exception as e:
            self.logger.error(f"Error generating map image: {e}")
            return None

    def _simulation_loop(self):
        """Simulation loop for testing"""
        angle = 0
        radius = 5

        while self.is_running:
            try:
                # Simulate robot movement in a circle
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                theta = angle + np.pi / 2

                self.update_robot_pose(x, y, theta)

                # Generate simulated point cloud (walls of a room)
                num_points = 500
                points = []

                # Add walls
                for i in range(num_points):
                    wall_angle = (i / num_points) * 2 * np.pi
                    wall_dist = 10 + np.random.randn() * 0.5
                    px = x + wall_dist * np.cos(wall_angle)
                    py = y + wall_dist * np.sin(wall_angle)
                    pz = 0
                    points.append([px, py, pz])

                # Add some obstacles
                for i in range(50):
                    obstacle_angle = np.random.rand() * 2 * np.pi
                    obstacle_dist = 3 + np.random.rand() * 4
                    px = x + obstacle_dist * np.cos(obstacle_angle)
                    py = y + obstacle_dist * np.sin(obstacle_angle)
                    pz = 0
                    points.append([px, py, pz])

                self.update_point_cloud(np.array(points))

                angle += 0.05
                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in simulation loop: {e}")
                time.sleep(0.5)

    def clear_map(self):
        """Clear the occupancy grid"""
        with self.lock:
            self.occupancy_grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
            self.point_cloud = None
            self.robot_pose = (0, 0, 0)

    def get_statistics(self) -> dict:
        """
        Get SLAM statistics

        Returns:
            dict: Statistics dictionary
        """
        with self.lock:
            return {
                "num_points": len(self.point_cloud) if self.point_cloud is not None else 0,
                "robot_x": self.robot_pose[0],
                "robot_y": self.robot_pose[1],
                "robot_theta": self.robot_pose[2],
                "map_coverage": np.sum(self.occupancy_grid > 0.5) * self.resolution ** 2
            }
