"""ZMQ client for bithuman runtime service."""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from collections import deque
from typing import Any, Awaitable, Callable, Dict, Optional

import cv2
import msgpack
import numpy as np
import zmq
import zmq.asyncio
from loguru import logger

from bithuman.api import AudioChunk, VideoControl
from bithuman.audio import AudioStreamBatcher, float32_to_int16, load_audio
from bithuman.service.messages import (
    AudioRequest,
    CheckInitStatusRequest,
    FrameMessage,
    GetSettingRequest,
    HeartbeatRequest,
    InitRequest,
    InterruptRequest,
    ResponseStatus,
    ServerResponse,
)
from bithuman.video_graph.video_script import VideoScript


class FPSMonitor:
    """Monitor FPS with a sliding window.

    Tracks frame timestamps and calculates current FPS based on
    a moving window of recent frames.
    """

    def __init__(self, window_size: int = 30) -> None:
        """Initialize FPS monitor."""
        self.timestamps: deque = deque(maxlen=window_size)
        self.last_fps_update: float = time.time()
        self.current_fps: float = 0
        logger.debug(f"Initialized FPSMonitor with window_size={window_size}")

    def update(self) -> None:
        """Add new frame timestamp and update FPS if needed."""
        self.timestamps.append(time.time())

        if time.time() - self.last_fps_update > 0.5:
            self._calculate_fps()
            self.last_fps_update = time.time()

    def _calculate_fps(self) -> None:
        """Calculate current FPS from timestamp differences."""
        if len(self.timestamps) < 2:
            self.current_fps = 0
            return

        time_diff = self.timestamps[-1] - self.timestamps[0]
        if time_diff > 0:
            self.current_fps = (len(self.timestamps) - 1) / time_diff

    @property
    def fps(self) -> float:
        """Get current FPS value."""
        return self.current_fps


class ZMQBithumanRuntimeClient:
    """Async client for Bithuman Runtime using ZMQ.

    Handles communication with server including:
    - Workspace initialization
    - Audio streaming
    - Frame receiving
    - Heartbeat monitoring
    """

    def __init__(
        self,
        client_id: str,
        host: str = "127.0.0.1",
        control_port: int = 5555,
        stream_port: int = 5556,
        request_timeout: float = 5,
        max_consecutive_errors: int = 3,
    ) -> None:
        """Initialize client.

        Args:
            client_id: Unique client identifier
            host: Host address
            control_port: Port for control messages
            stream_port: Port for frame streaming
            request_timeout: Timeout for requests in seconds
            max_consecutive_errors: Number of consecutive errors before disconnection
        """
        logger.info(
            f"Initializing BithumanRuntimeClient {client_id} connecting to ports "
            f"{control_port} (control) and {stream_port} (stream)"
        )
        self.client_id = client_id
        self.context = zmq.asyncio.Context()
        self.request_timeout = request_timeout
        self.max_consecutive_errors = max_consecutive_errors

        # Control socket (REQ/REP)
        self.control_socket = self.context.socket(zmq.REQ)
        # Set timeouts (in milliseconds)
        if request_timeout and request_timeout > 0:
            self.control_socket.setsockopt(zmq.RCVTIMEO, int(request_timeout * 1000))
            self.control_socket.setsockopt(zmq.SNDTIMEO, int(request_timeout * 1000))
            logger.debug(f"Set request timeouts to {request_timeout}s")
        self.control_socket.connect(f"tcp://{host}:{control_port}")
        logger.debug(f"Connected control socket to tcp://{host}:{control_port}")

        # Subscribe socket for frames
        self.stream_socket = self.context.socket(zmq.SUB)
        self.stream_socket.connect(f"tcp://{host}:{stream_port}")
        self.stream_socket.setsockopt_string(zmq.SUBSCRIBE, client_id)
        logger.debug(f"Connected stream socket to tcp://{host}:{stream_port}")

        # Frame callback and FPS monitoring
        self.frame_callback: Optional[
            Callable[[FrameMessage, Dict[str, Any]], Awaitable[None] | None]
        ] = None
        self.fps_monitor = FPSMonitor()
        self.running = True
        self.is_initialized = False

        # Add stream batcher
        self.stream_batcher = AudioStreamBatcher(fps=25, output_sample_rate=16000)

        # Tasks
        self._frame_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.init_frame: Optional[np.ndarray] = None
        self.first_frame_received = False

        # Add socket state tracking
        self._socket_lock = asyncio.Lock()
        self._is_closed = False

        # Add connection state callbacks
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_connection_error: Optional[Callable[[str], None]] = None

        # Add video script
        self._video_script: Optional[VideoScript] = None

    def set_connection_callbacks(
        self,
        on_disconnected: Optional[Callable[[], None]] = None,
        on_connection_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Set callbacks for connection state changes."""
        self.on_disconnected = on_disconnected
        self.on_connection_error = on_connection_error

    async def _handle_connection_error(self, error_msg: str) -> None:
        """Handle connection errors."""
        logger.error(f"Connection error: {error_msg}")
        if self.on_connection_error:
            self.on_connection_error(error_msg)

    async def _handle_disconnection(self) -> None:
        """Handle server disconnection."""
        logger.warning("Server disconnected")
        if self.on_disconnected:
            self.on_disconnected()

    async def start(self) -> None:
        """Start client tasks."""
        logger.info("Starting client tasks")
        self._frame_task = asyncio.create_task(self._receive_frames())

    async def wait_for_init_frame(self, timeout: Optional[float] = None) -> None:
        """Wait for workspace initialization."""
        logger.info("Waiting for initialization frame")
        start_time = time.time()
        while self.init_frame is None:
            if timeout and time.time() - start_time > timeout:
                logger.error("Timed out waiting for initialization frame")
                raise TimeoutError("Timed out waiting for initialization")
            await asyncio.sleep(0.1)
        logger.debug("Initialization frame received")

    async def wait_for_first_frame(self, timeout: Optional[float] = None) -> None:
        """Wait for first frame."""
        logger.info("Waiting for first frame")
        start_time = time.time()
        while not self.first_frame_received:
            if timeout and time.time() - start_time > timeout:
                logger.error("Timed out waiting for first frame")
                raise TimeoutError("Timed out waiting for first frame")
            await asyncio.sleep(0.1)
        logger.debug("First frame received")

    async def _send_and_receive(
        self, request_data: bytes, client_id: str = None
    ) -> ServerResponse:
        """Send request and receive response with error handling and locking."""
        client_id = client_id or self.client_id
        logger.debug(f"Sending request to server (client_id={client_id})")
        if self._is_closed:
            error_msg = "Client is closed"
            logger.error(f"{error_msg} (client_id={client_id})")
            await self._handle_connection_error(error_msg)
            return ServerResponse(status=ResponseStatus.ERROR, message=error_msg)

        try:
            async with self._socket_lock:
                try:
                    await self.control_socket.send(request_data)
                    response_data = await self.control_socket.recv()
                except zmq.Again:
                    error_msg = "Request timed out"
                    logger.error(f"{error_msg} (client_id={client_id})")
                    await self._handle_connection_error(error_msg)
                    return ServerResponse(
                        status=ResponseStatus.ERROR, message=error_msg
                    )

            return ServerResponse.from_dict(msgpack.unpackb(response_data, raw=False))

        except zmq.ZMQError as e:
            error_msg = f"ZMQ error while sending request: {str(e)}"
            logger.error(f"{error_msg} (client_id={client_id})")
            await self._handle_connection_error(error_msg)
            return ServerResponse(status=ResponseStatus.ERROR, message=error_msg)
        except Exception as e:
            error_msg = f"Failed to send request: {str(e)}"
            logger.exception(f"{error_msg} (client_id={client_id})")
            await self._handle_connection_error(error_msg)
            return ServerResponse(status=ResponseStatus.ERROR, message=error_msg)

    async def init_workspace(
        self,
        avatar_model_path: str,
        video_file: Optional[str] = None,
        inference_data_file: Optional[str] = None,
        check_interval: float = 1.0,
        max_retries: Optional[int] = None,
    ) -> ServerResponse:
        """Initialize avatar model with async status checking.

        Args:
            avatar_model_path: Avatar model path
            video_file: Optional video file path
            inference_data_file: Optional inference data file path
            check_interval: Interval between status checks in seconds
            max_retries: Maximum number of status checks before giving up

        Returns:
            Final initialization response
        """
        logger.info(
            f"Initializing avatar model from '{avatar_model_path}' "
            f"with video_file='{video_file}' and "
            f"inference_data_file='{inference_data_file}'"
        )
        # Send initial request
        request = InitRequest(
            client_id=self.client_id,
            avatar_model_path=avatar_model_path,
            video_file=video_file,
            inference_data_file=inference_data_file,
        )
        response = await self._send_and_receive(
            msgpack.packb(request.to_dict(), use_bin_type=True)
        )
        logger.debug(f"Initial avatar model init response: {response}")

        if response.status == ResponseStatus.ERROR:
            return response

        # Start heartbeat immediately after sending init request
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._send_heartbeat())
            logger.info("Heartbeat task started")

        # Keep checking status until complete or error
        retries = 0
        while max_retries is None or retries < max_retries:
            if response.status == ResponseStatus.SUCCESS:
                self.is_initialized = True
                logger.info("Avatar model initialized successfully")
                return response
            elif response.status == ResponseStatus.ERROR:
                logger.error(f"Initialization failed: {response}")
                return response

            await asyncio.sleep(check_interval)
            logger.debug("Checking initialization status")

            status_request = CheckInitStatusRequest(client_id=self.client_id)
            response = await self._send_and_receive(
                msgpack.packb(status_request.to_dict(), use_bin_type=True)
            )
            logger.debug(f"Avatar model init status response: {response}")

            retries += 1

        # If we timeout, don't stop the heartbeat - let the client handle cleanup
        logger.error("Initialization timed out")
        return ServerResponse(
            status=ResponseStatus.ERROR,
            message="Initialization timed out",
        )

    async def get_setting(self, name: str) -> Any:
        """Get a setting from server."""
        logger.debug(f"Getting setting '{name}' from server")
        request = GetSettingRequest(client_id=self.client_id, name=name)
        response = await self._send_and_receive(
            msgpack.packb(request.to_dict(), use_bin_type=True)
        )
        if response.status != ResponseStatus.SUCCESS:
            logger.error(f"Failed to get setting '{name}': {response}")
            raise RuntimeError(f"Failed to get setting {name}: {response}")
        logger.debug(f"Received setting '{name}': {response.extra['value']}")
        return response.extra["value"]

    async def get_video_script(self) -> VideoScript:
        """Get the video script from server."""
        if self._video_script is None:
            data = await self.get_setting("video_script")
            self._video_script = VideoScript.from_dict(data)
        return self._video_script

    async def send_video_control(
        self, target_video: str | None, actions: list[str] | str | None = None
    ) -> ServerResponse:
        """Send video control commands to server."""
        logger.info(f"Sending video control to server: '{target_video=}', '{actions=}'")
        request = AudioRequest(
            client_id=self.client_id,
            data=VideoControl(target_video=target_video, action=actions),
        )
        return await self._send_audio(request)

    async def send_answer_finished_sentinel(self) -> ServerResponse:
        """Send answer finished sentinel to server to enable latter action triggers."""
        logger.debug("Sending answer finished sentinel to server")
        request = AudioRequest(
            client_id=self.client_id,
            data=VideoControl(end_of_speech=True),
        )
        return await self._send_audio(request)

    async def send_audio(
        self,
        audio_bytes: bytes,
        sample_rate: int,
        is_last: bool = False,
        **kwargs: dict[str, Any],
    ) -> str | None:
        """Stream audio data in chunks.

        Returns:
            Message ID for the streamed audio
        """
        logger.trace(
            f"Streaming audio data: sample_rate={sample_rate}, "
            f"duration={len(audio_bytes) / 2 / sample_rate:.2f}s, is_last={is_last}"
        )

        control = VideoControl(
            audio=AudioChunk.from_bytes(audio_bytes, sample_rate, last_chunk=is_last),
            **kwargs,
        )
        request = AudioRequest(client_id=self.client_id, data=control)
        response = await self._send_audio(request)

        if response.status != ResponseStatus.SUCCESS:
            logger.error(f"Failed to send audio chunk: {response}")
            return None

        return control.message_id

    async def interrupt(self) -> ServerResponse:
        """Interrupt current audio processing."""
        logger.info("Interrupting current audio processing")
        self.reset_audio_stream()

        request = InterruptRequest(client_id=self.client_id)
        return await self._send_and_receive(
            msgpack.packb(request.to_dict(), use_bin_type=True)
        )

    def set_frame_callback(
        self, callback: Callable[[FrameMessage, Dict[str, Any]], Awaitable[None] | None]
    ) -> None:
        """Set callback for received frames. Can be sync or async function."""
        self.frame_callback = callback

    async def _send_audio(self, request: AudioRequest) -> ServerResponse:
        """Send audio data to server."""
        return await self._send_and_receive(
            msgpack.packb(request.to_dict(), use_bin_type=True)
        )

    async def _receive_frames(self) -> None:
        """Receive and process frames."""
        logger.info(f"Starting frame receiver task (client_id={self.client_id})")

        while self.running:
            try:
                parts = await self.stream_socket.recv_multipart()
                if len(parts) < 2:
                    logger.warning(
                        f"Received incomplete message "
                        f"(client_id={self.client_id}, parts_count={len(parts)})"
                    )
                    continue

                _, msg = parts

                try:
                    frame_dict = msgpack.unpackb(msg, raw=False)

                    # Keep one client_id check for security
                    if frame_dict["client_id"] != self.client_id:
                        logger.warning(
                            f"Received message for wrong client "
                            f"(client_id={self.client_id}, "
                            f"received_client_id={frame_dict['client_id']})"
                        )
                        continue

                    frame_msg = FrameMessage(**frame_dict)

                except Exception as e:
                    logger.error(
                        f"Error processing message "
                        f"(client_id={self.client_id}, error={str(e)})"
                    )
                    continue

                if frame_msg.source_message_id == "_init_frame":
                    logger.info(
                        f"Received init frame (client_id={self.client_id}, "
                        f"shape={frame_msg.image.shape})"
                    )
                    self.init_frame = frame_msg.image
                else:
                    self.first_frame_received = True
                    self.fps_monitor.update()

                if self.frame_callback and self.first_frame_received:
                    result = self.frame_callback(
                        frame_msg, {"fps": self.fps_monitor.fps}
                    )
                    if result is not None and isinstance(result, Awaitable):
                        await result

            except asyncio.CancelledError:
                logger.info("Frame receiver task cancelled")
                break
            except Exception as e:
                logger.exception(
                    f"Error receiving frame "
                    f"(client_id={self.client_id}, error={str(e)})"
                )
                await asyncio.sleep(0.001)

    async def _send_heartbeat(self) -> None:
        """Send periodic heartbeat to server."""
        logger.info("Heartbeat task started")
        consecutive_errors = 0
        while self.running:
            try:
                if self._is_closed:
                    logger.debug("Client is closed, stopping heartbeat")
                    break

                request = HeartbeatRequest(client_id=self.client_id)
                logger.debug("Sending heartbeat to server")
                response = await self._send_and_receive(
                    msgpack.packb(request.to_dict(), use_bin_type=True)
                )
                logger.debug(f"Heartbeat response: {response}")

                if response.status != ResponseStatus.SUCCESS:
                    consecutive_errors += 1
                    logger.warning(f"Heartbeat failed: {response}")

                    # If we get multiple consecutive failures, assume disconnection
                    if consecutive_errors >= self.max_consecutive_errors:
                        logger.error(
                            f"Multiple heartbeat failures, "
                            f"assuming disconnected (client_id={self.client_id})"
                        )
                        await self._handle_disconnection()
                        break
                else:
                    consecutive_errors = 0  # Reset counter on successful heartbeat

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                logger.info("Heartbeat task cancelled")
                break
            except Exception as e:
                consecutive_errors += 1
                logger.exception(f"Error sending heartbeat: {e}")

                # Check for disconnection on consecutive errors
                if consecutive_errors >= self.max_consecutive_errors:
                    logger.error(
                        f"Multiple heartbeat errors, "
                        f"assuming disconnected (client_id={self.client_id})"
                    )
                    await self._handle_disconnection()
                    break

                await asyncio.sleep(0.2)

    async def close(self) -> None:
        """Close the client."""
        logger.info("Closing client connection")
        self._is_closed = True  # Set closed flag first

        async with self._socket_lock:  # Ensure no ongoing operations
            self.running = False

            if self._frame_task:
                self._frame_task.cancel()
                try:
                    await self._frame_task
                except asyncio.CancelledError:
                    logger.debug("Frame receiving task cancelled")

            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    logger.debug("Heartbeat task cancelled")

            # Close sockets
            try:
                self.control_socket.close(linger=0)
                self.stream_socket.close(linger=0)
                logger.debug("Sockets closed")
            except zmq.ZMQError as e:
                logger.error(f"Error closing sockets: {e}")

            # Terminate context
            try:
                self.context.term()
                logger.debug("ZMQ context terminated")
            except zmq.ZMQError as e:
                logger.error(f"Error terminating context: {e}")

        logger.info("Client closed successfully")

    def reset_audio_stream(self) -> None:
        """Reset the audio stream batcher."""
        logger.debug("Resetting audio stream batcher")
        self.stream_batcher.reset()


async def run_example_client(
    client_id: str,
    avatar_model_path: str,
    window_name: Optional[str] = None,
) -> None:
    """Run an example client with visualization."""

    async def show_frame(frame: FrameMessage, frame_info: dict) -> None:
        # Add FPS text to frame
        image = frame.image
        fps_text = f"FPS: {frame_info.get('fps', 0):.1f}"
        cv2.putText(
            image,
            fps_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        logger.debug(f"Displaying frame {frame.source_message_id} with FPS {fps_text}")

        window = window_name or f"Client {client_id}"
        cv2.imshow(window, image)
        key = chr(cv2.waitKey(1) & 0xFF).lower()
        if key == "q":
            logger.info("Quit key pressed, raising KeyboardInterrupt")
            raise KeyboardInterrupt

        # Example of async processing
        await asyncio.sleep(0)  # Allow other tasks to run

    # Initialize client
    client = ZMQBithumanRuntimeClient(client_id)
    client.set_frame_callback(show_frame)  # Now accepts async callback
    logger.info("Starting example client")
    await client.start()

    try:
        # Initialize workspace
        response = await client.init_workspace(avatar_model_path)
        if response.status != ResponseStatus.SUCCESS:
            logger.error(f"Failed to initialize workspace: {response}")
            return
        logger.info("Workspace initialized in example client")

        # Keep running until interrupted
        while True:
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Shutting down client...")
    finally:
        await client.close()
        cv2.destroyAllWindows()
        logger.info("Example client closed")


async def play_audio_example(
    client_ids: list[str],
    audio_file: str,
    text: Optional[str] = None,
    control_port: int = 5555,
) -> None:
    """Play audio file to multiple clients.

    Args:
        client_ids: List of client IDs to send audio to
        audio_file: Path to audio file
        text: Optional text to be spoken
        control_port: Server control port
    """
    for client_id in client_ids:
        try:
            # Create client
            client = ZMQBithumanRuntimeClient(client_id, control_port=control_port)
            await client.start()

            # Load and prepare audio
            logger.info(f"Loading audio file: {audio_file}")
            audio_data, sample_rate = load_audio(audio_file)
            audio_data = float32_to_int16(audio_data)

            # Stream audio
            logger.info(
                f"Streaming audio to {client_id}: "
                f"duration={len(audio_data) / sample_rate:.2f}s, "
                f"sample_rate={sample_rate}Hz"
            )
            await client.send_audio(
                audio_bytes=audio_data.tobytes(),
                sample_rate=sample_rate,
                is_last=False,
                text=text,
            )

            # Cleanup
            await client.close()

        except Exception as e:
            logger.exception(f"Error playing audio to client {client_id}: {e}")


async def interrupt_example(client_ids: list[str], control_port: int = 5555) -> None:
    """Interrupt audio processing for multiple clients.

    Args:
        client_ids: List of client IDs to interrupt
        control_port: Server control port
    """
    for client_id in client_ids:
        try:
            client = ZMQBithumanRuntimeClient(client_id, control_port=control_port)
            await client.start()
            await client.interrupt()
            await client.close()
        except Exception as e:
            logger.exception(f"Error interrupting client {client_id}: {e}")


def main() -> None:
    """Main entry point for the client CLI."""
    parser = argparse.ArgumentParser(description="ZMQ Bithuman Runtime Client CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start client command
    start_parser = subparsers.add_parser(
        "start", help="Start a test client with visualization"
    )
    start_parser.add_argument("--client-id", type=str, required=True, help="Client ID")
    start_parser.add_argument(
        "--avatar-model-path", type=str, required=True, help="Avatar model path"
    )
    start_parser.add_argument("--window-name", type=str, help="Window name for display")

    # Play audio command
    play_parser = subparsers.add_parser(
        "play-audio", help="Play audio to one or more clients"
    )
    play_parser.add_argument(
        "--client-id",
        type=str,
        nargs="+",
        required=True,
        help="Client IDs to send audio to",
    )
    play_parser.add_argument(
        "--audio-file", type=str, required=True, help="Path to audio file"
    )
    play_parser.add_argument("--text", type=str, help="Text to be spoken")
    play_parser.add_argument(
        "--control-port", type=int, default=5555, help="Server control port"
    )

    # Interrupt command
    interrupt_parser = subparsers.add_parser(
        "interrupt", help="Interrupt audio processing"
    )
    interrupt_parser.add_argument(
        "--client-id",
        type=str,
        nargs="+",
        required=True,
        help="Client IDs to interrupt",
    )
    interrupt_parser.add_argument(
        "--control-port", type=int, default=5555, help="Server control port"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    logger.remove()
    logger.add(sys.stderr, level="INFO")

    try:
        logger.debug(f"Executing command '{args.command}' with args: {args}")
        if args.command == "start":
            args.avatar_model_path = os.path.abspath(args.avatar_model_path)
            asyncio.run(
                run_example_client(
                    args.client_id, args.avatar_model_path, args.window_name
                )
            )

        elif args.command == "play-audio":
            asyncio.run(
                play_audio_example(
                    client_ids=args.client_id,
                    audio_file=args.audio_file,
                    text=args.text,
                    control_port=args.control_port,
                )
            )

        elif args.command == "interrupt":
            asyncio.run(
                interrupt_example(
                    client_ids=args.client_id,
                    control_port=args.control_port,
                )
            )

    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
    except Exception as e:
        logger.exception(f"Error executing command {args.command}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
