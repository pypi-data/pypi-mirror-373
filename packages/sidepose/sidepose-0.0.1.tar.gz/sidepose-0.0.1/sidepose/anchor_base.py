from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Property
from PySide6.QtQuick import QQuickItem

from .controller import PoseController
from .model import PeopleModel, PersonObject, KeypointObject
from .mapping import compute_scale_offset


class PoseAnchorBase(QQuickItem):
    """Shared behavior for pose anchors: processor wiring, mapping, person access.
    Subclasses must implement _update_geometry(person: Optional[PersonObject]) -> None
    and call self.setVisible appropriately.
    """

    def __init__(self, parent: Optional[QQuickItem] = None) -> None:
        super().__init__(parent)
        self._processor: Optional[PoseController] = None
        self._personIndex: int = 0
        self._minConfidence: float = 0.5
        self._fitMode: int = 0
        # Optional explicit mapping rect (e.g., VideoOutput.contentRect)
        self._mapX = -1.0
        self._mapY = -1.0
        self._mapW = -1.0
        self._mapH = -1.0
        # React to our own and parent's size changes
        try:
            self.widthChanged.connect(self._onTick)
            self.heightChanged.connect(self._onTick)
        except Exception:
            pass

    def _get_processor(self) -> Optional[QObject]:
        return self._processor

    def _set_processor(self, p: Optional[QObject]) -> None:
        # disconnect old
        if self._processor is not None:
            try:
                self._processor.telemetryUpdated.disconnect(self._onTick)
                self._processor.frameSizeChanged.disconnect(self._onTick)
            except Exception:
                pass
            try:
                m = self._processor.peopleModel
                m.modelReset.disconnect(self._onTick)
                m.rowsInserted.disconnect(self._onTick)
                m.rowsRemoved.disconnect(self._onTick)
                m.countChanged.disconnect(self._onTick)
            except Exception:
                pass
        self._processor = p if isinstance(p, PoseController) else None
        # connect new
        if self._processor is not None:
            try:
                self._processor.telemetryUpdated.connect(self._onTick)
                self._processor.frameSizeChanged.connect(self._onTick)
                m = self._processor.peopleModel
                m.modelReset.connect(self._onTick)
                m.rowsInserted.connect(self._onTick)
                m.rowsRemoved.connect(self._onTick)
                m.countChanged.connect(self._onTick)
            except Exception:
                pass
        self._onTick()

    processor = Property(QObject, fget=_get_processor, fset=_set_processor)

    def _get_personIndex(self) -> int:
        return self._personIndex

    def _set_personIndex(self, i: int) -> None:
        self._personIndex = max(0, int(i))
        self._onTick()

    personIndex = Property(int, fget=_get_personIndex, fset=_set_personIndex)

    def _get_minConfidence(self) -> float:
        return self._minConfidence

    def _set_minConfidence(self, v: float) -> None:
        self._minConfidence = float(v)
        self._onTick()

    minConfidence = Property(float, fget=_get_minConfidence, fset=_set_minConfidence)

    def _get_fitMode(self) -> int:
        return self._fitMode

    def _set_fitMode(self, m: int) -> None:
        self._fitMode = int(m)
        self._onTick()

    fitMode = Property(int, fget=_get_fitMode, fset=_set_fitMode)

    # Optional mapping rect properties
    def _get_mapX(self) -> float:
        return self._mapX

    def _set_mapX(self, v: float) -> None:
        self._mapX = float(v)
        self._onTick()

    mapX = Property(float, fget=_get_mapX, fset=_set_mapX)

    def _get_mapY(self) -> float:
        return self._mapY

    def _set_mapY(self, v: float) -> None:
        self._mapY = float(v)
        self._onTick()

    mapY = Property(float, fget=_get_mapY, fset=_set_mapY)

    def _get_mapWidth(self) -> float:
        return self._mapW

    def _set_mapWidth(self, v: float) -> None:
        self._mapW = float(v)
        self._onTick()

    mapWidth = Property(float, fget=_get_mapWidth, fset=_set_mapWidth)

    def _get_mapHeight(self) -> float:
        return self._mapH

    def _set_mapHeight(self, v: float) -> None:
        self._mapH = float(v)
        self._onTick()

    mapHeight = Property(float, fget=_get_mapHeight, fset=_set_mapHeight)

    def _person(self) -> Optional[PersonObject]:
        proc = self._processor
        if proc is None:
            return None
        try:
            model: PeopleModel = proc.peopleModel  # type: ignore[attr-defined]
            return model.personAt(self._personIndex)
        except Exception:
            return None

    def _kp(self, person: Optional[PersonObject], idx: int) -> Optional[KeypointObject]:
        if person is None or idx < 0:
            return None
        try:
            kps = person.keypoints
            if isinstance(kps, list) and idx < len(kps):
                return kps[idx]
        except Exception:
            pass
        return None

    def _mapping(self) -> tuple[float, float, float]:
        proc = self._processor
        if proc is None:
            return 1.0, 0.0, 0.0
        try:
            sw = int(getattr(proc, 'frameWidth', 0))
            sh = int(getattr(proc, 'frameHeight', 0))
        except Exception:
            sw, sh = 0, 0
        if sw <= 0 or sh <= 0:
            return 1.0, 0.0, 0.0
        # 1) Explicit rect wins
        if self._mapW > 0 and self._mapH > 0 and self._mapX >= 0 and self._mapY >= 0:
            scale = float(self._mapW) / float(sw)
            return scale, float(self._mapX), float(self._mapY)
        # 2) Walk up ancestors: prefer a PoseSpace-like parent exposing map rect
        it = self.parentItem()
        sized_item = None
        mirror = False
        while it is not None:
            try:
                mw = float(it.property('mapWidth'))
                mh = float(it.property('mapHeight'))
                mx = float(it.property('mapX'))
                my = float(it.property('mapY'))
                try:
                    mirror = bool(it.property('mirror'))
                except Exception:
                    pass
                if mw > 0 and mh > 0:
                    scale = mw / float(sw)
                    # Mirror is handled by anchors in their own geometry (by flipping x around map rect)
                    return scale, mx, my
            except Exception:
                pass
            try:
                iw = float(it.property('width'))
                ih = float(it.property('height'))
                if iw > 0 and ih > 0 and sized_item is None:
                    sized_item = (iw, ih)
            except Exception:
                pass
            it = it.parentItem()
        # 3) Fallback: compute from nearest sized ancestor or our own size
        if sized_item is None:
            try:
                sized_item = (float(self.property('width')), float(self.property('height')))
            except Exception:
                sized_item = (0.0, 0.0)
        w, h = sized_item
        if w <= 0 or h <= 0:
            return 1.0, 0.0, 0.0
        return compute_scale_offset(w, h, sw, sh, self._fitMode)

    def _map_ex(self) -> tuple[float, float, float, float, bool]:
        """Extended mapping: returns (scale, offx, offy, mapWidth, mirror).
        - mapWidth is derived from source width and scale.
        - mirror is detected from an ancestor (e.g., PoseSpace.mirror).
        """
        scale, offx, offy = self._mapping()
        # Derive map width from source width and scale
        sw = 0
        try:
            if self._processor is not None:
                sw = int(getattr(self._processor, 'frameWidth', 0))
        except Exception:
            sw = 0
        mapW = float(sw) * float(scale) if sw > 0 else 0.0
        # Detect mirror flag from ancestors (first true wins)
        mirror = False
        it = self.parentItem()
        while it is not None:
            try:
                if bool(it.property('mirror')):
                    mirror = True
                    break
            except Exception:
                pass
            it = it.parentItem()
        return scale, offx, offy, mapW, mirror

    def _onTick(self, *args) -> None:  # Qt slot signature friendly
        self._update_geometry(self._person())

    def _update_geometry(self, person: Optional[PersonObject]) -> None:  # abstract
        raise NotImplementedError
    # When parent changes, re-attach to size change notifications

    def itemChange(self, change: QQuickItem.ItemChange, value):  # type: ignore[override]
        res = super().itemChange(change, value)
        if change == QQuickItem.ItemParentHasChanged:
            p = self.parentItem()
            if p is not None:
                try:
                    p.widthChanged.connect(self._onTick)
                    p.heightChanged.connect(self._onTick)
                except Exception:
                    pass
            self._onTick()
        return res
