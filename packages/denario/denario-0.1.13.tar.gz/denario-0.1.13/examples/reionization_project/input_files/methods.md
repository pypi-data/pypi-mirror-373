# Methodology

## 1. Theoretical Framework and Model Assumptions

The analysis is grounded in the semianalytical modeling of cosmic reionization, focusing on the evolution of the ionized hydrogen volume filling factor, \( Q_{\rm HII}(z) \), as a function of redshift. The central hypothesis is that the escape fraction of ionizing photons, \( f_{\rm esc} \), and its evolution with redshift and halo mass, is a primary driver of the reionization history. The model assumes that star-forming galaxies are the dominant sources of reionization, with the IGM treated as a two-phase medium (ionized and neutral). The clumping factor, \( C(z) \), is included to account for IGM inhomogeneities, and the ionizing photon production efficiency, \( \xi_{\rm ion} \), is informed by stellar population synthesis models.

## 2. Governing Equations

The evolution of the ionized fraction is described by the following differential equation:

<code>
\[
\frac{dQ_{\rm HII}}{dt} = \frac{\dot{n}_{\rm ion}}{\langle n_{\rm H} \rangle} - \frac{Q_{\rm HII}}{t_{\rm rec}}
\]
</code>

where:
- \( \dot{n}_{\rm ion}(z) = f_{\rm esc}(z, M_h) \; \xi_{\rm ion} \; \rho_{\rm UV}(z) \) is the comoving ionizing photon production rate density,
- \( \langle n_{\rm H} \rangle \) is the mean comoving hydrogen number density,
- \( t_{\rm rec}(z) = [C(z) \; \alpha_B(T) \; (1+Y_p/4X_p) \; \langle n_{\rm H} \rangle \; (1+z)^3]^{-1} \) is the effective recombination timescale.

The UV luminosity density, \( \rho_{\rm UV}(z) \), is computed by integrating the observed or modeled UV luminosity function down to a limiting magnitude.

## 3. Parameterization of Key Quantities

- **Escape Fraction (\( f_{\rm esc} \))**: Parameterized as a function of redshift and halo mass:
  <code>
  \[
  f_{\rm esc}(z, M_h) = f_0 \left( \frac{1+z}{7} \right)^{\alpha} \left( \frac{M_h}{10^{10} M_\odot} \right)^{\beta}
  \]
  </code>
  where \( f_0 \), \( \alpha \), and \( \beta \) are free parameters.

- **Clumping Factor (\( C(z) \))**: Parameterized as \( C(z) = C_0 \left( \frac{1+z}{7} \right)^{-\gamma} \), with \( C_0 \) and \( \gamma \) as free parameters.

- **Ionizing Photon Production Efficiency (\( \xi_{\rm ion} \))**: Treated as a constant or weakly evolving parameter.

- **UV Luminosity Density (\( \rho_{\rm UV}(z) \))**: Derived from observed luminosity functions or modeled as a function of redshift.

## 4. Numerical Solution

The differential equation for \( Q_{\rm HII}(z) \) is recast in terms of redshift using \( dt/dz = -[H(z)(1+z)]^{-1} \) and solved numerically from \( z \sim 20 \) to \( z \sim 5 \) using a fourth-order Runge-Kutta integration scheme. The model is evaluated over a multidimensional parameter space defined by \( f_0, \alpha, \beta, C_0, \gamma, \xi_{\rm ion} \).

## 5. Incorporation of Observational Constraints

The model predictions for \( Q_{\rm HII}(z) \) are directly compared to the redshift-dependent constraints from table 5.1 of the reference, which provide measurements and uncertainties at discrete redshifts. Additional constraints from UV luminosity functions and the integrated CMB optical depth (\( \tau_e \)) are incorporated where available.

## 6. Bayesian Parameter Estimation

A Bayesian inference framework is employed to estimate the posterior distributions of the model parameters. The likelihood function is constructed as:

<code>
\[
\mathcal{L}(\theta) = \prod_{i} \frac{1}{\sqrt{2\pi}\sigma_i} \exp\left[ -\frac{(Q_{\rm HII, model}(z_i; \theta) - Q_{\rm HII, obs}(z_i))^2}{2\sigma_i^2} \right]
\]
</code>

where \( Q_{\rm HII, obs}(z_i) \) and \( \sigma_i \) are the observed ionization fraction and its uncertainty at redshift \( z_i \). Priors are chosen based on physical plausibility and literature. The posterior is sampled using Markov Chain Monte Carlo (MCMC) methods, such as the affine-invariant ensemble sampler.

## 7. Addressing Parameter Degeneracies and Model Validation

Degeneracies between parameters (e.g., \( f_{\rm esc} \), \( C \), \( \xi_{\rm ion} \)) are quantified through the joint posterior distributions. Additional likelihood terms from UV luminosity functions and CMB optical depth are used to break degeneracies. Model predictions are validated against independent observables, such as Ly\(\alpha\) emitter statistics and the evolution of the UV luminosity density.

## 8. Sensitivity Analysis and Robustness Checks

Sensitivity analyses are performed by varying prior choices, analyzing subsets of the data, and exploring alternative parameterizations for \( f_{\rm esc}(z, M_h) \) and \( C(z) \). Posterior predictive checks are conducted to ensure the model provides an adequate fit to the data.

---

This methodology provides a comprehensive, data-driven approach to constraining the evolution of the escape fraction and its impact on cosmic reionization, directly linking the modeling strategy to the hypotheses and assumptions outlined in the theoretical framework.