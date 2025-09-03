# filename: codebase/run_mcmc_analysis.py
import numpy as np
import matplotlib.pyplot as plt
import os
import time
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

def run_bayesian_analysis(nwalkers=32, nsteps=1000, discard=200, z_range=(20.0, 5.0), 
                          QHII_init=1e-4, include_tau_e=True):
    """
    Run the complete Bayesian parameter estimation workflow.
    
    Parameters:
    -----------
    nwalkers : int, optional
        Number of walkers for MCMC
    nsteps : int, optional
        Number of steps per walker
    discard : int, optional
        Number of steps to discard as burn-in
    z_range : tuple, optional
        Redshift range for model calculation
    QHII_init : float, optional
        Initial ionization fraction
    include_tau_e : bool, optional
        Whether to include CMB optical depth constraint
        
    Returns:
    --------
    tuple
        (flat_samples, param_names, summary_stats) containing the MCMC results
    """
    print("Starting Bayesian analysis of cosmic reionization model")
    start_time = time.time()
    
    # Extract observational data
    print("Extracting observational constraints...")
    obs_data = extract_observational_data()
    
    # Print summary of observational data
    print("Observational data summary:")
    print("Number of data points:", len(obs_data['z']))
    print("Redshift range:", min(obs_data['z']), "to", max(obs_data['z']))
    print("Measurement methods:", np.unique(obs_data['method']))
    
    if 'tau_e' in obs_data:
        print("CMB optical depth constraint:", obs_data['tau_e'], "±", obs_data['tau_e_error'])
    
    # Run MCMC sampling
    print("\nRunning MCMC sampling...")
    sampler, samples, flat_samples, param_names = run_mcmc(
        obs_data, nwalkers=nwalkers, nsteps=nsteps, z_range=z_range, 
        QHII_init=QHII_init, include_tau_e=include_tau_e, progress=True, discard=discard
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
    print("\nBayesian analysis completed in", round(runtime, 2), "seconds")
    
    # Save flat samples to file
    samples_file = os.path.join(database_path, "mcmc_samples.npz")
    np.savez(samples_file, flat_samples=flat_samples, param_names=param_names)
    print("Saved MCMC samples to:", samples_file)
    
    return flat_samples, param_names, summary_stats


if __name__ == "__main__":
    # Run the analysis with default parameters
    flat_samples, param_names, summary_stats = run_bayesian_analysis(
        nwalkers=32,
        nsteps=1000,  # Reduced for demonstration, use 5000+ for production
        discard=200,
        z_range=(20.0, 5.0),
        QHII_init=1e-4,
        include_tau_e=True
    )