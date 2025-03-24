import numpy as np

# Global variables used by the mesh-based APF functions.
goal = (0.0, 1.0)       # Local goal in (x, y)
obstacle = (0.0, 999.0) # Local obstacle in (x, y); 999 implies "very far away"

def set_goal(gx, gy):
    global goal
    goal = (gx, gy)

def set_obstacle(ox, oy):
    global obstacle
    obstacle = (ox, oy)

# Creating mesh
def create_grid(x_min=-1.0, x_max=1.0, y_min=0.0, y_max=2.0, step=0.1):
    x = np.arange(x_min, x_max + step, step)
    y = np.arange(y_min, y_max + step, step)
    X, Y = np.meshgrid(x, y)
    return X, Y

def obstacleAvoidance(X, Y, alpha=50, beta=50, s=5, r=0.5):
    global goal, obstacle
    gx, gy = goal
    ox, oy = obstacle

    # Initialize force arrays.
    delx = np.zeros_like(X)
    dely = np.zeros_like(Y)

    for i in range(len(X)):
        for j in range(len(X[i])):
            px = X[i][j]
            py = Y[i][j]

            # Compute distances (adding a small value to avoid division by zero).
            d_goal = np.sqrt((gx - px) ** 2 + (gy - py) ** 2) + 1e-9
            d_obs = np.sqrt((ox - px) ** 2 + (oy - py) ** 2) + 1e-9

            # Attractive force (toward goal)
            F_att = beta * (d_goal ** 2) / (d_goal ** 2 + 1.0)

            # Repulsive force (away from obstacle)
            F_rep = alpha * np.exp((d_obs - r) / s) / (d_obs ** 2)

            # Decompose forces into x and y components.
            delx[i][j] = F_att * (gx - px) / d_goal + F_rep * (px - ox) / d_obs
            dely[i][j] = F_att * (gy - py) / d_goal + F_rep * (py - oy) / d_obs

    # Sum the forces across the grid.
    res_delx = np.sum(delx)
    res_dely = np.sum(dely)

    #  0° is +X and 90° is +Y.
    angle = np.arctan2(res_dely, res_delx)
    steering_dir = (np.degrees(angle) + 90.0) % 360.0

    return steering_dir

def computeSteering(heading_deg, lane_offset_m, obstacle_dist, alpha=50, beta=50, s=5, r=0.5):
    # Convert heading to radians.
    hdg_rad = np.radians(heading_deg)

    # Define a forward target 1.0 m ahead along the heading.
    forward_x = np.cos(hdg_rad) * 1.0
    forward_y = np.sin(hdg_rad) * 1.0

    # Compute a lateral offset perpendicular to the heading.
    offset_x = -np.sin(hdg_rad) * lane_offset_m
    offset_y =  np.cos(hdg_rad) * lane_offset_m

    # Combine to form the final goal.
    gx = forward_x + offset_x
    gy = forward_y + offset_y
    set_goal(gx, gy)

    # Set the obstacle position.
    if obstacle_dist < 999:
        set_obstacle(0.0, obstacle_dist)
    else:
        set_obstacle(0.0, 999.0)

    # Create a small grid ahead of the vehicle.
    X, Y = create_grid(x_min=-1.0, x_max=1.0, y_min=0.0, y_max=2.0, step=0.1)

    # Calculate and return the steering direction.
    steering_dir = obstacleAvoidance(X, Y, alpha, beta, s, r)
    return steering_dir