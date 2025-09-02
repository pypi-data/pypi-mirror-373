from __future__ import annotations

import time

from loguru import logger


class FPSController:
    """Controls frame rate for synchronous processing.

    Maintains target FPS by calculating appropriate sleep times and adjusting
    for processing delays.

    Attributes:
        target_fps: Target frames per second
        frame_interval: Time interval between frames in seconds
        average_fps: Current average FPS
    """

    def __init__(
        self, target_fps: int, max_frame_count: int = 10, disabled: bool = False
    ) -> None:
        """Initialize FPS controller.

        Args:
            target_fps: Target frames per second
            max_frame_count: Number of frames to keep for FPS calculation
            disabled: If True, the FPS controller will be disabled.
        """
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.max_frame_count = max_frame_count
        self.disabled = disabled

        # Timing control
        self.next_frame_time = None
        self.display_ts = []
        self.average_fps = 0

    def wait_next_frame(self, *, sleep: bool = True) -> float:
        """Wait until it's time for the next frame.

        Adjusts sleep time based on actual FPS to maintain target rate.
        """
        current_time = time.time()

        # Initialize next_frame_time if needed
        if self.next_frame_time is None:
            self.next_frame_time = current_time
            self.display_ts = []

        # Calculate sleep time to maintain target FPS
        sleep_time = self.next_frame_time - current_time

        if sleep_time > 0 and not self.disabled:
            # Adjust sleep time based on actual FPS
            if len(self.display_ts) >= 2:
                self.average_fps = (len(self.display_ts) - 1) / (
                    self.display_ts[-1] - self.display_ts[0]
                )
                scale = min(1.1, max(0.9, self.average_fps / self.target_fps))
                sleep_time *= scale
            if sleep:
                time.sleep(sleep_time)
            return sleep_time
        else:
            # Check if significantly behind schedule
            if -sleep_time > self.frame_interval * 8:
                logger.warning(
                    f"Frame processing was behind schedule for "
                    f"{-sleep_time * 1000:.2f} ms"
                )
                self.next_frame_time = time.time()
        return sleep_time

    def update(self) -> None:
        """Update timing information after processing a frame."""
        current_time = time.time()

        # Update timing information
        self.display_ts.append(current_time)
        if len(self.display_ts) > self.max_frame_count:
            self.display_ts = self.display_ts[-self.max_frame_count :]

        # Calculate next frame time
        self.next_frame_time += self.frame_interval

    @property
    def fps(self) -> float:
        """Get current average FPS."""
        return self.average_fps
