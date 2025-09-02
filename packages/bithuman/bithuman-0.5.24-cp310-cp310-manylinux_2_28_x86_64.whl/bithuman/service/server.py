"""ZMQ server for bithuman runtime service."""
from __future__ import annotations

import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from queue import Empty
from threading import Lock, Semaphore, Thread
from typing import Dict, Optional

import msgpack
import numpy as np
import zmq
from loguru import logger

from bithuman.api import VideoFrame
from bithuman.runtime import Bithuman
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
from bithuman.utils.fps_controller import FPSController

logger.remove()
logger.add(sys.stdout, level="INFO")


class SessionWorker(ABC):
    """Abstract base class for session workers.

    Handles frame processing and streaming for a single client session.
    """

    def __init__(
        self,
        stream_socket: zmq.Socket,
        init_request: InitRequest,
        stream_socket_lock: Lock,
        init_semaphore: Semaphore,
    ) -> None:
        """Initialize the worker.

        Args:
            stream_socket: ZMQ socket for streaming frames
            init_request: Initialization request
            stream_socket_lock: Lock for stream socket
            init_semaphore: Semaphore for initialization
        """
        self.client_id = init_request.client_id
        self.stream_socket = stream_socket
        self.stream_socket_lock = stream_socket_lock  # Add lock
        self.init_semaphore = (
            init_semaphore  # Add semaphore for concurrent initialization
        )
        self.init_request = init_request
        self.is_active = True
        self.fps = 25

        # FPS control
        self.fps_controller = FPSController(target_fps=self.fps)

        # Statistics
        self.frame_count = 0
        self.last_log_time = time.time()

        # Initialize daemon with mutable Event
        self.runtime = Bithuman()
        self.runtime.set_model(
            model_path=self.init_request.avatar_model_path, load_data=False
        )

        # Add last active timestamp
        self.last_active_time = time.time()
        self.max_inactive_time = 5.0  # 5 seconds timeout

        self.interrupt_requested = False

        self.cleanup_lock = Lock()
        self.cleaned_up = False

        logger.info(
            f"Created worker for client {self.client_id}: {self.init_request.to_dict()}"
        )

    def get_first_frame(self) -> Optional[np.ndarray]:
        """Get the first frame of the video."""
        return self.runtime.get_first_frame()

    def interrupt(self) -> None:
        """Interrupt current processing by temporarily muting.

        Clears the input queue and temporarily mutes audio processing
        while maintaining video output.
        """
        self.runtime.interrupt()
        logger.info(f"Interrupted processing for client {self.client_id}")

    def run(self) -> None:
        """Process frames for the client."""
        logger.info(f"Starting frame processing for client {self.client_id}")
        with self.init_semaphore:
            logger.info(f"Loading model for client {self.client_id}")
            self.runtime.load_data()
            logger.info(f"Model loaded for client {self.client_id}")

        while self.is_running:
            try:
                # Process frames
                for frame in self.runtime.run():
                    if not self.is_running or not self.is_active:
                        logger.debug(
                            f"Worker for client {self.client_id} stopped or inactive"
                        )
                        break

                    # Wait for next frame time
                    self.fps_controller.wait_next_frame()
                    self.send_frame(frame, time.time())
                    # Update FPS controller
                    self.fps_controller.update()

            except Empty:
                time.sleep(0.001)
            except Exception:
                logger.exception(f"Error processing frames for client {self.client_id}")

    def send_frame(self, frame: VideoFrame, current_time: float) -> None:
        """Send a frame to the client."""
        try:
            # Create FrameMessage first (outside lock)
            frame_msg = FrameMessage.create(
                client_id=self.client_id,
                frame_image=frame.bgr_image,
                frame_index=frame.frame_index,
                source_message_id=frame.source_message_id,
                end_of_speech=frame.end_of_speech,
                audio_bytes=frame.audio_chunk.bytes if frame.audio_chunk else None,
                sample_rate=(
                    frame.audio_chunk.sample_rate if frame.audio_chunk else None
                ),
                # metadata
                stream_fps=self.fps_controller.fps,
            )

            # Serialize data outside lock
            try:
                msg_data = zmq.Frame(
                    msgpack.packb(frame_msg.to_dict(), use_bin_type=True)
                )
                topic = zmq.Frame(self.client_id.encode())
            except Exception as e:
                logger.error(
                    f"Failed to serialize frame data for client {self.client_id}: {e}"
                )
                return

            # Only lock the actual send operation
            try:
                with self.stream_socket_lock:
                    self.stream_socket.send_multipart(
                        [topic, msg_data], flags=zmq.NOBLOCK, copy=False
                    )
            except zmq.error.Again as e:
                logger.warning(f"Client {self.client_id} is not receiving frames: {e}")
                return
            except zmq.ZMQError as e:
                logger.error(f"Failed to send frame for client {self.client_id}: {e}")
                return

            # Update statistics (outside lock)
            self.frame_count += 1
            if current_time - self.last_log_time > 5:
                fps = self.frame_count / (current_time - self.last_log_time)
                logger.debug(
                    f"Client {self.client_id} streaming at {fps:.2f} FPS "
                    f"(target: {self.fps_controller.target_fps}, "
                    f"average: {self.fps_controller.fps:.2f})"
                )
                self.frame_count = 0
                self.last_log_time = current_time

        except Exception as e:
            logger.error(f"Failed to send frame for client {self.client_id}: {e}")

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Check if the worker is running.

        Returns:
            True if the worker is still running, False otherwise
        """
        pass

    def stop(self) -> None:
        """Stop the worker and cleanup resources with proper locking."""
        with self.cleanup_lock:
            if self.cleaned_up:
                return
            self.cleaned_up = True
            self.is_active = False

            # Ensure daemon cleanup
            if self.runtime is not None:
                self.runtime.cleanup()
                self.runtime = None

        logger.info(f"Cleaned up worker for client {self.client_id}")

    def update_active_time(self) -> None:
        """Update last active timestamp to current time."""
        self.last_active_time = time.time()
        logger.debug(f"Updated active time for client {self.client_id}")

    @property
    def is_inactive_timeout(self) -> bool:
        """Check if worker has been inactive for too long.

        Returns:
            True if worker has exceeded max inactive time, False otherwise
        """
        return time.time() - self.last_active_time > self.max_inactive_time


class ThreadedSessionWorker(SessionWorker):
    """Threaded implementation of session worker."""

    def __init__(
        self,
        stream_socket: zmq.Socket,
        init_request: InitRequest,
        stream_socket_lock: Lock,
        init_semaphore: Semaphore,
    ) -> None:
        """Initialize the threaded worker."""
        super().__init__(
            stream_socket, init_request, stream_socket_lock, init_semaphore
        )
        self.running = True
        self.thread = Thread(target=self.run)
        logger.info(f"Initialized threaded worker for client {self.client_id}")

    @property
    def is_running(self) -> bool:
        """Check if the worker is running."""
        return self.running

    def stop(self) -> None:
        """Stop the worker thread."""
        logger.info(f"Stopping worker for client {self.client_id}")
        self.running = False
        self.thread.join()
        super().stop()
        logger.info(f"Stopped worker for client {self.client_id}")


class ZMQBithumanRuntimeServer:
    """ZMQ server for Bithuman Runtime.

    Manages client connections, worker processes, and message routing.
    Handles initialization, audio processing, and frame streaming for multiple clients.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        control_port: int = 5555,
        stream_port: int = 5556,
        max_concurrent_inits: int = 1,
    ) -> None:
        """Initialize the server.

        Args:
            host: Host address to bind to
            control_port: Port for control messages
            stream_port: Port for frame streaming
            max_concurrent_inits: Maximum number of concurrent initializations
        """
        logger.info(
            f"Initializing ZMQBithumanRuntimeServer on {host} "
            f"(control_port={control_port}, stream_port={stream_port})"
        )
        self.context = zmq.Context()

        # Control socket for commands (REQ/REP pattern)
        self.control_socket = self.context.socket(zmq.REP)
        self.control_socket.bind(f"tcp://{host}:{control_port}")
        logger.debug(f"Control socket bound to tcp://{host}:{control_port}")

        # Pub socket for streaming frames
        self.stream_socket = self.context.socket(zmq.PUB)
        self.stream_socket.bind(f"tcp://{host}:{stream_port}")
        logger.debug(f"Stream socket bound to tcp://{host}:{stream_port}")

        self.workers: Dict[str, SessionWorker] = {}
        self.workers_lock = Lock()
        self.running = True

        # Add stream socket lock
        self.stream_socket_lock = Lock()
        # Replace Lock with Semaphore for concurrent initialization
        self.init_semaphore = Semaphore(max_concurrent_inits)

        # Start control message handler
        self.control_thread = Thread(target=self._handle_control)
        self.control_thread.start()
        logger.info("Started control message handler thread")

        # Start worker monitor thread
        self.monitor_thread = Thread(target=self._monitor_workers)
        self.monitor_thread.start()
        logger.info("Started worker monitor thread")

        self.initializing_workers: Dict[
            str, Thread
        ] = {}  # Track workers being initialized
        self.init_errors: Dict[str, str] = {}  # Track initialization errors

    def _handle_control(self) -> None:
        """Handle incoming control messages."""
        logger.info("Starting control message handler loop")

        while self.running:
            try:
                try:
                    msg = msgpack.unpackb(
                        self.control_socket.recv(flags=zmq.NOBLOCK), raw=False
                    )
                except zmq.error.Again:
                    # No messages waiting
                    time.sleep(0.001)
                    continue
                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        # Context was terminated
                        break
                    logger.error(f"ZMQ error in control handler: {e}")
                    continue

                self._process_control_message(msg)

            except Exception as e:
                logger.exception("Error handling control message")
                error_response = ServerResponse(
                    status=ResponseStatus.ERROR,
                    message=str(e),
                )
                self._send_response(error_response, "unknown")

    def _process_control_message(self, msg: dict) -> None:
        """Process a single control message."""
        cmd = msg.get("command")
        client_id = msg.get("client_id", "unknown")

        logger.debug(f"Received '{cmd}' command from client {client_id}")

        # Update worker active time and check connection
        with self.workers_lock:
            worker = self.workers.get(client_id)
            if worker:
                worker.update_active_time()

        # Handle command
        if cmd == "init":
            response = self._handle_init(msg)
        elif cmd == "audio":
            response = self._handle_audio(msg)
        elif cmd == "heartbeat":
            response = self._handle_heartbeat(msg)
        elif cmd == "interrupt":
            response = self._handle_interrupt(msg)
        elif cmd == "check_init_status":
            response = self._handle_check_init_status(msg)
        elif cmd == "get_setting":
            response = self._handle_get_setting(msg)
        else:
            logger.warning(f"Unknown command received from client {client_id}: {cmd}")
            response = ServerResponse(
                status=ResponseStatus.ERROR,
                message=f"Unknown command: {cmd}",
            )

        # Send response
        self._send_response(response, client_id)
        logger.debug(f"Sent response to client {client_id}: {response}")

    def _send_response(self, response: ServerResponse, client_id: str) -> None:
        """Send response to client."""
        try:
            # Use blocking send for REQ/REP pattern
            self.control_socket.send(
                msgpack.packb(response.to_dict(), use_bin_type=True)
            )
        except zmq.ZMQError as e:
            logger.error(f"Failed to send response to client {client_id}: {e}")

    def _handle_init(self, msg: dict) -> ServerResponse:
        """Handle workspace initialization request."""
        try:
            request = InitRequest(**msg)
            logger.info(f"Handling init request for client {request.client_id}")

            if not Path(request.avatar_model_path).exists():
                error_msg = f"Workspace not found: {request.avatar_model_path}"
                logger.error(error_msg)
                return ServerResponse(
                    status=ResponseStatus.ERROR,
                    message=error_msg,
                )

            # If already initialized, return success
            if request.client_id in self.workers:
                logger.info(f"Client {request.client_id} already initialized")
                return ServerResponse(
                    status=ResponseStatus.SUCCESS,
                    message="Client already initialized",
                )

            # If already initializing, return loading status
            if request.client_id in self.initializing_workers:
                logger.info(f"Client {request.client_id} initialization in progress")
                return ServerResponse(
                    status=ResponseStatus.LOADING,
                    message="Initialization in progress",
                )

            # Define initialization function
            def initialize_worker() -> None:
                logger.info(f"Initializing worker for client {request.client_id}")
                try:
                    worker = ThreadedSessionWorker(
                        stream_socket=self.stream_socket,
                        init_request=request,
                        stream_socket_lock=self.stream_socket_lock,
                        init_semaphore=self.init_semaphore,
                    )
                    worker.thread.start()
                    logger.info(f"Started worker thread for client {request.client_id}")

                    with self.workers_lock:
                        self.workers[request.client_id] = worker
                        if request.client_id in self.initializing_workers:
                            del self.initializing_workers[request.client_id]
                    logger.info(f"Worker created for client {request.client_id}")

                    # Send first frame
                    first_frame = worker.get_first_frame()
                    if first_frame is not None:
                        frame_msg = VideoFrame(
                            bgr_image=first_frame, source_message_id="_init_frame"
                        )
                        worker.send_frame(frame_msg, time.time())
                        logger.info(f"Sent first frame to client {request.client_id}")
                    worker.update_active_time()

                except Exception as e:
                    logger.exception(
                        f"Failed to initialize worker for client {request.client_id}"
                    )
                    with self.workers_lock:
                        self.init_errors[request.client_id] = str(e)
                        if request.client_id in self.initializing_workers:
                            del self.initializing_workers[request.client_id]

            # Start initialization in background thread
            init_thread = Thread(target=initialize_worker)
            with self.workers_lock:
                self.initializing_workers[request.client_id] = init_thread
            init_thread.start()
            logger.info(f"Started initialization thread for client {request.client_id}")

            return ServerResponse(
                status=ResponseStatus.LOADING,
                message="Started initialization",
            )

        except Exception as e:
            logger.exception("Failed to start initialization")
            return ServerResponse(status=ResponseStatus.ERROR, message=str(e))

    def _handle_audio(self, msg: dict) -> ServerResponse:
        """Handle audio processing request."""
        try:
            request = AudioRequest.from_dict(msg)

            with self.workers_lock:
                worker = self.workers.get(request.client_id)
                if not worker:
                    error_msg = "Client not initialized"
                    logger.error(error_msg)
                    return ServerResponse(
                        status=ResponseStatus.ERROR, message=error_msg
                    )
            if not request.data.audio:
                logger.info(f"Received control message: {request}")
            worker.runtime.push(request.data)
            return ServerResponse(status=ResponseStatus.SUCCESS)

        except Exception as e:
            logger.exception(f"Error handling audio for client {msg.get('client_id')}")
            return ServerResponse(status=ResponseStatus.ERROR, message=str(e))

    def _handle_heartbeat(self, msg: dict) -> ServerResponse:
        """Handle heartbeat request.

        Args:
            msg: Message containing heartbeat parameters

        Returns:
            Response indicating success or failure
        """
        try:
            request = HeartbeatRequest(**msg)
            client_id = request.client_id
            logger.debug(f"Handling heartbeat for client {client_id}")

            with self.workers_lock:
                if (
                    client_id not in self.workers
                    and client_id not in self.initializing_workers
                ):
                    error_msg = "Client not initialized"
                    logger.error(error_msg)
                    return ServerResponse(
                        status=ResponseStatus.ERROR, message=error_msg
                    )

                return ServerResponse(status=ResponseStatus.SUCCESS)

        except Exception as e:
            logger.exception(
                f"Error handling heartbeat for client {msg.get('client_id')}"
            )
            return ServerResponse(status=ResponseStatus.ERROR, message=str(e))

    def _handle_interrupt(self, msg: dict) -> ServerResponse:
        """Handle interrupt request.

        Args:
            msg: Message containing interrupt parameters

        Returns:
            Response indicating success or failure
        """
        try:
            request = InterruptRequest(**msg)
            logger.info(f"Handling interrupt for client {request.client_id}")

            with self.workers_lock:
                worker = self.workers.get(request.client_id)
                if not worker:
                    error_msg = "Client not initialized"
                    logger.error(error_msg)
                    return ServerResponse(
                        status=ResponseStatus.ERROR, message=error_msg
                    )

                worker.interrupt()
                logger.info(f"Interrupted audio for client {request.client_id}")
                return ServerResponse(status=ResponseStatus.SUCCESS)

        except Exception as e:
            logger.exception(
                f"Error handling interrupt for client {msg.get('client_id')}"
            )
            return ServerResponse(status=ResponseStatus.ERROR, message=str(e))

    def _handle_check_init_status(self, msg: dict) -> ServerResponse:
        """Handle initialization status check request."""
        try:
            request = CheckInitStatusRequest(**msg)
            client_id = request.client_id
            logger.debug(f"Checking init status for client {client_id}")

            # Check for initialization error
            if client_id in self.init_errors:
                error_msg = self.init_errors.pop(client_id)
                logger.error(
                    f"Initialization error for client {client_id}: {error_msg}"
                )
                return ServerResponse(status=ResponseStatus.ERROR, message=error_msg)

            # Check if initialization completed
            if client_id in self.workers:
                logger.info(f"Initialization complete for client {client_id}")
                return ServerResponse(
                    status=ResponseStatus.SUCCESS,
                    message="Initialization complete",
                )

            # Still initializing
            if client_id in self.initializing_workers:
                logger.info(f"Initialization in progress for client {client_id}")
                return ServerResponse(
                    status=ResponseStatus.LOADING,
                    message="Initialization in progress",
                )

            error_msg = "No initialization found for client"
            logger.error(f"{error_msg}: {client_id}")
            return ServerResponse(
                status=ResponseStatus.ERROR,
                message=error_msg,
            )

        except Exception as e:
            logger.exception("Error checking initialization status")
            return ServerResponse(status=ResponseStatus.ERROR, message=str(e))

    def _handle_get_setting(self, msg: dict) -> ServerResponse:
        """Handle get setting request."""
        try:
            request = GetSettingRequest(**msg)
            logger.debug(f"Handling get setting request for client {request.client_id}")
            worker = self.workers.get(request.client_id)
            if not worker:
                error_msg = "Client not exist or not initialized"
                logger.error(error_msg)
                return ServerResponse(
                    status=ResponseStatus.ERROR,
                    message=error_msg,
                )
            if request.name == "video_script":
                logger.info(f"Retrieved video script for client {request.client_id}")
                return ServerResponse(
                    status=ResponseStatus.SUCCESS,
                    extra={"value": worker.runtime.video_graph.videos_script.to_dict()},
                )

            settings = worker.runtime.settings
            if not hasattr(settings, request.name):
                error_msg = f"Setting {request.name} not found"
                logger.error(error_msg)
                return ServerResponse(
                    status=ResponseStatus.ERROR,
                    message=error_msg,
                )
            value = getattr(worker.runtime.settings, request.name)
            logger.info(
                f"Retrieved setting '{request.name}' for client "
                f"{request.client_id}: {value}"
            )
            return ServerResponse(status=ResponseStatus.SUCCESS, extra={"value": value})
        except Exception as e:
            logger.exception("Error getting setting")
            return ServerResponse(status=ResponseStatus.ERROR, message=str(e))

    def _monitor_workers(self) -> None:
        """Monitor workers and cleanup inactive ones."""
        logger.info("Starting worker monitor thread")

        while self.running:
            try:
                with self.workers_lock:
                    inactive_workers = [
                        client_id
                        for client_id, worker in self.workers.items()
                        if worker.is_inactive_timeout
                    ]

                    for client_id in inactive_workers:
                        logger.info(f"Stopping inactive worker for client {client_id}")
                        worker = self.workers[client_id]
                        worker.stop()
                        del self.workers[client_id]

                time.sleep(0.5)  # Check every 500ms

            except Exception:
                logger.exception("Error in worker monitor")

    def stop(self) -> None:
        """Stop the server and cleanup resources.

        Stops all worker threads, closes sockets, and performs cleanup.
        """
        logger.info("Shutting down server...")
        self.running = False

        # Stop all workers
        with self.workers_lock:
            for worker in self.workers.values():
                worker.stop()
            self.workers.clear()
            logger.info("Stopped all workers")

        # Stop threads
        self.monitor_thread.join()
        self.control_thread.join()

        # Close sockets
        self.control_socket.close()
        logger.debug("Closed control socket")
        self.stream_socket.close()
        logger.debug("Closed stream socket")
        self.context.term()
        logger.info("Server shutdown complete")


def serve(
    host: str = "0.0.0.0", control_port: int = 5555, stream_port: int = 5556
) -> None:
    """Start the server.

    Args:
        host: Host address to bind to
        control_port: Port for control messages
        stream_port: Port for frame streaming
    """
    server = ZMQBithumanRuntimeServer(
        host=host, control_port=control_port, stream_port=stream_port
    )
    try:
        logger.info(
            f"Server started on {host} "
            f"(control_port={control_port}, stream_port={stream_port})"
        )
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down server...")
        server.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ZMQ Bithuman Runtime Server")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host address to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--control-port",
        type=int,
        default=5555,
        help="Port for control messages (default: 5555)",
    )
    parser.add_argument(
        "--stream-port",
        type=int,
        default=5556,
        help="Port for frame streaming (default: 5556)",
    )

    args = parser.parse_args()
    serve(host=args.host, control_port=args.control_port, stream_port=args.stream_port)
