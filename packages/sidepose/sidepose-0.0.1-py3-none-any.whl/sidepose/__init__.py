from PySide6.QtQml import qmlRegisterType, qmlRegisterSingletonType
try:
    # Available in newer PySide6
    from PySide6.QtQml import qmlRegisterSingletonInstance  # type: ignore
except Exception:  # pragma: no cover - older PySide6
    qmlRegisterSingletonInstance = None  # type: ignore

from .model import PeopleModel, PersonObject, KeypointObject, BBoxObject, TelemetryObject
from .controller import PoseController
from .overlay import PoseOverlay
from .anchors import PoseKeypointAnchor, PoseJointAnchor, PoseBoneAnchor, PoseFaceAnchor
from .constants import PoseConstants, BONE_ID_TO_PAIR


def register_qml_types():
    # Module: Pose 1.0
    uri = "Pose"
    major = 1
    minor = 0
    qmlRegisterType(PoseController, uri, major, minor, "PoseController")
    # Alias for clarity in QML: PoseProcessor (headless)
    qmlRegisterType(PoseController, uri, major, minor, "PoseProcessor")
    qmlRegisterType(PoseOverlay, uri, major, minor, "PoseOverlayQSG")
    qmlRegisterType(PoseKeypointAnchor, uri, major, minor, "PoseKeypointAnchor")
    # Back-compat name
    qmlRegisterType(PoseJointAnchor, uri, major, minor, "PoseJointAnchor")
    qmlRegisterType(PoseBoneAnchor, uri, major, minor, "PoseBoneAnchor")
    qmlRegisterType(PoseFaceAnchor, uri, major, minor, "PoseFaceAnchor")

    # Singleton: Pose enums (Keypoint, Bone, FitMode, FaceStrategy, FaceRotation)
    pose_singleton = PoseConstants()
    # Prefer instance registration when available (Qt 6.5+)
    if qmlRegisterSingletonInstance is not None:
        try:
            qmlRegisterSingletonInstance(uri, major, minor, "Pose",
                                         pose_singleton)  # type: ignore[arg-type]
        except Exception:
            # Fall back to provider callback variants
            try:
                def _provider1(engine):  # noqa: ARG001
                    return PoseConstants()
                qmlRegisterSingletonType(PoseConstants, uri, major, minor, "Pose", _provider1)
            except TypeError:
                def _provider2(engine, scriptEngine):  # noqa: ARG001
                    return PoseConstants()
                qmlRegisterSingletonType(PoseConstants, uri, major, minor, "Pose", _provider2)
    else:
        # Older PySide6: try provider with 1 arg first, then 2 args
        try:
            def _provider1(engine):  # noqa: ARG001
                return PoseConstants()
            qmlRegisterSingletonType(PoseConstants, uri, major, minor, "Pose", _provider1)
        except TypeError:
            def _provider2(engine, scriptEngine):  # noqa: ARG001
                return PoseConstants()
            qmlRegisterSingletonType(PoseConstants, uri, major, minor, "Pose", _provider2)
    # Expose models as creatable QML types (optional, but useful for type hints)
    qmlRegisterType(PeopleModel, uri, major, minor, "PeopleModel")
    qmlRegisterType(PersonObject, uri, major, minor, "PersonObject")
    qmlRegisterType(KeypointObject, uri, major, minor, "KeypointObject")
    qmlRegisterType(BBoxObject, uri, major, minor, "BBoxObject")
    qmlRegisterType(TelemetryObject, uri, major, minor, "TelemetryObject")


__all__ = [
    "register_qml_types",
    "PeopleModel",
    "PersonObject",
    "KeypointObject",
    "BBoxObject",
    "TelemetryObject",
    "PoseController",
    "PoseOverlay",
    "PoseJointAnchor",
    "PoseBoneAnchor",
    "PoseFaceAnchor",
    "Pose",
    "BONE_ID_TO_PAIR",
]

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("sidepose")
except Exception:
    __version__ = "0.0.0"
