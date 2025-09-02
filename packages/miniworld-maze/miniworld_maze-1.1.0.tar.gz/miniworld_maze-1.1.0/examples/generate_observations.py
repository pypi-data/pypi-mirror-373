#!/usr/bin/env python3
"""
Generate comprehensive observations for Nine Rooms environment variants.
Supports: NineRooms, SpiralNineRooms, TwentyFiveRooms
"""

import argparse
import os

import numpy as np
from PIL import Image

from miniworld_maze.core.miniworld_gymnasium.rendering.framebuffer import (
    FrameBuffer,
)
from miniworld_maze.environments.factory import NineRoomsEnvironmentWrapper


def generate_observations(variant, output_dir=None, high_res_full_views=False):
    """Generate comprehensive observations for the specified environment variant."""
    if output_dir is None:
        output_dir = f"{variant.lower()}_observations"

    os.makedirs(output_dir, exist_ok=True)

    # Create environment
    env = NineRoomsEnvironmentWrapper(variant=variant, size=64)

    # Get base environment for direct render access
    base_env = env.env if hasattr(env, "env") else env
    while hasattr(base_env, "env") or hasattr(base_env, "_env"):
        if hasattr(base_env, "env"):
            base_env = base_env.env
        elif hasattr(base_env, "_env"):
            base_env = base_env._env
        else:
            break

    # Reset environment
    obs, _ = env.reset(seed=42)

    # Create high-resolution frame buffer if requested
    high_res_fb = None
    if high_res_full_views:
        high_res_fb = FrameBuffer(512, 512, 8)

    # === FULL ENVIRONMENT OBSERVATIONS ===
    # 1. Full view with agent at starting position
    if high_res_full_views:
        full_view_start = base_env.render_top_view(
            frame_buffer=high_res_fb, POMDP=False
        )
    else:
        full_view_start = base_env.render_top_view(POMDP=False)
    Image.fromarray(full_view_start).save(f"{output_dir}/full_view_start.png")

    # 2. Full view without agent (clean maze view)
    if high_res_full_views:
        full_view_clean = base_env.render_top_view(
            frame_buffer=high_res_fb, POMDP=False, render_ag=False
        )
    else:
        full_view_clean = base_env.render_top_view(POMDP=False, render_ag=False)
    Image.fromarray(full_view_clean).save(f"{output_dir}/full_view_clean.png")

    # 3. Full view with agent in center
    center_x = (base_env.min_x + base_env.max_x) / 2
    center_z = (base_env.min_z + base_env.max_z) / 2
    base_env.place_agent(pos=[center_x, 0.0, center_z])
    if high_res_full_views:
        full_view_center = base_env.render_top_view(
            frame_buffer=high_res_fb, POMDP=False
        )
    else:
        full_view_center = base_env.render_top_view(POMDP=False)
    Image.fromarray(full_view_center).save(f"{output_dir}/full_view_center.png")

    # === PARTIAL OBSERVATIONS ===

    # Reset agent to start position
    base_env.place_agent(pos=[2.5, 0.0, 2.5])

    # 1. Partial view from starting position
    partial_start = base_env.render_top_view(POMDP=True)
    Image.fromarray(partial_start).save(f"{output_dir}/partial_start.png")

    # 2. Partial view from center
    base_env.place_agent(pos=[center_x, 0.0, center_z])
    partial_center = base_env.render_top_view(POMDP=True)
    Image.fromarray(partial_center).save(f"{output_dir}/partial_center.png")

    # 3. Partial view from corner/edge
    corner_x = base_env.max_x - 2.5
    corner_z = base_env.max_z - 2.5
    base_env.place_agent(pos=[corner_x, 0.0, corner_z])
    partial_corner = base_env.render_top_view(POMDP=True)
    Image.fromarray(partial_corner).save(f"{output_dir}/partial_corner.png")

    # 4. Partial view at strategic location
    if variant == "NineRooms":
        strategic_x, strategic_z = 15.0, 7.5  # Room boundary
    elif variant == "SpiralNineRooms":
        strategic_x, strategic_z = 22.5, 15.0  # Center of spiral
    else:  # TwentyFiveRooms
        strategic_x, strategic_z = 37.5, 37.5  # Mid-outer area

    base_env.place_agent(pos=[strategic_x, 0.0, strategic_z])
    partial_strategic = base_env.render_top_view(POMDP=True)
    Image.fromarray(partial_strategic).save(f"{output_dir}/partial_strategic.png")

    # === WRAPPED OBSERVATIONS ===

    # Reset environment
    obs, _ = env.reset(seed=42)
    obs = obs["observation"]

    # 1. Standard gymnasium observation
    obs_hwc = obs
    Image.fromarray(obs_hwc).save(f"{output_dir}/gymnasium_standard.png")

    # 2. Observations after movement
    actions = [2, 2, 1]  # move_forward, move_forward, turn_right
    action_names = ["move_forward", "move_forward", "turn_right"]

    for i, action in enumerate(actions):
        obs, _, _, _, _ = env.step(action)
        obs = obs["observation"]
        obs_hwc = obs
        Image.fromarray(obs_hwc).save(
            f"{output_dir}/gymnasium_step_{i + 1}_{action_names[i]}.png"
        )

    # === RENDER_ON_POS EXAMPLES ===

    # Define test positions based on variant
    if variant == "NineRooms":
        test_positions = [
            ([7.5, 0.0, 7.5], "top_middle_room"),  # top-middle room center
            ([37.5, 0.0, 37.5], "bottom_right_room"),  # bottom-right room center
            ([22.5, 0.0, 22.5], "environment_center"),  # environment center
            ([7.5, 0.0, 22.5], "middle_left_room"),  # middle-left room center
        ]
    elif variant == "SpiralNineRooms":
        test_positions = [
            ([7.5, 0.0, 7.5], "spiral_start"),  # top-left room (spiral start)
            ([37.5, 0.0, 37.5], "spiral_end"),  # bottom-right room (spiral end)
            ([22.5, 0.0, 7.5], "top_right_room"),  # top-right room
            ([7.5, 0.0, 37.5], "bottom_left_room"),  # bottom-left room
        ]
    else:  # TwentyFiveRooms
        test_positions = [
            ([37.5, 0.0, 37.5], "near_corner"),  # room (1,1) - near corner
            ([112.5, 0.0, 112.5], "far_corner"),  # room (4,4) - far corner
            ([75.0, 0.0, 75.0], "center_room"),  # center room (2,2)
            ([37.5, 0.0, 112.5], "opposite_corner"),  # room (1,4) - opposite corner
        ]

    for i, (pos, pos_name) in enumerate(test_positions):
        # First-person view from agent's perspective
        render_obs = env.render_on_pos(pos)

        # Convert CHW to HWC for PIL
        if len(render_obs.shape) == 3 and render_obs.shape[0] == 3:
            render_obs = np.transpose(render_obs, (1, 2, 0))

        Image.fromarray(render_obs).save(
            f"{output_dir}/render_on_pos_{i + 1}_{pos_name}_firstperson.png"
        )

        # Also generate top-down view for comparison
        # Store original position and move agent
        original_pos = base_env.agent.pos.copy()
        base_env.place_agent(pos=pos)

        # Get top-down POMDP view
        topdown_obs = base_env.render_top_view(POMDP=True, render_ag=False)
        Image.fromarray(topdown_obs).save(
            f"{output_dir}/render_on_pos_{i + 1}_{pos_name}_topdown.png"
        )

        # Restore original position
        base_env.place_agent(pos=original_pos)

    env.close()
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate observations for Nine Rooms environment variants"
    )
    parser.add_argument(
        "variant",
        choices=["NineRooms", "SpiralNineRooms", "TwentyFiveRooms"],
        help="Environment variant to use",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for images (default: {variant}_observations)",
    )
    parser.add_argument(
        "--high-res-full",
        action="store_true",
        help="Generate 512x512 high-resolution full environment views",
    )

    args = parser.parse_args()

    output_dir = generate_observations(
        args.variant, args.output_dir, args.high_res_full
    )

    return output_dir


if __name__ == "__main__":
    main()
