<!-- filename: cosmic_reionization_framework.md -->
# Semianalytical Model Framework for Cosmic Reionization

## Governing Equations for the Ionization Fraction

The evolution of the ionized hydrogen volume filling factor, \( Q_{\rm HII}(z) \), is described by the balance between the rate of ionizing photon injection into the intergalactic medium (IGM) and the rate of recombinations. The standard semianalytical equation is:

<code>
\[
\frac{dQ_{\rm HII}}{dt} = \frac{\dot{n}_{\rm ion}}{\langle n_{\rm H} \rangle} - \frac{Q_{\rm HII}}{t_{\rm rec}}
\]
</code>

where:
- \( \dot{n}_{\rm ion} \) is the comoving ionizing photon production rate density (photons s\(^{-1}\) Mpc\(^{-3}\)),
- \( \langle n_{\rm H} \rangle \) is the mean comoving hydrogen number density,
- \( t_{\rm rec} \) is the effective recombination timescale in the IGM.

The ionizing photon production rate density is given by:

<code>
\[
\dot{n}_{\rm ion}(z) = f_{\rm esc}(z, M_h) \, \xi_{\rm ion} \, \rho_{\rm UV}(z)
\]
</code>

where:
- \( f_{\rm esc}(z, M_h) \) is the escape fraction, potentially dependent on redshift and halo mass,
- \( \xi_{\rm ion} \) is the ionizing photon production efficiency (photons erg\(^{-1}\) Hz),
- \( \rho_{\rm UV}(z) \) is the UV luminosity density, integrated over the galaxy population.

The recombination timescale is:

<code>
\[
t_{\rm rec}(z) = \left[ C(z) \, \alpha_B(T) \, (1+Y_p/4X_p) \, \langle n_{\rm H} \rangle \, (1+z)^3 \right]^{-1}
\]
</code>

where:
- \( C(z) \) is the clumping factor,
- \( \alpha_B(T) \) is the case B recombination coefficient,
- \( Y_p \) and \( X_p \) are the primordial helium and hydrogen mass fractions.

## Parameterization of Key Quantities

- **Escape Fraction (\( f_{\rm esc} \))**: Parameterized as a function of redshift and, optionally, halo mass. For example:
  <code>
  \[
  f_{\rm esc}(z, M_h) = f_0 \left( \frac{1+z}{7} \right)^{\alpha} \left( \frac{M_h}{10^{10} M_\odot} \right)^{\beta}
  \]
  </code>
  where \( f_0 \), \( \alpha \), and \( \beta \) are free parameters to be constrained.

- **Clumping Factor (\( C(z) \))**: Adopted from simulations or parameterized as \( C(z) = C_0 \left( \frac{1+z}{7} \right)^{-\gamma} \).

- **UV Luminosity Density (\( \rho_{\rm UV}(z) \))**: Computed by integrating the observed or modeled UV luminosity function down to a limiting magnitude.

- **Ionizing Photon Production Efficiency (\( \xi_{\rm ion} \))**: Treated as a constant or weakly evolving parameter, informed by stellar population synthesis models.

## Solution Approach

The differential equation for \( Q_{\rm HII}(z) \) is generally not analytically solvable for arbitrary parameterizations. The following approach is adopted:

- **Numerical Integration**: The equation is recast in terms of redshift using \( dt/dz = -[H(z)(1+z)]^{-1} \), and integrated from high redshift (\( z \sim 20 \)) to low redshift (\( z \sim 5 \)) using a fourth-order Runge-Kutta method.
- **Parameter Grid or MCMC**: The model is evaluated over a grid or within a Markov Chain Monte Carlo (MCMC) framework to explore the parameter space of \( f_{\rm esc} \), \( C \), and \( \xi_{\rm ion} \).

## Incorporation of Observational Constraints

- **Ionization Fraction Data**: The model predictions for \( Q_{\rm HII}(z) \) are directly compared to the constraints from table 5.1 of the reference, which provides measurements and uncertainties at discrete redshifts.
- **Likelihood Construction**: For each set of model parameters, a likelihood is computed based on the agreement between the predicted and observed \( Q_{\rm HII}(z) \) values, accounting for the reported uncertainties.
- **Additional Data**: Where available, UV luminosity functions and other reionization observables are incorporated as additional likelihood terms to further constrain the model.

This framework enables a systematic exploration of the allowed evolution of the escape fraction and its impact on the reionization history, tightly anchored to the latest observational data.