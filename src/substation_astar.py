import pandas as pd
import numpy as np
import heapq


class Substation:
    def __init__(self, node_name, list_nodes):
        self.node = node_name
        self.list_nodes = list_nodes
        self.x, self.y = self.coordenates()

    def coordenates(self):
        i = self.list_nodes[0].index(self.node)
        coord = self.list_nodes[1][i]
        return coord

    def geometric_distance(self, solution_node):
        i = self.list_nodes[0].index(solution_node)
        coord = self.list_nodes[1][i]
        node_geometric_distance = np.sqrt(
            (coord[0] - self.x) ** 2 + (coord[1] - self.y) ** 2
        )
        return node_geometric_distance

    def is_solution(self, solution_node):
        return self.node == solution_node


def dijkstra_km_to_goal(distance_df, nodes, goal_node):
    """
    Calcula la distancia mínima en km desde cada nodo hasta goal_node,
    usando Dijkstra en el grafo invertido (para respetar la dirección original).
    Pesos = dist_km.
    """
    # Construimos lista de adyacencia del grafo invertido: end_node -> start_node
    adj_rev = {n: [] for n in nodes}
    for _, row in distance_df.iterrows():
        u = row["start_node"]
        v = row["end_node"]
        w = float(row["dist_km"])
        # invertimos el arco: v -> u
        adj_rev[v].append((u, w))

    INF = float("inf")
    dist = {n: INF for n in nodes}
    dist[goal_node] = 0.0

    pq = [(0.0, goal_node)]  # (distancia, nodo)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj_rev[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    return dist


def A_star(start_node_name, list_nodes, distance, goal_node, heuristic="euclidean_fcc"):
    """
    Algoritmo A* con dos heurísticas posibles:
    - 'euclidean_fcc' : distancia euclídea * FCC_min
    - 'dijkstra_fcc'  : (distancia mínima en km hasta goal) * FCC_min

    Devuelve:
    - sol: lista con la solución (ruta, coste)
    - frontier: contenido final de la frontera
    - explored: nodos explorados
    - node_info: dict con g, h, f y orden de expansión de cada nodo
    """
    sol = []
    explored = []

    nodes = list_nodes[0]

    # FCC mínimo (en tu caso es 2, pero así queda general)
    fcc_min = distance["FCC"].min()

    # Diccionario para reconstruir el camino
    came_from = {start_node_name: None}

    # Preprocesado de heurística si es tipo Dijkstra
    dijkstra_km_dist = None
    if heuristic == "dijkstra_fcc":
        if "dist_km" not in distance.columns:
            raise ValueError("La heurística dijkstra_fcc requiere columna 'dist_km' en el DataFrame.")
        dijkstra_km_dist = dijkstra_km_to_goal(distance, nodes, goal_node)

    # Función heurística h(n) según el tipo elegido
    def h(node_name):
        if heuristic == "euclidean_fcc":
            sub = Substation(node_name, list_nodes=list_nodes)
            return fcc_min * sub.geometric_distance(goal_node)
        elif heuristic == "dijkstra_fcc":
            # Si un nodo es inalcanzable hacia el objetivo, su heurística es infinita
            return fcc_min * dijkstra_km_dist[node_name]
        else:
            raise ValueError(f"Heurística '{heuristic}' no reconocida.")

    # Información de nodos: g, h, f y orden de expansión
    node_info = {}

    # Nodo inicial y heurística inicial
    h0 = h(start_node_name)
    g0 = 0.0
    f0 = g0 + h0

    # order 0 para el nodo inicial cuando se expanda
    expansion_order = 0

    # Inicializamos info del nodo inicial (sin haberse expandido aún)
    node_info[start_node_name] = {
        "g": g0,
        "h": h0,
        "f": f0,
        "expansion_order": None,  # se pondrá 0 cuando se expanda
    }

    frontier = [
        {
            "node_name": start_node_name,
            "g": g0,
            "cost": f0,
            "parent": None,
        }
    ]

    while len(frontier) > 0:
        frontier.sort(key=lambda x: x["cost"])
        less_cost_node = frontier.pop(0)
        node = Substation(less_cost_node["node_name"], list_nodes=list_nodes)
        g_current = less_cost_node["g"]

        # h y f del nodo actual (puede haber cambiado si usamos heurística Dijkstra)
        h_current = h(node.node)
        f_current = g_current + h_current

        # Guardamos/actualizamos info del nodo actual
        node_info[node.node] = {
            "g": g_current,
            "h": h_current,
            "f": f_current,
            "expansion_order": expansion_order,
        }
        expansion_order += 1  # siguiente nodo expandido tendrá el siguiente número

        # Evaluamos si es solución
        if node.node == goal_node:
            # Reconstruimos el camino desde GOAL hacia atrás
            path = [node.node]
            parent = came_from[node.node]
            while parent is not None:
                path.append(parent)
                parent = came_from[parent]
            path.reverse()

            solution_node = {
                "node_name": node.node,
                "cost": g_current,
                "path": path,
            }
            sol.append(solution_node)
            print(f"Optimal path found: {' -> '.join(path)} with total cost: {g_current}")
            # Solución encontrada: detenemos A*
            return sol, frontier, explored, node_info

        # Si no es solución, lo metemos en explorados
        explored.append(less_cost_node)

        # Expandimos sucesores
        actions = distance[distance["start_node"] == node.node]

        for child in actions["end_node"]:
            child_node = Substation(child, list_nodes)

            # Coste del paso (de node.node a child)
            row = distance[
                (distance["start_node"] == node.node)
                & (distance["end_node"] == child)
            ]
            if row.empty:
                print(f"No cost defined for the arc: {node.node} -> {child}, we ignore it.\n")
                continue

            step_cost = float(row["real"].iloc[0])
            g_child = g_current + step_cost
            h_child = h(child)  # según heurística elegida
            f_child = g_child + h_child

            front = [x["node_name"] for x in frontier]
            exp = [x["node_name"] for x in explored]

            # Si el hijo NO está ni en frontera ni en explorados, lo añadimos
            if (child_node.node not in front) and (child_node.node not in exp):
                frontier.append(
                    {
                        "node_name": child,
                        "g": g_child,
                        "cost": f_child,
                        "parent": node.node,
                    }
                )
                came_from[child] = node.node

                # guardamos info del hijo (todavía no expandido)
                prev_order = node_info.get(child, {}).get("expansion_order", None)
                node_info[child] = {
                    "g": g_child,
                    "h": h_child,
                    "f": f_child,
                    "expansion_order": prev_order,
                }

            # Si el hijo ya está en frontera, miramos si hemos encontrado un camino más barato
            elif child_node.node in front:
                for entry in frontier:
                    if entry["node_name"] == child:
                        old_cost = entry["cost"]
                        old_g = entry["g"]
                        break

                if old_cost > f_child:
                    entry["cost"] = f_child
                    entry["g"] = g_child
                    entry["parent"] = node.node
                    came_from[child] = node.node

                    # Actualizamos info de nodo si mejora
                    info = node_info.get(child, {})
                    node_info[child] = {
                        "g": g_child,
                        "h": h_child,
                        "f": f_child,
                        "expansion_order": info.get("expansion_order", None),
                    }

    # Si salimos del while es que no hay camino al objetivo
    print("No path has been found")
    sol.sort(key=lambda x: x["cost"])
    return sol, frontier, explored, node_info