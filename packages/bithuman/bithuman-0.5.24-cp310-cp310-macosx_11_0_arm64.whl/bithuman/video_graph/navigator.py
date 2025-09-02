from __future__ import annotations

import hashlib
from collections import defaultdict
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
from loguru import logger

from bithuman.config import Settings
from bithuman.utils.unzip import unzip_tarfile
from bithuman.video_graph.driver_video import (
    DriverVideo,
    Frame,
    LoopingVideo,
    NodeID,
    SingleActionVideo,
)
from bithuman.video_graph.video_script import VideoConfigs, VideoScript


class VideoGraphNavigator:
    CROSS_VIDEO_PENALTY = 30

    def __init__(
        self,
        avatar_model_path: str | Tuple[str, TemporaryDirectory],
        video_configs: VideoConfigs = None,
    ) -> None:
        self.videos: Dict[str, DriverVideo] = {}
        self.filler_videos: Dict[str, DriverVideo] = {}

        self._video_configs = video_configs or VideoConfigs()

        # Workspace directory
        if isinstance(avatar_model_path, tuple):
            self.avatar_model_path, self.temp_dir = avatar_model_path
        else:
            self.avatar_model_path = avatar_model_path
            self.temp_dir = None
        self.filler_frames_dir = Path(self.avatar_model_path) / "filler_videos"
        self.similarity_cache_dir = Path(self.avatar_model_path) / "similarities"

        # Similarity matrices between two videos
        self.similarity_matrices: Dict[Tuple[str, str], np.ndarray] = {}

        # Graph and frame buffer for output
        self.graph = nx.DiGraph()
        self.curr_node = None
        self.frame_buffer: List[Frame] = []

        # Cache all the paths from one node to another
        self.path_cache: Dict[NodeID, Dict[NodeID, Tuple[float, List[NodeID]]]] = (
            defaultdict(dict)
        )

    def cleanup(self):
        """Clean up the temporary directory if it exists."""
        if self.temp_dir and Path(self.temp_dir.name).exists():
            self.temp_dir.cleanup()
        self.temp_dir = None

    def __del__(self):
        """Clean up the temporary directory if it exists."""
        self.cleanup()

    @property
    def videos_script(self) -> VideoScript:
        """Get the video script."""
        return self._video_configs.videos_script

    def update_runtime_configs(self, settings: Settings):
        """Update the runtime configs from the settings."""
        self._video_configs.update_runtime_configs(settings)

    def video_exists(self, name: str, is_action: bool = None) -> bool:
        """Check if the video exists in the navigator.

        Args:
            name: The video name
            is_action: If True, only check the action videos.
                If False, only check the looping videos.
                None, check both.

        Returns:
            True if the video exists.
        """
        if name not in self.videos:
            return False
        if is_action is None:
            return True
        return isinstance(self.videos[name], SingleActionVideo) == is_action

    @property
    def action_videos(self) -> List[SingleActionVideo]:
        """Get all the action videos in the navigator."""
        return [
            video
            for video in self.videos.values()
            if isinstance(video, SingleActionVideo)
        ]

    @property
    def action_video_names(self) -> List[str]:
        """Get all the action video names in the navigator."""
        return [video.video_name for video in self.action_videos]

    @classmethod
    def from_single_video(
        cls, video_file: str, inference_data_file: str = None
    ) -> "VideoGraphNavigator":
        """Create a navigator with a single video."""
        video_configs = VideoConfigs.from_videofile(video_file, inference_data_file)
        return cls(
            avatar_model_path=Path(video_file).parent,
            video_configs=video_configs,
        )

    @classmethod
    def from_workspace(
        cls,
        avatar_model_path: str,
        video_config_file: str = None,
        extract_to_local: bool = False,
    ) -> "VideoGraphNavigator":
        """Create a navigator from the model."""
        logger.info(f"Loading model from {avatar_model_path}")
        avatar_model_path, temp_dir = unzip_tarfile(
            avatar_model_path, extract_to_local=extract_to_local
        )

        # Load video configs
        video_config_file = video_config_file or Path(avatar_model_path) / "videos.yaml"
        if Path(video_config_file).exists():
            video_configs = VideoConfigs.from_yaml(video_config_file)
        elif (Path(avatar_model_path) / "videos").exists():
            video_configs = VideoConfigs.from_videofolder(
                Path(avatar_model_path) / "videos"
            )
        else:
            files = list(Path(avatar_model_path).glob("*"))
            raise FileNotFoundError(
                f"model not found in {avatar_model_path}, files: {files}"
            )

        # Update video files to absolute path
        for video in video_configs.videos:
            video.video_file = str(
                Path(avatar_model_path).absolute() / video.video_file
            )

        return cls(
            avatar_model_path=(avatar_model_path, temp_dir),
            video_configs=video_configs,
        )

    def load_workspace(
        self, prepare_filler_frames: bool = True
    ) -> "VideoGraphNavigator":
        """Load the videos from workspace.

        Args:
            prepare_filler_frames: If True, prepare filler frames for all the edges
        """
        # Load videos
        videos = self._video_configs.load_videos(video_root=self.avatar_model_path)

        # Init the navigator
        for video, config in zip(videos, self._video_configs.videos):
            self.add_video(video, **config.adding_kwargs)
        if prepare_filler_frames:
            self.load_filler_frames_for_allnodes()
        return self

    def update_path_cache(self):
        """Update the path cache for all the nodes in the graph."""
        self.path_cache.clear()
        for source in self.graph.nodes:
            distance, path = nx.single_source_dijkstra(
                self.graph, source, weight="distance"
            )
            self.path_cache[source] = {
                target: (distance[target], path[target]) for target in path
            }

    def single_source_multi_target_dijkstra(
        self, source: NodeID, targets: List[NodeID]
    ) -> Tuple[float, List[NodeID]]:
        """Find the shortest path from the source node to any of target nodes.

        The method uses the path cache to speed up the computation.
        Make sure to update the path cache after the graph is updated.

        Args:
            source: Node to start the search from
            targets: List of target nodes

        Raises:
            nx.NetworkXNoPath: If no path is found from the source
                to any of the target nodes

        Returns:
            Tuple[float, List[NodeID]]: The distance and the shortest path
                from the source to one of the target nodes
        """
        paths = [
            self.path_cache[source][target]
            for target in targets
            if target in self.path_cache[source]
        ]
        if not paths:
            raise nx.NetworkXNoPath(f"No path found from {source} to {targets}")
        shortest_path = min(paths, key=lambda x: x[0])
        return shortest_path

    def reset_buffer(self) -> None:
        """Reset the frame buffer."""
        self.curr_node = None
        self.frame_buffer = []

    def add_edge(
        self,
        source_node: NodeID,
        target_node: NodeID,
        distance: float,
        num_filler_frames: int = 0,
        single_direction: bool = False,
        cross_video: bool = False,
    ) -> None:
        """Add an edge to the graph.

        Set two metadata for the edge: distance and num_filler_frames.

        Args:
            source_node: The source node of the edge
            target_node: The target node of the edge
            distance: The distance between the two nodes, added a penalty for
                cross-video edges with filler frames
            num_filler_frames: The number of filler frames between the two nodes
            single_direction: If the edge is only in one direction
        """
        if cross_video:
            distance += self.CROSS_VIDEO_PENALTY
        metadata = {
            "distance": distance,
            "num_filler_frames": num_filler_frames,
            "cross_video": cross_video,
        }
        self.graph.add_edge(source_node, target_node, **metadata)
        if not single_direction:
            self.graph.add_edge(target_node, source_node, **metadata)

    def get_first_frame(self, output_size: Optional[int] = None) -> np.ndarray:
        if not self.videos:
            raise ValueError("No videos is added.")
        video = next(iter(self.videos.values()))
        return video.get_first_frame(output_size)

    def get_frame_wh(self, output_size: Optional[int] = None) -> Tuple[int, int]:
        if not self.videos:
            raise ValueError("No videos is added.")
        video = next(iter(self.videos.values()))
        return video.get_frame_wh(output_size)

    @property
    def num_frames(self) -> int:
        return sum(len(video.frames) for video in self.videos.values())

    @property
    def num_nodes(self) -> int:
        return self.graph.number_of_nodes()

    @property
    def num_edges(self) -> int:
        return self.graph.number_of_edges()

    @property
    def edges_with_filler_frames(self) -> List[Tuple[NodeID, NodeID]]:
        edges = []
        seen = set()
        for source, target in self.graph.edges:
            if not self.graph[source][target].get("num_filler_frames"):
                continue
            key = tuple(sorted([source, target]))
            if key in seen:
                continue
            seen.add(key)
            edges.append((source, target))
        return edges

    @property
    def num_filler_frames(self) -> int:
        return sum(
            self.graph[source][target]["num_filler_frames"]
            for source, target in self.edges_with_filler_frames
        )

    def load_similarity_matrix(
        self, video1: DriverVideo, video2: DriverVideo
    ) -> np.ndarray:
        sorted_videos = sorted([video1, video2], key=lambda x: x.video_id)
        transition_frames = [
            [node.frame_index for node in video.transition_nodes]
            for video in sorted_videos
        ]
        nodes_hash = hashlib.md5(str(transition_frames).encode()).hexdigest()
        sim_cache_file = (
            Path(self.similarity_cache_dir)
            / f"{sorted_videos[0].video_id}-{sorted_videos[1].video_id}"
            f"-{nodes_hash[:8]}.npy"
        )
        if not Path(sim_cache_file).exists():
            raise FileNotFoundError(
                f"Similarity matrix not found between {video1.video_name} and {video2.video_name}."
            )
        sim_matrix = np.load(sim_cache_file)
        if sorted_videos[0].video_id == video1.video_id:
            return sim_matrix
        else:
            return sim_matrix.T

    def load_filler_frames_for_allnodes(self) -> "VideoGraphNavigator":
        """Generate filler frames for all the edges in the graph."""
        logger.trace(
            f"Load filler frames for {len(self.edges_with_filler_frames)} edges, "
            f"total {self.num_filler_frames} frames.",
        )
        # Load videos sequentially without ThreadPool
        for source, target in self.edges_with_filler_frames:
            self.load_filler_frames(source, target)

        self.update_path_cache()
        return self

    def load_filler_frames(
        self, source_node: NodeID, target_node: NodeID, lock: Lock = None
    ) -> int:
        """Generate filler frames between two nodes.

        Returns the number of filler frames loaded.
        """
        edge = self.graph.get_edge_data(source_node, target_node)
        if not edge or not edge.get("num_filler_frames"):
            return 0

        lock = lock or nullcontext()
        num_filler_frames = edge["num_filler_frames"]

        filler_name = self._get_filler_video_name(source_node, target_node)
        filler_video_path = self._get_filler_video_path(source_node, target_node)
        if not Path(filler_video_path).exists():
            logger.warning(
                f"Filler video {filler_video_path} not found, "
                f"skip the {num_filler_frames} filler frames between "
                f"{source_node} and {target_node}."
            )
            return 0

        # Load the filler video
        filler_video = DriverVideo(name=filler_name, video_path=filler_video_path)
        self.filler_videos[filler_name] = filler_video

        # Update edge distance
        with lock:
            self.graph[source_node][target_node]["distance"] = (
                1 + filler_video.num_frames + self.CROSS_VIDEO_PENALTY
            )
        return filler_video.num_frames

    def _get_filler_video_name(self, source: NodeID, target: NodeID) -> str:
        """Get the filler video name."""
        key = tuple(sorted([source, target]))
        n1, n2 = key
        return f"Filler_{n1}-{n2}"

    def _get_filler_video_path(self, source: NodeID, target: NodeID) -> str:
        """Get the cache path for the filler frames."""
        key = tuple(sorted([source, target]))
        n1, n2 = key
        video_file = str(self.filler_frames_dir / f"{n1}-{n2}.mp4")
        return video_file

    def get_filler_frames(
        self, source_node: NodeID, target_node: NodeID
    ) -> List[Frame]:
        """Get the filler frames between two nodes."""
        edge = self.graph.get_edge_data(source_node, target_node)
        if edge is None or not edge.get("num_filler_frames"):
            # No filler frames between the two nodes
            return []

        filler_name = self._get_filler_video_name(source_node, target_node)
        if filler_name not in self.filler_videos:
            logger.warning(
                f"Filler video not found between {source_node} and {target_node}, "
                f"expected {edge['num_filler_frames']} frames. "
                "Please generate the filler frames first."
            )
            return []

        frames = self.filler_videos[filler_name].frames.copy()
        if source_node > target_node:
            # reverse the frames if the source node is after the target node
            frames = frames[::-1]
        return frames

    def add_video(
        self,
        video: DriverVideo,
        edge_threshold: float = 0.7,
        connects_to: List[str] = None,
        num_filler_frames: int = None,
    ) -> None:
        """Add a video to the navigator.

        Connect the video with all the existing videos in the navigator.

        Args:
            video: The video to add
            edge_threshold: The threshold for the edge weight
            connects_to: The video names to connect to the new video,
                if None, connect to all the existing videos
            num_filler_frames: The number of filler frames between the two videos
        """
        if video.video_name in self.videos:
            raise ValueError(f"Video {video.video_name} is already added.")

        self.videos[video.video_name] = video
        self.graph.update(video.as_graph())

        for target_video in self.videos.values():
            if target_video.video_hash == video.video_hash:
                continue
            if connects_to and target_video.video_name not in connects_to:
                continue
            self.connect_two_videos(
                target_video,
                video,
                edge_threshold=edge_threshold,
                num_filler_frames=num_filler_frames,
            )
        self.update_path_cache()

    def connect_two_videos(
        self,
        video1: DriverVideo,
        video2: DriverVideo,
        edge_threshold: float = 0.7,
        num_filler_frames: int = None,
    ) -> int:
        if video1.video_hash == video2.video_hash:
            # TODO: support the same video with different frames
            return 0

        key = (video1.video_id, video2.video_id)
        if key not in self.similarity_matrices:
            sim_matrix = self.load_similarity_matrix(video1, video2)
            self.similarity_matrices[key] = sim_matrix
            self.similarity_matrices[key[::-1]] = sim_matrix.T

        sim_matrix = self.similarity_matrices[key]

        # Add nodes and edges to the graph
        def get_num_fillers(similarity: float):
            if similarity > 0.98:
                return 0
            if similarity > 0.80:
                return 3
            if similarity > 0.70:
                return 7
            return 7

        new_edges = set()

        def connect(video1: DriverVideo, video2: DriverVideo, sim_matrix):
            sim_matrix = sim_matrix.copy()
            if isinstance(video1, SingleActionVideo) and video1.single_direction:
                # Only nodes after the action node are out-nodes
                invalid_indices = [
                    i
                    for i, n in enumerate(video1.transition_nodes)
                    if n < video1.action_node
                ]
                sim_matrix[invalid_indices] = -1
            if isinstance(video2, SingleActionVideo):
                # Only nodes before the action node are in-nodes
                invalid_indices = [
                    i
                    for i, n in enumerate(video2.transition_nodes)
                    if n >= video2.action_node
                ]
                sim_matrix[:, invalid_indices] = -1

            argmax = np.argmax(sim_matrix, axis=1)  # video1 -> video2
            indices = [(i, j, sim_matrix[i, j]) for i, j in enumerate(argmax)]
            indices = list(filter(lambda x: x[2] > edge_threshold, indices))

            for i, j, score in indices:
                # if isinstance(video1, SingleActionVideo) and video1.single_direction:
                #     # Only nodes after the action node are out-nodes
                #     if video1.transition_nodes[i] < video1.action_node:
                #         continue
                # if isinstance(video2, SingleActionVideo):
                #     # Only nodes before the action node are in-nodes
                #     print(video2.transition_nodes[j], video2.action_node)
                #     if video2.transition_nodes[j] >= video2.action_node:
                #         continue

                edge_filler_frames = (
                    get_num_fillers(score)
                    if num_filler_frames is None
                    else num_filler_frames
                )
                self.add_edge(
                    video1.transition_nodes[i],
                    video2.transition_nodes[j],
                    distance=edge_filler_frames + 1,
                    num_filler_frames=edge_filler_frames,
                    single_direction=True,
                    cross_video=video1.video_id != video2.video_id,
                )
                key = tuple(
                    sorted([video1.transition_nodes[i], video2.transition_nodes[j]])
                )
                new_edges.add(key)

        connect(video1, video2, sim_matrix)
        connect(video2, video1, sim_matrix.T)

        logger.trace(
            f"Connect {video1.video_name} and "
            f"{video2.video_name}, {len(new_edges)} edges."
        )

    def find_path(
        self, source: NodeID, target: str | NodeID
    ) -> Tuple[float, List[NodeID]]:
        """Find the shortest path from the source node to the target video or node.

        Args:
            source: The source node
            target: The target video name or node

        Returns:
            The distance and the shortest path from the source to the target
        """

        def count_cross_video_penalty(path: List[NodeID]) -> int:
            penalty = 0
            for i in range(1, len(path)):
                edge = self.graph.get_edge_data(path[i - 1], path[i])
                if edge is None or not edge.get("cross_video"):
                    continue
                penalty += self.CROSS_VIDEO_PENALTY
            return penalty

        if isinstance(target, NodeID):
            distance, path = self.single_source_multi_target_dijkstra(source, [target])
            return distance - count_cross_video_penalty(path), path

        target_video = self.videos[target]
        if target_video.video_hash == source.video_hash:
            # Already in the target video
            return 0, [source]

        # find the shortest path to a node of the target video
        distance, path = self.single_source_multi_target_dijkstra(
            source, target_video.transition_nodes
        )
        return distance - count_cross_video_penalty(path), path

    def collect_path_frames(self, path: List[NodeID]) -> List[Frame]:
        """Collect frames from the path."""
        frames = []
        for i in range(len(path) - 1):
            source, target = path[i], path[i + 1]
            frames += self.videos[source.video_name].collect_frames(source, target)
            # Add filler frames if they exist
            frames += self.get_filler_frames(source, target)
        return frames

    def collect_n_frames(
        self,
        min_n: int,
        target_video_name: str = None,
        actions_name: List[str] | str = None,
    ) -> List[Frame]:
        """Collect at least min_n frames from the navigator.

        The frames are collected from the current node to the target video.
        """
        target_video_name, actions_name = self.filter_video_names(
            target_video_name, actions_name
        )
        if min_n <= 0 and not actions_name and not target_video_name:
            return []

        if self.curr_node is None:
            if target_video_name is None:
                self.curr_node = list(self.videos.values())[0].nodes[0]
                logger.trace(
                    f"Current node is not set, set to the first node of "
                    f"{self.curr_node.video_name}."
                )
            else:
                self.curr_node = self.videos[target_video_name].nodes[0]

        target_video_name = target_video_name or self.curr_node.video_name
        target_videos = [self.videos[target_video_name]]

        if isinstance(actions_name, str):
            actions_name = [actions_name]
        if actions_name:
            target_videos = [self.videos[name] for name in actions_name] + target_videos

        assert isinstance(target_videos[-1], LoopingVideo), (
            "The target video must be a LoopingVideo"
        )

        # [action_1, action_2, ..., target_video]
        total_path = [self.curr_node]
        total_distance = 0
        for video in target_videos:
            target = (
                video.action_node
                if isinstance(video, SingleActionVideo)
                else video.video_name
            )
            distance, path = self.find_path(total_path[-1], target)

            total_path += path[1:]
            total_distance += distance

        frames = self.collect_path_frames(total_path)
        if total_distance != len(frames):
            logger.warning(
                f"Distance mismatch: {total_distance} != {len(frames)}, "
                f"Path: {total_path}"
            )
        # Collect frames from the target video
        n_left = min_n - len(frames)
        last_node = total_path[-2] if len(total_path) > 1 else None
        target_frames, last_node = target_videos[-1].get_n_frames(
            n_left, start=total_path[-1], last_position=last_node
        )
        frames += target_frames
        self.curr_node = last_node or total_path[-1]

        logger.trace(
            f"Path: {total_path} -> {self.curr_node}, path len: {total_distance}, "
            f"rest: {len(target_frames)}, total: {len(frames)}/{min_n}"
        )

        return frames

    def next_n_frames(
        self,
        num_frames: int,
        target_video_name: str = None,
        actions_name: List[str] | str = None,
        on_user_speech: bool = False,
        on_agent_speech: bool = False,
    ) -> List[Frame]:
        """Get the next n frames from the navigator.

        Args:
            num_frames: The number of frames to get
            target_video_name: The target video name. Keep the current video if None.
            actions_name: The actions before the target video.
        """
        if self.frame_buffer:
            video = self.videos.get(self.frame_buffer[0].video_name)
            if video:
                if (on_user_speech and video.stop_on_user_speech) or (
                    on_agent_speech and video.stop_on_agent_speech
                ):
                    self.reset_buffer()
                    logger.trace(
                        f"Stop on {video.video_name} because of {on_user_speech=} or "
                        f"{on_agent_speech=}"
                    )

        if num_frames <= 0:
            return []

        min_n = num_frames - len(self.frame_buffer)
        self.frame_buffer += self.collect_n_frames(
            min_n, target_video_name=target_video_name, actions_name=actions_name
        )
        frames = self.frame_buffer[:num_frames]
        self.frame_buffer = self.frame_buffer[num_frames:]
        return frames

    def filter_video_names(
        self, target_video: Optional[str], actions: Optional[List[str] | str]
    ) -> Tuple[str, List[str]]:
        """Filter the target video and actions."""
        if target_video:
            if not self.video_exists(target_video, is_action=False):
                logger.warning(f"Invalid video name: {target_video}")
                target_video = None

        if actions:
            if isinstance(actions, str):
                actions = [actions]
            valid_actions = []
            for action in actions:
                if self.video_exists(action, is_action=True):
                    valid_actions.append(action)
                else:
                    logger.warning(f"Invalid action name: {action}")
            actions = valid_actions
        return target_video, actions
