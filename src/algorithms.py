from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
import heapq
import pandas as pd


# =========================================================
# Utilidades comunes
# =========================================================
def build_adjacency(distance_df: pd.DataFrame) -> Dict[str, List[Tuple[str, float]]]:
    """Adjacency list con coste real (dist_km * FCC)."""
    adj: Dict[str, List[Tuple[str, float]]] = {}
    nodes = set(distance_df["start_node"]).union(set(distance_df["end_node"]))
    for n in nodes:
        adj[n] = []
    for _, r in distance_df.iterrows():
        u = r["start_node"]
        v = r["end_node"]
        w = float(r["real"])
        adj[u].append((v, w))
    return adj


def reconstruct_path(came_from: Dict[str, Optional[str]], goal: str) -> List[str]:
    path = [goal]
    cur = goal
    while came_from.get(cur) is not None:
        cur = came_from[cur]  # type: ignore
        path.append(cur)
    path.reverse()
    return path


# =========================================================
# A*
# =========================================================
@dataclass
class AStarResult:
    found: bool
    start: str
    goal: str
    path: Optional[List[str]]
    total_cost: Optional[float]
    node_info: pd.DataFrame
    event_info: pd.DataFrame
    stats: Dict[str, float | int]


def a_star(
    start: str,
    goal: str,
    distance_df: pd.DataFrame,
    heuristic_h: Callable[[str], float],
) -> AStarResult:
    """
    A* (graph-search) con:
    - heapq (priority queue)
    - g_score para mejor coste conocido
    - came_from para reconstrucción
    - node_info: g,h,f,expansion_order,parent
    - event_info: eventos (para tree_viz)
    """
    adj = build_adjacency(distance_df)

    stats: Dict[str, float | int] = {
        "expanded_nodes": 0,
        "generated_nodes": 0,
        "max_frontier": 0,
        "reopen_updates": 0,
    }

    INF = float("inf")
    g_score: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}

    node_info_dict: Dict[str, Dict[str, float | int | None | str]] = {}
    event_records: Dict[str, Dict[str, float | int | None | str]] = {}
    event_id_counter = 0

    def new_event_id(state: str) -> str:
        nonlocal event_id_counter
        event_id_counter += 1
        return f"{state}_{event_id_counter}"

    # init
    h0 = float(heuristic_h(start))
    f0 = 0.0 + h0

    tie = 0
    start_eid = new_event_id(start)
    frontier: List[Tuple[float, int, str, str]] = []
    heapq.heappush(frontier, (f0, tie, start_eid, start))
    stats["max_frontier"] = 1
    stats["generated_nodes"] = 1

    node_info_dict[start] = {"g": 0.0, "h": h0, "f": f0, "expansion_order": None, "parent": None}

    event_records[start_eid] = {
        "event_id": start_eid,
        "state": start,
        "parent_event_id": None,
        "g": 0.0,
        "h": h0,
        "f": f0,
        "expansion_order": None,
        "decision": "accepted",
    }

    closed = set()
    exp_counter = 0

    while frontier:
        stats["max_frontier"] = max(int(stats["max_frontier"]), len(frontier))

        f_cur, _, cur_eid, current = heapq.heappop(frontier)

        if current in closed:
            continue

        g_cur = g_score.get(current, INF)

        # Expand
        closed.add(current)
        node_info_dict.setdefault(current, {})
        node_info_dict[current]["expansion_order"] = exp_counter
        event_records[cur_eid]["expansion_order"] = exp_counter
        exp_counter += 1

        if current == goal:
            path = reconstruct_path(came_from, goal)
            stats["expanded_nodes"] = len(closed)

            df_nodes = pd.DataFrame([{"node": n, **node_info_dict[n]} for n in node_info_dict])
            df_events = pd.DataFrame(list(event_records.values()))

            return AStarResult(
                found=True,
                start=start,
                goal=goal,
                path=path,
                total_cost=g_cur,
                node_info=df_nodes,
                event_info=df_events,
                stats=stats,
            )

        for nxt, step_cost in adj.get(current, []):
            if step_cost < 0:
                raise ValueError("Negative edge cost is not allowed for A* / Dijkstra-style methods.")

            cand_g = g_cur + step_cost
            known_g = g_score.get(nxt, INF)

            h_nxt = float(heuristic_h(nxt))
            f_nxt = cand_g + h_nxt

            child_eid = new_event_id(nxt)
            event_records[child_eid] = {
                "event_id": child_eid,
                "state": nxt,
                "parent_event_id": cur_eid,
                "g": cand_g,
                "h": h_nxt,
                "f": f_nxt,
                "expansion_order": None,
                "decision": "discarded",
            }

            if cand_g < known_g:
                event_records[child_eid]["decision"] = "accepted"

                if nxt in g_score:
                    stats["reopen_updates"] = int(stats["reopen_updates"]) + 1

                g_score[nxt] = cand_g
                came_from[nxt] = current

                if nxt not in node_info_dict:
                    node_info_dict[nxt] = {
                        "g": cand_g, "h": h_nxt, "f": f_nxt,
                        "expansion_order": None, "parent": current
                    }
                else:
                    node_info_dict[nxt]["g"] = cand_g
                    node_info_dict[nxt]["h"] = h_nxt
                    node_info_dict[nxt]["f"] = f_nxt
                    node_info_dict[nxt]["parent"] = current

                tie += 1
                heapq.heappush(frontier, (f_nxt, tie, child_eid, nxt))
                stats["generated_nodes"] = int(stats["generated_nodes"]) + 1

    # no solution
    stats["expanded_nodes"] = len(closed)
    df_nodes = pd.DataFrame([{"node": n, **node_info_dict[n]} for n in node_info_dict]) if node_info_dict else pd.DataFrame()
    df_events = pd.DataFrame(list(event_records.values())) if event_records else pd.DataFrame()

    return AStarResult(
        found=False,
        start=start,
        goal=goal,
        path=None,
        total_cost=None,
        node_info=df_nodes,
        event_info=df_events,
        stats=stats,
    )


# =========================================================
# Dijkstra
# =========================================================
@dataclass
class DijkstraResult:
    found: bool
    start: str
    goal: str
    path: Optional[List[str]]
    total_cost: Optional[float]
    stats: Dict[str, float | int]


def dijkstra(start: str, goal: str, distance_df: pd.DataFrame) -> DijkstraResult:
    """Dijkstra (graph-search) con coste real."""
    adj = build_adjacency(distance_df)

    INF = float("inf")
    dist: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}

    pq: List[Tuple[float, int, str]] = []
    tie = 0
    heapq.heappush(pq, (0.0, tie, start))

    closed = set()

    stats: Dict[str, float | int] = {
        "expanded_nodes": 0,
        "generated_nodes": 1,
        "max_frontier": 1,
        "reopen_updates": 0,
    }

    while pq:
        stats["max_frontier"] = max(int(stats["max_frontier"]), len(pq))
        g_cur, _, u = heapq.heappop(pq)

        if u in closed:
            continue
        closed.add(u)

        if u == goal:
            stats["expanded_nodes"] = len(closed)
            return DijkstraResult(
                found=True,
                start=start,
                goal=goal,
                path=reconstruct_path(came_from, goal),
                total_cost=g_cur,
                stats=stats,
            )

        for v, w in adj.get(u, []):
            if w < 0:
                raise ValueError("Negative edge cost is not allowed for Dijkstra.")
            cand = g_cur + w
            known = dist.get(v, INF)
            if cand < known:
                if v in dist:
                    stats["reopen_updates"] = int(stats["reopen_updates"]) + 1
                dist[v] = cand
                came_from[v] = u
                tie += 1
                heapq.heappush(pq, (cand, tie, v))
                stats["generated_nodes"] = int(stats["generated_nodes"]) + 1

    stats["expanded_nodes"] = len(closed)
    return DijkstraResult(
        found=False,
        start=start,
        goal=goal,
        path=None,
        total_cost=None,
        stats=stats,
    )


# =========================================================
# UCS
# =========================================================
@dataclass
class UCSResult:
    found: bool
    start: str
    goal: str
    path: Optional[List[str]]
    total_cost: Optional[float]
    stats: Dict[str, float | int]


def ucs(start: str, goal: str, distance_df: pd.DataFrame) -> UCSResult:
    """
    Uniform Cost Search (graph-search) con coste real.
    En costes no negativos, UCS es equivalente a Dijkstra (pero lo mantenemos separado por claridad académica).
    """
    adj = build_adjacency(distance_df)

    INF = float("inf")
    best_g: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}

    pq: List[Tuple[float, int, str]] = []
    tie = 0
    heapq.heappush(pq, (0.0, tie, start))

    closed = set()

    stats: Dict[str, float | int] = {
        "expanded_nodes": 0,
        "generated_nodes": 1,
        "max_frontier": 1,
        "reopen_updates": 0,
    }

    while pq:
        stats["max_frontier"] = max(int(stats["max_frontier"]), len(pq))
        g_cur, _, u = heapq.heappop(pq)

        if u in closed:
            continue
        closed.add(u)

        if u == goal:
            stats["expanded_nodes"] = len(closed)
            return UCSResult(
                found=True,
                start=start,
                goal=goal,
                path=reconstruct_path(came_from, goal),
                total_cost=g_cur,
                stats=stats,
            )

        for v, w in adj.get(u, []):
            if w < 0:
                raise ValueError("Negative edge cost is not allowed for UCS.")
            cand = g_cur + w
            known = best_g.get(v, INF)
            if cand < known:
                if v in best_g:
                    stats["reopen_updates"] = int(stats["reopen_updates"]) + 1
                best_g[v] = cand
                came_from[v] = u
                tie += 1
                heapq.heappush(pq, (cand, tie, v))
                stats["generated_nodes"] = int(stats["generated_nodes"]) + 1

    stats["expanded_nodes"] = len(closed)
    return UCSResult(
        found=False,
        start=start,
        goal=goal,
        path=None,
        total_cost=None,
        stats=stats,
    )
@dataclass
class AStarFastResult:
    found: bool
    start: str
    goal: str
    path: Optional[List[str]]
    total_cost: Optional[float]
    stats: Dict[str, float | int]


def a_star_fast(
    start: str,
    goal: str,
    distance_df: pd.DataFrame,
    heuristic_h: Callable[[str], float],
) -> AStarFastResult:
    """
    A* (graph-search) en modo FAST:
    - NO guarda event_info ni node_info
    - Ideal para benchmark de algoritmos (sin overhead de trazas)
    """
    adj = build_adjacency(distance_df)

    stats: Dict[str, float | int] = {
        "expanded_nodes": 0,
        "generated_nodes": 0,
        "max_frontier": 0,
        "reopen_updates": 0,
    }

    INF = float("inf")
    g_score: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}

    # frontier: (f, tie, node)
    tie = 0
    frontier: List[Tuple[float, int, str]] = []
    h0 = float(heuristic_h(start))
    heapq.heappush(frontier, (h0, tie, start))

    stats["generated_nodes"] = 1
    stats["max_frontier"] = 1

    closed = set()

    while frontier:
        stats["max_frontier"] = max(int(stats["max_frontier"]), len(frontier))

        f_cur, _, current = heapq.heappop(frontier)
        if current in closed:
            continue

        g_cur = g_score.get(current, INF)
        closed.add(current)

        if current == goal:
            stats["expanded_nodes"] = len(closed)
            return AStarFastResult(
                found=True,
                start=start,
                goal=goal,
                path=reconstruct_path(came_from, goal),
                total_cost=g_cur,
                stats=stats,
            )

        for nxt, step_cost in adj.get(current, []):
            if step_cost < 0:
                raise ValueError("Negative edge cost is not allowed for A*.")

            cand_g = g_cur + step_cost
            known_g = g_score.get(nxt, INF)

            if cand_g < known_g:
                if nxt in g_score:
                    stats["reopen_updates"] = int(stats["reopen_updates"]) + 1

                g_score[nxt] = cand_g
                came_from[nxt] = current

                tie += 1
                f_nxt = cand_g + float(heuristic_h(nxt))
                heapq.heappush(frontier, (f_nxt, tie, nxt))
                stats["generated_nodes"] = int(stats["generated_nodes"]) + 1

    stats["expanded_nodes"] = len(closed)
    return AStarFastResult(
        found=False,
        start=start,
        goal=goal,
        path=None,
        total_cost=None,
        stats=stats,
    )