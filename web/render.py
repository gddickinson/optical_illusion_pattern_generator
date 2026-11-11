"""Render a pattern with the real Python generator (matplotlib, Agg) and return it as a PNG."""
import base64
import io
import threading

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import numpy as np  # noqa: E402

from web.catalog import BY_ID, make_config  # noqa: E402
from web.recorder import RandomLog  # noqa: E402

_LOCK = threading.Lock()  # pyplot is not thread-safe
MAX_PIXELS = 1600 * 1200
MAX_RESOLUTION = 2000


def cost_error(gid, params, cfg):
    """Reason to refuse a request that would take the pure-Python generators minutes, else None."""
    if cfg.width * cfg.height > MAX_PIXELS:
        return f"figure larger than {MAX_PIXELS} pixels"
    if cfg.resolution > MAX_RESOLUTION:
        return f"resolution above {MAX_RESOLUTION} (the browser engine has no such limit)"
    if gid == "cellular":
        n, g = int(params.get("grid_size", 100)), int(params.get("generations", 50))
        if n * n * g > 1_000_000:
            return "cellular automata grid_size^2 x generations above 1,000,000 (pure-Python loops)"
    if gid == "fractal":
        if params.get("fractal_type", "mandelbrot") in ("mandelbrot", "julia") and \
                cfg.resolution ** 2 * int(params.get("iterations", 100)) > 2e8:
            return "resolution^2 x iterations above 2e8"
    return None


def render_png(gid, params, cfg_dict, seed=None):
    """PNG (base64) of BY_ID[gid] at params/config, plus the np.random calls it made (for exact replay in JS)."""
    cls = BY_ID[gid][2]
    cfg = make_config(cfg_dict)
    with _LOCK:
        if seed is not None:
            np.random.seed(seed)
        with RandomLog() as log:
            arr = cls(cfg).generate(**params)
    buf = io.BytesIO()
    mpimg.imsave(buf, arr, format="png")
    return {"png": base64.b64encode(buf.getvalue()).decode("ascii"), "width": int(arr.shape[1]),
            "height": int(arr.shape[0]), "random": log.calls}
