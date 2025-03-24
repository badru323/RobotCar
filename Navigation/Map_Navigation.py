import math
import heapq

# Convert from centimeters to meters. 
# Each row: "Horizontal Road" + "_" + "Vertical Road": (X/100, Y/100).

# DOUBLE CHECK IM SLEEP DEPRIVED MAKING THIS TABLE LIST

INTERSECTIONS = {
    # Aquatic Ave.
    "AquaticAve_BeakSt":       (4.52, 0.29),
    "AquaticAve_FeatherSt":    (3.05, 0.29),
    "AquaticAve_WaddleWay":    (1.29, 0.29),
    "AquaticAve_WaterfoulWay": (2.13, 0.29),

    # Breadcrumb Ave.
    "BreadcrumbAve_TheCircle": (2.84, 3.93),
    "BreadcrumbAve_WaddleWay": (1.81, 4.59),

    # The Circle
    "TheCircle_FeatherSt":     (3.05, 2.96),
    "TheCircle_WaterfoulWay":  (2.73, 3.07),
    "TheCircle_350324":        (3.50, 3.24),

    # Dabbler Dr.
    "DabblerDr_BeakSt":        (4.52, 2.93),
    "DabblerDr_MallardSt":     (5.85, 2.93),

    # Drake Dr.
    "DrakeDr_BeakSt":          (4.52, 4.02),
    "DrakeDr_MallardSt":       (5.76, 3.54),

    # Duckling Dr.
    "DucklingDr_BeakSt":       (4.52, 4.74),
    "DucklingDr_MallardSt":    (5.93, 3.54), 

    # Migration Ave.
    "MigrationAve_BeakSt":       (4.52, 1.35),
    "MigrationAve_FeatherSt":    (3.05, 1.35),
    "MigrationAve_MallardSt":    (5.85, 1.35),
    "MigrationAve_QuackSt":      (0.29, 1.35),
    "MigrationAve_WaddleWay":    (1.29, 1.35),
    "MigrationAve_WaterfoulWay": (2.13, 1.35),

    # Pondside Ave.
    "PondsideAve_BeakSt":       (4.52, 2.33),
    "PondsideAve_FeatherSt":    (3.05, 2.33),
    "PondsideAve_MallardSt":    (5.85, 2.33), 
    "PondsideAve_QuackSt":      (0.28, 3.29),
    "PondsideAve_WaterfoulWay": (2.14, 2.41),
    "PondsideAve_WaddleWay":    (1.57, 2.66),
    
    # Tail Ave.
    "TailAve_BeakSt":           (4.52, 4.65),
    "TailAve_TheCircle":        (3.35, 3.87),
}

# connect them in ascending order along each horizontal/vertical road.

HORIZONTAL_ROADS = {
    "AquaticAve": [
        "AquaticAve_WaddleWay",
        "AquaticAve_WaterfoulWay",
        "AquaticAve_FeatherSt",
        "AquaticAve_BeakSt",
    ],
    "BreadcrumbAve": [
        "BreadcrumbAve_WaddleWay",
        "BreadcrumbAve_TheCircle",
    ],
    "DabblerDr": [
        "DabblerDr_BeakSt",
        "DabblerDr_MallardSt",
    ],
    "DrakeDr": [
        "DrakeDr_BeakSt",
        "DrakeDr_MallardSt",
    ],
    "DucklingDr": [
        "DucklingDr_BeakSt",
        "DucklingDr_MallardSt",
    ],
    "MigrationAve": [
        "MigrationAve_QuackSt",
        "MigrationAve_WaddleWay",
        "MigrationAve_WaterfoulWay",
        "MigrationAve_FeatherSt",
        "MigrationAve_BeakSt",
        "MigrationAve_MallardSt",
    ],
    "PondsideAve": [
        "PondsideAve_QuackSt",
        "PondsideAve_WaddleWay",
        "PondsideAve_WaterfoulWay",
        "PondsideAve_FeatherSt",
        "PondsideAve_BeakSt",
        "PondsideAve_MallardSt",
    ],
    "TailAve": [
        "TailAve_TheCircle",
        "TailAve_BeakSt",
    ],
}

VERTICAL_ROADS = {
    "BeakSt": [
        "AquaticAve_BeakSt",
        "MigrationAve_BeakSt",
        "PondsideAve_BeakSt",
        "DabblerDr_BeakSt",
        "DrakeDr_BeakSt",
        "TailAve_BeakSt",
        "DucklingDr_BeakSt",
    ],
    "FeatherSt": [
        "AquaticAve_FeatherSt",
        "MigrationAve_FeatherSt",
        "PondsideAve_FeatherSt",
        "TheCircle_FeatherSt",
    ],
    "WaddleWay": [
        "AquaticAve_WaddleWay",
        "MigrationAve_WaddleWay",
        "BreadcrumbAve_WaddleWay",
        "PondsideAve_WaddleWay",
    ],
    "WaterfoulWay": [
        "AquaticAve_WaterfoulWay",
        "MigrationAve_WaterfoulWay",
        "TheCircle_WaterfoulWay",
        "PondsideAve_WaterfoulWay",
    ],
    "MallardSt": [
        "MigrationAve_MallardSt",
        "PondsideAve_MallardSt",
        "DabblerDr_MallardSt",
        "DrakeDr_MallardSt",
        "DucklingDr_MallardSt",
    ],
    "TheCircle": [
        "BreadcrumbAve_TheCircle",
        "TheCircle_FeatherSt",
        "TheCircle_WaterfoulWay",
        "TailAve_TheCircle",
        "TheCircle_350324",
    ],
    # QuackSt might only appear in "MigrationAve_QuackSt" or "PondsideAve_QuackSt" 
    "QuackSt": [
        "MigrationAve_QuackSt",
        "PondsideAve_QuackSt",
    ],
}

def euclidean_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def connect_in_order(nodes_list, graph):
    valid_nodes = [n for n in nodes_list if n in INTERSECTIONS]
    if len(valid_nodes) < 2:
        return

    valid_nodes.sort(key=lambda n: (INTERSECTIONS[n][0], INTERSECTIONS[n][1]))
    for i in range(len(valid_nodes) - 1):
        n1 = valid_nodes[i]
        n2 = valid_nodes[i+1]
        p1 = INTERSECTIONS[n1]
        p2 = INTERSECTIONS[n2]
        dist = euclidean_dist(p1, p2)
        graph.setdefault(n1, []).append((n2, dist))
        graph.setdefault(n2, []).append((n1, dist))

# Adjanecy List
def build_road_graph():
    graph = {}

    # Connect horizontal roads
    for road, nodes in HORIZONTAL_ROADS.items():
        connect_in_order(nodes, graph)

    # Connect vertical roads
    for road, nodes in VERTICAL_ROADS.items():
        connect_in_order(nodes, graph)

    # Ensure every intersection is in the graph
    for node in INTERSECTIONS:
        graph.setdefault(node, [])

    return graph

# A* stuff
def heuristic_cost_estimate(nodeA, nodeB):
    pA = INTERSECTIONS[nodeA]
    pB = INTERSECTIONS[nodeB]
    return euclidean_dist(pA, pB)

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    total_path.reverse()
    return total_path

def a_star_search(graph, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {n: float('inf') for n in graph}
    g_score[start] = 0.0
    f_score = {n: float('inf') for n in graph}
    f_score[start] = heuristic_cost_estimate(start, goal)

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)

        for (neighbor, dist) in graph[current]:
            tentative_g = g_score[current] + dist
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic_cost_estimate(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

def find_closest_node(x, y):
    closest = None
    closest_dist = float('inf')
    for node, pos in INTERSECTIONS.items():
        d = euclidean_dist((x, y), pos)
        if d < closest_dist:
            closest_dist = d
            closest = node
    return closest

def plan_route(curr_x, curr_y, goal_x, goal_y):
    """
    1) Build the road graph
    2) Find the closest intersection to (curr_x, curr_y)
    3) Find the closest intersection to (goal_x, goal_y)
    4) Run A* from start_node to end_node
    5) Return a list of (x,y) in meters
    """
    graph = build_road_graph()
    start_node = find_closest_node(curr_x, curr_y)
    end_node   = find_closest_node(goal_x, goal_y)

    if start_node not in graph or end_node not in graph:
        print("plan_route: Start or end node not in graph.")
        return []

    path_nodes = a_star_search(graph, start_node, end_node)
    if not path_nodes:
        print("plan_route: No path found by A*.")
        return []

    # Convert node names to (x,y)
    path_coords = [INTERSECTIONS[n] for n in path_nodes]
    return path_coords

def euclidean_dist_coords(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def direct_heading(curr_x, curr_y, goal_x, goal_y):
    """
    Returns the heading in degrees from the current position to the goal.
    0° corresponds to the +X direction and 90° to the +Y direction.
    """
    dx = goal_x - curr_x
    dy = goal_y - curr_y
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg
