from __future__ import annotations

from typing import Optional, List, Tuple

from PySide6.QtCore import QObject, Property, QRectF
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtQuick import QQuickPaintedItem

from .model import PeopleModel, KeypointObject


class PoseOverlay(QQuickPaintedItem):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._peopleModel: Optional[PeopleModel] = None
        self._visibilityThreshold = 0.3
        self._jointRadius = 3
        self._boneWidth = 2
        self._sourceWidth = 0
        self._sourceHeight = 0
        self.setFlag(QQuickPaintedItem.ItemHasContents, True)

    @Property(QObject)
    def peopleModel(self) -> Optional[PeopleModel]:
        return self._peopleModel

    @peopleModel.setter
    def peopleModel(self, m: Optional[QObject]) -> None:
        # Disconnect old signals
        if self._peopleModel is not None:
            for sig in [self._peopleModel.dataChanged, self._peopleModel.modelReset, self._peopleModel.rowsInserted, self._peopleModel.rowsRemoved]:
                try:
                    sig.disconnect(self.update)
                except Exception:
                    pass
        self._peopleModel = m if isinstance(m, PeopleModel) else None
        # Connect new signals
        if self._peopleModel is not None:
            for sig in [self._peopleModel.dataChanged, self._peopleModel.modelReset, self._peopleModel.rowsInserted, self._peopleModel.rowsRemoved, self._peopleModel.countChanged]:
                try:
                    sig.connect(self.update)
                except Exception:
                    pass
        self.update()

    @Property(float)
    def visibilityThreshold(self) -> float:
        return self._visibilityThreshold

    @visibilityThreshold.setter
    def visibilityThreshold(self, v: float) -> None:
        self._visibilityThreshold = float(v)
        self.update()

    @Property(int)
    def jointRadius(self) -> int:
        return self._jointRadius

    @jointRadius.setter
    def jointRadius(self, r: int) -> None:
        self._jointRadius = int(r)
        self.update()

    @Property(int)
    def boneWidth(self) -> int:
        return self._boneWidth

    @boneWidth.setter
    def boneWidth(self, w: int) -> None:
        self._boneWidth = int(w)
        self.update()

    @Property(int)
    def sourceWidth(self) -> int:
        return self._sourceWidth

    @sourceWidth.setter
    def sourceWidth(self, w: int) -> None:
        self._sourceWidth = int(w)
        self.update()

    @Property(int)
    def sourceHeight(self) -> int:
        return self._sourceHeight

    @sourceHeight.setter
    def sourceHeight(self, h: int) -> None:
        self._sourceHeight = int(h)
        self.update()

    def paint(self, painter: QPainter) -> None:  # type: ignore[override]
        if not self._peopleModel:
            return
        painter.setRenderHint(QPainter.Antialiasing, True)
        bonePen = QPen(QColor("#4FC3F7"), self._boneWidth)
        jointPen = QPen(QColor("#FF7043"), 1)
        jointBrush = QColor("#FF7043")

        connections = self._mediapipe_connections()
        w = max(1.0, float(self.width()))
        h = max(1.0, float(self.height()))
        sw = float(self._sourceWidth)
        sh = float(self._sourceHeight)
        if sw <= 0 or sh <= 0:
            return
        # PreserveAspectFit mapping: scale to fit and center with letterboxing
        scale = min(w / sw, h / sh)
        offx = (w - sw * scale) * 0.5
        offy = (h - sh * scale) * 0.5

        # PeopleModel.count is a Qt property, not a callable
        try:
            count = int(getattr(self._peopleModel, 'count'))
        except Exception:
            count = 0
        for i in range(count):
            person = self._peopleModel.personAt(i)
            if not person:
                continue
            # Robustly extract keypoints list from QObject property, even if Python sees a Qt Property descriptor
            try:
                kps = getattr(person, 'keypoints', None)
                if not isinstance(kps, list):
                    # Fallback to QObject.property access
                    kps = person.property('keypoints') if hasattr(person, 'property') else None
            except Exception:
                kps = None
            if not isinstance(kps, list):
                # Can't draw without a proper list of keypoints
                continue

            # Draw bones
            painter.setPen(bonePen)
            for a, b in connections:
                if a < len(kps) and b < len(kps):
                    ka: KeypointObject = kps[a]  # type: ignore[assignment]
                    kb: KeypointObject = kps[b]  # type: ignore[assignment]
                    if ka.confidence >= self._visibilityThreshold and kb.confidence >= self._visibilityThreshold:
                        painter.drawLine(offx + ka.x * scale, offy + ka.y * scale,
                                         offx + kb.x * scale, offy + kb.y * scale)

            # Draw joints
            painter.setPen(jointPen)
            painter.setBrush(jointBrush)
            r = float(self._jointRadius)
            for kp in kps:
                if kp.confidence >= self._visibilityThreshold:
                    painter.drawEllipse(QRectF(offx + kp.x * scale - r,
                                               offy + kp.y * scale - r,
                                               r * 2, r * 2))

    def _mediapipe_connections(self) -> List[Tuple[int, int]]:
        return [
            (11, 12),  # shoulders
            (11, 13), (13, 15),  # left arm
            (12, 14), (14, 16),  # right arm
            (23, 24),  # hips
            (11, 23), (12, 24),  # torso
            (23, 25), (25, 27),  # left leg
            (24, 26), (26, 28),  # right leg
        ]
