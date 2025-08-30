from __future__ import annotations

import os
import errno
import logging
from urllib.parse import urlparse
from urllib.request import urlretrieve
from typing import Optional

from PySide6.QtCore import QUrl
import sys

logger = logging.getLogger(__name__)


_MODEL_URLS = {
    # Official MediaPipe storage (versioned). Float16 variants are common; adjust if needed.
    "pose_landmarker_lite": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
    "pose_landmarker_full": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task",
    "pose_landmarker_heavy": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task",
}


def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def _cache_dir() -> str:
    # 1) Explicit override
    base = os.environ.get("SIDEPOSE_CACHE_DIR")
    if not base:
        # 2) Platform-aware defaults
        if sys.platform.startswith("win"):
            base = os.environ.get("LOCALAPPDATA")
            if not base:
                # Fallback to user-local AppData path if env is missing
                base = os.path.expanduser(r"~\\AppData\\Local")
        elif sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Caches")
        else:
            base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    d = os.path.join(base, "sidepose", "models")
    _ensure_dir(d)
    return d


def _is_file(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except Exception:
        return False


def resolve_model_asset(name_or_path: Optional[str], use_gpu: bool = False) -> str:
    """Return a local filesystem path to a .task model.

    Accepts:
    - None or "": defaults to 'pose_landmarker_full'.
    - A bare name (with or without .task suffix): e.g., 'pose_landmarker_full'.
    - A local file path.
    - A file:// URL or http(s):// URL (downloaded into cache).
    """
    # 1) Default name
    s = (name_or_path or "").strip()
    if not s:
        s = "pose_landmarker_full"

    # 2) If it's a URL, handle accordingly
    try:
        qurl = QUrl(s)
        if qurl.isValid() and qurl.scheme():
            if qurl.scheme().startswith("file"):
                local = qurl.toLocalFile()
                if local and _is_file(local):
                    return local
                # If file:// but doesn't exist, fall through to name handling
            elif qurl.scheme() in ("http", "https"):
                # Download to cache
                parsed = urlparse(s)
                fname = os.path.basename(parsed.path) or "model.task"
                dest = os.path.join(_cache_dir(), fname)
                if not _is_file(dest):
                    logger.info("Downloading model: %s -> %s", s, dest)
                    urlretrieve(s, dest)
                return dest
    except Exception:
        pass

    # 3) If it's an existing local path, use it
    if _is_file(s):
        return s

    # 4) Treat as a model name (strip .task suffix for lookup)
    base = s
    if base.endswith(".task"):
        base = base[:-5]
    # Map known names to URLs
    url = _MODEL_URLS.get(base)
    if url is None:
        # Unknown name: assume it's a filename in CWD or in repo root
        alt = s if s.endswith(".task") else f"{s}.task"
        if _is_file(alt):
            return alt
        # As a last resort, try in current working directory's parent (repo root assumption)
        try:
            repo_alt = os.path.abspath(os.path.join(os.getcwd(), alt))
            if _is_file(repo_alt):
                return repo_alt
        except Exception:
            pass
        # Fallback to full model default URL
        base = "pose_landmarker_full"
        url = _MODEL_URLS[base]

    # 5) Download mapped URL into cache if needed
    fname = f"{base}.task"
    dest = os.path.join(_cache_dir(), fname)
    if not _is_file(dest):
        logger.info("Fetching model '%s' from %s", base, url)
        urlretrieve(url, dest)
    return dest
