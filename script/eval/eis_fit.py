# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 10:51:49 2024

@author: Jaehyun
"""

from impedance.models.circuits import CustomCircuit, fitting
from impedance.visualization import plot_nyquist
from impedance import preprocessing
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import addcopyfighandler

f_pred = np.logspace(5,-2)


# rc3 = CustomCircuit(initial_guess=[.8, .1, .1, .1, .2, .2, .3],
#                     circuit='R0-p(R1,C1)-p(R2,C2)-p(R3,C3)')

# print(rc3)

# file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
# frequencies, Z = preprocessing.readCSV(file_path)
# rc3.fit(frequencies, Z)
# print(rc3)

# rc3_fit = rc3.predict(frequencies)

# # Calculate RMSE
# rmse = fitting.rmse(Z, rc3_fit)
# print(f'RMSE: {rmse:.4f}')

# fig, ax = plt.subplots(figsize=(5,5))
# plot_nyquist(Z, ax=ax)
# plot_nyquist(rc3_fit, fmt='-', ax=ax)

# ax.legend(['Data', 'Fitting'])
# plt.show()


# # 1 ZARC between two RC elements
# zarc = CustomCircuit(initial_guess=[.8, .1, .1, .1, .2, 1, .2, .3], 
#                             circuit='R0-p(R1,C1)-Zarc2-p(R3,C3)')

# print(zarc)

# file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
# frequencies, Z = preprocessing.readCSV(file_path)
# zarc.fit(frequencies, Z)
# print(zarc)

# zarc_fit = zarc.predict(frequencies)

# # Calculate RMSE
# rmse = fitting.rmse(Z, zarc_fit)
# print(f'RMSE: {rmse:.4f}')

# fig, ax = plt.subplots(figsize=(5,5))
# plot_nyquist(Z, ax=ax)
# plot_nyquist(zarc_fit, fmt='-', ax=ax)

# ax.legend(['Data', 'Fitting'])
# plt.show()


# 2 ZARCs
zarc = CustomCircuit(initial_guess=[.8, .1, .2, .5, .2, .3, .5], 
                            circuit='R0-Zarc1-Zarc2')

print(zarc)

file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
frequencies, Z = preprocessing.readCSV(file_path)
zarc.fit(frequencies, Z)
print(zarc)

zarc_fit = zarc.predict(frequencies)

# Calculate RMSE
rmse = fitting.rmse(Z, zarc_fit)
print(f'RMSE: {rmse:.4f}')

fig, ax = plt.subplots(figsize=(5,5))
plot_nyquist(Z, ax=ax)
plot_nyquist(zarc_fit, fmt='-', ax=ax)

ax.legend(['Data', 'Fitting'])
plt.show()