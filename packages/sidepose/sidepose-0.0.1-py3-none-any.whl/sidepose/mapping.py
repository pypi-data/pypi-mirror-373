from __future__ import annotations

from typing import Tuple


def compute_scale_offset(parent_w: float, parent_h: float, src_w: int, src_h: int, fit_mode: int) -> Tuple[float, float, float]:
    """Compute scale and offsets to map source pixel coords to a parent item.

    fit_mode:
      0: PreserveAspectFit, 1: Fill, 2: FitWidth, 3: FitHeight
    Returns (scale, offx, offy).
    """
    w = max(1.0, float(parent_w))
    h = max(1.0, float(parent_h))
    sw = max(1, int(src_w))
    sh = max(1, int(src_h))
    if fit_mode == 1:  # Fill
        scale = max(w / sw, h / sh)
    elif fit_mode == 2:  # FitWidth
        scale = w / sw
    elif fit_mode == 3:  # FitHeight
        scale = h / sh
    else:  # PreserveAspectFit
        scale = min(w / sw, h / sh)
    offx = (w - sw * scale) * 0.5 if fit_mode in (0, 1, 3) else 0.0
    offy = (h - sh * scale) * 0.5 if fit_mode in (0, 1, 2) else 0.0
    return scale, offx, offy
