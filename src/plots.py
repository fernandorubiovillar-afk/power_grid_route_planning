from __future__ import annotations

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _grouped_bar(df: pd.DataFrame, value_col: str, title: str, outpath: str, label_col: str = "label"):
    pivot = df.pivot(index="case", columns=label_col, values=value_col)
    cases = pivot.index.tolist()
    labels = pivot.columns.tolist()

    x = np.arange(len(cases))
    n = len(labels)
    width = 0.8 / max(n, 1)

    fig, ax = plt.subplots()
    for i, lb in enumerate(labels):
        y = pivot[lb].values.astype(float)
        ax.bar(x + (i - (n - 1) / 2) * width, y, width, label=lb)

    ax.set_xticks(x)
    ax.set_xticklabels(cases, rotation=0)
    ax.set_title(title)
    ax.set_ylabel(value_col)
    ax.legend()

    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def _heatmap_winners(df: pd.DataFrame, outpath: str, label_col: str = "label"):
    metrics = ["expanded_nodes", "exec_time_ms_mean", "ms_per_expanded", "max_frontier"]

    cases = sorted(df["case"].unique().tolist())
    labels = sorted(df[label_col].unique().tolist())

    wins = pd.DataFrame(0, index=cases, columns=labels, dtype=int)

    for c in cases:
        df_c = df[df["case"] == c].copy()
        df_c = df_c[df_c["found"] == True]
        if df_c.empty:
            continue

        for m in metrics:
            df_m = df_c.dropna(subset=[m])
            if df_m.empty:
                continue
            best_val = df_m[m].min()
            winners = df_m[df_m[m] == best_val][label_col].tolist()
            for w in winners:
                wins.loc[c, w] += 1

    data = wins.values.astype(float)

    fig, ax = plt.subplots()
    im = ax.imshow(data, aspect="auto")

    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(cases)))
    ax.set_yticklabels(cases)

    ax.set_title("Heatmap de ganadores (nº métricas ganadas por caso)")

    for i in range(len(cases)):
        for j in range(len(labels)):
            ax.text(j, i, int(data[i, j]), ha="center", va="center")

    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def generate_images(df_all: pd.DataFrame, images_dir: str, label_col: str = "label", title_prefix: str = ""):
    os.makedirs(images_dir, exist_ok=True)
    p = (title_prefix + " - ") if title_prefix else ""

    _grouped_bar(
        df_all,
        value_col="expanded_nodes",
        title=f"{p}Nodos expandidos por caso",
        outpath=os.path.join(images_dir, "01_expanded_nodes.png"),
        label_col=label_col,
    )

    _grouped_bar(
        df_all,
        value_col="exec_time_ms_mean",
        title=f"{p}Tiempo medio de ejecución (ms) por caso",
        outpath=os.path.join(images_dir, "02_exec_time_ms_mean.png"),
        label_col=label_col,
    )

    _grouped_bar(
        df_all,
        value_col="ms_per_expanded",
        title=f"{p}Eficiencia: ms por nodo expandido",
        outpath=os.path.join(images_dir, "03_ms_per_expanded.png"),
        label_col=label_col,
    )

    _grouped_bar(
        df_all,
        value_col="max_frontier",
        title=f"{p}Tamaño máximo de frontera (max_frontier)",
        outpath=os.path.join(images_dir, "04_max_frontier.png"),
        label_col=label_col,
    )

    _heatmap_winners(
        df_all,
        outpath=os.path.join(images_dir, "05_heatmap_winners.png"),
        label_col=label_col,
    )
