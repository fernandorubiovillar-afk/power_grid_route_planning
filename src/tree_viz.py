from __future__ import annotations

import os
from typing import Optional, List, Dict, Tuple

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def _hierarchy_pos(G: nx.DiGraph, root: str, dx=1.0, dy=1.0) -> Dict[str, Tuple[float, float]]:
    """
    Posiciona nodos como árbol jerárquico real:
    - Cada subárbol ocupa su propio intervalo horizontal
    - Los hijos se dibujan debajo del padre
    """
    pos: Dict[str, Tuple[float, float]] = {}
    widths: Dict[str, float] = {}

    def _subtree_width(n: str) -> float:
        children = list(G.successors(n))
        if not children:
            widths[n] = 1.0
            return 1.0
        w = sum(_subtree_width(c) for c in children)
        widths[n] = w
        return w

    def _assign_pos(n: str, x: float, y: float) -> None:
        pos[n] = (x * dx, y * dy)
        children = list(G.successors(n))
        if not children:
            return

        cur_x = x - widths[n] / 2.0
        for c in children:
            cw = widths[c]
            cx = cur_x + cw / 2.0
            _assign_pos(c, cx, y - 1)
            cur_x += cw

    _subtree_width(root)
    _assign_pos(root, 0.0, 0.0)
    return pos


def _fmt_es(x: float, nd: int = 2) -> str:
    """Formato decimal español (coma)."""
    return f"{x:.{nd}f}".replace(".", ",")


def draw_search_tree(
    node_info: pd.DataFrame,
    start: str,
    goal: str,
    out_png: str,
    path: Optional[List[str]] = None,
) -> None:
    """
    Dibuja el árbol de eventos (event_id) parent_event_id -> event_id.

    - Dentro del nodo: letra (state)
    - A la izquierda: f = g + h (con valores)
    - A la derecha-arriba: orden de expansión (si existe)
    """
    df = node_info.copy()

    required = {"event_id", "state", "parent_event_id", "g", "h", "f", "expansion_order"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"node_info debe contener columnas {sorted(required)}. Faltan: {sorted(missing)}")

    # Grafo parent_event_id -> event_id
    G = nx.DiGraph()
    for _, r in df.iterrows():
        eid = str(r["event_id"])
        G.add_node(eid)

    for _, r in df.iterrows():
        eid = str(r["event_id"])
        peid = r["parent_event_id"]
        if pd.notna(peid) and peid is not None:
            G.add_edge(str(peid), eid)

    # Root: el primer evento del start sin padre (si existe)
    root_candidates = df[(df["state"] == start) & (df["parent_event_id"].isna())]
    if root_candidates.empty:
        root_candidates = df[df["state"] == start]
    start_event_id = str(root_candidates.iloc[0]["event_id"])

    # Layout
    try:
        import pydot  # noqa: F401
        pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
    except Exception:
        pos = _hierarchy_pos(G, root=start_event_id, dx=3.0, dy=2.5)

        
    fig = plt.figure(figsize=(18, 10))
    ax = plt.gca()
    ax.set_title(f"Árbol de expansión A*: {start} → {goal}")
    ax.axis("off")

    nx.draw_networkx_edges(G, pos, arrows=True, ax=ax)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=900)

    # Textos
    bbox = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85)

    for _, r in df.iterrows():
        eid = str(r["event_id"])
        label = str(r["state"])
        x, y = pos.get(eid, (0.0, 0.0))

        g = float(r["g"])
        h = float(r["h"])
        f = float(r["f"])
        eo = r["expansion_order"]

        # letra dentro del nodo
        ax.text(x, y, label, ha="center", va="center", fontsize=12, fontweight="bold", bbox=None)

        # etiqueta a la izquierda (2 líneas)
        txt = f"f=g+h\n{_fmt_es(f)}={_fmt_es(g)}+{_fmt_es(h)}"
        ax.annotate(
            txt,
            xy=(x, y),
            xycoords="data",
            textcoords="offset points",
            xytext=(-30, 0),      # <-- ajusta: -40 más cerca / -70 más lejos
            ha="right",
            va="center",
            fontsize=8,
            bbox=bbox,
        )

        # expansion order arriba derecha
        if pd.notna(eo):
            ax.annotate(
            str(int(eo)),
            xy=(x, y),
            xycoords="data",
            textcoords="offset points",
            xytext=(10, 10),   # <-- ajusta: (8,8) más cerca
            ha="left",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            bbox=bbox,
        )


    fig.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
