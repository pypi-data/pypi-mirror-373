# filename: codebase/bayesian_framework.py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm, uniform, truncnorm
from scipy.integrate import simpson  # Using simpson instead of simps (renamed in newer SciPy)
import os
from codebase.cosmic_reionization_model import (
    solve_QHII, H, sigma_T, c, n_H_0, X_p, year_in_s, Mpc_to_cm
)

# Create data directory if it doesn't exist
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Set matplotlib parameters to avoid LaTeX rendering
plt.rcParams['text.usetex'] = False


def extract_observational_data():
    """
    Extract observational constraints on the ionization fraction from Table 5.1
    of the reference paper and other sources.
    
    Returns:
    --------
    dict
        Dictionary containing observational data with keys:
        - 'z': redshift values
        - 'Q_HII': ionization fraction values
        - 'Q_HII_lower': lower bounds on ionization fraction
        - 'Q_HII_upper': upper bounds on ionization fraction
        - 'method': measurement method
    """
    # Data from Table 5.1 of the reference paper
    # Format: redshift, Q_HII, lower_error, upper_error, method
    table_data = [
        # Dark pixel covering fraction
        [5.9, 0.91, 0.02, 0.03, "Dark pixel"],
        # Lyman-alpha emission fraction
        [7, 0.66, 0.09, 0.09, "Lyman-alpha emission"],
        [7.5, 0.46, 0.12, 0.12, "Lyman-alpha emission"],
        # Lyman-alpha + Lyman-beta dark fraction
        [6, 0.87, 0.08, 0.05, "Lyman-alpha + beta dark fraction"],
        [6.2, 0.79, 0.08, 0.08, "Lyman-alpha + beta dark fraction"],
        [6.4, 0.69, 0.08, 0.08, "Lyman-alpha + beta dark fraction"],
        [6.6, 0.52, 0.08, 0.08, "Lyman-alpha + beta dark fraction"],
        [6.8, 0.35, 0.08, 0.08, "Lyman-alpha + beta dark fraction"],
        # QSO damping wings
        [7.09, 0.48, 0.26, 0.26, "QSO damping wings"],
        [7.54, 0.4, 0.23, 0.23, "QSO damping wings"],
        [7.0, 0.7, 0.2, 0.2, "QSO damping wings"],
        # Lyman-alpha dark fraction
        [5.6, 0.94, 0.06, 0.06, "Lyman-alpha dark fraction"],
        [5.8, 0.88, 0.05, 0.05, "Lyman-alpha dark fraction"],
        [6.0, 0.85, 0.05, 0.05, "Lyman-alpha dark fraction"],
        [6.2, 0.71, 0.06, 0.06, "Lyman-alpha dark fraction"],
        [6.4, 0.59, 0.06, 0.06, "Lyman-alpha dark fraction"],
        [6.6, 0.44, 0.06, 0.06, "Lyman-alpha dark fraction"]
    ]
    
    # Convert to numpy arrays
    data = np.array(table_data, dtype=object)
    z = np.array(data[:, 0], dtype=float)
    Q_HII = np.array(data[:, 1], dtype=float)
    Q_HII_lower = Q_HII - np.array(data[:, 2], dtype=float)  # Lower bound
    Q_HII_upper = Q_HII + np.array(data[:, 3], dtype=float)  # Upper bound
    method = np.array(data[:, 4])
    
    # Ensure bounds are within [0, 1]
    Q_HII_lower = np.clip(Q_HII_lower, 0, 1)
    Q_HII_upper = np.clip(Q_HII_upper, 0, 1)
    
    # Create a dictionary with the data
    obs_data = {
        'z': z,
        'Q_HII': Q_HII,
        'Q_HII_lower': Q_HII_lower,
        'Q_HII_upper': Q_HII_upper,
        'method': method
    }
    
    # Additional constraint: CMB optical depth from Planck 2018
    # tau_e = 0.054 ± 0.007
    obs_data['tau_e'] = 0.054
    obs_data['tau_e_error'] = 0.007
    
    return obs_data


def calculate_tau_e(z_array, Q_HII_array, z_max=30.0):
    """
    Calculate the CMB optical depth to electron scattering.
    
    Parameters:
    -----------
    z_array : array-like
        Redshift array
    Q_HII_array : array-like
        Ionization fraction array
    z_max : float, optional
        Maximum redshift to consider
        
    Returns:
    --------
    float
        CMB optical depth
    """
    # Ensure z_array is in ascending order for integration
    if z_array[0] > z_array[-1]:
        z_array = z_array[::-1]
        Q_HII_array = Q_HII_array[::-1]
    
    # Extend arrays to z_max if needed
    if z_array[-1] < z_max:
        z_extended = np.append(z_array, z_max)
        # Assume Q_HII = 0 at z_max
        Q_HII_extended = np.append(Q_HII_array, 0.0)
    else:
        z_extended = z_array
        Q_HII_extended = Q_HII_array
    
    # Calculate the integrand: n_e(z) * sigma_T * c * dt/dz
    integrand = np.zeros_like(z_extended)
    
    for i, z in enumerate(z_extended):
        # Electron number density: n_e(z) = n_H(z) * Q_HII(z) * (1 + Y_p/(4*X_p))
        # n_H(z) = n_H_0 * (1+z)^3
        n_e = n_H_0 * (1 + z)**3 * Q_HII_extended[i] * (1 + 0.25/0.75)  # Assuming Y_p=0.25, X_p=0.75
        
        # dt/dz = -1/[H(z)*(1+z)]
        dt_dz = -1.0 / (H(z) * (1 + z) * 1.0e5 / Mpc_to_cm)  # Convert H(z) from km/s/Mpc to 1/s
        
        integrand[i] = n_e * sigma_T * c * dt_dz
    
    # Integrate using Simpson's rule
    tau_e = simpson(integrand, z_extended)
    
    return tau_e


def log_likelihood(params, obs_data, z_range=(20.0, 5.0), QHII_init=1e-4, include_tau_e=True):
    """
    Calculate the log-likelihood of the model parameters given the observational data.
    
    Parameters:
    -----------
    params : tuple
        Model parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
    obs_data : dict
        Dictionary containing observational data
    z_range : tuple, optional
        Redshift range for model calculation
    QHII_init : float, optional
        Initial ionization fraction
    include_tau_e : bool, optional
        Whether to include CMB optical depth constraint
        
    Returns:
    --------
    float
        Log-likelihood value
    """
    # Unpack parameters
    f0, alpha, beta, C0, gamma, xi0, M_h = params
    
    # Solve the model
    try:
        z_model, Q_HII_model = solve_QHII(z_range, params, QHII_init)
    except Exception as e:
        print("Error in model solution: " + str(e))
        return -np.inf
    
    # Initialize log-likelihood
    log_like = 0.0
    
    # Contribution from ionization fraction measurements
    for i, z_obs in enumerate(obs_data['z']):
        # Find the model value at the observed redshift
        idx = np.argmin(np.abs(z_model - z_obs))
        Q_HII_pred = Q_HII_model[idx]
        
        # Observed value and uncertainty
        Q_HII_obs = obs_data['Q_HII'][i]
        
        # Use asymmetric errors if available
        Q_HII_lower = obs_data['Q_HII_lower'][i]
        Q_HII_upper = obs_data['Q_HII_upper'][i]
        
        # Calculate sigma based on which side of the observation the prediction falls
        if Q_HII_pred <= Q_HII_obs:
            sigma = Q_HII_obs - Q_HII_lower
        else:
            sigma = Q_HII_upper - Q_HII_obs
        
        # Avoid division by zero
        if sigma <= 0:
            sigma = 0.1  # Default uncertainty
        
        # Add to log-likelihood (assuming Gaussian errors)
        log_like += -0.5 * ((Q_HII_pred - Q_HII_obs) / sigma)**2
    
    # Contribution from CMB optical depth if included
    if include_tau_e and 'tau_e' in obs_data and 'tau_e_error' in obs_data:
        tau_e_obs = obs_data['tau_e']
        tau_e_error = obs_data['tau_e_error']
        
        # Calculate model prediction for tau_e
        tau_e_pred = calculate_tau_e(z_model, Q_HII_model)
        
        # Add to log-likelihood
        log_like += -0.5 * ((tau_e_pred - tau_e_obs) / tau_e_error)**2
    
    return log_like


def log_prior(params):
    """
    Calculate the log-prior probability of the model parameters.
    
    Parameters:
    -----------
    params : tuple
        Model parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
        
    Returns:
    --------
    float
        Log-prior value
    """
    f0, alpha, beta, C0, gamma, xi0, M_h = params
    
    # Prior ranges based on physical plausibility and literature
    # f0: escape fraction normalization [0, 1]
    if not 0 <= f0 <= 1:
        return -np.inf
    
    # alpha: redshift dependence of escape fraction [-2, 5]
    if not -2 <= alpha <= 5:
        return -np.inf
    
    # beta: halo mass dependence of escape fraction [-2, 2]
    if not -2 <= beta <= 2:
        return -np.inf
    
    # C0: clumping factor normalization [1, 20]
    if not 1 <= C0 <= 20:
        return -np.inf
    
    # gamma: redshift dependence of clumping factor [0, 3]
    if not 0 <= gamma <= 3:
        return -np.inf
    
    # xi0: ionizing photon production efficiency [1e24, 1e26]
    if not 1e24 <= xi0 <= 1e26:
        return -np.inf
    
    # M_h: characteristic halo mass [1e9, 1e12]
    if not 1e9 <= M_h <= 1e12:
        return -np.inf
    
    # If all parameters are within their prior ranges, return 0 (log(1))
    return 0.0


def log_posterior(params, obs_data, z_range=(20.0, 5.0), QHII_init=1e-4, include_tau_e=True):
    """
    Calculate the log-posterior probability of the model parameters.
    
    Parameters:
    -----------
    params : tuple
        Model parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
    obs_data : dict
        Dictionary containing observational data
    z_range : tuple, optional
        Redshift range for model calculation
    QHII_init : float, optional
        Initial ionization fraction
    include_tau_e : bool, optional
        Whether to include CMB optical depth constraint
        
    Returns:
    --------
    float
        Log-posterior value
    """
    # Calculate log-prior
    lp = log_prior(params)
    
    # If parameters are outside prior range, return -inf
    if not np.isfinite(lp):
        return -np.inf
    
    # Calculate log-likelihood
    ll = log_likelihood(params, obs_data, z_range, QHII_init, include_tau_e)
    
    # Return log-posterior (log-prior + log-likelihood)
    return lp + ll


def visualize_observational_constraints(obs_data):
    """
    Visualize the observational constraints on the ionization fraction.
    
    Parameters:
    -----------
    obs_data : dict
        Dictionary containing observational data
    
    Returns:
    --------
    str
        Filename of the saved plot
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Get unique measurement methods
    methods = np.unique(obs_data['method'])
    
    # Define colors and markers for different methods
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    markers = ['o', 's', '^', 'D', 'v']
    
    # Plot data points with error bars for each method
    for i, method in enumerate(methods):
        # Find indices for this method
        idx = np.where(obs_data['method'] == method)[0]
        
        # Plot data points with error bars
        ax.errorbar(
            obs_data['z'][idx],
            obs_data['Q_HII'][idx],
            yerr=[
                obs_data['Q_HII'][idx] - obs_data['Q_HII_lower'][idx],
                obs_data['Q_HII_upper'][idx] - obs_data['Q_HII'][idx]
            ],
            fmt=markers[i % len(markers)],
            color=colors[i % len(colors)],
            label=method,
            capsize=4,
            markersize=8,
            elinewidth=2
        )
    
    # Set axis labels and title
    ax.set_xlabel('Redshift (z)')
    ax.set_ylabel('Ionization Fraction (Q_HII)')
    ax.set_title('Observational Constraints on Ionization Fraction')
    
    # Save the figure to the data directory
    filename = os.path.join('data', 'observational_constraints.png')
    plt.savefig(filename)
    plt.close()
    
    return filename
