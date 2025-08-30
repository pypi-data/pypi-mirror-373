from __future__ import annotations

from typing import List, Optional

try:
    import numpy as np
    import mediapipe as mp
    from mediapipe.tasks.python import vision as mp_vision
    from mediapipe.tasks.python.core.base_options import BaseOptions
    _HAVE_MP = True
except Exception:  # pragma: no cover - optional dependency
    _HAVE_MP = False
    np = None  # type: ignore


class MediaPipePoseBackend:
    def __init__(self, model_path: str, num_poses: int = 1,
                 min_detection_confidence: float = 0.5,
                 min_presence_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 use_gpu: bool = False):
        if not _HAVE_MP:
            raise RuntimeError("mediapipe is not installed")
        base_opts = BaseOptions(
            model_asset_path=model_path,
            delegate=BaseOptions.Delegate.GPU if use_gpu else BaseOptions.Delegate.CPU,
        )
        options = mp_vision.PoseLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=num_poses,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_segmentation_masks=False,
        )
        self._detector = mp_vision.PoseLandmarker.create_from_options(options)

    def detect(self, rgb_image, timestamp_ms: int):
        # rgb_image: HxWx3 uint8
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        return self._detector.detect_for_video(image, timestamp_ms)
