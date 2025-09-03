<!-- filename: parameter_estimation_model_validation.md -->
# Statistical and Computational Methodology for Parameter Estimation and Model Validation

## Bayesian Framework for Parameter Estimation

A Bayesian inference framework will be employed to estimate the posterior probability distributions of the key model parameters, including the escape fraction normalization and evolution parameters (\(f_0, \alpha, \beta\)), the clumping factor (\(C_0, \gamma\)), and the ionizing photon production efficiency (\(\xi_{\rm ion}\)). The likelihood function is constructed by comparing the model-predicted ionization fraction \(Q_{\rm HII}(z)\) to the observational constraints from table 5.1, which provide measurements and uncertainties at discrete redshifts. Assuming Gaussian errors, the likelihood for a given set of parameters \(\theta\) is:

<code>
\[
\mathcal{L}(\theta) = \prod_{i} \frac{1}{\sqrt{2\pi}\sigma_i} \exp\left[ -\frac{(Q_{\rm HII, model}(z_i; \theta) - Q_{\rm HII, obs}(z_i))^2}{2\sigma_i^2} \right]
\]
</code>

where \(Q_{\rm HII, obs}(z_i)\) and \(\sigma_i\) are the observed ionization fraction and its uncertainty at redshift \(z_i\).

Priors for each parameter are chosen based on physical plausibility and previous literature, with broad, non-informative priors for parameters with large uncertainties. The posterior distribution is then sampled using Markov Chain Monte Carlo (MCMC) techniques, such as the affine-invariant ensemble sampler (e.g., `emcee`), to efficiently explore the multidimensional parameter space.

## Addressing Parameter Degeneracies

Degeneracies between parameters—such as between the escape fraction, source luminosity, and clumping factor—are inherent in reionization modeling. The Bayesian approach naturally quantifies these degeneracies through the joint posterior distributions. To further break degeneracies, additional observational constraints are incorporated:

- **UV Luminosity Functions:** The model-predicted UV luminosity density \(\rho_{\rm UV}(z)\) is compared to observed luminosity functions at relevant redshifts, adding a likelihood term for the UV data.
- **Integrated Optical Depth (\(\tau_e\)):** The integrated electron scattering optical depth, as measured by the CMB, provides an integral constraint on the reionization history and is included as an additional likelihood term.

By combining these datasets, the analysis leverages complementary information to disentangle the effects of different parameters.

## Model Validation Against Additional Observables

Model predictions are validated against independent observables not used in the primary parameter estimation:

- **UV Luminosity Functions:** The predicted \(\rho_{\rm UV}(z)\) is compared to observed values, ensuring consistency with galaxy population data.
- **Ly(\(\alpha\)) Emitter Statistics:** Where available, the evolution of the Ly\(\alpha\) emitter fraction is compared to model predictions for the neutral fraction.
- **CMB Optical Depth:** The model-derived \(\tau_e\) is checked against Planck measurements.

Discrepancies between model predictions and these observables may indicate the need for revised parameterizations or additional physical processes.

## Sensitivity Analysis and Robustness Checks

To assess the robustness of the inferred parameter constraints, several sensitivity analyses are performed:

- **Prior Sensitivity:** The impact of different prior choices on the posterior distributions is evaluated.
- **Data Subset Analysis:** The analysis is repeated with subsets of the observational data (e.g., excluding certain redshift bins) to test the stability of the results.
- **Alternative Parameterizations:** Different functional forms for \(f_{\rm esc}(z, M_h)\) and \(C(z)\) are explored to assess model dependence.

Posterior predictive checks are conducted by generating mock datasets from the posterior predictive distribution and comparing them to the observed data, ensuring that the model provides an adequate fit.

This comprehensive statistical and computational methodology enables robust inference of the escape fraction evolution and its impact on cosmic reionization, while rigorously quantifying uncertainties and addressing parameter degeneracies.