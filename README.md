# power_grid_route_planning
Este repositorio contiene un framework modular en Python para la resolución y comparación de problemas de camino más corto en grafos dirigidos ponderados, utilizando:

A* con distintas heurísticas

Uniform Cost Search (UCS)

Dijkstra

El objetivo principal es comparar de forma justa:

Diferentes heurísticas para A*

Diferentes algoritmos de búsqueda

separando claramente la lógica de búsqueda del overhead de visualización y trazado, y permitiendo análisis cuantitativos reproducibles.

🚀 Características principales

Implementación desde cero de:

A* (modo completo y modo rápido)

Dijkstra

Uniform Cost Search (UCS)

Comparación objetiva basada en métricas:

Nodos expandidos

Tiempo medio de ejecución

Tamaño máximo de la frontera

Eficiencia temporal por nodo expandido

Generación automática de:

Benchmarks en CSV/XLSX

Gráficas comparativas

Árboles de búsqueda de A* (visualización)

Arquitectura pensada para:

Separar algoritmos, heurísticas, benchmarking y visualización

Evitar sesgos por instrumentación (logging / trazas)

🧠 Diseño clave: A* FULL vs A* FAST

Para garantizar comparaciones justas, se utilizan dos variantes de A*:

🔍 A* FULL

Registra información detallada de:

Expansiones

Estados evaluados

Eventos de decisión

Se utiliza exclusivamente para:

Dibujar árboles de búsqueda

Analizar el proceso de expansión

⚡ A* FAST

No guarda trazas ni eventos

Se utiliza para:

Comparación entre heurísticas

Comparación entre algoritmos

Elimina el overhead de instrumentación y permite medir:

Tiempo real

Eficiencia algorítmica

📂 Estructura del proyecto
.
├── data/
│   └── nodes_distance.csv        # Grafo: arcos, distancias y costes reales
│
├── src/
│   ├── algorithms.py             # A*, A*_fast, Dijkstra, UCS
│   ├── heuristics.py             # Heurísticas admisibles
│   ├── benchmark.py              # Lógica de benchmarking
│   ├── plots.py                  # Generación de gráficas
│   ├── tree_viz.py               # Visualización de árboles de búsqueda
│   └── main.py                   # Script principal
│
├── results/
│   ├── heuristics/
│   │   ├── benchmarks/           # CSV/XLSX por heurística
│   │   ├── images/               # Gráficas comparativas
│   │   └── search_trees/         # Árboles de A*
│   │
│   └── algorithms/
│       ├── benchmarks/           # Comparativa A* vs Dijkstra vs UCS
│       └── images/               # Gráficas comparativas
│
└── README.md

📐 Heurísticas implementadas

Todas las heurísticas utilizadas son admisibles.

- Euclídea escalada
- Manhattan escalada
- Chebyshev escalada

Escalada análoga a la Manhattan

La constante de escalado garantiza:

Admisibilidad

Comparaciones consistentes entre heurísticas

📊 Métricas de comparación

Para cada caso de prueba se recogen:

expanded_nodes

generated_nodes

max_frontier

exec_time_ms_mean

exec_time_ms_min

ms_per_expanded

total_cost

path_length

La heurística ganadora global se selecciona mediante un sistema de ranking por caso y métrica.

▶️ Ejecución

Desde la carpeta raíz del proyecto:

python -m src.main


Esto genera automáticamente:

Benchmarks por heurística

Árboles de búsqueda (A*)

Gráficas comparativas

Comparación final entre algoritmos

🧪 Casos de prueba

Los casos se definen directamente en main.py:

cases = [
    ("A", "H"),
    ("D", "A"),
    ("C", "G"),
    ("E", "A"),
]

El framework es fácilmente extensible a nuevos grafos y conjuntos de casos.
👨‍💻 Autor

Fernando Rubio Villar
