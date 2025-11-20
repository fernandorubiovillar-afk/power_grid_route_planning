import pandas as pd
import numpy as np
class Substation:
    def __init__(self, node_name, list_nodes):
        self.node = node_name
        self.list_nodes = list_nodes
        self.x,self.y = self.coordenates()
    def coordenates(self):
        i = self.list_nodes[0].index(self.node)
        coord = self.list_nodes[1][i]
        return coord
    def geometric_distance(self, solution_node):
        i = self.list_nodes[0].index(solution_node)
        coord = self.list_nodes[1][i]
        node_geometric_distance = np.sqrt((coord[0]-self.x)**2+(coord[1]-self.y)**2)
        return node_geometric_distance
    def is_solution(self, solution_node):
        if self.node == solution_node:
            sol = True
        else:
            sol = False
        return sol    
    
def A_star(start_node_name,list_nodes, distance, goal_node):
        sol = []
        explored = []

        #Dictionary to create the path
        came_from = {start_node_name: None}

        #Start node and start heuristic (the chosen heuristic is Direct Straight Line)
        start_sub = Substation(start_node_name, list_nodes = list_nodes)
        
        h0 = start_sub.geometric_distance(goal_node)
        g0 = 0.0

        frontier = [{'node_name':start_node_name,
                    'g':g0,
                    'cost':g0+h0,
                    'parent': None
                    }]
        while len(frontier) > 0:
            frontier.sort(key=lambda x: x['cost'])
            less_cost_node = frontier.pop(0)
            node = Substation(less_cost_node['node_name'],list_nodes=list_nodes)
            g_current = less_cost_node['g']

            #We evaluate if node is solution:
            if node.node == goal_node:
                #We rebuild the path from GOAL backwards to the start.
                path = [node.node]
                parent = came_from[node.node]
                while parent is not None:
                    path.append(parent)
                    parent = came_from[parent]
                path.reverse()
         
                solution_node = {'node_name': node.node,
                                'cost': g_current,
                                'path': path}
                sol.append(solution_node)
                print(f"Optimal path found: {' -> '.join(path)} with total cost: {g_current}")
                # Solution found. We can stop here.
                return sol, frontier, explored
            #If node not solution, then we included it into explored.
            explored.append(less_cost_node)

            #We expand the node with less cost on frontier
            actions = distance[distance['start_node']==node.node]
            #We evaluate the succesors to check if they have been already explored or if they should be included in the frontier
            for child in actions['end_node']:             
                child_node = Substation(child, list_nodes)

                #Cost from actual step of the path(from node.node to child)
                
                row = distance[(distance['start_node'] == node.node) & (distance['end_node'] == child)]
                if row.empty:
                    print(f"No cost define for the arc: {node.node} -> {child}, we ignore it.\n")
                    continue
                step_cost = float(row['real'].iloc[0])  # valor escalar
                g_child = g_current + step_cost
                h_child = child_node.geometric_distance(goal_node)
                f_child = g_child + h_child

                front = [x['node_name'] for x in frontier]
                exp = [x['node_name']for x in explored]

                # if child is not in frontier neither in explored, we added in .
                if (child_node.node not in front) and (child_node.node not in exp):
                    frontier.append({'node_name': child,
                                     'g': g_child,
                                    'cost': f_child,
                                    'parent': node.node
                                    })
                    came_from[child] = node.node

                # if child exists in frontier, we check if we found a cheaper path.
                elif (child_node.node in front):
                    for entry in frontier:
                        if entry['node_name'] == child:
                            old_cost = entry['cost']
                            old_g = entry['g']
                            break               
                    if old_cost > f_child:
                        entry['cost'] = f_child
                        entry['g'] = g_child
                        entry['parent'] = node.node
                        came_from[child] = node.node
        #if we exit the while loop, there is no solution
        print("No path has been found")
        sol.sort(key=lambda x: x['cost'])
        return sol, frontier, explored