# power_grid_route_planning
Este repositorio contiene un framework modular en Python para la resolución y comparación de problemas de camino más corto en grafos dirigidos ponderados, utilizando:

- A* con distintas heurísticas
- Uniform Cost Search (UCS)
- Dijkstra

El objetivo principal es comparar de forma justa:
1. Diferentes heurísticas para A*
2. Diferentes algoritmos de búsqueda

separando claramente la lógica de búsqueda del overhead de visualización y trazado, y permitiendo análisis cuantitativos reproducibles.

---

## Características principales

- Implementación desde cero de:
  - A* (modo completo y modo rápido)
  - Dijkstra
  - Uniform Cost Search (UCS)
- Comparación objetiva basada en métricas:
  - Nodos expandidos
  - Tiempo medio de ejecución
  - Tamaño máximo de la frontera
  - Eficiencia temporal por nodo expandido
- Generación automática de:
  - Benchmarks en CSV y XLSX
  - Gráficas comparativas
  - Árboles de búsqueda de A* (visualización)
- Arquitectura modular:
  - Algoritmos
  - Heurísticas
  - Benchmarking
  - Visualización

---

## Diseño clave: A* FULL vs A* FAST

Para garantizar comparaciones justas, se utilizan dos variantes de A*.

### A* FULL
- Registra información detallada de:
  - Expansiones
  - Estados evaluados
  - Eventos de decisión
- Se utiliza exclusivamente para:
  - Dibujar árboles de búsqueda
  - Analizar el proceso de expansión

### A* FAST
- No guarda trazas ni eventos
- Se utiliza para:
  - Comparación entre heurísticas
  - Comparación entre algoritmos
- Elimina el overhead de instrumentación y permite medir la eficiencia real del algoritmo

---

## Estructura del proyecto
├── data <br> 
│ └── nodes_distance.csv<br> 
│<br> 
├── src/<br> 
│ ├── algorithms.py<br> 
│ ├── heuristics.py<br> 
│ ├── benchmark.py<br> 
│ ├── plots.py<br> 
│ ├── tree_viz.py<br> 
│ └── main.py<br> 
│<br> 
├── results/<br> 
│ ├── heuristics/<br> 
│ │ ├── benchmarks/<br> 
│ │ ├── images/<br> 
│ │ └── search_trees/<br> 
│ │<br> 
│ └── algorithms/<br> 
│ ├── benchmarks/<br> 
│ └── images/<br> 
│<br> 
└── README.md<br> 
## Heurísticas implementadas

Todas las heurísticas utilizadas son admisibles.

- Euclídea escalada  
  Distancia euclídea multiplicada por el FCC mínimo

- Manhattan escalada  
  Escalada mediante la constante:

  k = min_{(u,v) in E} c(u,v) / d_Manhattan(u,v)

- Chebyshev escalada  
  Escalada análoga a la Manhattan

El escalado garantiza:
- Admisibilidad
- Comparaciones consistentes entre heurísticas

---

## Métricas de comparación

Para cada caso de prueba se recogen:

- expanded_nodes
- generated_nodes
- max_frontier
- exec_time_ms_mean
- exec_time_ms_min
- ms_per_expanded
- total_cost
- path_length

La heurística ganadora global se selecciona mediante un sistema de ranking por caso y métrica.

---

## Ejecución

Desde la carpeta raíz del proyecto:

```bash
python -m src.main

Esto genera automáticamente:

- Benchmarks por heurística

- Árboles de búsqueda (A*)

- Gráficas comparativas

## Casos de prueba
Los casos se definen directamente en `main.py`
cases = [
    ("A", "H"),
    ("D", "A"),
    ("C", "G"),
    ("E", "A"),
]

El framework es fácilmente extensible a nuevos grafos y conjuntos de casos.
👨‍💻 Autor

Fernando Rubio Villar
