from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

import cv2
import numpy as np

try:
    from livekit import rtc
    from livekit.agents import utils
    from livekit.agents.voice import AgentSession, io
    from livekit.agents.voice.avatar import (
        AudioReceiver,
        AudioSegmentEnd,
        AvatarOptions,
    )
    from livekit.agents.voice.chat_cli import ChatCLI
except ImportError:
    raise ImportError(
        "livekit-agents is required, please install it with `pip install livekit-agents[openai,silero,deepgram,cartesia]~=1.0rc`"
    )
from loguru import logger

from bithuman import AsyncBithuman, AudioChunk, VideoFrame
from bithuman.utils import FPSController


class AudioOutput(ABC):
    @abstractmethod
    async def capture_frame(self, audio_chunk: AudioChunk) -> None:
        pass

    @abstractmethod
    def clear_buffer(self) -> None:
        pass


class VideoOutput(ABC):
    @abstractmethod
    async def capture_frame(
        self, frame: VideoFrame, fps: float, exp_time: float
    ) -> None:
        pass

    @abstractmethod
    def buffer_empty(self) -> bool:
        pass


class LocalAudioIO(ChatCLI, AudioOutput):
    """Chat interface that redirects audio output to a custom destination."""

    def __init__(
        self,
        session: AgentSession,
        agent_audio_output: io.AudioOutput,
        *,
        buffer_size: int = 0,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(agent_session=session, loop=loop)
        self._redirected_audio_output = agent_audio_output
        self._input_buffer = utils.aio.Chan[rtc.AudioFrame](maxsize=buffer_size)
        self._forward_audio_atask: Optional[asyncio.Task] = None

        self._sample_rate = self._audio_sink.sample_rate
        self._resampler: Optional[rtc.AudioResampler] = None

    async def start(self) -> None:
        await super().start()
        self._forward_audio_atask = asyncio.create_task(self._forward_audio())

    async def capture_frame(self, audio_chunk: AudioChunk) -> None:
        audio_frame = rtc.AudioFrame(
            data=audio_chunk.bytes,
            sample_rate=audio_chunk.sample_rate,
            num_channels=1,
            samples_per_channel=len(audio_chunk.array),
        )

        if not self._resampler and self._sample_rate != audio_chunk.sample_rate:
            self._resampler = rtc.AudioResampler(
                input_rate=audio_chunk.sample_rate,
                output_rate=self._sample_rate,
                num_channels=1,
            )

        if self._resampler:
            for f in self._resampler.push(audio_frame):
                await self._input_buffer.send(f)
        else:
            await self._input_buffer.send(audio_frame)

    def clear_buffer(self) -> None:
        while not self._input_buffer.empty():
            self._input_buffer.recv_nowait()
        with self._audio_sink.lock:
            self._audio_sink.audio_buffer.clear()

    @utils.log_exceptions(logger=logger)
    async def _forward_audio(self) -> None:
        async for frame in self._input_buffer:
            await self._audio_sink.capture_frame(frame)

    def _update_speaker(self, *, enable: bool) -> None:
        super()._update_speaker(enable=enable)

        # redirect the agent's audio output
        if enable:
            self._session.output.audio = self._redirected_audio_output
        else:
            self._session.output.audio = None

    async def aclose(self) -> None:
        if not self._done_fut.done():
            self._done_fut.set_result(None)
        if self._main_atask:
            await utils.aio.cancel_and_wait(self._main_atask)

        self._input_buffer.close()
        if self._forward_audio_atask:
            await utils.aio.cancel_and_wait(self._forward_audio_atask)


class LocalVideoPlayer(VideoOutput):
    """Video display for rendering avatar frames with debug information."""

    def __init__(
        self,
        window_size: tuple[int, int],
        window_name: str = "BitHuman Avatar",
        buffer_size: int = 0,
    ) -> None:
        self.window_name: str = window_name
        self.start_time: Optional[float] = None
        self._input_buffer = utils.aio.Chan[tuple[VideoFrame, float, float]](
            maxsize=buffer_size
        )
        self._display_atask: Optional[asyncio.Task] = None

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, window_size[0], window_size[1])

        self.start_time = asyncio.get_event_loop().time()
        self._display_atask = asyncio.create_task(self._display_frame())

    async def aclose(self) -> None:
        cv2.destroyAllWindows()
        if self._display_atask:
            await utils.aio.cancel_and_wait(self._display_atask)

    async def capture_frame(
        self, frame: VideoFrame, fps: float = 0.0, exp_time: float = 0.0
    ) -> None:
        if not frame.has_image:
            return
        await self._input_buffer.send((frame, fps, exp_time))

    def buffer_empty(self) -> bool:
        return self._input_buffer.empty()

    @utils.log_exceptions(logger=logger)
    async def _display_frame(self) -> None:
        async for frame, fps, exp_time in self._input_buffer:
            image = await self.render_image(frame, fps, exp_time)
            cv2.imshow(self.window_name, image)
            cv2.waitKey(1)

    async def render_image(
        self, frame: VideoFrame, fps: float = 0.0, exp_time: float = 0.0
    ) -> np.ndarray:
        image = frame.bgr_image.copy()

        # Add overlay information
        self._add_debug_info(image, fps, exp_time)

        return image

    def _add_debug_info(self, image: np.ndarray, fps: float, exp_time: float) -> None:
        # Add FPS information
        cv2.putText(
            image,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # Add elapsed time
        current_time = asyncio.get_event_loop().time()
        if self.start_time is not None:
            elapsed = current_time - self.start_time
            cv2.putText(
                image,
                f"Time: {elapsed:.1f}s",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        # Add expiration time if available
        if exp_time > 0:
            exp_in_seconds = exp_time - time.time()
            cv2.putText(
                image,
                f"Exp in: {exp_in_seconds:.1f}s",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )


class LocalAvatarRunner:
    """Controls and synchronizes avatar audio and video playback."""

    def __init__(
        self,
        *,
        bithuman_runtime: AsyncBithuman,
        audio_input: AudioReceiver,
        audio_output: AudioOutput,
        video_output: VideoOutput,
        options: AvatarOptions,
        runtime_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._bithuman_runtime = bithuman_runtime
        self._runtime_kwargs = runtime_kwargs or {}
        self._options = options

        self._audio_recv = audio_input
        self._audio_output = audio_output
        self._video_output = video_output
        self._stop_event = asyncio.Event()

        # State management
        self._playback_position: float = 0.0
        self._audio_playing: bool = False
        self._tasks: set[asyncio.Task] = set()
        self._read_audio_atask: Optional[asyncio.Task] = None
        self._publish_video_atask: Optional[asyncio.Task] = None

        # FPS control
        self._fps_controller = FPSController(target_fps=options.video_fps)

    async def start(self) -> None:
        await self._audio_recv.start()

        # Setup event handler
        self._audio_recv.on("clear_buffer", self._create_clear_buffer_task)

        # Start processing tasks
        self._read_audio_atask = asyncio.create_task(self._read_audio())
        self._publish_video_atask = asyncio.create_task(self._publish_video())

    def _create_clear_buffer_task(self) -> None:
        """Create a task to handle clear buffer events."""
        task = asyncio.create_task(self._handle_clear_buffer())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    @utils.log_exceptions(logger=logger)
    async def _read_audio(self) -> None:
        """Process incoming audio frames."""
        async for frame in self._audio_recv:
            if self._stop_event.is_set():
                break

            if not self._audio_playing and isinstance(frame, rtc.AudioFrame):
                self._audio_playing = True
            if isinstance(frame, AudioSegmentEnd):
                await self._bithuman_runtime.flush()
                continue
            await self._bithuman_runtime.push_audio(
                bytes(frame.data), frame.sample_rate, last_chunk=False
            )

    @utils.log_exceptions(logger=logger)
    async def _publish_video(self) -> None:
        """Process and display video frames."""
        async for frame in self._bithuman_runtime.run(
            out_buffer_empty=self._video_output.buffer_empty,
            **self._runtime_kwargs,
        ):
            # Control frame rate
            sleep_time = self._fps_controller.wait_next_frame(sleep=False)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

            # Send video frame
            if frame.has_image:
                await self._video_output.capture_frame(
                    frame,
                    fps=self._fps_controller.average_fps,
                    exp_time=self._bithuman_runtime.get_expiration_time(),
                )

            # Send audio chunk
            audio_chunk = frame.audio_chunk
            if audio_chunk is not None:
                await self._audio_output.capture_frame(audio_chunk)
                self._playback_position += audio_chunk.duration

            # Handle end of speech
            if frame.end_of_speech:
                await self._handle_end_of_speech()

            self._fps_controller.update()

    async def _handle_end_of_speech(self) -> None:
        """Handle end of speech event."""
        if self._audio_playing:
            notify_task = self._audio_recv.notify_playback_finished(
                playback_position=self._playback_position,
                interrupted=False,
            )
            if asyncio.iscoroutine(notify_task):
                await notify_task

            self._playback_position = 0.0
        self._audio_playing = False

    async def _handle_clear_buffer(self) -> None:
        """Handle clearing the buffer and notify about interrupted playback."""
        tasks = []
        self._bithuman_runtime.interrupt()
        self._audio_output.clear_buffer()

        # Handle interrupted playback
        if self._audio_playing:
            notify_task = self._audio_recv.notify_playback_finished(
                playback_position=self._playback_position,
                interrupted=True,
            )
            if asyncio.iscoroutine(notify_task):
                tasks.append(notify_task)
            self._playback_position = 0.0
            self._audio_playing = False

        await asyncio.gather(*tasks)

    async def aclose(self) -> None:
        """Close the avatar controller and clean up resources."""
        if self._read_audio_atask:
            await utils.aio.cancel_and_wait(self._read_audio_atask)
        if self._publish_video_atask:
            await utils.aio.cancel_and_wait(self._publish_video_atask)
        await utils.aio.cancel_and_wait(*self._tasks)

    def stop(self) -> None:
        self._stop_event.set()
