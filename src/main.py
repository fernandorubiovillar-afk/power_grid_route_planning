from __future__ import annotations

import os
import pandas as pd

from .heuristics import build_coords_map, make_heuristic
from .benchmark import (
    benchmark_heuristics,
    benchmark_algorithms,
    run_single,
    pick_best_label_overall,
)
from .plots import generate_images
from .tree_viz import draw_search_tree


def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_PATH = os.path.join(BASE_DIR, "data", "nodes_distance.csv")

    RESULTS_DIR = os.path.join(BASE_DIR, "results")

    # --- Subcarpetas ---
    HEUR_DIR = os.path.join(RESULTS_DIR, "heuristics")
    HEUR_SEARCH_DIR = os.path.join(HEUR_DIR, "search_trees")
    HEUR_BENCH_DIR = os.path.join(HEUR_DIR, "benchmarks")
    HEUR_IMG_DIR = os.path.join(HEUR_DIR, "images")

    ALG_DIR = os.path.join(RESULTS_DIR, "algorithms")
    ALG_BENCH_DIR = os.path.join(ALG_DIR, "benchmarks")
    ALG_IMG_DIR = os.path.join(ALG_DIR, "images")

    for d in [HEUR_SEARCH_DIR, HEUR_BENCH_DIR, HEUR_IMG_DIR, ALG_BENCH_DIR, ALG_IMG_DIR]:
        os.makedirs(d, exist_ok=True)

    # --- Nodos y coordenadas ---
    nodes = ["A", "B", "C", "D", "E", "F", "G", "H"]
    coord = [
        [200, 700],
        [400, 800],
        [700, 800],
        [800, 500],  # D
        [600, 300],
        [300, 400],
        [200, 100],
        [800, 100],
    ]
    coords_map = build_coords_map([nodes, coord])

    # --- Dataset ---
    dist = pd.read_csv(CSV_PATH, delimiter=";")
    dist["real"] = dist["dist_km"] * dist["FCC"]

    # --- Casos ---
    cases = [("A", "H"), ("D", "A"), ("C", "G"), ("E", "A")]

    # --- Heurísticas A* (SIN dijkstra) ---
    heuristic_names = [
        "euclidean",
        "manhattan_scaled",
        "chebyshev_scaled",
    ]

    repeats = 50

    # =========================================================
    # 1) BENCHMARK HEURÍSTICAS (A*)
    # =========================================================
    all_case_dfs = []

    for start, goal in cases:
        bundles = [make_heuristic(hn, dist, coords_map, goal=goal, fcc_min=2.0) for hn in heuristic_names]

        df_case = benchmark_heuristics(
            cases=[(start, goal)],
            heuristics=bundles,
            distance_df=dist,
            repeats=repeats,
        )
        all_case_dfs.append(df_case)

        out_case_xlsx = os.path.join(HEUR_BENCH_DIR, f"benchmark_{start}_to_{goal}.xlsx")
        out_case_csv = os.path.join(HEUR_BENCH_DIR, f"benchmark_{start}_to_{goal}.csv")
        df_case.to_excel(out_case_xlsx, index=False)
        df_case.to_csv(out_case_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")

        # --- Search trees por heurística ---
        case_dir = os.path.join(HEUR_SEARCH_DIR, f"{start}_to_{goal}")
        os.makedirs(case_dir, exist_ok=True)

        for hb in bundles:
            res = run_single(start, goal, dist, hb)
            df_events = res.event_info.copy()

            out_csv = os.path.join(case_dir, f"{hb.name}_events.csv")
            df_events.to_csv(out_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")

            out_png = os.path.join(case_dir, f"{hb.name}.png")
            draw_search_tree(node_info=df_events, start=start, goal=goal, out_png=out_png, path=None)

            if res.path:
                df_nodes = res.node_info.copy()
                df_nodes["status"] = df_nodes["expansion_order"].apply(
                    lambda x: "expanded" if pd.notna(x) else "evaluated_not_expanded"
                )
                df_nodes["in_path"] = df_nodes["node"].isin(res.path)

                df_path = (
                    df_nodes.set_index("node")
                    .loc[res.path, ["g", "h", "f", "expansion_order", "parent", "status", "in_path"]]
                    .reset_index()
                )
                out_path_csv = os.path.join(case_dir, f"{hb.name}_PATH.csv")
                df_path.to_csv(out_path_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")

    df_heur_all = pd.concat(all_case_dfs, ignore_index=True)

    out_all_xlsx = os.path.join(HEUR_BENCH_DIR, "benchmark_all_cases.xlsx")
    out_all_csv = os.path.join(HEUR_BENCH_DIR, "benchmark_all_cases.csv")
    df_heur_all.to_excel(out_all_xlsx, index=False)
    df_heur_all.to_csv(out_all_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")

    generate_images(df_heur_all, HEUR_IMG_DIR, label_col="label", title_prefix="Heurísticas (A*)")

    # Elegir heurística ganadora global
    winner_label = pick_best_label_overall(df_heur_all)

    # reconstruir el bundle ganador por caso (depende de goal)
    # (lo hacemos en el benchmark_algorithms por cada caso)
    # =========================================================
    # 2) BENCHMARK ALGORITMOS (A* vs Dijkstra vs UCS)
    # =========================================================
    alg_case_dfs = []
    for start, goal in cases:
        # bundle ganador para ESTE goal (mismo nombre label => necesitamos mapearlo)
        # winner_label coincide con hb.name (ej: "manhattan_scaled")
        # pero euclidean devuelve "euclidean_x_fccmin"
        # por eso mapeamos:
        if winner_label == "euclidean_x_fccmin":
            wn = "euclidean"
        elif winner_label == "manhattan_scaled":
            wn = "manhattan_scaled"
        elif winner_label == "chebyshev_scaled":
            wn = "chebyshev_scaled"
        else:
            # fallback razonable
            wn = "manhattan_scaled"

        winner_bundle = make_heuristic(wn, dist, coords_map, goal=goal, fcc_min=2.0)

        df_alg_case = benchmark_algorithms(
            cases=[(start, goal)],
            distance_df=dist,
            astar_heuristic=winner_bundle,
            repeats=repeats,
        )
        alg_case_dfs.append(df_alg_case)

        out_case_xlsx = os.path.join(ALG_BENCH_DIR, f"benchmark_{start}_to_{goal}.xlsx")
        out_case_csv = os.path.join(ALG_BENCH_DIR, f"benchmark_{start}_to_{goal}.csv")
        df_alg_case.to_excel(out_case_xlsx, index=False)
        df_alg_case.to_csv(out_case_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")

    df_alg_all = pd.concat(alg_case_dfs, ignore_index=True)

    out_all_xlsx = os.path.join(ALG_BENCH_DIR, "benchmark_all_cases.xlsx")
    out_all_csv = os.path.join(ALG_BENCH_DIR, "benchmark_all_cases.csv")
    df_alg_all.to_excel(out_all_xlsx, index=False)
    df_alg_all.to_csv(out_all_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")

    generate_images(df_alg_all, ALG_IMG_DIR, label_col="label", title_prefix="Algoritmos")

    print("✅ Resultados guardados en:")
    print(" - Heuristics:")
    print("   - Search trees:", HEUR_SEARCH_DIR)
    print("   - Benchmarks:", HEUR_BENCH_DIR)
    print("   - Images:", HEUR_IMG_DIR)
    print(" - Algorithms:")
    print("   - Benchmarks:", ALG_BENCH_DIR)
    print("   - Images:", ALG_IMG_DIR)
    print(f"🏆 Heurística ganadora global: {winner_label}")


if __name__ == "__main__":
    main()

