# filename: run_mcmc_analysis.py
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import sys

# Ensure corner is installed
try:
    import corner
except ImportError:
    print("Installing corner package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "corner"])
    import corner

from codebase.mcmc_sampling import (
    run_mcmc, check_convergence, plot_chains, plot_corner, 
    compute_summary_statistics, plot_best_fit_model
)
from codebase.bayesian_framework import extract_observational_data

# Create data directory if it doesn't exist
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Set matplotlib parameters to avoid LaTeX rendering
plt.rcParams['text.usetex'] = False

# Extract observational data
print("Extracting observational constraints...")
obs_data = extract_observational_data()

# Print summary of observational data
print("Observational data summary:")
print("Number of data points: " + str(len(obs_data['z'])))
print("Redshift range: " + str(min(obs_data['z'])) + " to " + str(max(obs_data['z'])))
print("Measurement methods: " + str(np.unique(obs_data['method'])))

if 'tau_e' in obs_data:
    print("CMB optical depth constraint: " + str(obs_data['tau_e']) + " ± " + str(obs_data['tau_e_error']))

# Set MCMC parameters - using smaller values for demonstration
nwalkers = 32
nsteps = 200  # Reduced for demonstration, use 5000+ for production
discard = 50
z_range = (20.0, 5.0)
QHII_init = 1e-4
include_tau_e = True

# Run MCMC sampling
print("\nRunning MCMC sampling...")
start_time = time.time()
sampler, samples, flat_samples, param_names = run_mcmc(
    obs_data, nwalkers=nwalkers, nsteps=nsteps, z_range=z_range, 
    QHII_init=QHII_init, include_tau_e=include_tau_e, progress=False, discard=discard
)

# Check convergence
print("\nChecking convergence...")
convergence_results = check_convergence(sampler, discard=discard)

if 'converged' in convergence_results and convergence_results['converged']:
    print("MCMC chains have converged!")
else:
    print("Warning: MCMC chains may not have fully converged. Consider running for more steps.")

# Plot chains
print("\nGenerating diagnostic plots...")
chains_file = plot_chains(samples, param_names, discard=discard)

# Plot corner plot
corner_file = plot_corner(flat_samples, param_names)

# Compute summary statistics
print("\nComputing summary statistics...")
summary_stats = compute_summary_statistics(flat_samples, param_names)

# Plot best-fit model
print("\nGenerating best-fit model plot...")
model_file = plot_best_fit_model(flat_samples, obs_data, param_names, z_range=z_range, QHII_init=QHII_init)

# Calculate total runtime
end_time = time.time()
runtime = end_time - start_time
print("\nBayesian analysis completed in " + str(round(runtime, 2)) + " seconds")

# Save flat samples to file
samples_file = os.path.join(database_path, "mcmc_samples.npz")
np.savez(samples_file, flat_samples=flat_samples, param_names=param_names)
print("Saved MCMC samples to: " + samples_file)

# Print best-fit parameters
median_params = np.median(flat_samples, axis=0)
print("\nBest-fit parameters:")
for i, param in enumerate(param_names):
    print(param + ": " + str(median_params[i]))

# Calculate tau_e for best-fit model
from codebase.bayesian_framework import calculate_tau_e
from codebase.cosmic_reionization_model import solve_QHII

# Fixed parameters
xi0 = 2.5e25
M_h = 1.0e10

# Calculate best-fit model
full_params = tuple(median_params) + (xi0, M_h)
z_model, Q_HII_model = solve_QHII(z_range, full_params, QHII_init)

# Calculate tau_e
tau_e = calculate_tau_e(z_model, Q_HII_model)
print("\nCMB optical depth for best-fit model: " + str(tau_e))
if 'tau_e' in obs_data:
    print("Observed CMB optical depth: " + str(obs_data['tau_e']) + " ± " + str(obs_data['tau_e_error']))
