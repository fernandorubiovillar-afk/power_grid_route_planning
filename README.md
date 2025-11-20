# power_grid_route_planning
This scripts is a solution to find an efficient route planning in infrastructure networks is critical for reducing operation and maintenance costs and time.
🔌 Optimización de Rutas entre Subestaciones mediante A*

Este proyecto implementa el algoritmo A* para encontrar el camino óptimo entre nodos que representan subestaciones eléctricas conectadas por distancias reales. El objetivo es calcular la ruta de menor coste entre un nodo de inicio y un nodo destino, utilizando información geométrica (heurística admisible) y datos reales de distancia.

📌 Objetivos del proyecto

Implementar una clase Substation que gestione:

Coordenadas de cada nodo

Cálculo de distancia geométrica (heurística)

Evaluación de si un nodo es solución

Implementar una función A_star() capaz de:

Expandir nodos sucesores

Mantener frontera y nodos explorados

Evaluar coste real + heurístico

Reconstruir el camino óptimo

Probar el algoritmo con un conjunto de nodos y distancias reales incluidos en el dataset.

🗂️ Estructura del proyecto

01_Opt_Substations/
├── src/
│ ├── main.py
│ └── substation_astar.py
├── data/
│ └── nodes_distance.csv
├── notebooks/
│ └── main.ipynb
├── docs/
│ └── example_network.png (opcional)
├── requirements.txt
└── README.md

Descripción:

src/ → Código fuente del proyecto

data/ → Datos de entrada (distancias reales entre nodos)

notebooks/ → Notebooks para exploración y pruebas

docs/ → Imágenes o documentación adicional

🚀 Ejecución del algoritmo

El script principal está en:

src/main.py

Ejecutarlo desde la raíz del proyecto con:

python src/main.py

El programa imprimirá:

El camino óptimo

El coste total

La frontera

Los nodos explorados

🧠 Breve explicación del algoritmo A*

A* combina dos valores:

g(n): coste real acumulado desde el inicio

h(n): distancia geométrica al objetivo (heurística)

La función de evaluación es:

f(n) = g(n) + h(n)

Esto permite seleccionar en cada paso el nodo más prometedor, logrando una solución eficiente y óptima.

📊 Dataset utilizado

El archivo:

data/nodes_distance.csv

Incluye:

Nodo de inicio

Nodo de destino

Distancia en km

Factor FCC (coste asociado)

real = dist_km × FCC

Este dataset actúa como grafo dirigido para que A* explore todas las rutas posibles.

📦 Instalación

Crear entorno virtual (opcional):
python -m venv .venv

Activarlo:
En Windows:
..venv\Scripts\activate

Instalar dependencias:
pip install -r requirements.txt
