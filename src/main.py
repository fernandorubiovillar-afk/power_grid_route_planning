import pandas as pd
import os

from substation_astar_2 import Substation, A_star   # ojo al nombre del fichero

# Ruta base del proyecto (carpeta 01_Opt_Substations)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas a data y results
CSV_PATH = os.path.join(BASE_DIR, "data", "nodes_distance.csv")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Creamos la carpeta results si no existe
os.makedirs(RESULTS_DIR, exist_ok=True)

# Definición de nodos y coordenadas
nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
coord = [
    [200, 700],
    [400, 800],
    [700, 800],
    [800, 500],
    [600, 300],
    [300, 400],
    [200, 100],
    [800, 100],
]
list_nodes = [nodes, coord]

# Cargamos distancias reales
dist_real = pd.read_csv(CSV_PATH, delimiter=";")
dist_real["real"] = dist_real["dist_km"] * dist_real["FCC"]

start_node = "E"
goal_node = "A"

# =========================
# 1) A* con heurística Euclidiana × FCC_min
# =========================
sol_euc, frontier_euc, explored_euc, node_info_euc = A_star(
    start_node,
    list_nodes,
    dist_real,
    goal_node,
    heuristic="euclidean_fcc",
)

# Pasamos node_info_euc a DataFrame
df_euc = pd.DataFrame.from_dict(node_info_euc, orient="index").reset_index()
df_euc = df_euc.rename(columns={"index": "node"})

# (Opcional) ordenamos por orden de expansión
df_euc = df_euc.sort_values(
    by=["expansion_order", "node"],
    na_position="last"
)

# Guardamos CSV
euclidean_csv_path = os.path.join(RESULTS_DIR, "astar_euclidean_fcc_E-A.csv")
df_euc.to_csv(euclidean_csv_path, sep=";", decimal=",", index=False, encoding="utf-8-sig")
print(f"Guardado CSV de heurística Euclidean×FCC_min en: {euclidean_csv_path}")

# =========================
# 2) A* con heurística Dijkstra(km) × FCC_min
# =========================
sol_dij, frontier_dij, explored_dij, node_info_dij = A_star(
    start_node,
    list_nodes,
    dist_real,
    goal_node,
    heuristic="dijkstra_fcc",
)

# Pasamos node_info_dij a DataFrame
df_dij = pd.DataFrame.from_dict(node_info_dij, orient="index").reset_index()
df_dij = df_dij.rename(columns={"index": "node"})

df_dij = df_dij.sort_values(
    by=["expansion_order", "node"],
    na_position="last"
)

# Guardamos CSV
dijkstra_csv_path = os.path.join(RESULTS_DIR, "astar_dijkstra_fcc_E-A.csv")
df_dij.to_csv(dijkstra_csv_path, sep=";", decimal=",", index=False, encoding="utf-8-sig")
print(f"Guardado CSV de heurística Dijkstra×FCC_min en: {dijkstra_csv_path}")
