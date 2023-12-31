# -*- coding: utf-8 -*-
"""Part_1_pr_3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VQcMEpBpWJTXaBwgy8oqDad3BYe2K0H0
"""

!pip install casadi
from casadi import *

import numpy as np
from numpy import sin, cos, pi
import matplotlib.pyplot as plt
from matplotlib import animation
from time import time


def visualize(car_states, ref_traj, obstacles, t, time_step, save=False):
    init_state = car_states[0,:]
    def create_triangle(state=[0,0,0], h=0.5, w=0.25, update=False):
        x, y, th = state
        triangle = np.array([
            [h, 0   ],
            [0,  w/2],
            [0, -w/2],
            [h, 0   ]
        ]).T
        rotation_matrix = np.array([
            [cos(th), -sin(th)],
            [sin(th),  cos(th)]
        ])

        coords = np.array([[x, y]]) + (rotation_matrix @ triangle).T
        if update == True:
            return coords
        else:
            return coords[:3, :]

    def init():
        return path, current_state, target_state,

    def animate(i):
        # get variables
        x = car_states[i,0]
        y = car_states[i,1]
        th = car_states[i,2]

        # update path
        if i == 0:
            path.set_data(np.array([]), np.array([]))
        x_new = np.hstack((path.get_xdata(), x))
        y_new = np.hstack((path.get_ydata(), y))
        path.set_data(x_new, y_new)

        # update horizon
        #x_new = car_states[0, :, i]
        #y_new = car_states[1, :, i]
        #horizon.set_data(x_new, y_new)

        # update current_state
        current_state.set_xy(create_triangle([x, y, th], update=True))

        # update current_target
        x_ref = ref_traj[i,0]
        y_ref = ref_traj[i,1]
        th_ref = ref_traj[i,2]
        target_state.set_xy(create_triangle([x_ref, y_ref, th_ref], update=True))

        # update target_state
        # xy = target_state.get_xy()
        # target_state.set_xy(xy)

        return path, current_state, target_state,
    circles = []
    for obs in obstacles:
        circles.append(plt.Circle((obs[0], obs[1]), obs[2], color='r', alpha = 0.5))
    # create figure and axes
    fig, ax = plt.subplots(figsize=(6, 6))
    min_scale_x = min(init_state[0], np.min(ref_traj[:,0])) - 1.5
    max_scale_x = max(init_state[0], np.max(ref_traj[:,0])) + 1.5
    min_scale_y = min(init_state[1], np.min(ref_traj[:,1])) - 1.5
    max_scale_y = max(init_state[1], np.max(ref_traj[:,1])) + 1.5
    ax.set_xlim(left = min_scale_x, right = max_scale_x)
    ax.set_ylim(bottom = min_scale_y, top = max_scale_y)
    for circle in circles:
        ax.add_patch(circle)
    # create lines:
    #   path
    path, = ax.plot([], [], 'k', linewidth=2)

    #   current_state
    current_triangle = create_triangle(init_state[:3])
    current_state = ax.fill(current_triangle[:, 0], current_triangle[:, 1], color='r')
    current_state = current_state[0]
    #   target_state
    target_triangle = create_triangle(ref_traj[0,0:3])
    target_state = ax.fill(target_triangle[:, 0], target_triangle[:, 1], color='b')
    target_state = target_state[0]

    #   reference trajectory
    ax.scatter(ref_traj[:,0], ref_traj[:,1], marker='x')

    sim = animation.FuncAnimation(
        fig=fig,
        func=animate,
        init_func=init,
        frames=len(t),
        interval=time_step*100,
        blit=True,
        repeat=True
    )
    plt.show()

    if save == True:
        sim.save('/content/drive/MyDrive/fig' + str(time()) +'.gif', writer='ffmpeg', fps=15)

    return

#%%
from time import time
import numpy as np
from casadi import *

#%%
# Simulation params
np.random.seed(10)
time_step = 0.5 # time between steps in seconds
sim_time = 120    # simulation time

# Car params
x_init = 1.5
y_init = 0.0
theta_init = np.pi/2
v_max = 1
v_min = 0
w_max = 1
w_min = -1

# This function returns the reference point at time step k
def lissajous(k):
    xref_start = 0
    yref_start = 0
    A = 2
    B = 2
    a = 2*np.pi/50
    b = 3*a
    T = np.round(2*np.pi/(a*time_step))
    # print(T)
    k = k % T
    delta = np.pi/2
    xref = xref_start + A*np.sin(a*k*time_step + delta)
    yref = yref_start + B*np.sin(b*k*time_step)
    v = [A*a*np.cos(a*k*time_step + delta), B*b*np.cos(b*k*time_step)]
    thetaref = np.arctan2(v[1], v[0])
    return [xref, yref, thetaref]

# This function implements a simple P controller
def simple_controller(cur_state, ref_state):
    k_v = 0.55
    k_w = 1.0
    v = k_v*np.sqrt((cur_state[0] - ref_state[0])**2 + (cur_state[1] - ref_state[1])**2)
    v = np.clip(v, v_min, v_max)
    angle_diff = ref_state[2] - cur_state[2]
    angle_diff = (angle_diff + np.pi) % (2 * np.pi ) - np.pi
    w = k_w*angle_diff
    w = np.clip(w, w_min, w_max)
    return [v,w]

def calculate_objective(error_val, controls_val, Q_val, q_val, R_val):
    Value_fun = 0
    N_val = controls_val.shape[1]
    for i in range(N_val):
        Value_fun += (error_val[:2, i].T @ Q_val @ error_val[:2, i] + q_val * (1 - cos(error_val[2, i]))**2 + controls_val[:, i].T @ R_val @ controls_val[:, i])
    Value_fun += error_val[:, -1].T @ error_val[:, -1]
    return Value_fun


def apply_constraints(opti, error_val, controls_val, error_param, ref_func, cur_iter):
    N_val = controls_val.shape[1]
    opti.subject_to(opti.bounded(0, controls_val[0, :], 1))
    opti.subject_to(opti.bounded(-1, controls_val[1, :], 1))
    opti.subject_to(error_val[:, 0] == error_param)
    for i in range(1, N_val + 1):
        ref_t_val = ref_func(cur_iter + i)
        ref_t_1_val = ref_func(cur_iter + i - 1)
        opti.subject_to(error_val[:, i] == error_val[:, i - 1] + vertcat(hcat([0.5 * cos(error_val[2, i - 1] + ref_t_1_val[2]), 0]),
                                                                      hcat([0.5 * sin(error_val[2, i - 1] + ref_t_1_val[2]), 0]),
                                                                      hcat([0, 0.5])) @ controls_val[:, i - 1] -
                        vcat([ref_t_val[0] - ref_t_1_val[0], ref_t_val[1] - ref_t_1_val[1], (ref_t_val[2] - ref_t_1_val[2] + np.pi) % (2 * np.pi) - np.pi]))

        opti.subject_to(opti.bounded(vcat([-3, -3]), error_val[:2, i] + vcat([ref_t_val[0], ref_t_val[1]]), vcat([3, 3])))
        opti.subject_to((error_val[0, i] + ref_t_val[0] + 2) ** 2 + (error_val[1, i] + ref_t_val[1] + 2) ** 2 > 0.5 ** 2)
        opti.subject_to((error_val[0, i] + ref_t_val[0] - 1) ** 2 + (error_val[1, i] + ref_t_val[1] - 2) ** 2 > 0.5 ** 2)


def cec_control(cur_state, ref, cur_iter):
    Q_val, q_val, R_val, T_val = 10, 30, 15, 10 ########################################################################################

    Q_p_val = Q_val * np.eye(2)
    R_p_val = R_val * np.eye(2)

    cur_ref_val = ref
    error_x_val = cur_state[0] - cur_ref_val[0]
    error_y_val = cur_state[1] - cur_ref_val[1]
    error_theta_val = cur_state[2] - cur_ref_val[2]
    error_theta_val = (error_theta_val + np.pi) % (2 * np.pi) - np.pi

    opti = Opti()

    controls_val = opti.variable(2, T_val)
    error_val = opti.variable(3, T_val + 1)
    error_param = opti.parameter(3, 1)
    opti.set_value(error_param, vcat([error_x_val, error_y_val, error_theta_val]))

    Value_fun = calculate_objective(error_val, controls_val, Q_val, q_val, R_val)
    opti.minimize(Value_fun)
    apply_constraints(opti, error_val, controls_val, error_param, traj, cur_iter)

    opti.solver('ipopt')
    sol = opti.solve()

    return sol.value(controls_val)[:, 0][0], sol.value(controls_val)[:, 0][1]



# This function implement the car dynamics
def car_next_state(time_step, cur_state, control, noise = True):
    theta = cur_state[2]
    rot_3d_z = np.array([[np.cos(theta), 0], [np.sin(theta), 0], [0, 1]])
    f = rot_3d_z @ control
    mu, sigma = 0, 0.04 # mean and standard deviation for (x,y)
    w_xy = np.random.normal(mu, sigma, 2)
    mu, sigma = 0, 0.004  # mean and standard deviation for theta
    w_theta = np.random.normal(mu, sigma, 1)
    w = np.concatenate((w_xy, w_theta))
    if noise:
        return cur_state + time_step*f.flatten() + w
    else:
        return cur_state + time_step*f.flatten()
#%%
if __name__ == '__main__':
    # Obstacles in the environment
    obstacles = np.array([[-2,-2,0.5], [1,2,0.5]])
    # Params
    traj = lissajous
    ref_traj = []
    error = 0.0
    car_states = []
    times = []
    # Start main loop
    main_loop = time()  # return time in sec
    # Initialize state
    cur_state = np.array([x_init, y_init, theta_init])
    cur_iter = 0
    # Main loop
    while (cur_iter * time_step < sim_time):
        t1 = time()
        # Get reference state
        cur_time = cur_iter*time_step
        cur_ref = traj(cur_iter)
        # Save current state and reference state for visualization
        ref_traj.append(cur_ref)
        car_states.append(cur_state)

        ################################################################
        # Generate control input
        # TODO: Replace this simple controller with your own controller
        # control = simple_controller(cur_state, cur_ref)
        v,w = cec_control(cur_state, cur_ref,cur_iter)
        v = np.clip(v, v_min, v_max)
        w = np.clip(w,w_min, w_max)
        ################################################################

        # Apply control input
        next_state = car_next_state(time_step, cur_state, [v,w], noise=True)
        # Update current state
        cur_state = next_state

        t2 = time()

        times.append(t2-t1)
        error= error + np.linalg.norm([cur_state[0] - cur_ref[0], cur_state[1] - cur_ref[1],
        (cur_state[2] - cur_ref[2] + np.pi) % (2*np.pi) - np.pi])
        cur_iter = cur_iter + 1

    main_loop_time = time()
    print('\n\n')
    print('Total time: ', main_loop_time - main_loop)
    print('Average iteration time: ', np.array(times).mean() * 1000, 'ms')
    print('Final error: ', error)

    # Visualization
    ref_traj = np.array(ref_traj)
    car_states = np.array(car_states)
    times = np.array(times)
    visualize(car_states, ref_traj, obstacles, times, time_step, save=True)