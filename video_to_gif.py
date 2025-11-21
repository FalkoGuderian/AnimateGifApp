#!/usr/bin/env python3
"""
Video to GIF Converter for Web Application

Modifies the CLI video_to_gif function for web use with progress tracking.
"""

import time
from pathlib import Path

from moviepy import VideoFileClip


def convert_video_to_gif_web(input_path, output_path, fps=10, scale=0.5,
                           start_time=0.0, duration=None, loops=0, speed=1.0, progress_callback=None):
    """
    Convert video to GIF with web-friendly progress tracking.

    Args:
        input_path (str): Path to input video file
        output_path (str): Path for output GIF file
        fps (int): Frames per second
        scale (float): Scale factor (1.0 = original size)
        start_time (float): Start time in seconds
        duration (float or None): Duration in seconds, None for full video
        loops (int): Number of loops (0 = unlimited)
        progress_callback (callable): Function to call with progress percentage (0-100)

    Returns:
        bool: True if successful, False otherwise
    """

    # Wrap progress_callback to handle None
    def safe_progress(percent):
        if progress_callback:
            try:
                progress_callback(percent)
            except Exception:
                pass  # Ignore progress callback errors

    safe_progress(5)  # Loading video

    try:
        clip = VideoFileClip(input_path)
    except Exception as e:
        safe_progress(-1)  # Error signal
        return False

    safe_progress(20)  # Video loaded

    # Apply start time and duration
    if start_time > 0:
        if duration is not None:
            if start_time + duration > clip.duration:
                duration = clip.duration - start_time
            clip = clip.subclipped(start_time, start_time + duration)
        else:
            clip = clip.subclipped(start_time)
    elif duration is not None:
        if duration > clip.duration:
            duration = clip.duration
        clip = clip.subclipped(0, duration)

    safe_progress(40)  # Time adjustments applied

    # Apply speed effect
    if speed != 1.0:
        if speed > 0:  # Prevent division by zero or negative speeds
            clip = clip.with_speed_scaled(speed)
        else:
            print(f"Warning: Invalid speed value {speed}, using 1.0")
            speed = 1.0

    safe_progress(50)  # Speed effect applied

    # Apply scale
    if scale != 1.0:
        new_size = (int(clip.w * scale), int(clip.h * scale))
        clip = clip.resized(new_size)

    safe_progress(70)  # Scaling applied

    # Set frame rate
    clip = clip.with_fps(fps)

    safe_progress(80)  # FPS set

    try:
        # Write GIF - this is where actual conversion happens
        clip.write_gif(output_path, fps=fps, loop=loops, logger=None)

        # Verify output file was created
        if Path(output_path).exists():
            safe_progress(100)
            return True
        else:
            safe_progress(-1)
            return False

    except Exception:
        safe_progress(-1)
        return False
    finally:
        clip.close()
