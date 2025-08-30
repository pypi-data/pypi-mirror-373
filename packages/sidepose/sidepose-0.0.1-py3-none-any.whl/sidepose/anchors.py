from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Property
from PySide6.QtQuick import QQuickItem

from .anchor_base import PoseAnchorBase
from .model import PersonObject, KeypointObject
from .constants import BONE_ID_TO_PAIR


class PoseKeypointAnchor(PoseAnchorBase):
    """Positions itself at a given keypoint (landmark).
    Children (Image, AnimatedImage, Video, etc.) can anchor to this item (e.g., anchors.centerIn: parent).
    It performs aspect-aware mapping internally using its parent's size and the processor's frame size.
    """

    def __init__(self, parent: Optional[QQuickItem] = None) -> None:
        super().__init__(parent)
        self._joint: int = 0  # MediaPipe index
        # Give it a minimal size so children can center anchor
        self.setWidth(1)
        self.setHeight(1)

    # Inherit processor/personIndex/minConfidence/fitMode from base

    def _get_joint(self) -> int:
        return self._joint

    def _set_joint(self, j: int) -> None:
        self._joint = max(0, int(j))
        self._onTick()

    # Back-compat: 'joint' property name
    joint = Property(int, fget=_get_joint, fset=_set_joint)

    # Preferred: 'keypoint' property name
    def _get_keypoint(self) -> int:
        return self._joint

    def _set_keypoint(self, j: int) -> None:
        self._set_joint(j)

    keypoint = Property(int, fget=_get_keypoint, fset=_set_keypoint)

    def _update_geometry(self, person: Optional[PersonObject]) -> None:
        if person is None:
            self.setVisible(False)
            return
        kp = self._kp(person, self._joint)
        if kp is None or kp.confidence < self._minConfidence:
            self.setVisible(False)
            return
        scale, offx, offy, mapW, mirror = self._map_ex()
        if mirror and mapW > 0:
            mx = offx + (mapW - kp.x * scale)
        else:
            mx = offx + kp.x * scale
        my = offy + kp.y * scale
        self.setX(mx - self.width() * 0.5)
        self.setY(my - self.height() * 0.5)
        self.setVisible(True)


# Backwards-compatible alias for existing QML code
class PoseJointAnchor(PoseKeypointAnchor):
    pass


class PoseBoneAnchor(PoseAnchorBase):
    """Positions and rotates a container along a named bone; children can fill/stretch it."""

    def __init__(self, parent: Optional[QQuickItem] = None) -> None:
        super().__init__(parent)
        self._bone: int = 0  # maps to BONE_ID_TO_PAIR
        self.setHeight(20)
    # inherit processor/personIndex/minConfidence/fitMode

    def _get_bone(self) -> int:
        return self._bone

    def _set_bone(self, b: int) -> None:
        self._bone = max(0, int(b))
        self._onTick()

    bone = Property(int, fget=_get_bone, fset=_set_bone)

    def _update_geometry(self, person: Optional[PersonObject]) -> None:
        if person is None:
            self.setVisible(False)
            return
        a_idx, b_idx = BONE_ID_TO_PAIR.get(int(self._bone), (-1, -1))
        ka = self._kp(person, a_idx)
        kb = self._kp(person, b_idx)
        if (ka is None or kb is None or
                min(ka.confidence, kb.confidence) < self._minConfidence):
            self.setVisible(False)
            return
        dx = kb.x - ka.x
        dy = kb.y - ka.y
        length = (dx * dx + dy * dy) ** 0.5
        mx = (ka.x + kb.x) * 0.5
        my = (ka.y + kb.y) * 0.5
        scale, offx, offy, mapW, mirror = self._map_ex()
        self.setWidth(max(1.0, length * scale))
        import math
        if mirror and mapW > 0:
            px = offx + (mapW - mx * scale)
            self.setRotation(-math.degrees(math.atan2(dy, dx)))
        else:
            px = offx + mx * scale
            self.setRotation(math.degrees(math.atan2(dy, dx)))
        self.setX(px - self.width() * 0.5)
        self.setY(offy + my * scale - self.height() * 0.5)
        self.setVisible(True)


class PoseFaceAnchor(PoseAnchorBase):
    """Positions a rectangle over the face with optional rotation and scale."""

    def __init__(self, parent: Optional[QQuickItem] = None) -> None:
        super().__init__(parent)
        self._strategy: int = 0  # 0: EyesEars, 1: EyesNose, 2: BBoxFallback
        self._rotationFrom: int = 0  # 0: EarLine, 1: EyeLine, 2: None
        self._scaleFactor: float = 1.0
        # fitMode and others inherited

    def _get_strategy(self) -> int:
        return self._strategy

    def _set_strategy(self, v: int) -> None:
        self._strategy = int(v)
        self._onTick()

    strategy = Property(int, fget=_get_strategy, fset=_set_strategy)

    def _get_rotationFrom(self) -> int:
        return self._rotationFrom

    def _set_rotationFrom(self, v: int) -> None:
        self._rotationFrom = int(v)
        self._onTick()

    rotationFrom = Property(int, fget=_get_rotationFrom, fset=_set_rotationFrom)

    def _get_scaleFactor(self) -> float:
        return self._scaleFactor

    def _set_scaleFactor(self, v: float) -> None:
        self._scaleFactor = float(v)
        self._onTick()

    scaleFactor = Property(float, fget=_get_scaleFactor, fset=_set_scaleFactor)

    def _update_geometry(self, person: Optional[PersonObject]) -> None:
        if person is None:
            self.setVisible(False)
            return
        # indices
        L_EYE_OUT, R_EYE_OUT, L_EAR, R_EAR, NOSE = 3, 6, 7, 8, 0
        le = self._kp(person, L_EYE_OUT)
        re = self._kp(person, R_EYE_OUT)
        leEar = self._kp(person, L_EAR)
        reEar = self._kp(person, R_EAR)
        nose = self._kp(person, NOSE)

        def ok(k: Optional[KeypointObject]) -> bool:
            return k is not None and k.confidence >= self._minConfidence

        # center
        if self._strategy == 1 and ok(le) and ok(re) and ok(nose):
            cx = (le.x + re.x + nose.x) / 3.0
            cy = (le.y + re.y + nose.y) / 3.0
        else:
            if ok(le) and ok(re):
                cx = (le.x + re.x) * 0.5
                cy = (le.y + re.y) * 0.5
            elif ok(nose):
                cx, cy = nose.x, nose.y
            else:
                try:
                    bb = person.bbox
                    cx = float(bb.cx)
                    cy = float(bb.cy)
                except Exception:
                    cx, cy = 0.0, 0.0

        # size from ear distance or bbox
        import math
        if ok(leEar) and ok(reEar):
            face_w = math.hypot(reEar.x - leEar.x, reEar.y - leEar.y) * 1.2
        else:
            try:
                bb = person.bbox
                face_w = float(bb.width) * 0.6
            except Exception:
                face_w = 0.0
        face_h = face_w * 0.6

        # rotation
        if self._rotationFrom == 2:
            angle_deg = 0.0
        else:
            # Note: MediaPipe landmark names are anatomical (subject-left/right).
            # In image coordinates (not mirrored), subject-left appears on the viewer's right.
            # To get a 0-degree baseline and correct tilt direction on screen,
            # we form the vector from subject-right to subject-left (screen-left to screen-right).
            if self._rotationFrom == 1 and ok(le) and ok(re):
                ax, ay, bx, by = re.x, re.y, le.x, le.y  # Eye line: Right -> Left
            elif ok(leEar) and ok(reEar):
                ax, ay, bx, by = reEar.x, reEar.y, leEar.x, leEar.y  # Ear line: Right -> Left
            else:
                ax, ay, bx, by = 0.0, 0.0, 1.0, 0.0
            angle_deg = math.degrees(math.atan2(by - ay, bx - ax))

        scale, offx, offy, mapW, mirror = self._map_ex()
        wpx = max(1.0, face_w * self._scaleFactor * scale)
        hpx = max(1.0, face_h * self._scaleFactor * scale)
        self.setWidth(wpx)
        self.setHeight(hpx)
        if mirror and mapW > 0:
            px = offx + (mapW - cx * scale)
            # flip rotation sign when mirrored
            angle_deg = -angle_deg
        else:
            px = offx + cx * scale
        self.setX(px - wpx * 0.5)
        self.setY(offy + cy * scale - hpx * 0.5)
        self.setRotation(angle_deg)
        self.setVisible(True)
