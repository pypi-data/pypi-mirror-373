#!/usr/bin/env python3
"""
OpenCV-based dual-view live keyboard control for Nine Rooms environments.
Shows ego view and top-down map side by side with agent position tracking.
Avoids OpenGL conflicts by using OpenCV for display instead of pygame.

Controls:
    W/A/S/D - Move forward/turn left/move backward/turn right
    SPACE   - Pick up object
    X       - Drop object
    E       - Toggle/activate object
    R       - Reset environment
    ESC/Q   - Quit
    1/2/3   - Switch between environment variants

Features:
    - Dual synchronized views: ego view (configurable) + top-down map
    - Real-time agent position tracking on the map
    - Both environments stay perfectly synchronized
    - No OpenGL conflicts with environment rendering
"""

import argparse
import math
import time
from typing import Optional

import cv2
import numpy as np

from miniworld_maze import NineRoomsEnvironmentWrapper, ObservationLevel

OPENCV_AVAILABLE = True


class OpenCVLiveController:
    """Live environment controller using OpenCV for display."""

    def __init__(
        self,
        variant: str = "NineRooms",
        size: int = 256,
        obs_level: ObservationLevel = ObservationLevel.TOP_DOWN_PARTIAL,
    ):
        """
        Initialize the OpenCV live controller.

        Args:
            variant: Environment variant to start with
            size: Observation image size
            obs_level: Observation level (FIRST_PERSON, TOP_DOWN_PARTIAL, TOP_DOWN_FULL)
        """
        self.size = size
        self.current_variant = variant
        self.obs_level = obs_level
        self.env = None  # Main environment (ego view)
        self.map_env = None  # Separate environment for top-down map
        self.current_obs = None
        self.current_map_obs = None
        self.current_goal = None
        self.current_info = None
        self.running = True

        # Available variants
        self.variants = ["NineRooms", "SpiralNineRooms", "TwentyFiveRooms"]
        self.variant_index = (
            self.variants.index(variant) if variant in self.variants else 0
        )

        # Action mapping for keyboard
        self.action_map = {
            ord("w"): 2,  # move_forward
            ord("s"): 3,  # move_back
            ord("a"): 0,  # turn_left
            ord("d"): 1,  # turn_right
            ord(" "): 4,  # pickup (space)
            ord("x"): 5,  # drop
            ord("e"): 6,  # toggle
        }

        # Stats
        self.step_count = 0
        self.episode_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0

        # Display settings
        self.display_width = 1800  # Wider to accommodate four views
        self.display_height = 600
        self.info_height = 100  # Reduced height for info text
        self.view_size = 400  # Size of each view panel

    def create_environment(self, variant: str) -> bool:
        """
        Create or recreate the environment.

        Args:
            variant: Environment variant to create

        Returns:
            True if successful, False otherwise
        """
        # Close existing environments
        if self.env:
            self.env.close()
        if self.map_env:
            self.map_env.close()

        print(f"🔄 Creating {variant} environments...")

        # Create main environment (ego view)
        self.env = NineRoomsEnvironmentWrapper(
            variant=variant,
            size=self.size,
            obs_level=self.obs_level,
            agent_mode="triangle",  # Make agent visible for better demo
            info_obs=[ObservationLevel.FIRST_PERSON],
        )

        # Create separate environment for top-down map
        self.map_env = NineRoomsEnvironmentWrapper(
            variant=variant,
            size=self.size,
            obs_level=ObservationLevel.TOP_DOWN_FULL,
            # Always use full top-down for map
            agent_mode="triangle",  # Make agent visible in map view
            info_obs=[ObservationLevel.FIRST_PERSON],
        )

        # Synchronize both environments to same initial state
        obs, info = self.env.reset(seed=42)
        map_obs, map_info = self.map_env.reset(seed=42)

        # Store info for accessing additional observations
        self.current_info = info

        # Extract observation array from dict
        self.current_obs = obs["observation"]
        self.current_goal = obs["desired_goal"]
        self.current_map_obs = map_obs["observation"]

        self.current_variant = variant
        self.step_count = 0
        self.episode_count += 1

        print(f"✅ {variant} environments ready!")
        print(f"   Ego view shape: {self.current_obs.shape}")
        print(f"   Map view shape: {self.current_map_obs.shape}")
        print(f"   Action space: {self.env.action_space}")

        return True

    def get_ego_view_display(self) -> Optional[np.ndarray]:
        """
        Get current ego observation formatted for OpenCV display.

        Returns:
            BGR image array for OpenCV or None if failed
        """
        if self.current_obs is not None:
            # Already in HWC format
            obs_hwc = self.current_obs

            # Convert RGB to BGR for OpenCV
            obs_bgr = cv2.cvtColor(obs_hwc, cv2.COLOR_RGB2BGR)

            # Resize for display
            obs_resized = cv2.resize(obs_bgr, (self.view_size, self.view_size))

            return obs_resized
        else:
            return self._create_placeholder("No Ego View")

    def get_goal_view_display(self) -> Optional[np.ndarray]:
        """
        Get current goal observation formatted for OpenCV display.

        Returns:
            BGR image array for OpenCV or None if failed
        """
        if self.current_goal is not None:
            # Already in HWC format
            obs_hwc = self.current_goal

            # Convert RGB to BGR for OpenCV
            obs_bgr = cv2.cvtColor(obs_hwc, cv2.COLOR_RGB2BGR)

            # Resize for display
            obs_resized = cv2.resize(obs_bgr, (self.view_size, self.view_size))

            return obs_resized
        else:
            return self._create_placeholder("No Goal View")

    def get_first_person_view_display(self) -> Optional[np.ndarray]:
        """
        Get current first person observation from info formatted for OpenCV display.

        Returns:
            BGR image array for OpenCV or None if failed
        """
        if self.current_info is not None and "FIRST_PERSON" in self.current_info:
            # Get first person observation from info
            obs_hwc = self.current_info["FIRST_PERSON"]

            # Convert RGB to BGR for OpenCV
            obs_bgr = cv2.cvtColor(obs_hwc, cv2.COLOR_RGB2BGR)

            # Resize for display
            obs_resized = cv2.resize(obs_bgr, (self.view_size, self.view_size))

            return obs_resized
        else:
            return self._create_placeholder("No First Person View")

    def get_map_view_display(self) -> Optional[np.ndarray]:
        """
        Get current map observation with agent rendered by the engine.

        Returns:
            BGR image array for OpenCV or None if failed
        """
        if self.map_env is not None:
            # Get base environment to access the new get_observation method
            base_env = self.map_env
            while hasattr(base_env, "env") or hasattr(base_env, "_env"):
                if hasattr(base_env, "env"):
                    base_env = base_env.env
                elif hasattr(base_env, "_env"):
                    base_env = base_env._env
                else:
                    break

            # Use the new get_observation method with agent rendering enabled
            if hasattr(base_env, "get_observation"):
                map_obs_with_agent = base_env.get_observation(render_agent=True)

                if map_obs_with_agent is not None:
                    # get_observation returns HWC format, so use directly
                    obs_hwc = map_obs_with_agent

                    # Convert RGB to BGR for OpenCV
                    obs_bgr = cv2.cvtColor(obs_hwc, cv2.COLOR_RGB2BGR)

                    # Resize for display
                    obs_resized = cv2.resize(obs_bgr, (self.view_size, self.view_size))

                    return obs_resized
                else:
                    return self._create_placeholder("No Map View")
            else:
                # Fallback to current observation with manual overlay (HWC format)
                if self.current_map_obs is not None:
                    obs_hwc = self.current_map_obs  # Already in HWC format
                    obs_bgr = cv2.cvtColor(obs_hwc, cv2.COLOR_RGB2BGR)
                    obs_resized = cv2.resize(obs_bgr, (self.view_size, self.view_size))
                    return self._add_agent_marker(obs_resized)
                else:
                    return self._create_placeholder("No Map View")
        else:
            return self._create_placeholder("No Map View")

    def _add_agent_marker(self, map_image: np.ndarray) -> np.ndarray:
        """
        Add agent position and orientation marker to the map view.

        Args:
            map_image: The top-down map image

        Returns:
            Map image with agent marker
        """
        # Get access to the base environment to read agent position
        base_env = self.map_env
        while hasattr(base_env, "env") or hasattr(base_env, "_env"):
            if hasattr(base_env, "env"):
                base_env = base_env.env
            elif hasattr(base_env, "_env"):
                base_env = base_env._env
            else:
                break

        # Get agent position and orientation
        if hasattr(base_env, "agent") and base_env.agent is not None:
            agent_pos = base_env.agent.pos
            agent_dir = base_env.agent.dir

            # Convert world coordinates to pixel coordinates
            # Environment bounds
            env_min_x = base_env.min_x
            env_max_x = base_env.max_x
            env_min_z = base_env.min_z
            env_max_z = base_env.max_z

            # Convert agent position to pixel coordinates
            pixel_x = int(
                (agent_pos[0] - env_min_x) / (env_max_x - env_min_x) * self.view_size
            )
            pixel_z = int(
                (agent_pos[2] - env_min_z) / (env_max_z - env_min_z) * self.view_size
            )

            # Clamp to image bounds
            pixel_x = max(0, min(self.view_size - 1, pixel_x))
            pixel_z = max(0, min(self.view_size - 1, pixel_z))

            # Create a copy to avoid modifying the original
            marked_image = map_image.copy()

            # Draw agent position as a circle
            agent_radius = max(5, self.view_size // 80)  # Scale with image size
            cv2.circle(
                marked_image, (pixel_x, pixel_z), agent_radius, (0, 255, 255), -1
            )  # Yellow filled circle
            cv2.circle(
                marked_image, (pixel_x, pixel_z), agent_radius + 2, (0, 0, 0), 2
            )  # Black outline

            # Draw direction indicator (small arrow/line)
            if agent_dir is not None:
                # Calculate direction vector
                dir_length = agent_radius + 8
                end_x = int(pixel_x + dir_length * math.cos(agent_dir))
                end_z = int(pixel_z + dir_length * math.sin(agent_dir))

                # Draw direction line
                cv2.line(
                    marked_image, (pixel_x, pixel_z), (end_x, end_z), (0, 255, 0), 3
                )  # Green direction line

                # Draw small arrowhead
                arrow_size = 5
                arrow_angle = 0.5  # radians

                # Calculate arrowhead points
                left_x = int(end_x - arrow_size * math.cos(agent_dir - arrow_angle))
                left_z = int(end_z - arrow_size * math.sin(agent_dir - arrow_angle))
                right_x = int(end_x - arrow_size * math.cos(agent_dir + arrow_angle))
                right_z = int(end_z - arrow_size * math.sin(agent_dir + arrow_angle))

                # Draw arrowhead
                cv2.line(marked_image, (end_x, end_z), (left_x, left_z), (0, 255, 0), 2)
                cv2.line(
                    marked_image, (end_x, end_z), (right_x, right_z), (0, 255, 0), 2
                )

            return marked_image
        else:
            return map_image

    def _create_placeholder(self, text: str) -> np.ndarray:
        """Create a placeholder image with text."""
        placeholder = np.zeros((self.view_size, self.view_size, 3), dtype=np.uint8)
        placeholder[::20, :] = [100, 100, 100]  # Grid pattern
        placeholder[:, ::20] = [100, 100, 100]

        # Add text
        cv2.putText(
            placeholder,
            text,
            (self.view_size // 4, self.view_size // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return placeholder

    def create_quad_view_display(
        self,
        first_person_img: np.ndarray,
        ego_img: np.ndarray,
        map_img: np.ndarray,
        goal_img: np.ndarray,
    ) -> np.ndarray:
        """
        Create quad-view display with first person view, ego view,
        top-down map, and goal view.

        Args:
            first_person_img: First person view image
            ego_img: Ego view image
            map_img: Top-down map image
            goal_img: Goal view image

        Returns:
            Combined image with four views and info panel
        """
        # Create main canvas
        combined_img = np.zeros(
            (self.display_height, self.display_width, 3), dtype=np.uint8
        )

        # View positions
        first_person_x = 50
        first_person_y = 50
        ego_x = first_person_x + self.view_size + 50
        ego_y = 50
        map_x = ego_x + self.view_size + 50
        map_y = 50
        goal_x = map_x + self.view_size + 50
        goal_y = 50

        # Place first person view
        combined_img[
            first_person_y : first_person_y + self.view_size,
            first_person_x : first_person_x + self.view_size,
        ] = first_person_img

        # Place ego view
        combined_img[ego_y : ego_y + self.view_size, ego_x : ego_x + self.view_size] = (
            ego_img
        )

        # Place map view
        combined_img[map_y : map_y + self.view_size, map_x : map_x + self.view_size] = (
            map_img
        )

        # Place goal view
        combined_img[
            goal_y : goal_y + self.view_size, goal_x : goal_x + self.view_size
        ] = goal_img

        # Add labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255)
        thickness = 2

        # First person view label
        cv2.putText(
            combined_img,
            "First Person View",
            (first_person_x, first_person_y - 10),
            font,
            font_scale,
            color,
            thickness,
        )

        # Ego view label
        obs_level_name = (
            self.obs_level.name
            if hasattr(self.obs_level, "name")
            else str(self.obs_level)
        )
        cv2.putText(
            combined_img,
            f"Ego View ({obs_level_name})",
            (ego_x, ego_y - 10),
            font,
            font_scale,
            color,
            thickness,
        )

        # Map view label
        cv2.putText(
            combined_img,
            "Map View (TOP_DOWN_FULL)",
            (map_x, map_y - 10),
            font,
            font_scale,
            color,
            thickness,
        )

        # Goal view label
        cv2.putText(
            combined_img,
            "Goal View",
            (goal_x, goal_y - 10),
            font,
            font_scale,
            color,
            thickness,
        )

        # Add agent rendering info to legend
        legend_x = goal_x + self.view_size - 150
        legend_y = goal_y + 20
        legend_font_scale = 0.4

        # Legend text - agent is now rendered by the engine
        cv2.putText(
            combined_img,
            "Agent Rendered by Engine",
            (legend_x, legend_y),
            font,
            legend_font_scale,
            (200, 200, 200),
            1,
        )

        # Create info panel at bottom
        info_y = self.view_size + 70

        # Environment and stats info
        font_scale = 0.6
        cv2.putText(
            combined_img,
            f"Environment: {self.current_variant}",
            (10, info_y),
            font,
            font_scale,
            color,
            1,
        )
        cv2.putText(
            combined_img,
            f"Episode: {self.episode_count} | Step: {self.step_count} | "
            f"FPS: {self.current_fps}",
            (10, info_y + 25),
            font,
            font_scale,
            color,
            1,
        )

        # Controls info
        font_scale_small = 0.5
        controls_y = info_y + 55
        controls = [
            "CONTROLS: W/A/S/D=Move/Turn, SPACE=Pickup, X=Drop, E=Toggle, "
            "R=Reset, 1/2/3=Switch Env, ESC/Q=Quit"
        ]

        for i, control in enumerate(controls):
            cv2.putText(
                combined_img,
                control,
                (10, controls_y + i * 20),
                font,
                font_scale_small,
                (200, 200, 200),
                1,
            )

        return combined_img

    def handle_input(self, key: int) -> bool:
        """
        Handle keyboard input.

        Args:
            key: OpenCV key code

        Returns:
            True to continue, False to quit
        """
        if key == 27 or key == ord("q"):  # ESC or Q
            return False

        elif key == ord("r"):
            # Reset both environments
            if self.env and self.map_env:
                # Use same seed to keep environments synchronized
                seed = np.random.randint(0, 1000000)
                obs, info = self.env.reset(seed=seed)
                map_obs, map_info = self.map_env.reset(seed=seed)

                # Store info for accessing additional observations
                self.current_info = info

                # Extract observation array from dict
                self.current_obs = obs["observation"]
                self.current_goal = obs["desired_goal"]
                self.current_map_obs = map_obs["observation"]
                self.step_count = 0
                self.episode_count += 1
                print(f"🔄 Both environments reset (Episode {self.episode_count})")

        elif key in [ord("1"), ord("2"), ord("3")]:
            # Switch environment variant
            variant_map = {ord("1"): 0, ord("2"): 1, ord("3"): 2}
            new_index = variant_map[key]
            if new_index < len(self.variants):
                new_variant = self.variants[new_index]
                print(f"🔄 Switching to {new_variant}...")
                if self.create_environment(new_variant):
                    self.variant_index = new_index

        elif self.env and self.map_env and key in self.action_map:
            # Execute action on both environments to keep them synchronized
            action = self.action_map[key]
            # Step both environments with the same action
            obs, reward, terminated, truncated, info = self.env.step(action)
            map_obs, map_reward, map_terminated, map_truncated, map_info = (
                self.map_env.step(action)
            )

            # Store info for accessing additional observations
            self.current_info = info

            # Extract observation array from dict
            self.current_obs = obs["observation"]
            self.current_goal = obs["desired_goal"]
            self.current_map_obs = map_obs["observation"]
            self.step_count += 1

            # Print action feedback
            action_names = [
                "turn_left",
                "turn_right",
                "move_forward",
                "move_back",
                "pickup",
                "drop",
                "toggle",
            ]
            if action < len(action_names):
                print(
                    f"🎯 {action_names[action]} | Reward: {reward:.2f} | "
                    f"Step: {self.step_count}"
                )

            if terminated or truncated:
                print(f"🏁 Episode ended! Reward: {reward:.2f}")
                # Reset both environments with same seed
                seed = np.random.randint(0, 1000000)
                obs, info = self.env.reset(seed=seed)
                map_obs, map_info = self.map_env.reset(seed=seed)
                # Store info for accessing additional observations
                self.current_info = info
                # Extract observation array from dict
                self.current_obs = obs["observation"]
                self.current_goal = obs["desired_goal"]
                self.current_map_obs = map_obs["observation"]
                self.step_count = 0
                self.episode_count += 1

        return True

    def update_fps(self):
        """Update FPS counter."""
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time

    def run(self):
        """Main run loop."""
        print("🎮 Nine Rooms OpenCV Live Controller")
        print("=" * 50)

        print("🔄 Step 1: Creating dual environments...")
        # Create initial environment
        if not self.create_environment(self.current_variant):
            print("❌ Failed to create initial environment")
            return

        print("✅ Step 1 completed: Dual environments created")

        print("\n📖 Controls:")
        print("   W/A/S/D - Move forward/turn left/move backward/turn right")
        print("   SPACE - Pick up object")
        print("   X - Drop object")
        print("   E - Toggle/activate object")
        print("   R - Reset environment")
        print("   1/2/3 - Switch between environment variants")
        print("   ESC/Q - Quit")
        print("\n👀 OpenCV window will open - click on it to focus for keyboard input!")
        print("🔍 If window doesn't appear, try running with: DISPLAY=:0 python ...")

        # Create window
        window_name = "Nine Rooms Live Control (OpenCV)"
        print(f"📺 Creating OpenCV window: {window_name}")
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        print("✅ Window created successfully")

        while self.running:
            # Get all views
            ego_img = self.get_ego_view_display()
            map_img = self.get_map_view_display()
            goal_img = self.get_goal_view_display()

            if ego_img is not None and map_img is not None and goal_img is not None:
                # Get first person view
                first_person_img = self.get_first_person_view_display()

                if first_person_img is not None:
                    # Create combined quad-view display
                    display_img = self.create_quad_view_display(
                        first_person_img, ego_img, map_img, goal_img
                    )
                else:
                    # Fallback to placeholder if first person view fails
                    display_img = self._create_placeholder("Display Error")

                # Show image
                cv2.imshow(window_name, display_img)

            # Handle input (1ms timeout for responsiveness)
            key = cv2.waitKey(1) & 0xFF
            if key != 255:  # Key was pressed
                if not self.handle_input(key):
                    break

            # Update FPS
            self.update_fps()

        if self.env:
            self.env.close()
        if self.map_env:
            self.map_env.close()
        cv2.destroyAllWindows()
        print("\n👋 OpenCV dual-view live controller stopped")


def main():
    """Main function."""
    if not OPENCV_AVAILABLE:
        return

    parser = argparse.ArgumentParser(
        description="OpenCV live control for Nine Rooms environments"
    )
    parser.add_argument(
        "--variant",
        choices=["NineRooms", "SpiralNineRooms", "TwentyFiveRooms"],
        default="NineRooms",
        help="Environment variant to start with",
    )
    parser.add_argument(
        "--size", type=int, default=128, help="Observation image size (default: 128)"
    )
    parser.add_argument(
        "--obs-level",
        choices=["FIRST_PERSON", "TOP_DOWN_PARTIAL", "TOP_DOWN_FULL"],
        default="TOP_DOWN_PARTIAL",
        help="Observation level (default: TOP_DOWN_PARTIAL)",
    )

    args = parser.parse_args()

    # Convert string to enum
    obs_level_map = {
        "FIRST_PERSON": ObservationLevel.TOP_DOWN_PARTIAL,
        "TOP_DOWN_PARTIAL": ObservationLevel.TOP_DOWN_PARTIAL,
        "TOP_DOWN_FULL": ObservationLevel.TOP_DOWN_FULL,
    }
    obs_level = obs_level_map[args.obs_level]

    controller = OpenCVLiveController(
        variant=args.variant, size=args.size, obs_level=obs_level
    )
    controller.run()


if __name__ == "__main__":
    main()
