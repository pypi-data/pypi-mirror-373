from __future__ import annotations

from typing import Dict, Tuple
from PySide6.QtCore import QObject, Property
from PySide6.QtQml import QQmlPropertyMap


def _make_property_map(d: Dict[str, int]) -> QQmlPropertyMap:
    m = QQmlPropertyMap()
    for k, v in d.items():
        m.insert(k, int(v))
    return m


KEYPOINTS: Dict[str, int] = {
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

BONE_PAIRS: Dict[str, Tuple[int, int]] = {
    "Shoulders": (11, 12),
    "Hips": (23, 24),
    "TorsoLeft": (11, 23),
    "TorsoRight": (12, 24),
    "LeftUpperArm": (11, 13),
    "LeftForearm": (13, 15),
    "RightUpperArm": (12, 14),
    "RightForearm": (14, 16),
    "LeftThigh": (23, 25),
    "LeftShank": (25, 27),
    "RightThigh": (24, 26),
    "RightShank": (26, 28),
}

# Assign integer IDs to bones for QML enums; keep reverse map for runtime lookup
BONES: Dict[str, int] = {name: i for i, name in enumerate(BONE_PAIRS.keys())}
BONE_ID_TO_PAIR: Dict[int, Tuple[int, int]] = {i: BONE_PAIRS[name] for name, i in BONES.items()}

FIT_MODE: Dict[str, int] = {"PreserveAspectFit": 0, "Fill": 1, "FitWidth": 2, "FitHeight": 3}
FACE_STRATEGY: Dict[str, int] = {"EyesEars": 0, "EyesNose": 1, "BBoxFallback": 2}
FACE_ROTATION: Dict[str, int] = {"EarLine": 0, "EyeLine": 1, "None": 2}


class PoseConstants(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        # Backing fields
        self._Keypoint = _make_property_map(KEYPOINTS)
        self._Bone = _make_property_map(BONES)
        self._FitMode = _make_property_map(FIT_MODE)
        self._FaceStrategy = _make_property_map(FACE_STRATEGY)
        self._FaceRotation = _make_property_map(FACE_ROTATION)

    # QML-accessible read-only properties
    @Property(QObject, constant=True)
    def Keypoint(self) -> QObject:  # type: ignore[override]
        return self._Keypoint

    @Property(QObject, constant=True)
    def Bone(self) -> QObject:  # type: ignore[override]
        return self._Bone

    @Property(QObject, constant=True)
    def FitMode(self) -> QObject:  # type: ignore[override]
        return self._FitMode

    @Property(QObject, constant=True)
    def FaceStrategy(self) -> QObject:  # type: ignore[override]
        return self._FaceStrategy

    @Property(QObject, constant=True)
    def FaceRotation(self) -> QObject:  # type: ignore[override]
        return self._FaceRotation


__all__ = [
    "PoseConstants",
    "KEYPOINTS",
    "BONES",
    "BONE_ID_TO_PAIR",
    "FIT_MODE",
    "FACE_STRATEGY",
    "FACE_ROTATION",
]
