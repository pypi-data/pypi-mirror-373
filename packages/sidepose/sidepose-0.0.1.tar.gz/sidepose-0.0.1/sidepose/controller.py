from __future__ import annotations

import math
import time
from typing import Optional, List
import threading
import queue

from PySide6.QtCore import QObject, Property, Signal, QTimer, Qt, QUrl
from PySide6.QtMultimedia import QVideoSink, QVideoFrame, QVideoFrameFormat
from PySide6.QtGui import QImage

from .model import PeopleModel, PersonObject, KeypointObject, BBoxObject, TelemetryObject
from .model_hub import resolve_model_asset

try:
    # Optional MediaPipe backend
    from .backends.mediapipe_backend import MediaPipePoseBackend, _HAVE_MP
except Exception:
    MediaPipePoseBackend = None  # type: ignore
    _HAVE_MP = False  # type: ignore


import logging


logger = logging.getLogger(__name__)


class PoseController(QObject):
    error = Signal(str)
    telemetryUpdated = Signal()
    frameSizeChanged = Signal()
    primaryPersonChanged = Signal()
    numPosesChanged = Signal()
    trackingEnabledChanged = Signal()
    minPoseDetectionConfidenceChanged = Signal()
    minPosePresenceConfidenceChanged = Signal()
    minTrackingConfidenceChanged = Signal()
    backendResultReady = Signal(object, int, int, float)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._videoSink = None
        self._enabled = True
        self._backend = "mediapipe"
        self._modelAssetPath = ""
        self._numPoses = 1
        self._minPoseDetectionConfidence = 0.5
        self._minPosePresenceConfidence = 0.5
        self._minTrackingConfidence = 0.5
        self._useGpu = False
        self._inferenceMaxSide = 960  # 0 disables downscale
        self._frameDecimation = 1  # process every Nth frame
        self._mp_backend = None
        self._peopleModel = PeopleModel(self)
        self._telemetry = TelemetryObject(self)
        self._last_ts = time.time()
        self._frame_width = 0
        self._frame_height = 0
        self._frame_seq = 0
        # Tracking state
        self._trackingEnabled = True
        self._tracks = []  # list of dicts: {id:int, cx:float, cy:float, last_ts:float}
        self._nextTrackId = 1
        self._trackMaxAgeSec = 1.0
        self._trackDistThresh = 0.12  # as fraction of frame diagonal
        self._freeTrackIds = []

        # Worker thread infra for background inference
        self._in_q = queue.Queue(maxsize=1)
        self._stop_event = threading.Event()
        self._worker = None

        # Debounced backend initialization (coalesce multiple QML property sets)
        self._init_timer = QTimer(self)
        self._init_timer.setSingleShot(True)
        self._init_timer.setInterval(0)
        self._init_timer.timeout.connect(self._init_backend_impl)
        self._last_backend_config = None  # tuple capturing last init config

        self.backendResultReady.connect(self._onBackendResult)
        # Keep primaryPerson notify in sync with PeopleModel resets/inserts/removals
        try:
            self._peopleModel.modelReset.connect(self._onPeopleModelChanged)
            self._peopleModel.rowsInserted.connect(self._onPeopleModelChanged)
            self._peopleModel.rowsRemoved.connect(self._onPeopleModelChanged)
            self._peopleModel.countChanged.connect(self._onPeopleModelChanged)
        except Exception:
            pass
        # Ensure worker is stopped on object destruction
        try:
            self.destroyed.connect(lambda *_: self._stop_worker())
        except Exception:
            pass

        self._dummyTimer = QTimer(self)
        self._dummyTimer.setInterval(33)
        self._dummyTimer.timeout.connect(self._onDummyTick)
        self._dummyTimer.start()

        def __init__(self, parent: Optional[QObject] = None):
            super().__init__(parent)
            self._videoSink = None
            self._enabled = True
            self._backend = "mediapipe"
            self._modelAssetPath = ""
            self._numPoses = 1
            self._minPoseDetectionConfidence = 0.5
            self._minPosePresenceConfidence = 0.5
            self._minTrackingConfidence = 0.5
            self._useGpu = False
            self._inferenceMaxSide = 960  # 0 disables downscale
            self._frameDecimation = 1  # process every Nth frame
            self._mp_backend = None
            self._peopleModel = PeopleModel(self)
            self._telemetry = TelemetryObject(self)
            self._last_ts = time.time()
            self._frame_width = 0
            self._frame_height = 0
            self._frame_seq = 0
            # Tracking state
            self._trackingEnabled = True
            self._tracks = []  # list of dicts: {id:int, cx:float, cy:float, last_ts:float}
            self._nextTrackId = 1
            self._trackMaxAgeSec = 1.0
            self._trackDistThresh = 0.12  # as fraction of frame diagonal
            self._freeTrackIds = []

            # Worker thread infra for background inference
            self._in_q = queue.Queue(maxsize=1)
            self._stop_event = threading.Event()
            self._worker = None

            # Coalesce backend init across multiple property updates from QML
            self._init_timer = QTimer(self)
            self._init_timer.setSingleShot(True)
            self._init_timer.setInterval(0)
            self._init_timer.timeout.connect(self._init_backend_impl)
            self._last_backend_config = None  # tuple capturing last init config

            self.backendResultReady.connect(self._onBackendResult)
            # Keep primaryPerson notify in sync with PeopleModel resets/inserts/removals
            try:
                self._peopleModel.modelReset.connect(self._onPeopleModelChanged)
                self._peopleModel.rowsInserted.connect(self._onPeopleModelChanged)
                self._peopleModel.rowsRemoved.connect(self._onPeopleModelChanged)
                self._peopleModel.countChanged.connect(self._onPeopleModelChanged)
            except Exception:
                pass
            # Ensure worker is stopped on object destruction
            try:
                self.destroyed.connect(lambda *_: self._stop_worker())
            except Exception:
                pass

            self._dummyTimer = QTimer(self)
            self._dummyTimer.setInterval(33)
            self._dummyTimer.timeout.connect(self._onDummyTick)
            self._dummyTimer.start()

    @Property(QObject)
    def videoSink(self) -> Optional[QObject]:
        return self._videoSink

    @videoSink.setter
    def videoSink(self, sink: Optional[QObject]) -> None:
        if self._videoSink is not None:
            try:
                self._videoSink.videoFrameChanged.disconnect(self._onVideoFrame)
            except Exception:
                pass
        self._videoSink = sink if isinstance(sink, QVideoSink) else None
        if self._videoSink is not None:
            self._videoSink.videoFrameChanged.connect(self._onVideoFrame)

    @Property(str)
    def backend(self) -> str:
        return self._backend

    @backend.setter
    def backend(self, name: str) -> None:
        self._backend = str(name or "mediapipe")
        self._maybe_init_backend()

    @Property(str)
    def modelAssetPath(self) -> str:
        return self._modelAssetPath

    @modelAssetPath.setter
    def modelAssetPath(self, p: str) -> None:
        self._modelAssetPath = str(p or "")
        self._maybe_init_backend()

    @Property(int, notify=numPosesChanged)
    def numPoses(self) -> int:
        return self._numPoses

    @numPoses.setter
    def numPoses(self, n: int) -> None:
        self._numPoses = int(n)
        self._maybe_init_backend()
        try:
            self.numPosesChanged.emit()
        except Exception:
            pass

    @Property(bool)
    def useGpu(self) -> bool:
        return self._useGpu

    @useGpu.setter
    def useGpu(self, v: bool) -> None:
        self._useGpu = bool(v)
        self._maybe_init_backend()

    @Property(float, notify=minPoseDetectionConfidenceChanged)
    def minPoseDetectionConfidence(self) -> float:
        return self._minPoseDetectionConfidence

    @minPoseDetectionConfidence.setter
    def minPoseDetectionConfidence(self, v: float) -> None:
        self._minPoseDetectionConfidence = float(v)
        self._maybe_init_backend()
        try:
            self.minPoseDetectionConfidenceChanged.emit()
        except Exception:
            pass

    @Property(float, notify=minPosePresenceConfidenceChanged)
    def minPosePresenceConfidence(self) -> float:
        return self._minPosePresenceConfidence

    @minPosePresenceConfidence.setter
    def minPosePresenceConfidence(self, v: float) -> None:
        self._minPosePresenceConfidence = float(v)
        self._maybe_init_backend()
        try:
            self.minPosePresenceConfidenceChanged.emit()
        except Exception:
            pass

    @Property(float, notify=minTrackingConfidenceChanged)
    def minTrackingConfidence(self) -> float:
        return self._minTrackingConfidence

    @minTrackingConfidence.setter
    def minTrackingConfidence(self, v: float) -> None:
        self._minTrackingConfidence = float(v)
        self._maybe_init_backend()
        try:
            self.minTrackingConfidenceChanged.emit()
        except Exception:
            pass

    @Property(int)
    def inferenceMaxSide(self) -> int:
        return self._inferenceMaxSide

    @inferenceMaxSide.setter
    def inferenceMaxSide(self, v: int) -> None:
        self._inferenceMaxSide = max(0, int(v))

    def _maybe_init_backend(self) -> None:
        # Debounce: many QML setters may fire in sequence; schedule a single init
        try:
            if self._init_timer.isActive():
                self._init_timer.stop()
            self._init_timer.start()
        except Exception:
            # Fallback: if timer not available, run immediately
            self._init_backend_impl()

    def _init_backend_impl(self) -> None:
        # Avoid redundant reinitialization if config unchanged
        cfg = (
            self._backend,
            self._modelAssetPath,
            int(self._numPoses),
            float(self._minPoseDetectionConfidence),
            float(self._minPosePresenceConfidence),
            float(self._minTrackingConfidence),
            bool(self._useGpu),
        )
        if self._mp_backend is not None and self._last_backend_config == cfg:
            return
        if self._backend == "mediapipe":
            # Resolve or download model (handles default name, URLs, and file paths)
            model_path = resolve_model_asset(self._modelAssetPath, use_gpu=self._useGpu)
            try:
                url = QUrl(str(model_path))
                if url.isValid() and url.scheme() and url.scheme().startswith("file"):
                    local = url.toLocalFile()
                    if local:
                        model_path = local
            except Exception:
                pass
            if _HAVE_MP and MediaPipePoseBackend is not None:
                try:
                    self._mp_backend = MediaPipePoseBackend(
                        model_path,
                        num_poses=self._numPoses,
                        min_detection_confidence=self._minPoseDetectionConfidence,
                        min_presence_confidence=self._minPosePresenceConfidence,
                        min_tracking_confidence=self._minTrackingConfidence,
                        use_gpu=self._useGpu,
                    )
                    logger.info(
                        "MediaPipe backend initialized: GPU=%s, model='%s'",
                        self._useGpu,
                        model_path,
                    )
                    self._last_backend_config = cfg
                    self._start_worker()
                except Exception as e:
                    if self._useGpu:
                        try:
                            self._mp_backend = MediaPipePoseBackend(
                                model_path,
                                num_poses=self._numPoses,
                                min_detection_confidence=self._minPoseDetectionConfidence,
                                min_presence_confidence=self._minPosePresenceConfidence,
                                min_tracking_confidence=self._minTrackingConfidence,
                                use_gpu=False,
                            )
                            self._useGpu = False
                            logger.warning(
                                "MediaPipe GPU init failed; falling back to CPU delegate.")
                            logger.info(
                                "MediaPipe backend initialized: GPU=%s, model='%s'",
                                self._useGpu,
                                model_path,
                            )
                            self._last_backend_config = (
                                self._backend,
                                self._modelAssetPath,
                                int(self._numPoses),
                                float(self._minPoseDetectionConfidence),
                                float(self._minPosePresenceConfidence),
                                float(self._minTrackingConfidence),
                                False,
                            )
                            self._start_worker()
                        except Exception as e2:
                            self._mp_backend = None
                            self.error.emit(str(e2))
                            self._stop_worker()
                    else:
                        self._mp_backend = None
                        self.error.emit(str(e))
                        self._stop_worker()
            else:
                self._mp_backend = None
                self.error.emit("mediapipe not available; using dummy skeleton")
                self._stop_worker()
        else:
            self._mp_backend = None
            self._stop_worker()

    @Property(bool)
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, v: bool) -> None:
        self._enabled = bool(v)

    @Property(QObject, constant=True)
    def peopleModel(self) -> PeopleModel:
        return self._peopleModel

    @Property(QObject, notify=primaryPersonChanged)
    def primaryPerson(self):
        try:
            return self._peopleModel.personAt(0)
        except Exception:
            return None

    @Property(QObject, notify=telemetryUpdated)
    def telemetry(self) -> TelemetryObject:
        return self._telemetry

    @Property(int, notify=frameSizeChanged)
    def frameWidth(self) -> int:
        return self._frame_width

    @Property(int, notify=frameSizeChanged)
    def frameHeight(self) -> int:
        return self._frame_height

    @Property(bool, notify=trackingEnabledChanged)
    def trackingEnabled(self) -> bool:
        return self._trackingEnabled

    @trackingEnabled.setter
    def trackingEnabled(self, v: bool) -> None:
        v = bool(v)
        if self._trackingEnabled != v:
            self._trackingEnabled = v
            # Reset tracks when toggled
            self._tracks = []
            self._nextTrackId = 1
            self._freeTrackIds = []
            try:
                self.trackingEnabledChanged.emit()
            except Exception:
                pass

    def _onVideoFrame(self, frame: QVideoFrame) -> None:
        if not self._enabled:
            return
        try:
            width = frame.width()
            height = frame.height()
        except Exception:
            fmt = frame.videoFrameFormat()
            width = fmt.frameWidth() if fmt is not None else 0
            height = fmt.frameHeight() if fmt is not None else 0
        if width != self._frame_width or height != self._frame_height:
            self._frame_width = width
            self._frame_height = height
            self.frameSizeChanged.emit()

        now = time.time()
        elapsed = max(1e-6, now - self._last_ts)
        self._last_ts = now
        self._telemetry.setFps(1.0 / elapsed)
        self.telemetryUpdated.emit()

        if self._mp_backend is not None:
            self._frame_seq += 1
            if self._frameDecimation <= 1 or (self._frame_seq % self._frameDecimation) == 0:
                try:
                    img = self._frame_to_numpy_rgb(frame, self._inferenceMaxSide)
                except Exception as e:
                    img = None
                    self.error.emit(f"frame conversion failed: {e}")
                if img is not None:
                    item = (img, width, height, now)
                    try:
                        self._in_q.put_nowait(item)
                    except Exception:
                        try:
                            _ = self._in_q.get_nowait()
                        except Exception:
                            pass
                        try:
                            self._in_q.put_nowait(item)
                        except Exception:
                            pass
            return
        else:
            person = self._make_dummy_person(max(1, width), max(1, height), now)
            self._peopleModel.setPeople([person])

    def _frame_to_numpy_rgb(self, frame: QVideoFrame, target_max_side: int = 0):
        try:
            import importlib
            np = importlib.import_module('numpy')  # type: ignore
        except Exception:
            return None
        if not frame.isValid():
            return None
        if target_max_side in (0, None) and frame.map(QVideoFrame.MapMode.ReadOnly):
            try:
                w = frame.width()
                h = frame.height()
                bpl = frame.bytesPerLine()
                pf = frame.pixelFormat()
                buf = frame.bits()
                arr = np.frombuffer(buf, dtype=np.uint8, count=bpl * h)
                if pf in (QVideoFrameFormat.PixelFormat.Format_RGBA8888, QVideoFrameFormat.PixelFormat.Format_ARGB8888):
                    rgba = arr.reshape((h, bpl // 4, 4))[:, :w, :]
                    return rgba[:, :, :3].copy()
                if pf in (QVideoFrameFormat.PixelFormat.Format_BGRA8888, QVideoFrameFormat.PixelFormat.Format_ABGR8888):
                    bgra = arr.reshape((h, bpl // 4, 4))[:, :w, :]
                    return bgra[:, :, 2::-1].copy()
            except Exception:
                pass
            finally:
                frame.unmap()

        try:
            qimg: QImage = frame.toImage()
        except Exception:
            qimg = QImage()
        if not qimg or qimg.isNull():
            return None
        if target_max_side and target_max_side > 0:
            sw = qimg.width()
            sh = qimg.height()
            max_side = max(sw, sh)
            if max_side > target_max_side:
                scale = target_max_side / float(max_side)
                tw = max(1, int(sw * scale))
                th = max(1, int(sh * scale))
                qimg = qimg.scaled(tw, th, Qt.KeepAspectRatio,
                                   Qt.FastTransformation)  # type: ignore
        rgb = qimg.convertToFormat(QImage.Format.Format_RGB888)
        w = rgb.width()
        h = rgb.height()
        ptr = rgb.bits()  # memoryview in PySide6
        arr = np.frombuffer(ptr, dtype=np.uint8)
        bpl = rgb.bytesPerLine()
        if arr.size < h * bpl:
            return None
        arr = arr.reshape((h, bpl))[:, : w * 3]
        return arr.reshape((h, w, 3)).copy()

    def _convert_mediapipe_result(self, res, width: int, height: int) -> List[PersonObject]:
        people: List[PersonObject] = []
        try:
            pose_list = res.pose_landmarks or []
        except Exception:
            pose_list = []
        for lm_set in pose_list:
            kps: List[KeypointObject] = []
            minx, miny, maxx, maxy = width, height, 0.0, 0.0
            for lm in lm_set:
                x = float(getattr(lm, 'x', 0.0)) * width
                y = float(getattr(lm, 'y', 0.0)) * height
                c = float(getattr(lm, 'visibility', 1.0))
                kps.append(KeypointObject(x, y, c, c))
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)
            bbox = BBoxObject(minx, miny, maxx, maxy)
            people.append(PersonObject(pid=-1, score=1.0, bbox=bbox, keypoints=kps))
        return people

    def _make_dummy_person(self, width: int, height: int, t: float) -> PersonObject:
        keypoints: List[KeypointObject] = []
        cx = width * 0.5
        cy = height * 0.5
        radius = min(width, height) * 0.2
        for i in range(33):
            ang = t * 2.0 + i * (2 * math.pi / 33.0)
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            keypoints.append(KeypointObject(x, y, 0.9))
        bbox = BBoxObject(cx - radius, cy - radius, cx + radius, cy + radius)
        return PersonObject(pid=1, score=0.9, bbox=bbox, keypoints=keypoints)

    def _onDummyTick(self) -> None:
        if self._videoSink is not None:
            return
        now = time.time()
        if self._frame_width == 0 or self._frame_height == 0:
            self._frame_width, self._frame_height = 1280, 720
            self.frameSizeChanged.emit()
        person = self._make_dummy_person(self._frame_width, self._frame_height, now)
        self._peopleModel.setPeople([person])

    @Property(int)
    def frameDecimation(self) -> int:
        return self._frameDecimation

    @frameDecimation.setter
    def frameDecimation(self, n: int) -> None:
        self._frameDecimation = max(1, int(n))

    def _start_worker(self) -> None:
        self._stop_worker()
        self._stop_event.clear()

        def _loop():
            while not self._stop_event.is_set():
                try:
                    item = self._in_q.get(timeout=0.1)
                except Exception:
                    continue
                if item is None:
                    continue
                img, w, h, ts = item
                try:
                    res = None
                    if self._mp_backend is not None:
                        res = self._mp_backend.detect(img, int(ts * 1000))
                    self.backendResultReady.emit(res, int(w), int(h), float(ts))
                except Exception as e:
                    self.error.emit(f"mediapipe failed: {e}")

        self._worker = threading.Thread(target=_loop, name="PoseControllerWorker", daemon=True)
        self._worker.start()

    def _stop_worker(self) -> None:
        try:
            self._stop_event.set()
        except Exception:
            pass
        try:
            if self._worker and self._worker.is_alive():
                self._worker.join(timeout=0.5)
        except Exception:
            pass
        self._worker = None
        try:
            while True:
                self._in_q.get_nowait()
        except Exception:
            pass

    def _onBackendResult(self, res_obj: object, width: int, height: int, ts_sec: float) -> None:
        try:
            people = self._convert_mediapipe_result(
                res_obj, width, height) if res_obj is not None else []
            if self._trackingEnabled:
                id_map = self._update_tracks_and_assign_ids(people, width, height, ts_sec)
                for i, person in enumerate(people):
                    try:
                        tid = id_map.get(i, None)
                        if tid is not None:
                            person._id = int(tid)  # type: ignore[attr-defined]
                    except Exception:
                        pass
            else:
                for i, person in enumerate(people, start=1):
                    try:
                        person._id = int(i)  # type: ignore[attr-defined]
                    except Exception:
                        pass
            self._peopleModel.setPeople(people)
            self.primaryPersonChanged.emit()
        except Exception as e:
            self.error.emit(f"result handling failed: {e}")

    def _onPeopleModelChanged(self, *args, **kwargs) -> None:  # Qt signals compatible
        try:
            self.primaryPersonChanged.emit()
        except Exception:
            pass

    def _update_tracks_and_assign_ids(self, detections: List[PersonObject], width: int, height: int, ts: float):
        alive_tracks = []
        expired_ids: List[int] = []
        for tr in self._tracks:
            if ts - tr.get('last_ts', 0.0) <= self._trackMaxAgeSec:
                alive_tracks.append(tr)
            else:
                try:
                    expired_ids.append(int(tr.get('id')))
                except Exception:
                    pass
        self._tracks = alive_tracks
        if expired_ids:
            self._freeTrackIds.extend(expired_ids)

        pairs = []
        diag = max(1.0, (width * width + height * height) ** 0.5)

        def det_center(p: PersonObject):
            try:
                bb = p.property("bbox")
                return float(bb.property("cx")), float(bb.property("cy"))
            except Exception:
                return 0.0, 0.0

        for ti, tr in enumerate(self._tracks):
            tcx, tcy = float(tr.get('cx', 0.0)), float(tr.get('cy', 0.0))
            for di, det in enumerate(detections):
                dcx, dcy = det_center(det)
                dx, dy = (dcx - tcx), (dcy - tcy)
                dist = (dx * dx + dy * dy) ** 0.5 / diag
                if dist <= self._trackDistThresh:
                    pairs.append((ti, di, dist))

        pairs.sort(key=lambda x: x[2])
        matched_tracks = set()
        matched_dets = set()
        det_to_track_id = {}
        for ti, di, _ in pairs:
            if ti in matched_tracks or di in matched_dets:
                continue
            tr = self._tracks[ti]
            det = detections[di]
            dcx, dcy = det_center(det)
            tr['cx'], tr['cy'] = dcx, dcy
            tr['last_ts'] = ts
            matched_tracks.add(ti)
            matched_dets.add(di)
            det_to_track_id[di] = tr['id']

        for di, det in enumerate(detections):
            if di in matched_dets:
                continue
            dcx, dcy = det_center(det)
            if self._freeTrackIds:
                tid = self._freeTrackIds.pop(0)
            else:
                tid = self._nextTrackId
                self._nextTrackId += 1
            tr = {'id': tid, 'cx': dcx, 'cy': dcy, 'last_ts': ts}
            self._tracks.append(tr)
            det_to_track_id[di] = tr['id']

        return det_to_track_id
