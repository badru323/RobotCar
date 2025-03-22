def obstacleAvoidance(X, Y):
    delx = np.zeros_like(X)
    dely = np.zeros_like(Y)
    alpha = 50
    beta = 50
    s = 5
    r = .5

    for i in range(len(X)):
        for j in range(len(Y)):
            #finding the goal distance and obstacle distance
            d_goal = np.sqrt((goal[0] - X[i][j]) ** 2 + (goal[1] - Y[i][j]) ** 2)
            d_obs = np.sqrt((obstacle[0] - X[i][j]) ** 2 + (obstacle[1] - Y[i][j]) ** 2)

            #calculate repulsive and attractive forces
            F_rep = alpha * np.exp((d_obs - r) / s) / d_obs ** 2
            F_att = beta * (d_goal ** 2) / (d_goal ** 2 + 1)

            # Calculate x and y components of the resulting force
            delx[i][j] = F_att * (goal[0] - X[i][j]) / d_goal + F_rep * (X[i][j] - obstacle[0]) / d_obs
            dely[i][j] = F_att * (goal[1] - Y[i][j]) / d_goal + F_rep * (Y[i][j] - obstacle[1]) / d_obs

    #calculate the resultant x and y components of the force
    res_delx = np.sum(delx, axis=0)
    res_dely = np.sum(dely, axis=0)

    #calculate the angle of the resultant force
    angle = np.arctan2(res_dely, res_delx)

    #convert the angle to degrees and add 90 to get the steering direction
    steering_dir = np.degrees(angle) + 90

    #limit the steering direction to be between 0 and 359 degrees
    steering_dir = steering_dir % 360

    return steering_dir

#main function