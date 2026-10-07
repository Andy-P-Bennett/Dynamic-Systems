"""
Fit a second-order differential model to the data
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

# Linear Model and fitting - Mu_K and C_d are unknown coefficients
m = 1760+150 #kg
g = 9.81
rho_f = 1.06
A_p = 2.15
theta = np.radians(1.03) #degrees

f_south = g*np.sin(theta)
f_north = -f_south  # going up against gravity
v_wind = 3.12928 # 7 mph -> m/s, from the North

def ode(t, v, mu_k, c_d, f_grav, v_wind): #linear
    return (f_grav - mu_k*g*np.cos(theta) - (c_d*A_p*rho_f*(v+v_wind)**2)/(2*m))

def error(guesses):
    mu_k = guesses[0]
    c_d = guesses[1]
    sol_south = solve_ivp(
        fun = ode,
        t_span = (t1[0], t1[-1]),
        y0 = [v1[0]],
        t_eval = t1,
        args = (mu_k, c_d, f_south, -v_wind) #going with the wind, so drag velocity decreased, '-'
    )    
    sol_north = solve_ivp(
        fun = ode,
        t_span = (t2[0], t2[-1]),
        y0 = [v2[0]],
        t_eval = t2,
        args = (mu_k, c_d, f_north, v_wind)
    )

    error_south = np.sum((v1 - sol_south.y[0]) ** 2)
    error_north = np.sum((v2 - sol_north.y[0]) ** 2)
    return error_south + error_north

minimum = minimize(error, x0=[0.02, 0.3], bounds = [(0, None), (0, None)])
MuK_out = minimum.x[0]
Cd_out = minimum.x[1]
print(MuK_out, Cd_out)

# Now we actually grab those output curves for the optimized Mu_K and C_d values
sol_south_fit = solve_ivp(
    fun = ode,
    t_span = (t1[0], t1[-1]),
    y0 = [v1[0]],
    t_eval = t1,
    args = (MuK_out, Cd_out, f_south, -v_wind)
)

sol_north_fit = solve_ivp(
    fun = ode,
    t_span = (t2[0], t2[-1]),
    y0 = [v2[0]],
    t_eval = t2,
    args = (MuK_out, Cd_out, f_north, v_wind)
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
plt.title('Speed vs. Time, Data and Nonlinear Model')

plt.show()