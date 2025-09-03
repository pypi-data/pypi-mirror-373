__all__ = ["broken_and_clip_axes", "scale_axes"]

from typing import Literal

from matplotlib.axes import Axes
from matplotlib.text import Text
from matplotlib.spines import Spine

from matplotlib.scale import FuncScale, FuncScaleLog
import matplotlib.transforms as mtransforms
from matplotlib.path import Path
import numpy as np

__version__ = "0.1.0"
__author__ = "Wu Yao <wuyao1997@qq.com>"


def create_scale(
    interval: list[tuple[float, float, float]],
    mode: Literal["linear", "log"] = "linear",
) -> FuncScale | FuncScaleLog:
    """Create a ScaleBase object by FuncScale or FuncScaleLog.

    Parameters
    ----------
    interval : list[Tuple[float, float, float]]
        [(a1, b1, f1), (a2, b2, f2), ...], where a1 < b1 < a2 < b2 < ...,
        f1 > 0, f2 > 0, ..., and f1, f2 are the scale factor of [a1, b1] and [a2, b2]...
    mode : Literal["linear", "log"], optional
        Scale mode, by default "linear"

    Returns
    -------
    FuncScale | FuncScaleLog
        ScaleBase object which could be passed to ax.set_xscale() or ax.set_yscale()

    Raises
    ------
    ValueError
        Input interval must be non-overlapping and sorted.
    ValueError
        Input scale factor must be positive.
    """
    x0, factor = [], []
    _prev_b = float("-inf")
    # It can be improved. Floating-point numbers are not suitable for direct comparison.
    for a, b, f in interval:
        if not ((a < b) and (_prev_b <= a)):
            raise ValueError("Input interval must be non-overlapping and sorted.")
        if f <= 0:
            raise ValueError("c must be positive")
        x0.extend([a, b]) if _prev_b < a else x0.extend([b])
        if _prev_b < a:
            factor.extend([f, 1])
        else:
            factor.insert(-1, f)
        _prev_b = b

    N = len(x0)

    def _forward(x):
        res = x.copy()

        ymin = x0[0]
        for n in range(N - 1):
            xmin, xmax = x0[n], x0[n + 1]
            cond = (x > xmin) & (x <= xmax)
            res[cond] = (x[cond] - xmin) * factor[n] + ymin
            ymin += (xmax - xmin) * factor[n]

        res[x > xmax] = (x[x > xmax] - xmax) * factor[-1] + ymin

        return res

    def _inverse(y):
        res = y.copy()

        ymin = x0[0]
        for n in range(N - 1):
            xmin, xmax = x0[n], x0[n + 1]
            ymax = ymin + (xmax - xmin) * factor[n]
            cond = (y > ymin) & (y <= ymax)
            res[cond] = (y[cond] - ymin) / factor[n] + xmin

            ymin = ymax

        res[y > ymax] = (y[y > ymax] - ymax) / factor[-1] + xmax

        return res

    if mode == "linear":
        return FuncScale(None, functions=(_forward, _inverse))
    else:
        return FuncScaleLog(None, functions=(_forward, _inverse))


def scale_axis(
    ax: Axes,
    interval: list[tuple[float, float, float]],
    axis: Literal["x", "y"] = "x",
    mode: Literal["linear", "log"] = "linear",
) -> None:
    """Scale the axis by the given interval and factor.

    Parameters
    ----------
    ax : Axes
        The axes to scale.
    interval : list[Tuple[float, float, float]]
        [(a1, b1, f1), (a2, b2, f2), ...], where a1 < b1 < a2 < b2 < ...,
        f1 > 0, f2 > 0, ..., and f1, f2 are the scale factor of [a1, b1] and [a2, b2]...
    axis : Literal["x", "y"], optional
        The axis to scale, by default "x"
    mode : Literal["linear", "log"], optional
        Scale mode, by default "linear"
    """
    if axis not in ["x", "y"]:
        raise ValueError("axis must be 'x' or 'y'")
    scale = create_scale(interval, mode=mode)
    if axis == "x":
        ax.set_xscale(scale)
    if axis == "y":
        ax.set_yscale(scale)
    return


def offset_data_point(ax: Axes, x, y, dx_pt=0, dy_pt=0):
    """
    将数据坐标 (x, y) 偏移 dx_pt, dy_pt 后，返回新的数据坐标。
    """
    # 数据坐标 -> 显示坐标（像素）
    x, y = float(x), float(y)
    x_disp, y_disp = ax.transData.transform((x, y))

    # 创建物理偏移
    dx_inch = dx_pt / 72
    dy_inch = dy_pt / 72
    offset = mtransforms.ScaledTranslation(dx_inch, dy_inch, ax.figure.dpi_scale_trans)
    x_off, y_off = offset.transform((x_disp, y_disp))

    # 显示坐标 -> 数据坐标
    x_new, y_new = ax.transData.inverted().transform((x_off, y_off))

    return x_new, y_new


def get_broken_points(ax, x, y, axis, gap, dx, dy) -> list[tuple[float, float]]:
    if axis not in ["x", "y"]:
        raise ValueError("which must be 'x' or 'y'")
    if axis == "x":
        gap_x, gap_y = gap / 2.0, 0
    else:
        gap_x, gap_y = 0, gap / 2.0

    x0, y0 = offset_data_point(ax, x, y, -gap_x - dx, -gap_y - dy)
    x1, y1 = offset_data_point(ax, x, y, -gap_x + dx, -gap_y + dy)
    x2, y2 = offset_data_point(ax, x, y, gap_x - dx, gap_y - dy)
    x3, y3 = offset_data_point(ax, x, y, gap_x + dx, gap_y + dy)
    return [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]


def xy2points(
    x: float | list[float], y: float | list[float]
) -> list[tuple[float, float]]:
    if isinstance(x, list) and isinstance(y, list):
        assert len(x) == len(y), (
            "if both x and y are list, they must have the same length"
        )
    if isinstance(x, (float, int)) and isinstance(y, (float, int)):
        return [(x, y)]
    if isinstance(x, list) and isinstance(y, (float, int)):
        assert all(isinstance(px, (int, float)) for px in x), (
            "if x is list, all elements must be float or int"
        )
        return [(x, y) for x in x]
    if isinstance(x, (float, int)) and isinstance(y, list):
        assert all(isinstance(py, (int, float)) for py in y), (
            "if y is list, all elements must be float or int"
        )
        return [(x, y) for y in y]

    raise ValueError("x and y must be list[float|int] or float")
    # assert isinstance(x, (float, int, list)) and isinstance(y, (float, int, list)), "x and y must be float, int or list[float|int]"


def add_broken_line(
    ax: Axes,
    x: float | list[float],
    y: float | list[float],
    axis="x",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    **kwargs,
):
    """
    在 Axes 中添加一条从 (x, y) 开始，偏移 dx_pt, dy_pt 的折线。
    """

    if axis not in ["x", "y"]:
        raise ValueError("which must be 'x' or 'y'")
    points = xy2points(x, y)

    if "color" not in kwargs:
        kwargs["color"] = "black"
    if "lw" not in kwargs:
        kwargs["lw"] = 1.5
    if "clip_on" not in kwargs:
        kwargs["clip_on"] = False

    results = []
    for x, y in points:
        points = get_broken_points(ax, x, y, axis, gap, dx, dy)
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        l1, l2 = ax.plot(x[:2], y[:2], x[2:], y[2:], **kwargs)
        results.append((l1, l2))

    return results


def get_axis_clip_path(
    ax: Axes,
    x: float | list[float],
    y: float | list[float],
    axis="x",
    gap=5,
    dx=3,
    dy=3,
) -> Path:
    # Edge marker points, Extend by gap distance to avoid cutting off spine ends
    if axis == "x":
        xlow, xhigh = ax.get_xlim()
        ylow = y[0] if isinstance(y, list) else y
        yhigh = y[-1] if isinstance(y, list) else y
        x0, y0 = offset_data_point(ax, xlow, ylow, -gap - dx, -dy)
        x1, y1 = offset_data_point(ax, xlow, ylow, -gap + dx, dy)
        x2, y2 = offset_data_point(ax, xhigh, yhigh, gap - dx, -dy)
        x3, y3 = offset_data_point(ax, xhigh, yhigh, gap + dx, dy)
    else:
        ylow, yhigh = ax.get_ylim()
        xlow = x[0] if isinstance(x, list) else x
        xhigh = x[-1] if isinstance(x, list) else x
        x0, y0 = offset_data_point(ax, xlow, ylow, -dx, -gap - dy)
        x1, y1 = offset_data_point(ax, xlow, ylow, dx, -gap + dy)
        x2, y2 = offset_data_point(ax, xhigh, yhigh, -dx, gap - dy)
        x3, y3 = offset_data_point(ax, xhigh, yhigh, dx, gap + dy)

    points_lst = [(x0, y0), (x1, y1)]
    for x, y in xy2points(x, y):
        points = get_broken_points(ax, x, y, axis, gap, dx, dy)
        points_lst.extend(points)
    points_lst.extend([(x2, y2), (x3, y3)])

    N = int(len(points_lst) / 4)
    vertices, codes = [], []
    for i in range(N):
        points = points_lst[i * 4 : i * 4 + 4]
        vertices.extend([points[0], points[1], points[3], points[2], points[0]])
        codes.extend([Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY])

    path = Path(vertices, codes)
    return path


def get_axes_clip_path(ax: Axes, x, y, gap: float = 5.0) -> Path:
    xlow, xhigh = ax.get_xlim()
    xlst = [xlow]
    for _x in x:
        x0, _ = offset_data_point(ax, _x, 0, -gap / 2.0)
        x1, _ = offset_data_point(ax, _x, 0, gap / 2.0)
        xlst.extend([x0, x1])
    xlst.append(xhigh)

    ylow, yhigh = ax.get_ylim()
    ylst = [ylow]
    for _y in y:
        _, y0 = offset_data_point(ax, 0, _y, 0, -gap / 2.0)
        _, y1 = offset_data_point(ax, 0, _y, 0, gap / 2.0)
        ylst.extend([y0, y1])
    ylst.append(yhigh)

    xlst = [xlst[i : i + 2] for i in range(0, len(xlst), 2)]
    ylst = [ylst[i : i + 2] for i in range(0, len(ylst), 2)]

    vertices, codes = [], []
    for x in xlst:
        for y in ylst:
            x0, x1 = x[0], x[1]
            y0, y1 = y[0], y[1]

            p0 = (x0, y0)
            p1 = (x1, y0)
            p2 = (x1, y1)
            p3 = (x0, y1)
            vertices.extend([p0, p1, p2, p3, p0])
            codes.extend([Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY])

    return Path(vertices, codes)


def scale_axes(
    ax: Axes,
    x_interval: list[tuple[float, float, float]],
    y_interval: list[tuple[float, float, float]],
    mode: Literal["linear", "log"] = "linear",
):
    if x_interval:
        scale_axis(ax, x_interval, axis="x", mode=mode)
    if y_interval:
        scale_axis(ax, y_interval, axis="y", mode=mode)
    return


def add_broken_line_in_axis(
    ax: Axes,
    x: list[float] | float = None,
    y: list[float] | float = None,
    which: Literal["lower", "upper", "both"] = "both",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    **kwargs,
):
    if which not in ["lower", "upper", "both"]:
        raise ValueError("which must be 'lower', 'upper' or 'both'")

    if x:
        ylow, yhigh = ax.get_ylim()
        if which in ["lower", "both"]:
            add_broken_line(ax, x, ylow, axis="x", gap=gap, dx=dx, dy=dy, **kwargs)
        if which in ["upper", "both"]:
            add_broken_line(ax, x, yhigh, axis="x", gap=gap, dx=dx, dy=dy, **kwargs)

    if y:
        xlow, xhigh = ax.get_xlim()
        if which in ["lower", "both"]:
            add_broken_line(ax, xlow, y, axis="y", gap=gap, dx=dx, dy=dy, **kwargs)
        if which in ["upper", "both"]:
            add_broken_line(ax, xhigh, y, axis="y", gap=gap, dx=dx, dy=dy, **kwargs)
    return


def clip_axes(
    ax: Axes,
    x: list[float] | float = None,
    y: list[float] | float = None,
    which: Literal["lower", "upper", "both"] = "both",
    axes_clip: bool = True,
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
):
    if which not in ["lower", "upper", "both"]:
        raise ValueError("which must be 'lower', 'upper' or 'both'")
    if x:
        ylow, yhigh = ax.get_ylim()
        if which in ["lower", "both"]:
            clip_path = get_axis_clip_path(ax, x, ylow, axis="x", gap=gap, dx=dx, dy=dy)
            ax.spines["bottom"].set_clip_path(clip_path, transform=ax.transData)
        if which in ["high", "both"]:
            clip_path = get_axis_clip_path(
                ax, x, yhigh, axis="x", gap=gap, dx=dx, dy=dy
            )
            ax.spines["top"].set_clip_path(clip_path, transform=ax.transData)

    if y:
        xlow, xhigh = ax.get_xlim()
        if which in ["lower", "both"]:
            clip_path = get_axis_clip_path(ax, xlow, y, axis="y", gap=gap, dx=dx, dy=dy)
            ax.spines["left"].set_clip_path(clip_path, transform=ax.transData)
        if which in ["high", "both"]:
            clip_path = get_axis_clip_path(
                ax, xhigh, y, axis="y", gap=gap, dx=dx, dy=dy
            )
            ax.spines["right"].set_clip_path(clip_path, transform=ax.transData)

    if axes_clip:
        axes_clip_path = get_axes_clip_path(ax, x, y, gap)

        for art in ax.get_children():
            if isinstance(art, (Text, Spine)):
                continue
            if id(art) == id(ax.patch):
                continue
            art.set_clip_path(axes_clip_path, ax.transData)
    return


def broken_and_clip_axes(
    ax: Axes,
    x: list[float] | float = None,
    y: list[float] | float = None,
    axes_clip: bool = True,
    which: Literal["lower", "upper", "both"] = "both",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    **kwargs,
):
    add_broken_line_in_axis(ax, x, y, which, gap, dx, dy, **kwargs)
    clip_axes(ax, x, y, which, axes_clip, gap, dx, dy)
    return
