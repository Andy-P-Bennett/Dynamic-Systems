"""
Fit a first-order differential model to the data
"""

import scipy.io
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt

# Load the .mat file
data = scipy.io.loadmat('LexusData.mat')
# Contains: t1 v1 t2 v2 theta_deg units_note

# Extract variables from the loaded data
t1 = data['t1'].flatten()  # flatten to convert 2D arrays to 1D
v1 = data['v1'].flatten()

t2 = data['t2'].flatten()
v2 = data['v2'].flatten()

#Data wasn't monotonous/increasing, this strips out bad data points
t1, unique_idx1 = np.unique(t1, return_index=True)
v1 = v1[unique_idx1]

t2, unique_idx2 = np.unique(t2, return_index=True)
v2 = v2[unique_idx2]

# Linear Model and fitting
m = 1760+150 #kg
g = 9.81
theta = np.radians(1.03) #degrees

f_south = m*g*np.sin(theta)
f_north = -f_south  # going up against gravity

def ode(t, v, b, f_grav): #linear
    return (f_grav - b*v) / m

def error(b_guess):
    b = b_guess[0]
    sol_south = solve_ivp(
        fun = ode,
        t_span = (t1[0], t1[-1]),
        y0 = [v1[0]],
        t_eval = t1,
        args = (b, f_south)
    )    
    sol_north = solve_ivp(
        fun = ode,
        t_span = (t2[0], t2[-1]),
        y0 = [v2[0]],
        t_eval = t2,
        args = (b, f_north)
    )

    error_south = np.sum((v1 - sol_south.y[0]) ** 2)
    error_north = np.sum((v2 - sol_north.y[0]) ** 2)
    return error_south + error_north

minimum = minimize(error, x0=[20.0], bounds = [(0, None)])
b_out = minimum.x[0]
print(b_out)

sol_south_fit = solve_ivp(
    fun = ode,
    t_span = (t1[0], t1[-1]),
    y0 = [v1[0]],
    t_eval = t1,
    args = (b_out, f_south)
)

sol_north_fit = solve_ivp(
    fun = ode,
    t_span = (t2[0], t2[-1]),
    y0 = [v2[0]],
    t_eval = t2,
    args = (b_out, f_north)
)

# Comparison Plots
plt.figure(1)
plt.plot(t1, v1, label='South')
plt.plot(t2, v2, label='North')

# Plot fitted model as solid lines
plt.plot(t1, sol_south_fit.y[0], 'b-', linewidth=2, label='South (Fitted Model)')
plt.plot(t2, sol_north_fit.y[0], 'r-', linewidth=2, label='North (Fitted Model)')

plt.grid(True)
plt.xlabel('Time (s)')
plt.ylabel('Speed (m/s)')
plt.legend()
plt.title('Speed vs. Time, Data and Linear Model')

plt.show()