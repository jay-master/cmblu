# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 13:47:08 2024

@author: Jaehyun
"""

## Import necessary packages
# Python modules 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import pandas as pd
import importlib
from numpy import loadtxt
from matplotlib import gridspec # for the contour plots
from cvxopt import matrix, solvers

# pyDRTtools' modules
import pyDRTtools
import pyDRTtools.basics as basics # pyDRTtools functions
import pyDRTtools.GUI as UI

## for nice plot
# options for the plots
plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=15)
plt.rc('xtick', labelsize=15)
plt.rc('ytick', labelsize=15)
# matplotlib inline

## Load the data
df = pd.read_csv('E:/Projekte/vertraulich/CMBlu/meas_data/15th_new_cell_standard_45grad/ch1/15th_2nd_EIS&CCCV_nach_eis_45grad - Kopie.csv')
N_freqs = df.shape[0]
freq_vec = np.flip(df['Frequency (Hz)'].values)
Z_exp = np.flip(df['Zre (ohms)'].values + 1j*df['Zim (ohms)'].values)

## Define the range of timescales
N_taus = 64
log_tau_min = -4  
log_tau_max = 4   
tau_vec = np.logspace(log_tau_min, log_tau_max, num = N_taus, endpoint=True)
log_tau_vec = np.log(tau_vec)

## Define the discretization matrices
shape_control = 'FWHM Coefficient'
coeff = 0.5
# order of the derivative for the differentiation matrix M ('1st', '2nd')
# rbf_type = 'Piecewise Linear'
rbf_type = 'Gaussian'
# rbf_type = 'C0 Matern'
# rbf_type = 'C2 Matern'
# rbf_type = 'C4 Matern'
# rbf_type = 'C6 Matern'
# rbf_type = 'Inverse Quadratic'

cv_type = 'GCV'
# cv_type = 'mGCV'
# cv_type = 'rGCV'
# cv_type = 'LC'
# cv_type = 'kf'
# cv_type = 're-im'

## Compute the discretization matrices
# epsilon parameter
epsilon  = basics.compute_epsilon(freq_vec, coeff, rbf_type, shape_control)

# differentiation matrix for the real part of the impedance
# this includes the contributions of an Ohmic resistance, R_inf, and an inductance, L_0
A_re = basics.assemble_A_re(freq_vec, tau_vec, epsilon, rbf_type)

A_re_R_inf = np.ones((N_freqs, 1))
A_re_L_0 = np.zeros((N_freqs, 1))
A_re = np.hstack(( A_re_R_inf, A_re_L_0, A_re))

# differentiation matrix for the imaginary part of the impedance
A_im = basics.assemble_A_im(freq_vec, tau_vec, epsilon, rbf_type)

#assemble_A_im(freq_vec, tau_vec, epsilon, 'Piecewise Linear', flag1='simple', flag2='impedance')

A_im_R_inf = np.zeros((N_freqs, 1))
A_im_L_0 = 2*np.pi*freq_vec.reshape((N_freqs, 1))
A_im = np.hstack(( A_im_R_inf, A_im_L_0, A_im))

# complete discretization matrix
A = np.vstack((A_re, A_im))

## Define the differentiation matrix
# second-order differentiation matrix for ridge regression (RR)
M2 = np.zeros((N_taus+2, N_taus+2))
M2[2:,2:] = basics.assemble_M_2(tau_vec, epsilon, rbf_type)

## Select the regularization parameter
# regularization parameter obtained with generalized cross-validation (GCV)
lambda_value = basics.optimal_lambda(A_re, A_im, np.real(Z_exp), np.imag(Z_exp), M2, -3, freq_vec, False, 'GCV')

## Deconvolve the DRT from a single EIS spectrum
# we recover the DRT as a quadratic problem using cvxplot
lb = np.zeros([N_taus+2])
bound_mat = np.eye(lb.shape[0])

H_combined, c_combined = basics.quad_format_combined(A_re, A_im, np.real(Z_exp), np.imag(Z_exp), M2, lambda_value)

# set bound constraint
G = matrix(-np.identity(Z_exp.imag.shape[0]+2))
h = matrix(np.zeros(Z_exp.imag.shape[0]+2))
print("Shape of G:", G.size)
print("Shape of h:", h.size)

print("Rank of A:", np.linalg.matrix_rank(A))
print("Rank of G:", np.linalg.matrix_rank(G))
print("Rank of H_combined:", np.linalg.matrix_rank(H_combined))
epsilon = 1e-4  # Increased regularization parameter
H_combined_reg = H_combined + epsilon * np.eye(H_combined.shape[0])
print("Min and max of H_combined:", np.min(H_combined), np.max(H_combined))
print("Min and max of c_combined:", np.min(c_combined), np.max(c_combined))
print("Min and max of G:", np.min(G), np.max(G))
print("Sum of h:", np.sum(h))

scale_factor_H = np.max(np.abs(H_combined))
H_combined_scaled = H_combined / scale_factor_H
c_combined_scaled = c_combined / scale_factor_H

scale_factor_G = np.max(np.abs(G))
G_scaled = G / scale_factor_G if scale_factor_G != 0 else G

# Don't scale h if it's all zeros
h_scaled = h

solvers.options['show_progress'] = False
solvers.options['abstol'] = 1e-10
solvers.options['reltol'] = 1e-9
solvers.options['feastol'] = 1e-10

sol = solvers.qp(matrix(H_combined_scaled), matrix(c_combined_scaled), matrix(G_scaled), matrix(h_scaled))

if sol['status'] != 'optimal':
    print(f"Optimization failed with status: {sol['status']}")
else:
    print("Optimization successful")
# sol = solvers.qp(matrix(H_combined), matrix(c_combined),G,h)


## deconvolved DRT
x = np.array(sol['x']).flatten()

R_inf_DRT, L_0_DRT = x[0:2]
gamma_DRT = x[2:]

## plot the recovered DRT

fig = plt.gcf()
plt.semilogx(tau_vec, gamma_DRT, linewidth=4, color='black', label='DRT') 
plt.axis([1E-6, 1E2, 0, 20])
plt.legend(frameon=False, fontsize = 15, loc='upper left')
plt.xlabel(r'$\tau/\rm s$', fontsize = 20)
plt.ylabel(r'$\gamma/\Omega$', fontsize = 20)
fig.set_size_inches(6.472, 4)

plt.show()

## Recover the impedance
# the impedance is recovered as a matrix product
Z_DRT = A@x
Z_DRT = Z_DRT[0:N_freqs] + 1j*Z_DRT[N_freqs:]

## Nyquist plots
# Nyquist plots of the exact, experimental, and recovered DRTs
plt.plot(np.real(Z_DRT), -np.imag(Z_DRT), linewidth=4, color='black', label='RR')
plt.plot(np.real(Z_exp), -np.imag(Z_exp), 'o', markersize=7, color='red', label='exp')
plt.legend(frameon=False, fontsize = 15)
plt.axis('scaled')
plt.xticks(range(0, 90, 20))
plt.yticks(range(-40, 60, 20))
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel(r'$Z_{\rm re}/\Omega$', fontsize = 20)
plt.ylabel(r'$-Z_{\rm im}/\Omega$', fontsize = 20)
fig = plt.gcf()
fig.set_size_inches(6.472, 4)

plt.show()

## Save the recovered DRT and impedance
# save the DRT recovered with RR
gamma_DRT_excel = pd.DataFrame(gamma_DRT)
gamma_DRT_excel.to_csv('E:/Projekte/vertraulich/CMBlu/Jaehyun/eval_result/DRT/1ZARC_DRT-RR.csv',index=False)

# save the impedance recovered with RR
df = pd.DataFrame.from_dict({'Freq': freq_vec, 'Real': np.real(Z_DRT), 'Imag': np.imag(Z_DRT)})
df.to_csv('E:/Projekte/vertraulich/CMBlu/Jaehyun/eval_result/DRT/1ZARC_Z-RR.csv')