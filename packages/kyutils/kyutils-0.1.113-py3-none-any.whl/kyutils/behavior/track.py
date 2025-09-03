from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Optional, Tuple, List

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra

import matplotlib.pyplot as plt
from matplotlib.axes import Axes


@dataclass(frozen=True)
class GridGraph:
    """8-neighbor graph over occupied bins inferred from (x, y) samples.

    Attributes
    ----------
    adj : csr_matrix, shape (n_nodes, n_nodes)
        Sparse adjacency (edge weights, physical units).
    centers : np.ndarray, shape (n_nodes, 2)
        (x, y) bin centers for each node index.
    ij : np.ndarray, shape (n_nodes, 2)
        (i=row, j=col) integer grid coordinates for each node.
    index_of_ij : dict[tuple[int, int], int]
        Mapping (i, j) -> node index.
    dx : float
        Bin size along x (columns).
    dy : float
        Bin size along y (rows).
    x0 : float
        Bin origin along x. Bin j spans [x0 + j*dx, x0 + (j+1)*dx).
    y0 : float
        Bin origin along y. Bin i spans [y0 + i*dy, y0 + (i+1)*dy).
    """

    adj: csr_matrix
    centers: NDArray[np.float64]
    ij: NDArray[np.int_]
    index_of_ij: Dict[tuple[int, int], int]
    dx: float
    dy: float
    x0: float
    y0: float


def _compute_bin_origin(
    xy: NDArray[np.float64], dx: float, dy: float, mode: Literal["min", "zero"] = "min"
) -> Tuple[float, float]:
    """Choose bin origin (x0, y0)."""
    if mode == "zero":
        return 0.0, 0.0
    if mode == "min":
        x0 = float(np.floor(np.min(xy[:, 0]) / dx) * dx)
        y0 = float(np.floor(np.min(xy[:, 1]) / dy) * dy)
        return x0, y0
    raise ValueError("origin_mode must be 'min' or 'zero'.")


def bin_points(
    xy_t: NDArray[np.float64],
    *,
    bin_size: float | Tuple[float, float],
    origin: Optional[Tuple[float, float]] = None,
    origin_mode: Literal["min", "zero"] = "min",
) -> Tuple[NDArray[np.int_], NDArray[np.float64], float, float, float, float]:
    """Bin (x, y) samples into a rectilinear grid and return occupied bins.

    Parameters
    ----------
    xy_t : np.ndarray, shape (n_time, 2)
        Sequence of (x, y) locations.
    bin_size : float | tuple[float, float]
        Bin size. If float, uses square bins (dx=dy=bin_size). Otherwise (dx, dy).
    origin : Optional[tuple[float, float]], default=None
        Custom (x0, y0). If provided, overrides `origin_mode`.
    origin_mode : {"min", "zero"}, default="min"
        How to auto-pick origin when `origin` is None.

    Returns
    -------
    ij : np.ndarray, shape (n_nodes, 2), dtype=int
        Integer bin indices of *occupied* bins, deduplicated.
    centers : np.ndarray, shape (n_nodes, 2), dtype=float
        Center coordinates of the occupied bins in (x, y).
    dx : float
        Bin size along x.
    dy : float
        Bin size along y.
    x0 : float
        Chosen origin along x.
    y0 : float
        Chosen origin along y.
    """
    if xy_t.ndim != 2 or xy_t.shape[1] != 2:
        raise ValueError("xy_t must have shape (n_time, 2)")

    dx, dy = (
        (float(bin_size), float(bin_size))
        if np.isscalar(bin_size)
        else map(float, bin_size)
    )
    xy_t = xy_t.astype(np.float64, copy=False)

    if origin is None:
        x0, y0 = _compute_bin_origin(xy_t, dx, dy, origin_mode)
    else:
        x0, y0 = float(origin[0]), float(origin[1])

    j = np.floor((xy_t[:, 0] - x0) / dx).astype(int)
    i = np.floor((xy_t[:, 1] - y0) / dy).astype(int)
    ij_all = np.column_stack([i, j])

    order = np.lexsort((ij_all[:, 1], ij_all[:, 0]))
    ij_sorted = ij_all[order]
    uniq = np.ones(ij_sorted.shape[0], dtype=bool)
    uniq[1:] = np.any(np.diff(ij_sorted, axis=0) != 0, axis=1)
    ij = ij_sorted[uniq]

    cx = x0 + (ij[:, 1] + 0.5) * dx
    cy = y0 + (ij[:, 0] + 0.5) * dy
    centers = np.column_stack([cx, cy]).astype(np.float64)

    return ij, centers, dx, dy, x0, y0


def build_graph_from_xy(
    xy_t: NDArray[np.float64],
    *,
    bin_size: float | Tuple[float, float],
    origin: Optional[Tuple[float, float]] = None,
    origin_mode: Literal["min", "zero"] = "min",
) -> GridGraph:
    """Build an 8-neighbor graph from raw (x, y) samples with **physical** weights.

    Edge weights (physical units):
        horizontal: dx
        vertical:   dy
        diagonal:   hypot(dx, dy)

    Parameters
    ----------
    xy_t : np.ndarray, shape (n_time, 2)
        (x, y) positions over time.
    bin_size : float | tuple[float, float]
        Bin size (dx or (dx, dy)).
    origin : Optional[tuple[float, float]], default=None
        Custom origin (x0, y0). If None, uses `origin_mode`.
    origin_mode : {"min", "zero"}, default="min"
        How to auto-pick origin when `origin` is None.

    Returns
    -------
    GridGraph
        Undirected sparse graph with correct single-copy weights.
    """
    ij, centers, dx, dy, x0, y0 = bin_points(
        xy_t, bin_size=bin_size, origin=origin, origin_mode=origin_mode
    )

    n = ij.shape[0]
    keys = [tuple(rc) for rc in ij.tolist()]
    index_of_ij = {k: idx for idx, k in enumerate(keys)}

    # 8-neighbor offsets
    nbrs = np.array(
        [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ],
        dtype=int,
    )

    # Directional weights (physical)
    w_dir = np.empty(8, dtype=float)
    for k, (di, dj) in enumerate(nbrs):
        if abs(di) + abs(dj) == 2:
            w_dir[k] = float(np.hypot(dx, dy))
        elif di != 0:
            w_dir[k] = float(dy)
        else:
            w_dir[k] = float(dx)

    # Collect edges once, then unique-then-mirror
    rows_raw: list[int] = []
    cols_raw: list[int] = []
    data_raw: list[float] = []

    for k, (di, dj) in enumerate(nbrs):
        nbr_ij = ij + np.array([di, dj], dtype=int)
        nbr_idx = [index_of_ij.get((int(ii), int(jj)), -1) for ii, jj in nbr_ij]
        nbr_idx = np.asarray(nbr_idx, dtype=int)
        valid = nbr_idx >= 0
        if not np.any(valid):
            continue
        rows_raw.append(np.nonzero(valid)[0])
        cols_raw.append(nbr_idx[valid])
        data_raw.append(np.full(np.count_nonzero(valid), w_dir[k], dtype=float))

    if len(rows_raw) == 0:
        adj = csr_matrix((n, n))
    else:
        row_raw = np.concatenate(rows_raw)
        col_raw = np.concatenate(cols_raw)
        w_raw = np.concatenate(data_raw)

        # --- UNIQUE-THEN-MIRROR (prevents double-weighting) ---
        keep = row_raw < col_raw
        row = row_raw[keep]
        col = col_raw[keep]
        w = w_raw[keep]

        row_sym = np.concatenate([row, col])
        col_sym = np.concatenate([col, row])
        w_sym = np.concatenate([w, w])
        # ------------------------------------------------------

        adj = coo_matrix((w_sym, (row_sym, col_sym)), shape=(n, n)).tocsr()

    return GridGraph(
        adj=adj,
        centers=centers,
        ij=ij,
        index_of_ij=index_of_ij,
        dx=float(dx),
        dy=float(dy),
        x0=float(x0),
        y0=float(y0),
    )


def build_graph_from_binned(
    ij: NDArray[np.int_],
    *,
    dx: float,
    dy: float,
    x0: float,
    y0: float,
) -> GridGraph:
    """Build an undirected 8-neighbor grid graph (physical weights) from occupied bins.

    Parameters
    ----------
    ij : np.ndarray, shape (n_nodes, 2), dtype=int
        Occupied bin indices (i=row, j=col).
    dx : float
        Bin size along x (columns).
    dy : float
        Bin size along y (rows).
    x0 : float
        Origin along x. Bin j spans [x0 + j*dx, x0 + (j+1)*dx).
    y0 : float
        Origin along y. Bin i spans [y0 + i*dy, y0 + (i+1)*dy).

    Returns
    -------
    GridGraph
        Sparse undirected graph with edge weights in physical units.

    Notes
    -----
    - Uses unique-then-mirror to avoid duplicate (u,v) entries that would sum in CSR.
    - Edge weights:
      - horizontal moves cost ``dx``,
      - vertical moves cost ``dy``,
      - diagonal moves cost ``hypot(dx, dy)``.
    """
    if ij.ndim != 2 or ij.shape[1] != 2:
        raise ValueError("ij must have shape (n_nodes, 2)")

    ij = ij.astype(int, copy=False)
    n = ij.shape[0]

    # Map (i, j) -> node index
    keys = [tuple(rc) for rc in ij.tolist()]
    index_of_ij: Dict[Tuple[int, int], int] = {k: idx for idx, k in enumerate(keys)}

    # Bin centers (x, y)
    centers = np.column_stack(
        [x0 + (ij[:, 1] + 0.5) * dx, y0 + (ij[:, 0] + 0.5) * dy]
    ).astype(np.float64)

    # 8-neighbor offsets
    nbrs = np.array(
        [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ],
        dtype=int,
    )

    # Directional weights (physical units)
    w_dir = np.empty(8, dtype=float)
    for k, (di, dj) in enumerate(nbrs):
        if abs(di) + abs(dj) == 2:  # diagonal
            w_dir[k] = float(np.hypot(dx, dy))
        elif di != 0:  # vertical
            w_dir[k] = float(dy)
        else:  # horizontal
            w_dir[k] = float(dx)

    # Collect raw directed edges from the sweep
    rows_raw: List[int] = []
    cols_raw: List[int] = []
    data_raw: List[float] = []

    for k, (di, dj) in enumerate(nbrs):
        nbr_ij = ij + np.array([di, dj], dtype=int)
        nbr_idx = [index_of_ij.get((int(ii), int(jj)), -1) for ii, jj in nbr_ij]
        nbr_idx = np.asarray(nbr_idx, dtype=int)
        valid = nbr_idx >= 0
        if not np.any(valid):
            continue
        rows_raw.append(np.nonzero(valid)[0])
        cols_raw.append(nbr_idx[valid])
        data_raw.append(np.full(np.count_nonzero(valid), w_dir[k], dtype=float))

    if len(rows_raw) == 0:
        adj = csr_matrix((n, n))
    else:
        row_raw = np.concatenate(rows_raw)
        col_raw = np.concatenate(cols_raw)
        w_raw = np.concatenate(data_raw)

        # --- unique-then-mirror (prevents doubling weights) ---
        keep = row_raw < col_raw
        row = row_raw[keep]
        col = col_raw[keep]
        w = w_raw[keep]

        row_sym = np.concatenate([row, col])
        col_sym = np.concatenate([col, row])
        w_sym = np.concatenate([w, w])
        # ------------------------------------------------------

        adj = coo_matrix((w_sym, (row_sym, col_sym)), shape=(n, n)).tocsr()

    return GridGraph(
        adj=adj,
        centers=centers,
        ij=ij,
        index_of_ij=index_of_ij,
        dx=float(dx),
        dy=float(dy),
        x0=float(x0),
        y0=float(y0),
    )


def shortest_distances(
    graph: GridGraph,
    sources: Iterable[int],
    targets: Optional[Iterable[int]] = None,
) -> Tuple[NDArray[np.float64], NDArray[np.int_]]:
    """Dijkstra shortest-path distances on the 8-neighbor grid.

    Parameters
    ----------
    graph : GridGraph
        Output of `build_graph_from_xy` or `build_graph_from_binned`.
    sources : Iterable[int]
        Source node indices (into graph.centers).
    targets : Optional[Iterable[int]], default=None
        If provided, only return distances to these target indices.

    Returns
    -------
    dists : np.ndarray, shape (n_sources, n_targets) or (n_sources, n_nodes)
        Shortest-path distances; `np.inf` if unreachable.
    nodes : np.ndarray, shape (n_targets,) or (n_nodes,)
        Node indices corresponding to columns of `dists`.
    """
    src = np.asarray(list(sources), dtype=int)
    if src.size == 0:
        raise ValueError("sources must be non-empty")

    if targets is None:
        d = dijkstra(csgraph=graph.adj, directed=False, indices=src)
        nodes = np.arange(graph.adj.shape[0], dtype=int)
        return d, nodes

    tgt = np.asarray(list(targets), dtype=int)
    full = dijkstra(csgraph=graph.adj, directed=False, indices=src)
    return full[:, tgt], tgt


def nearest_node_index(
    graph: GridGraph,
    x: float,
    y: float,
    *,
    mode: Literal["grid", "euclidean", "grid_expand"] = "grid_expand",
    max_radius: int = 4,
) -> int:
    """Snap (x, y) to an existing node index.

    Parameters
    ----------
    graph : GridGraph
        The graph.
    x : float
        Query x.
    y : float
        Query y.
    mode : {"grid", "euclidean", "grid_expand"}, default="grid_expand"
        - "grid": snap to nearest grid cell; fail if empty.
        - "euclidean": closest center by Euclidean distance; always succeeds if graph nonempty.
        - "grid_expand": snap, else expand Chebyshev shells to nearest occupied bin.
    max_radius : int, default=4
        Max Chebyshev radius for "grid_expand".

    Returns
    -------
    int
        Node index into ``graph.centers``.

    Raises
    ------
    ValueError
        If the graph is empty, inputs are non-finite where required, or no node
        is found within ``max_radius`` for ``mode="grid_expand"``.
    """
    if graph.centers.shape[0] == 0:
        raise ValueError("Graph has no nodes.")

    if mode == "euclidean":
        # Require finite query; guard against any non-finite centers by masking.
        if not (np.isfinite(x) and np.isfinite(y)):
            raise ValueError("x and y must be finite for mode='euclidean'.")

        diffs = graph.centers - np.array([x, y], dtype=float)
        # Distance squared; set non-finite rows to +inf so they won't win argmin.
        d2 = np.einsum("ij,ij->i", diffs, diffs)
        bad = ~np.isfinite(d2)
        if np.all(bad):
            raise ValueError("All graph centers are non-finite.")
        d2[bad] = np.inf
        return int(np.argmin(d2))

    # The grid-based modes require finite x, y, and positive finite dx, dy.
    if not (np.isfinite(x) and np.isfinite(y)):
        raise ValueError("x and y must be finite for grid-based modes.")
    if not (np.isfinite(graph.dx) and np.isfinite(graph.dy)):
        raise ValueError("graph.dx and graph.dy must be finite.")
    if graph.dx <= 0 or graph.dy <= 0:
        raise ValueError("graph.dx and graph.dy must be positive.")

    j = int(np.floor((x - graph.x0) / graph.dx))
    i = int(np.floor((y - graph.y0) / graph.dy))

    if mode == "grid":
        idx = graph.index_of_ij.get((i, j), -1)
        if idx < 0:
            raise ValueError("Nearest grid location has no node.")
        return idx

    # mode == "grid_expand"
    idx = graph.index_of_ij.get((i, j), -1)
    if idx >= 0:
        return int(idx)

    for r in range(1, max_radius + 1):
        ii = np.arange(i - r, i + r + 1, dtype=int)
        jj = np.arange(j - r, j + r + 1, dtype=int)
        ring = np.unique(
            np.vstack(
                [
                    np.column_stack([np.full_like(jj, i - r), jj]),
                    np.column_stack([np.full_like(jj, i + r), jj]),
                    np.column_stack([ii, np.full_like(ii, j - r)]),
                    np.column_stack([ii, np.full_like(ii, j + r)]),
                ]
            ),
            axis=0,
        )
        for ii_jj in ring:
            hit = graph.index_of_ij.get((int(ii_jj[0]), int(ii_jj[1])), -1)
            if hit >= 0:
                return int(hit)

    raise ValueError("No existing node found within max_radius in grid_expand mode.")


def plot_grid_graph(
    graph: GridGraph,
    *,
    ax: Optional[Axes] = None,
    node_color: str = "tab:blue",
    edge_color: str = "lightgray",
    show_indices: bool = False,
    node_size: float = 40.0,
) -> Axes:
    """Visualize a GridGraph with matplotlib.

    Parameters
    ----------
    graph : GridGraph
        Graph built with `build_graph_from_xy` or `build_graph_from_binned`.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw on. If None, create a new one.
    node_color : str, default="tab:blue"
        Color for nodes.
    edge_color : str, default="lightgray"
        Color for edges.
    show_indices : bool, default=False
        If True, annotate each node with its index.
    node_size : float, default=40.0
        Marker size for nodes.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot.
    """
    if ax is None:
        fig, ax = plt.subplots()

    centers = graph.centers
    n_nodes = centers.shape[0]

    # Draw edges
    adj = graph.adj
    row, col = adj.nonzero()
    for r, c in zip(row, col):
        if r < c:  # undirected graph: plot each edge once
            x1, y1 = centers[r]
            x2, y2 = centers[c]
            ax.plot([x1, x2], [y1, y2], color=edge_color, lw=0.8, zorder=1)

    # Draw nodes
    ax.scatter(
        centers[:, 0],
        centers[:, 1],
        c=node_color,
        s=node_size,
        edgecolors="k",
        linewidths=0.5,
        zorder=2,
    )

    # Optionally annotate indices
    if show_indices:
        for idx, (x, y) in enumerate(centers):
            ax.text(x, y, str(idx), fontsize=8, ha="center", va="center", zorder=3)

    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return ax
