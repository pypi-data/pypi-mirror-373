from __future__ import annotations

from typing import Dict, Tuple
from PySide6.QtCore import QObject, Property


class KeypointEnum(QObject):
    """Container of MediaPipe Pose 33 landmark indices as QML-accessible constants.
    Usage from QML: Pose.Keypoint.RightWrist
    """

    # Indices based on MediaPipe Pose Landmarks v0.10
    _values = {
        # Face core
        "Nose": 0,
        "LeftEyeInner": 1,
        "LeftEye": 2,
        "LeftEyeOuter": 3,
        "RightEyeInner": 4,
        "RightEye": 5,
        "RightEyeOuter": 6,
        "LeftEar": 7,
        "RightEar": 8,
        "MouthLeft": 9,
        "MouthRight": 10,
        # Torso/Arms
        "LeftShoulder": 11,
        "RightShoulder": 12,
        "LeftElbow": 13,
        "RightElbow": 14,
        "LeftWrist": 15,
        "RightWrist": 16,
        "LeftPinky": 17,
        "RightPinky": 18,
        "LeftIndex": 19,
        "RightIndex": 20,
        "LeftThumb": 21,
        "RightThumb": 22,
        # Hips/Legs
        "LeftHip": 23,
        "RightHip": 24,
        "LeftKnee": 25,
        "RightKnee": 26,
        "LeftAnkle": 27,
        "RightAnkle": 28,
        "LeftHeel": 29,
        "RightHeel": 30,
        "LeftFootIndex": 31,
        "RightFootIndex": 32,
    }

    def __getattr__(self, name: str) -> int:
        if name in self._values:
            return int(self._values[name])
        raise AttributeError(name)

    # Expose as QML constants
    def _make_prop(name: str, value: int):  # type: ignore
        return Property(int, fget=lambda self, v=value: v, constant=True)

    locals().update({k: _make_prop(k, v) for k, v in _values.items()})


class BoneEnum(QObject):
    """Named bones mapping to landmark index pairs. QML constant ints.
    Use with PoseBoneAnchor; runtime pairs accessible via BONE_TO_PAIR.
    """

    # Assign sequential integer IDs
    _pairs: Dict[str, Tuple[int, int]] = {
        # Torso
        "Shoulders": (11, 12),
        "Hips": (23, 24),
        "TorsoLeft": (11, 23),
        "TorsoRight": (12, 24),
        # Arms
        "LeftUpperArm": (11, 13),
        "LeftForearm": (13, 15),
        "RightUpperArm": (12, 14),
        "RightForearm": (14, 16),
        # Legs
        "LeftThigh": (23, 25),
        "LeftShank": (25, 27),
        "RightThigh": (24, 26),
        "RightShank": (26, 28),
    }
    _ids: Dict[str, int] = {name: i for i, name in enumerate(_pairs.keys())}
    _id_to_pair: Dict[int, Tuple[int, int]] = {i: _pairs[name] for name, i in _ids.items()}

    def __getattr__(self, name: str) -> int:
        if name in self._ids:
            return int(self._ids[name])
        raise AttributeError(name)

    # Expose as QML constants
    def _make_prop(name: str, value: int):  # type: ignore
        return Property(int, fget=lambda self, v=value: v, constant=True)

    locals().update({k: _make_prop(k, v) for k, v in _ids.items()})

    @staticmethod
    def pair_for_id(bone_id: int) -> Tuple[int, int]:
        return BoneEnum._id_to_pair.get(int(bone_id), (-1, -1))


class FitModeEnum(QObject):
    _values = {"PreserveAspectFit": 0, "Fill": 1, "FitWidth": 2, "FitHeight": 3}

    def __getattr__(self, name: str) -> int:
        if name in self._values:
            return int(self._values[name])
        raise AttributeError(name)

    def _make_prop(name: str, value: int):  # type: ignore
        return Property(int, fget=lambda self, v=value: v, constant=True)

    locals().update({k: _make_prop(k, v) for k, v in _values.items()})


class FaceStrategyEnum(QObject):
    _values = {"EyesEars": 0, "EyesNose": 1, "BBoxFallback": 2}

    def __getattr__(self, name: str) -> int:
        if name in self._values:
            return int(self._values[name])
        raise AttributeError(name)

    def _make_prop(name: str, value: int):  # type: ignore
        return Property(int, fget=lambda self, v=value: v, constant=True)

    locals().update({k: _make_prop(k, v) for k, v in _values.items()})


class FaceRotationEnum(QObject):
    _values = {"EarLine": 0, "EyeLine": 1, "None": 2}

    def __getattr__(self, name: str) -> int:
        if name in self._values:
            return int(self._values[name])
        raise AttributeError(name)

    def _make_prop(name: str, value: int):  # type: ignore
        return Property(int, fget=lambda self, v=value: v, constant=True)

    locals().update({k: _make_prop(k, v) for k, v in _values.items()})


__all__ = [
    "KeypointEnum",
    "BoneEnum",
    "FitModeEnum",
    "FaceStrategyEnum",
    "FaceRotationEnum",
]
