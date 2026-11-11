"""Record what the real Python generators draw and which random numbers they draw.

- ``record_scene(generator, params)`` runs ``generator.generate(**params)`` with ``plt.subplots`` swapped for a fake
  figure/axes that log every drawing call as a JSON-able primitive (the same scene schema the JS engine in
  web/static/engine.js produces), so the browser port can be compared call by call with the Python.
- ``RandomLog`` patches the ``np.random`` functions the generators use and logs each call and its result; the JS
  engine's ReplayRng plays such a log back, so even the random patterns can be compared exactly.

Colours are normalised to RGBA with matplotlib.colors.to_rgba; colormaps are recorded as a 9-point RGBA signature.
"""
import contextlib

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba

CMAP_SAMPLES = np.linspace(0, 1, 9)
RANDOM_FUNCS = ("random", "randint", "uniform", "normal", "choice")


def _rgba(c):
    if c is None:
        return None
    if isinstance(c, np.ndarray):
        c = tuple(float(v) for v in c)
    return [round(float(v), 12) for v in to_rgba(c)]


def _floats(a):
    return [float(v) for v in np.asarray(a, dtype=float).ravel()]


def _cmap_sig(cmap):
    cm = matplotlib.colormaps[cmap] if isinstance(cmap, str) else cmap
    return [[round(float(v), 12) for v in rgba] for rgba in cm(CMAP_SAMPLES)]


FMT_COLORS = {"k": "black", "r": "red", "b": "blue", "g": "green", "w": "white"}


def _parse_fmt(fmt):
    """Matplotlib format strings used in the repo: 'o', 'ko', 'k-', 'k--', ':'."""
    color = FMT_COLORS.get(fmt[0]) if fmt and fmt[0] in FMT_COLORS else None
    rest = fmt[1:] if color else fmt
    if rest == "o":
        return color, None, "o"
    return color, {"-": "-", "--": "--", ":": ":"}.get(rest, "-"), None


class FakeAxes:
    """Logs the subset of the matplotlib Axes API used by the pattern generators."""

    def __init__(self):
        self.prims = []
        self.view = {"xlim": None, "ylim": None, "aspect": None, "axis_off": False}

    def plot(self, x, y, fmt=None, color=None, linewidth=None, alpha=None, markersize=None,
             markeredgecolor=None, markeredgewidth=None, solid_capstyle=None):
        fcolor, ls, marker = _parse_fmt(fmt) if fmt else (None, "-", None)
        col = color if color is not None else fcolor
        p = {"x": _floats(np.atleast_1d(x)), "y": _floats(np.atleast_1d(y)), "color": _rgba(col),
             "alpha": None if alpha is None else float(alpha)}
        if marker:
            p.update(t="marker", ms=None if markersize is None else float(markersize),
                     mec=_rgba(markeredgecolor), mew=None if markeredgewidth is None else float(markeredgewidth))
        else:
            p.update(t="line", lw=None if linewidth is None else float(linewidth), ls=ls,
                     cap=solid_capstyle or None)
        self.prims.append(p)

    def fill(self, x, y, color=None, alpha=None, edgecolor=None, linewidth=None):
        self.prims.append({"t": "fill", "x": _floats(x), "y": _floats(y), "color": _rgba(color),
                           "alpha": None if alpha is None else float(alpha), "ec": _rgba(edgecolor),
                           "lw": None if linewidth is None else float(linewidth)})

    def _span(self, t, v, color=None, linewidth=None, alpha=None, xmin=0, xmax=1):
        self.prims.append({"t": t, "v": float(v), "color": _rgba(color), "alpha": None if alpha is None else float(alpha),
                           "lw": None if linewidth is None else float(linewidth), "span": [float(xmin), float(xmax)]})

    def axhline(self, y=0, **kw):
        self._span("hline", y, **kw)

    def axvline(self, x=0, **kw):
        self._span("vline", x, **kw)

    def scatter(self, x, y, s=None, c=None, alpha=None):
        self.prims.append({"t": "scatter", "x": _floats(x), "y": _floats(y), "s": float(s), "color": _rgba(c),
                           "alpha": None if alpha is None else float(alpha)})

    def add_patch(self, patch):
        self.prims.append({"t": "circle", "cx": float(patch.center[0]), "cy": float(patch.center[1]),
                           "r": float(patch.radius), "color": [round(float(v), 12) for v in patch.get_facecolor()]})

    def contour(self, X, Y, Z, levels=None, colors=None, cmap=None, linewidths=None):
        fig, ax = plt.figure(), None
        try:  # the real levels matplotlib would draw (MaxNLocator + trimming)
            ax = fig.add_subplot()
            lv = ax.contour(X, Y, Z, levels=levels).levels
        finally:
            plt.close(fig)
        X = np.asarray(X)
        self.prims.append({"t": "contour", "x": _floats(X[0, :]), "y": _floats(np.asarray(Y)[:, 0]), "z": _floats(Z),
                           "levels": _floats(lv), "color": _rgba(colors) if colors is not None else None,
                           "cmap": None if colors is not None else _cmap_sig(cmap or "viridis"),
                           "lw": None if linewidths is None else float(linewidths)})

    def imshow(self, data, cmap=None, origin=None, extent=None, aspect=None):
        data = np.asarray(data, dtype=float)
        self.prims.append({"t": "image", "rows": int(data.shape[0]), "cols": int(data.shape[1]), "data": _floats(data),
                           "cmap": _cmap_sig(cmap or "viridis"), "origin": origin or "upper",
                           "extent": None if extent is None else _floats(extent)})

    def set_xlim(self, a, b):
        self.view["xlim"] = [float(a), float(b)]

    def set_ylim(self, a, b):
        self.view["ylim"] = [float(a), float(b)]

    def set_aspect(self, a):
        self.view["aspect"] = a

    def axis(self, a):
        self.view["axis_off"] = a == "off"


class _Patch:
    def __init__(self):
        self.color = None

    def set_facecolor(self, c):
        self.color = _rgba(c)


class _Canvas:
    def draw(self):
        pass

    def buffer_rgba(self):
        return np.zeros((1, 1, 4), dtype=np.uint8)

    def get_width_height(self):
        return (1, 1)


class FakeFigure:
    def __init__(self, figsize):
        self.figsize = [float(v) for v in figsize]
        self.patch = _Patch()
        self.canvas = _Canvas()


@contextlib.contextmanager
def _fake_pyplot(store):
    saved = {k: getattr(plt, k) for k in ("subplots", "tight_layout", "gcf", "close")}

    def subplots(figsize=(6.4, 4.8)):
        store["fig"], store["ax"] = FakeFigure(figsize), FakeAxes()
        return store["fig"], store["ax"]

    plt.subplots = subplots
    plt.tight_layout = lambda *a, **k: None
    plt.gcf = lambda: store["fig"]
    plt.close = lambda *a, **k: None if a and isinstance(a[0], FakeFigure) else saved["close"](*a, **k)
    try:
        yield
    finally:
        for k, v in saved.items():
            setattr(plt, k, v)


class RandomLog:
    """Context manager: log every np.random.<fn> call the generators make (name, result)."""

    def __init__(self):
        self.calls = []

    def __enter__(self):
        self._saved = {k: getattr(np.random, k) for k in RANDOM_FUNCS}
        for name in RANDOM_FUNCS:
            setattr(np.random, name, self._wrap(name, self._saved[name]))
        return self

    def _wrap(self, name, fn):
        def wrapped(*a, **k):
            r = fn(*a, **k)
            self.calls.append([name, np.asarray(r).ravel().tolist() if np.ndim(r) else r.item() if hasattr(r, "item") else r])
            return r
        return wrapped

    def __exit__(self, *exc):
        for k, v in self._saved.items():
            setattr(np.random, k, v)


def record_scene(generator, params):
    """Run generator.generate(**params) against the fake axes; return (scene dict, random log)."""
    store = {}
    with _fake_pyplot(store), RandomLog() as log:
        generator.generate(**params)
    ax, fig = store["ax"], store["fig"]
    return {"figsize": fig.figsize, "bg": fig.patch.color, "view": ax.view, "prims": ax.prims}, log.calls
