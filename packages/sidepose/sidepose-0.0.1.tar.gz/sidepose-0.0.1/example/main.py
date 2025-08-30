from __future__ import annotations
from sidepose import register_qml_types
import logging
import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


def main() -> int:
    # Minimal logging setup for the example app
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    app = QGuiApplication(sys.argv)
    register_qml_types()

    engine = QQmlApplicationEngine()
    qml_path = os.path.join(os.path.dirname(__file__), "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
