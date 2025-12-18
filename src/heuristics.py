from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple
import numpy as np
import pandas as pd

Coords = Dict[str, Tuple[float, float]]


def build_coords_map(list_nodes: List[List]) -> Coords:
    """list_nodes = [nodes, coord] -> {"A": (x,y), ...}"""
    nodes = list_nodes[0]
    coords = list_nodes[1]
    return {n: (float(coords[i][0]), float(coords[i][1])) for i, n in enumerate(nodes)}


def euclidean(a: str, b: str, coords: Coords) -> float:
    ax, ay = coords[a]
    bx, by = coords[b]
    return float(np.hypot(bx - ax, by - ay))


def manhattan(a: str, b: str, coords: Coords) -> float:
    ax, ay = coords[a]
    bx, by = coords[b]
    return float(abs(bx - ax) + abs(by - ay))


def chebyshev(a: str, b: str, coords: Coords) -> float:
    ax, ay = coords[a]
    bx, by = coords[b]
    return float(max(abs(bx - ax), abs(by - ay)))


def compute_scaling_k(distance_df: pd.DataFrame, coords: Coords, metric: str) -> float:
    """
    k = min_{(u,v) in E} cost(u,v) / d_metric(u,v)
    Usando cost(u,v)=real (dist_km*FCC). Garantiza h(n)=k*d_metric(n,goal) admisible.

    metric in {"manhattan","chebyshev","euclidean"}
    """
    metric = metric.lower().strip()
    if metric not in {"manhattan", "chebyshev", "euclidean"}:
        raise ValueError(f"metric must be one of manhattan/chebyshev/euclidean, got {metric}")

    ratios = []
    for _, row in distance_df.iterrows():
        u = row["start_node"]
        v = row["end_node"]
        cost = float(row["real"])

        if metric == "manhattan":
            d = manhattan(u, v, coords)
        elif metric == "chebyshev":
            d = chebyshev(u, v, coords)
        else:
            d = euclidean(u, v, coords)

        if d > 0:
            ratios.append(cost / d)

    if not ratios:
        return 0.0

    k = float(min(ratios))
    return max(0.0, k)


@dataclass(frozen=True)
class HeuristicBundle:
    """Empaqueta una heurística como callable h(node)->float, y su metadata."""
    name: str
    h: Callable[[str], float]


def make_heuristic(
    name: str,
    distance_df: pd.DataFrame,
    coords: Coords,
    goal: str,
    fcc_min: float = 2.0,
) -> HeuristicBundle:
    """
    name in {"euclidean", "manhattan_scaled", "chebyshev_scaled"}

    - euclidean: h = fcc_min * euclidean_distance
    - manhattan_scaled: h = kM * manhattan_distance (kM calculado desde el grafo con coste real)
    - chebyshev_scaled: h = kC * chebyshev_distance (kC calculado desde el grafo con coste real)
    """
    name = name.lower().strip()

    if name == "euclidean":
        def h(n: str) -> float:
            return float(fcc_min * euclidean(n, goal, coords))
        return HeuristicBundle("euclidean_x_fccmin", h)

    if name == "manhattan_scaled":
        kM = compute_scaling_k(distance_df, coords, metric="manhattan")

        def h(n: str) -> float:
            return float(kM * manhattan(n, goal, coords))
        return HeuristicBundle("manhattan_scaled", h)

    if name == "chebyshev_scaled":
        kC = compute_scaling_k(distance_df, coords, metric="chebyshev")

        def h(n: str) -> float:
            return float(kC * chebyshev(n, goal, coords))
        return HeuristicBundle("chebyshev_scaled", h)

    raise ValueError(f"Unknown heuristic name: {name}")
