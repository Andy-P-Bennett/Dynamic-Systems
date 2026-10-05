"""
Fit a first-order differential model to the data
"""

import scipy.io
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

# Optional: Display any notes from the .mat file
if 'units_note' in data:
    print(data['units_note'])

# Linear Model and fitting

# Comparison Plots
plt.figure(1)
plt.plot(t1, v1, label='South')
plt.plot(t2, v2, label='North')
plt.grid(True)
plt.xlabel('Time (s)')
plt.ylabel('Speed (m/s)')
plt.legend()
plt.title('Speed vs. Time')

plt.show()