# filename: codebase/mcmc_sampling.py
import numpy as np
import matplotlib.pyplot as plt
import emcee
import corner
import os
import time
from multiprocessing import Pool
from scipy.stats import norm
import pandas as pd
from codebase.cosmic_reionization_model import solve_QHII
from codebase.bayesian_framework import (
    extract_observational_data, log_posterior, calculate_tau_e
)

# Create data directory if it doesn't exist
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Set matplotlib parameters to avoid LaTeX rendering
plt.rcParams['text.usetex'] = False


def run_mcmc(obs_data, nwalkers=32, nsteps=1000, ndim=5, z_range=(20.0, 5.0), 
             QHII_init=1e-4, include_tau_e=True, progress=False, discard=200):
    """
    Run MCMC sampling to obtain posterior distributions for model parameters.
    
    Parameters:
    -----------
    obs_data : dict
        Dictionary containing observational data
    nwalkers : int, optional
        Number of walkers
    nsteps : int, optional
        Number of steps per walker
    ndim : int, optional
        Number of dimensions (parameters)
    z_range : tuple, optional
        Redshift range for model calculation
    QHII_init : float, optional
        Initial ionization fraction
    include_tau_e : bool, optional
        Whether to include CMB optical depth constraint
    progress : bool, optional
        Whether to show progress bar
    discard : int, optional
        Number of steps to discard as burn-in
        
    Returns:
    --------
    tuple
        (sampler, samples, flat_samples, param_names) containing the emcee sampler and samples
    """
    # Define parameter names and initial values
    param_names = ['f0', 'alpha', 'beta', 'C0', 'gamma']
    
    # Fixed parameters
    xi0 = 2.5e25
    M_h = 1.0e10
    
    # Define initial positions for walkers with some dispersion
    # Initial values based on literature and physical considerations
    initial_positions = np.array([
        0.1,    # f0: escape fraction normalization
        2.0,    # alpha: redshift dependence of escape fraction
        -0.5,   # beta: halo mass dependence of escape fraction
        3.0,    # C0: clumping factor normalization
        1.0     # gamma: redshift dependence of clumping factor
    ])
    
    # Add dispersion to initial positions
    pos = initial_positions + 0.01 * np.random.randn(nwalkers, ndim)
    
    # Ensure initial positions are within prior ranges
    pos[:, 0] = np.clip(pos[:, 0], 0.01, 0.99)  # f0
    pos[:, 1] = np.clip(pos[:, 1], -1.9, 4.9)   # alpha
    pos[:, 2] = np.clip(pos[:, 2], -1.9, 1.9)   # beta
    pos[:, 3] = np.clip(pos[:, 3], 1.1, 19.9)   # C0
    pos[:, 4] = np.clip(pos[:, 4], 0.1, 2.9)    # gamma
    
    # Define log probability function for emcee
    def log_prob(p):
        # Add fixed parameters
        full_params = tuple(p) + (xi0, M_h)
        return log_posterior(full_params, obs_data, z_range, QHII_init, include_tau_e)
    
    # Set up the sampler
    print("Setting up MCMC sampler with " + str(nwalkers) + " walkers and " + str(ndim) + " dimensions")
    
    # Use multiprocessing for parallel sampling
    with Pool() as pool:
        sampler = emcee.EnsembleSampler(
            nwalkers, ndim, log_prob, pool=pool
        )
        
        # Run the sampler
        print("Running MCMC sampling for " + str(nsteps) + " steps...")
        start_time = time.time()
        sampler.run_mcmc(pos, nsteps, progress=progress)
        end_time = time.time()
        print("MCMC sampling completed in " + str(round(end_time - start_time, 2)) + " seconds")
    
    # Get the samples
    samples = sampler.get_chain()
    
    # Discard burn-in and flatten the chain
    flat_samples = sampler.get_chain(discard=discard, thin=15, flat=True)
    
    # Print acceptance fraction
    print("Mean acceptance fraction: " + str(np.mean(sampler.acceptance_fraction)))
    
    return sampler, samples, flat_samples, param_names


def check_convergence(sampler, discard=200):
    """
    Check convergence of the MCMC chains using autocorrelation time.
    
    Parameters:
    -----------
    sampler : emcee.EnsembleSampler
        MCMC sampler
    discard : int, optional
        Number of steps to discard as burn-in
        
    Returns:
    --------
    dict
        Dictionary containing convergence diagnostics
    """
    # Calculate autocorrelation time
    try:
        tau = sampler.get_autocorr_time()
        print("Autocorrelation time:")
        for i, t in enumerate(tau):
            print("Parameter " + str(i) + " : " + str(t))
        
        # Check if we have enough samples
        n_steps = sampler.iteration
        thin = int(np.max(tau) / 2)
        n_effective = (n_steps - discard) / thin / tau
        
        print("Number of effective samples:")
        for i, n in enumerate(n_effective):
            print("Parameter " + str(i) + " : " + str(n))
        
        # Gelman-Rubin-like diagnostic
        # Split chains in half and compare means
        nwalkers = sampler.nwalkers
        ndim = sampler.ndim
        half_nwalkers = nwalkers // 2
        
        samples = sampler.get_chain(discard=discard)
        
        # Calculate means for each half
        means1 = np.mean(samples[:, :half_nwalkers, :], axis=(0, 1))
        means2 = np.mean(samples[:, half_nwalkers:, :], axis=(0, 1))
        
        # Calculate variances for each half
        vars1 = np.var(samples[:, :half_nwalkers, :], axis=(0, 1))
        vars2 = np.var(samples[:, half_nwalkers:, :], axis=(0, 1))
        
        # Calculate Gelman-Rubin R statistic
        W = (vars1 + vars2) / 2  # Within-chain variance
        B = ((means1 - means2)**2) / 2  # Between-chain variance
        var_hat = W + B  # Pooled variance
        R_hat = np.sqrt(var_hat / W)  # Gelman-Rubin statistic
        
        print("Gelman-Rubin R statistic:")
        for i, r in enumerate(R_hat):
            print("Parameter " + str(i) + " : " + str(r))
        
        converged = np.all(R_hat < 1.1) and np.all(n_effective > 50)
        
        return {
            'tau': tau,
            'n_effective': n_effective,
            'R_hat': R_hat,
            'converged': converged,
            'thin': thin
        }
    except Exception as e:
        print("Error calculating convergence diagnostics: " + str(e))
        return {
            'converged': False,
            'error': str(e)
        }


def plot_chains(samples, param_names, discard=200):
    """
    Plot the MCMC chains to visualize convergence.
    
    Parameters:
    -----------
    samples : array-like
        MCMC samples
    param_names : list
        List of parameter names
    discard : int, optional
        Number of steps to discard as burn-in
        
    Returns:
    --------
    str
        Filename of the saved plot
    """
    nsteps, nwalkers, ndim = samples.shape
    
    fig, axes = plt.subplots(ndim, figsize=(10, 2*ndim), dpi=300)
    
    for i in range(ndim):
        ax = axes[i]
        ax.plot(samples[:, :, i], alpha=0.3)
        ax.set_ylabel(param_names[i])
        ax.axvline(discard, color='red', linestyle='--')
    
    axes[-1].set_xlabel("Step Number")
    plt.tight_layout()
    
    # Save the figure
    filename = os.path.join(database_path, "mcmc_chains_" + str(np.random.randint(10000)) + ".png")
    plt.savefig(filename, dpi=300)
    plt.close()
    
    print("Saved MCMC chains plot to: " + filename)
    return filename


def plot_corner(flat_samples, param_names, truths=None):
    """
    Create a corner plot of the parameter posteriors.
    
    Parameters:
    -----------
    flat_samples : array-like
        Flattened MCMC samples
    param_names : list
        List of parameter names
    truths : array-like, optional
        True parameter values for comparison
        
    Returns:
    --------
    str
        Filename of the saved plot
    """
    # Create corner plot
    fig = corner.corner(
        flat_samples, 
        labels=param_names,
        quantiles=[0.16, 0.5, 0.84],
        show_titles=True,
        title_kwargs={"fontsize": 12},
        truths=truths
    )
    
    # Save the figure
    filename = os.path.join(database_path, "corner_plot_" + str(np.random.randint(10000)) + ".png")
    plt.savefig(filename, dpi=300)
    plt.close()
    
    print("Saved corner plot to: " + filename)
    return filename


def compute_summary_statistics(flat_samples, param_names):
    """
    Compute summary statistics for the parameter posteriors.
    
    Parameters:
    -----------
    flat_samples : array-like
        Flattened MCMC samples
    param_names : list
        List of parameter names
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing summary statistics
    """
    # Calculate percentiles
    percentiles = np.percentile(flat_samples, [16, 50, 84], axis=0)
    
    # Create summary statistics
    stats = {
        'parameter': param_names,
        'median': percentiles[1],
        'lower_error': percentiles[1] - percentiles[0],
        'upper_error': percentiles[2] - percentiles[1],
        'mean': np.mean(flat_samples, axis=0),
        'std': np.std(flat_samples, axis=0)
    }
    
    # Create DataFrame
    df = pd.DataFrame(stats)
    
    # Save to CSV
    filename = os.path.join(database_path, "parameter_statistics.csv")
    df.to_csv(filename, index=False)
    print("Saved parameter statistics to: " + filename)
    
    # Print summary
    print("\nParameter Summary Statistics:")
    for i, param in enumerate(param_names):
        print(param + ": " + str(percentiles[1, i]) + " - " + str(percentiles[1, i] - percentiles[0, i]) + " + " + str(percentiles[2, i] - percentiles[1, i]))
    
    return df


def plot_best_fit_model(flat_samples, obs_data, param_names, z_range=(20.0, 5.0), QHII_init=1e-4, n_samples=100):
    """
    Plot the best-fit model and credible intervals.
    
    Parameters:
    -----------
    flat_samples : array-like
        Flattened MCMC samples
    obs_data : dict
        Dictionary containing observational data
    param_names : list
        List of parameter names
    z_range : tuple, optional
        Redshift range for model calculation
    QHII_init : float, optional
        Initial ionization fraction
    n_samples : int, optional
        Number of random samples to draw for credible intervals
        
    Returns:
    --------
    str
        Filename of the saved plot
    """
    # Fixed parameters
    xi0 = 2.5e25
    M_h = 1.0e10
    
    # Get median parameter values
    median_params = np.median(flat_samples, axis=0)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Calculate best-fit model
    full_params = tuple(median_params) + (xi0, M_h)
    z_model, Q_HII_model = solve_QHII(z_range, full_params, QHII_init)
    
    # Plot best-fit model
    ax.plot(z_model, Q_HII_model, 'k-', linewidth=2, label='Best-fit Model')
    
    # Calculate and plot credible intervals
    Q_HII_samples = np.zeros((len(z_model), n_samples))
    
    # Randomly sample from the posterior
    indices = np.random.randint(0, len(flat_samples), n_samples)
    
    for i, idx in enumerate(indices):
        sample_params = tuple(flat_samples[idx]) + (xi0, M_h)
        try:
            _, Q_HII_sample = solve_QHII(z_range, sample_params, QHII_init)
            Q_HII_samples[:, i] = Q_HII_sample
        except Exception as e:
            print("Error calculating model for sample " + str(i) + ": " + str(e))
            Q_HII_samples[:, i] = np.nan
    
    # Calculate percentiles
    Q_HII_lower = np.nanpercentile(Q_HII_samples, 16, axis=1)
    Q_HII_upper = np.nanpercentile(Q_HII_samples, 84, axis=1)
    
    # Plot credible interval
    ax.fill_between(z_model, Q_HII_lower, Q_HII_upper, color='gray', alpha=0.3, label='68% Credible Interval')
    
    # Plot observational data
    methods = np.unique(obs_data['method'])
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    markers = ['o', 's', '^', 'D', 'v']
    
    for i, method in enumerate(methods):
        idx = np.where(obs_data['method'] == method)[0]
        # Calculate asymmetric error bars
        yerr = [obs_data['Q_HII'][idx] - obs_data['Q_HII_lower'][idx], 
                obs_data['Q_HII_upper'][idx] - obs_data['Q_HII'][idx]]
        ax.errorbar(obs_data['z'][idx], obs_data['Q_HII'][idx], yerr=yerr, fmt=markers[i % len(markers)], 
                    color=colors[i % len(colors)], label=method)
    
    ax.set_xlabel("Redshift")
    ax.set_ylabel("Q_HII")
    ax.legend()
    plt.tight_layout()
    
    # Save the figure
    filename = os.path.join(database_path, "best_fit_model_" + str(np.random.randint(10000)) + ".png")
    plt.savefig(filename, dpi=300)
    plt.close()
    
    print("Saved best-fit model plot to: " + filename)
    return filename