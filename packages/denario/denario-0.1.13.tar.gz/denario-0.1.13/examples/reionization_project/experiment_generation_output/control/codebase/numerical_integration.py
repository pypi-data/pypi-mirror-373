# filename: codebase/numerical_integration.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os
import time
from codebase.cosmic_reionization_model import (
    dQHII_dz, solve_QHII, H, n_ion_dot, t_rec, n_H_0
)

# Create data directory if it doesn't exist
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Set matplotlib parameters to avoid LaTeX rendering
plt.rcParams['text.usetex'] = False


def compare_solvers(z_range=(20.0, 5.0), params=(0.1, 2.0, -0.5, 3.0, 1.0, 2.5e25, 1.0e10), 
                   QHII_init=1e-4, methods=None):
    """
    Compare different numerical integration methods for solving the reionization equation.
    
    Parameters:
    -----------
    z_range : tuple
        (z_start, z_end) redshift range to solve over
    params : tuple
        Parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
    QHII_init : float
        Initial ionization fraction at z_start
    methods : list
        List of integration methods to compare
        
    Returns:
    --------
    dict
        Dictionary containing results for each method
    """
    if methods is None:
        methods = ['RK45', 'BDF', 'Radau']
    
    results = {}
    
    for method in methods:
        start_time = time.time()
        
        # Solve the differential equation
        sol = solve_ivp(
            lambda z, y: dQHII_dz(z, y, params),
            [z_range[0], z_range[1]],
            [QHII_init],
            method=method,
            rtol=1e-6,
            atol=1e-9,
            dense_output=True
        )
        
        end_time = time.time()
        
        # Create a finer grid for output
        z_array = np.linspace(z_range[0], z_range[1], 1000)
        
        # Check if the solver was successful
        if sol.success:
            QHII_array = sol.sol(z_array)[0]
            # Ensure QHII is between 0 and 1
            QHII_array = np.clip(QHII_array, 0.0, 1.0)
        else:
            print("Solver " + method + " failed with message: " + sol.message)
            # Create a dummy array for failed solvers
            QHII_array = np.zeros_like(z_array)
        
        results[method] = {
            'z_array': z_array,
            'QHII_array': QHII_array,
            'time': end_time - start_time,
            'nfev': sol.nfev,
            'njev': sol.njev if hasattr(sol, 'njev') else 0,
            'nlu': sol.nlu if hasattr(sol, 'nlu') else 0,
            'status': sol.status,
            'success': sol.success,
            'message': sol.message
        }
    
    return results


def step_size_sensitivity(z_range=(20.0, 5.0), params=(0.1, 2.0, -0.5, 3.0, 1.0, 2.5e25, 1.0e10), 
                         QHII_init=1e-4, rtol_values=None, atol_values=None):
    """
    Analyze sensitivity to step size control parameters (rtol, atol).
    
    Parameters:
    -----------
    z_range : tuple
        (z_start, z_end) redshift range to solve over
    params : tuple
        Parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
    QHII_init : float
        Initial ionization fraction at z_start
    rtol_values : list
        List of relative tolerance values to test
    atol_values : list
        List of absolute tolerance values to test
        
    Returns:
    --------
    tuple
        (z_array, QHII_ref, results) containing the reference solution and results for each tolerance setting
    """
    if rtol_values is None:
        rtol_values = [1e-3, 1e-6, 1e-9]
    if atol_values is None:
        atol_values = [1e-6, 1e-9, 1e-12]
    
    results = {}
    
    # Generate reference solution with very tight tolerances
    sol_ref = solve_ivp(
        lambda z, y: dQHII_dz(z, y, params),
        [z_range[0], z_range[1]],
        [QHII_init],
        method='RK45',
        rtol=1e-12,
        atol=1e-15,
        dense_output=True
    )
    
    z_array = np.linspace(z_range[0], z_range[1], 1000)
    
    # Check if reference solution was successful
    if sol_ref.success:
        QHII_ref = sol_ref.sol(z_array)[0]
        QHII_ref = np.clip(QHII_ref, 0.0, 1.0)
    else:
        print("Reference solution failed with message: " + sol_ref.message)
        # Create a dummy reference array
        QHII_ref = np.zeros_like(z_array)
        return z_array, QHII_ref, {}  # Return early if reference solution fails
    
    for rtol in rtol_values:
        for atol in atol_values:
            key = "rtol=" + str(format(rtol, '.0e')) + "_atol=" + str(format(atol, '.0e'))
            
            start_time = time.time()
            
            sol = solve_ivp(
                lambda z, y: dQHII_dz(z, y, params),
                [z_range[0], z_range[1]],
                [QHII_init],
                method='RK45',
                rtol=rtol,
                atol=atol,
                dense_output=True
            )
            
            end_time = time.time()
            
            if sol.success:
                QHII_array = sol.sol(z_array)[0]
                QHII_array = np.clip(QHII_array, 0.0, 1.0)
                
                # Calculate error metrics
                abs_error = np.abs(QHII_array - QHII_ref)
                max_error = np.max(abs_error)
                mean_error = np.mean(abs_error)
                
                results[key] = {
                    'QHII_array': QHII_array,
                    'time': end_time - start_time,
                    'nfev': sol.nfev,
                    'max_error': max_error,
                    'mean_error': mean_error,
                    'status': sol.status,
                    'success': sol.success,
                    'message': sol.message
                }
            else:
                print("Solution for " + key + " failed with message: " + sol.message)
                results[key] = {
                    'QHII_array': np.zeros_like(z_array),
                    'time': end_time - start_time,
                    'nfev': sol.nfev,
                    'max_error': np.nan,
                    'mean_error': np.nan,
                    'status': sol.status,
                    'success': sol.success,
                    'message': sol.message
                }
    
    return z_array, QHII_ref, results


def stability_analysis(z_range=(20.0, 5.0), QHII_init=1e-4):
    """
    Analyze numerical stability across different parameter regimes.
    
    Parameters:
    -----------
    z_range : tuple
        (z_start, z_end) redshift range to solve over
    QHII_init : float
        Initial ionization fraction at z_start
        
    Returns:
    --------
    dict
        Dictionary containing stability results for different parameter regimes
    """
    # Define parameter regimes to test
    regimes = {
        'standard': (0.1, 2.0, -0.5, 3.0, 1.0, 2.5e25, 1.0e10),
        'high_escape': (0.5, 2.0, -0.5, 3.0, 1.0, 2.5e25, 1.0e10),
        'low_escape': (0.01, 2.0, -0.5, 3.0, 1.0, 2.5e25, 1.0e10),
        'high_clumping': (0.1, 2.0, -0.5, 10.0, 1.0, 2.5e25, 1.0e10),
        'low_clumping': (0.1, 2.0, -0.5, 1.0, 1.0, 2.5e25, 1.0e10),
        'steep_redshift': (0.1, 4.0, -0.5, 3.0, 1.0, 2.5e25, 1.0e10),
        'extreme': (0.8, 5.0, -1.0, 15.0, 2.0, 5.0e25, 1.0e9)
    }
    
    results = {}
    
    for regime_name, params in regimes.items():
        try:
            # Try with default settings
            sol = solve_ivp(
                lambda z, y: dQHII_dz(z, y, params),
                [z_range[0], z_range[1]],
                [QHII_init],
                method='RK45',
                rtol=1e-6,
                atol=1e-9,
                dense_output=True
            )
            
            z_array = np.linspace(z_range[0], z_range[1], 1000)
            
            if sol.success:
                QHII_array = sol.sol(z_array)[0]
                QHII_array = np.clip(QHII_array, 0.0, 1.0)
                
                # Check for stability issues
                is_stable = sol.status == 0
                has_oscillations = False
                if len(QHII_array) > 2:
                    # Check for oscillations by looking at sign changes in the derivative
                    dQdz = np.diff(QHII_array)
                    sign_changes = np.sum(np.abs(np.diff(np.sign(dQdz))) )
                    has_oscillations = sign_changes > 10  # Arbitrary threshold
                
                # Calculate stiffness estimate
                f0, alpha, beta, C0, gamma, xi0, M_h = params
                
                # Estimate source and sink terms at a few points
                z_samples = np.linspace(z_range[0], z_range[1], 10)
                stiffness_ratios = []
                
                for z in z_samples:
                    source = n_ion_dot(z, f0, alpha, beta, xi0, M_h) / n_H_0
                    sink_coeff = 1.0 / t_rec(z, C0, gamma)
                    # Stiffness ratio is approximately the ratio of the fastest to slowest timescales
                    if source > 0:
                        stiffness_ratios.append(sink_coeff / source)
                
                max_stiffness = max(stiffness_ratios) if stiffness_ratios else 0
                
                results[regime_name] = {
                    'z_array': z_array,
                    'QHII_array': QHII_array,
                    'is_stable': is_stable,
                    'has_oscillations': has_oscillations,
                    'max_stiffness': max_stiffness,
                    'nfev': sol.nfev,
                    'status': sol.status,
                    'success': sol.success,
                    'message': sol.message
                }
            else:
                print("Solution for regime " + regime_name + " failed with message: " + sol.message)
                results[regime_name] = {
                    'is_stable': False,
                    'success': False,
                    'message': sol.message
                }
            
        except Exception as e:
            print("Error in regime " + regime_name + ": " + str(e))
            results[regime_name] = {
                'is_stable': False,
                'success': False,
                'error': str(e)
            }
    
    return results


def generate_model_predictions(z_range=(20.0, 5.0), QHII_init=1e-4):
    """
    Generate model predictions for a grid of parameter values.
    
    Parameters:
    -----------
    z_range : tuple
        (z_start, z_end) redshift range to solve over
    QHII_init : float
        Initial ionization fraction at z_start
        
    Returns:
    --------
    dict
        Dictionary containing model predictions for different parameter sets
    """
    # Define parameter grid
    f0_values = [0.05, 0.1, 0.2]
    alpha_values = [1.0, 2.0, 3.0]
    C0_values = [2.0, 3.0, 5.0]
    
    # Fixed parameters
    beta = -0.5
    gamma = 1.0
    xi0 = 2.5e25
    M_h = 1.0e10
    
    results = {}
    
    # Generate predictions for each parameter combination
    for f0 in f0_values:
        for alpha in alpha_values:
            for C0 in C0_values:
                key = "f0=" + str(f0) + "_alpha=" + str(alpha) + "_C0=" + str(C0)
                params = (f0, alpha, beta, C0, gamma, xi0, M_h)
                
                try:
                    z_array, QHII_array = solve_QHII(z_range, params, QHII_init)
                    
                    # Find redshift where QHII = 0.5 (if it exists)
                    z_half_idx = np.where(QHII_array >= 0.5)[0]
                    z_half = z_array[z_half_idx[0]] if len(z_half_idx) > 0 else None
                    
                    # Find redshift where QHII = 0.99 (if it exists)
                    z_complete_idx = np.where(QHII_array >= 0.99)[0]
                    z_complete = z_array[z_complete_idx[0]] if len(z_complete_idx) > 0 else None
                    
                    results[key] = {
                        'z_array': z_array,
                        'QHII_array': QHII_array,
                        'z_half': z_half,
                        'z_complete': z_complete
                    }
                except Exception as e:
                    print("Error generating model prediction for " + key + ": " + str(e))
                    results[key] = {
                        'z_array': None,
                        'QHII_array': None,
                        'error': str(e)
                    }
    
    return results