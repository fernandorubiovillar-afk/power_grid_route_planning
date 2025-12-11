# power_grid_route_planning
Este proyecto implementa el algoritmo **A\*** para calcular rutas óptimas entre
subestaciones eléctricas, teniendo en cuenta:

- Distancias reales en kilómetros  
- Factores de Conservación del Camino (FCC)  
- Funciones heurísticas específicas para el dominio  

El sistema permite comparar dos heurísticas diferentes y genera trazabilidad
completa de la búsqueda (valores de `g`, `h`, `f`, orden de expansión y ruta final).

---

## 🚀 Funcionalidades principales

### ✔ Implementación completa del algoritmo A*
Incluye:
- Gestión de frontera (open list)
- Gestión de explorados (closed list)
- Actualización de caminos más eficientes (path improvement)
- Reconstrucción de rutas óptimas mediante `came_from`

### ✔ Dos heurísticas especializadas
1. **Distancia euclídea × FCC_min**
2. **Distancia Dijkstra × 2 (en km)**

Ambas cumplen admisibilidad y consistencia bajo el modelo planteado.

### ✔ Exportación de resultados
El algoritmo genera automáticamente:
- Los valores de `g`, `h`, `f` para cada nodo
- El orden de expansión
- Archivos Excel en la carpeta `results/` para cada heurística

---

## 📁 Estructura del repositorio

project/ <br>
│<br>
├── data/<br>
│ └── nodes_distance.csv<br>
│<br>
├── docs/<br>
│<br>
├── results/<br>
│ └── (aquí se generan los Excel con los resultados)<br>
│<br>
├── src/<br>
│ ├── main.py<br>
│ └── substation_astar.py<br>
│<br>
├── README.md<br>
└── requirements.txt<br>

Descripción:

src/ → Código fuente del proyecto

data/ → Datos de entrada (distancias reales entre nodos)

notebooks/ → Notebooks para exploración y pruebas

docs/ → Imágenes o documentación adicional

## 🧠 Cómo funciona el modelo de subestaciones

Cada subestación se define por:
- Nombre del nodo  
- Coordenadas (x, y)  
- Conexiones salientes  
- Distancia y FCC por arco  

El coste real se calcula como:

\[
\text{coste} = \text{distancia (km)} \times \text{FCC}
\]

---

## ▶ Ejecución

Desde la raíz del proyecto:


python src/main.py

El script:

Carga los datos desde data/nodes_distance.csv.

Ejecuta A* con las dos heurísticas disponibles.

Imprime la ruta óptima y su coste total.

Exporta los resultados en formato Excel a la carpeta results/.

📦 Dependencias

Instalar ejecutando:

pip install -r requirements.txt

📘 Estructura del dataset

El archivo nodes_distance.csv debe contener:

| start_node | end_node | dist_km | FCC |

El coste se obtiene multiplicando dist_km × FCC.

👨‍💻 Autor

Fernando Rubio Villar
