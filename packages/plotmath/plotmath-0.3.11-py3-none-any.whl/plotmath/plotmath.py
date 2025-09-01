import pathlib

import numpy as np
import matplotlib.pyplot as plt
import shutil
import platform
import warnings

# Check if LaTeX is available
if platform.system() == "Windows":
    latex_available = shutil.which("latex.exe") is not None
else:
    latex_available = shutil.which("latex") is not None


if latex_available:
    try:
        plt.rc("text", usetex=True)
    except (FileNotFoundError, RuntimeError):
        plt.rc("text", usetex=False)
else:
    plt.rc("text", usetex=False)

red = (220 / 255, 94 / 255, 139 / 255)
blue = (0 / 255, 114 / 255, 178 / 255)
orange = (220 / 255, 80 / 255, 20 / 255)
# skyblue = "#56B4E9"
skyblue = "#D3E6F6"  # udir blue
# green = (0, 130 / 255, 90 / 255)
# green = "#DDF1E7"  # udir green
green = "#BBE3CE"  # udir green (deeper)
common = "#26A69A"
rare = "#1E88E5"
epic = "#9C27B0"
legendary = "#FFA000"
colors = [blue, red, green, skyblue, orange, common, rare, epic, legendary]

COLORS = {
    "blue": blue,
    "red": red,
    "orange": orange,
    "skyblue": skyblue,
    "green": green,
    "common": common,
    "rare": rare,
    "epic": epic,
    "legendary": legendary,
}

plt.rcParams["axes.prop_cycle"] = plt.cycler(color=colors)


def show():
    plt.show()


def close():
    plt.close()


# --- Tick helpers ---------------------------------------------------------
def _nice_step(span: float, max_ticks: int = 10) -> float:
    """Return a "nice" step size for a given span and desired max tick count.

    Uses multiples of 1, 2, 2.5, or 5 times a power of 10.
    """
    if not np.isfinite(span) or span <= 0:
        return 1.0
    if max_ticks <= 0:
        max_ticks = 10

    raw = span / max_ticks
    power = np.floor(np.log10(raw))
    base = 10**power
    for m in (1.0, 2.0, 2.5, 5.0):
        step = m * base
        if span / step <= max_ticks:
            return step
    # Fallback: next power of ten
    return 10.0 * base


def _generate_ticks(vmin: float, vmax: float, step: float) -> list:
    """Generate tick positions from vmin to vmax with given step.

    Ensures numerical stability and inclusive end when appropriate.
    """
    if step <= 0:
        return []
    start = np.ceil(vmin / step) * step
    # Add a small epsilon to include the endpoint when close
    eps = step * 1e-9
    ticks = np.arange(start, vmax + eps, step)
    # Ensure within bounds after floating errors
    ticks = ticks[(ticks > vmin + eps) & (ticks < vmax - eps)]
    return list(np.round(ticks, 12))


def _get_figure_and_axis():

    fig, ax = plt.subplots()

    ax.spines["left"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["bottom"].set_position("zero")
    ax.spines["top"].set_color("none")

    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

    ax.set_xlabel(r"$x$", fontsize=16, loc="right")
    ax.set_ylabel(r"$y$", fontsize=16, loc="top", rotation="horizontal")

    return fig, ax


def _get_figures_and_axes(n, m, figsize):
    figs, axes = plt.subplots(n, m, figsize=figsize)
    for ax in axes.flat:
        ax.spines["left"].set_position("zero")
        ax.spines["right"].set_color("none")
        ax.spines["bottom"].set_position("zero")
        ax.spines["top"].set_color("none")

        ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
        ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

    return figs, axes


def _set_ticks(
    xmin,
    xmax,
    ymin,
    ymax,
    xstep=None,
    ystep=None,
    max_ticks: int = 18,
):

    # Auto-compute steps if not provided
    if xstep is None:
        xstep = _nice_step(float(xmax - xmin), int(max_ticks))
    if ystep is None:
        ystep = _nice_step(float(ymax - ymin), int(max_ticks))

    xticks = _generate_ticks(xmin, xmax, xstep)
    yticks = _generate_ticks(ymin, ymax, ystep)

    # Omit 0 to avoid clutter at the origin
    xticks = [t for t in xticks if not np.isclose(t, 0.0)]
    yticks = [t for t in yticks if not np.isclose(t, 0.0)]

    plt.xticks(xticks, fontsize=16)
    plt.yticks(yticks, fontsize=16)

    return None


def _set_multiple_ticks(
    xmin,
    xmax,
    ymin,
    ymax,
    xstep,
    ystep,
    axes,
    fontsize=20,
    max_ticks: int = 10,
):
    # Auto-compute steps if not provided
    if xstep is None:
        xstep = _nice_step(float(xmax - xmin), int(max_ticks))
    if ystep is None:
        ystep = _nice_step(float(ymax - ymin), int(max_ticks))

    xticks = _generate_ticks(xmin, xmax, xstep)
    yticks = _generate_ticks(ymin, ymax, ystep)

    xticks = [t for t in xticks if not np.isclose(t, 0.0)]
    yticks = [t for t in yticks if not np.isclose(t, 0.0)]

    xticklabels = [f"${t}$" for t in xticks]
    yticklabels = [f"${t}$" for t in yticks]

    for ax in axes.flat:
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels, fontsize=fontsize)

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels, fontsize=fontsize)

    return axes


def annotate(xy, xytext, s, arc=0.3, fontsize=20):
    ax = plt.gca()
    ax.annotate(
        text=s,
        xy=xy,
        xytext=xytext,
        fontsize=fontsize,
        arrowprops=dict(
            arrowstyle="->",
            lw=2,
            color="black",
            alpha=0.7,
            connectionstyle=f"arc3,rad={arc}",
        ),
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="black", lw=1.5),
        horizontalalignment="left",
        verticalalignment="center",
    )


def make_bar(xy, length, orientation):
    x, y = xy

    if orientation == "horizontal":
        plt.annotate(
            "",
            xy=xy,
            xycoords="data",
            xytext=(x + length, y),
            textcoords="data",
            arrowprops=dict(arrowstyle="|-|,widthA=0.5,widthB=0.5", color="black"),
        )

    elif orientation == "vertical":
        plt.annotate(
            "",
            xy=xy,
            xycoords="data",
            xytext=(x, y + length),
            textcoords="data",
            arrowprops=dict(arrowstyle="|-|,widthA=0.5,widthB=0.5", color="black"),
        )


def _limits_from_data(xdata, ydata, pad_frac: float = 0.05, fallback=(-6, 6, -6, 6)):
    """Compute nice axis limits from x/y data with padding.

    - Filters out non-finite values.
    - Adds a small fractional padding to both axes.
    - If span is zero, expands by a reasonable amount.
    """
    try:
        x = np.asarray(xdata)
        y = np.asarray(ydata)
    except Exception:
        return fallback

    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() == 0:
        return fallback

    x = x[mask]
    y = y[mask]

    xmin = float(np.min(x))
    xmax = float(np.max(x))
    ymin = float(np.min(y))
    ymax = float(np.max(y))

    # Handle degenerate ranges
    if not np.isfinite(xmin) or not np.isfinite(xmax) or xmin == xmax:
        cx = xmin if np.isfinite(xmin) else 0.0
        pad = max(1.0, abs(cx) * 0.1)
        xmin, xmax = cx - pad, cx + pad
    else:
        pad = (xmax - xmin) * pad_frac
        xmin, xmax = xmin - pad, xmax + pad

    if not np.isfinite(ymin) or not np.isfinite(ymax) or ymin == ymax:
        cy = ymin if np.isfinite(ymin) else 0.0
        pad = max(1.0, abs(cy) * 0.1)
        ymin, ymax = cy - pad, cy + pad
    else:
        pad = (ymax - ymin) * pad_frac
        ymin, ymax = ymin - pad, ymax + pad

    return xmin, xmax, ymin, ymax


def plot(
    functions=[],
    fn_labels=False,
    xmin=None,
    xmax=None,
    ymin=None,
    ymax=None,
    xstep=None,
    ystep=None,
    ticks=True,
    alpha=None,
    grid=True,
    lw=2.5,
    domain=False,
    fontsize=20,
    figsize=None,
    xlabel=None,
    ylabel=None,
    xdata=None,
    ydata=None,
    max_ticks: int = 18,
):
    fig, ax = _get_figure_and_axis()

    if figsize is not None:
        fig.set_size_inches(figsize)

    if xlabel is None:
        xlabel = r"$x$"

    ax.set_xlabel(xlabel, fontsize=fontsize, loc="right")

    if ylabel is None:
        ylabel = r"$y$"

    ax.set_ylabel(ylabel, fontsize=fontsize, loc="top", rotation="horizontal")

    # Determine effective axis limits
    using_data = (xdata is not None) and (ydata is not None)

    if using_data:
        data_limits = _limits_from_data(xdata, ydata)
    else:
        data_limits = (-6, 6, -6, 6)

    exmin = data_limits[0] if xmin is None else xmin
    exmax = data_limits[1] if xmax is None else xmax
    eymin = data_limits[2] if ymin is None else ymin
    eymax = data_limits[3] if ymax is None else ymax

    # If still None (no data and not provided), fallback to defaults
    if exmin is None:
        exmin = -6
    if exmax is None:
        exmax = 6
    if eymin is None:
        eymin = -6
    if eymax is None:
        eymax = 6

    if ticks:
        # If ticks are auto and driven by data, force integer step sizes
        if using_data:
            if xstep is None:
                span_x = float(exmax - exmin)
                xstep = max(1, int(np.ceil(_nice_step(span_x, max_ticks))))
            if ystep is None:
                span_y = float(eymax - eymin)
                ystep = max(1, int(np.ceil(_nice_step(span_y, max_ticks))))
        _set_ticks(
            xmin=exmin,
            xmax=exmax,
            ymin=eymin,
            ymax=eymax,
            xstep=xstep,
            ystep=ystep,
            max_ticks=max_ticks,
        )

        ax.yaxis.label.set_size(fontsize)  # Set y-axis label font size
        ax.xaxis.label.set_size(fontsize)  # Set x-axis label font size

    else:
        plt.xticks([])
        plt.yticks([])

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(fontsize)  # Set to desired font size

    if domain:
        x = np.linspace(domain[0], domain[1], int(2**12))
    else:
        x = np.linspace(exmin, exmax, int(2**12))

    if isinstance(fn_labels, bool) and fn_labels:  # If True, automatically set labels
        fn_labels = [f"${fn.__name__}$" for fn in functions]
    elif isinstance(fn_labels, bool) and not fn_labels:  # If False, disable labels
        fn_labels = None
    # Otherwise the code will apply user-specified labels

    if fn_labels is not None:
        for f, label in zip(functions, fn_labels):
            ax.plot(x, f(x), lw=lw, alpha=alpha, label=label)

        ax.legend(fontsize=fontsize)

    else:
        for f in functions:
            ax.plot(x, f(x), lw=lw, alpha=alpha)

    plt.ylim(eymin, eymax)
    plt.xlim(exmin, exmax)

    if using_data:
        ax.plot(xdata, ydata, lw=lw, color=blue)

    if grid:
        plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()

    return fig, ax


def multiplot(
    functions,
    fn_labels=False,
    xmin=-6,
    xmax=6,
    ymin=-6,
    ymax=6,
    xstep=None,
    ystep=None,
    ticks=True,
    alpha=None,
    grid=True,
    rows=2,
    cols=2,
    figsize=(8, 6),
    lw=2.5,
    fontsize=20,
    max_ticks: int = 10,
):
    figs, axes = _get_figures_and_axes(rows, cols, figsize)

    if ticks:
        axes = _set_multiple_ticks(
            xmin=xmin + 1,
            xmax=xmax,
            ymin=ymin + 1,
            ymax=ymax,
            xstep=xstep,
            ystep=ystep,
            axes=axes,
            max_ticks=max_ticks,
        )
    else:
        for ax in axes.flat:
            ax.set_xticks([])
            ax.set_yticks([])

    x = np.linspace(xmin, xmax, int(2**12))

    if isinstance(fn_labels, bool) and fn_labels:  # If True, automatically set labels
        fn_labels = [f"${fn.__name__}$" for fn in functions]
    elif isinstance(fn_labels, bool) and not fn_labels:  # If False, disable labels
        fn_labels = None
    else:
        fn_labels = [f"${label}$" for label in fn_labels]

    if functions != []:
        for f, ax, label in zip(functions, axes.flat, fn_labels):
            ax.plot(x, f(x), lw=lw, alpha=alpha, label=label)
            ax.legend(fontsize=fontsize)

    for ax in axes.flat:
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.set_xlabel(r"$x$", fontsize=fontsize, loc="right")
        ax.set_ylabel(r"$y$", fontsize=fontsize, loc="top", rotation="horizontal")

    if grid:
        for ax in axes.flat:
            ax.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()

    return figs, axes


def savefig(dirname, fname, transparent=True):
    dir = pathlib.Path(dirname)
    dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(f"{dir}/{fname}", transparent=transparent)

    return None


# Legacy function
def plot_polygon(
    *points,
    ax=None,
    color=blue,
    alpha=0.05,
    show_vertices=False,
    ls="-",
    edges=True,
):
    return polygon(
        *points,
        ax=ax,
        color=color,
        alpha=alpha,
        show_vertices=show_vertices,
        ls=ls,
        edges=edges,
    )


def polygon(
    *points,
    ax=None,
    color=blue,
    alpha=0.05,
    show_vertices=False,
    ls="-",
    edges=True,
):
    points = [*points]
    points.append(points[0])
    if ax is None:
        ax = plt.gca()

    x, y = zip(*points)
    ax.fill(x, y, color=color, alpha=alpha)
    if edges:
        ax.plot(x, y, color="black", alpha=1, lw=1.5, ls=ls)

    if show_vertices:
        x, y = zip(*set(points))
        ax.plot(x, y, "ko", markersize=8, alpha=0.7)

    return None


def histogram(
    xmin,
    frequencies,
    binsizes,
    xlabel=None,
    ylabel=None,
    rotation=0,
    fontsize=16,
    norwegian=True,
    lw=2.5,
    alpha=0.6,
):
    heights = [f / b for f, b in zip(frequencies, binsizes)]
    fig, ax = _get_figure_and_axis()

    x = [xmin]
    for i, binsize in enumerate(binsizes):
        x.append(x[i] + binsize)

    xticks = x[:]
    if 0 in xticks:
        xticks.remove(0)

    ax.set_xticks(xticks)
    ax.set_xticklabels([f"${i}$" for i in xticks], fontsize=fontsize, rotation=0)

    yticks = list(np.arange(1, max(heights) + 1, 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"${int(i)}$" for i in yticks], fontsize=fontsize, rotation=0)

    if ylabel:
        ax.set_ylabel(
            ylabel,
            fontsize=fontsize,
            rotation=0,
            loc="top",
        )
    else:
        if norwegian:
            ax.set_ylabel(
                r"$\displaystyle \frac{\mathrm{Frekvens}}{\mathrm{Klassebredde}}$",
                fontsize=fontsize,
                rotation=0,
                loc="top",
            )
        else:
            ax.set_ylabel(
                r"$\displaystyle \frac{\mathrm{Frequency}}{\mathrm{Binsize}}$",
                fontsize=fontsize,
                rotation=0,
                loc="top",
            )

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=16, loc="right")
    else:
        ax.set_xlabel(r"$x$", fontsize=16, loc="right")

    plt.xlim(-1, x[-1] + 4)
    plt.ylim(-0.5, max(heights) + 1)

    for i in range(len(x) - 1):
        ax.plot(
            [x[i], x[i + 1]], [heights[i], heights[i]], color="teal", lw=lw, alpha=alpha
        )
        ax.plot([x[i], x[i]], [0, heights[i]], color="teal", lw=lw, alpha=alpha)
        ax.plot([x[i + 1], x[i + 1]], [0, heights[i]], color="teal", lw=lw, alpha=alpha)

        ax.fill(
            [x[i], x[i + 1], x[i + 1], x[i]],
            [0, 0, heights[i], heights[i]],
            color="teal",
            alpha=0.3,
        )

    ax.grid(False)

    plt.subplots_adjust(
        left=0.25,
        bottom=0.068,
        top=0.885,
    )

    return fig, ax


def gca():
    return plt.gca()
