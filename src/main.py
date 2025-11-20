import pandas as pd
import os
from src.substations_astar import Substation, A_star

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "nodes_distance.csv")


nodes = ['A','B','C','D','E','F','G','H']
coord = [[200,700],
        [400,800],
        [700,800],
        [500,800],
        [600,300],
        [300,400],
        [200,100],
        [800,100]]
list_nodes = [nodes,coord]
dist_real = pd.read_csv(CSV_PATH, delimiter=";")
dist_real['real'] = dist_real['dist_km']*dist_real['FCC']

sol,frontier,explored = A_star('A',list_nodes,dist_real,'H')
