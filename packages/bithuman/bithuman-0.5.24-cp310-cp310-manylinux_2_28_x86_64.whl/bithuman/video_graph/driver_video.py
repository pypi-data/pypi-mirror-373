from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import networkx as nx
import numpy as np
from loguru import logger


@dataclass(frozen=True, order=True)
class Frame:
    video_name: str
    frame_index: int


@dataclass(frozen=True, order=True)
class NodeID:
    video_name: str
    video_hash: str
    frame_index: int

    def __repr__(self) -> str:
        return f"{self.video_name}_{self.video_hash[:8]}_{self.frame_index}"


class DriverVideo:
    def __init__(
        self,
        name: str,
        video_path: str,
        video_data_path: Optional[str] = None,
        num_frames: Optional[int] = None,
        *,
        stride: int = 10,
        single_direction: bool = False,
        stop_on_user_speech: bool = False,
        stop_on_agent_speech: bool = False,
        lip_sync_required: bool = True,
    ) -> None:
        self.video_name = name

        self.video_path: str = video_path

        # read the video hash
        with open(video_path, "rb") as f:
            self.video_hash = hashlib.md5(f.read()).hexdigest()

        # update the video_data_path
        self.video_data_path: Optional[str] = video_data_path or _find_video_data_path(
            video_path, self.video_hash
        )

        # read the number of frames
        cap = cv2.VideoCapture(video_path)
        try:
            total_num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.resolution = (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            )
        finally:
            cap.release()
        if num_frames is not None:
            assert num_frames <= total_num_frames, (
                f"num_frames {num_frames} > total_num_frames {total_num_frames}"
            )
        else:
            num_frames = total_num_frames
        self.num_frames = num_frames
        self.frames = [Frame(self.video_name, i) for i in range(num_frames)]

        # The transition points, default to all nodes
        self.single_direction = single_direction
        self.init_nodes(stride)
        self.transition_nodes = self.nodes

        # Stop on user speech or agent speech
        self.stop_on_user_speech = stop_on_user_speech
        self.stop_on_agent_speech = stop_on_agent_speech
        self.lip_sync_required = lip_sync_required

    @property
    def video_id(self) -> str:
        return f"{self.video_name}_{self.video_hash[:8]}"

    def get_frame_wh(self, scale_size: Optional[int] = None) -> Tuple[int, int]:
        if scale_size is None:
            return self.resolution

        # scale max dimension to `scale_size`
        scale = scale_size / max(self.resolution)
        return (
            int(self.resolution[0] * scale),
            int(self.resolution[1] * scale),
        )

    def get_first_frame(self, scale_size: Optional[int] = None) -> np.ndarray:
        cap = cv2.VideoCapture(str(self.video_path))
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                raise ValueError("Failed to read the first frame")

            if scale_size is not None:
                frame = cv2.resize(frame, self.get_frame_wh(scale_size))
            return frame
        finally:
            cap.release()

    def init_nodes(self, stride: int) -> None:
        if stride <= 0:
            # one node for whole video
            stride = self.num_frames
        self.stride = stride
        self.nodes = [
            NodeID(self.video_name, self.video_hash, i)
            for i in range(0, self.num_frames, stride)
        ]
        # Last frame
        if self.nodes[-1].frame_index != self.num_frames - 1:
            self.nodes.append(
                NodeID(self.video_name, self.video_hash, self.num_frames - 1)
            )

    def remove_nodes(
        self, *, indices: List[int] = None, frame_indices: List[int] = None
    ) -> int:
        new_nodes = self.nodes

        if indices:
            new_nodes = [
                node for idx, node in enumerate(new_nodes) if idx not in set(indices)
            ]

        if frame_indices:
            new_nodes = [
                node for node in new_nodes if node.frame_index not in set(frame_indices)
            ]

        removed = len(self.nodes) - len(new_nodes)
        self.nodes = new_nodes
        self.transition_nodes = self.nodes
        return removed

    def insert_nodes(self, frame_indices: List[int]) -> None:
        new_nodes = []
        for idx in frame_indices:
            if idx < self.num_frames:
                new_nodes.append(NodeID(self.video_name, self.video_hash, idx))
        self.nodes = sorted(set(self.nodes + new_nodes))
        self.transition_nodes = self.nodes

    @property
    def transition_frames(self) -> List[Frame]:
        return [self.frames[node.frame_index] for node in self.transition_nodes]

    def draw_nodes(
        self, nodes: List[NodeID], n_cols: int = 2, image_width: int = 720
    ) -> np.ndarray:
        """Draw the frames of the nodes."""
        frames = [self.frames[node.frame_index] for node in nodes]
        node_indices = [self.nodes.index(node) for node in nodes]
        labels = [f"{idx}: {node}" for idx, node in zip(node_indices, nodes)]
        return self.draw_frames(frames, labels, n_cols, image_width)

    def as_graph(self) -> nx.DiGraph:
        """Create a graph from the video nodes.
        For single_direction mode, creates a directed cycle that only moves forward.
        For normal mode, creates a bidirectional graph.
        """
        graph = nx.DiGraph()
        graph.add_nodes_from(self.nodes)
        # Add edges between consecutive nodes
        for i in range(1, len(self.nodes)):
            first, second = self.nodes[i - 1], self.nodes[i]
            distance = second.frame_index - first.frame_index

            # Add forward edge
            graph.add_edge(first, second, distance=distance)

            # Add backward edge if not in single direction mode
            if not self.single_direction:
                graph.add_edge(second, first, distance=distance)

        return graph

    def collect_frames(
        self,
        source: NodeID | int,
        target: NodeID | int,
        allow_multi_steps: bool = True,
    ) -> List[Frame]:
        """Collect frames between two nodes.

        Include the frame of the `source` and exclude the frame of the `target`.
        If the distance between the two nodes is larger than one step,
        and `allow_multi_steps` is False, return only the frame of the `prev_node`.
        # TODO: write filler info to the edge and remove `allow_multi_steps`

        Returns:
            List[np.ndarray]: The collected frames.
        """
        if isinstance(source, int):
            source = self.nodes[source]
        if isinstance(target, int):
            target = self.nodes[target]

        if (
            source.video_hash != self.video_hash
            and target.video_hash != self.video_hash
        ):
            logger.warning(
                f"Both nodes are not from this video: "
                f"{source} and {target} != {self.video_hash}"
            )
            return []

        if source.video_hash != self.video_hash:
            # Jump from another video to this video, return empty list
            return []

        if target.video_hash != self.video_hash or (
            not allow_multi_steps
            and abs(source.frame_index - target.frame_index) > self.stride
        ):
            # Jump from this video to another video
            # or the distance between the two nodes is larger than one step
            # assume this is a "jumper connection"
            return [self.frames[source.frame_index]]

        # Both nodes are from this video
        stride = 1 if source.frame_index < target.frame_index else -1
        if self.single_direction and stride == -1:
            # Single direction video can only move forward
            return []
        return self.frames[source.frame_index : target.frame_index : stride]


class LoopingVideo(DriverVideo):
    def __init__(
        self,
        name: str,
        video_path: str,
        video_data_path: Optional[str] = None,
        num_frames: Optional[int] = None,
        *,
        stride: int = 10,
        single_direction: bool = False,
        stop_on_user_speech: bool = False,
        stop_on_agent_speech: bool = False,
        lip_sync_required: bool = True,
        loop_between: Tuple[int, int] = (0, None),
    ) -> None:
        """A video that loops between two frames.

        Args:
            loop_between: Tuple of (start, end) frame indices to loop between.
                None means start or end of video.
            single_direction: If True, video only plays forward from start to end,
                then jumps back to start. If False, video plays back and forth.
        """
        super().__init__(
            name,
            video_path=video_path,
            video_data_path=video_data_path,
            num_frames=num_frames,
            stride=stride,
            single_direction=single_direction,
            stop_on_user_speech=stop_on_user_speech,
            stop_on_agent_speech=stop_on_agent_speech,
            lip_sync_required=lip_sync_required,
        )

        self.loop_direction = 1  # 1 for forward, -1 for backward
        self._loop_start_node = None
        self._loop_end_node = None
        self.set_loop_between(*loop_between)

    def set_loop_between(self, start: Optional[int], end: Optional[int]) -> int:
        start = start or 0
        end = end or -1
        if end < 0:
            end = len(self.frames) + end
        self.loop_between = (max(0, start), min(len(self.frames) - 1, end))
        if self.loop_between[0] > self.loop_between[1]:
            raise ValueError(f"Invalid loop_between {self.loop_between}")

        # Create and store loop nodes
        self._loop_start_node = NodeID(
            self.video_name, self.video_hash, self.loop_between[0]
        )
        self._loop_end_node = NodeID(
            self.video_name, self.video_hash, self.loop_between[1]
        )

        # Add loop nodes if not already in nodes list
        if self._loop_start_node not in self.nodes:
            self.nodes = sorted(self.nodes + [self._loop_start_node])
        if self._loop_end_node not in self.nodes:
            self.nodes = sorted(self.nodes + [self._loop_end_node])

        return self.loop_between[1] - self.loop_between[0]

    def get_n_frames(
        self, min_n: int, start: NodeID, last_position: Optional[NodeID] = None
    ) -> Tuple[List[Frame], NodeID]:
        """Get at least `min_n` frames from the start node.

        Args:
            min_n: The minimum number of frames to get.
            start: The start node.
            last_position: The last position node for determine direction.

        Returns:
            The collected frames and the last position node.
        """
        if start.video_hash != self.video_hash:
            logger.warning(
                f"Enter node is not from this video: {start} != {self.video_hash}"
            )
            return [], None

        if min_n <= 0:
            return [], None

        start_idx = self.nodes.index(start)
        if start_idx == -1:
            logger.warning(f"Node {start} is not in the nodes list")
            return [], None

        # NOTE: loop_end and loop_start are frame index,
        # be careful if the new node index is valid
        loop_start, loop_end = self.loop_between

        # For single_direction, always move forward
        if self.single_direction:
            self.loop_direction = 1
        elif last_position and last_position.video_hash != self.video_hash:
            # reset the direction if the last postion is from another video
            # Move to the direction with more frames
            left_frames = start.frame_index - loop_start
            right_frames = loop_end - start.frame_index
            self.loop_direction = 1 if right_frames > left_frames else -1

        frames = []
        curr_node = start
        curr_idx = start_idx
        while len(frames) < min_n:
            if self.single_direction:
                if curr_node.frame_index >= loop_end:
                    # Jump back to loop_start when reaching loop_end
                    next_node = self._loop_start_node
                    next_idx = self.nodes.index(self._loop_start_node)
                else:
                    next_idx = curr_idx + 1
                    next_node = self.nodes[next_idx]
            else:
                # bidirectional behavior
                if curr_node.frame_index >= loop_end:
                    self.loop_direction = -1
                elif curr_node.frame_index <= loop_start:
                    self.loop_direction = 1
                next_idx = curr_idx + self.loop_direction
                next_node = self.nodes[next_idx]

            frames += self.collect_frames(curr_node, next_node)
            curr_node = next_node
            curr_idx = next_idx

        return frames, curr_node

    def as_graph(self) -> nx.Graph:
        """Create a graph from the video nodes with a loop back edge."""
        graph = super().as_graph()

        # Add loop back edge using stored nodes
        if self.single_direction:
            graph.add_edge(self._loop_end_node, self._loop_start_node, distance=0)

        return graph


class SingleActionVideo(DriverVideo):
    def __init__(
        self,
        name: str,
        video_path: str,
        video_data_path: Optional[str] = None,
        num_frames: Optional[int] = None,
        *,
        single_direction: bool = False,
        stop_on_user_speech: bool = False,
        stop_on_agent_speech: bool = False,
        lip_sync_required: bool = True,
        transition_frames: Optional[List[int]] = None,
        action_frame: int = -1,
    ) -> None:
        """A video that plays a single action.

        `transition_frame_indices` is a list of frame indices
            that are the transition nodes.
        """
        super().__init__(
            name,
            video_path=video_path,
            video_data_path=video_data_path,
            num_frames=num_frames,
            stride=-1,
            single_direction=single_direction,
            stop_on_user_speech=stop_on_user_speech,
            stop_on_agent_speech=stop_on_agent_speech,
            lip_sync_required=lip_sync_required,
        )
        transition_frames = transition_frames or [0]
        if single_direction:
            transition_frames.append(-1)
        transition_frames = [
            frame if frame >= 0 else len(self.frames) + frame
            for frame in transition_frames
        ]
        transition_nodes = [
            NodeID(self.video_name, self.video_hash, i) for i in set(transition_frames)
        ]

        action_frame = (
            action_frame if action_frame >= 0 else len(self.frames) + action_frame
        )
        self._action_node = NodeID(self.video_name, self.video_hash, action_frame)

        self.nodes = sorted(set(self.nodes + transition_nodes + [self._action_node]))
        self.transition_nodes = sorted(transition_nodes)

    @property
    def action_node(self) -> NodeID:
        return self._action_node

    def as_graph(self) -> nx.Graph:
        if not self.single_direction:
            return super().as_graph()
        graph = nx.DiGraph()
        graph.add_nodes_from(self.nodes)
        # add edges for a single direction video
        for i in range(1, len(self.nodes)):
            first, second = self.nodes[i - 1], self.nodes[i]
            graph.add_edge(
                first, second, distance=second.frame_index - first.frame_index
            )
        return graph

    def get_frames(self, start: NodeID) -> Tuple[List[Frame], NodeID]:
        if start.video_hash != self.video_hash:
            logger.warning(
                f"Enter node is not from this video: {start} != {self.video_hash}"
            )
            return ([], None)
        start_idx = self.nodes.index(start)
        if start_idx == -1:
            logger.warning(f"Node {start} is not in the nodes list")
            return ([], None)

        # Collect all frames of the action
        # start -> last frame -> last transition frame
        path = [start, self.action_node, self.transition_nodes[-1]]
        frames = []
        for i in range(1, len(path)):
            frames += self.collect_frames(path[i - 1], path[i], allow_multi_steps=True)
        return frames, path[-1]


def _find_video_data_path(video_path: str, file_hash: str) -> Optional[str]:
    video_path = Path(video_path)
    name = f"{video_path.name}.*_{file_hash[:8]}"
    for suffix in ["h5", "pth"]:
        files = list(video_path.parent.glob(name + f".{suffix}"))
        if files:
            return files[0].as_posix()
    return None
