# filename: codebase/cosmic_reionization_model.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os

# Create data directory if it doesn't exist
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Set matplotlib parameters to avoid LaTeX rendering
plt.rcParams['text.usetex'] = False

# Constants and cosmological parameters
# All in cgs units where applicable
H0 = 67.4  # Hubble constant in km/s/Mpc
h = H0 / 100.0  # Dimensionless Hubble parameter
Omega_m = 0.315  # Matter density parameter
Omega_b = 0.0493  # Baryon density parameter
Omega_Lambda = 1.0 - Omega_m  # Dark energy density parameter
Y_p = 0.24  # Primordial helium mass fraction
X_p = 1.0 - Y_p  # Primordial hydrogen mass fraction
T_IGM = 2e4  # IGM temperature in K
alpha_B = 2.6e-13  # Case B recombination coefficient at T_IGM in cm^3/s
sigma_T = 6.65e-25  # Thomson cross-section in cm^2
c = 3.0e10  # Speed of light in cm/s
Mpc_to_cm = 3.086e24  # Conversion from Mpc to cm
M_sun = 1.989e33  # Solar mass in g
G = 6.67e-8  # Gravitational constant in cm^3/g/s^2
m_H = 1.67e-24  # Mass of hydrogen atom in g
year_in_s = 3.154e7  # Year in seconds

# Mean hydrogen number density at z=0 in comoving units (cm^-3)
n_H_0 = (Omega_b * 3.0 * H0**2 * (1.0e5 / c)**2 / (8.0 * np.pi * G) * X_p / m_H) / (Mpc_to_cm**3)


def H(z):
    """
    Hubble parameter as a function of redshift.
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
        
    Returns:
    --------
    float or array-like
        Hubble parameter in km/s/Mpc
    """
    return H0 * np.sqrt(Omega_m * (1.0 + z)**3 + Omega_Lambda)


def f_esc(z, M_h, f0=0.1, alpha=2.0, beta=-0.5):
    """
    Escape fraction of ionizing photons as a function of redshift and halo mass.
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
    M_h : float or array-like
        Halo mass in solar masses
    f0 : float, optional
        Normalization factor
    alpha : float, optional
        Redshift dependence power-law index
    beta : float, optional
        Halo mass dependence power-law index
        
    Returns:
    --------
    float or array-like
        Escape fraction (dimensionless)
    """
    f = f0 * ((1.0 + z) / 7.0)**alpha * (M_h / 1.0e10)**beta
    
    # Ensure escape fraction is between 0 and 1
    if np.isscalar(f):
        return max(0.0, min(1.0, f))
    else:
        return np.clip(f, 0.0, 1.0)


def C(z, C0=3.0, gamma=1.0):
    """
    Clumping factor as a function of redshift.
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
    C0 : float, optional
        Normalization factor
    gamma : float, optional
        Redshift dependence power-law index
        
    Returns:
    --------
    float or array-like
        Clumping factor (dimensionless)
    """
    return C0 * ((1.0 + z) / 7.0)**(-gamma)


def xi_ion(z, xi0=2.5e25):
    """
    Ionizing photon production efficiency as a function of redshift.
    Units: erg^-1 Hz
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
    xi0 : float, optional
        Base ionizing photon production efficiency
        
    Returns:
    --------
    float or array-like
        Ionizing photon production efficiency in erg^-1 Hz
    """
    # For simplicity, we assume a constant value
    # In more complex models, this could depend on metallicity, IMF, etc.
    return xi0


def rho_UV(z):
    """
    UV luminosity density as a function of redshift.
    Based on observed luminosity functions.
    Units: erg/s/Hz/Mpc^3
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
        
    Returns:
    --------
    float or array-like
        UV luminosity density in erg/s/Hz/Mpc^3
    """
    # Simple parameterization based on observations
    # From Bouwens et al. 2015, Robertson et al. 2015
    log_rho_UV = 26.20 - 0.16 * (z - 6.0)
    return 10.0**log_rho_UV


def n_ion_dot(z, f0=0.1, alpha=2.0, beta=-0.5, xi0=2.5e25, M_h=1.0e10):
    """
    Comoving ionizing photon production rate density.
    Units: photons/s/cm^3
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
    f0, alpha, beta : float, optional
        Parameters for escape fraction
    xi0 : float, optional
        Ionizing photon production efficiency
    M_h : float, optional
        Characteristic halo mass in solar masses
        
    Returns:
    --------
    float or array-like
        Ionizing photon production rate density in photons/s/cm^3
    """
    return f_esc(z, M_h, f0, alpha, beta) * xi_ion(z, xi0) * rho_UV(z) / (Mpc_to_cm**3)


def t_rec(z, C0=3.0, gamma=1.0):
    """
    Recombination time as a function of redshift.
    Units: seconds
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
    C0, gamma : float, optional
        Parameters for clumping factor
        
    Returns:
    --------
    float or array-like
        Recombination time in seconds
    """
    return 1.0 / (C(z, C0, gamma) * alpha_B * (1.0 + Y_p/(4.0*X_p)) * n_H_0 * (1.0 + z)**3)


def dQHII_dt(z, QHII, params):
    """
    Time derivative of the ionization fraction.
    
    Parameters:
    -----------
    z : float
        Redshift
    QHII : float
        Ionization fraction
    params : tuple
        Parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
        
    Returns:
    --------
    float
        Time derivative of QHII
    """
    f0, alpha, beta, C0, gamma, xi0, M_h = params
    
    # Ensure QHII is between 0 and 1
    QHII = max(0.0, min(1.0, QHII))
    
    # Source term
    source = n_ion_dot(z, f0, alpha, beta, xi0, M_h) / n_H_0
    
    # Sink term
    sink = QHII / t_rec(z, C0, gamma)
    
    return source - sink


def dQHII_dz(z, QHII, params):
    """
    Redshift derivative of the ionization fraction.
    
    Parameters:
    -----------
    z : float
        Redshift
    QHII : float
        Ionization fraction
    params : tuple
        Parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
        
    Returns:
    --------
    float
        Redshift derivative of QHII
    """
    # Convert from dt to dz using dt/dz = -1/[H(z)*(1+z)]
    return -dQHII_dt(z, QHII, params) / (H(z) * (1.0 + z) * 1.0e5 / Mpc_to_cm)


def solve_QHII(z_range, params, QHII_init=1e-4):
    """
    Solve for the ionization fraction as a function of redshift.
    
    Parameters:
    -----------
    z_range : tuple
        (z_start, z_end) redshift range to solve over
    params : tuple
        Parameters (f0, alpha, beta, C0, gamma, xi0, M_h)
    QHII_init : float, optional
        Initial ionization fraction at z_start
        
    Returns:
    --------
    tuple
        (z_array, QHII_array) redshift and ionization fraction arrays
    """
    # We integrate from high to low redshift
    z_start, z_end = z_range
    
    # Solve the differential equation
    sol = solve_ivp(
        lambda z, y: dQHII_dz(z, y, params),
        [z_start, z_end],
        [QHII_init],
        method='RK45',
        rtol=1e-6,
        atol=1e-9,
        dense_output=True
    )
    
    # Create a finer grid for output
    z_array = np.linspace(z_start, z_end, 1000)
    QHII_array = sol.sol(z_array)[0]
    
    # Ensure QHII is between 0 and 1
    QHII_array = np.clip(QHII_array, 0.0, 1.0)
    
    return z_array, QHII_array


def analytical_QHII_simple(z, z_reion=8.0, dz_width=0.5):
    """
    Simple analytical approximation for QHII(z) for validation.
    Uses a tanh function centered at z_reion with width dz_width.
    
    Parameters:
    -----------
    z : float or array-like
        Redshift
    z_reion : float, optional
        Redshift of reionization (where QHII = 0.5)
    dz_width : float, optional
        Width of the transition
        
    Returns:
    --------
    float or array-like
        Ionization fraction
    """
    return 0.5 * (1.0 - np.tanh((z - z_reion) / dz_width))


def validate_model():
    """
    Validate the model by comparing numerical solutions to simplified cases.
    """
    # Define parameters for a simplified case
    f0 = 0.2
    alpha = 1.0
    beta = 0.0
    C0 = 3.0
    gamma = 0.0
    xi0 = 2.5e25
    M_h = 1.0e10
    params = (f0, alpha, beta, C0, gamma, xi0, M_h)
    
    # Solve the model
    z_range = (20.0, 5.0)
    z_array, QHII_array = solve_QHII(z_range, params)
    
    # Find z where QHII = 0.5 for the analytical approximation
    z_half_idx = np.argmin(np.abs(QHII_array - 0.5))
    z_reion = z_array[z_half_idx]
    
    # Calculate analytical approximation
    QHII_analytical = analytical_QHII_simple(z_array, z_reion=z_reion)
    
    # Plot comparison
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    ax.plot(z_array, QHII_array, 'b-', linewidth=2, label='Numerical Solution')
    ax.plot(z_array, QHII_analytical, 'r--', linewidth=2, label='Analytical Approximation')
    
    ax.set_xlabel('Redshift (z)')
    ax.set_ylabel('Ionization Fraction (Q_HII)')
    ax.set_title('Validation: Numerical vs. Analytical Solution')
    ax.set_xlim(z_range[1], z_range[0])
    ax.set_ylim(0, 1.05)
    ax.grid(True)
    ax.legend()
    
    plt.tight_layout()
    
    # Save the figure
    filename = database_path + "validation_plot_1_" + str(np.random.randint(10000)) + ".png"
    plt.savefig(filename, dpi=300)
    print("Saved validation plot comparing numerical and analytical solutions to:", filename)
    
    # Calculate and print some metrics
    max_diff = np.max(np.abs(QHII_array - QHII_analytical))
    mean_diff = np.mean(np.abs(QHII_array - QHII_analytical))
    
    print("\nValidation Metrics:")
    print("Maximum absolute difference:", max_diff)
    print("Mean absolute difference:", mean_diff)
    print("Redshift at QHII = 0.5:", z_reion)
    
    return max_diff, mean_diff, z_reion


def parameter_sensitivity():
    """
    Test sensitivity of the model to different parameter values.
    """
    # Base parameters
    f0_base = 0.1
    alpha_base = 2.0
    beta_base = -0.5
    C0_base = 3.0
    gamma_base = 1.0
    xi0_base = 2.5e25
    M_h_base = 1.0e10
    
    # Parameter variations
    f0_values = [0.05, 0.1, 0.2]
    alpha_values = [1.0, 2.0, 3.0]
    
    # Redshift range
    z_range = (20.0, 5.0)
    
    # Create figure with two subplots for sensitivity analysis
    fig, axs = plt.subplots(1, 2, figsize=(15, 6), dpi=300)
    
    # Test f0 sensitivity
    for f0 in f0_values:
        params = (f0, alpha_base, beta_base, C0_base, gamma_base, xi0_base, M_h_base)
        z_array, QHII_array = solve_QHII(z_range, params)
        axs[0].plot(z_array, QHII_array, label="f0=" + str(f0), linewidth=2)
    axs[0].set_xlabel("Redshift (z)")
    axs[0].set_ylabel("Ionization Fraction (Q_HII)")
    axs[0].set_title("Sensitivity to f0")
    axs[0].grid(True)
    axs[0].legend()
    
    # Test alpha sensitivity
    for alpha in alpha_values:
        params = (f0_base, alpha, beta_base, C0_base, gamma_base, xi0_base, M_h_base)
        z_array, QHII_array = solve_QHII(z_range, params)
        axs[1].plot(z_array, QHII_array, label="alpha=" + str(alpha), linewidth=2)
    axs[1].set_xlabel("Redshift (z)")
    axs[1].set_ylabel("Ionization Fraction (Q_HII)")
    axs[1].set_title("Sensitivity to alpha")
    axs[1].grid(True)
    axs[1].legend()
    
    plt.tight_layout()
    sensitivity_filename = database_path + "sensitivity_plot_" + str(np.random.randint(10000)) + ".png"
    plt.savefig(sensitivity_filename, dpi=300)
    print("Saved sensitivity analysis plot to:", sensitivity_filename)
    
    return sensitivity_filename


if __name__ == "__main__":
    print("Running validation...")
    validate_model()
    print("Running parameter sensitivity analysis...")
    parameter_sensitivity()
