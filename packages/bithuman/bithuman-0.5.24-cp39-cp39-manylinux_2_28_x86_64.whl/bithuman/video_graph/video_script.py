"""Definition of the script for the video graph."""

from __future__ import annotations

import copy
import json
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml
from dataclasses_json import dataclass_json
from loguru import logger

from ..api import Emotion, EmotionPrediction
from ..config import Settings
from .driver_video import DriverVideo, LoopingVideo, SingleActionVideo

VIDEO_EXTS = [".mp4", ".mov", ".avi"]


@dataclass_json
@dataclass
class EmotionToVideo:
    """Dataclass for emotion to video mapping.

    Attributes:
        emotion: The emotion.
        video_name: The video name.
        threshold: The threshold for the emotion.
        actions: The actions before the video.
    """

    emotion: Emotion
    video_name: str
    threshold: float = 0.1
    actions: List[str] = field(default_factory=list)


@dataclass_json
@dataclass
class IdleAction:
    """Dataclass for idle action.

    Attributes:
        actions: The actions for the idle video.
        interval: Play the action every interval seconds
            or randomly between the interval.
    """

    actions: List[str] = field(default_factory=list)
    interval: float | Tuple[float, float] = 60

    @property
    def min_interval(self) -> float:
        return self.interval if isinstance(self.interval, float) else self.interval[0]


@dataclass_json
@dataclass
class VideoScript:
    default_video: Optional[str] = None
    action_hi_video: Optional[str] = None
    emotions_map: List[EmotionToVideo] = field(default_factory=list)
    idle_video: Optional[str] = None
    idle_actions: List[IdleAction] = field(default_factory=list)
    FPS: float = 25
    BACK_TO_IDLE: float = 10  # back to idle after 10 seconds

    def __post_init__(self):
        self.last_nonidle_frame = 0
        self.last_video_name = None

        self.update_index()

    def update_index(self):
        # index the videos by emotion and group by threshold
        emotions_map_index: Dict[Emotion, Dict[float, List[EmotionToVideo]]] = {}
        for e2v in self.emotions_map:
            emotions_map_index.setdefault(e2v.emotion, defaultdict(list))[
                e2v.threshold
            ].append(e2v)

        # sort the videos by threshold in descending order
        for emotion in emotions_map_index:
            emotions_map_index[emotion] = OrderedDict(
                sorted(
                    emotions_map_index[emotion].items(),
                    key=lambda x: x[0],
                    reverse=True,
                )
            )
        self.emotions_map_index = emotions_map_index

        # Next idle action, randomly selected from the idle actions
        self.set_next_idle_action()

    def set_next_idle_action(self, next_idle_action: IdleAction | None = None):
        """Set the next idle action.

        Args:
            next_idle_action: The next idle action. If None, randomly select one.
        """
        if not next_idle_action:
            next_idle_action = (
                np.random.choice(self.idle_actions) if self.idle_actions else None
            )

        self.next_idle_action = next_idle_action
        if not self.next_idle_action:
            self.next_idle_action_interval = None
            return

        if isinstance(self.next_idle_action.interval, (tuple, list)):
            interval = np.random.uniform(*self.next_idle_action.interval)
        else:
            interval = self.next_idle_action.interval
        self.next_idle_action_interval = interval

    def get_video_and_actions(
        self,
        curr_frame_index: int,
        emotions: List[EmotionPrediction] = None,
        text: str = None,
        is_idle: bool = False,
        settings: Settings = None,
    ) -> Tuple[str, List[str], bool]:
        """Get the videos for the emotion."""
        is_idle = is_idle and not emotions  # idle only when no emotion

        reset_action = False
        video_name, actions = None, []
        if is_idle:
            idle_time = (curr_frame_index - self.last_nonidle_frame) / self.FPS

            # Back to the default video if idle for a long time
            if idle_time >= self.BACK_TO_IDLE:
                next_idle_video = (
                    self.idle_video
                    if settings and settings.LIVA_IDEL_VIDEO_ENABLED
                    else None
                )
                # TODO: random select one idle video from a list
                video_name = next_idle_video or self.default_video

            # Play a random idle action if the idle time is long enough
            if self.next_idle_action and idle_time >= self.next_idle_action_interval:
                # Play the idle action, then reset the next idle action
                actions = self.next_idle_action.actions
                reset_action = True
                self.set_next_idle_action()
                self.last_nonidle_frame = curr_frame_index
        else:
            self.last_nonidle_frame = curr_frame_index

            # Get the video for the emotion
            if emotions:
                # Ignore neutral if there are other emotions > 0.2
                if len(emotions) > 1:
                    if (
                        emotions[0].emotion == Emotion.NEUTRAL
                        and emotions[1].score > 0.2
                    ):
                        emotions = emotions[1:]

                top_emotion = emotions[0]
                for threshold, e2v_list in self.emotions_map_index.get(
                    top_emotion.emotion, {}
                ).items():
                    if top_emotion.score >= threshold and e2v_list:
                        # Randomly select one video from the list
                        e2v: EmotionToVideo = np.random.choice(e2v_list)
                        video_name, actions = e2v.video_name, e2v.actions
                        break
            if (
                text
                and self.action_hi_video
                and settings
                and settings.LIVA_AUTO_SAY_HI
                and self.action_hi_video not in actions
            ):
                # Detect Hello, hi, Bye, Goodbye
                say_hi = False
                text = text.lower()
                for word in ["hello", "hi ", "bye", "goodbye"]:
                    if text.startswith(word):
                        say_hi = True
                        break
                if say_hi:
                    actions = [self.action_hi_video] + actions

            if (
                not video_name
                and self.idle_video
                and self.last_video_name == self.idle_video
            ):
                # Back to the default video if nonidle and no video is selected
                video_name = self.default_video

        self.last_video_name = video_name
        return video_name, actions, reset_action


@dataclass_json
@dataclass
class VideoConfig:
    name: str
    video_file: str
    video_type: str = "LoopingVideo"
    stride: int = 10
    loop_between: Tuple[int, int] = (0, -1)
    remove_nodes: Optional[List[int]] = None
    transition_frames: Optional[List[int]] = None
    action_frame: int = -1
    single_direction: bool = False
    adding_kwargs: Dict = field(default_factory=dict)
    lip_sync_required: bool = True
    stop_on_user_speech: bool = False
    stop_on_agent_speech: bool = False

    def load_video(self) -> DriverVideo:
        if self.video_type == "LoopingVideo":
            video = LoopingVideo(
                name=self.name,
                video_path=self.video_file,
                stride=self.stride,
                single_direction=self.single_direction,
                stop_on_user_speech=self.stop_on_user_speech,
                stop_on_agent_speech=self.stop_on_agent_speech,
                loop_between=self.loop_between,
                lip_sync_required=self.lip_sync_required,
            )
        elif self.video_type == "SingleActionVideo":
            video = SingleActionVideo(
                name=self.name,
                video_path=self.video_file,
                single_direction=self.single_direction,
                stop_on_user_speech=self.stop_on_user_speech,
                stop_on_agent_speech=self.stop_on_agent_speech,
                transition_frames=self.transition_frames,
                action_frame=self.action_frame,
                lip_sync_required=self.lip_sync_required,
            )
        else:
            raise ValueError(f"Unknown video type: {self.video_type}")

        if self.lip_sync_required and not video.video_data_path:
            raise ValueError(
                f"Lip sync is required for video {self.name}, but no video data path is provided"
            )

        if self.remove_nodes:
            video.remove_nodes(frame_indices=self.remove_nodes)
        return video


@dataclass_json
@dataclass
class VideoConfigs:
    videos: List[VideoConfig]
    videos_script: Optional[VideoScript] = field(default_factory=VideoScript)
    talking_face_configs: Optional[Dict[str, Any]] = None

    def load_videos(
        self, video_root: str = None, verbose: bool = True
    ) -> List["DriverVideo"]:
        if video_root:
            video_configs = copy.deepcopy(self.videos)
            video_root = Path(video_root)
            for video in video_configs:
                video.video_file = str(video_root / video.video_file)
        else:
            video_configs = self.videos

        return [video_config.load_video() for video_config in video_configs]

    @classmethod
    def from_videofolder(cls, video_folder: str) -> "VideoConfigs":
        """Create a VideoConfigs object with a video folder."""
        video_files = [
            p
            for p in Path(video_folder).iterdir()
            if p.suffix.lower() in VIDEO_EXTS and not p.name.startswith(".")
        ]
        if len(video_files) == 0:
            raise ValueError(f"No video files found in {video_folder}")
        if len(video_files) > 1:
            raise ValueError(
                f"Multiple video files found in {video_folder}: {video_files}"
            )
        video_file = video_files[0]
        return cls(
            videos=[VideoConfig(name=video_file.stem, video_file=str(video_file))]
        )

    @classmethod
    def from_videofile(
        cls, video_file: str, inference_data_file: str = None
    ) -> "VideoConfigs":
        """Create a VideoConfigs object with a video file."""
        return cls(
            videos=[
                VideoConfig(
                    name=Path(video_file).stem,
                    video_file=str(video_file),
                    inference_data_file=inference_data_file,
                )
            ]
        )

    @classmethod
    def from_yaml(cls, file_path: str) -> "VideoConfigs":
        """Load the video configs from a YAML file."""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def to_yaml(self, file_path: str) -> None:
        """Save the video configs to a YAML file."""
        with open(file_path, "w") as f:
            data = json.loads(self.to_json())
            yaml.dump(data, f, sort_keys=False)

    def update_runtime_configs(self, settings: Settings):
        """Update the runtime configs."""
        if not settings.ALLOW_VIDEO_SCRIPT_UPDATE:
            logger.info(
                "Video script update is disabled, skip updating runtime configs."
            )
            return

        configs = self.talking_face_configs or {}
        fails, success = {}, {}
        for k, v in configs.items():
            if hasattr(settings, k):
                setattr(settings, k, v)
                success[k] = v
            else:
                fails[k] = v
        logger.info(f"Updated runtime configs from model: {success}")
        if fails:
            logger.warning(f"Runtime configs not found in settings: {fails}")
