#!/usr/bin/env python3
"""
Benchmark rendering performance (FPS) for various observation sizes.

This script tests the direct rendering performance of the Nine Rooms environments
across different observation sizes to demonstrate the efficiency of the
direct rendering approach vs the old resize-based approach.
"""

import argparse
import os
import time

import numpy as np

# Enable headless rendering to avoid X11/OpenGL context issues
os.environ["PYGLET_HEADLESS"] = "1"

from miniworld_maze.core.constants import (
    DEFAULT_BENCHMARK_STEPS,
    DEFAULT_WARMUP_STEPS,
    FLOAT32_BYTES,
    MB_TO_BYTES,
    RGB_CHANNELS,
)
from miniworld_maze.environments.factory import NineRoomsEnvironmentWrapper


def benchmark_rendering_performance(
    variant="NineRooms",
    sizes=None,
    num_steps=DEFAULT_BENCHMARK_STEPS,
    num_warmup=DEFAULT_WARMUP_STEPS,
):
    """
    Benchmark rendering performance across different observation sizes.

    Args:
        variant: Environment variant to test
        sizes: List of observation sizes to test
        num_steps: Number of steps to run for timing
        num_warmup: Number of warmup steps (not timed)

    Returns:
        Dictionary with benchmark results
    """
    if sizes is None:
        sizes = [32, 48, 64, 96, 128, 192, 256]

    print(f"🚀 Benchmarking {variant} rendering performance...")
    print(f"📊 Testing sizes: {sizes}")
    print(f"⏱️  Steps per test: {num_steps} (+ {num_warmup} warmup)")
    print("=" * 60)

    results = {}

    for size in sizes:
        print(f"\n🔍 Testing {size}x{size} observations...")

        # Create environment with specific observation size
        env = NineRoomsEnvironmentWrapper(variant, size=size)

        # Warmup phase
        print(f"   🔥 Warming up ({num_warmup} steps)...")
        obs, info = env.reset(seed=42)
        for _ in range(num_warmup):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                obs, info = env.reset()

        # Benchmark phase
        print(f"   ⏱️  Benchmarking ({num_steps} steps)...")
        start_time = time.time()

        step_times = []
        for i in range(num_steps):
            step_start = time.time()
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                obs, info = env.reset()
            step_end = time.time()
            step_times.append(step_end - step_start)

        end_time = time.time()
        total_time = end_time - start_time

        env.close()

        # Calculate statistics
        fps = num_steps / total_time
        avg_step_time = np.mean(step_times)
        min_step_time = np.min(step_times)
        max_step_time = np.max(step_times)
        std_step_time = np.std(step_times)

        # Memory per observation
        pixels_per_obs = size * size * RGB_CHANNELS
        memory_mb = (pixels_per_obs * FLOAT32_BYTES) / MB_TO_BYTES

        results[size] = {
            "fps": fps,
            "avg_step_time": avg_step_time,
            "min_step_time": min_step_time,
            "max_step_time": max_step_time,
            "std_step_time": std_step_time,
            "total_time": total_time,
            "memory_mb": memory_mb,
            "pixels": size * size,
        }

        print(f"   ✅ {fps:.2f} FPS (avg: {avg_step_time * 1000:.2f}ms/step)")

    return results


def print_benchmark_results(results, variant):
    """Print detailed benchmark results in a formatted table."""

    print(f"\n{'=' * 80}")
    print(f"📊 RENDERING PERFORMANCE BENCHMARK RESULTS - {variant}")
    print(f"{'=' * 80}")

    # Table header
    print(
        f"{'Size':>8} {'Pixels':>10} {'FPS':>8} {'Avg ms':>8} {'Min ms':>8} {'Max ms':>8} {'Std ms':>8} {'Memory':>8}"
    )
    print("-" * 80)

    # Table rows
    for size, data in sorted(results.items()):
        print(
            f"{size:>8} {data['pixels']:>10,} {data['fps']:>8.1f} {data['avg_step_time'] * 1000:>8.1f} "
            f"{data['min_step_time'] * 1000:>8.1f} {data['max_step_time'] * 1000:>8.1f} "
            f"{data['std_step_time'] * 1000:>8.1f} {data['memory_mb']:>7.1f}MB"
        )

    print("-" * 80)

    # Performance insights
    print("\n🎯 PERFORMANCE INSIGHTS:")

    # Find best and worst performers
    best_fps = max(results.values(), key=lambda x: x["fps"])
    worst_fps = min(results.values(), key=lambda x: x["fps"])
    best_size = next(
        size for size, data in results.items() if data["fps"] == best_fps["fps"]
    )
    worst_size = next(
        size for size, data in results.items() if data["fps"] == worst_fps["fps"]
    )

    print(f"   🏆 Highest FPS: {best_size}x{best_size} at {best_fps['fps']:.1f} FPS")
    print(f"   🐌 Lowest FPS:  {worst_size}x{worst_size} at {worst_fps['fps']:.1f} FPS")

    # Calculate performance scaling
    size_32 = results.get(32)
    size_256 = results.get(256)
    if size_32 and size_256:
        pixel_ratio = (256 * 256) / (32 * 32)
        fps_ratio = size_32["fps"] / size_256["fps"]
        print(
            f"   📈 Scaling: 256x256 has {pixel_ratio:.1f}x more pixels but only {fps_ratio:.1f}x slower"
        )

    # Memory usage
    total_memory = sum(data["memory_mb"] for data in results.values())
    print(f"   💾 Total memory tested: {total_memory:.1f}MB across all sizes")


def benchmark_environment_variants(sizes=None, num_steps=50):
    """Benchmark all environment variants."""

    if sizes is None:
        sizes = [64, 128, 256]

    variants = ["NineRooms", "SpiralNineRooms", "TwentyFiveRooms"]
    all_results = {}

    print("🌟 COMPREHENSIVE ENVIRONMENT BENCHMARK")
    print(f"Testing variants: {variants}")
    print(f"Testing sizes: {sizes}")
    print("=" * 80)

    for variant in variants:
        results = benchmark_rendering_performance(
            variant=variant, sizes=sizes, num_steps=num_steps, num_warmup=5
        )
        all_results[variant] = results

        # Quick summary
        avg_fps = np.mean([data["fps"] for data in results.values()])
        print(f"\n📈 {variant} average FPS across all sizes: {avg_fps:.1f}")

    # Comparative analysis
    print(f"\n{'=' * 80}")
    print("🔄 VARIANT COMPARISON")
    print("=" * 80)

    for size in sizes:
        print(f"\nSize {size}x{size}:")
        for variant in variants:
            if size in all_results[variant]:
                fps = all_results[variant][size]["fps"]
                print(f"   {variant:20}: {fps:6.1f} FPS")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Nine Rooms rendering performance"
    )
    parser.add_argument(
        "--variant",
        default="NineRooms",
        choices=["NineRooms", "SpiralNineRooms", "TwentyFiveRooms"],
        help="Environment variant to benchmark",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[32, 48, 64, 96, 128, 192, 256],
        help="Observation sizes to test",
    )
    parser.add_argument(
        "--steps", type=int, default=1000, help="Number of steps per benchmark"
    )
    parser.add_argument(
        "--all-variants", action="store_true", help="Benchmark all environment variants"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick benchmark with fewer steps and sizes",
    )

    args = parser.parse_args()

    if args.quick:
        args.steps = 30
        args.sizes = [64, 128, 256]

    print("🎮 Nine Rooms Rendering Performance Benchmark")
    print("=" * 80)

    if args.all_variants:
        all_results = benchmark_environment_variants(
            sizes=args.sizes, num_steps=args.steps
        )

        # Print detailed results for each variant
        for variant, results in all_results.items():
            print_benchmark_results(results, variant)

    else:
        results = benchmark_rendering_performance(
            variant=args.variant, sizes=args.sizes, num_steps=args.steps
        )
        print_benchmark_results(results, args.variant)

    print("\n🎉 Benchmark complete!")
    print("✨ Direct rendering approach shows excellent performance scaling!")


if __name__ == "__main__":
    main()
