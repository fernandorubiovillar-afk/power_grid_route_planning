from __future__ import annotations

from typing import Dict, List, Tuple, Callable
import time
import pandas as pd

from .algorithms import a_star, AStarResult, a_star_fast, AStarFastResult, dijkstra, ucs
from .heuristics import HeuristicBundle



def run_single(
    start: str,
    goal: str,
    distance_df: pd.DataFrame,
    heuristic: HeuristicBundle,
) -> AStarResult:
    """Ejecuta A* FULL una vez (para sacar árbol de búsqueda / event_info)."""
    return a_star(start, goal, distance_df, heuristic.h)


# -------------------------
# 1) Benchmarks entre heurísticas (A*)
# -------------------------
def run_benchmark_case_astar(
    start: str,
    goal: str,
    distance_df: pd.DataFrame,
    heuristic: HeuristicBundle,
    repeats: int = 50,
) -> Dict:
    times_ms: List[float] = []
    last: AStarFastResult | None = None

    for _ in range(repeats):
        t0 = time.perf_counter()
        last = a_star_fast(start, goal, distance_df, heuristic.h)
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000.0)

    assert last is not None

    expanded = int(last.stats["expanded_nodes"])
    mean_ms = sum(times_ms) / len(times_ms)

    row = {
        "case": f"{start}->{goal}",
        "start": start,
        "goal": goal,
        "label": heuristic.name,
        "kind": "heuristic",
        "found": last.found,
        "exec_time_ms_mean": mean_ms,
        "exec_time_ms_min": min(times_ms),
        "expanded_nodes": expanded,
        "generated_nodes": int(last.stats["generated_nodes"]),
        "max_frontier": int(last.stats["max_frontier"]),
        "reopen_updates": int(last.stats["reopen_updates"]),
        "total_cost": last.total_cost,
        "path_length": (len(last.path) - 1) if last.path else None,
        "path": " -> ".join(last.path) if last.path else None,
        "ms_per_expanded": (mean_ms / expanded) if expanded > 0 else None,
    }
    return row


def benchmark_heuristics(
    cases: List[Tuple[str, str]],
    heuristics: List[HeuristicBundle],
    distance_df: pd.DataFrame,
    repeats: int = 50,
) -> pd.DataFrame:
    rows = []
    for s, g in cases:
        for h in heuristics:
            rows.append(run_benchmark_case_astar(s, g, distance_df, h, repeats=repeats))

    df = pd.DataFrame(rows)
    df = df.sort_values(["start", "goal", "label"]).reset_index(drop=True)
    return df


def pick_best_label_overall(df: pd.DataFrame) -> str:
    """
    Escoge el 'label' ganador (heurística) globalmente usando ranking por caso en:
    expanded_nodes, exec_time_ms_mean, ms_per_expanded, max_frontier.
    Menor es mejor.
    """
    metrics = ["expanded_nodes", "exec_time_ms_mean", "ms_per_expanded", "max_frontier"]
    df = df.copy()
    df = df[df["found"] == True]
    if df.empty:
        # fallback: el primero que haya
        return str(df["label"].iloc[0]) if "label" in df.columns and len(df) else ""

    labels = sorted(df["label"].unique().tolist())
    score = {lb: 0.0 for lb in labels}

    for case in sorted(df["case"].unique().tolist()):
        dfc = df[df["case"] == case].copy()
        if dfc.empty:
            continue

        for m in metrics:
            d = dfc.dropna(subset=[m])
            if d.empty:
                continue
            # ranking: menor valor => rank 1
            d = d.sort_values(m, ascending=True)
            # asignar rank (ties -> mismo rank mínimo)
            best = float(d[m].iloc[0])
            # rank simple: 1..n
            ranks = {row["label"]: i + 1 for i, (_, row) in enumerate(d.iterrows())}
            # ties: todos con el mismo valor que best tienen rank 1
            for _, row in d.iterrows():
                if float(row[m]) == best:
                    ranks[row["label"]] = 1

            for lb, rk in ranks.items():
                score[lb] += float(rk)

    # menor score gana
    return min(score.items(), key=lambda kv: kv[1])[0]


# -------------------------
# 2) Benchmarks entre algoritmos (A* vs Dijkstra vs UCS)
# -------------------------
def _bench_algo(
    start: str,
    goal: str,
    distance_df: pd.DataFrame,
    algo_name: str,
    algo_fn: Callable[[], Tuple[bool, float | None, List[str] | None, Dict[str, float | int]]],
    repeats: int,
) -> Dict:
    times_ms: List[float] = []
    last_found = False
    last_cost = None
    last_path = None
    last_stats: Dict[str, float | int] = {}

    for _ in range(repeats):
        t0 = time.perf_counter()
        found, cost, path, stats = algo_fn()
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000.0)
        last_found, last_cost, last_path, last_stats = found, cost, path, stats

    expanded = int(last_stats.get("expanded_nodes", 0))
    mean_ms = sum(times_ms) / len(times_ms)

    return {
        "case": f"{start}->{goal}",
        "start": start,
        "goal": goal,
        "label": algo_name,                # <-- columna común
        "kind": "algorithm",
        "found": last_found,
        "exec_time_ms_mean": mean_ms,
        "exec_time_ms_min": min(times_ms),
        "expanded_nodes": expanded,
        "generated_nodes": int(last_stats.get("generated_nodes", 0)),
        "max_frontier": int(last_stats.get("max_frontier", 0)),
        "reopen_updates": int(last_stats.get("reopen_updates", 0)),
        "total_cost": last_cost,
        "path_length": (len(last_path) - 1) if last_path else None,
        "path": " -> ".join(last_path) if last_path else None,
        "ms_per_expanded": (mean_ms / expanded) if expanded > 0 else None,
    }


def benchmark_algorithms(
    cases: List[Tuple[str, str]],
    distance_df: pd.DataFrame,
    astar_heuristic: HeuristicBundle,
    repeats: int = 50,
) -> pd.DataFrame:
    rows = []
    for s, g in cases:
        # A* con heurística ganadora
        rows.append(
            _bench_algo(
                s, g, distance_df,
                algo_name=f"A*_({astar_heuristic.name})",
                algo_fn=lambda s=s, g=g: (
                    (res := a_star_fast(s, g, distance_df, astar_heuristic.h)).found,
                    res.total_cost,
                    res.path,
                    res.stats,
                ),
                repeats=repeats,
            )
        )

        # Dijkstra
        rows.append(
            _bench_algo(
                s, g, distance_df,
                algo_name="Dijkstra",
                algo_fn=lambda s=s, g=g: (
                    (res := dijkstra(s, g, distance_df)).found,
                    res.total_cost,
                    res.path,
                    res.stats,
                ),
                repeats=repeats,
            )
        )

        # UCS
        rows.append(
            _bench_algo(
                s, g, distance_df,
                algo_name="UCS",
                algo_fn=lambda s=s, g=g: (
                    (res := ucs(s, g, distance_df)).found,
                    res.total_cost,
                    res.path,
                    res.stats,
                ),
                repeats=repeats,
            )
        )

    df = pd.DataFrame(rows)
    df = df.sort_values(["start", "goal", "label"]).reset_index(drop=True)
    return df
