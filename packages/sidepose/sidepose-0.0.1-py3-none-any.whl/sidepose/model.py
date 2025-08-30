from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot, Qt, QAbstractListModel, QModelIndex


class KeypointObject(QObject):
    def __init__(self, x: float = 0.0, y: float = 0.0, confidence: float = 0.0, visibility: Optional[float] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._x = float(x)
        self._y = float(y)
        self._confidence = float(confidence)
        self._visibility = float(visibility) if visibility is not None else None

    @Property(float, constant=True)
    def x(self) -> float:
        return self._x

    @Property(float, constant=True)
    def y(self) -> float:
        return self._y

    @Property(float, constant=True)
    def confidence(self) -> float:
        return self._confidence

    @Property(float, constant=True)
    def visibility(self) -> float:
        return -1.0 if self._visibility is None else float(self._visibility)


class BBoxObject(QObject):
    def __init__(self, x1: float = 0.0, y1: float = 0.0, x2: float = 0.0, y2: float = 0.0, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._x1 = float(x1)
        self._y1 = float(y1)
        self._x2 = float(x2)
        self._y2 = float(y2)

    @Property(float, constant=True)
    def x1(self) -> float:
        return self._x1

    @Property(float, constant=True)
    def y1(self) -> float:
        return self._y1

    @Property(float, constant=True)
    def x2(self) -> float:
        return self._x2

    @Property(float, constant=True)
    def y2(self) -> float:
        return self._y2

    @Property(float, constant=True)
    def width(self) -> float:
        return max(0.0, self._x2 - self._x1)

    @Property(float, constant=True)
    def height(self) -> float:
        return max(0.0, self._y2 - self._y1)

    @Property(float, constant=True)
    def cx(self) -> float:
        return (self._x1 + self._x2) / 2.0

    @Property(float, constant=True)
    def cy(self) -> float:
        return (self._y1 + self._y2) / 2.0


class PersonObject(QObject):
    changed = Signal()

    def __init__(self, pid: Optional[int] = None, score: float = 0.0, bbox: Optional[BBoxObject] = None, keypoints: Optional[List[KeypointObject]] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._id: Optional[int] = pid
        self._score: float = float(score)
        self._bbox: BBoxObject = bbox if bbox is not None else BBoxObject()
        self._keypoints: List[KeypointObject] = keypoints if keypoints is not None else []

    @Property(int, notify=changed)
    def id(self) -> int:
        return -1 if self._id is None else int(self._id)

    @Property(float, notify=changed)
    def score(self) -> float:
        return self._score

    @Property(QObject, notify=changed)
    def bbox(self) -> BBoxObject:
        return self._bbox

    @Property('QVariantList', notify=changed)
    def keypoints(self):
        return list(self._keypoints)


class PoseFrameObject(QObject):
    def __init__(self, width: int, height: int, timestamp: float, people: List[PersonObject], parent: Optional[QObject] = None):
        super().__init__(parent)
        self._width = int(width)
        self._height = int(height)
        self._timestamp = float(timestamp)
        self._people = list(people)

    @Property(int, constant=True)
    def width(self) -> int:
        return self._width

    @Property(int, constant=True)
    def height(self) -> int:
        return self._height

    @Property(float, constant=True)
    def timestamp(self) -> float:
        return self._timestamp

    @Property('QVariantList', constant=True)
    def people(self):
        return list(self._people)


class TelemetryObject(QObject):
    updated = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._fps = 0.0
        self._captureMs = 0.0
        self._preprocessMs = 0.0
        self._inferMs = 0.0
        self._postMs = 0.0
        self._drawMs = 0.0

    @Property(float, notify=updated)
    def fps(self) -> float:
        return self._fps

    def setFps(self, v: float) -> None:
        if self._fps != v:
            self._fps = float(v)
            self.updated.emit()

    @Property(float, notify=updated)
    def captureMs(self) -> float:
        return self._captureMs

    @Property(float, notify=updated)
    def preprocessMs(self) -> float:
        return self._preprocessMs

    @Property(float, notify=updated)
    def inferMs(self) -> float:
        return self._inferMs

    @Property(float, notify=updated)
    def postMs(self) -> float:
        return self._postMs

    @Property(float, notify=updated)
    def drawMs(self) -> float:
        return self._drawMs


class PeopleModel(QAbstractListModel):
    PersonRole = Qt.UserRole + 1
    IdRole = Qt.UserRole + 2
    ScoreRole = Qt.UserRole + 3

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._people: List[PersonObject] = []
        self._count_cache = 0

    # Notifiable count property so QML bindings update
    countChanged = Signal()

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._people)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        if parent.isValid():
            return 0
        return len(self._people)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not (0 <= index.row() < len(self._people)):
            return None
        person = self._people[index.row()]
        if role == PeopleModel.PersonRole:
            return person
        if role == PeopleModel.IdRole:
            return person.id()
        if role == PeopleModel.ScoreRole:
            return person.score()
        return None

    def roleNames(self):  # type: ignore[override]
        return {
            PeopleModel.PersonRole: b"person",
            PeopleModel.IdRole: b"id",
            PeopleModel.ScoreRole: b"score",
        }

    # Note: Do not expose a method named 'count' to avoid shadowing the property above.

    def setPeople(self, people: List[PersonObject]) -> None:
        self.beginResetModel()
        self._people = list(people)
        self.endResetModel()
        if self._count_cache != len(self._people):
            self._count_cache = len(self._people)
            self.countChanged.emit()

    @Slot(int, result=QObject)
    def personAt(self, i: int):
        if 0 <= i < len(self._people):
            return self._people[i]
        return None
